#!/usr/bin/env python3
"""LLM-judge grader for benchmark runs.

Reads a run record written by ``run.py`` and, for each Jensen turn,
calls Haiku 4.5 (via the Claude Agent SDK, so auth is via Claude Code
OAuth just like the web app) to score on the dimensions listed in
``rubrics.yaml``. Writes grades back into the same JSON file.

The judge is explicitly NOT the same model family as the responder —
grading Opus with Opus would produce biased self-assessment.

Example:
    scripts/bench/grade.py                        # latest run
    scripts/bench/grade.py --file history/2026-04-20T10-00-00Z.json
    scripts/bench/grade.py --dry-run              # show the prompts, don't call
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
HISTORY_DIR = HERE / "history"

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("Install pyyaml: pip install pyyaml\n")
    sys.exit(2)

# Scrub the API key before we spin up the Claude Agent SDK, so it uses
# the same Claude Code / Max OAuth path as the web app.
os.environ.pop("ANTHROPIC_API_KEY", None)

try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        StreamEvent,
        TextBlock,
        query,
    )
except ImportError:
    sys.stderr.write(
        "claude-agent-sdk not installed. Use the web-app venv:\n"
        "  virtual-jensen-web/.venv/bin/python scripts/bench/grade.py\n"
    )
    sys.exit(2)


def _latest_history() -> Optional[Path]:
    files = sorted(HISTORY_DIR.glob("*.json"))
    return files[-1] if files else None


# Dimensions that presuppose the user has already triggered something
# specific (asked a fact question, requested a debrief, disagreed with
# Jensen). Grading these on the opener turn — where nothing has happened
# yet — produces false-negative 0/1 scores. Only score them on the final
# turn of each case.
_LAST_TURN_DIMS = {
    "tool_use_appropriateness",
    "factual_grounding",
    "pushback_specificity",
}


def _active_dimensions(case: dict, turn: dict, turn_index: int, total_turns: int) -> list[str]:
    """Filter case['rubric'] down to the dimensions that apply to *this* turn."""
    requested = case.get("rubric", []) or []
    is_last = turn_index == total_turns - 1
    return [d for d in requested if d not in _LAST_TURN_DIMS or is_last]


def _judge_prompt(case: dict, turn: dict, active_dims: list[str], rubric_cfg: dict) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the judge call."""
    dimension_block = []
    for dim in active_dims:
        d = rubric_cfg["dimensions"].get(dim)
        if not d:
            continue
        dimension_block.append(
            f"### {dim} — {d['title']}\n{d['rubric'].strip()}"
        )
    anchor_section = ""
    if case.get("anchor") and turn["kind"] == "opener":
        anchor_section = (
            "\n## Anchor — a 4/4 response looks roughly like this\n"
            "```\n" + case["anchor"].strip() + "\n```\n"
        )

    system = (
        "You are a strict, unbiased grader. You are NOT playing Jensen. "
        "You are scoring an AI impersonation of Jensen Huang against a rubric. "
        "Produce ONLY a single JSON object. No prose, no markdown fences.\n\n"
        "Each dimension you're asked about gets:\n"
        '  {"score": 0..4, "evidence": "<verbatim quote from the response, or empty>", "reason": "<one short sentence>"}\n'
        "\n"
        "Evidence must be an exact substring of the response (or the empty string "
        "if score is 0). Never invent quotes."
    )

    user = (
        f"## Case: {case['id']} — {case.get('label', '')}\n"
        f"Mode: {case.get('mode', 'sharp')}\n"
        f"User turn: {turn.get('user_input') or '[opening — /api/start]'}\n\n"
        f"## Jensen's response\n```\n{turn['response_text']}\n```\n\n"
        f"## Tools used in this turn\n{json.dumps(turn.get('tool_uses') or [], indent=2)}\n\n"
        f"## Rubric dimensions to score\n" + "\n\n".join(dimension_block) + "\n"
        + anchor_section
        + "\nReturn a JSON object with one key per dimension listed above, "
        + "plus a top-level \"overall_note\" field (one sentence)."
    )
    return system, user


