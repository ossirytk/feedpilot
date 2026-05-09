"""Feedpilot MCP server — daily tech digest tools."""

from datetime import UTC, datetime
from pathlib import Path

from fastmcp import FastMCP

from feedpilot.feeds import FetchResult, fetch_feed, fetch_many
from feedpilot.seen import filter_unseen
from feedpilot.seen import mark_seen as _mark_seen
from feedpilot.sources import SOURCES
from feedpilot.user_sources import add_custom_source, load_custom_sources, remove_custom_source

mcp = FastMCP(
    name="feedpilot",
    instructions=(
        "Feedpilot delivers a daily tech digest from RSS/Atom feeds. "
        "Use `digest` to get headlines across all default sources. "
        "Use `headlines` to fetch from a specific source by name or URL. "
        "Use `multi_headlines` to fetch from several named sources in one call. "
        "Use `list_sources` to see the available default feeds. "
        "Use `search` to filter headlines across all sources by keyword. "
        "Use `mark_seen` to record articles you have read. "
        "Use `add_source` / `remove_source` / `list_custom_sources` to manage personal feeds. "
        "Use `export_digest` to save today's digest as a Markdown or Org-mode file."
    ),
)


def _all_sources() -> list[dict]:
    """Return built-in sources merged with user-defined custom sources."""
    custom = load_custom_sources()
    built_in_names = {s["name"].lower() for s in SOURCES}
    extras = [s for s in custom if s["name"].lower() not in built_in_names]
    return SOURCES + extras


def _result_to_dict(result: FetchResult) -> dict:
    """Serialise a FetchResult into a plain dict for MCP responses."""
    out: dict = {"items": result.entries}
    if result.last_updated:
        out["last_updated"] = result.last_updated
    if result.cache_age_seconds > 0:
        out["cache_age_seconds"] = round(result.cache_age_seconds, 1)
    return out


def _build_response(
    sources: list[dict],
    results: list[FetchResult],
    *,
    unseen_only: bool = False,
) -> dict:
    """Build a multi-source response with per-source data and a top-level errors block."""
    out: dict = {}
    errors: dict[str, str] = {}

    for source, result in zip(sources, results, strict=True):
        name = source["name"]
        if result.error:
            errors[name] = result.error
            continue
        entries = filter_unseen(result.entries) if unseen_only else result.entries
        source_out = {"items": entries}
        if result.last_updated:
            source_out["last_updated"] = result.last_updated  # type: ignore[assignment]
        if result.cache_age_seconds > 0:
            source_out["cache_age_seconds"] = round(result.cache_age_seconds, 1)  # type: ignore[assignment]
        out[name] = source_out

    if errors:
        out["errors"] = errors  # type: ignore[assignment]

    return out


@mcp.tool
def list_sources() -> list[dict]:
    """Return all configured default feed sources with their tags."""
    return _all_sources()


@mcp.tool
async def headlines(
    source: str,
    limit: int = 10,
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
    unseen_only: bool = False,
) -> dict:
    """Fetch recent headlines from a specific source.

    Args:
        source: Name of a default source (e.g. 'Phoronix') or a raw feed URL.
        limit: Maximum number of items to return.
        force_refresh: Bypass the cache and fetch live data.
        fetch_summaries: Follow each article URL and include a short body preview.
        unseen_only: Return only articles not yet marked as seen.
    """
    url = source
    for s in _all_sources():
        if s["name"].lower() == source.lower():
            url = s["url"]
            break

    result = await fetch_feed(url, limit=limit, force_refresh=force_refresh, fetch_summaries=fetch_summaries)

    if result.error:
        return {"items": [], "error": result.error}

    entries = filter_unseen(result.entries) if unseen_only else result.entries
    out: dict = {"items": entries}
    if result.last_updated:
        out["last_updated"] = result.last_updated
    if result.cache_age_seconds > 0:
        out["cache_age_seconds"] = round(result.cache_age_seconds, 1)
    return out


@mcp.tool
async def multi_headlines(
    sources: list[str],
    limit: int = 10,
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
    unseen_only: bool = False,
) -> dict:
    """Fetch recent headlines from several sources in parallel.

    Args:
        sources: List of source names (e.g. ['Phoronix', 'LKML']) or raw feed URLs.
        limit: Maximum number of items to return per source.
        force_refresh: Bypass the cache and fetch live data.
        fetch_summaries: Follow each article URL and include a short body preview.
        unseen_only: Return only articles not yet marked as seen.
    """
    name_to_url = {s["name"].lower(): s["url"] for s in _all_sources()}
    resolved = [(name_to_url.get(s.lower(), s), s) for s in sources]

    pairs = [(url, limit) for url, _ in resolved]
    results = await fetch_many(pairs, force_refresh=force_refresh, fetch_summaries=fetch_summaries)

    source_dicts = [{"name": label} for _, label in resolved]
    return _build_response(source_dicts, results, unseen_only=unseen_only)


