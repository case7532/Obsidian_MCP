# obsidian-mcp

MCP server for Obsidian vault — read, write, search, and query notes via the [Model Context Protocol](https://modelcontextprotocol.io/).

## Features

| Category | Tools |
|---|---|
| **Read** | `read_note`, `list_notes`, `search_notes`, `get_note_metadata`, `get_backlinks`, `get_outgoing_links`, `read_canvas` |
| **Write** | `create_note`, `update_note`, `delete_note`, `move_note`, `create_folder`, `delete_folder` |
| **Advanced** | `get_graph_data`, `get_all_tags`, `get_dataview_fields`, `get_daily_note`, `list_attachments` |

## Requirements

- Python ≥ 3.10
- An Obsidian vault (must contain a `.obsidian/` directory)

## Setup

```bash
uv sync
```

## Usage

```bash
# via CLI argument
uv run obsidian-mcp --vault /path/to/vault

# via environment variable
OBSIDIAN_VAULT_PATH=/path/to/vault uv run obsidian-mcp
```

## MCP Client Config

Add to your MCP client configuration (e.g. Kiro CLI, Claude Desktop):

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

## Tool Reference

### Read Tools

**`read_note(path)`**  
Read a note's raw content and parsed frontmatter.

**`list_notes(folder?, tag?)`**  
List notes, optionally filtered by folder path or tag (with or without `#` prefix).

**`search_notes(query, limit=20)`**  
Full-text search across all notes. Returns scored results with ~100-char excerpts. Max 100 results.

**`get_note_metadata(path)`**  
Return frontmatter, tags, file size, and created/modified timestamps.

**`get_backlinks(path)`**  
Find all notes that contain a wiki-link pointing to the given note.

**`get_outgoing_links(path)`**  
List all `[[wiki-links]]` in a note, including resolved vault-relative paths.

**`read_canvas(path)`**  
Parse and return an Obsidian `.canvas` file as structured JSON.

### Write Tools

**`create_note(path?, content, frontmatter?, title?, description?, links?)`**  
Create a note with standard format: frontmatter block, H1 title, description line, body, and a Related section with `[[wikilinks]]`. Path is inferred from content/tags if omitted.

**`update_note(path, content, mode="replace")`**  
Replace or append content. Use `mode="append"` to add to the end of a note.

**`delete_note(path)`**  
Permanently delete a note.

**`move_note(source, destination, update_links=True)`**  
Move or rename a note. When `update_links=True`, all `[[wikilinks]]` across the vault pointing to the source are rewritten to the destination.

**`create_folder(path)`**  
Create a folder and auto-generate an `_index.md` summary document inside it.

**`delete_folder(path, force=False)`**  
Delete a folder. Raises `FolderNotEmptyError` if non-empty unless `force=True`.

### Advanced Tools

**`get_graph_data()`**  
Build the full vault link graph. Returns nodes (notes with title, path, tags) and edges (wiki-link connections).

**`get_all_tags()`**  
List every tag used in the vault with usage count and the paths of all notes using each tag.

**`get_dataview_fields(path)`**  
Parse Dataview inline fields (`key:: value`) from a note and return them as a dict.

**`get_daily_note(date)`**  
Get the daily note for a date (`YYYY-MM-DD`). Reads `.obsidian/daily-notes.json` for custom folder and moment.js format configuration; falls back to common locations (`Daily Notes/`, vault root).

**`list_attachments(folder?)`**  
List all non-markdown files (images, PDFs, audio, etc.) with name, extension, size in bytes, and modified timestamp. Optionally scoped to a subfolder.

## Error Types

| Exception | When raised |
|---|---|
| `VaultError` | Vault path missing, not a directory, or lacks `.obsidian/` |
| `PathTraversalError` | User-supplied path escapes vault boundary |
| `NoteNotFoundError` | Requested note does not exist |
| `NoteExistsError` | Attempted to create an already-existing note |
| `FolderNotEmptyError` | Delete folder called on non-empty folder without `force=True` |

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=obsidian_mcp
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
