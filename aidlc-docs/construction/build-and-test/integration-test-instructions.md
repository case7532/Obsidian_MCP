# Integration Test Instructions

> Hướng dẫn chạy integration tests và kiểm tra kết nối MCP client-server.

## Contents
- [Purpose](#purpose)
- [Setup](#setup)
- [Key scenarios to test manually](#key-scenarios-to-test-manually)
- [Run integration tests (when implemented)](#run-integration-tests-when-implemented)
- [Notes](#notes)

## Purpose
Verify that MCP tools work end-to-end against a real vault (NoteReader + NoteWriter + AdvancedFeatures + server wiring).

## Setup
```bash
# Create a test vault
mkdir -p /tmp/test-vault/.obsidian
```

## Key scenarios to test manually

### Scenario 1: Read → Write → Read round-trip
```python
# In tests/integration/test_tools.py
# 1. create_note("test.md", "# Hello")
# 2. read_note("test.md") → verify content
# 3. update_note("test.md", "\nAppended", mode="append")
# 4. read_note("test.md") → verify both lines
# 5. delete_note("test.md") → verify gone
```

### Scenario 2: Move note + backlink update
```python
# 1. create_note("original.md", "# Original")
# 2. create_note("linker.md", "See [[original]]")
# 3. move_note("original.md", "renamed.md", update_links=True)
# 4. read_note("linker.md") → verify [[renamed]] in content
```

### Scenario 3: Search across vault
```python
# 1. Create 5 notes with varying content
# 2. search_notes("keyword") → verify only matching notes returned
# 3. Verify score ordering (title match > body match)
```

### Scenario 4: Server startup
```bash
OBSIDIAN_VAULT_PATH=/tmp/test-vault uv run obsidian-mcp &
# Verify no errors on stderr within 2 seconds
kill %1
```

## Run integration tests (when implemented)
```bash
uv run pytest tests/integration/ -v
```

## Notes
- Integration tests use `tmp_path` fixture (real filesystem, temp directory)
- No mocking — test against actual file I/O
- Each test creates its own isolated vault via fixture

## Related
- [[unit-test-instructions]]
- [[performance-test-instructions]]
- [[build-and-test-summary]]
