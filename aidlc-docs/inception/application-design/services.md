# Services — Obsidian MCP Server

> MCP Tool Registry: mapping 18 tools sang components và error handling flow.

## Contents
- [Service Layer Overview](#service-layer-overview)
- [MCP Tool Registry](#mcp-tool-registry)
- [Error Handling Flow (SECURITY-15)](#error-handling-flow-security-15)

## Service Layer Overview

Project này là một MCP server đơn giản với local filesystem access — không cần service orchestration layer phức tạp. "Service" ở đây là MCP Tool handlers, mỗi tool là một thin wrapper.

---

## MCP Tool Registry

**File**: `src/obsidian_mcp/server.py` (registration) + `src/obsidian_mcp/tools/`

**Pattern**: FastMCP `@mcp.tool()` decorators — tools được register trực tiếp, không qua service bus.

**Tool → Component Mapping:**

### Read Tools (`tools/read_tools.py`)
| MCP Tool | Calls | Returns |
|---|---|---|
| `read_note` | `NoteReader.read_note()` | NoteContent |
| `list_notes` | `NoteReader.list_notes()` | list[NoteInfo] |
| `search_notes` | `NoteReader.search_notes()` | list[SearchResult] |
| `get_note_metadata` | `NoteReader.get_metadata()` | NoteMetadata |
| `get_backlinks` | `NoteReader.get_backlinks()` | list[str] |
| `get_outgoing_links` | `NoteReader.get_outgoing_links()` | list[WikiLink] |
| `read_canvas` | `NoteReader.read_canvas()` | dict |

### Write Tools (`tools/write_tools.py`)
| MCP Tool | Calls | Returns |
|---|---|---|
| `create_note` | `NoteWriter.create_note()` | NoteInfo |
| `update_note` | `NoteWriter.update_note()` | NoteInfo |
| `delete_note` | `NoteWriter.delete_note()` | confirmation |
| `move_note` | `NoteWriter.move_note()` | NoteInfo |
| `create_folder` | `NoteWriter.create_folder()` | confirmation |
| `delete_folder` | `NoteWriter.delete_folder()` | confirmation |

### Advanced Tools (`tools/advanced_tools.py`)
| MCP Tool | Calls | Returns |
|---|---|---|
| `get_graph_data` | `AdvancedFeatures.get_graph_data()` | GraphData |
| `get_all_tags` | `AdvancedFeatures.get_all_tags()` | list[TagInfo] |
| `get_dataview_fields` | `AdvancedFeatures.get_dataview_fields()` | dict |
| `get_daily_note` | `AdvancedFeatures.get_daily_note()` | NoteContent\|None |
| `list_attachments` | `AdvancedFeatures.list_attachments()` | list[AttachmentInfo] |

---

## Error Handling Flow (SECURITY-15)

```
MCP Tool Handler
      |
      | try
      v
  PathUtils.safe_vault_path()  <-- validate FIRST
      |
      v
  Component method()
      |
      | except ObsidianMCPError -> return MCP error response (user-safe message)
      | except Exception        -> log + return generic "Internal error" (no stack trace)
```

**Global error handler**: configured at server level via FastMCP error middleware.

## Related
- [[components]]
- [[application-design]]
- [[build-and-test-summary]]
