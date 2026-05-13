from __future__ import annotations

import importlib

import pytest

import feedpilot.seen as seen_module
import feedpilot.server as server_module
import feedpilot.user_sources as user_sources_module
from feedpilot.cache import get_cache
from feedpilot.feeds import FetchResult, fetch_feed
from feedpilot.server import (
    add_source,
    digest,
    export_digest,
    headlines,
    list_custom_sources,
    list_sources,
    mark_seen,
    multi_headlines,
    remove_source,
    search,
)


@pytest.fixture()
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    importlib.reload(seen_module)
    importlib.reload(user_sources_module)
    monkeypatch.setattr(server_module, "add_custom_source", user_sources_module.add_custom_source)
    monkeypatch.setattr(server_module, "load_custom_sources", user_sources_module.load_custom_sources)
    monkeypatch.setattr(server_module, "remove_custom_source", user_sources_module.remove_custom_source)
    get_cache().clear()
    return tmp_path


def test_seen_and_custom_source_helpers(isolated_home) -> None:
    del isolated_home
    first_inserted = seen_module.mark_seen(["https://example.com/a", "https://example.com/a", ""])
    assert first_inserted == 1
    assert seen_module.has_seen("https://example.com/a")
    assert seen_module.seen_count() == 1

    filtered = seen_module.filter_unseen([{"url": "https://example.com/a"}, {"url": "https://example.com/b"}])
    assert filtered == [{"url": "https://example.com/b"}]

    added = user_sources_module.add_custom_source("Custom Feed", "https://example.com/feed.xml", ["tech", "oss"])
    assert added["name"] == "Custom Feed"
    assert user_sources_module.load_custom_sources()[0]["url"] == "https://example.com/feed.xml"
    assert user_sources_module.remove_custom_source("Custom Feed")
    assert not user_sources_module.remove_custom_source("Custom Feed")

    with pytest.raises(ValueError, match="must not be empty"):
        user_sources_module.add_custom_source("   ", "https://example.com/feed.xml")
    with pytest.raises(ValueError, match="Invalid URL"):
        user_sources_module.add_custom_source("Broken", "ftp://example.com/feed.xml")


@pytest.mark.asyncio()
async def test_fetch_feed_with_cache_and_preview(isolated_home, respx_mock) -> None:
    del isolated_home
    rss = """<?xml version='1.0'?>
    <rss version='2.0'>
      <channel>
        <title>Demo Feed</title>
        <lastBuildDate>Mon, 15 Jan 2024 00:00:00 GMT</lastBuildDate>
        <item>
          <title>Article One</title>
          <link>https://example.com/article-1</link>
          <description>Summary one</description>
          <pubDate>Mon, 15 Jan 2024 00:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """
    feed_route = respx_mock.get("https://example.com/feed.xml").mock(
        return_value=pytest.importorskip("httpx").Response(200, text=rss)
    )
    article_route = respx_mock.get("https://example.com/article-1").mock(
        return_value=pytest.importorskip("httpx").Response(
            200, text="<html><body><h1>Title</h1><p>Hello <b>world</b></p></body></html>"
        )
    )

    result = await fetch_feed("https://example.com/feed.xml", limit=1, fetch_summaries=True)
    assert result.error is None
    assert len(result.entries) == 1
    assert result.entries[0]["title"] == "Article One"
    assert "Hello world" in result.entries[0]["preview"]
    assert result.last_updated is not None

    cached = await fetch_feed("https://example.com/feed.xml", limit=1, fetch_summaries=True)
    assert cached.cache_age_seconds >= 0
    assert feed_route.call_count == 1
    assert article_route.call_count == 1


@pytest.mark.asyncio()
async def test_fetch_feed_error_path(isolated_home, respx_mock) -> None:
    del isolated_home
    respx_mock.get("https://example.com/fail.xml").mock(
        return_value=pytest.importorskip("httpx").Response(500, text="boom")
    )
    result = await fetch_feed("https://example.com/fail.xml")
    assert result.entries == []
    assert result.error is not None


