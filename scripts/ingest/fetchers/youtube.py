"""YouTube channel fetcher (yt-dlp backend).

YouTube's free ``videos.xml`` RSS endpoint was deprecated in 2026 and now
returns 404 for every channel. This fetcher uses ``yt-dlp --flat-playlist``
against the channel's ``/videos`` page to enumerate recent uploads. It
returns the same item shape as ``rss.py`` so ``run.py`` doesn't have to
care about the backend swap.

We deliberately use ``--flat-playlist`` (metadata only, no per-video
network round-trip) to keep the daily monitoring run cheap. Full
transcripts are an opt-in upgrade — see ``upgrade_transcript.py``.

Resolution path:
    handle (@foo) ──► http_get HTML ──► externalId regex ──► channel_id
    channel_id ──► yt-dlp --flat-playlist ──► list[video JSON]

The handle→channel_id mapping is cached in ``state['_youtube_channels']``
across runs so we don't re-hit the HTML for every daily pass.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import List, Optional

_CHANNEL_ID_RE = re.compile(r'"externalId":"(UC[\w-]{22})"')
_UPLOADS_URL = "https://www.youtube.com/channel/{cid}/videos"
_YT_DLP_TIMEOUT = 30
_PLAYLIST_ITEMS = "1:15"


class YouTubeFeedUnavailable(Exception):
    """Raised when we can't enumerate a channel's uploads."""


def _resolve_channel_id(handle: str, state: dict, *, http_get) -> Optional[str]:
    """Resolve ``@handle`` -> ``UCxxxxxxxxxxxxxxxxxxxxxx``. Cached in state."""
    cache = state.setdefault("_youtube_channels", {})
    if handle in cache:
        return cache[handle]
    try:
        html = http_get(f"https://www.youtube.com/{handle}")
    except Exception:
        return None
    m = _CHANNEL_ID_RE.search(html)
    if not m:
        return None
    cid = m.group(1)
    cache[handle] = cid
    return cid


def fetch_channel(
    source: dict, *, http_get, state: Optional[dict] = None
) -> List[dict]:
    channel_id = source.get("channel_id")
    if not channel_id:
        handle = source.get("handle")
        if not handle:
            return []
        state = state if state is not None else {}
        channel_id = _resolve_channel_id(handle, state, http_get=http_get)
        if not channel_id:
            raise YouTubeFeedUnavailable(
                f"could not resolve channel id for handle {handle!r}"
            )

    return _fetch_via_yt_dlp(channel_id)


# ---------------------------------------------------------------------------
# yt-dlp backend
# ---------------------------------------------------------------------------


def _yt_dlp_path() -> Optional[str]:
    # Look up every call rather than at import time, so a user who pip-installs
    # yt-dlp mid-session doesn't have to restart the runner.
    return shutil.which("yt-dlp")


def _fetch_via_yt_dlp(channel_id: str) -> List[dict]:
    """Enumerate a channel's recent uploads via ``yt-dlp --flat-playlist``."""
    binary = _yt_dlp_path()
    if not binary:
        raise YouTubeFeedUnavailable(
            "yt-dlp not installed; run: pip install yt-dlp"
        )

    url = _UPLOADS_URL.format(cid=channel_id)
    cmd = [
        binary,
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--playlist-items", _PLAYLIST_ITEMS,
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
    except subprocess.TimeoutExpired as e:
        raise YouTubeFeedUnavailable(
            f"yt-dlp timed out after {_YT_DLP_TIMEOUT}s for {channel_id}"
        ) from e
    except FileNotFoundError as e:
        # Race: PATH lookup succeeded but exec didn't. Treat as "not installed".
        raise YouTubeFeedUnavailable(
            "yt-dlp not installed; run: pip install yt-dlp"
        ) from e

    if proc.returncode != 0:
        stderr_tail = (proc.stderr or "").strip().splitlines()[-3:]
        tail = " | ".join(stderr_tail) or f"exit {proc.returncode}"
        raise YouTubeFeedUnavailable(f"yt-dlp failed: {tail}")

    items: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            # Skip malformed lines rather than taking down the whole channel.
            continue
        vid = obj.get("id")
        if not vid:
            continue
        items.append({
            "id": vid,
            "title": obj.get("title") or "",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "published": _published_from_yt_dlp(obj),
            "summary": "",
        })
    return items


def _published_from_yt_dlp(obj: dict) -> Optional[str]:
    """Pull a best-effort ISO8601 timestamp out of a yt-dlp entry.

    ``--flat-playlist`` usually omits ``timestamp``; ``upload_date`` (YYYYMMDD)
    is sometimes present. Either way we normalize to UTC ISO8601 so the runner
    can print it uniformly.
    """
    ts = obj.get("timestamp")
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            pass
    upload_date = obj.get("upload_date")
    if isinstance(upload_date, str) and len(upload_date) == 8 and upload_date.isdigit():
        try:
            dt = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            pass
    return None