@mcp.tool
async def digest(  # noqa: PLR0913
    limit_per_source: int = 5,
    tags: list[str] | None = None,
    exclude: list[str] | None = None,
    overrides: dict[str, int] | None = None,
    *,
    force_refresh: bool = False,
    fetch_summaries: bool = False,
    unseen_only: bool = False,
) -> dict:
    """Fetch headlines from all default sources and return a combined digest.

    Args:
        limit_per_source: Default number of items to fetch per source.
        tags: Optional list of tags to filter sources (e.g. ['linux', 'hardware']).
              If empty, all sources are included.
        exclude: Optional list of source names to skip (e.g. ['LKML']).
        overrides: Optional per-source item limits (e.g. {'LKML': 3, 'Phoronix': 10}).
                   Unspecified sources use limit_per_source.
        force_refresh: Bypass the cache and fetch live data.
        fetch_summaries: Follow each article URL and include a short body preview.
        unseen_only: Return only articles not yet marked as seen.
    """
    sources = _all_sources()
    if tags:
        tag_set = {t.lower() for t in tags}
        sources = [s for s in sources if tag_set.intersection(t.lower() for t in s.get("tags", []))]
    if exclude:
        exclude_set = {e.lower() for e in exclude}
        sources = [s for s in sources if s["name"].lower() not in exclude_set]

    override_map = {str(k).lower(): v for k, v in overrides.items()} if overrides else {}
    pairs = [(s["url"], override_map.get(s["name"].lower(), limit_per_source)) for s in sources]
    results = await fetch_many(pairs, force_refresh=force_refresh, fetch_summaries=fetch_summaries)
    return _build_response(sources, results, unseen_only=unseen_only)


@mcp.tool
async def search(
    query: str,
    tags: list[str] | None = None,
    limit_per_source: int = 10,
    *,
    force_refresh: bool = False,
) -> dict:
    """Search headlines across all sources by keyword.

    Fetches all sources (optionally pre-filtered by tag), then returns only entries
    whose title or summary contains the query string (case-insensitive).

    Args:
        query: Keyword or phrase to search for.
        tags: Optional list of source tags to restrict which sources are searched.
        limit_per_source: Maximum items to fetch per source before filtering.
        force_refresh: Bypass the cache and fetch live data.
    """
    sources = _all_sources()
    if tags:
        tag_set = {t.lower() for t in tags}
        sources = [s for s in sources if tag_set.intersection(t.lower() for t in s.get("tags", []))]

    pairs = [(s["url"], limit_per_source) for s in sources]
    results = await fetch_many(pairs, force_refresh=force_refresh)

    q = query.lower()
    out: dict = {}
    errors: dict[str, str] = {}

    for source, result in zip(sources, results, strict=True):
        if result.error:
            errors[source["name"]] = result.error
            continue
        matched = [e for e in result.entries if q in e.get("title", "").lower() or q in e.get("summary", "").lower()]
        if matched:
            out[source["name"]] = matched

    if errors:
        out["errors"] = errors  # type: ignore[assignment]

    return out


@mcp.tool
def mark_seen(urls: list[str]) -> dict:
    """Mark article URLs as read/seen so they can be excluded from future digests.

    Args:
        urls: List of article URLs to mark as seen.
    """
    newly_seen = _mark_seen(urls)
    return {"marked": newly_seen, "total_provided": len(urls)}


@mcp.tool
def add_source(name: str, url: str, tags: list[str] | None = None) -> dict:
    """Add a custom feed source to your personal source list.

    Args:
        name: Display name for the source (must be unique).
        url: RSS/Atom feed URL (must start with http:// or https://).
        tags: Optional list of tags for filtering (e.g. ['tech', 'linux']).
    """
    try:
        entry = add_custom_source(name, url, tags)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    else:
        return {"status": "added", "source": entry}


@mcp.tool
def remove_source(name: str) -> dict:
    """Remove a custom feed source from your personal source list.

    Args:
        name: Name of the custom source to remove.
    """
    removed = remove_custom_source(name)
    if removed:
        return {"status": "removed", "name": name}
    return {"status": "not_found", "name": name}


@mcp.tool
def list_custom_sources() -> list[dict]:
    """Return all user-added custom feed sources."""
    return load_custom_sources()


@mcp.tool
async def export_digest(
    format: str = "markdown",  # noqa: A002
    path: str | None = None,
    limit_per_source: int = 5,
    tags: list[str] | None = None,
) -> dict:
    """Fetch today's digest and export it to a Markdown or Org-mode file.

    Args:
        format: Output format — 'markdown' or 'org'.
        path: Destination file path. Defaults to ~/.feedpilot/YYYY-MM-DD.md or .org.
        limit_per_source: Items to include per source.
        tags: Optional tag filter for sources.
    """
    fmt = format.lower().strip()
    if fmt not in {"markdown", "org"}:
        return {"status": "error", "message": f"Unsupported format {format!r}. Use 'markdown' or 'org'."}

    sources = _all_sources()
    if tags:
        tag_set = {t.lower() for t in tags}
        sources = [s for s in sources if tag_set.intersection(t.lower() for t in s.get("tags", []))]

    pairs = [(s["url"], limit_per_source) for s in sources]
    results = await fetch_many(pairs)

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    ext = "org" if fmt == "org" else "md"

    out_path = Path(path) if path else Path.home() / ".feedpilot" / f"{today}.{ext}"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if fmt == "markdown":
        lines.append(f"# Feed Digest — {today}\n")
        for source, result in zip(sources, results, strict=True):
            if result.error or not result.entries:
                continue
            lines.append(f"\n## {source['name']}\n")
            for entry in result.entries:
                pub = entry.get("published", "")
                lines.append(f"- [{entry['title']}]({entry['url']}) — {pub}")
    else:  # org
        lines.append(f"#+TITLE: Feed Digest — {today}")
        lines.append("#+STARTUP: overview\n")
        for source, result in zip(sources, results, strict=True):
            if result.error or not result.entries:
                continue
            tag_str = ":".join(source.get("tags", [])) or ""
            tag_block = f"  :{tag_str}:" if tag_str else ""
            lines.append(f"\n* {source['name']}{tag_block}")
            for entry in result.entries:
                pub = entry.get("published", "")
                lines.append(f"** [[{entry['url']}][{entry['title']}]]")
                lines.append(":PROPERTIES:")
                lines.append(f":DATE: {pub}")
                lines.append(":END:")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": "ok", "path": str(out_path), "format": fmt}


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
