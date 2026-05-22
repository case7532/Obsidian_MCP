# Performance Test Instructions

> Benchmark script và targets cho read/search/write operations.

## Contents
- [Performance Targets (from NFR-01)](#performance-targets-from-nfr-01)
- [Manual benchmark — generate test vault](#manual-benchmark-—-generate-test-vault)
- [Expected results](#expected-results)
- [No dedicated perf test framework required](#no-dedicated-perf-test-framework-required)

## Performance Targets (from NFR-01)
- Read operations: < 200ms
- Search (full-text): < 1s for vault < 10,000 notes
- Write operations: < 500ms

## Manual benchmark — generate test vault

```python
# generate_test_vault.py — create a large vault for perf testing
import time
from pathlib import Path
from obsidian_mcp.vault_config import VaultConfig
from obsidian_mcp.note_reader import NoteReader
from obsidian_mcp.note_writer import NoteWriter

vault_path = Path("/tmp/perf-vault")
vault_path.mkdir(exist_ok=True)
(vault_path / ".obsidian").mkdir(exist_ok=True)

config = VaultConfig(vault_path)
reader = NoteReader(config)
writer = NoteWriter(config, reader)

# Create 1000 notes
for i in range(1000):
    writer.create_note(f"note-{i:04d}.md", f"# Note {i}\n\nContent with #tag{i % 10} and [[note-{(i+1) % 1000:04d}]]")

# Benchmark
t0 = time.perf_counter()
results = reader.search_notes("Content", limit=20)
print(f"search_notes (1000 notes): {(time.perf_counter() - t0)*1000:.1f}ms")

t0 = time.perf_counter()
notes = reader.list_notes()
print(f"list_notes (1000 notes): {(time.perf_counter() - t0)*1000:.1f}ms")

t0 = time.perf_counter()
backlinks = reader.get_backlinks("note-0000.md")
print(f"get_backlinks (1000 notes): {(time.perf_counter() - t0)*1000:.1f}ms")
```

```bash
cd /path/to/obsidian-mcp
uv run python generate_test_vault.py
```

## Expected results
All operations should complete well within targets for 1,000-note vault. For 10,000 notes, search may approach the 1s target — acceptable per NFR-01.

## No dedicated perf test framework required
This is a local filesystem tool with no network I/O. Performance testing is straightforward benchmarking, not load testing.

## Related
- [[build-instructions]]
- [[build-and-test-summary]]
