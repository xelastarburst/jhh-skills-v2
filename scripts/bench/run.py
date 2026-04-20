#!/usr/bin/env python3
"""Virtual Jensen benchmark runner.

Drives scripted cases through the live web app (localhost:8000 by default),
captures each Jensen turn, runs deterministic checks, and writes one run
record to ``scripts/bench/history/<timestamp>.json``.

Grading via the LLM judge is a separate step — ``grade.py`` consumes the
record this writes. Splitting the two means you can re-grade old runs
against a new rubric without replaying the full transcript.

Example:
    scripts/bench/run.py                       # all cases, default base URL
    scripts/bench/run.py --only opener,debrief-request
    scripts/bench/run.py --base http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional
from urllib import error, request

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
HISTORY_DIR = HERE / "history"
HISTORY_DIR.mkdir(exist_ok=True)

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("Install pyyaml: pip install pyyaml\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Deterministic checks
# ---------------------------------------------------------------------------

_AI_DISCLAIMERS = re.compile(
    r"\b(as an ai|i'm claude|i am claude|as a large language model|"
    r"i'm an assistant|i don't have access to real-time)\b",
    re.IGNORECASE,
)

_SIGNATURE_PHRASES = [
    "let me reason",
    "the question is",
    "who specifically",
    "commodity",
    "what's the architecture",
    "speed of light",
    "it turns out",
    "this is a very big idea",
    "of course",
    "has something changed",
]

_APOLOGY = re.compile(
    r"\b(i apologize|sorry for (being|the)|let me tone (it|that) down|"
    r"i'll (back off|ease up))\b",
    re.IGNORECASE,
)

_PUSHBACK_VAGUE = re.compile(
    r"(\bspecifically\b|\bname them\b|\bwho has\b|"
    r"\b(that's|it's|this is) (not )?an? (category|symptom|tool|wish)\b|"
    r"\bthat's a category\b|\bthat's not (a|an) (answer|problem|business)\b|"
    r"\bgive me the real\b|\bbe concrete\b|\byou're describing\b|"
    r"\bthat's a hope, not\b)",
    re.IGNORECASE,
)

_PUSHBACK_MULTI = re.compile(
    r"(\bpick one\b|\bcan't do three\b|\byou can't do three\b|"
    r"\breasoning chain is strongest\b|\bthree ideas means\b|"
    r"\bmenu\b|\bhobby list\b|\bzero commitment\b|"
    r"\bwhich one\b|\bthe one that keeps you up\b)",
    re.IGNORECASE,
)

_WHY_NOW = re.compile(
    r"(\bwhy now\b|\bhas something changed\b|\bwhat changed\b|"
    r"\bwhat has changed\b|\bwhy will .{0,30} emerge\b|"
    r"\bwhy is this possible now\b)",
    re.IGNORECASE,
)

_DEBRIEF_MARKERS = [
    "Reasoning Chain Strength",
    "Framework Steps",
]

_NO_CAPITULATION = re.compile(
    r"(\bconvince me\b|\bmake the case\b|\bokay,? show me\b|\bprove it\b|"
    r"\bchange my mind\b|\bshow me why\b|\bmake me see it\b|"
    r"\bbefore i say (a single thing|anything|whether)\b|"
    r"\bi need to understand\b|\byou think you're right\b)",
    re.IGNORECASE,
)


def _first_person_ratio(text: str) -> float:
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return 0.0
    first = sum(1 for t in tokens if t in {"i", "me", "my", "we", "our"})
    return first / len(tokens)


def run_checks(response_text: str, response_tools: list[dict], checks: list[str]) -> dict:
    """Return {check_name: {passed: bool, reason: str}}."""
    out: dict[str, dict] = {}
    for name in checks:
        try:
            out[name] = CHECKS[name](response_text, response_tools)
        except KeyError:
            out[name] = {"passed": False, "reason": f"unknown check: {name}"}
    return out


def _check_no_ai_disclaimer(text: str, _tools: list[dict]) -> dict:
    m = _AI_DISCLAIMERS.search(text)
    return {"passed": not m, "reason": f"matched {m.group(0)!r}" if m else "clean"}


def _check_first_person(text: str, _tools: list[dict]) -> dict:
    ratio = _first_person_ratio(text)
    return {
        "passed": ratio >= 0.015,  # a few first-person words in a normal-length reply
        "reason": f"first-person ratio {ratio:.3f}",
    }


def _check_signature_phrase(text: str, _tools: list[dict]) -> dict:
    low = text.lower()
    hits = [p for p in _SIGNATURE_PHRASES if p in low]
    return {
        "passed": bool(hits),
        "reason": f"matched: {hits}" if hits else "no Jensen signature phrase",
    }


def _check_asks_question(text: str, _tools: list[dict]) -> dict:
    # Jensen asks at least one direct question per turn (usually more).
    qcount = text.count("?")
    return {"passed": qcount >= 1, "reason": f"{qcount} question marks"}


def _check_mentions_whiteboard(text: str, _tools: list[dict]) -> dict:
    m = re.search(r"\bwhiteboard\b", text, re.IGNORECASE)
    return {"passed": bool(m), "reason": "whiteboard mentioned" if m else "no whiteboard reference"}


def _check_no_apology(text: str, _tools: list[dict]) -> dict:
    m = _APOLOGY.search(text)
    return {"passed": not m, "reason": f"apologized: {m.group(0)!r}" if m else "no apology"}


def _check_pushback_on_vague(text: str, _tools: list[dict]) -> dict:
    m = _PUSHBACK_VAGUE.search(text)
    return {"passed": bool(m), "reason": f"matched {m.group(0)!r}" if m else "no specificity push"}


def _check_pushback_on_multi_idea(text: str, _tools: list[dict]) -> dict:
    m = _PUSHBACK_MULTI.search(text)
    return {"passed": bool(m), "reason": f"matched {m.group(0)!r}" if m else "didn't force a pick"}


def _check_mentions_why_now(text: str, _tools: list[dict]) -> dict:
    m = _WHY_NOW.search(text)
    return {"passed": bool(m), "reason": "'why now' present" if m else "missing 'why now'"}


def _check_used_wiki_tool(_text: str, tools: list[dict]) -> dict:
    wiki_tools = {"Read", "Grep", "Glob"}
    used = [t["name"] for t in tools if t.get("name") in wiki_tools]
    return {
        "passed": bool(used),
        "reason": f"wiki tools: {used}" if used else "no wiki tool used",
    }


def _check_used_web_tool(_text: str, tools: list[dict]) -> dict:
    web = [t["name"] for t in tools if t.get("name") in {"WebSearch", "WebFetch"}]
    return {
        "passed": bool(web),
        "reason": f"web tools: {web}" if web else "no web tool used",
    }


def _check_debrief_structure(text: str, _tools: list[dict]) -> dict:
    missing = [m for m in _DEBRIEF_MARKERS if m not in text]
    has_rating = bool(re.search(r"⚡|✅|⚠️", text))
    ok = not missing and has_rating
    return {
        "passed": ok,
        "reason": f"missing={missing} has_rating={has_rating}",
    }


def _check_no_capitulation(text: str, _tools: list[dict]) -> dict:
    m = _NO_CAPITULATION.search(text)
    return {
        "passed": bool(m),
        "reason": f"matched {m.group(0)!r}" if m else "no 'convince me' style",
    }


CHECKS = {
    "no_ai_disclaimer": _check_no_ai_disclaimer,
    "first_person": _check_first_person,
    "signature_phrase": _check_signature_phrase,
    "asks_question": _check_asks_question,
    "mentions_whiteboard": _check_mentions_whiteboard,
    "no_apology": _check_no_apology,
    "pushback_on_vague": _check_pushback_on_vague,
    "pushback_on_multi_idea": _check_pushback_on_multi_idea,
    "mentions_why_now": _check_mentions_why_now,
    "used_wiki_tool": _check_used_wiki_tool,
    "used_web_tool": _check_used_web_tool,
    "debrief_structure": _check_debrief_structure,
    "no_capitulation": _check_no_capitulation,
}


# ---------------------------------------------------------------------------
# SSE client
# ---------------------------------------------------------------------------

@dataclass
class Turn:
    kind: str                       # "opener" | "user_message"
    user_input: Optional[str]
    response_text: str = ""
    tool_uses: list[dict] = field(default_factory=list)
    latency_ms_first_token: Optional[int] = None
    latency_ms_total: Optional[int] = None
    error: Optional[str] = None


def _post_sse(url: str, body: dict, cookies: dict) -> tuple[Turn, dict]:
    """POST and stream SSE. Returns (Turn, updated_cookies)."""
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    req = request.Request(url, data=data, headers=headers, method="POST")
    turn = Turn(kind="sse", user_input=body.get("message") or body.get("__opener__"))

    t0 = time.monotonic()
    first_token_ms: Optional[float] = None

    try:
        resp = request.urlopen(req, timeout=120)
    except error.HTTPError as e:
        turn.error = f"HTTP {e.code} {e.reason}"
        return turn, cookies
    except error.URLError as e:
        turn.error = f"URLError: {e.reason}"
        return turn, cookies

    # Capture Set-Cookie
    new_cookies = dict(cookies)
    for header_val in resp.headers.get_all("Set-Cookie") or []:
        kv = header_val.split(";", 1)[0]
        if "=" in kv:
            k, v = kv.split("=", 1)
            new_cookies[k.strip()] = v.strip()

    pending_tool_calls: dict[str, dict] = {}
    buffer = ""
    while True:
        chunk = resp.read1(4096)
        if not chunk:
            break
        buffer += chunk.decode("utf-8", errors="replace")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line or not line.startswith("data: "):
                continue
            try:
                ev = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            if "error" in ev:
                turn.error = ev["error"]
                break
            if "text" in ev:
                if first_token_ms is None:
                    first_token_ms = (time.monotonic() - t0) * 1000
                turn.response_text += ev["text"]
            elif "tool_use" in ev:
                tu = ev["tool_use"]
                tid = tu.get("id")
                if tid:
                    pending_tool_calls[tid] = {"id": tid, "name": tu.get("name"), "label": tu.get("label")}
            elif "tool_use_update" in ev:
                tu = ev["tool_use_update"]
                tid = tu.get("id")
                if tid:
                    pending_tool_calls.setdefault(tid, {"id": tid})
                    pending_tool_calls[tid].update({"name": tu.get("name"), "label": tu.get("label")})
            elif ev.get("done"):
                break
        if turn.error:
            break

    turn.tool_uses = list(pending_tool_calls.values())
    turn.latency_ms_first_token = int(first_token_ms) if first_token_ms is not None else None
    turn.latency_ms_total = int((time.monotonic() - t0) * 1000)
    return turn, new_cookies


# ---------------------------------------------------------------------------
# Case runner
# ---------------------------------------------------------------------------

def _split_checks(checks: list[str]) -> tuple[list[str], list[str]]:
    """Universal checks run on every Jensen turn; last-turn-only checks run
    only on the final turn (they presuppose the user triggered something
    specific — a wiki fact question, a debrief request, etc.)."""
    LAST_TURN_ONLY = {
        "used_wiki_tool",
        "used_web_tool",
        "debrief_structure",
        "pushback_on_multi_idea",
        "mentions_why_now",
        "no_capitulation",
        "no_apology",
        "pushback_on_vague",
    }
    universal = [c for c in checks if c not in LAST_TURN_ONLY]
    last_only = [c for c in checks if c in LAST_TURN_ONLY]
    return universal, last_only


def run_case(case: dict, base: str, *, default_model: str) -> dict:
    model = case.get("model") or default_model
    mode = case.get("mode", "sharp")
    scripted_turns = list(case.get("turns") or [])
    universal_checks, last_turn_checks = _split_checks(list(case.get("checks") or []))
    total_turns = 1 + len(scripted_turns)  # opener + scripted

    turns_out: list[dict] = []
    cookies: dict[str, str] = {}

    def checks_for_turn(idx: int) -> list[str]:
        if idx == total_turns - 1:
            return universal_checks + last_turn_checks
        return universal_checks

    # 1. /api/start — always first
    opener_turn, cookies = _post_sse(
        f"{base}/api/start",
        {"model": model, "mode": mode, "__opener__": "[opener]"},
        cookies,
    )
    checks_run = run_checks(opener_turn.response_text, opener_turn.tool_uses, checks_for_turn(0))
    turns_out.append({
        "kind": "opener",
        "user_input": None,
        "response_text": opener_turn.response_text,
        "tool_uses": opener_turn.tool_uses,
        "latency_ms_first_token": opener_turn.latency_ms_first_token,
        "latency_ms_total": opener_turn.latency_ms_total,
        "checks": checks_run,
        "error": opener_turn.error,
    })

    # 2. Scripted /api/chat turns
    for i, user_msg in enumerate(scripted_turns, start=1):
        if opener_turn.error:
            break
        chat_turn, cookies = _post_sse(
            f"{base}/api/chat",
            {"message": user_msg, "model": model, "mode": mode},
            cookies,
        )
        checks_run = run_checks(chat_turn.response_text, chat_turn.tool_uses, checks_for_turn(i))
        turns_out.append({
            "kind": "user_message",
            "user_input": user_msg,
            "response_text": chat_turn.response_text,
            "tool_uses": chat_turn.tool_uses,
            "latency_ms_first_token": chat_turn.latency_ms_first_token,
            "latency_ms_total": chat_turn.latency_ms_total,
            "checks": checks_run,
            "error": chat_turn.error,
        })

    # 3. Clean up the session server-side so we don't leak ClaudeSDKClients.
    try:
        req = request.Request(
            f"{base}/api/new-meeting",
            headers={"Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items())},
            method="POST",
        )
        request.urlopen(req, timeout=10).read()
    except Exception:
        pass

    return {
        "id": case["id"],
        "label": case.get("label", case["id"]),
        "mode": mode,
        "model": model,
        "turns": turns_out,
        "rubric": case.get("rubric", []),
        "anchor": case.get("anchor"),
    }


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _summarize(run: dict) -> dict:
    total = 0
    passed = 0
    check_breakdown: dict[str, dict[str, int]] = {}
    for case in run["cases"]:
        for t in case["turns"]:
            for name, res in (t.get("checks") or {}).items():
                total += 1
                bucket = check_breakdown.setdefault(name, {"passed": 0, "failed": 0})
                if res.get("passed"):
                    passed += 1
                    bucket["passed"] += 1
                else:
                    bucket["failed"] += 1
    return {
        "check_pass_rate": round(passed / total, 3) if total else 0.0,
        "checks_total": total,
        "checks_passed": passed,
        "check_breakdown": check_breakdown,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000",
                    help="Web app base URL (server must be running).")
    ap.add_argument("--only", default="",
                    help="Comma-separated case ids to run (default: all).")
    ap.add_argument("--model", default="claude-sonnet-4-6",
                    help="Default model for cases that don't override it.")
    ap.add_argument("--tag", default="",
                    help="Optional tag stored in the run record (e.g. 'post-prompt-tweak').")
    ap.add_argument("--cases-file", default=str(HERE / "cases.yaml"))
    args = ap.parse_args()

    with open(args.cases_file) as f:
        cfg = yaml.safe_load(f)
    cases = cfg.get("cases", [])
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        cases = [c for c in cases if c["id"] in wanted]
        if not cases:
            print(f"No cases matched --only={args.only}", file=sys.stderr)
            return 1

    run = {
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": _git_sha(),
        "tag": args.tag,
        "base": args.base,
        "default_model": args.model,
        "cases": [],
    }

    for case in cases:
        print(f"\n> {case['id']} — {case.get('label', '')}")
        t0 = time.monotonic()
        case_result = run_case(case, args.base, default_model=args.model)
        dt = time.monotonic() - t0
        # Print one-liner summary
        n_turns = len(case_result["turns"])
        errors = sum(1 for t in case_result["turns"] if t.get("error"))
        checks_passed = sum(
            1 for t in case_result["turns"] for r in (t.get("checks") or {}).values() if r.get("passed")
        )
        checks_total = sum(
            len(t.get("checks") or {}) for t in case_result["turns"]
        )
        print(f"  turns={n_turns} errors={errors} checks={checks_passed}/{checks_total} ({dt:.1f}s)")
        run["cases"].append(case_result)

    run["summary"] = _summarize(run)
    stamp = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
    out = HISTORY_DIR / f"{stamp}.json"
    with open(out, "w") as f:
        json.dump(run, f, indent=2, ensure_ascii=False)
    print(f"\nSaved run: {out}")
    print(f"Overall deterministic-check pass rate: "
          f"{run['summary']['check_pass_rate']:.1%} "
          f"({run['summary']['checks_passed']}/{run['summary']['checks_total']})")
    print("Next: scripts/bench/grade.py  to add LLM-judge scores to this record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
