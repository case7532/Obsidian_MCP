# API Documentation

## MCP Tools — Public API

Tất cả tools được expose qua MCP stdio protocol. AI client gọi theo tên tool + parameters.

---

### Read Tools

#### `read_note`
- **Purpose**: Đọc nội dung và frontmatter của một ghi chú
- **Parameters**: `path: str` — vault-relative path (vd: `folder/note.md`)
- **Returns**: `NoteContent` dict: `{path, raw, frontmatter, body}`
- **Errors**: `NoteNotFoundError` nếu không tồn tại

#### `list_notes`
- **Purpose**: Liệt kê ghi chú, lọc theo folder hoặc tag
- **Parameters**: `folder?: str`, `tag?: str` (có hoặc không có `#` prefix)
- **Returns**: `list[NoteInfo]` dict: `[{path, title, tags, modified_at}]`

#### `search_notes`
- **Purpose**: Full-text search đơn giản
- **Parameters**: `query: str`, `limit: int = 20` (max 100)
- **Returns**: `list[SearchResult]` dict: `[{path, title, excerpt, score}]` — sorted by score
- **Notes**: Score = 1.0 nếu match trong title, 0.5 nếu chỉ match trong body

#### `bm25_search` *(dev branch)*
- **Purpose**: BM25-ranked search, nhanh hơn và chính xác hơn search_notes
- **Parameters**: `query: str`, `limit: int = 20` (max 100)
- **Returns**: `list[dict]` JSON:
  ```json
  [
    {
      "path": "folder/note.md",
      "title": "Note Title",
      "score": 3.1416,
      "matched_terms": ["term1", "term2"],
      "excerpts": [
        {"term": "term1", "snippet": "…context around term1…"},
        {"term": "term2", "snippet": "…context around term2…"}
      ]
    }
  ]
  ```
- **Algorithm**: BM25 với k1=1.5, b=0.75; multi-word query; IDF-weighted; length-normalized

#### `get_note_metadata`
- **Purpose**: Lấy metadata của ghi chú
- **Parameters**: `path: str`
- **Returns**: `NoteMetadata` dict: `{path, frontmatter, tags, created_at, modified_at, size_bytes}`

#### `get_backlinks`
- **Purpose**: Tìm tất cả ghi chú link đến ghi chú này
- **Parameters**: `path: str`
- **Returns**: `list[str]` — vault-relative paths

#### `get_outgoing_links`
- **Purpose**: Lấy tất cả wiki-links trong ghi chú
- **Parameters**: `path: str`
- **Returns**: `list[WikiLink]` dict: `[{display, target, resolved_path}]`
  - `resolved_path` là `null` nếu link target không tồn tại trong vault

#### `read_canvas`
- **Purpose**: Đọc file `.canvas` Obsidian
- **Parameters**: `path: str` — phải là `.canvas` file
- **Returns**: `dict` — parsed JSON of canvas file structure

---

### Write Tools

#### `create_note`
- **Purpose**: Tạo ghi chú mới với format chuẩn; tự động cập nhật `_index.md` của folder
- **Parameters**:
  - `path?: str` — nếu bỏ qua, tự suy ra từ content/tags
  - `content: str = ""`
  - `frontmatter?: dict`
  - `title?: str`
  - `description: str = ""`
  - `links?: list[str]` — danh sách tên ghi chú cho Related section
- **Returns**: `NoteInfo` dict
- **Errors**: `NoteExistsError` nếu đã tồn tại
- **Side effect**: Cập nhật `_index.md` của folder — chỉ bổ sung entry còn thiếu, không xóa mô tả cũ

#### `update_note`
- **Purpose**: Cập nhật nội dung ghi chú
- **Parameters**: `path: str`, `content: str`, `mode: str = "replace"` (`"replace"` hoặc `"append"`)
- **Returns**: `NoteInfo` dict
- **Errors**: `NoteNotFoundError`

#### `delete_note`
- **Purpose**: Xóa ghi chú vĩnh viễn
- **Parameters**: `path: str`
- **Returns**: `{deleted: path}`
- **Errors**: `NoteNotFoundError`