@pytest.mark.asyncio()
async def test_server_tools_with_mocked_fetchers(isolated_home, monkeypatch) -> None:
    del isolated_home
    fake_sources = [
        {"name": "Linux", "url": "https://linux.example/feed", "tags": ["linux", "kernel"]},
        {"name": "Dev", "url": "https://dev.example/feed", "tags": ["devtools"]},
    ]

    async def fake_fetch_feed(url, limit=10, **kwargs):
        del limit, kwargs
        if "fail" in url:
            return FetchResult([], error="failed")
        return FetchResult(
            [
                {
                    "title": "Kernel release",
                    "url": "https://example.com/kernel",
                    "summary": "linux news",
                    "published": "2026-01-01T00:00:00+00:00",
                },
                {
                    "title": "Dev update",
                    "url": "https://example.com/dev",
                    "summary": "tooling update",
                    "published": "2026-01-01T00:00:00+00:00",
                },
            ],
            last_updated="2026-01-01T00:00:00+00:00",
            cache_age_seconds=2.3,
        )

    async def fake_fetch_many(pairs, **kwargs):
        del kwargs
        out: list[FetchResult] = []
        for url, _ in pairs:
            if "dev.example" in url:
                out.append(FetchResult([], error="timeout"))
            else:
                out.append(
                    FetchResult(
                        [
                            {
                                "title": "Kernel release",
                                "url": "https://example.com/kernel",
                                "summary": "linux news",
                                "published": "2026-01-01T00:00:00+00:00",
                            }
                        ],
                        last_updated="2026-01-01T00:00:00+00:00",
                    )
                )
        return out

    monkeypatch.setattr("feedpilot.server._all_sources", lambda: fake_sources)
    monkeypatch.setattr("feedpilot.server.fetch_feed", fake_fetch_feed)
    monkeypatch.setattr("feedpilot.server.fetch_many", fake_fetch_many)
    monkeypatch.setattr("feedpilot.server.filter_unseen", lambda items: [i for i in items if "kernel" in i["url"]])

    source_list = list_sources()
    assert source_list[0]["name"] == "Linux"

    one = await headlines("Linux", unseen_only=True)
    assert len(one["items"]) == 1
    assert one["items"][0]["title"] == "Kernel release"
    assert one["cache_age_seconds"] == 2.3
    assert one["last_updated"] == "2026-01-01T00:00:00+00:00"

    multi = await multi_headlines(["Linux", "Dev"], limit=3)
    assert "Linux" in multi
    assert multi["Linux"]["items"][0]["title"] == "Kernel release"
    assert multi["errors"]["Dev"] == "timeout"

    dig = await digest(
        limit_per_source=5,
        tags=["linux"],
        exclude=["dev"],
        overrides={"linux": 2},
        unseen_only=True,
    )
    assert "Linux" in dig
    assert "Dev" not in dig
    assert dig["Linux"]["items"][0]["title"] == "Kernel release"

    search_result = await search("kernel", tags=["linux"], limit_per_source=5)
    assert "Linux" in search_result
    assert search_result["Linux"][0]["title"] == "Kernel release"

    marked = mark_seen(["https://example.com/kernel"])
    assert marked["marked"] == 1
    assert marked["total_provided"] == 1

    add_result = add_source("Community", "https://community.example/feed.xml", ["community"])
    assert add_result["status"] == "added"
    listed_custom = list_custom_sources()
    assert listed_custom[0]["name"] == "Community"
    remove_result = remove_source("Community")
    assert remove_result["status"] == "removed"
    missing_remove = remove_source("Community")
    assert missing_remove["status"] == "not_found"


@pytest.mark.asyncio()
async def test_export_digest_formats_and_validation(isolated_home, monkeypatch) -> None:
    home = isolated_home
    fake_sources = [{"name": "Linux", "url": "https://linux.example/feed", "tags": ["linux"]}]

    async def fake_fetch_many(pairs, **kwargs):
        del pairs, kwargs
        return [
            FetchResult(
                [
                    {
                        "title": "Headline",
                        "url": "https://example.com/article",
                        "summary": "desc",
                        "published": "2026-01-01T00:00:00+00:00",
                    }
                ]
            )
        ]

    monkeypatch.setattr("feedpilot.server._all_sources", lambda: fake_sources)
    monkeypatch.setattr("feedpilot.server.fetch_many", fake_fetch_many)

    md_path = home / "digest.md"
    org_path = home / "digest.org"
    md_res = await export_digest(format="markdown", path=str(md_path), limit_per_source=3)
    org_res = await export_digest(format="org", path=str(org_path), limit_per_source=3)
    bad_res = await export_digest(format="txt", path=str(home / "digest.txt"), limit_per_source=3)

    assert md_res["status"] == "ok"
    assert org_res["status"] == "ok"
    assert bad_res["status"] == "error"
    assert md_path.exists()
    assert org_path.exists()
    assert "Feed Digest" in md_path.read_text(encoding="utf-8")
    assert "Linux" in org_path.read_text(encoding="utf-8")
