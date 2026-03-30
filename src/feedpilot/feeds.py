"""RSS feed fetching and parsing."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx


def _parse_date(entry) -> str:
    for field in ("published", "updated"):
        raw = entry.get(f"{field}_parsed")
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def fetch_feed(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse an RSS/Atom feed, returning the most recent entries."""
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)
    except Exception as exc:
        return [{"error": str(exc), "url": url}]

    results = []
    for entry in parsed.entries[:limit]:
        results.append(
            {
                "title": entry.get("title", "(no title)"),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": _parse_date(entry),
            }
        )
    return results
