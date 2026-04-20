#!/usr/bin/env python3
"""Interview-extraction subagent for the Virtual Jensen knowledge-refresh pipeline.

Distills NEW quotes, mental models, analogies, and bets from a Jensen
transcript (plain text, VTT, or SRT) using Claude Opus 4.7 via the
Claude Agent SDK. Writes append-only entries to
``references/interviews-log.md``. Never edits SKILL.md; flags promotable
material with ``PROMOTE?`` for the human operator.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
SKILL_PATH = REPO_ROOT / "SKILL.md"
LOG_PATH = REPO_ROOT / "references" / "interviews-log.md"

LOG_HEADER = (
    "# Jensen Interviews — Append-Only Log\n\n"
    "Extracted from public appearances. Promotion to SKILL.md is a "
    "human decision.\n"
)

# Scrub the API key before spinning up the SDK so auth flows through the
# same Claude Code / Max OAuth path as the web app.
os.environ.pop("ANTHROPIC_API_KEY", None)

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
        "  virtual-jensen-web/.venv/bin/python "
        "scripts/ingest/agents/extract_interview.py --help\n"
    )
    sys.exit(2)


_TIMESTAMP_RE = re.compile(
    r"^\s*\d{1,2}:\d{2}(?::\d{2})?[.,]?\d*\s*-->\s*"
    r"\d{1,2}:\d{2}(?::\d{2})?[.,]?\d*.*$"
)
_SRT_INDEX_RE = re.compile(r"^\s*\d+\s*$")


def _strip_transcript(raw: str) -> str:
    """Drop VTT headers, SRT indices, timestamp arrows; collapse blanks."""
    cleaned: list[str] = []
    for ln in raw.splitlines():
        s = ln.rstrip()
        if not s:
            cleaned.append("")
            continue
        if s.upper().startswith("WEBVTT") or s.startswith("NOTE ") or s == "NOTE":
            continue
        if _TIMESTAMP_RE.match(s) or _SRT_INDEX_RE.match(s):
            continue
        cleaned.append(s)
    out: list[str] = []
    blank = False
    for ln in cleaned:
        is_blank = not ln.strip()
        if is_blank and blank:
            continue
        blank = is_blank
        out.append(ln)
    return "\n".join(out).strip()


SYSTEM_PROMPT = """\
You are the Interview Extraction subagent for Virtual Jensen. You
distill what's NEW in Jensen Huang's thinking from one appearance so the
reasoning engine stays current.

HARD RULES
1. Output ONLY the append-only markdown entry below. No preamble, no
   closing remarks, no outer code fences.
2. Emit ONLY material NEW relative to the provided SKILL.md AND the
   existing interviews-log.md. Skip anything already covered, even if
   paraphrased there.
3. NEVER fabricate. Every quote MUST be a verbatim substring of the
   transcript.
4. NEVER edit SKILL.md. You have no Edit tool. Framework-worthy material
   goes under "Framework candidates (PROMOTE?)" prefixed `PROMOTE?`.
5. If there is genuinely no new material, emit exactly one line and
   nothing else:
   `## {date} — {source-name} — no new material (already covered)`

OUTPUT SHAPE (omit empty sections):
## YYYY-MM-DD — {source-name}
🔗 {source-url}

### New quotes
> "verbatim quote from transcript"
> — Jensen, @HH:MM:SS context

### New mental models
- concise reasoning pattern not already in SKILL.md

### New analogies
- ...

### New bets / positions
- ...

### Framework candidates (PROMOTE?)
- PROMOTE? items that might warrant promotion to SKILL.md

