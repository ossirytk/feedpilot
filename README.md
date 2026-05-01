# feedpilot

A daily tech digest MCP server for use with GitHub Copilot CLI and GitHub Copilot in VS Code.

Aggregates RSS/Atom feeds from sources you care about — Linux hardware news, kernel updates, Hacker News, GitHub announcements — and lets you discuss, summarize, and drill into the day's signal with Copilot. No browser required.

---

## Quick Start

### Prerequisites

- Python 3.12 or higher
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Option A — Install with `uv tool` (Recommended)

Install feedpilot directly from GitHub. No clone needed:

```powershell
uv tool install git+https://github.com/ossirytk/feedpilot
```

This installs a `feedpilot` command globally. Find where `uv` placed it if you need the full path for MCP config:

```powershell
uv tool dir --bin
```

Then jump to [MCP client configuration](#mcp-client-configuration) below.

### Option B — Clone and run with `uv`

```powershell
git clone https://github.com/ossirytk/feedpilot
cd feedpilot
uv sync
```

Then jump to [MCP client configuration](#mcp-client-configuration) below.

---

## MCP Client Configuration

feedpilot runs as an MCP server over stdio. Configure your MCP client once, then ask Copilot naturally.

### GitHub Copilot CLI

Add feedpilot to `~/.copilot/mcp-config.json` (create it if it doesn't exist).

**If you used `uv tool install` (Option A):**

```json
{
  "mcpServers": {
    "feedpilot": {
      "type": "stdio",
      "command": "feedpilot"
    }
  }
}
```

> **Note:** If the Copilot CLI process doesn't inherit your PATH, use the full path returned by `uv tool dir --bin`. On Windows: `"C:\\Users\\<YourUsername>\\.local\\bin\\feedpilot.exe"`.

**If you cloned the repo (Option B):**

*Windows:*
```json
{
  "mcpServers": {
    "feedpilot": {
      "command": "C:\\Users\\<YourUsername>\\.local\\bin\\uv.exe",
      "args": ["run", "feedpilot"],
      "cwd": "D:\\feedpilot"
    }
  }
}
```

*macOS / Linux:*
```json
{
  "mcpServers": {
    "feedpilot": {
      "command": "/home/<youruser>/.local/bin/uv",
      "args": ["run", "feedpilot"],
      "cwd": "/path/to/feedpilot"
    }
  }
}
```

> **Tip:** Find the full path to `uv` with `(Get-Command uv).Source` (PowerShell) or `which uv` (bash/fish).

Restart the Copilot CLI, then run `/mcp` to confirm `feedpilot` appears and its tools are listed.

### VS Code Copilot

For detailed VS Code setup including workspace-scoped config and troubleshooting, see [MCP-SETUP.md](MCP-SETUP.md).

**Quick config** — create or edit `%APPDATA%\Code\User\mcp.json` (Windows), `~/Library/Application Support/Code/User/mcp.json` (macOS), or `~/.config/Code/User/mcp.json` (Linux):

*With `uv tool install` (Option A):*
```json
{
  "servers": {
    "feedpilot": {
      "type": "stdio",
      "command": "feedpilot"
    }
  }
}
```

*With cloned repo (Option B):*
```json
{
  "servers": {
    "feedpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "feedpilot"],
      "cwd": "/path/to/feedpilot"
    }
  }
}
```

Run `MCP: List Servers` from the VS Code Command Palette to confirm `feedpilot` is listed and enabled.

---

## Usage

Once configured, ask Copilot naturally:

> *"What's new on Phoronix today?"*  
> *"Give me the Linux digest — kernel and hardware only"*  
> *"Any interesting stuff on Hacker News right now?"*  
> *"List all feed sources"*

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
| `multi_headlines` | Fetch headlines from multiple sources in parallel |
| `list_sources` | List all configured default feed sources with their tags |

---

## Updating

**Option A (`uv tool install`):**

```powershell
uv tool upgrade feedpilot
```

**Option B (cloned repo):**

```powershell
git pull
uv sync
```

---

## Development

```powershell
git clone https://github.com/ossirytk/feedpilot
cd feedpilot
uv sync

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .

# Run tests
uv run pytest
```

---

## License

[MIT](LICENSE)
