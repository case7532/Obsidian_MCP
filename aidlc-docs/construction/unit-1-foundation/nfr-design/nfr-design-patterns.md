# NFR Design Patterns — Unit 1: Foundation

> Design patterns áp dụng cho path validation, error handling và logging.

## Contents
- [Security Pattern: Fail-Closed Path Validation (SECURITY-05, SECURITY-15)](#security-pattern-fail-closed-path-validation-security-05-security-15)
- [Error Handling Pattern: Fail-Closed + Generic Messages (SECURITY-09, SECURITY-15)](#error-handling-pattern-fail-closed-+-generic-messages-security-09-security-15)
- [Logging Pattern (SECURITY-03)](#logging-pattern-security-03)
- [Dependency Pinning Pattern (SECURITY-10)](#dependency-pinning-pattern-security-10)
- [PBT Design (PBT-02, PBT-03, PBT-07)](#pbt-design-pbt-02-pbt-03-pbt-07)

## Security Pattern: Fail-Closed Path Validation (SECURITY-05, SECURITY-15)

```
User Input (path string)
    |
    v
[1] Path("").resolve() against vault_path  ← normalize + make absolute
    |
    v
[2] resolved.is_relative_to(vault_path)    ← boundary check
    |
    +-- False → raise PathTraversalError("Path outside vault boundary")
    |
    +-- True  → return resolved Path        ← ONLY exit with valid path
```

**Pattern**: Allowlist (must be inside vault) not denylist (block `..`). Dùng `Path.resolve()` thay vì string manipulation — immune to `../`, `%2e%2e`, symlink tricks.

## Error Handling Pattern: Fail-Closed + Generic Messages (SECURITY-09, SECURITY-15)

```python
# Internal errors: full detail in logs (SECURITY-03)
# External errors: generic user-safe message only

class PathTraversalError(ObsidianMCPError):
    # message: "Path outside vault boundary"  ← không reveal vault_path
    
class VaultError(ObsidianMCPError):
    # message: "Invalid vault: .obsidian directory not found"  ← generic
```

## Logging Pattern (SECURITY-03)

- Dùng Python `logging` stdlib — không dùng `print()`
- Log level: `WARNING` cho security events (path traversal attempts)
- Log format: `%(asctime)s %(levelname)s %(name)s: %(message)s`
- **KHÔNG log**: vault_path contents, note content, user data
- **LOG**: operation type, error type, sanitized path (truncated nếu dài)

## Dependency Pinning Pattern (SECURITY-10)

```toml
# pyproject.toml — exact lower bounds + lock file
[project]
dependencies = [
    "mcp>=1.0.0",
    "PyYAML>=6.0.1",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "hypothesis>=6.100.0",
]
```

`uv.lock` committed to version control — đảm bảo reproducible builds.

## PBT Design (PBT-02, PBT-03, PBT-07)

### Generator Design

```python
# Reusable generators cho path_utils tests
vault_relative_paths = st.from_regex(r'[a-zA-Z0-9_\- /]+\.md', fullmatch=True)
note_names = st.from_regex(r'[a-zA-Z0-9_\- ]+', fullmatch=True)
frontmatter_dicts = st.dictionaries(
    keys=st.text(alphabet=st.characters(whitelist_categories=('Lu','Ll','Nd'), min_codepoint=32), min_size=1, max_size=20),
    values=st.one_of(st.text(max_size=100), st.integers(), st.lists(st.text(max_size=20)))
)
```

### Properties to Test

| Property | Type | Test |
|---|---|---|
| `to_relative(to_absolute(p)) == p` | Round-trip | PBT-02 |
| `safe_vault_path` output always inside vault | Invariant | PBT-03 |
| `normalize_note_path` idempotent | Idempotence | PBT-04 |
| `parse_frontmatter(serialize(fm)) == fm` | Round-trip | PBT-02 |

## Related
- [[nfr-requirements]]
- [[business-logic-model]]
