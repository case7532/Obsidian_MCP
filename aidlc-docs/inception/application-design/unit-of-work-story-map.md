# Unit of Work Story Map

> Mapping Functional Requirements sang từng unit of work.

## Contents
- [FR → Unit Mapping](#fr-→-unit-mapping)
- [Coverage Summary](#coverage-summary)

*Note: User Stories stage was skipped (developer tool, no user personas). Mapping được tạo trực tiếp từ Functional Requirements.*

## FR → Unit Mapping

| Requirement | Tool(s) | Unit |
|---|---|---|
| FR-01: MCP Server Core | server entry point, stdio | Unit 4 |
| FR-02: read_note | `read_note` | Unit 2 |
| FR-02: list_notes | `list_notes` | Unit 2 |
| FR-02: search_notes | `search_notes` | Unit 2 |
| FR-02: get_note_metadata | `get_note_metadata` | Unit 2 |
| FR-02: get_backlinks | `get_backlinks` | Unit 2 |
| FR-02: get_outgoing_links | `get_outgoing_links` | Unit 2 |
| FR-02: read_canvas | `read_canvas` | Unit 2 |
| FR-03: create_note | `create_note` | Unit 3 |
| FR-03: update_note | `update_note` | Unit 3 |
| FR-03: delete_note | `delete_note` | Unit 3 |
| FR-03: move_note | `move_note` | Unit 3 |
| FR-03: create_folder | `create_folder` | Unit 3 |
| FR-03: delete_folder | `delete_folder` | Unit 3 |
| FR-04: get_all_tags | `get_all_tags` | Unit 4 |
| FR-04: get_graph_data | `get_graph_data` | Unit 4 |
| FR-04: read_canvas (advanced) | (in Unit 2 NoteReader) | Unit 2 |
| FR-04: get_dataview_fields | `get_dataview_fields` | Unit 4 |
| FR-04: get_daily_note | `get_daily_note` | Unit 4 |
| FR-05: Vault Configuration | `VaultConfig`, `PathUtils` | Unit 1 |
| FR-06: list_attachments | `list_attachments` | Unit 4 |
| NFR-02: Security / path traversal | `PathUtils.safe_vault_path` | Unit 1 |
| NFR-02: Input validation | all tool handlers | Unit 2+3+4 |
| NFR-03: Atomic writes | `NoteWriter` | Unit 3 |
| NFR-03: Error handling | exceptions + global handler | Unit 1+4 |

## Coverage Summary

| Unit | FRs Covered | Tools |
|---|---|---|
| Unit 1: Foundation | FR-05, NFR-02 (security) | — (infrastructure only) |
| Unit 2: Read | FR-02 | 7 tools |
| Unit 3: Write | FR-03 | 6 tools |
| Unit 4: Advanced + Server | FR-01, FR-04, FR-06 | 5 tools + server wiring |
| **Total** | **All FRs** | **18 tools** |

## Related
- [[unit-of-work]]
- [[requirements]]
