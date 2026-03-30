"""Feedpilot MCP server — daily tech digest tools."""

from fastmcp import FastMCP

from feedpilot.feeds import fetch_feed
from feedpilot.sources import SOURCES

mcp = FastMCP(
    name="feedpilot",
    instructions=(
        "Feedpilot delivers a daily tech digest from RSS/Atom feeds. "
        "Use `digest` to get headlines across all default sources. "
        "Use `headlines` to fetch from a specific source by name or URL. "
        "Use `list_sources` to see the available default feeds."
    ),
)


@mcp.tool
def list_sources() -> list[dict]:
    """Return all configured default feed sources with their tags."""
    return SOURCES


@mcp.tool
def headlines(source: str, limit: int = 10) -> list[dict]:
    """Fetch recent headlines from a specific source.

    Args:
        source: Name of a default source (e.g. 'Phoronix') or a raw feed URL.
        limit: Maximum number of items to return.
    """
    url = source
    for s in SOURCES:
        if s["name"].lower() == source.lower():
            url = s["url"]
            break

    return fetch_feed(url, limit=limit)


@mcp.tool
def digest(limit_per_source: int = 5, tags: list[str] | None = None) -> dict[str, list[dict]]:
    """Fetch headlines from all default sources and return a combined digest.

    Args:
        limit_per_source: Number of items to fetch per source.
        tags: Optional list of tags to filter sources (e.g. ['linux', 'hardware']).
              If empty, all sources are included.
    """
    sources = SOURCES
    if tags:
        tag_set = {t.lower() for t in tags}
        sources = [s for s in sources if tag_set.intersection(t.lower() for t in s["tags"])]

    result = {}
    for source in sources:
        result[source["name"]] = fetch_feed(source["url"], limit=limit_per_source)
    return result


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
