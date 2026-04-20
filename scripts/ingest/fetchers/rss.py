"""Generic RSS/Atom fetcher.

Returns a list of items:
    {"id": <entry link or guid>, "title": ..., "url": ..., "published": ISO8601 or None, "summary": ...}

Uses ``feedparser`` if available; otherwise falls back to a tiny regex-based
parser that handles the common RSS 2.0 shape we encounter.
"""

from __future__ import annotations

import re
from typing import List, Optional

try:
    import feedparser  # type: ignore
    _HAS_FEEDPARSER = True
except Exception:  # noqa: BLE001
    _HAS_FEEDPARSER = False


def fetch(source: dict, *, http_get) -> List[dict]:
    url = source["url"]
    body = http_get(url)
    if _HAS_FEEDPARSER:
        return _parse_with_feedparser(body)
    return _parse_minimal(body)


def _parse_with_feedparser(body: str) -> List[dict]:
    parsed = feedparser.parse(body)
    items = []
    for e in parsed.entries:
        link = getattr(e, "link", "") or ""
        guid = getattr(e, "id", "") or link
        items.append({
            "id": guid,
            "title": getattr(e, "title", ""),
            "url": link,
            "published": getattr(e, "published", None),
            "summary": getattr(e, "summary", ""),
        })
    return items


_ITEM_RE = re.compile(
    r"<item[^>]*>(.*?)</item>|<entry[^>]*>(.*?)</entry>",
    re.DOTALL | re.IGNORECASE,
)
_FIELD_RE = re.compile(
    r"<(title|link|guid|id|pubDate|published|summary|description)[^>]*>(.*?)</\1>",
    re.DOTALL | re.IGNORECASE,
)
_CDATA_RE = re.compile(r"^<!\[CDATA\[(.*)\]\]>$", re.DOTALL)


def _parse_minimal(body: str) -> List[dict]:
    items = []
    for m in _ITEM_RE.finditer(body):
        chunk = m.group(1) or m.group(2) or ""
        fields = {}
        for fm in _FIELD_RE.finditer(chunk):
            key, val = fm.group(1).lower(), fm.group(2).strip()
            mc = _CDATA_RE.match(val)
            if mc:
                val = mc.group(1)
            fields.setdefault(key, val)
        url = fields.get("link") or ""
        # atom <link href="..."/>
        if not url:
            hm = re.search(r'<link[^>]*href="([^"]+)"', chunk, re.IGNORECASE)
            if hm:
                url = hm.group(1)
        items.append({
            "id": fields.get("guid") or fields.get("id") or url,
            "title": _strip_tags(fields.get("title", "")),
            "url": url,
            "published": fields.get("pubdate") or fields.get("published"),
            "summary": _strip_tags(fields.get("description") or fields.get("summary", "")),
        })
    return items


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()
