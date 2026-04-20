#!/usr/bin/env python3
"""Wiki-update subagent driver for the Virtual Jensen ingestion pipeline.

Given a set of new source items (from the ingestion fetchers) and the
source's ``targets:`` glob(s) in ``sources.yaml``, invoke Claude Opus 4.7
via the Claude Agent SDK to propose edits to specific pages under ``wiki/``.

Dry-run by default: proposed diffs stream to stdout and nothing on disk is
modified. Pass ``--apply`` to additionally parse the fenced diffs, apply
them to files under ``wiki/``, and commit the result to a fresh branch.

Examples:
    update_wiki.py --source "NVIDIA Blog" --items items.json
    update_wiki.py --source "AMD Newsroom" --items items.json --tier weekly --apply

``--items`` is a JSON array of objects with ``id``, ``title``, ``url``,
``published``, ``summary`` — compatible with ``run.py --json``'s ``new:``
entries. Extra keys pass through verbatim.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
SOURCES_YAML = HERE.parent / "sources.yaml"

# So sibling modules under scripts/ingest/ are importable if needed later.
sys.path.insert(0, str(HERE.parent))

# Scrub ANTHROPIC_API_KEY before importing the SDK so Claude Code uses the
# user's Max-plan OAuth rather than API billing. Mirrors virtual-jensen-web/app.py.
if os.environ.pop("ANTHROPIC_API_KEY", None):
    sys.stderr.write("note: dropped ANTHROPIC_API_KEY (using Claude Code OAuth)\n")

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("Install pyyaml: pip install pyyaml\n")
    sys.exit(2)

try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )
except ImportError:
    sys.stderr.write(
        "claude-agent-sdk not installed. Use the web-app venv:\n"
        "  virtual-jensen-web/.venv/bin/python scripts/ingest/agents/update_wiki.py ...\n"
    )
    sys.exit(2)


# ----- Source + target resolution -----

def load_sources_cfg() -> dict:
    with open(SOURCES_YAML) as f:
        return yaml.safe_load(f)


def find_source(cfg: dict, name: str) -> dict:
    """Search both interview_sources and wiki_sources for a name match."""
    for group_key in ("interview_sources", "wiki_sources"):
        for entry in cfg.get(group_key, []) or []:
            if entry.get("name") == name:
                out = dict(entry)
                out["_group"] = group_key
                return out
    raise SystemExit(
        f"source {name!r} not found in {SOURCES_YAML.name}. "
        "Check the exact `name:` spelling."
    )


def expand_targets(globs: list[str]) -> list[Path]:
    """Expand ``targets:`` globs under ``wiki/`` into concrete .md files."""
    seen: dict[Path, None] = {}
    for pattern in globs or []:
        # Accept "products/*", "products/*.md", or "competitors/amd.md".
        patterns = [pattern]
        if not pattern.endswith(".md"):
            patterns.append(pattern + ".md")
        for p in patterns:
            for match in sorted(WIKI_DIR.glob(p)):
                if match.is_file() and match.suffix == ".md":
                    seen[match] = None
    return list(seen.keys())


def load_items(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON array of items")
    return data


# ----- Prompts -----

SYSTEM_PROMPT = """You are the wiki-maintenance subagent for Virtual Jensen — an institutional-memory engine powering a Jensen Huang strategy-meeting persona. Take a batch of newly-discovered source items and propose precise, minimal edits to specific wiki pages.

## Hard rules

1. **Scope.** Edit ONLY pages listed under "Candidate pages" in the user prompt. If items don't belong on any candidate, say so — don't fabricate a target.
2. **Frontmatter.** Each page has a YAML block with at least `title`, `last_updated`, `freshness`, `category`. On any content change: bump `last_updated:` to today's date (in the user prompt). Do NOT change `freshness:` (evergreen / quarterly / fast-moving) unless a source explicitly justifies a re-tiering — and call it out in the rationale. Preserve all other fields verbatim.
3. **Citations.** New factual claims must cite the source: inline "(source: <url>, <date>)" on the sentence introducing the fact, or extend a bottom "## Sources" section with a bulleted URL.
4. **No fabrication.** Use only what the source items say. If an item is trivial, off-topic, or redundant, emit `NO CHANGE PROPOSED: <one-sentence rationale>` — don't invent edits to look productive.
5. **Minimal diffs.** Surgical edits over rewrites. If a bullet needs one number updated, edit just that line.

## Output format

For each page that changes, emit a fenced unified diff with the path on the opening fence:

