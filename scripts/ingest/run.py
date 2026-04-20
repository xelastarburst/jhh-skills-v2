#!/usr/bin/env python3
"""Virtual Jensen knowledge-refresh ingestion runner.

Reads ``sources.yaml``, runs fetchers for the chosen tier, dedupes
against ``state.json``, prints a human-readable report, and optionally
drives the wiki-update / interview-extract subagents.

Three operating modes:

  default (fetcher-only, dry-run)
      Reports what would be fetched. Subagents are not invoked.
      state.json is not written.

  --invoke-agents (pipeline, dry-run)
      For each source with new items:
        - wiki source      → scripts/ingest/agents/update_wiki.py
                             emits proposed unified diffs on stdout
        - interview source → scripts/ingest/agents/extract_interview.py
                             emits the proposed interviews-log.md entry
                             on stdout
      Neither subagent modifies disk in this mode.
      state.json is not written — safe to rerun.

  --invoke-agents --apply (the real thing)
      Subagents run in --apply mode: wiki updater creates a local
      ``ingest/<date>-<source>`` branch, interview extractor appends
      to ``references/interviews-log.md``. state.json IS updated on
      success so the next run doesn't re-surface processed items.

Examples:
    scripts/ingest/run.py --tier daily
    scripts/ingest/run.py --tier all --no-fetch
    scripts/ingest/run.py --tier daily --invoke-agents
    scripts/ingest/run.py --tier daily --invoke-agents --apply
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
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


# =========================================================================
# Subagent invocation
# =========================================================================

AGENT_DIR = HERE / "agents"
UPDATE_WIKI = AGENT_DIR / "update_wiki.py"
EXTRACT_INTERVIEW = AGENT_DIR / "extract_interview.py"
UPGRADE_TRANSCRIPT = HERE / "upgrade_transcript.py"

# Match the same "skip if stub / fallback to summary" cutoff the fetchers use.
_MAX_ITEMS_PER_INVOCATION = 15


def _python() -> str:
    """Resolve the venv Python so the subagent sees claude_agent_sdk."""
    candidates = [
        REPO_ROOT / "virtual-jensen-web" / ".venv" / "bin" / "python",
        Path(sys.executable),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable


def invoke_wiki_agent(src: dict, items: list[dict], *, tier: str, apply: bool) -> int:
    """Run update_wiki.py on a batch of new items for one wiki source."""
    if not items:
        return 0
    if not UPDATE_WIKI.exists():
        print(f"  [wiki agent missing: {UPDATE_WIKI}]", file=sys.stderr)
        return 1
    # Subagent expects a JSON array of {id, title, url, published, summary}.
    payload = items[:_MAX_ITEMS_PER_INVOCATION]
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", prefix="vj-ingest-", delete=False
    ) as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        items_path = fh.name
    cmd = [
        _python(), str(UPDATE_WIKI),
        "--source", src["name"],
        "--items", items_path,
        "--tier", tier,
    ]
    if apply:
        cmd.append("--apply")
    print(f"\n  [invoking wiki agent: {src['name']} ({len(payload)} items, "
          f"{'apply' if apply else 'dry-run'})]")
    try:
        rc = subprocess.call(cmd)
    finally:
        try:
            os.unlink(items_path)
        except OSError:
            pass
    return rc


def invoke_interview_pipeline(
    src: dict, items: list[dict], *, tier: str, apply: bool, transcript_service: str
) -> int:
    """Run extract_interview.py for each new interview-source item.

    For YouTube sources: upgrade the transcript via upgrade_transcript.py,
    then run the extractor against the resulting file.
    For RSS sources: write the item summary to a tempfile and run the
    extractor against that (quality is summary-only, but it still
    surfaces new framing on text-only analyses like Stratechery).
    """
    if not items:
        return 0
    if not EXTRACT_INTERVIEW.exists():
        print(f"  [interview extractor missing: {EXTRACT_INTERVIEW}]", file=sys.stderr)
        return 1

    is_youtube = src.get("type") == "youtube_channel"
    rcs: list[int] = []
    for item in items[:_MAX_ITEMS_PER_INVOCATION]:
        transcript_path, cleanup = _prepare_interview_transcript(
            src, item, transcript_service=transcript_service, is_youtube=is_youtube,
        )
        if transcript_path is None:
            print(f"  [skipping {item.get('id')}: no transcript produced]",
                  file=sys.stderr)
            continue
        cmd = [
            _python(), str(EXTRACT_INTERVIEW),
            "--transcript", str(transcript_path),
            "--source-name", f"{src['name']} — {item.get('title','')[:80]}".strip(" —"),
            "--source-url", item.get("url") or "",
            "--published", _iso_date_from_item(item),
        ]
        if apply:
            cmd.append("--apply")
        print(f"\n  [invoking interview extractor: {item.get('title','')[:70]!r} "
              f"({'apply' if apply else 'dry-run'})]")
        try:
            rc = subprocess.call(cmd)
        finally:
            if cleanup:
                cleanup()
        rcs.append(rc)
    return 0 if all(r == 0 for r in rcs) else 1


def _iso_date_from_item(item: dict) -> str:
    """Coerce an item's `published` field to YYYY-MM-DD for the extractor."""
    pub = item.get("published") or ""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", pub)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # RFC-822 style "Thu, 16 Apr 2026 13:00:11 +0000"
    m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", pub)
    if m:
        import calendar
        mon = {m: i for i, m in enumerate(calendar.month_abbr) if m}.get(m.group(2))
        if mon:
            return f"{m.group(3)}-{mon:02d}-{int(m.group(1)):02d}"
    return time.strftime("%Y-%m-%d")


