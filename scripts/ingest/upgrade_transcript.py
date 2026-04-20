#!/usr/bin/env python3
"""Fetch a high-quality transcript for a single YouTube video.

Three backends, in order of fidelity (and cost):

  - ``youtube``    (default, free) — yt-dlp auto-captions. ~95%-ish
                   accuracy, brittle on specialist vocab, no speaker
                   labels. Good enough for daily monitoring to decide
                   *whether* to upgrade.
  - ``assemblyai`` (~$0.12/hr + ~$0.05/hr for speaker labels) — verbatim
                   transcription with speaker diarization. Use for any
                   long-form Jensen appearance we plan to extract from.
                   Needs ``ASSEMBLYAI_API_KEY`` env var.
  - ``rev``        (~$1.50/min) — human-grade verbatim. Not wired;
                   AssemblyAI has been close enough at 1/10th the cost.

Usage:
    upgrade_transcript.py VIDEO_ID [--service youtube|assemblyai|rev] [--lang en]

Writes to ``scripts/ingest/transcripts/<video_id>.<ext>`` — .vtt for
youtube, .txt (with speaker labels) for assemblyai.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRANSCRIPTS_DIR = HERE / "transcripts"
_YT_DLP_TIMEOUT = 60
_ASSEMBLYAI_TIMEOUT = 1200  # 20 min ceiling for a single transcript
_ASSEMBLYAI_POLL = 8        # seconds between status polls
_ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2"

SERVICES = ("youtube", "assemblyai", "rev")


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
        "Rev transcription not yet wired — AssemblyAI covers this need at "
        "1/10th the cost. If you specifically need Rev's human-verbatim "
        "tier, add the integration in scripts/ingest/upgrade_transcript.py."
    )


# ---------------------------------------------------------------------------
# AssemblyAI
# ---------------------------------------------------------------------------


def _extract_audio(video_id: str) -> Path:
    """Pull just the audio track from a YouTube video via yt-dlp."""
    binary = shutil.which("yt-dlp")
    if not binary:
        raise SystemExit("yt-dlp not installed; run: pip install yt-dlp")

    # Use a temp dir so we don't leave mp3s lying around.
    tmp_dir = Path(tempfile.mkdtemp(prefix="vj-audio-"))
    out_template = str(tmp_dir / "%(id)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        binary,
        "-x",                     # extract audio
        "--audio-format", "mp3",
        "--audio-quality", "5",   # medium quality — AssemblyAI handles lossy input fine
        "-o", out_template,
        url,
    ]
    print(f"[extracting audio for {video_id}]", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=_YT_DLP_TIMEOUT * 6)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-5:]
        raise SystemExit("yt-dlp audio extraction failed:\n  " + "\n  ".join(tail))
    candidates = sorted(tmp_dir.glob(f"{video_id}*.mp3"))
    if not candidates:
        raise SystemExit(f"no audio file produced for {video_id}")
    return candidates[0]


def _assemblyai_upload(audio_path: Path, api_key: str) -> str:
    """Upload a local audio file; return the signed upload_url AssemblyAI gives us."""
    data = audio_path.read_bytes()
    req = urllib.request.Request(
        f"{_ASSEMBLYAI_BASE}/upload",
        data=data,
        headers={"authorization": api_key, "content-type": "application/octet-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    url = body.get("upload_url")
    if not url:
        raise SystemExit(f"AssemblyAI upload returned no upload_url: {body}")
    return url


def _assemblyai_submit(upload_url: str, api_key: str, lang: str) -> str:
    """Queue a transcription job. Returns the job id."""
    payload = {
        "audio_url": upload_url,
        "language_code": lang,
        "speaker_labels": True,      # diarization — worth the +$0.05/hr
        "punctuate": True,
        "format_text": True,
    }
    req = urllib.request.Request(
        f"{_ASSEMBLYAI_BASE}/transcript",
        data=json.dumps(payload).encode("utf-8"),
        headers={"authorization": api_key, "content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    tid = body.get("id")
    if not tid:
        raise SystemExit(f"AssemblyAI submit returned no id: {body}")
    return tid


def _assemblyai_poll(transcript_id: str, api_key: str) -> dict:
    """Block until the job is 'completed' or 'error'. Returns the payload."""
    req = urllib.request.Request(
        f"{_ASSEMBLYAI_BASE}/transcript/{transcript_id}",
        headers={"authorization": api_key},
    )
    deadline = time.monotonic() + _ASSEMBLYAI_TIMEOUT
    last_status = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            # Transient network error — keep polling.
            print(f"[poll error: {e}]", file=sys.stderr)
            time.sleep(_ASSEMBLYAI_POLL)
            continue
        status = body.get("status")
        if status != last_status:
            print(f"[assemblyai {transcript_id}: {status}]", file=sys.stderr)
            last_status = status
        if status == "completed":
            return body
        if status == "error":
            raise SystemExit(f"AssemblyAI job failed: {body.get('error')}")
        time.sleep(_ASSEMBLYAI_POLL)
    raise SystemExit(f"AssemblyAI job {transcript_id} exceeded {_ASSEMBLYAI_TIMEOUT}s")


def _format_diarized(payload: dict) -> str:
    """Convert AssemblyAI utterances into a speaker-labelled transcript."""
    utts = payload.get("utterances") or []
    if not utts:
        # No diarization — fall back to raw text.
        return payload.get("text", "").strip() + "\n"
    lines = []
    for u in utts:
        speaker = u.get("speaker") or "?"
        start_ms = int(u.get("start", 0))
        ts = time.strftime("%H:%M:%S", time.gmtime(start_ms / 1000))
        text = (u.get("text") or "").strip()
        if text:
            lines.append(f"[{ts}] Speaker {speaker}: {text}")
    return "\n".join(lines) + "\n"


def _fetch_assemblyai(video_id: str, lang: str) -> Path:
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "ASSEMBLYAI_API_KEY not set. Get a key from https://www.assemblyai.com "
            "and either export it in your shell or add it to "
            "virtual-jensen-web/.env (the web app reads that file and subsequent "
            "child processes inherit it)."
        )

    audio = _extract_audio(video_id)
    try:
        print(f"[uploading {audio.stat().st_size // 1024} KB to AssemblyAI]", file=sys.stderr)
        upload_url = _assemblyai_upload(audio, api_key)
        transcript_id = _assemblyai_submit(upload_url, api_key, lang)
        payload = _assemblyai_poll(transcript_id, api_key)
    finally:
        # Clean up the audio file + its tmpdir regardless of outcome.
        try:
            audio.unlink()
            audio.parent.rmdir()
        except OSError:
            pass

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.assemblyai.txt"
    out.write_text(_format_diarized(payload), encoding="utf-8")
    return out


_DISPATCH = {
    "youtube": _fetch_youtube,
    "assemblyai": _fetch_assemblyai,
    "rev": _fetch_rev,
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
