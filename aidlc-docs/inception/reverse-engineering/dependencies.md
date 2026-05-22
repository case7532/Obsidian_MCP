# Dependencies

## Internal Module Dependencies

```
server.py
  +-- vault_config.py
  +-- note_reader.py
  |     +-- models.py
  |     +-- exceptions.py
  |     +-- path_utils.py
  |     +-- vault_config.py
  +-- note_writer.py
  |     +-- models.py
  |     +-- exceptions.py
  |     +-- path_utils.py
  |     +-- vault_config.py
  |     +-- note_reader.py  (for _note_info helper)
  +-- advanced_features.py
  |     +-- models.py
  |     +-- exceptions.py
  |     +-- path_utils.py
  |     +-- vault_config.py
  |     +-- note_reader.py  (delegates read_note for daily_note)
  +-- tools/read_tools.py
  |     +-- note_reader.py
  +-- tools/write_tools.py
  |     +-- note_writer.py
  +-- tools/advanced_tools.py
        +-- advanced_features.py

models.py        -- no dependencies (pure dataclasses)
exceptions.py    -- no dependencies (pure exceptions)
path_utils.py    -- exceptions.py only
vault_config.py  -- exceptions.py, stdlib only
```

## External Dependencies

### Runtime

| Dependency | Version | Purpose | License |
|---|---|---|---|
| `mcp` | >=1.0.0 | FastMCP server framework, MCP protocol implementation, stdio transport | MIT |
| `PyYAML` | >=6.0.1 | YAML parsing và serialization cho frontmatter | MIT |

### Development / Test

| Dependency | Version | Purpose | License |
|---|---|---|---|
| `pytest` | >=8.0.0 | Test runner | MIT |
| `pytest-cov` | >=5.0.0 | Code coverage measurement | MIT |
| `hypothesis` | >=6.100.0 | Property-based testing, shrinkable counterexamples | MPL 2.0 |

## Dependency Notes

- **Zero transitive runtime risk**: Chỉ 2 runtime dependencies (`mcp`, `PyYAML`) — cả hai widely-used, mature libraries
- **No network dependencies**: Không call external APIs, không cần internet
- **BM25 search**: Implement thuần Python stdlib (`math`, `collections`) — không cần thư viện ML/NLP
- **Lockfile**: `uv.lock` đảm bảo reproducible builds với pinned versions

## Module Coupling Analysis

| Module | Afferent (used by) | Efferent (depends on) | Coupling |
|---|---|---|---|
| `models.py` | reader, writer, advanced, tools | 0 | Low |
| `exceptions.py` | reader, writer, advanced, path_utils, vault_config | 0 | Low |
| `path_utils.py` | reader, writer, advanced | exceptions | Low |
| `vault_config.py` | server, reader, writer, advanced | exceptions | Low |
| `note_reader.py` | server, writer, advanced, tools | vault_config, path_utils, models, exceptions | Medium |
| `note_writer.py` | server, tools | vault_config, note_reader, path_utils, models, exceptions | Medium |
| `advanced_features.py` | server, tools | vault_config, note_reader, path_utils, models | Medium |
| `server.py` | (entry point) | all | High (intentional) |