```diff path=wiki/products/gpu-blackwell.md
--- a/wiki/products/gpu-blackwell.md
+++ b/wiki/products/gpu-blackwell.md
@@ -1,5 +1,5 @@
 ---
 title: Blackwell GPU Architecture
-last_updated: 2026-04-09
+last_updated: 2026-04-19
 freshness: quarterly
 category: products
```

Immediately after each diff, write a one-paragraph `Rationale:` — what changed, which item(s) drove it, any judgment calls. If nothing should change, emit one `NO CHANGE PROPOSED:` line and stop.

## Tools

- `Read` — inspect a candidate page before proposing a diff.
- `Grep` / `Glob` — check whether a fact is already represented.
- `WebSearch` — verify a claim or pull in missing context (e.g. exact dates).

You have no write tools. Your only output channel is proposed diffs on stdout; a human reviews every diff before anything lands.
"""


USER_PROMPT_TEMPLATE = """## Today's date
{today}

## Source
Name: {source_name}
Type: {source_type}
Tier (informational): {tier}
URL: {source_url}

## Candidate pages (you may edit ONLY these)
{candidate_list}

## New items to consider
```json
{items_json}
```

## Task

1. Read the candidate pages you think are relevant (pick what the items plausibly touch — you don't have to read all of them).
2. For each page that warrants an edit, emit a fenced diff block and a one-paragraph rationale, per the system prompt.
3. If no page should change, emit a single `NO CHANGE PROPOSED:` line with a brief reason.

Begin now. Thinking out loud is welcome, but diffs MUST be in the exact fenced format described.
"""


def build_user_prompt(
    *, source: dict, items: list[dict], candidates: list[Path],
    tier: Optional[str], today: str,
) -> str:
    if candidates:
        candidate_list = "\n".join(
            f"- {p.relative_to(REPO_ROOT).as_posix()}" for p in candidates
        )
    else:
        candidate_list = "(none — this source has no `targets:` globs or none matched)"
    return USER_PROMPT_TEMPLATE.format(
        today=today,
        source_name=source.get("name", "?"),
        source_type=source.get("type", "?"),
        tier=tier or source.get("tier") or "?",
        source_url=source.get("url") or source.get("handle") or "?",
        candidate_list=candidate_list,
        items_json=json.dumps(items, indent=2, ensure_ascii=False),
    )


# ----- SDK invocation -----

async def run_subagent(
    *, system: str, user: str, model: str, cli_path: Optional[str],
) -> str:
    opts_kwargs: dict[str, Any] = dict(
        system_prompt=system,
        allowed_tools=["Read", "Grep", "Glob", "WebSearch"],
        permission_mode="bypassPermissions",
        cwd=str(REPO_ROOT),
        model=model,
        include_partial_messages=False,
        setting_sources=None,
    )
    if cli_path:
        opts_kwargs["cli_path"] = cli_path
    opts = ClaudeAgentOptions(**opts_kwargs)

    full_text = ""
    async for msg in query(prompt=user, options=opts):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock) and block.text:
                    sys.stdout.write(block.text)
                    sys.stdout.flush()
                    full_text += block.text
        elif isinstance(msg, ResultMessage):
            break
    if not full_text.endswith("\n"):
        sys.stdout.write("\n")
        sys.stdout.flush()
    return full_text


def count_proposed_edits(output: str) -> int:
    """Count unique `path=wiki/...` annotations on diff fences."""
    seen: set[str] = set()
    for line in output.splitlines():
        s = line.strip()
        if not (s.startswith("```diff") and "path=" in s):
            continue
        tail = s.split("path=", 1)[1].strip().split()
        if tail:
            seen.add(tail[0])
    return len(seen)


# ----- Apply mode: parse fenced diffs, write files, commit on a branch -----

# Matches a fenced diff block opened with ```diff path=wiki/<...>.md and
# closed with a line containing only ```. Captures (path, body). The body
# excludes the opening fence line and the closing fence line. DOTALL so "."
# swallows newlines inside the diff body.
_DIFF_FENCE_RE = re.compile(
    r"^```diff[ \t]+path=(?P<path>\S+)[ \t]*\n(?P<body>.*?)\n```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)


def extract_diff_blocks(output: str) -> list[tuple[str, str, tuple[int, int]]]:
    """Return a list of (path, diff_body, (start, end)) from the subagent's output.

    ``start`` and ``end`` are character offsets into ``output`` covering the
    full fenced block (from the opening ```diff line through the closing ```).
    Callers use those offsets to slice out the "rationale" text between blocks.
    """
    blocks: list[tuple[str, str, tuple[int, int]]] = []
    for m in _DIFF_FENCE_RE.finditer(output):
        blocks.append((m.group("path"), m.group("body"), (m.start(), m.end())))
    return blocks


def extract_rationale(output: str, blocks: list[tuple[str, str, tuple[int, int]]]) -> str:
    """Concatenate the text between/around fenced diff blocks, trimmed.

    Includes any preamble before the first block and any trailing text after
    the last block. Collapses runs of blank lines to a single blank line.
    """
    if not blocks:
        return output.strip()
    pieces: list[str] = []
    prev_end = 0
    for _, _, (start, end) in blocks:
        pieces.append(output[prev_end:start])
        prev_end = end
    pieces.append(output[prev_end:])
    joined = "\n\n".join(p.strip() for p in pieces if p.strip())
    # Collapse 3+ consecutive newlines to 2.
    return re.sub(r"\n{3,}", "\n\n", joined).strip()


def _parse_hunks(diff_body: str) -> Optional[list[dict]]:
    """Parse a unified-diff body into a list of hunks.

    Returns a list of dicts with keys ``old_start``, ``old_count``,
    ``new_start``, ``new_count``, ``lines`` (list of lines including the
    leading ' ', '+', or '-'). Returns None if the body can't be parsed —
    caller should treat that as "skip this diff".
    """
    lines = diff_body.splitlines()
    i = 0
    # Skip the `--- a/...` and `+++ b/...` headers if present.
    while i < len(lines) and (lines[i].startswith("--- ") or lines[i].startswith("+++ ")):
        i += 1
    hunks: list[dict] = []
    hunk_header_re = re.compile(
        r"^@@ -(?P<os>\d+)(?:,(?P<oc>\d+))? \+(?P<ns>\d+)(?:,(?P<nc>\d+))? @@"
    )
    while i < len(lines):
        line = lines[i]
        if not line.startswith("@@"):
            # Allow blank lines between hunks, but any other stray content is fatal.
            if line.strip() == "":
                i += 1
                continue
            return None
        m = hunk_header_re.match(line)
        if not m:
            return None
        old_count = int(m.group("oc")) if m.group("oc") else 1
        new_count = int(m.group("nc")) if m.group("nc") else 1
        hunk = {
            "old_start": int(m.group("os")),
            "old_count": old_count,
            "new_start": int(m.group("ns")),
            "new_count": new_count,
            "lines": [],
        }
        i += 1
        consumed_old = 0
        consumed_new = 0
        while i < len(lines) and not lines[i].startswith("@@"):
            hl = lines[i]
            if hl.startswith("\\"):
                # "\ No newline at end of file" — tolerate and skip.
                i += 1
                continue
            if hl == "":
                # Some generators emit bare empty lines for context; treat as " ".
                hl = " "
            if hl[0] == " ":
                consumed_old += 1
                consumed_new += 1
            elif hl[0] == "-":
                consumed_old += 1
            elif hl[0] == "+":
                consumed_new += 1
            else:
                return None
            hunk["lines"].append(hl)
            i += 1
            if consumed_old >= old_count and consumed_new >= new_count:
                break
        if consumed_old != old_count or consumed_new != new_count:
            # Short/long hunk vs header — reject the whole diff rather than guess.
            return None
        hunks.append(hunk)
    return hunks or None


def _apply_hunks(original: list[str], hunks: list[dict]) -> Optional[list[str]]:
    """Apply a list of parsed hunks to ``original`` (list of lines, no newlines).

    Returns the new list of lines, or None if any hunk's context/removal lines
    don't match the current file content at the expected offset.
    """
    # Apply in reverse so earlier line numbers stay valid for later hunks.
    out = list(original)
    for hunk in sorted(hunks, key=lambda h: h["old_start"], reverse=True):
        old_start = hunk["old_start"]  # 1-based
        idx = old_start - 1 if hunk["old_count"] > 0 else old_start
        # Build the expected old-slice and the replacement new-slice.
        expected: list[str] = []
        replacement: list[str] = []
        for hl in hunk["lines"]:
            tag, text = hl[0], hl[1:]
            if tag == " ":
                expected.append(text)
                replacement.append(text)
            elif tag == "-":
                expected.append(text)
            elif tag == "+":
                replacement.append(text)
        end = idx + len(expected)
        if end > len(out):
            return None
        if out[idx:end] != expected:
            return None
        out[idx:end] = replacement
    return out


def apply_diff_to_file(wiki_root: Path, rel_path: str, diff_body: str) -> tuple[str, Optional[Path]]:
    """Apply one fenced diff to the file at ``wiki_root/<relative>``.

    ``rel_path`` is the value after ``path=`` on the opening fence — e.g.
    ``wiki/products/gpu-blackwell.md``. Returns (status, resolved_path) where
    status is one of "applied", "skip-outside-wiki", "skip-missing",
    "skip-parse-error", "skip-conflict".
    """
    repo_root = wiki_root.parent
    # Defense-in-depth path safety: must live under wiki/, no traversal.
    if not rel_path.startswith("wiki/"):
        return ("skip-outside-wiki", None)
    candidate = (repo_root / rel_path).resolve()
    try:
        candidate.relative_to(wiki_root.resolve())
    except ValueError:
        raise SystemExit(
            f"refusing to apply diff: path {rel_path!r} resolves outside {wiki_root}"
        )
    if not candidate.exists() or not candidate.is_file():
        return ("skip-missing", candidate)
    hunks = _parse_hunks(diff_body)
    if hunks is None:
        return ("skip-parse-error", candidate)
    original_text = candidate.read_text()
    # Preserve trailing-newline state: splitlines() drops it, so track it.
    had_trailing_nl = original_text.endswith("\n")
    original_lines = original_text.splitlines()
    new_lines = _apply_hunks(original_lines, hunks)
    if new_lines is None:
        return ("skip-conflict", candidate)
    new_text = "\n".join(new_lines)
    if had_trailing_nl or not new_text.endswith("\n"):
        new_text += "\n" if had_trailing_nl else ""
    if had_trailing_nl and not new_text.endswith("\n"):
        new_text += "\n"
    candidate.write_text(new_text)
    return ("applied", candidate)


def slugify_source(name: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        slug = "source"
    return slug[:limit].rstrip("-") or "source"


def _git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), check=check,
        capture_output=True, text=True,
    )


def _branch_exists(cwd: Path, name: str) -> bool:
    r = _git(["rev-parse", "--verify", "--quiet", f"refs/heads/{name}"],
             cwd=cwd, check=False)
    return r.returncode == 0


def _pick_branch_name(cwd: Path, base: str) -> str:
    if not _branch_exists(cwd, base):
        return base
    n = 2
    while True:
        candidate = f"{base}-{n}"
        if not _branch_exists(cwd, candidate):
            return candidate
        n += 1


def assert_tree_clean_outside_wiki(repo_root: Path) -> None:
    """Raise SystemExit if `git status --porcelain` shows changes outside wiki/."""
    r = _git(["status", "--porcelain"], cwd=repo_root)
    dirty: list[str] = []
    for line in r.stdout.splitlines():
        # Porcelain format: "XY path" (XY is 2 chars, then space, then path).
        if len(line) < 4:
            continue
        path = line[3:]
        # Strip rename arrows if any: "orig -> new".
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith("wiki/"):
            dirty.append(line)
    if dirty:
        sys.stderr.write(
            "refusing to --apply: working tree has changes outside wiki/:\n"
            + "\n".join(f"  {l}" for l in dirty)
            + "\nClean your working tree first, or pass --apply-allow-dirty.\n"
        )
        raise SystemExit(2)


def apply_and_commit(
    *, output: str, source_name: str, repo_root: Path,
    allow_dirty: bool,
) -> int:
    """Parse diffs from ``output``, apply them, commit on a fresh branch.

    Returns 0 on success (including the no-op case), non-zero on error.
    Prints the branch name as the last stdout line when a commit was made.
    """
    if not allow_dirty:
        assert_tree_clean_outside_wiki(repo_root)

    blocks = extract_diff_blocks(output)
    rationale = extract_rationale(output, blocks)

    applied: list[Path] = []
    skipped: list[tuple[str, str]] = []  # (reason, rel_path)
    for rel_path, body, _ in blocks:
        status, resolved = apply_diff_to_file(WIKI_DIR, rel_path, body)
        if status == "applied" and resolved is not None:
            applied.append(resolved)
        else:
            skipped.append((status, rel_path))

    for reason, rel_path in skipped:
        sys.stderr.write(f"  warning: {reason} for {rel_path}\n")

    if not applied:
        sys.stderr.write(
            f"apply: 0 files changed ({len(skipped)} skipped); no commit.\n"
        )
        print("no wiki edits proposed")
        return 0

    today = date.today().isoformat()
    base_branch = f"ingest/{today}-{slugify_source(source_name)}"
    branch = _pick_branch_name(repo_root, base_branch)

    _git(["checkout", "-b", branch], cwd=repo_root)
    rel_applied = [
        str(p.resolve().relative_to(repo_root.resolve())) for p in applied
    ]
    _git(["add", "--", *rel_applied], cwd=repo_root)

    status_after = _git(["status", "--porcelain", "--", *rel_applied], cwd=repo_root)
    if not status_after.stdout.strip():
        sys.stderr.write(
            "apply: files matched existing content after patching — nothing to commit.\n"
        )
        # Leave the empty branch checked out; caller can delete it. Still print it
        # so the caller isn't stranded on an unexpected branch.
        print(branch)
        return 0

    subject = f"wiki: update {source_name} ({len(applied)} pages)"
    body = rationale or "(no rationale provided by subagent)"
    commit_msg = f"{subject}\n\n{body}\n"
    _git(["commit", "-m", commit_msg], cwd=repo_root)

    sys.stderr.write(
        f"apply: committed {len(applied)} file(s) to branch {branch} "
        f"({len(skipped)} skipped)\n"
    )
    # LAST stdout line — caller parses this.
    print(branch)
    return 0


# ----- CLI -----

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Propose wiki edits for a batch of new source items via the Claude "
            "Agent SDK (Claude Opus 4.7). Dry-run by default: proposed unified "
            "diffs stream to stdout. Pass --apply to additionally write the "
            "diffs to disk and commit them on a fresh git branch."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  update_wiki.py --source 'NVIDIA Blog' --items new.json --tier daily\n",
    )
    ap.add_argument("--source", required=True,
                    help="Source name (must match a `name:` in scripts/ingest/sources.yaml).")
    ap.add_argument("--items", required=True, type=Path,
                    help="Path to a JSON file with new items (array of "
                         "{id, title, url, published, summary}). Compatible with run.py --json.")
    ap.add_argument("--tier", default=None,
                    help="Informational: the tier that triggered this run "
                         "(daily/weekly/monthly). Passed into the subagent prompt for context only.")
    ap.add_argument("--apply", action="store_true",
                    help="After streaming the subagent's proposed diffs, parse them, "
                         "apply them to files under wiki/, and commit on a fresh local "
                         "branch named ingest/YYYY-MM-DD-<source-slug>. Never pushes. "
                         "Refuses to run if the working tree has changes outside wiki/ "
                         "(override with --apply-allow-dirty).")
    ap.add_argument("--apply-allow-dirty", action="store_true",
                    help="Allow --apply even when the working tree has untracked or "
                         "modified files outside wiki/. Use with care.")
    ap.add_argument("--model", default="claude-opus-4-7",
                    help="Claude model for the subagent (default: claude-opus-4-7).")
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.apply and not args.apply_allow_dirty:
        # Fail fast before we burn SDK tokens.
        assert_tree_clean_outside_wiki(REPO_ROOT)

    if not args.items.exists():
        sys.stderr.write(f"--items file not found: {args.items}\n")
        return 1

    cfg = load_sources_cfg()
    source = find_source(cfg, args.source)
    targets = source.get("targets") or []
    candidates = expand_targets(targets) if targets else []

    items = load_items(args.items)
    if not items:
        print("NO CHANGE PROPOSED: --items file contained zero new items.")
        return 0

    today = date.today().isoformat()
    user_prompt = build_user_prompt(
        source=source, items=items, candidates=candidates,
        tier=args.tier, today=today,
    )

    mode_label = "apply" if args.apply else "dry-run"
    sys.stderr.write(
        f"update_wiki: source={source['name']!r} items={len(items)} "
        f"candidates={len(candidates)} model={args.model} ({mode_label})\n"
    )
    if not candidates:
        sys.stderr.write(
            "  warning: no candidate pages resolved from this source's targets "
            "globs — the subagent will likely emit NO CHANGE PROPOSED.\n"
        )

    cli_path = shutil.which("claude")
    if not cli_path:
        sys.stderr.write(
            "  warning: `claude` not on PATH — SDK will use its bundled CLI, "
            "which has no auth. Install Claude Code and `claude login` first.\n"
        )

    output = asyncio.run(run_subagent(
        system=SYSTEM_PROMPT, user=user_prompt,
        model=args.model, cli_path=cli_path,
    ))

    n = count_proposed_edits(output)
    sys.stderr.write(f"\nupdate_wiki: proposed edits to {n} page(s)\n")

    if args.apply:
        return apply_and_commit(
            output=output,
            source_name=source["name"],
            repo_root=REPO_ROOT,
            allow_dirty=args.apply_allow_dirty,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
