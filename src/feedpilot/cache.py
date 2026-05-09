"""In-memory TTL cache for RSS feed responses."""

import os
import time
from threading import Lock

_DEFAULT_TTL = 1800  # 30 minutes


def _get_ttl() -> int:
    try:
        return int(os.environ.get("FEEDPILOT_CACHE_TTL", _DEFAULT_TTL))
    except ValueError:
        return _DEFAULT_TTL


class _CacheEntry:
    __slots__ = ("expires_at", "fetched_at", "value")

    def __init__(self, value: object, ttl: int) -> None:
        self.fetched_at = time.monotonic()
        self.expires_at = self.fetched_at + ttl
        self.value = value

    def age_seconds(self) -> float:
        return time.monotonic() - self.fetched_at

    def is_expired(self) -> bool:
        return time.monotonic() >= self.expires_at


class FeedCache:
    """Thread-safe in-memory TTL cache for feed responses."""

    def __init__(self) -> None:
        self._store: dict[tuple, _CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: tuple) -> tuple[list[dict] | None, float]:
        """Return (value, age_seconds) or (None, 0.0) on miss/expiry."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None or entry.is_expired():
                if entry is not None:
                    del self._store[key]
                return None, 0.0
            return entry.value, entry.age_seconds()

    def set(self, key: tuple, value: list[dict]) -> None:
        with self._lock:
            self._store[key] = _CacheEntry(value, _get_ttl())

    def invalidate(self, key: tuple) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            total = len(self._store)
            expired = sum(1 for e in self._store.values() if e.is_expired())
            return {"total_entries": total, "expired_entries": expired, "live_entries": total - expired}


_cache = FeedCache()


def get_cache() -> FeedCache:
    """Return the global feed cache singleton."""
    return _cache
