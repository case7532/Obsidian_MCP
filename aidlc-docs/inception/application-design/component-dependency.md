# Component Dependency — Obsidian MCP Server

> Ma trận phụ thuộc giữa các components và thứ tự khởi tạo.

## Contents
- [Dependency Matrix](#dependency-matrix)
- [Data Flow](#data-flow)
- [Key Design Decisions](#key-design-decisions)

## Dependency Matrix

| Component | Depends On |
|---|---|
| `server.py` | VaultConfig, all Tool modules |
| `tools/read_tools.py` | NoteReader, PathUtils |
| `tools/write_tools.py` | NoteWriter, PathUtils |
| `tools/advanced_tools.py` | AdvancedFeatures, PathUtils |
| `NoteReader` | VaultConfig, PathUtils |
| `NoteWriter` | VaultConfig, PathUtils, NoteReader (for link update) |
| `AdvancedFeatures` | VaultConfig, PathUtils, NoteReader |
| `VaultConfig` | (none — only stdlib) |
| `PathUtils` | VaultConfig |
| `models.py` | (none — pure dataclasses) |
| `exceptions.py` | (none — pure exceptions) |

## Data Flow

```
Kiro CLI / MCP Client
        |  stdio (JSON-RPC)
        v
   server.py (FastMCP)
        |
        v
   Tool Handler (input validation)
        |
        v
   PathUtils.safe_vault_path()
        |
        v
   Component (NoteReader / NoteWriter / AdvancedFeatures)
        |
        v
   Local Filesystem (vault_path)
```

## Key Design Decisions

- **No circular dependencies**: models.py và exceptions.py đứng độc lập, mọi component đều có thể import.
- **PathUtils là security boundary**: Mọi path đến filesystem đều phải qua `safe_vault_path()` trước.
- **NoteWriter phụ thuộc NoteReader**: Chỉ để `move_note()` cần scan và update backlinks. Không phụ thuộc theo chiều ngược lại.
- **VaultConfig là single source of truth** cho vault_path — không hardcode path ở bất kỳ đâu khác.

## Related
- [[components]]
- [[application-design]]
