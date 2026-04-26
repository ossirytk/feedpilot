# Feedpilot — Improvement Ideas

## Fixes (P0)

- **No response caching** — every `digest` or `headlines` call hits live RSS feeds with no local cache. This hammers sources, adds latency, and makes the tool unusable for rapid follow-up queries. Add an in-memory or on-disk TTL cache (15–30 min default, configurable via `FEEDPILOT_CACHE_TTL`).
- **Error visibility** — when one source fails, the error is embedded inside the response dict but easy to miss. Add a top-level `errors` block in all multi-source responses listing failed sources with their error messages.

## Enhancements (P1)

- **Keyword/topic search across fetched headlines** — add a `search` tool that fetches all sources then filters titles/summaries by keyword or regex. Avoids the user needing to call `digest` then manually scan.
- **Read/seen tracking** — persist a local SQLite store (like captainslog) that records which article URLs have been surfaced. Add a `mark_seen` tool and a `unseen_only` filter on `digest`/`headlines`.
- **Persistent user-configurable sources** — `headlines` accepts raw URLs but there's no way to save a custom source into the default list. Add `add_source` / `remove_source` tools backed by a local config file (`~/.feedpilot/sources.json`).
- **Expand default sources** — consider adding: The Changelog, lobste.rs, Ars Technica (tech), Reddit r/programming, or LKML for a broader default signal.

## Enhancements (P2)

- **Export formats** — add `export_digest` tool that writes a Markdown or Org-mode digest file to disk (daily digest log).
- **Article summary fetch** — optionally follow the article URL and return the first N characters of body text as a preview, so users can triage without opening a browser.
- **Per-source freshness reporting** — include `last_updated` timestamp from the feed alongside headlines so stale feeds are obvious.
