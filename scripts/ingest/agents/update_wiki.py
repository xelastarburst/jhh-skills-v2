#!/usr/bin/env python3
"""Wiki-update subagent driver for the Virtual Jensen ingestion pipeline.

Given a set of new source items (from the ingestion fetchers) and the
source's ``targets:`` glob(s) in ``sources.yaml``, invoke Claude Opus 4.7
via the Claude Agent SDK to propose edits to specific pages under ``wiki/``.

**Dry-run only.** Proposed diffs stream to stdout; nothing on disk is
modified. ``--apply`` raises ``NotImplementedError`` — a later commit wires
actual file writes + git-branch automation.

Examples:
    update_wiki.py --source "NVIDIA Blog" --items items.json
    update_wiki.py --source "AMD Newsroom" --items items.json --tier weekly

``--items`` is a JSON array of objects with ``id``, ``title``, ``url``,
``published``, ``summary`` — compatible with ``run.py --json``'s ``new:``
entries. Extra keys pass through verbatim.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
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


# ----- CLI -----

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Propose wiki edits for a batch of new source items via the Claude "
            "Agent SDK (Claude Opus 4.7). DRY-RUN ONLY: proposed unified diffs "
            "stream to stdout; no files are modified. --apply raises "
            "NotImplementedError (apply-mode is a later commit)."
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
                    help="[NOT IMPLEMENTED] Raises NotImplementedError. A later commit "
                         "will wire file writes + git-branch automation. For now, only "
                         "dry-run is supported — proposed diffs always go to stdout.")
    ap.add_argument("--model", default="claude-opus-4-7",
                    help="Claude model for the subagent (default: claude-opus-4-7).")
    return ap


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.apply:
        raise NotImplementedError(
            "--apply is not implemented yet. This subagent is dry-run only: it "
            "emits proposed unified diffs on stdout. A follow-up commit will wire "
            "actual file writes and git-branch automation."
        )

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

    sys.stderr.write(
        f"update_wiki: source={source['name']!r} items={len(items)} "
        f"candidates={len(candidates)} model={args.model} (dry-run)\n"
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
