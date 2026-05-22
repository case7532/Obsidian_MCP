# Functional Design — Unit 1: Foundation

> Domain entities, business rules và data contracts cho Foundation layer.

## Contents
- [Business Logic Model](#business-logic-model)
- [Domain Entities](#domain-entities)
- [Business Rules](#business-rules)

## Business Logic Model

Unit 1 là pure infrastructure — không có business logic phức tạp, chỉ có:
1. **Path security logic** — validate & resolve paths
2. **Vault detection logic** — kiểm tra vault hợp lệ
3. **Data contracts** — shared models

---

## Domain Entities

### VaultConfig
```
VaultConfig
  vault_path: Path         # absolute, resolved, validated
  
  Invariant: vault_path.exists() AND (vault_path / ".obsidian").is_dir()
```

### NoteContent
```
NoteContent
  path: str                # vault-relative, e.g. "folder/note.md"
  raw: str                 # full file content
  frontmatter: dict        # parsed YAML from --- block (empty dict if none)
  body: str                # markdown content without frontmatter block
  
  Invariant: raw == (serialize(frontmatter) + body) if frontmatter else raw == body
```

### NoteInfo (lightweight reference)
```
NoteInfo
  path: str                # vault-relative
  title: str               # frontmatter["title"] OR stem of filename
  tags: list[str]          # from frontmatter["tags"] + inline #tags
  modified_at: str         # ISO 8601
```

### NoteMetadata
```
NoteMetadata
  path: str
  frontmatter: dict
  tags: list[str]
  created_at: str | None   # from frontmatter or filesystem (platform-dependent)
  modified_at: str         # ISO 8601 from filesystem mtime
  size_bytes: int
```

### WikiLink
```
WikiLink
  display: str             # text displayed — either alias or target
  target: str              # link target (note name or relative path)
  resolved_path: str|None  # vault-relative path if note exists; None if broken
  
  Cases: [[target]], [[target|alias]], [[target#heading]], [[target#heading|alias]]
```

### GraphData
```
GraphData
  nodes: list[{id: str, title: str, path: str, tags: list[str]}]
  edges: list[{source: str, target: str}]  # source/target = vault-relative paths
```

### TagInfo
```
TagInfo
  tag: str        # without # prefix
  count: int      # number of notes containing this tag
  notes: list[str]  # vault-relative paths
```

### SearchResult
```
SearchResult
  path: str
  title: str
  excerpt: str    # ~100 chars around first match
  score: float    # 0.0–1.0 (simple: 1.0 = title match, 0.5 = body match)
```

### AttachmentInfo
```
AttachmentInfo
  path: str       # vault-relative
  name: str       # filename with extension
  extension: str  # lowercase, no dot: "png", "pdf"
  size_bytes: int
  modified_at: str  # ISO 8601
```

---

## Business Rules

### BR-01: Vault Validation
- vault_path phải tồn tại trên filesystem
- vault_path phải là directory (không phải file)
- vault_path phải chứa `.obsidian/` subdirectory
- Nếu vi phạm → raise `VaultError` với message mô tả vấn đề (không expose system path đầy đủ trong production error)

### BR-02: Path Traversal Prevention (critical security rule — SECURITY-05)
- Mọi user-supplied path phải được resolve thành absolute path
- Resolved path phải bắt đầu bằng `vault_path` (dùng `Path.is_relative_to()`)
- Nếu vi phạm → raise `PathTraversalError` với message "Path outside vault boundary"
- Phải check TRƯỚC khi bất kỳ filesystem operation nào

### BR-03: Path Normalization
- Strip leading `/` từ vault-relative paths
- Normalize `..` và `.` components
- Ensure `.md` extension cho note paths (tự động thêm nếu thiếu)
- Normalize path separators (dùng `Path` object, không manipulate string thủ công)

### BR-04: Filename Sanitization
- Các ký tự không hợp lệ trong Obsidian filenames: `\ / : * ? " < > |`
- Replace bằng `-` hoặc raise error tùy context (write operations raise, read thì normalize)
- Obsidian cho phép Unicode — không strip Unicode chars

### BR-05: Frontmatter Parsing
- Frontmatter block là YAML giữa `---` delimiters ở đầu file
- Nếu không có frontmatter block → trả về empty dict, body = toàn bộ content
- YAML parse errors → trả về empty dict (graceful degradation, không crash)
- Tags trong frontmatter: field `tags` có thể là `list[str]` hoặc `str` (single tag)

### BR-06: Tag Normalization
- Strip `#` prefix nếu có
- Lowercase normalize (Obsidian tags case-insensitive)
- Deduplicate trong cùng một note

## Related
- [[nfr-requirements]]
- [[components]]
- [[unit-of-work]]
