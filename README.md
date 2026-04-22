# feedpilot

A daily tech digest MCP server for use with GitHub Copilot CLI.

Aggregates RSS/Atom feeds from sources you care about — Linux hardware news, kernel updates, Hacker News, GitHub announcements — and lets you discuss, summarize, and drill into the day's signal with Copilot. No browser required.

---

## Default Sources

| Source | Tags |
|--------|------|
| [Phoronix](https://www.phoronix.com) | linux, hardware, benchmarks |
| [Hacker News](https://news.ycombinator.com) | tech, programming |
| [LWN.net](https://lwn.net) | linux, kernel |
| [GitHub Blog](https://github.blog) | github, devtools |

---

## Tools

| Tool | Description |
|------|-------------|
| `digest` | Fetch headlines from all sources; optionally filter by tags |
| `headlines` | Fetch recent items from a specific source by name or raw URL |
| `list_sources` | List all configured default feed sources with their tags |

---

## Usage

Run as an MCP server (stdio transport, for use with Copilot CLI or any MCP client):

```powershell
uv run feedpilot
```

Register it in your MCP client config and then ask naturally:

> *"What's new on Phoronix today?"*  
> *"Give me the Linux digest — kernel and hardware only"*  
> *"Any interesting stuff on Hacker News right now?"*

---

## Installation

```powershell
uv sync
uv run feedpilot
```

---

## VS Code Integration

To use feedpilot with GitHub Copilot in VS Code, see [MCP-SETUP.md](MCP-SETUP.md) for configuration instructions.

Quick summary:
1. Copy the MCP server config into your VS Code / GitHub Copilot MCP settings as described in [MCP-SETUP.md](MCP-SETUP.md)
2. Update the `cwd` path to match your feedpilot installation
3. Restart VS Code and ask Copilot about the latest news

---

## Development

```powershell
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run checks and fix auto-fixable issues
uv run ruff check --fix .
```
