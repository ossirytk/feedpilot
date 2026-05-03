---
name: feedpilot
description: Tech news and RSS feed digest. Use this skill when the user wants to catch up on tech news, check a specific feed source, get today's digest, or browse headlines from Phoronix, Hacker News, LWN.net, or GitHub Blog. Invoke for prompts like "what's new in tech", "Linux news", "Hacker News digest", "show me headlines from Phoronix", or "any GitHub updates today".
---

## Overview

feedpilot aggregates RSS/Atom feeds from curated tech sources and exposes them through four MCP tools. No browser required — ask naturally and get the day's signal.

## Default Sources

| Source | Tags |
|--------|------|
| Phoronix | linux, hardware, benchmarks |
| Hacker News | tech, programming |
| LWN.net | linux, kernel |
| GitHub Blog | github, devtools |

## Available Tools

| Tool | When to use |
|------|-------------|
| `list_sources` | List all configured default feed sources with their tags. Use this to orient before fetching. |
| `headlines` | Fetch recent headlines from a specific source. Accepts `source` (source name or raw feed URL) and optional `limit`. |
| `multi_headlines` | Fetch headlines from several named sources in parallel. Accepts `sources` (list of names or URLs) and optional `limit`. |
| `digest` | Fetch headlines from all sources in one call. Accepts optional `limit_per_source`, `tags` list for filtering, `exclude` for skipping sources, and `overrides` for per-source limits. |

## Guidance

- For a general "what's new" request: call `digest` with no filters.
- For topic-specific requests (e.g. "Linux news only"): pass `tags: ["linux"]` or `tags: ["linux", "kernel"]` to `digest`.
- For a single source: call `headlines` with the source name (e.g. `"Phoronix"` or `"Hacker News"`).
- For multiple specific sources: call `multi_headlines` with a list of source names.
- Default `limit_per_source` is 5; increase to 10–15 if the user wants more depth.
- After fetching, summarize the headlines and highlight anything the user is likely to find interesting based on the conversation context.
