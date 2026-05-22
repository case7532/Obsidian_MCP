# Component Inventory

## Application Packages

| Package | Type | Purpose |
|---|---|---|
| `obsidian_mcp` | Application | MCP server chính — expose 15+ tools cho AI clients |

## Source Modules

| Module | Lines | Responsibility |
|---|---|---|
| `server.py` | ~55 | Entry point, component wiring, CLI, MCP run |
| `vault_config.py` | ~70 | Vault path validation, env/CLI config |
| `models.py` | ~55 | Data classes / DTOs |
| `exceptions.py` | ~20 | Exception hierarchy |
| `path_utils.py` | ~80 | Security boundary, path operations |
| `note_reader.py` | ~280 | All read + BM25 search logic |
| `note_writer.py` | ~220 | All write + folder index management |
| `advanced_features.py` | ~180 | Graph, tags, dataview, daily note, attachments |
| `tools/read_tools.py` | ~75 | MCP adapter: 8 read tools |
| `tools/write_tools.py` | ~75 | MCP adapter: 6 write tools |
| `tools/advanced_tools.py` | ~45 | MCP adapter: 5 advanced tools |

## MCP Tools Summary

| Category | Tool | Status |
|---|---|---|
| Read | `read_note` | Stable |
| Read | `list_notes` | Stable |
| Read | `search_notes` | Stable |
| Read | `bm25_search` | Dev (new) |
| Read | `get_note_metadata` | Stable |
| Read | `get_backlinks` | Stable |
| Read | `get_outgoing_links` | Stable |
| Read | `read_canvas` | Stable |
| Write | `create_note` | Stable (updated folder index logic) |
| Write | `update_note` | Stable |
| Write | `delete_note` | Stable |
| Write | `move_note` | Stable |
| Write | `create_folder` | Stable |
| Write | `delete_folder` | Stable |
| Advanced | `get_graph_data` | Stable |
| Advanced | `get_all_tags` | Stable |
| Advanced | `get_dataview_fields` | Stable |
| Advanced | `get_daily_note` | Stable |
| Advanced | `list_attachments` | Stable |

## Test Modules

| Module | Tests | Coverage |
|---|---|---|
| `test_vault_config.py` | ~10 | VaultConfig validation |
| `test_path_utils.py` | ~20 + PBT | Traversal, sanitize, normalize |
| `test_note_reader.py` | ~30 + PBT | All read ops, parsers |
| `test_note_writer.py` | ~30 | All write ops, folder index |
| `test_advanced_features.py` | ~15 | Graph, tags, dataview, attachments |
| **Total** | **85 tests** | All passing |

## Total Count
- **Total Modules**: 11 source + 5 test = 16
- **Application**: 8 domain modules
- **Adapter**: 3 tool modules
- **Infrastructure**: 3 (server, vault_config, path_utils)
- **Test**: 5 unit test modules
