# Functional Design — Unit 2: Read Operations

> Business logic cho 7 read tools: đọc note, search, backlinks, wiki-links.

## Contents
- [Business Rules](#business-rules)
- [PBT Properties (PBT-01)](#pbt-properties-pbt-01)

## Business Rules

### BR-R01: Frontmatter Parsing
- Block YAML giữa `---` ở đầu file (dòng đầu tiên phải là `---`)
- YAML parse error → empty dict, log WARNING, không raise
- Tags từ frontmatter: field `tags` — list hoặc string đơn → normalize sang list
- Frontmatter body separator: content sau closing `---\n`

### BR-R02: Wiki-link Parsing
- Pattern: `[[target]]`, `[[target|alias]]`, `[[target#heading]]`, `[[target#heading|alias]]`
- `display` = alias nếu có, else target (strip heading fragment)
- `target` = phần trước `#` và `|`
- `resolved_path`: tìm file `{target}.md` trong vault (BFS từ vault root), None nếu không tìm thấy

### BR-R03: Tag Extraction
- Inline tags: `#tag` ở đầu word boundary (không phải trong code block hay URL)
- Frontmatter tags + inline tags → merge, deduplicate, lowercase, strip `#`
- Exclude: tags trong fenced code blocks (``` ```  ```)

### BR-R04: Search
- Full-text: scan tất cả `.md` files, case-insensitive substring match
- Score: 1.0 nếu match trong title/filename, 0.5 nếu match trong body
- Excerpt: 100 chars xung quanh first match, ellipsis nếu truncated
- Limit: default 20, max 100

### BR-R05: Backlinks
- Scan toàn bộ vault, tìm notes có `[[current-note-name]]` hoặc `[[path/to/note]]`
- Match cả alias forms: `[[note|alias]]`
- Trả về vault-relative paths của notes chứa backlink

### BR-R06: Note Listing
- Scan đệ quy tất cả `.md` files trong vault (exclude `.obsidian/`)
- Filter by folder: path phải bắt đầu với folder prefix
- Filter by tag: note phải chứa tag sau normalize
- `title`: frontmatter["title"] nếu có, else filename stem

### BR-R07: Canvas Reading
- Canvas files là JSON — parse và trả về raw dict
- Nếu JSON invalid → raise `NoteNotFoundError` với message "Invalid canvas file"

## PBT Properties (PBT-01)

| Component | Category | Property |
|---|---|---|
| Frontmatter parser | Round-trip | `parse(serialize(fm)) == fm` (for serializable values) |
| Wiki-link parser | Round-trip | Re-format parsed link reproduces original target |
| Tag extraction | Invariant | Extracted tags ⊆ all `#tag` occurrences in text |
| Note listing + filter | Invariant | filtered list ⊆ full list |

## Related
- [[nfr-design-patterns]]
- [[components]]
- [[unit-of-work]]
