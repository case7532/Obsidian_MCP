# Business Overview

## Business Description

**obsidian-mcp** là một MCP server (Model Context Protocol) cho phép các AI assistant (Claude, Kiro, v.v.) tương tác trực tiếp với Obsidian vault — kho lưu trữ ghi chú Markdown của người dùng. Hệ thống cung cấp một lớp abstraction an toàn giữa AI model và filesystem, cho phép đọc, viết, tìm kiếm và quản lý ghi chú thông qua giao thức MCP chuẩn hóa.

**Version hiện tại**: 0.1.1 (branch `dev` có thêm smart folder index + BM25 search)

## Business Transactions

| # | Giao dịch | Mô tả |
|---|-----------|-------|
| BT-01 | Read Note | Đọc nội dung và frontmatter YAML của một ghi chú |
| BT-02 | List Notes | Liệt kê ghi chú theo folder hoặc tag |
| BT-03 | Search Notes (FTS) | Tìm kiếm toàn văn bản với excerpts |
| BT-04 | BM25 Search | Tìm kiếm thông minh đa trang, ranked theo relevance, kết quả JSON |
| BT-05 | Get Metadata | Lấy metadata (frontmatter, tags, kích thước, ngày tháng) |
| BT-06 | Get Backlinks | Tìm tất cả ghi chú liên kết đến một ghi chú |
| BT-07 | Get Outgoing Links | Liệt kê tất cả wiki-links trong một ghi chú |
| BT-08 | Read Canvas | Đọc file canvas Obsidian dưới dạng JSON |
| BT-09 | Create Note | Tạo ghi chú mới với định dạng chuẩn + tự động cập nhật folder index |
| BT-10 | Update Note | Cập nhật nội dung ghi chú (replace hoặc append) |
| BT-11 | Delete Note | Xóa ghi chú |
| BT-12 | Move Note | Di chuyển/đổi tên ghi chú, tự động cập nhật backlinks |
| BT-13 | Create Folder | Tạo folder + tự động sinh _index.md |
| BT-14 | Delete Folder | Xóa folder (có cơ chế bảo vệ non-empty) |
| BT-15 | Get Graph Data | Xây dựng đồ thị liên kết toàn vault |
| BT-16 | Get All Tags | Lấy tất cả tags với số lượng sử dụng |
| BT-17 | Get Dataview Fields | Đọc Dataview inline fields (`key:: value`) |
| BT-18 | Get Daily Note | Lấy daily note theo ngày, tích hợp cấu hình plugin |
| BT-19 | List Attachments | Liệt kê file đính kèm (ảnh, PDF, ...) |

## Business Dictionary

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| **Vault** | Thư mục gốc chứa toàn bộ ghi chú Obsidian; phải có `.obsidian/` directory |
| **Note** | File Markdown (`.md`) trong vault |
| **Canvas** | File `.canvas` — sơ đồ trực quan của Obsidian |
| **Frontmatter** | Block YAML ở đầu file ghi chú (`---` ... `---`) chứa metadata |
| **Wiki-link** | Cú pháp liên kết nội bộ `[[tên-ghi-chú]]` của Obsidian |
| **Backlink** | Ghi chú khác có wiki-link trỏ đến ghi chú hiện tại |
| **Tag** | Nhãn phân loại, có trong frontmatter hoặc inline `#tag` |
| **Vault-relative path** | Đường dẫn tương đối từ gốc vault, ví dụ `folder/note.md` |
| **MCP Tool** | Hàm được expose qua MCP protocol để AI model gọi |
| **_index.md** | File tổng hợp tự động sinh khi tạo folder mới |
| **BM25** | Thuật toán ranking tìm kiếm (Best Match 25) — cải tiến TF-IDF |
| **Dataview field** | Trường dữ liệu inline `key:: value` của plugin Dataview |

## Component Level Business Descriptions

### NoteReader
- **Purpose**: Cung cấp tất cả hoạt động đọc trên vault
- **Responsibilities**: Parse frontmatter/body, full-text search, BM25 search, backlink resolution, tag extraction, wiki-link parsing, canvas parsing

### NoteWriter
- **Purpose**: Cung cấp tất cả hoạt động ghi/thay đổi trên vault
- **Responsibilities**: Tạo/cập nhật/xóa/di chuyển ghi chú, quản lý folder index, cập nhật backlinks khi rename

### AdvancedFeatures
- **Purpose**: Tính năng nâng cao không phải CRUD cơ bản
- **Responsibilities**: Graph data, tag aggregation, Dataview parsing, daily note lookup, attachment listing

### VaultConfig
- **Purpose**: Validate và cung cấp truy cập vault path
- **Responsibilities**: Validate `.obsidian/` existence, resolve paths, convert relative/absolute

### PathUtils
- **Purpose**: Bảo mật filesystem — ngăn path traversal
- **Responsibilities**: safe_vault_path (boundary check), sanitize filename, normalize path, markdown/canvas detection

### MCP Server (FastMCP)
- **Purpose**: Entry point — expose tools qua MCP stdio transport
- **Responsibilities**: Khởi tạo components, đăng ký tools, handle CLI args và env vars
