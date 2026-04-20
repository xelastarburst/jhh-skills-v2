"""Pure fetchers — fetch, parse, return structured items. No LLM calls here."""

from . import rss, youtube, html  # noqa: F401

FETCHERS = {
    "rss": rss.fetch,
    "youtube_channel": youtube.fetch_channel,
    "html": html.fetch,
}
