#!/usr/bin/env python3
"""Fetch a high-quality transcript for a single YouTube video.

Default path is ``yt-dlp``'s auto-caption downloader (free, usually good
enough for monitoring). Paid, human-grade services (Rev, AssemblyAI) are
stubbed out — wire them up when we have a video whose signal justifies
the cost.

Usage:
    upgrade_transcript.py VIDEO_ID [--service youtube|rev|assemblyai] [--lang en]

Writes to: scripts/ingest/transcripts/<video_id>.<ext>
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRANSCRIPTS_DIR = HERE / "transcripts"
_YT_DLP_TIMEOUT = 60

SERVICES = ("youtube", "rev", "assemblyai")


def _fetch_youtube(video_id: str, lang: str) -> Path:
    binary = shutil.which("yt-dlp")
    if not binary:
        raise SystemExit("yt-dlp not installed; run: pip install yt-dlp")

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out_template = str(TRANSCRIPTS_DIR / "%(id)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        binary,
        "--write-auto-sub",
        "--sub-lang", lang,
        "--skip-download",
        "--convert-subs", "vtt",
        "-o", out_template,
        url,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_YT_DLP_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise SystemExit(f"yt-dlp timed out after {_YT_DLP_TIMEOUT}s")

    if proc.returncode != 0:
        stderr_tail = (proc.stderr or "").strip().splitlines()[-5:]
        raise SystemExit("yt-dlp failed:\n  " + "\n  ".join(stderr_tail))

    # yt-dlp names the file <video_id>.<lang>.vtt when --convert-subs vtt is set.
    candidates = sorted(TRANSCRIPTS_DIR.glob(f"{video_id}*.vtt"))
    if not candidates:
        raise SystemExit(
            f"yt-dlp reported success but no transcript file was found "
            f"in {TRANSCRIPTS_DIR}. Stderr:\n{proc.stderr}"
        )
    # Prefer the exact <id>.<lang>.vtt when multiple exist.
    for c in candidates:
        if c.name == f"{video_id}.{lang}.vtt":
            return c
    return candidates[0]


def _fetch_rev(video_id: str, lang: str) -> Path:
    raise NotImplementedError(
        "Rev transcription not yet wired — see scripts/ingest/README.md"
    )


def _fetch_assemblyai(video_id: str, lang: str) -> Path:
    raise NotImplementedError(
        "AssemblyAI transcription not yet wired — see scripts/ingest/README.md"
    )


_DISPATCH = {
    "youtube": _fetch_youtube,
    "rev": _fetch_rev,
    "assemblyai": _fetch_assemblyai,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fetch a transcript for a YouTube video."
    )
    ap.add_argument("video_id", help="11-character YouTube video ID")
    ap.add_argument(
        "--service",
        choices=SERVICES,
        default="youtube",
        help="Transcription backend (default: youtube auto-captions, free).",
    )
    ap.add_argument(
        "--lang",
        default="en",
        help="Subtitle language code (default: en).",
    )
    args = ap.parse_args()

    fetcher = _DISPATCH[args.service]
    path = fetcher(args.video_id, args.lang)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
