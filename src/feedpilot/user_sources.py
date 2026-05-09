"""Persistent user-configurable feed sources stored in ~/.feedpilot/sources.json."""

import json
import re
import threading
from pathlib import Path

_CONFIG_DIR = Path.home() / ".feedpilot"
_SOURCES_FILE = _CONFIG_DIR / "sources.json"
_lock = threading.Lock()

_URL_RE = re.compile(r"^https?://\S+$")


def _load_raw() -> list[dict]:
    if not _SOURCES_FILE.exists():
        return []
    try:
        data = json.loads(_SOURCES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save_raw(sources: list[dict]) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _SOURCES_FILE.write_text(json.dumps(sources, indent=2, ensure_ascii=False), encoding="utf-8")


def load_custom_sources() -> list[dict]:
    """Return all user-added custom sources."""
    return _load_raw()


def add_custom_source(name: str, url: str, tags: list[str] | None = None) -> dict:
    """Add a new custom source. Raises ValueError on invalid input or duplicate name."""
    name = name.strip()
    url = url.strip()

    if not name:
        msg = "Source name must not be empty."
        raise ValueError(msg)
    if not _URL_RE.match(url):
        msg = f"Invalid URL: {url!r}. Must start with http:// or https://."
        raise ValueError(msg)

    with _lock:
        sources = _load_raw()
        if any(s["name"].lower() == name.lower() for s in sources):
            msg = f"A custom source named {name!r} already exists."
            raise ValueError(msg)

        clean_tags = [t.strip() for t in (tags or []) if isinstance(t, str) and t.strip()]
        entry = {"name": name, "url": url, "tags": clean_tags}
        sources.append(entry)
        _save_raw(sources)
    return entry


def remove_custom_source(name: str) -> bool:
    """Remove a custom source by name. Returns True if removed, False if not found."""
    with _lock:
        sources = _load_raw()
        updated = [s for s in sources if s["name"].lower() != name.lower()]
        if len(updated) == len(sources):
            return False
        _save_raw(updated)
    return True
