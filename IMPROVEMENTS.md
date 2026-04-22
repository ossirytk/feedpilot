# IMPROVEMENTS

Future work backlog for Feedpilot, focused on making the MCP tool feel complete and production-ready.

## Priorities

- P0: Required for reliable day-to-day use
- P1: High-value quality and UX improvements
- P2: Nice-to-have enhancements

## P0 - Core Functional Completeness

### 1) MCP discovery and startup diagnostics
Status: not started

Problem:
- Users can enable the server but still not know why tools do not appear.

Proposed work:
- Add a startup self-check command/tool that reports:
  - resolved Python executable
  - resolved working directory
  - Feedpilot version
  - dependency import status
  - network reachability summary
- Return structured diagnostics in JSON for easy rendering in clients.

Acceptance criteria:
- A single MCP call can confirm server readiness without reading logs.
- Typical misconfigurations (bad cwd, missing deps, PATH mismatch) are reported clearly.

### 2) Robust filtering behavior
Status: not started

Problem:
- Tag filtering can produce confusing empty results depending on source tagging.

Proposed work:
- Normalize tags at ingest time and expose supported tags via a dedicated endpoint/tool.
- Add optional fallback mode:
  - strict tag match
  - relaxed keyword match across title/summary/source
- Include metadata in results: requested filters, effective filters, dropped sources.

Acceptance criteria:
- Filtered requests explain why items were or were not returned.
- Users can discover valid filter terms programmatically.

### 3) Error visibility per source
Status: not started

Problem:
- Partial failures (one feed down, others OK) are not obvious to end users.

Proposed work:
- Return per-source status block with:
  - success/failure
  - latency
  - HTTP/status error message (sanitized)
  - item count
- Keep successful source items even when some sources fail.

Acceptance criteria:
- Digest responses always include source-level status.
- Users can tell partial failure from empty-news scenarios.

## P1 - Reliability, Performance, and Data Quality

### 4) Keyword/topic filtering across fetched headlines
Status: not started

Problem:
- Tag filtering selects which *sources* to include but cannot filter individual *headlines* by topic.
- Users asking "anything about ransomware?" must receive all items and scan manually.

Proposed work:
- Add a `search(query: str, tags: list[str] | None, limit_per_source: int)` tool that:
  - fetches all sources (optionally pre-filtered by tag)
  - filters returned items by matching `query` against title and summary (case-insensitive substring or simple tokenised match)
  - returns only matching items, grouped by source
- Consider exposing the same filter as a `query` parameter on `digest` for inline use.

Acceptance criteria:
- Single MCP call returns cross-source results filtered by keyword.
- Empty-match is handled gracefully (returns empty dict, not an error).
- No additional dependencies required (pure Python string matching).

### 5) Local caching with TTL
Status: not started

Problem:
- Repeated requests can be slow and produce inconsistent snapshots.

Proposed work:
- Cache feed responses with source-level TTL.
- Add force-refresh option.
- Expose cache age in response metadata.

Acceptance criteria:
- Back-to-back calls are fast and deterministic within TTL.
- Users can bypass cache when needed.

### 6) Read/seen tracking
Status: not started

Problem:
- Digests repeatedly surface the same entries.

Proposed work:
- Persist seen item IDs/hashes locally.
- Add options to include only unseen, seen, or all items.
- Add mark-as-read behavior for returned items.

Acceptance criteria:
- Daily usage can focus on new items only.
- State survives restarts.

### 7) Better source control and persistence
Status: not started

Problem:
- User-added sources and source preferences are not fully managed.

Proposed work:
- Persist custom sources in local config (JSON/TOML).
- Validate source URLs and categories on add/update.
- Add enable/disable per source without deleting.

Acceptance criteria:
- Source list survives restarts.
- Invalid source configs are rejected with helpful error messages.

## P2 - Usability and Ecosystem

### 8) Output formats (Markdown and Org-mode)
Status: not started

Problem:
- Users may want digest output saved in reusable formats.

Proposed work:
- Add export options:
  - markdown file
  - org-mode file
- Include date-based file naming and source tags.

Acceptance criteria:
- Digest can be exported directly for personal workflows.

### 9) Optional advanced CLI integrations
Status: not started

Problem:
- Power users may want richer local workflows.

Proposed work:
- Optional integrations (graceful fallback if absent):
  - jq for structured filtering
  - rg for archive search
  - fzf for interactive selection (only when explicitly requested)

Acceptance criteria:
- Tool works fully without extras.
- When extras exist, enhanced workflows are available.

## Engineering Quality Work

### 10) Test coverage expansion
Status: not started

Proposed work:
- Add tests for:
  - filtering modes
  - partial source failures
  - caching behavior
  - seen-item tracking
  - config validation

Acceptance criteria:
- New behavior is covered by unit tests.
- Regression risk is reduced for feed parsing and MCP responses.

### 11) CI quality gates
Status: not started

Proposed work:
- Ensure CI runs:
  - uv sync
  - ruff format --check
  - ruff check
  - test suite
- Add lightweight smoke test that starts the MCP server and verifies tool list.

Acceptance criteria:
- Broken formatting/lint/tests fail CI.
- MCP startup regressions are caught early.

## Suggested Implementation Order

1. MCP diagnostics and source-level error reporting
2. Filter normalization and discoverability
3. Keyword/topic search across fetched headlines
4. Caching and seen-item tracking
5. Source persistence improvements
6. Export formats and optional integrations

## Notes

- Keep diffs minimal and terminal-reproducible.
- Use uv and ruff as the authoritative project tooling.
- Preserve cross-editor workflow compatibility (VS Code and Neovim).
