"""RSS feed fetching and parsing."""

import asyncio
import html
import html.parser
from datetime import UTC, datetime
from typing import Any

import feedparser
import httpx

from feedpilot.cache import get_cache

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; feedpilot/1.0; +https://github.com/ossirytk/feedpilot)"}


class _TextExtractor(html.parser.HTMLParser):
    """Minimal HTML parser that strips tags and collects text."""

    _SKIP_TAGS = frozenset({"script", "style", "head", "noscript"})

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip: int = 0

    def handle_starttag(self, tag: str, attrs: Any) -> None:  # noqa: ANN401, ARG002
        if tag in self._SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if self._skip == 0:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    def text(self) -> str:
        return " ".join(self._parts)


def _strip_html(raw: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(html.unescape(raw))
    return extractor.text()


def _parse_date(entry: feedparser.FeedParserDict) -> str:
    for field in ("published", "updated"):
        raw = entry.get(f"{field}_parsed")
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=UTC).isoformat()
            except Exception:  # noqa: S110
                pass
    return datetime.now(UTC).isoformat()


def _feed_last_updated(parsed: feedparser.FeedParserDict) -> str | None:
    feed = parsed.get("feed", {})
    for field in ("updated_parsed", "published_parsed"):
        raw = feed.get(field)
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=UTC).isoformat()
            except Exception:  # noqa: S110
                pass
    return None


def _parse_entries(parsed: feedparser.FeedParserDict, limit: int) -> list[dict]:
    return [
        {
            "title": entry.get("title", "(no title)"),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": _parse_date(entry),
        }
        for entry in parsed.entries[:limit]
    ]


async def _fetch_article_preview(url: str, client: httpx.AsyncClient, max_chars: int = 500) -> str | None:
    if not url:
        return None
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        text = _strip_html(resp.text)
        return text[:max_chars] if text else None
    except Exception:
        return None


class FetchResult:
    """Structured result from fetching a single feed."""

    __slots__ = ("cache_age_seconds", "entries", "error", "last_updated")

    def __init__(
        self,
        entries: list[dict],
        *,
        error: str | None = None,
        last_updated: str | None = None,
        cache_age_seconds: float = 0.0,
    ) -> None:
        self.entries = entries
        self.error = error
        self.last_updated = last_updated
        self.cache_age_seconds = cache_age_seconds


async def _fetch_one(
    url: str,
    limit: int,
    client: httpx.AsyncClient,
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
) -> FetchResult:
    cache = get_cache()
    cache_key = (url, limit, fetch_summaries)

    if not force_refresh:
        cached, age = cache.get(cache_key)
        if cached is not None:
            return FetchResult(cached, cache_age_seconds=age)

    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
        entries = _parse_entries(parsed, limit)
        last_updated = _feed_last_updated(parsed)

        if fetch_summaries:
            for entry in entries:
                entry["preview"] = await _fetch_article_preview(entry["url"], client)

        cache.set(cache_key, entries)
        return FetchResult(entries, last_updated=last_updated)
    except Exception as exc:
        return FetchResult([], error=str(exc), last_updated=None)


async def fetch_feed(
    url: str,
    limit: int = 10,
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
) -> FetchResult:
    """Fetch and parse a single RSS/Atom feed."""
    async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
        return await _fetch_one(url, limit, client, force_refresh=force_refresh, fetch_summaries=fetch_summaries)


async def fetch_many(
    sources: list[tuple[str, int]],
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
) -> list[FetchResult]:
    """Fetch multiple RSS/Atom feeds in parallel, sharing a single HTTP client."""
    async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
        tasks = [
            _fetch_one(url, limit, client, force_refresh=force_refresh, fetch_summaries=fetch_summaries)
            for url, limit in sources
        ]
        results = await asyncio.gather(*tasks)
    return list(results)
