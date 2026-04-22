# MCP Server Setup

This guide explains how to configure feedpilot as an MCP server for use with GitHub Copilot CLI and VS Code.

## Prerequisites

- VS Code with GitHub Copilot Chat extension
- Python 3.12+
- `uv` package manager

## Configuration Steps

### 1. GitHub Copilot CLI

Create `~/.copilot/mcp-config.json` (or add to it if it already exists):

**On Windows:**
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

> **Note:** Use the full path to `uv.exe` — the Copilot CLI process may not inherit your user `PATH`. Find yours with `(Get-Command uv).Source` in PowerShell.

**On macOS/Linux:**
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

Restart the Copilot CLI after saving. Run `/mcp` to confirm feedpilot appears.

### 2. VS Code User MCP Config

Create `%APPDATA%\Code\User\mcp.json` on Windows (or `~/.config/Code/User/mcp.json` on macOS/Linux):

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

> **Note:** Use the full path to `uv.exe` — VS Code may not inherit your user `PATH`.

### 3. VS Code Workspace MCP Config

Alternatively, use a workspace-scoped config. Create or edit `.vscode/mcp.json` in this repo:

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

1. Run `MCP: List Servers` from the Command Palette and confirm `feedpilot` is listed and enabled.
2. If prompted, trust the server so VS Code can start it and discover tools.

### 4. Verify Installation

Run the server manually to confirm it works:

```powershell
cd D:\feedpilot
uv run feedpilot
```

You should see the server initialize without errors. Press `Ctrl+C` to stop it.

## Using feedpilot in Copilot Chat

Once configured, you can ask Copilot questions like:

- *"What's new on Phoronix today?"*
- *"Give me the Linux digest — kernel and hardware only"*
- *"Any interesting stuff on Hacker News right now?"*
- *"List all feed sources"*

Copilot will automatically invoke the feedpilot tools to fetch and summarize the latest news.

## Troubleshooting

### Server not connecting

- Verify `uv` is installed and accessible: `uv --version`
- Check the configured path matches your feedpilot location
- Confirm you've run `uv sync` to install dependencies

### No tools available in Copilot CLI

- Confirm `~/.copilot/mcp-config.json` exists and is valid JSON
- Run `/mcp` in the CLI and check feedpilot is listed
- Restart the CLI after making config changes

### No tools available in VS Code

- Confirm the server exists in `.vscode/mcp.json` (or user `mcp.json`)
- Run `MCP: List Servers` and ensure `feedpilot` is enabled
- If needed, run `MCP: Reset Trust`, then restart and trust `feedpilot` again
- Check the MCP server logs via `MCP: List Servers` -> `Show Output`

### Command not found errors

- Ensure you're using the full path to `uv` or that it's in your PATH
- On Windows, when editing a `.json` file, escape backslashes with `\\` (for example, `C:\\Users\\<YourUsername>\\.local\\bin\\uv.exe`); only use PowerShell backticks if you're embedding JSON inside a PowerShell string

---

For more about MCP servers, see the [MCP documentation](https://modelcontextprotocol.io/).