#### `move_note`
- **Purpose**: Di chuyển/đổi tên ghi chú
- **Parameters**: `source: str`, `destination: str`, `update_links: bool = True`
- **Returns**: `NoteInfo` dict tại destination
- **Errors**: `NoteNotFoundError` (source), `NoteExistsError` (destination)
- **Side effect**: Nếu `update_links=True`, tự động rewrite tất cả `[[old_stem]]` → `[[new_stem]]` trong vault

#### `create_folder`
- **Purpose**: Tạo folder và sinh `_index.md`
- **Parameters**: `path: str`
- **Returns**: `{created: path}`

#### `delete_folder`
- **Purpose**: Xóa folder
- **Parameters**: `path: str`, `force: bool = False`
- **Returns**: `{deleted: path}`
- **Errors**: `FolderNotEmptyError` nếu non-empty và `force=False`

---

### Advanced Tools

#### `get_graph_data`
- **Purpose**: Lấy toàn bộ link graph của vault
- **Parameters**: None
- **Returns**: `GraphData` dict: `{nodes: [{id, title, path, tags}], edges: [{source, target}]}`

#### `get_all_tags`
- **Purpose**: Lấy tất cả tags với usage count
- **Parameters**: None
- **Returns**: `list[TagInfo]` dict: `[{tag, count, notes}]`

#### `get_dataview_fields`
- **Purpose**: Parse Dataview inline fields từ ghi chú
- **Parameters**: `path: str`
- **Returns**: `dict` — `{field_name: value}`
- **Errors**: `NoteNotFoundError`

#### `get_daily_note`
- **Purpose**: Lấy daily note theo ngày
- **Parameters**: `date: str` — format `YYYY-MM-DD`
- **Returns**: `NoteContent` dict hoặc `null` nếu không tìm thấy
- **Notes**: Đọc `.obsidian/daily-notes.json` cho folder/format config; hỗ trợ moment.js format string

#### `list_attachments`
- **Purpose**: Liệt kê file đính kèm (ảnh, PDF, audio, v.v.)
- **Parameters**: `folder?: str`
- **Returns**: `list[AttachmentInfo]` dict: `[{path, name, extension, size_bytes, modified_at}]`

---

## Internal APIs (Python)

### NoteReader Internal Helpers

| Function | Signature | Purpose |
|---|---|---|
| `_parse_frontmatter` | `(raw: str) -> (dict, str)` | Parse YAML frontmatter block, return (fm_dict, body) |
| `_extract_tags` | `(fm: dict, body: str) -> list[str]` | Combine frontmatter + inline `#tags`, normalize lowercase |
| `_parse_wikilinks` | `(text: str, vault_path) -> list[WikiLink]` | Extract all `[[link]]` with alias and resolved path |
| `_resolve_wikilink` | `(target: str, vault_path) -> str | None` | BFS search vault for matching stem |

### NoteWriter Internal Helpers

| Function | Signature | Purpose |
|---|---|---|
| `_build_document_template` | `(title, desc, content, links) -> str` | Build standard note format |
| `_infer_folder` | `(vault_path, title, tags, content) -> str` | Score folders by keyword match |
| `_update_folder_index` | `(folder_abs: Path) -> None` | Add missing note links to _index.md only |
| `_serialize_frontmatter` | `(fm: dict) -> str` | YAML dump with `---` delimiters |
| `_update_backlinks` | `(old_stem, new_stem) -> None` | Regex rewrite across all vault .md files |

## Data Models

### NoteContent
```
path: str          # vault-relative
raw: str           # full file content
frontmatter: dict  # parsed YAML
body: str          # content after frontmatter block
```

### NoteInfo
```
path: str
title: str         # frontmatter["title"] or filename stem
tags: list[str]    # normalized, lowercase, no # prefix
modified_at: str   # ISO 8601 UTC
```

### NoteMetadata
```
path: str
frontmatter: dict
tags: list[str]
created_at: str | None   # not available cross-platform
modified_at: str
size_bytes: int
```

### WikiLink
```
display: str             # alias or target name
target: str              # raw link target (without alias/heading)
resolved_path: str | None  # vault-relative if found
```

### SearchResult
```
path: str
title: str
excerpt: str    # ~100-char snippet around first match
score: float    # 0.5 or 1.0
```

### BM25SearchResult (dict)
```
path: str
title: str
score: float         # BM25 continuous score
matched_terms: list[str]
excerpts: list[{term, snippet}]
```