async def _judge_turn(system: str, user: str, model: str, cli_path: Optional[str]) -> dict:
    opts_kwargs = dict(
        system_prompt=system,
        allowed_tools=[],
        permission_mode="bypassPermissions",
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
            for b in msg.content:
                if isinstance(b, TextBlock):
                    full_text += b.text
        elif isinstance(msg, ResultMessage):
            break

    # Strip accidental fences.
    cleaned = full_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?|\n?```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"_parse_error": "judge returned non-JSON", "_raw": full_text[:2000]}


async def grade_run(record: dict, *, rubric_cfg: dict, dry_run: bool = False) -> dict:
    judge_model = rubric_cfg.get("judge_model", "claude-haiku-4-5")
    cli_path = shutil.which("claude")
    n_graded = 0

    for case in record["cases"]:
        total = len(case["turns"])
        for i, turn in enumerate(case["turns"]):
            if turn.get("error") or not turn.get("response_text"):
                continue
            active = _active_dimensions(case, turn, i, total)
            if not active:
                # This turn has nothing scoreable in this case's rubric.
                turn["llm_judge"] = {"model": judge_model, "scores": {}, "skipped": True}
                continue
            system, user = _judge_prompt(case, turn, active, rubric_cfg)
            if dry_run:
                print(f"\n--- {case['id']} / {turn['kind']} (dims={active}) ---\n{user[:800]}…")
                continue
            print(f"  grading {case['id']} / {turn['kind']} "
                  f"({len(active)} dim) …", end="", flush=True)
            try:
                scores = await _judge_turn(system, user, judge_model, cli_path)
            except Exception as e:  # noqa: BLE001
                scores = {"_error": f"{type(e).__name__}: {e}"}
            turn["llm_judge"] = {"model": judge_model, "scores": scores, "dims": active}
            n_graded += 1
            print(" ok" if "_error" not in scores and "_parse_error" not in scores else " ERR")

    record["grading"] = {
        "judge_model": judge_model,
        "turns_graded": n_graded,
        "rubric_source": "scripts/bench/rubrics.yaml",
    }
    return record


def _aggregate(record: dict) -> None:
    """Fill record['summary']['llm_avg'] with per-dimension averages."""
    totals: dict[str, list[int]] = {}
    for case in record["cases"]:
        for turn in case["turns"]:
            scores = (turn.get("llm_judge") or {}).get("scores") or {}
            for dim, payload in scores.items():
                if not isinstance(payload, dict):
                    continue
                v = payload.get("score")
                if isinstance(v, (int, float)):
                    totals.setdefault(dim, []).append(int(v))
    avg = {
        dim: round(sum(vs) / len(vs), 2) for dim, vs in totals.items() if vs
    }
    record.setdefault("summary", {})["llm_avg"] = avg


async def _amain(args) -> int:
    target = Path(args.file) if args.file else _latest_history()
    if not target or not target.exists():
        sys.stderr.write("No run record found. Run scripts/bench/run.py first.\n")
        return 1

    with open(target) as f:
        record = json.load(f)

    with open(HERE / "rubrics.yaml") as f:
        rubric_cfg = yaml.safe_load(f)

    print(f"Grading: {target.name}  (judge={rubric_cfg.get('judge_model')})")
    record = await grade_run(record, rubric_cfg=rubric_cfg, dry_run=args.dry_run)
    if args.dry_run:
        return 0

    _aggregate(record)

    with open(target, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f"\nSaved grades into {target.name}")
    if record.get("summary", {}).get("llm_avg"):
        print("Per-dimension averages:")
        for dim, v in sorted(record["summary"]["llm_avg"].items()):
            print(f"  {dim:28s} {v}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Specific run record; defaults to most recent.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show the judge prompts but don't call the model.")
    args = ap.parse_args()
    return asyncio.run(_amain(args))


if __name__ == "__main__":
    sys.exit(main())
