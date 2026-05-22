# Build Instructions

> Hướng dẫn cài đặt, build và chạy MCP server với uv và pyproject.toml.

## Contents
- [Prerequisites](#prerequisites)
- [Build Steps](#build-steps)
- [Run server locally](#run-server-locally)
- [Kiro CLI / Claude Desktop config](#kiro-cli--claude-desktop-config)
- [Troubleshooting](#troubleshooting)

## Prerequisites
- Python 3.10+
- `uv` package manager (`brew install uv` on macOS)

## Build Steps

### 1. Install dependencies
```bash
cd /path/to/obsidian-mcp
uv sync
```

### 2. Verify installation
```bash
uv run obsidian-mcp --help
```

**Expected output**: argument parser help with `--vault` option.

### 3. Build artifacts
- `.venv/` — virtual environment with all pinned dependencies
- `uv.lock` — reproducible lock file (commit to version control)

## Run server locally
```bash
# Via CLI arg
uv run obsidian-mcp --vault /path/to/your/vault

# Via env var
OBSIDIAN_VAULT_PATH=/path/to/your/vault uv run obsidian-mcp
```

## Kiro CLI / Claude Desktop config
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/obsidian-mcp", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/vault"
      }
    }
  }
}
```

## Troubleshooting

**`VaultError: .obsidian directory not found`** — Path does not point to a valid Obsidian vault. Open the vault in Obsidian at least once to create the `.obsidian/` directory.

**`uv: command not found`** — Install uv: `brew install uv` (macOS) or `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux).

## Related
- [[unit-test-instructions]]
- [[build-and-test-summary]]
