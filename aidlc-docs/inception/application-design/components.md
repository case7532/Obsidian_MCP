# Components — Obsidian MCP Server

> Danh sách 7 components: mục đích, trách nhiệm và quan hệ phụ thuộc.

## Contents
- [Component Overview](#component-overview)
- [C-01: MCP Server (Entry Point)](#c-01-mcp-server-entry-point)
- [C-02: Vault Config](#c-02-vault-config)
- [C-03: Path Security Utils](#c-03-path-security-utils)
- [C-04: Note Reader](#c-04-note-reader)
- [C-05: Note Writer](#c-05-note-writer)
- [C-06: Advanced Features](#c-06-advanced-features)
- [C-07: MCP Tools (Tool Handlers)](#c-07-mcp-tools-tool-handlers)

## Component Overview

```
+------------------+       +-------------------+       +------------------+
|   MCP Server     | ----> |   Tool Registry   | ----> |  Vault Access    |
|   (Entry Point)  |       |   (Dispatcher)    |       |  Layer           |
+------------------+       +-------------------+       +------------------+
                                                               |
                                    +--------------------------+----------+
                                    |                          |          |
                             +------+------+          +--------+---+  +--+--------+
                             | Note Reader |          | Note Writer|  | Advanced  |
                             | Component   |          | Component  |  | Features  |
                             +-------------+          +------------+  +-----------+
                                    |
                             +------+------+
                             |  Path Utils |
                             | (Security)  |
                             +-------------+
```

---

## C-01: MCP Server (Entry Point)

**File**: `src/obsidian_mcp/server.py`

**Purpose**: Điểm khởi động MCP server, wire up tất cả components, handle stdio transport.

**Responsibilities**:
- Khởi tạo FastMCP server instance
- Register tất cả tools từ Tool Registry
- Đọc `vault_path` từ CLI arg hoặc env var `OBSIDIAN_VAULT_PATH`
- Validate vault path trước khi start
- Run server qua stdio transport

---

## C-02: Vault Config

**File**: `src/obsidian_mcp/vault_config.py`

**Purpose**: Quản lý vault configuration và validation.

**Responsibilities**:
- Resolve và validate `vault_path` (tồn tại, có `.obsidian/` dir)
- Expose `vault_path` như một typed config object
- Cung cấp helper để resolve đường dẫn tương đối trong vault

---

## C-03: Path Security Utils

**File**: `src/obsidian_mcp/path_utils.py`

**Purpose**: Tất cả path operations đều đi qua đây — ngăn path traversal, normalize paths.

**Responsibilities**:
- Validate input paths không vượt ra ngoài vault root (path traversal prevention — SECURITY-05)
- Normalize paths (strip `.`, `..`, trailing slashes)
- Convert giữa vault-relative và absolute paths
- Sanitize note names (loại bỏ ký tự invalid trong filenames)

---

## C-04: Note Reader

**File**: `src/obsidian_mcp/note_reader.py`

**Purpose**: Tất cả read operations trên vault.

**Responsibilities**:
- Đọc note content (raw markdown)
- Parse frontmatter YAML
- Extract wiki-links `[[...]]`
- Extract tags (`#tag`)
- List notes với optional filters (folder, tag, extension)
- Search notes (full-text grep)
- Resolve backlinks (scan vault cho references đến một note)
- Đọc `.canvas` files (JSON)

---

## C-05: Note Writer

**File**: `src/obsidian_mcp/note_writer.py`

**Purpose**: Tất cả write/mutation operations trên vault.

**Responsibilities**:
- Tạo note mới (với frontmatter)
- Update note content (replace hoặc append mode)
- Delete note (với path validation)
- Move/rename note (atomic: write new → verify → delete old)
- Create folder
- Delete folder (check empty trước)
- Update backlinks khi move note

---

## C-06: Advanced Features

**File**: `src/obsidian_mcp/advanced_features.py`

**Purpose**: Obsidian-specific advanced operations.

**Responsibilities**:
- Build graph data (nodes + edges từ tất cả notes và links)
- Get all tags với usage count
- Parse Dataview inline fields (`key:: value`)
- Resolve daily note path theo vault config (`daily-notes` plugin config)
- List attachments (non-markdown files)

---

## C-07: MCP Tools (Tool Handlers)

**File**: `src/obsidian_mcp/tools/`

**Purpose**: MCP tool definitions — thin wrappers gọi vào các components trên.

**Responsibilities**:
- Define tool names, descriptions, parameters (dùng `@mcp.tool()` decorator)
- Input validation trước khi gọi xuống layer dưới (SECURITY-05)
- Map exceptions sang MCP-compliant error responses (SECURITY-15)
- Không chứa business logic — chỉ delegate

**Sub-modules**:
- `tools/read_tools.py` — tools đọc
- `tools/write_tools.py` — tools ghi
- `tools/advanced_tools.py` — tools nâng cao

## Related
- [[application-design]]
- [[component-methods]]
- [[component-dependency]]
