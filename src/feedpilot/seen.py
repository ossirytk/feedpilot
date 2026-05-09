"""Read/seen tracking for feed items using a local SQLite store."""

import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path

_DB_DIR = Path.home() / ".feedpilot"
_DB_PATH = _DB_DIR / "seen.db"

# Single shared connection with WAL mode for better concurrency.
# check_same_thread=False is safe because _lock serialises all access.
_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn  # noqa: PLW0603
    if _conn is None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(_DB_PATH), timeout=30, check_same_thread=False)
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("CREATE TABLE IF NOT EXISTS seen_items (url TEXT PRIMARY KEY, seen_at TEXT NOT NULL)")
        _conn.commit()
    return _conn


def _valid_urls(urls: list[str]) -> list[str]:
    """Return only non-empty string URLs from the input list."""
    return [u for u in urls if isinstance(u, str) and u.strip()]


def mark_seen(urls: list[str]) -> int:
    """Record URLs as seen. Returns the number of newly inserted rows."""
    clean = _valid_urls(urls)
    if not clean:
        return 0
    now = datetime.now(UTC).isoformat()
    with _lock:
        conn = _get_conn()
        result = conn.executemany(
            "INSERT OR IGNORE INTO seen_items (url, seen_at) VALUES (?, ?)",
            [(url, now) for url in clean],
        )
        conn.commit()
        return result.rowcount


def has_seen(url: str) -> bool:
    """Return True if the URL has previously been marked seen."""
    if not isinstance(url, str) or not url.strip():
        return False
    with _lock:
        conn = _get_conn()
        row = conn.execute("SELECT 1 FROM seen_items WHERE url = ?", (url,)).fetchone()
    return row is not None


def filter_unseen(entries: list[dict]) -> list[dict]:
    """Return only entries whose 'url' has not been marked seen."""
    if not entries:
        return []
    valid_urls = [u for e in entries if (u := e.get("url", "")) and u]
    if not valid_urls:
        return entries
    placeholders = ",".join("?" * len(valid_urls))
    with _lock:
        conn = _get_conn()
        seen_set = {
            row[0]
            for row in conn.execute(
                f"SELECT url FROM seen_items WHERE url IN ({placeholders})",  # noqa: S608
                valid_urls,
            ).fetchall()
        }
    return [e for e in entries if e.get("url", "") not in seen_set]


def seen_count() -> int:
    """Return total number of seen items."""
    with _lock:
        conn = _get_conn()
        row = conn.execute("SELECT COUNT(*) FROM seen_items").fetchone()
    return row[0] if row else 0
