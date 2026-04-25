# MCP Server Setup

This guide explains how to configure feedpilot as an MCP server for use with GitHub Copilot CLI and VS Code.

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager
- VS Code with GitHub Copilot extension (for VS Code setup)

## Installation

Choose one of two installation methods:

### Option A — `uv tool install` (Recommended)

Installs feedpilot as a standalone tool — no clone or `cwd` needed in your MCP config:

```powershell
uv tool install git+https://github.com/ossirytk/feedpilot
```

Find where `uv` placed the binary (needed if your MCP client doesn't inherit PATH):

```powershell
uv tool dir --bin
```

To upgrade later:

```powershell
uv tool upgrade feedpilot
```

### Option B — Clone and run with `uv`

Use this if you want to modify or inspect the source:

```powershell
git clone https://github.com/ossirytk/feedpilot
cd feedpilot
uv sync
```

---

## Configuration Steps

### 1. GitHub Copilot CLI

Create `~/.copilot/mcp-config.json` (or add `feedpilot` to it if the file already exists).

**Option A — `uv tool install`:**

```json
{
  "mcpServers": {
    "feedpilot": {
      "command": "feedpilot"
    }
  }
}
```

> If the CLI doesn't inherit your PATH, use the full binary path from `uv tool dir --bin`:
> - Windows: `"C:\\Users\\<YourUsername>\\.local\\bin\\feedpilot.exe"`
> - macOS/Linux: `"/home/<youruser>/.local/bin/feedpilot"`

**Option B — cloned repo, Windows:**

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

> Find the full path to `uv.exe` with `(Get-Command uv).Source` in PowerShell.

**Option B — cloned repo, macOS/Linux:**

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

> Find the full path to `uv` with `which uv`.

Restart the Copilot CLI after saving. Run `/mcp` to confirm `feedpilot` appears and its tools are listed.

---

### 2. VS Code — User MCP Config

This config applies across all your VS Code workspaces.

Create (or edit) the user MCP config file:
- **Windows:** `%APPDATA%\Code\User\mcp.json`
- **macOS/Linux:** `~/.config/Code/User/mcp.json`

**Option A — `uv tool install`:**

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

> Use the full binary path if VS Code doesn't pick up your PATH (see note in section 1 above).

**Option B — cloned repo, Windows:**

```json
{
  "servers": {
    "feedpilot": {
      "type": "stdio",
      "command": "C:\\Users\\<YourUsername>\\.local\\bin\\uv.exe",
      "args": ["run", "feedpilot"],
      "cwd": "D:\\feedpilot"
    }
  }
}
```

**Option B — cloned repo, macOS/Linux:**

```json
{
  "servers": {
    "feedpilot": {
      "type": "stdio",
      "command": "/home/<youruser>/.local/bin/uv",
      "args": ["run", "feedpilot"],
      "cwd": "/path/to/feedpilot"
    }
  }
}
```

---

### 3. VS Code — Workspace MCP Config

Useful for keeping feedpilot scoped to a specific project, or if you cloned this repo and want to use `${workspaceFolder}`. Create or edit `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "feedpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "feedpilot"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

> This uses `uv run` so `uv` must be in the PATH that VS Code inherits. If not, replace `"uv"` with its full path.

Run `MCP: List Servers` from the Command Palette and confirm `feedpilot` is listed. If prompted, trust the server so VS Code can start it and discover its tools.

---

### 4. Verify Installation

Run the server manually to confirm it starts without errors:

**Option A:**
```powershell
feedpilot
```

**Option B:**
```powershell
cd /path/to/feedpilot
uv run feedpilot
```

You should see the server initialize. Press `Ctrl+C` to stop it.

---

## Using feedpilot in Copilot Chat

Once configured, ask Copilot naturally:

- *"What's new on Phoronix today?"*
- *"Give me the Linux digest — kernel and hardware only"*
- *"Any interesting stuff on Hacker News right now?"*
- *"List all feed sources"*

Copilot will automatically invoke the feedpilot tools to fetch and summarize the latest news.

---

## Troubleshooting

### Server not connecting

- Verify `uv` is installed: `uv --version`
- **Option A:** confirm `feedpilot` is on PATH (`feedpilot --version`) or use full path
- **Option B:** confirm you've run `uv sync` and the `cwd` path is correct

### No tools available in Copilot CLI

- Confirm `~/.copilot/mcp-config.json` is valid JSON
- Run `/mcp` in the CLI and check `feedpilot` is listed
- Restart the CLI after making config changes

### No tools available in VS Code

- Confirm the server entry exists in `mcp.json` (user or workspace scope)
- Run `MCP: List Servers` and ensure `feedpilot` is enabled
- If needed, run `MCP: Reset Trust`, then restart and trust `feedpilot` again
- Check logs via `MCP: List Servers` → `Show Output`

### Command not found / path errors

- In JSON config files, escape Windows backslashes with `\\` (e.g. `C:\\Users\\...`)
- Use `uv tool dir --bin` to locate the feedpilot binary installed by `uv tool install`
- Use `(Get-Command uv).Source` (PowerShell) or `which uv` (bash/fish) to find the `uv` binary

---

For more about MCP servers, see the [MCP documentation](https://modelcontextprotocol.io/).
