# Code Structure

## Build System
- **Type**: uv (Python package manager) + hatchling (build backend)
- **Configuration**: `pyproject.toml`
- **Entry point**: `obsidian-mcp = "obsidian_mcp.server:main"`
- **Python**: >= 3.10

## Source Files Inventory

```
src/obsidian_mcp/
  __init__.py               -- Package marker
  server.py                 -- MCP server entry point, CLI argument parsing, component wiring
  vault_config.py           -- VaultConfig class: vault path validation + env/CLI config
  models.py                 -- Data models: NoteContent, NoteInfo, NoteMetadata, WikiLink,
                               SearchResult, GraphData, TagInfo, AttachmentInfo
  exceptions.py             -- Exception hierarchy: ObsidianMCPError, VaultError,
                               PathTraversalError, NoteNotFoundError, NoteExistsError,
                               FolderNotEmptyError
  path_utils.py             -- Security boundary: safe_vault_path, sanitize_filename,
                               normalize_note_path, to_vault_relative, is_markdown, is_canvas
  note_reader.py            -- NoteReader: read_note, list_notes, search_notes, bm25_search,
                               get_metadata, get_backlinks, get_outgoing_links, read_canvas;
                               helpers: _parse_frontmatter, _extract_tags, _parse_wikilinks,
                               _resolve_wikilink
  note_writer.py            -- NoteWriter: create_note, update_note, delete_note, move_note,
                               create_folder, delete_folder; helpers: _build_document_template,
                               _infer_folder, _update_folder_index, _update_backlinks,
                               _create_folder_index
  advanced_features.py      -- AdvancedFeatures: get_graph_data, get_all_tags,
                               get_dataview_fields, get_daily_note, list_attachments;
                               helpers: _moment_to_filename, _mtime_iso
  tools/
    __init__.py             -- Package marker
    read_tools.py           -- register_read_tools: MCP tool adapters for all NoteReader ops
                               (+ bm25_search tool - dev branch)
    write_tools.py          -- register_write_tools: MCP tool adapters for all NoteWriter ops
    advanced_tools.py       -- register_advanced_tools: MCP tool adapters for AdvancedFeatures

tests/
  __init__.py
  unit/
    test_vault_config.py    -- VaultConfig: from_env_or_arg, validate, error cases
    test_path_utils.py      -- path_utils: traversal prevention, sanitize, normalize (+ Hypothesis)
    test_note_reader.py     -- NoteReader: all read ops, frontmatter/tag/wikilink parsing (+ Hypothesis)
    test_note_writer.py     -- NoteWriter: all write ops, folder index, backlink update
    test_advanced_features.py -- AdvancedFeatures: graph, tags, dataview, daily note, attachments
```

## Key Classes / Module Hierarchy

```
ObsidianMCPError (exceptions)
  +-- VaultError
  +-- PathTraversalError
  +-- NoteNotFoundError
  +-- NoteExistsError
  +-- FolderNotEmptyError

VaultConfig
  + from_env_or_arg(vault_path?) -> VaultConfig
  + validate()
  + resolve_path(relative) -> Path
  + to_relative(absolute) -> str

NoteReader(config: VaultConfig)
  + read_note(path) -> NoteContent
  + list_notes(folder?, tag?) -> list[NoteInfo]
  + search_notes(query, limit) -> list[SearchResult]
  + bm25_search(query, limit) -> list[dict]       [dev branch]
  + get_metadata(path) -> NoteMetadata
  + get_backlinks(path) -> list[str]
  + get_outgoing_links(path) -> list[WikiLink]
  + read_canvas(path) -> dict

NoteWriter(config: VaultConfig, reader: NoteReader)
  + create_note(path?, content, fm?, title?, desc?, links?) -> NoteInfo
  + update_note(path, content, mode) -> NoteInfo
  + delete_note(path) -> None
  + move_note(source, dest, update_links) -> NoteInfo
  + create_folder(path) -> None
  + delete_folder(path, force) -> None
  - _update_folder_index(folder_abs)    [smart: only adds missing entries]
  - _update_backlinks(old_stem, new_stem)
  - _create_folder_index(folder_abs, name)

AdvancedFeatures(config: VaultConfig, reader: NoteReader)
  + get_graph_data() -> GraphData
  + get_all_tags() -> list[TagInfo]
  + get_dataview_fields(path) -> dict
  + get_daily_note(date) -> dict | None
  + list_attachments(folder?) -> list[AttachmentInfo]
```

## Design Patterns

### Adapter Pattern — Tools Layer
- **Location**: `tools/read_tools.py`, `tools/write_tools.py`, `tools/advanced_tools.py`
- **Purpose**: Tách domain logic khỏi MCP protocol; tools là thin adapters gọi domain services
- **Implementation**: `register_*_tools(mcp, service)` functions dùng `@mcp.tool()` decorator

### Security Boundary (Gateway Pattern)
- **Location**: `path_utils.safe_vault_path()`
- **Purpose**: Tất cả user-supplied paths phải qua một điểm kiểm tra duy nhất
- **Implementation**: Resolve path → check `is_relative_to(vault_path)` → raise `PathTraversalError` nếu vi phạm

### Template Method — Document Format
- **Location**: `note_writer._build_document_template()`
- **Purpose**: Chuẩn hóa format ghi chú: H1 title, description blockquote, Contents index (từ H2), body, Related links

### Strategy — Path Inference
- **Location**: `note_writer._infer_folder()`
- **Purpose**: Khi không có path, chọn folder phù hợp nhất bằng keyword scoring

## Critical Dependencies

| Dependency | Version | Usage |
|---|---|---|
| `mcp` | >=1.0.0 | FastMCP server, stdio transport, `@mcp.tool()` decorator |
| `PyYAML` | >=6.0.1 | Parse frontmatter YAML, serialize frontmatter |
| `pytest` | >=8.0.0 | Test framework |
| `pytest-cov` | >=5.0.0 | Coverage reporting |
| `hypothesis` | >=6.100.0 | Property-based testing cho path/tag edge cases |
