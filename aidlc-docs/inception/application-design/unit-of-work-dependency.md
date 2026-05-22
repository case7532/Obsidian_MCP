# Unit of Work Dependency

> Ma trận phụ thuộc giữa 4 units và thứ tự thực thi.

## Contents
- [Dependency Matrix](#dependency-matrix)
- [Inter-Unit Interface Contracts](#inter-unit-interface-contracts)
- [Critical Path](#critical-path)

## Dependency Matrix

| Unit | Depends On | Type |
|---|---|---|
| Unit 1: Foundation | — | — |
| Unit 2: Read | Unit 1 | Hard (imports models, path_utils, vault_config) |
| Unit 3: Write | Unit 1, Unit 2 | Hard (imports models, path_utils; NoteReader for backlink scan) |
| Unit 4: Advanced + Server | Unit 1, Unit 2, Unit 3 | Hard (all components, registers all tools) |

## Inter-Unit Interface Contracts

### Unit 1 → exports to all
- `VaultConfig` — vault path config object
- `safe_vault_path(vault_path, user_input) -> Path` — security boundary
- `NoteContent`, `NoteInfo`, `NoteMetadata`, `SearchResult`, `WikiLink`, `GraphData`, `TagInfo`, `AttachmentInfo` — shared models
- `ObsidianMCPError` hierarchy — exception types

### Unit 2 → exports to Unit 3 and Unit 4
- `NoteReader` class — Unit 3 uses it for `move_note` backlink scanning

### Unit 3 → exports to Unit 4
- `NoteWriter` class — Unit 4 registers write tools

### Unit 4 → exports to external
- `server.py` — MCP server entry point (`obsidian-mcp` CLI command)

## Critical Path

`Unit 1` → `Unit 2` → `Unit 3` → `Unit 4`

Unit 3 có dependency nhỏ vào Unit 2 (`NoteReader.get_backlinks` trong `move_note`). Nếu cần parallelize, Unit 3 có thể implement trước và stub `move_note` backlink update, hoàn thiện sau khi Unit 2 done.

## Related
- [[unit-of-work]]
- [[unit-of-work-story-map]]
