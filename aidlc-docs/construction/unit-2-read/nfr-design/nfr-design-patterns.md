# NFR Design Patterns — Unit 2: Read Operations

> Design patterns cho performance, caching và security trong read operations.

## Contents
- [Performance Pattern](#performance-pattern)
- [Security Pattern (SECURITY-05)](#security-pattern-security-05)
- [Error Handling (SECURITY-15)](#error-handling-security-15)
- [Logging (SECURITY-03)](#logging-security-03)

## Performance Pattern
- `list_notes`: scan filesystem once, cache trong request (không persistent cache — vault có thể thay đổi)
- `search_notes`: sequential scan, early exit khi đạt limit
- `get_backlinks`: scan toàn vault — O(n notes), acceptable cho vault < 10k notes

## Security Pattern (SECURITY-05)
- Mọi path input qua `safe_vault_path()` trước khi filesystem access
- `search_notes` query: không execute như code, chỉ dùng như substring pattern

## Error Handling (SECURITY-15)
- File không tồn tại → `NoteNotFoundError`
- Path traversal → `PathTraversalError` (từ path_utils)
- Permission error → wrap thành `ObsidianMCPError("Cannot read file")`
- Tất cả exceptions map sang MCP error responses tại tool handler level

## Logging (SECURITY-03)
- Log operation type và path (vault-relative), KHÔNG log note content
- `WARNING` cho missing files, `ERROR` cho unexpected exceptions

## Related
- [[business-logic-model]]
- [[nfr-requirements]]
