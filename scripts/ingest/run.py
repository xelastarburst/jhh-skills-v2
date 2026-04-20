#!/usr/bin/env python3
"""Virtual Jensen knowledge-refresh ingestion runner.

Reads ``sources.yaml``, runs fetchers for the chosen tier, dedupes against
``state.json``, and prints a human-readable report. In ``--dry-run`` mode
(the default for now) it does NOT invoke LLM subagents, does NOT modify
wiki pages, and does NOT create git branches. Apply mode is wired in a
follow-up commit.

Examples:
    scripts/ingest/run.py --tier daily
    scripts/ingest/run.py --tier all --no-fetch    # offline preview
    scripts/ingest/run.py --tier daily --apply     # not yet implemented
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Optional

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

sys.path.insert(0, str(HERE.parent))  # so `ingest.fetchers` imports work

from ingest import state as state_mod  # noqa: E402
from ingest.fetchers import FETCHERS  # noqa: E402

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# YouTube and several newsrooms serve different (or no) content to non-browser
# User-Agents, so we pretend to be a plain desktop browser. This is read-only,
# publicly-indexed content we're fetching.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
HTTP_TIMEOUT = 15


def http_get(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    # Follow redirects (default behavior, just being explicit for readers).
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def load_sources() -> dict:
    path = HERE / "sources.yaml"
    text = path.read_text()
    if yaml is None:
        raise SystemExit(
            "PyYAML not installed. Run: pip install pyyaml feedparser"
        )
    return yaml.safe_load(text)


def pick_tier(entries: list[dict], tier: str) -> list[dict]:
    if tier == "all":
        return list(entries)
    # Daily inherits from nothing else. Weekly ran on Monday typically also
    # covers daily. Monthly run (1st of month) implicitly covers weekly+daily
    # when invoked from launchd at the monthly slot. For each tier, we just
    # run sources whose tier ≤ the requested one.
    order = {"daily": 1, "weekly": 2, "monthly": 3}
    limit = order[tier]
    return [e for e in entries if order.get(e.get("tier", "weekly"), 2) <= limit]


def apply_filter(items: list[dict], pattern: Optional[str]) -> list[dict]:
    if not pattern:
        return items
    rx = re.compile(pattern, re.IGNORECASE)
    out = []
    for it in items:
        hay = " ".join([str(it.get("title", "")), str(it.get("summary", ""))])
        if rx.search(hay):
            out.append(it)
    return out


def _format_item(it: dict) -> str:
    title = (it.get("title") or "").strip()[:90]
    pub = it.get("published") or "?"
    url = it.get("url") or ""
    return f"    · {pub:25s}  {title}\n      {url}"


def process_group(
    label: str, sources: list[dict], tier: str, state: dict, *, fetch: bool
) -> dict:
    print(f"\n=== {label} ({tier}) ===")
    summary = {"label": label, "sources": []}
    selected = pick_tier(sources, tier)
    for src in selected:
        kind = src["type"]
        fetcher = FETCHERS.get(kind)
        src_rec = {"name": src["name"], "type": kind, "tier": src.get("tier"), "new": []}
        print(f"\n[{src.get('tier','?'):7s}] {src['name']}  ({kind})")
        if src.get("url"):
            print(f"          {src['url']}")
        if src.get("handle"):
            print(f"          handle={src['handle']}")
        if not fetcher:
            print("  skip: no fetcher for type", kind)
            continue
        if not fetch:
            print("  (--no-fetch: not contacting network)")
            summary["sources"].append(src_rec)
            continue
        try:
            kw = {"http_get": http_get}
            if kind == "youtube_channel":
                kw["state"] = state
            items = fetcher(src, **kw)
        except urllib.error.HTTPError as e:
            # videos.xml currently 404s for all channels (upstream deprecation).
            # Pipeline stays green; YouTube sources will light up again when
            # the yt-dlp fallback is wired in.
            print(f"  HTTP {e.code} {e.reason} (see youtube.py for status)")
            continue
        except Exception as e:  # noqa: BLE001
            print(f"  fetch error ({type(e).__name__}): {e}")
            continue
        items = apply_filter(items, src.get("filter"))
        new = state_mod.filter_new(state, src["name"], items, id_key="id")
        print(f"  fetched={len(items):3d}  new={len(new):3d}")
        for it in new[:5]:
            print(_format_item(it))
        if len(new) > 5:
            print(f"    … and {len(new) - 5} more")
        src_rec["new"] = [
            {"id": it["id"], "title": it.get("title"), "url": it.get("url")}
            for it in new
        ]
        summary["sources"].append(src_rec)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Virtual Jensen knowledge-refresh runner")
    ap.add_argument("--tier", choices=["daily", "weekly", "monthly", "all"],
                    default="daily", help="Which tier to run (default: daily).")
    ap.add_argument("--apply", action="store_true",
                    help="Apply changes (invoke subagents, open git branch). Not yet implemented.")
    ap.add_argument("--no-fetch", action="store_true",
                    help="Don't hit the network — just print what would be fetched.")
    ap.add_argument("--reset-state", action="store_true",
                    help="Clear state.json before running (treats everything as new).")
    ap.add_argument("--json", action="store_true",
                    help="Emit a machine-readable summary on stdout after the run.")
    args = ap.parse_args()

    if args.apply:
        print("[apply-mode is not implemented yet in this dry-run scaffold]", file=sys.stderr)
        return 2

    cfg = load_sources()
    state = {} if args.reset_state else state_mod.load()

    t0 = time.time()
    report = {
        "tier": args.tier,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dry_run": True,
        "groups": [],
    }
    report["groups"].append(process_group(
        "INTERVIEWS", cfg.get("interview_sources", []), args.tier, state, fetch=not args.no_fetch,
    ))
    report["groups"].append(process_group(
        "WIKI",       cfg.get("wiki_sources", []),      args.tier, state, fetch=not args.no_fetch,
    ))

    # Dry-run does NOT persist new IDs — so repeat runs keep surfacing the same items.
    print(f"\n(done in {time.time() - t0:.1f}s — dry-run, no state written, no branch created)")

    if args.json:
        print("---JSON---")
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
