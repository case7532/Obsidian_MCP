# System Architecture

## System Overview

obsidian-mcp là một **stdio MCP server** chạy local, nhận lệnh từ AI client (Claude Desktop, Kiro CLI, v.v.) qua stdin/stdout theo MCP protocol. Không có network exposure — toàn bộ giao tiếp qua process stdio.

## Architecture Diagram

```
+---------------------------+        stdio (MCP protocol)        +-----------------------------+
|    AI Client              |<---------------------------------->|   obsidian-mcp Server        |
|  (Claude/Kiro/etc.)       |                                    |   (FastMCP / Python)         |
+---------------------------+                                    +-----------------------------+
                                                                  |
                                    +-----------------------------+-----------------------------+
                                    |                             |                             |
                             +------+------+             +--------+------+            +---------+------+
                             | read_tools  |             | write_tools   |            | advanced_tools |
                             +------+------+             +--------+------+            +---------+------+
                                    |                             |                             |
                             +------+------+             +--------+------+            +---------+------+
                             | NoteReader  |             | NoteWriter    |            | AdvancedFeatures|
                             +------+------+             +--------+------+            +---------+------+
                                    |                             |                             |
                                    +-----------------------------+-----------------------------+
                                                                  |
                                                         +--------+--------+
                                                         |   VaultConfig   |
                                                         +--------+--------+
                                                                  |
                                                         +--------+--------+
                                                         |   path_utils    |  <-- security boundary
                                                         +--------+--------+
                                                                  |
                                                         +--------+--------+
                                                         | Obsidian Vault  |
                                                         | (filesystem)    |
                                                         +-----------------+
```

## Component Descriptions

### obsidian_mcp.server
- **Purpose**: MCP server entry point
- **Responsibilities**: Parse CLI args, init VaultConfig, instantiate Reader/Writer/Advanced, register tools, run MCP stdio transport
- **Dependencies**: FastMCP, VaultConfig, NoteReader, NoteWriter, AdvancedFeatures
- **Type**: Application entry point

### obsidian_mcp.note_reader
- **Purpose**: Tất cả read operations trên vault
- **Responsibilities**: read_note, list_notes, search_notes (FTS), bm25_search, get_metadata, get_backlinks, get_outgoing_links, read_canvas; parse frontmatter/tags/wikilinks
- **Dependencies**: VaultConfig, path_utils, models, exceptions
- **Type**: Domain service

### obsidian_mcp.note_writer
- **Purpose**: Tất cả write/mutation operations trên vault
- **Responsibilities**: create_note (với smart folder index update), update_note, delete_note, move_note (với backlink update), create_folder, delete_folder
- **Dependencies**: VaultConfig, NoteReader, path_utils, models, exceptions
- **Type**: Domain service

### obsidian_mcp.advanced_features
- **Purpose**: Tính năng vault-level nâng cao
- **Responsibilities**: get_graph_data, get_all_tags, get_dataview_fields, get_daily_note, list_attachments
- **Dependencies**: VaultConfig, NoteReader, path_utils, models
- **Type**: Domain service

### obsidian_mcp.vault_config
- **Purpose**: Vault path validation và configuration
- **Responsibilities**: Validate vault có `.obsidian/`, load từ CLI arg hoặc env var, resolve/convert paths
- **Dependencies**: exceptions
- **Type**: Infrastructure / Configuration

### obsidian_mcp.path_utils
- **Purpose**: Security boundary — tất cả path từ user phải qua đây
- **Responsibilities**: safe_vault_path (traversal prevention), normalize_note_path, sanitize_filename, is_markdown, is_canvas, to_vault_relative
- **Dependencies**: exceptions (PathTraversalError)
- **Type**: Security / Infrastructure

### obsidian_mcp.models
- **Purpose**: Data models / DTOs
- **Responsibilities**: NoteContent, NoteInfo, NoteMetadata, WikiLink, SearchResult, GraphData, TagInfo, AttachmentInfo
- **Dependencies**: None (pure data classes)
- **Type**: Model / DTO

### obsidian_mcp.exceptions
- **Purpose**: Exception hierarchy
- **Type**: Infrastructure

### tools/read_tools, write_tools, advanced_tools
- **Purpose**: Thin MCP adapter layer — đăng ký Python functions như MCP tools
- **Responsibilities**: Wrap domain service calls, convert dataclass → dict, expose docstrings làm tool descriptions
- **Type**: Adapter / Interface

## Data Flow — Create Note with Folder Index Update

```
AI Client
  --> create_note(path, content, ...)
    --> NoteWriter.create_note()
      --> path_utils.safe_vault_path()  [security check]
      --> _build_document_template()    [format content]
      --> abs_path.write_text()         [write file]
      --> _update_folder_index()        [check _index.md for missing links]
        --> read _index.md
        --> find wikilinks already present
        --> append only missing note entries
        --> write updated _index.md
      --> return NoteInfo
```

## Data Flow — BM25 Search

```
AI Client
  --> bm25_search(query, limit)
    --> NoteReader.bm25_search()
      --> rglob("*.md")                [scan all notes]
      --> tokenize each note           [build corpus]
      --> compute df (doc frequency)   [per-term IDF]
      --> score each doc (BM25 formula: k1=1.5, b=0.75)
      --> extract per-term excerpts
      --> sort by score desc
      --> return list[dict] (JSON)
```

## Integration Points

- **External APIs**: None
- **Databases**: None — Obsidian vault là filesystem flat-file store
- **MCP Protocol**: stdio transport via `mcp` library (FastMCP)
- **Configuration**: `.obsidian/daily-notes.json` cho daily note plugin settings
