#!/usr/bin/env python3
"""Fetch a high-quality transcript for a single YouTube video.

Six backends, in order of recommendation for extracting Jensen material:

  - ``whisper``       (default for upgrades, FREE, local) — faster-whisper
                      with the ``distil-large-v3`` model. ~10-15 min for a
                      2-hour podcast on a modern laptop CPU; faster on
                      Apple Silicon MPS or CUDA. Good accuracy, per-segment
                      timestamps. No diarization (single stream of text).
                      Install: ``pip install faster-whisper``.
  - ``parakeet``      (FREE, local, best English accuracy) — NVIDIA's own
                      Parakeet-TDT 0.6B v2 via NeMo. Tops the Open ASR
                      Leaderboard on English. Heavy install (~2 GB of
                      PyTorch + NeMo). Install:
                      ``pip install 'nemo_toolkit[asr]'``.
  - ``parakeet-mlx``  (FREE, local, Apple Silicon only) — Parakeet ported
                      to Apple's MLX framework. No PyTorch dependency, much
                      lighter install than NeMo, runs natively on M-series
                      GPUs. Install: ``pip install parakeet-mlx``.
  - ``youtube``       (FREE, lowest quality) — yt-dlp auto-captions. 30s
                      fetch. Good enough to decide *whether* to upgrade,
                      not good enough to extract quotes verbatim.
  - ``assemblyai``    (PAID, ~$0.17/hr with diarization) — verbatim +
                      speaker labels. Use when you need to attribute quotes
                      in a 3+-speaker podcast. Needs ``ASSEMBLYAI_API_KEY``.
  - ``rev``           (PAID, ~$90/hr) — human-grade verbatim. Not wired;
                      AssemblyAI covers the need at 1/20th the cost.

Optional ``--diarize`` post-processes any local STT output (whisper /
parakeet / parakeet-mlx) with ``pyannote.audio`` to produce a
speaker-labelled transcript. Requires a HuggingFace token and accepting
the model terms at https://huggingface.co/pyannote/speaker-diarization-3.1.

Usage:
    upgrade_transcript.py VIDEO_ID [--service SVC] [--lang en] [--model NAME] [--diarize]

Writes to ``scripts/ingest/transcripts/<video_id>.<service>.<ext>``.
With ``--diarize``, also writes ``<video_id>.<service>.diarized.txt``.

The default service is ``whisper`` because it's free, local, and
good enough to feed the interview extractor directly.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
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

_WHISPER_DEFAULT_MODEL = "distil-large-v3"  # 6x faster, comparable accuracy
_PARAKEET_DEFAULT_MODEL = "nvidia/parakeet-tdt-0.6b-v2"  # Open ASR leaderboard top
_PARAKEET_MLX_DEFAULT_MODEL = "mlx-community/parakeet-tdt-0.6b-v2"
_PARAKEET_TIMESTAMP_FMT = "%H:%M:%S"

_PYANNOTE_MODEL = "pyannote/speaker-diarization-3.1"
_DIARIZABLE_SERVICES = ("whisper", "parakeet", "parakeet-mlx")

SERVICES = ("whisper", "parakeet", "parakeet-mlx", "youtube", "assemblyai", "rev")


def _fetch_youtube(video_id: str, lang: str, **_kw) -> Path:
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


def _fetch_rev(video_id: str, lang: str, **_kw) -> Path:
    raise NotImplementedError(
        "Rev transcription not yet wired — AssemblyAI (or local Whisper) "
        "covers this need at a fraction of the cost. If you specifically "
        "need Rev's human-verbatim tier, add the integration in "
        "scripts/ingest/upgrade_transcript.py."
    )


# ---------------------------------------------------------------------------
# faster-whisper (local, free)
# ---------------------------------------------------------------------------


def _fetch_whisper(
    video_id: str,
    lang: str,
    *,
    model_name: str | None = None,
    audio_path: Path | None = None,
) -> tuple[Path, list[tuple[float, str]]]:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        raise SystemExit(
            "faster-whisper not installed. Install with:\n"
            "  pip install faster-whisper\n"
            "First run downloads the model (~1.5 GB for distil-large-v3)."
        )

    name = model_name or _WHISPER_DEFAULT_MODEL
    owns_audio = audio_path is None
    audio = audio_path if audio_path is not None else _extract_audio(video_id)
    segments_out: list[tuple[float, str]] = []
    try:
        # device="auto" picks CUDA > MPS > CPU. compute_type="int8" keeps CPU
        # inference fast with ~no measurable accuracy loss for English.
        print(f"[loading whisper model: {name}]", file=sys.stderr)
        asr = WhisperModel(name, device="auto", compute_type="int8")
        print(f"[transcribing {audio.name}]", file=sys.stderr)
        segments, info = asr.transcribe(
            str(audio),
            language=lang if lang != "auto" else None,
            vad_filter=True,             # skip long silences
            condition_on_previous_text=False,  # prevents looped hallucinations
            beam_size=5,
        )
        lines: list[str] = [
            f"# Transcript — faster-whisper ({name})",
            f"# video_id: {video_id}   detected language: "
            f"{getattr(info, 'language', '?')} "
            f"({getattr(info, 'language_probability', 0):.2f})",
            "",
        ]
        for seg in segments:
            text = (seg.text or "").strip()
            if not text:
                continue
            ts = time.strftime(_PARAKEET_TIMESTAMP_FMT, time.gmtime(seg.start))
            lines.append(f"[{ts}] {text}")
            segments_out.append((float(seg.start), text))
        body = "\n".join(lines) + "\n"
    finally:
        if owns_audio:
            _cleanup_audio(audio)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.whisper.txt"
    out.write_text(body, encoding="utf-8")
    return out, segments_out


# ---------------------------------------------------------------------------
# NVIDIA Parakeet via NeMo (local, free)
# ---------------------------------------------------------------------------


def _fetch_parakeet(
    video_id: str,
    lang: str,
    *,
    model_name: str | None = None,
    audio_path: Path | None = None,
) -> tuple[Path, list[tuple[float, str]]]:
    # Intentionally fail if requested in a non-English context — Parakeet
    # models on the Open ASR Leaderboard are English-only. Use whisper for
    # multilingual.
    if lang not in ("en", "auto"):
        raise SystemExit(
            f"Parakeet models are English-only (requested lang={lang!r}). "
            f"Use --service whisper for multilingual."
        )
    try:
        import nemo.collections.asr as nemo_asr  # type: ignore
    except ImportError:
        raise SystemExit(
            "nemo_toolkit not installed. Install with:\n"
            "  pip install 'nemo_toolkit[asr]'\n"
            "This is a ~2 GB install (PyTorch, torchaudio, NeMo, "
            "hydra-core). Use --service whisper for a lighter option, or "
            "--service parakeet-mlx on Apple Silicon."
        )

    name = model_name or _PARAKEET_DEFAULT_MODEL
    owns_audio = audio_path is None
    audio = audio_path if audio_path is not None else _extract_audio(video_id)
    try:
        print(f"[loading parakeet model: {name}]", file=sys.stderr)
        asr = nemo_asr.models.ASRModel.from_pretrained(name)
        print(f"[transcribing {audio.name}]", file=sys.stderr)
        hyps = asr.transcribe([str(audio)], timestamps=True)
    except TypeError:
        # Older NeMo without the `timestamps=` kwarg — transcribe without.
        hyps = asr.transcribe([str(audio)])
    finally:
        if owns_audio:
            _cleanup_audio(audio)

    text, timed_lines, timed_segments = _parakeet_render(hyps)
    header = [
        f"# Transcript — Parakeet ({name})",
        f"# video_id: {video_id}   language: en",
    ]
    if timed_lines:
        header.append("")
        body = "\n".join(header + timed_lines) + "\n"
    else:
        header.append(
            "# per-segment timestamps unavailable from this model/NeMo version"
        )
        header.append("")
        body = "\n".join(header) + text.strip() + "\n"

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.parakeet.txt"
    out.write_text(body, encoding="utf-8")
    return out, timed_segments


def _parakeet_render(hyps) -> tuple[str, list[str], list[tuple[float, str]]]:
    """NeMo's ASR.transcribe() return shape varies by model + version.

    Normalize to (flat_text, list_of_timestamped_lines, list_of_(start, text)).
    If segment timestamps aren't available, both timed lists are empty.
    """
    if not hyps:
        return "", [], []
    # NeMo often returns list[Hypothesis] or tuple(hyps, all_hyps).
    if isinstance(hyps, tuple):
        hyps = hyps[0] if hyps else []
    if not hyps:
        return "", [], []
    h = hyps[0]
    text = h.text if hasattr(h, "text") else (h if isinstance(h, str) else str(h))

    timed_lines: list[str] = []
    timed_segments: list[tuple[float, str]] = []
    # Newer NeMo: h.timestamp = {'segment': [{'start': s, 'end': e, 'segment': '...'}], 'word': [...]}
    ts = getattr(h, "timestamp", None)
    if isinstance(ts, dict):
        segs = ts.get("segment") or []
        for s in segs:
            start = float(s.get("start", 0))
            piece = (s.get("segment") or s.get("text") or "").strip()
            if piece:
                clock = time.strftime(_PARAKEET_TIMESTAMP_FMT, time.gmtime(start))
                timed_lines.append(f"[{clock}] {piece}")
                timed_segments.append((start, piece))
    return text, timed_lines, timed_segments


# ---------------------------------------------------------------------------
# Parakeet-MLX (local, free, Apple Silicon only)
# ---------------------------------------------------------------------------


def _fetch_parakeet_mlx(
    video_id: str,
    lang: str,
    *,
    model_name: str | None = None,
    audio_path: Path | None = None,
) -> tuple[Path, list[tuple[float, str]]]:
    # Parakeet is English-only — mirrors the NeMo backend.
    if lang not in ("en", "auto"):
        raise SystemExit(
            f"Parakeet models are English-only (requested lang={lang!r}). "
            f"Use --service whisper for multilingual."
        )

    # Hard platform guard — MLX only runs on Apple Silicon.
    if sys.platform != "darwin" or platform.machine() not in ("arm64", "aarch64"):
        raise SystemExit(
            "parakeet-mlx only runs on Apple Silicon (macOS arm64).\n"
            f"Detected: {sys.platform}/{platform.machine()}.\n"
            "Use --service parakeet (NeMo, cross-platform) or "
            "--service whisper (lightest option) instead."
        )

    try:
        from parakeet_mlx import from_pretrained  # type: ignore
    except ImportError:
        raise SystemExit(
            "parakeet-mlx not installed. Install with:\n"
            "  pip install parakeet-mlx\n"
            "Lightweight Apple-Silicon-native Parakeet port — no PyTorch\n"
            "dependency. See https://github.com/senstella/parakeet-mlx."
        )

    name = model_name or _PARAKEET_MLX_DEFAULT_MODEL
    owns_audio = audio_path is None
    audio = audio_path if audio_path is not None else _extract_audio(video_id)
    timed_segments: list[tuple[float, str]] = []
    try:
        print(f"[loading parakeet-mlx model: {name}]", file=sys.stderr)
        model = from_pretrained(name)
        print(f"[transcribing {audio.name}]", file=sys.stderr)
        result = model.transcribe(str(audio))
    finally:
        if owns_audio:
            _cleanup_audio(audio)

    # parakeet-mlx's result exposes a `.sentences` (or similar) iterable of
    # objects with .start / .end / .text. Older/newer releases sometimes
    # expose .text only — fall back gracefully.
    sentences = (
        getattr(result, "sentences", None)
        or getattr(result, "segments", None)
        or []
    )
    for s in sentences:
        start = float(getattr(s, "start", 0) or 0)
        piece = (getattr(s, "text", "") or "").strip()
        if piece:
            timed_segments.append((start, piece))

    header = [
        f"# Transcript — parakeet-mlx ({name})",
        f"# video_id: {video_id}   language: en",
    ]
    if timed_segments:
        header.append("")
        lines = header + [
            f"[{time.strftime(_PARAKEET_TIMESTAMP_FMT, time.gmtime(start))}] {piece}"
            for start, piece in timed_segments
        ]
        body = "\n".join(lines) + "\n"
    else:
        flat = (getattr(result, "text", "") or str(result)).strip()
        header.append("# per-segment timestamps unavailable from this model version")
        header.append("")
        body = "\n".join(header) + flat + "\n"

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.parakeet-mlx.txt"
    out.write_text(body, encoding="utf-8")
    return out, timed_segments


# ---------------------------------------------------------------------------
# Small shared helper so every backend cleans up its temp audio the same way.
# ---------------------------------------------------------------------------


def _cleanup_audio(audio: Path) -> None:
    try:
        audio.unlink()
        audio.parent.rmdir()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# pyannote diarization (optional post-processing)
# ---------------------------------------------------------------------------


def _diarize(audio: Path) -> list[tuple[float, float, str]]:
    """Run pyannote on ``audio`` and return a list of (start, end, speaker)."""
    token = (
        os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    )
    if not token:
        raise SystemExit(
            "pyannote diarization requires HF_TOKEN. "
            "Get one from https://huggingface.co/settings/tokens and accept "
            "the model terms at "
            "https://huggingface.co/pyannote/speaker-diarization-3.1."
        )
    try:
        from pyannote.audio import Pipeline  # type: ignore
    except ImportError:
        raise SystemExit(
            "pyannote.audio not installed. Install with:\n"
            "  pip install pyannote.audio torch torchaudio\n"
            "Then accept the model terms at "
            "https://huggingface.co/pyannote/speaker-diarization-3.1."
        )

    print(f"[loading pyannote pipeline: {_PYANNOTE_MODEL}]", file=sys.stderr)
    pipeline = Pipeline.from_pretrained(_PYANNOTE_MODEL, use_auth_token=token)
    print(f"[diarizing {audio.name}]", file=sys.stderr)
    diarization = pipeline(str(audio))

    # Map pyannote's internal speaker ids (SPEAKER_00, SPEAKER_01, ...) to
    # stable A/B/C labels in first-appearance order.
    labels: dict[str, str] = {}
    intervals: list[tuple[float, float, str]] = []
    for turn, _track, speaker in diarization.itertracks(yield_label=True):
        if speaker not in labels:
            labels[speaker] = chr(ord("A") + len(labels))
        intervals.append((float(turn.start), float(turn.end), labels[speaker]))
    intervals.sort(key=lambda x: x[0])
    return intervals


def _speaker_at(t: float, intervals: list[tuple[float, float, str]]) -> str:
    """Return the speaker label whose [a, b] contains t, else nearest neighbor."""
    if not intervals:
        return "?"
    best_label = intervals[0][2]
    best_dist = float("inf")
    for a, b, label in intervals:
        if a <= t <= b:
            return label
        # Distance to the nearest edge of this interval.
        dist = a - t if t < a else t - b
        if dist < best_dist:
            best_dist = dist
            best_label = label
    return best_label


def _write_diarized(
    video_id: str,
    service: str,
    stt_segments: list[tuple[float, str]],
    intervals: list[tuple[float, float, str]],
) -> Path:
    lines = [
        f"# Diarized transcript — {service} + pyannote",
        f"# video_id: {video_id}",
        "",
    ]
    if not stt_segments:
        lines.append(
            "# STT backend did not emit per-segment timestamps; diarization skipped."
        )
    for start, text in stt_segments:
        spk = _speaker_at(start, intervals)
        ts = time.strftime(_PARAKEET_TIMESTAMP_FMT, time.gmtime(start))
        lines.append(f"[{ts}] Speaker {spk}: {text}")

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.{service}.diarized.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


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


def _fetch_assemblyai(video_id: str, lang: str, **_kw) -> Path:
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "ASSEMBLYAI_API_KEY not set. Get a key from https://www.assemblyai.com "
            "and either export it in your shell or add it to "
            "virtual-jensen-web/.env (the web app reads that file and subsequent "
            "child processes inherit it).\n"
            "If you don't want to pay, use --service whisper (or parakeet) — "
            "both run locally and are free."
        )

    audio = _extract_audio(video_id)
    try:
        print(f"[uploading {audio.stat().st_size // 1024} KB to AssemblyAI]", file=sys.stderr)
        upload_url = _assemblyai_upload(audio, api_key)
        transcript_id = _assemblyai_submit(upload_url, api_key, lang)
        payload = _assemblyai_poll(transcript_id, api_key)
    finally:
        _cleanup_audio(audio)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = TRANSCRIPTS_DIR / f"{video_id}.assemblyai.txt"
    out.write_text(_format_diarized(payload), encoding="utf-8")
    return out


# Dispatch table. Local STT backends share the signature
#   (video_id: str, lang: str, *, model_name: str | None = None,
#    audio_path: Path | None = None) -> tuple[Path, list[(start, text)]]
# so --model can be passed uniformly and --diarize can reuse audio.
# Non-local backends (youtube, assemblyai, rev) return just Path.
_DISPATCH = {
    "whisper":       _fetch_whisper,
    "parakeet":      _fetch_parakeet,
    "parakeet-mlx":  _fetch_parakeet_mlx,
    "youtube":       _fetch_youtube,
    "assemblyai":    _fetch_assemblyai,
    "rev":           _fetch_rev,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Fetch a transcript for a YouTube video. Default backend is "
            "local faster-whisper (free, ~$0). Use --service parakeet for "
            "NVIDIA's Parakeet, --service parakeet-mlx for the Apple-Silicon "
            "port, --service assemblyai for paid + diarization. Add --diarize "
            "to post-process any local STT backend with pyannote."
        ),
    )
    ap.add_argument("video_id", help="11-character YouTube video ID")
    ap.add_argument(
        "--service",
        choices=SERVICES,
        default="whisper",
        help=(
            "Transcription backend. "
            "whisper (default, free, local): faster-whisper distil-large-v3. "
            "parakeet (free, local): NVIDIA Parakeet via NeMo — best English. "
            "parakeet-mlx (free, local, Apple Silicon only): MLX-native "
            "Parakeet port, much lighter than NeMo. "
            "youtube (free, low quality): yt-dlp auto-captions. "
            "assemblyai (paid, ~$0.17/hr): verbatim + speaker diarization. "
            "rev (not wired)."
        ),
    )
    ap.add_argument(
        "--lang",
        default="en",
        help="Language code (default: en). 'auto' lets whisper detect; "
             "parakeet and parakeet-mlx are English-only.",
    )
    ap.add_argument(
        "--model",
        default=None,
        help="Override the model id. For whisper: e.g. 'large-v3', 'base', "
             "'small'. For parakeet: e.g. 'nvidia/parakeet-rnnt-1.1b'. For "
             "parakeet-mlx: e.g. 'mlx-community/parakeet-tdt-0.6b-v2'.",
    )
    ap.add_argument(
        "--diarize",
        action="store_true",
        help="Post-process a local STT transcript with pyannote.audio to "
             "produce speaker-labelled output at "
             "<id>.<service>.diarized.txt. Requires HF_TOKEN (or "
             "HUGGING_FACE_HUB_TOKEN) and that you've accepted the model "
             "terms at https://huggingface.co/pyannote/speaker-diarization-3.1. "
             "Only applies to whisper/parakeet/parakeet-mlx — assemblyai "
             "already produces diarized output natively.",
    )
    args = ap.parse_args()

    fetcher = _DISPATCH[args.service]

    if args.diarize and args.service not in _DIARIZABLE_SERVICES:
        raise SystemExit(
            f"--diarize only supports local STT backends "
            f"({', '.join(_DIARIZABLE_SERVICES)}). "
            "assemblyai already emits speaker-labelled output natively; "
            "youtube/rev do not."
        )

    if args.diarize:
        # Extract once; reuse for both STT and pyannote.
        audio = _extract_audio(args.video_id)
        try:
            path, segments = fetcher(
                args.video_id,
                args.lang,
                model_name=args.model,
                audio_path=audio,
            )
            intervals = _diarize(audio)
        finally:
            _cleanup_audio(audio)
        diarized = _write_diarized(args.video_id, args.service, segments, intervals)
        print(path)
        print(diarized)
    else:
        result = fetcher(args.video_id, args.lang, model_name=args.model)
        # Local STT backends now return (Path, segments); others return Path.
        path = result[0] if isinstance(result, tuple) else result
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
