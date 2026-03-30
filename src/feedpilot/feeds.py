"""RSS feed fetching and parsing."""

from datetime import UTC, datetime

import feedparser
import httpx


def _parse_date(entry: feedparser.FeedParserDict) -> str:
    for field in ("published", "updated"):
        raw = entry.get(f"{field}_parsed")
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=UTC).isoformat()
            except Exception:  # noqa: S110
                pass
    return datetime.now(UTC).isoformat()


def fetch_feed(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse an RSS/Atom feed, returning the most recent entries."""
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
    except Exception as exc:
        return [{"error": str(exc), "url": url}]

    return [
        {
            "title": entry.get("title", "(no title)"),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": _parse_date(entry),
        }
        for entry in parsed.entries[:limit]
    ]
