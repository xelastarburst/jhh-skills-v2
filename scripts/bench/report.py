#!/usr/bin/env python3
"""Trend report: compare the latest bench run against prior runs.

Flags regressions in deterministic-check pass rate and LLM-judge
dimension averages. Exits 1 if anything regressed beyond the threshold,
so this can be wired into a pre-commit hook later.

Example:
    scripts/bench/report.py                    # latest vs previous
    scripts/bench/report.py --window 5         # latest vs median of last 5
    scripts/bench/report.py --threshold 0.5    # fail if any dim drops ≥0.5 pt
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
HISTORY_DIR = HERE / "history"


def _history() -> list[Path]:
    return sorted(HISTORY_DIR.glob("*.json"))


def _load(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _col(val: float, width: int = 6) -> str:
    return f"{val:>{width}.2f}"


def _delta(now: float, then: float) -> str:
    d = now - then
    if d == 0:
        return "   —  "
    sign = "+" if d > 0 else ""
    return f"{sign}{d:>5.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=1,
                    help="Compare latest to the median of the previous N runs (default 1).")
    ap.add_argument("--threshold", type=float, default=1.0,
                    help="Regression threshold in LLM-judge points (default 1.0).")
    ap.add_argument("--pass-rate-threshold", type=float, default=0.10,
                    help="Regression threshold for deterministic pass rate (default 0.10 = 10pp).")
    args = ap.parse_args()

    hist = _history()
    if not hist:
        print("No bench history yet. Run scripts/bench/run.py first.")
        return 0
    latest = _load(hist[-1])

    prior = [_load(p) for p in hist[-(1 + args.window):-1]]
    if not prior:
        print(f"Only one bench run on file ({hist[-1].name}). Nothing to compare yet.")
        _print_snapshot(latest)
        return 0

    print(f"Latest:  {hist[-1].name}  (git {latest.get('git_sha','?')}, tag={latest.get('tag') or '-'})")
    print(f"Compare: median of last {len(prior)} prior run(s)")

    # --- Deterministic pass-rate diff ------------------------------------
    latest_rate = latest.get("summary", {}).get("check_pass_rate", 0.0)
    prior_rates = [r.get("summary", {}).get("check_pass_rate", 0.0) for r in prior]
    prior_rate = statistics.median(prior_rates) if prior_rates else 0.0
    print("\n=== Deterministic checks ===")
    print(f"  pass rate:   {latest_rate:.1%}   was {prior_rate:.1%}   Δ {latest_rate-prior_rate:+.1%}")

    rate_regression = (prior_rate - latest_rate) >= args.pass_rate_threshold

    # --- Per-check breakdown ---------------------------------------------
    latest_break = latest.get("summary", {}).get("check_breakdown", {})
    print("\n  per-check failures (latest):")
    for name, bucket in sorted(latest_break.items()):
        fail = bucket.get("failed", 0)
        total = bucket.get("passed", 0) + fail
        if fail:
            print(f"    {name:28s} {fail}/{total} failed")
    if not any(b.get("failed") for b in latest_break.values()):
        print("    (all clean)")

    # --- LLM-judge per-dimension diff ------------------------------------
    dim_regressions: list[tuple[str, float, float]] = []
    latest_llm = latest.get("summary", {}).get("llm_avg", {}) or {}
    prior_llm: dict[str, list[float]] = {}
    for r in prior:
        for dim, v in (r.get("summary", {}).get("llm_avg") or {}).items():
            prior_llm.setdefault(dim, []).append(v)
    prior_llm_med = {dim: statistics.median(vs) for dim, vs in prior_llm.items() if vs}

    if latest_llm or prior_llm_med:
        print("\n=== LLM judge (0–4) ===")
        all_dims = sorted(set(latest_llm) | set(prior_llm_med))
        print(f"  {'dimension':30s}  now    was    Δ")
        for dim in all_dims:
            now = latest_llm.get(dim, float("nan"))
            was = prior_llm_med.get(dim, float("nan"))
            print(f"  {dim:30s}  {_col(now)} {_col(was)} {_delta(now, was)}")
            if not (now != now or was != was):  # neither NaN
                if (was - now) >= args.threshold:
                    dim_regressions.append((dim, now, was))
    else:
        print("\n=== LLM judge ===\n  (no graded runs yet — run scripts/bench/grade.py)")

    # --- Verdict ----------------------------------------------------------
    print()
    if rate_regression:
        print(f"⚠️  Deterministic pass rate dropped {prior_rate-latest_rate:.1%} "
              f"(≥{args.pass_rate_threshold:.0%} threshold).")
    for dim, now, was in dim_regressions:
        print(f"⚠️  {dim} regressed {was-now:+.2f} ({was:.2f} → {now:.2f}).")

    if rate_regression or dim_regressions:
        print("REGRESSION")
        return 1
    print("OK")
    return 0


def _print_snapshot(record: dict) -> None:
    summary = record.get("summary", {})
    print(f"\nPass rate: {summary.get('check_pass_rate', 0):.1%} "
          f"({summary.get('checks_passed', 0)}/{summary.get('checks_total', 0)})")
    if summary.get("llm_avg"):
        print("LLM-judge averages:")
        for dim, v in sorted(summary["llm_avg"].items()):
            print(f"  {dim:28s} {v}")


if __name__ == "__main__":
    sys.exit(main())
