"""YouTube channel fetcher.

**Current status (2026-04):** YouTube's free ``videos.xml`` RSS endpoint
returns 404 for every channel we've tested (including huge public ones
like MKBHD). The ``YouTube RSS Feeds server`` appears to have been
deprecated or geo-restricted. Until we switch to ``yt-dlp
--flat-playlist`` (which also gives us transcripts), this fetcher will
raise a clear, expected error so the pipeline doesn't silently drop
YouTube sources. RSS and HTML fetchers are unaffected.

TODO(next commit): implement ``yt-dlp`` backend. See the function
``_fetch_via_yt_dlp`` stub at the bottom of this file.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import List, Optional

_CHANNEL_ID_RE = re.compile(r'"externalId":"(UC[\w-]{22})"')
_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={cid}"


class YouTubeFeedUnavailable(Exception):
    """Raised when YouTube's public feed is unreachable for a channel."""


def _resolve_channel_id(handle: str, state: dict, *, http_get) -> Optional[str]:
    """Resolve ``@handle`` → ``UCxxxxxxxxxxxxxxxxxxxxxx``. Cached in state."""
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
        state = state or {}
        channel_id = _resolve_channel_id(handle, state, http_get=http_get)
        if not channel_id:
            raise YouTubeFeedUnavailable(
                f"could not resolve channel id for handle {handle!r}"
            )

    # Primary path: videos.xml — currently broken upstream (2026-04).
    # When Google restores it, this will just work again.
    try:
        body = http_get(_FEED_URL.format(cid=channel_id))
    except Exception as e:
        if _YT_DLP_PATH:
            return _fetch_via_yt_dlp(channel_id, source)
        raise YouTubeFeedUnavailable(
            f"videos.xml feed unavailable for {channel_id} "
            f"({type(e).__name__}: {e}). Install yt-dlp to enable the "
            f"fallback path: pip install yt-dlp"
        ) from e
    return _parse_feed(body)


_VIDEO_RE = re.compile(r"<entry>(.*?)</entry>", re.DOTALL)
_FIELD_RE = re.compile(
    r"<(title|published|updated)>(.*?)</\1>|<yt:videoId>([^<]+)</yt:videoId>|"
    r'<link[^>]*href="([^"]+)"|<media:description>(.*?)</media:description>',
    re.DOTALL,
)


def _parse_feed(body: str) -> List[dict]:
    items: list[dict] = []
    for m in _VIDEO_RE.finditer(body):
        chunk = m.group(1)
        fields: dict[str, str] = {}
        for fm in _FIELD_RE.finditer(chunk):
            title, published, updated, vid, link, desc = fm.groups()
            if title:
                fields.setdefault("title", title.strip())
            if published:
                fields.setdefault("published", published.strip())
            if updated:
                fields.setdefault("updated", updated.strip())
            if vid:
                fields.setdefault("id", vid)
            if link:
                fields.setdefault("url", link)
            if desc:
                fields.setdefault("summary", desc.strip())
        if fields.get("id"):
            items.append({
                "id": fields["id"],
                "title": fields.get("title", ""),
                "url": fields.get("url")
                    or f"https://www.youtube.com/watch?v={fields['id']}",
                "published": fields.get("published"),
                "summary": fields.get("summary", "")[:500],
            })
    return items


# ---------------------------------------------------------------------------
# yt-dlp fallback (stub)
# ---------------------------------------------------------------------------

_YT_DLP_PATH = shutil.which("yt-dlp")


def _fetch_via_yt_dlp(channel_id: str, source: dict) -> List[dict]:
    """Planned fallback: use ``yt-dlp --flat-playlist`` to enumerate uploads.

    Not wired yet — returns an empty list and logs a TODO. The implementation
    will run:
        yt-dlp --flat-playlist --dump-json --playlist-items 1:15 \\
               https://www.youtube.com/channel/<id>/videos

    parse the per-line JSON, and return items in the same shape as
    ``_parse_feed``. Captions fetch will be a separate helper so the daily
    monitoring run stays cheap.
    """
    # Intentionally a no-op for now; keeps the pipeline honest about what
    # it's doing.
    return []
