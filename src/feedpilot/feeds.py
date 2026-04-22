"""RSS feed fetching and parsing."""

import asyncio
from datetime import UTC, datetime

import feedparser
import httpx

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; feedpilot/1.0; +https://github.com/ossirytk/feedpilot)"}


def _parse_date(entry: feedparser.FeedParserDict) -> str:
    for field in ("published", "updated"):
        raw = entry.get(f"{field}_parsed")
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=UTC).isoformat()
            except Exception:  # noqa: S110
                pass
    return datetime.now(UTC).isoformat()


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


async def _fetch_one(url: str, limit: int, client: httpx.AsyncClient) -> list[dict]:
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
        return _parse_entries(parsed, limit)
    except Exception as exc:
        return [{"error": str(exc), "url": url}]


async def fetch_feed(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse a single RSS/Atom feed."""
    async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
        return await _fetch_one(url, limit, client)


async def fetch_many(sources: list[tuple[str, int]]) -> list[list[dict]]:
    """Fetch multiple RSS/Atom feeds in parallel, sharing a single HTTP client."""
    async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
        tasks = [_fetch_one(url, limit, client) for url, limit in sources]
        results = await asyncio.gather(*tasks)
    return list(results)
