"""Read/seen tracking for feed items using a local SQLite store."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

_DB_DIR = Path.home() / ".feedpilot"
_DB_PATH = _DB_DIR / "seen.db"


def _connect() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS seen_items (url TEXT PRIMARY KEY, seen_at TEXT NOT NULL)")
    conn.commit()
    return conn


def mark_seen(urls: list[str]) -> int:
    """Record URLs as seen. Returns the number of newly inserted rows."""
    if not urls:
        return 0
    now = datetime.now(UTC).isoformat()
    with _connect() as conn:
        result = conn.executemany(
            "INSERT OR IGNORE INTO seen_items (url, seen_at) VALUES (?, ?)",
            [(url, now) for url in urls],
        )
        conn.commit()
        return result.rowcount


def has_seen(url: str) -> bool:
    """Return True if the URL has previously been marked seen."""
    with _connect() as conn:
        row = conn.execute("SELECT 1 FROM seen_items WHERE url = ?", (url,)).fetchone()
    return row is not None


def filter_unseen(entries: list[dict]) -> list[dict]:
    """Return only entries whose 'url' has not been marked seen."""
    if not entries:
        return []
    with _connect() as conn:
        urls = [e.get("url", "") for e in entries]
        placeholders = ",".join("?" * len(urls))
        seen_set = {
            row[0]
            for row in conn.execute(
                f"SELECT url FROM seen_items WHERE url IN ({placeholders})",  # noqa: S608
                urls,
            ).fetchall()
        }
    return [e for e in entries if e.get("url", "") not in seen_set]


def seen_count() -> int:
    """Return total number of seen items."""
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) FROM seen_items").fetchone()
    return row[0] if row else 0