def _prepare_interview_transcript(
    src: dict, item: dict, *, transcript_service: str, is_youtube: bool,
):
    """Returns (transcript_path, cleanup_fn_or_None)."""
    if is_youtube:
        vid = item.get("id")
        if not vid:
            return None, None
        if not UPGRADE_TRANSCRIPT.exists():
            print(f"  [upgrade_transcript.py missing]", file=sys.stderr)
            return None, None
        cmd = [_python(), str(UPGRADE_TRANSCRIPT), vid, "--service", transcript_service]
        print(f"    [transcribing {vid} via {transcript_service}]")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            tail = (proc.stderr or "").strip().splitlines()[-3:]
            print(f"    [transcript failed: {' | '.join(tail)}]", file=sys.stderr)
            return None, None
        path = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
        if not path or not Path(path).exists():
            return None, None
        return Path(path), None  # transcripts/ is persistent; leave it on disk

    # RSS / HTML interview source — write summary to a tempfile.
    blob = (
        f"# {item.get('title','')}\n"
        f"Source URL: {item.get('url','')}\n"
        f"Published: {item.get('published','')}\n\n"
        f"{item.get('summary','')}\n"
    )
    if len(blob) < 200:
        # extract_interview.py refuses <200 chars — skip silently.
        return None, None
    tmp = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", prefix="vj-rss-", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(blob)
        tmp.close()
        return Path(tmp.name), (lambda p=tmp.name: _safe_unlink(p))
    except Exception:
        _safe_unlink(tmp.name)
        return None, None


def _safe_unlink(p: str) -> None:
    try:
        os.unlink(p)
    except OSError:
        pass


def invoke_agents(report: dict, *, tier: str, apply: bool, transcript_service: str) -> None:
    """Walk the fetched report and route each group to the right subagent."""
    print("\n" + "=" * 70)
    print(f"=== INVOKING SUBAGENTS ({'apply' if apply else 'dry-run'}) ===")
    print("=" * 70)

    cfg = load_sources()
    by_name = {s["name"]: s for s in cfg.get("interview_sources", [])}
    by_name.update({s["name"]: s for s in cfg.get("wiki_sources", [])})

    for group in report["groups"]:
        is_wiki = group["label"] == "WIKI"
        for src_rec in group["sources"]:
            items = src_rec.get("new") or []
            if not items:
                continue
            src_cfg = by_name.get(src_rec["name"])
            if src_cfg is None:
                continue
            if is_wiki:
                invoke_wiki_agent(src_cfg, items, tier=tier, apply=apply)
            else:
                invoke_interview_pipeline(
                    src_cfg, items,
                    tier=tier, apply=apply,
                    transcript_service=transcript_service,
                )


def main() -> int:
    ap = argparse.ArgumentParser(description="Virtual Jensen knowledge-refresh runner")
    ap.add_argument("--tier", choices=["daily", "weekly", "monthly", "all"],
                    default="daily", help="Which tier to run (default: daily).")
    ap.add_argument("--invoke-agents", action="store_true",
                    help="After fetch, route each source's new items through the "
                         "wiki-update / interview-extract subagents (dry-run).")
    ap.add_argument("--apply", action="store_true",
                    help="With --invoke-agents, run subagents in --apply mode: "
                         "wiki updater creates a local branch, interview "
                         "extractor appends to references/interviews-log.md, and "
                         "state.json is updated so items aren't re-processed. "
                         "Has no effect without --invoke-agents.")
    ap.add_argument("--transcript-service",
                    default="whisper",
                    choices=["whisper", "parakeet", "parakeet-mlx", "youtube", "assemblyai"],
                    help="Backend used by upgrade_transcript.py when the "
                         "interview pipeline needs a transcript (default: whisper).")
    ap.add_argument("--no-fetch", action="store_true",
                    help="Don't hit the network — just print what would be fetched.")
    ap.add_argument("--reset-state", action="store_true",
                    help="Clear state.json before running (treats everything as new).")
    ap.add_argument("--json", action="store_true",
                    help="Emit a machine-readable summary on stdout after the run.")
    args = ap.parse_args()

    if args.apply and not args.invoke_agents:
        print("[--apply without --invoke-agents is a no-op; "
              "did you mean --invoke-agents --apply?]", file=sys.stderr)

    cfg = load_sources()
    state = {} if args.reset_state else state_mod.load()

    t0 = time.time()
    dry_run = not args.apply
    report = {
        "tier": args.tier,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dry_run": dry_run,
        "invoke_agents": args.invoke_agents,
        "groups": [],
    }
    report["groups"].append(process_group(
        "INTERVIEWS", cfg.get("interview_sources", []), args.tier, state, fetch=not args.no_fetch,
    ))
    report["groups"].append(process_group(
        "WIKI",       cfg.get("wiki_sources", []),      args.tier, state, fetch=not args.no_fetch,
    ))

    if args.invoke_agents and not args.no_fetch:
        invoke_agents(
            report,
            tier=args.tier, apply=args.apply,
            transcript_service=args.transcript_service,
        )
        # Persist state only on --apply so dry-run stays idempotent.
        if args.apply:
            for group in report["groups"]:
                for src_rec in group["sources"]:
                    ids = [it["id"] for it in (src_rec.get("new") or [])]
                    if ids:
                        state_mod.record(state, src_rec["name"], ids)
            state_mod.save(state)
            print(f"\n[state.json updated with {sum(len(g['sources']) for g in report['groups'])} source(s)]")
        else:
            print("\n[dry-run — state.json NOT updated; re-run with --apply to persist]")
    else:
        print(f"\n(done in {time.time() - t0:.1f}s — fetch-only, no state written, "
              "no subagents invoked; add --invoke-agents to drive the pipeline)")

    if args.json:
        print("---JSON---")
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
