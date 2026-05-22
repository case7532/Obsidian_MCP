# Code Quality Assessment

## Test Coverage

- **Overall**: 85 tests — **Good**
- **Unit Tests**: 85 passing, 0 failing (verified `uv run pytest`)
- **Integration Tests**: None (thư mục `tests/integration/` rỗng)
- **Property-Based Tests**: Có (Hypothesis) cho `path_utils`, `note_reader` parsers

### Coverage by Component

| Module | Test Module | Coverage |
|---|---|---|
| `vault_config.py` | `test_vault_config.py` | Good |
| `path_utils.py` | `test_path_utils.py` + PBT | Good + edge cases |
| `note_reader.py` | `test_note_reader.py` + PBT | Good |
| `note_writer.py` | `test_note_writer.py` | Good |
| `advanced_features.py` | `test_advanced_features.py` | Fair |
| `server.py` | Not tested | Not tested |
| `tools/*.py` | Not tested | Not tested |
| `bm25_search` | Not tested (new) | Missing |

## Code Quality Indicators

- **Linting**: Không có cấu hình (`ruff`, `flake8`, `mypy` chưa setup)
- **Type Hints**: Tốt — hầu hết functions có type annotations đầy đủ
- **Code Style**: Consistent PEP 8 throughout
- **Docstrings**: Tốt — tất cả public methods có docstrings với Args/Returns
- **Logging**: Tốt — `logging.getLogger(__name__)` pattern đúng chuẩn
- **Error Handling**: Tốt — custom exception hierarchy, specific error messages

## Strengths

- **Security-first design**: `path_utils` là single security boundary, không bypass được
- **Clean separation of concerns**: domain (reader/writer/advanced) tách biệt adapter (tools)
- **Immutable DTOs**: Models dùng `@dataclass` — rõ ràng, serializable
- **BM25 without dependencies**: Pure stdlib implementation — không bloat runtime deps
- **Smart folder index**: Incremental update — không overwrite mô tả cũ của user

## Technical Debt

| Issue | Location | Severity | Notes |
|---|---|---|---|
| No linting config | project root | Low | Thiếu `ruff`/`mypy` config |
| BM25 not tested | `note_reader.py` | Medium | New feature cần unit tests |
| `tools/` not tested | `tools/*.py` | Low | Thin adapters, low risk |
| `server.py` not tested | `server.py` | Low | Entry point, hard to unit test |
| Integration tests empty | `tests/integration/` | Medium | Không có end-to-end test |
| BM25 in-memory corpus | `bm25_search` | Medium | Với vault lớn (>10k notes), build corpus mỗi query tốn thời gian — cần index cache |
| `created_at` = None | `NoteMetadata` | Low | macOS `st_birthtime` chưa implement |
| `search_notes` break early | `note_reader.py` | Low | Break khi đủ limit — không đảm bảo top-N relevant nhất |

## Patterns and Anti-patterns

### Good Patterns
- **Gateway/Security Boundary**: `safe_vault_path()` — tất cả user input path đi qua đây
- **Dependency Injection**: `NoteWriter(config, reader)` — testable, không hardcode
- **Adapter Pattern**: `tools/` layer tách domain khỏi protocol
- **Template Method**: `_build_document_template()` — format note nhất quán
- **Incremental Update**: `_update_folder_index()` — chỉ append missing, preserve existing

### Anti-patterns
- **BM25 corpus rebuild**: Build toàn bộ corpus mỗi lần gọi — nên cache/index
- **`rglob` everywhere**: `NoteReader`, `AdvancedFeatures`, `NoteWriter` đều scan toàn vault — với vault lớn sẽ chậm; chưa có caching layer
- **Circular import risk**: `note_writer` import từ `note_reader` nội bộ (`_parse_frontmatter`, `_extract_tags`) — nên extract ra `parsers.py` riêng
- **Missing `__all__`**: Không khai báo public API của modules

## Recommendations

1. **Thêm tests cho `bm25_search`** — feature mới cần coverage
2. **Thêm `ruff` vào pyproject.toml** — linting tự động
3. **Thêm `mypy` strict** — type checking
4. **Extract parsers** — `_parse_frontmatter`, `_extract_tags`, `_parse_wikilinks` vào `parsers.py` để tránh circular import tiềm năng
5. **Index cache cho search** — inverted index hoặc cache corpus để `bm25_search` nhanh hơn với vault lớn
6. **Integration test** — ít nhất 1 end-to-end test với real MCP transport
