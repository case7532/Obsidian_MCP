# Units of Work — Obsidian MCP Server

> Phân rã dự án thành 4 units: Foundation, Read Operations, Write Operations, Advanced.

## Contents
- [Deployment Model](#deployment-model)
- [Unit Definitions](#unit-definitions)
- [Execution Order](#execution-order)

## Deployment Model

**Single Python package** (`obsidian-mcp`) — monolith với logical units. Tất cả units nằm trong cùng một repo, deploy cùng nhau như một MCP server process.

## Unit Definitions

---

### Unit 1: Foundation (vault_config + path_utils + models + exceptions)

**Files**:
- `src/obsidian_mcp/vault_config.py`
- `src/obsidian_mcp/path_utils.py`
- `src/obsidian_mcp/models.py`
- `src/obsidian_mcp/exceptions.py`
- `tests/unit/test_path_utils.py`
- `tests/unit/test_vault_config.py`

**Responsibilities**:
- Vault path validation và configuration
- Security boundary (path traversal prevention)
- Shared data models (NoteContent, NoteInfo, WikiLink, ...)
- Custom exception hierarchy

**Why first**: Tất cả units khác đều phụ thuộc vào Foundation. Phải build và test Foundation trước.

**PBT coverage**: Path round-trip, path traversal invariant (critical security tests)

---

### Unit 2: Read Operations (note_reader + read_tools)

**Files**:
- `src/obsidian_mcp/note_reader.py`
- `src/obsidian_mcp/tools/read_tools.py`
- `tests/unit/test_note_reader.py`
- `tests/integration/test_read_tools.py`

**Responsibilities**:
- Đọc note content, parse frontmatter YAML
- List/search notes
- Extract wiki-links, tags, backlinks
- Read canvas files
- MCP tool handlers: `read_note`, `list_notes`, `search_notes`, `get_note_metadata`, `get_backlinks`, `get_outgoing_links`, `read_canvas`

**Depends on**: Unit 1 (Foundation)

**PBT coverage**: Frontmatter round-trip, wiki-link parse round-trip, list+filter invariant

---

### Unit 3: Write Operations (note_writer + write_tools)

**Files**:
- `src/obsidian_mcp/note_writer.py`
- `src/obsidian_mcp/tools/write_tools.py`
- `tests/unit/test_note_writer.py`
- `tests/integration/test_write_tools.py`

**Responsibilities**:
- Create, update, delete notes
- Move/rename notes (atomic + backlink update)
- Folder operations (create, delete)
- MCP tool handlers: `create_note`, `update_note`, `delete_note`, `move_note`, `create_folder`, `delete_folder`

**Depends on**: Unit 1 (Foundation), Unit 2 (NoteReader — cho backlink scanning khi move)

**PBT coverage**: Create→read→delete round-trip, move idempotency

---

### Unit 4: Advanced Features + Server Wiring

**Files**:
- `src/obsidian_mcp/advanced_features.py`
- `src/obsidian_mcp/tools/advanced_tools.py`
- `src/obsidian_mcp/tools/__init__.py`
- `src/obsidian_mcp/__init__.py`
- `src/obsidian_mcp/server.py`
- `tests/unit/test_advanced_features.py`
- `tests/integration/test_advanced_tools.py`
- `pyproject.toml`
- `README.md`

**Responsibilities**:
- Graph data generation (nodes + edges)
- Tag aggregation
- Dataview inline field parsing
- Daily note resolution
- Attachment listing
- FastMCP server wiring (register all tools, stdio transport, vault_path init)
- Packaging (pyproject.toml, entry point)
- MCP tool handlers: `get_graph_data`, `get_all_tags`, `get_dataview_fields`, `get_daily_note`, `list_attachments`

**Depends on**: Unit 1, Unit 2, Unit 3

**PBT coverage**: Dataview field parse round-trip, tag extraction invariant

---

## Execution Order

```
Unit 1 (Foundation)
    |
    v
Unit 2 (Read) ----+
    |              |
    v              v
Unit 3 (Write) ---+
    |              |
    v              v
Unit 4 (Advanced + Server)
```

Unit 2 và Unit 3 có thể được implement gần như song song (Unit 3 chỉ cần NoteReader cho `move_note`), nhưng Unit 2 phải hoàn thành trước khi Unit 3 có thể test đầy đủ.

## Related
- [[execution-plan]]
- [[unit-of-work-dependency]]
- [[unit-of-work-story-map]]