STYLE: terse. Jensen's voice in quotes, tight neutral voice elsewhere.
If no timestamp, use a short context tag (e.g. `@on-export-controls`).
Prefer one sharp bullet over three blurry ones.
"""


def _build_user_prompt(
    *,
    source_name: str,
    source_url: str,
    published: str,
    transcript: str,
    skill_md: str,
    existing_log: Optional[str],
) -> str:
    log_block = (
        existing_log.strip()
        if existing_log and existing_log.strip()
        else "(empty — first entry; driver will add the file header)"
    )
    return (
        f"## Source metadata\n"
        f"- name: {source_name}\n"
        f"- url: {source_url}\n"
        f"- published: {published}\n\n"
        f"## Existing SKILL.md (reasoning framework — do not duplicate)\n"
        f"```markdown\n{skill_md.strip()}\n```\n\n"
        f"## Existing interviews-log.md (do not duplicate)\n"
        f"```markdown\n{log_block}\n```\n\n"
        f"## Transcript (timestamps stripped where obvious)\n"
        f"```\n{transcript}\n```\n\n"
        f"Produce the append-only entry now. Remember: NEW material only, "
        f"verbatim quotes only, no SKILL.md edits."
    )


async def _run_extraction(
    *, system: str, user: str, model: str, cli_path: Optional[str]
) -> str:
    kw = dict(
        system_prompt=system, allowed_tools=["Read"],
        permission_mode="bypassPermissions", cwd=str(REPO_ROOT), model=model,
        include_partial_messages=False, setting_sources=None,
    )
    if cli_path:
        kw["cli_path"] = cli_path
    full = ""
    async for msg in query(prompt=user, options=ClaudeAgentOptions(**kw)):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    sys.stdout.write(b.text)
                    sys.stdout.flush()
                    full += b.text
        elif isinstance(msg, ResultMessage):
            break
    if full and not full.endswith("\n"):
        sys.stdout.write("\n")
        sys.stdout.flush()
    return full.strip()


def _strip_fences(text: str) -> str:
    """If the model wrapped the whole entry in ```...```, unwrap it."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:markdown|md)?\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s)
    return s.strip()


def _append_to_log(entry: str) -> None:
    entry = _strip_fences(entry)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text(LOG_HEADER, encoding="utf-8")
    existing = LOG_PATH.read_text(encoding="utf-8")
    sep = "\n\n---\n\n" if existing.strip() else "\n"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(sep)
        f.write(entry.rstrip() + "\n")


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Extract NEW Jensen material from an interview transcript."
    )
    ap.add_argument("--transcript", required=True,
                    help="UTF-8 transcript (plain text, VTT, or SRT).")
    ap.add_argument("--source-name", required=True,
                    help='e.g. "Acquired FM — Jensen Huang (2026)".')
    ap.add_argument("--source-url", required=True, help="Canonical URL.")
    ap.add_argument("--published", required=True, help="ISO date YYYY-MM-DD.")
    ap.add_argument("--apply", action="store_true",
                    help="Append to references/interviews-log.md (default: "
                         "dry-run — print only).")
    ap.add_argument("--model", default="claude-opus-4-7",
                    help="Subagent model (default: claude-opus-4-7).")
    return ap.parse_args()


async def _amain(args: argparse.Namespace) -> int:
    transcript_path = Path(args.transcript).expanduser().resolve()
    if not transcript_path.is_file():
        sys.stderr.write(f"Transcript not found: {transcript_path}\n")
        return 1
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.published):
        sys.stderr.write("--published must be YYYY-MM-DD.\n")
        return 1
    if not SKILL_PATH.is_file():
        sys.stderr.write(f"SKILL.md not found at {SKILL_PATH}\n")
        return 1

    transcript = _strip_transcript(
        transcript_path.read_text(encoding="utf-8", errors="replace")
    )
    if len(transcript) < 200:
        sys.stderr.write(
            f"Transcript too short after cleanup ({len(transcript)} chars).\n"
        )
        return 1

    skill_md = SKILL_PATH.read_text(encoding="utf-8")
    existing_log = (
        LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.is_file() else None
    )

    user_prompt = _build_user_prompt(
        source_name=args.source_name,
        source_url=args.source_url,
        published=args.published,
        transcript=transcript,
        skill_md=skill_md,
        existing_log=existing_log,
    )

    mode = "APPLY" if args.apply else "DRY-RUN"
    sys.stderr.write(
        f"[extract_interview] mode={mode} model={args.model} "
        f"transcript={transcript_path.name} ({len(transcript)} chars) "
        f"log={'exists' if existing_log else 'new'}\n"
        f"{'-' * 60}\n"
    )

    try:
        entry = await _run_extraction(
            system=SYSTEM_PROMPT, user=user_prompt, model=args.model,
            cli_path=shutil.which("claude"),
        )
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"\nSubagent call failed: {type(e).__name__}: {e}\n")
        return 2

    sys.stderr.write(f"{'-' * 60}\n")
    if not entry:
        sys.stderr.write("Subagent returned no text. Nothing written.\n")
        return 2

    if args.apply:
        _append_to_log(entry)
        sys.stderr.write(f"Appended entry to {LOG_PATH}\n")
    else:
        sys.stderr.write("Dry-run: re-run with --apply to persist.\n")
    return 0


def main() -> int:
    return asyncio.run(_amain(_parse_args()))


if __name__ == "__main__":
    sys.exit(main())
