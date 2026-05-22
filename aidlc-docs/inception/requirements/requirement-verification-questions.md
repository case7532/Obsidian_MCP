# Requirement Verification Questions

> Câu hỏi làm rõ yêu cầu ban đầu và câu trả lời của người dùng.

## Contents
- [Question 1](#question-1)
- [Question 2](#question-2)
- [Question 3](#question-3)
- [Question 4](#question-4)
- [Question 5](#question-5)
- [Question 6](#question-6)
- [Question 7](#question-7)
- [Question 8 — Extension: Security Baseline](#question-8-—-extension-security-baseline)
- [Question 9 — Extension: SBV Circular 64/2024/TT-NHNN Compliance](#question-9-—-extension-sbv-circular-642024tt-nhnn-compliance)
- [Question 10 — Extension: Document Consistency](#question-10-—-extension-document-consistency)
- [Question 11 — Extension: Property-Based Testing](#question-11-—-extension-property-based-testing)

Vui lòng trả lời các câu hỏi dưới đây bằng cách điền chữ cái vào sau thẻ `[Answer]:`.
Nếu không có lựa chọn nào phù hợp, chọn "Other" và mô tả sau thẻ `[Answer]:`.

---

## Question 1
Loại MCP (Model Context Protocol) bạn muốn xây dựng cho Obsidian là gì?

A) MCP Server — cho phép AI (Claude, v.v.) đọc/ghi notes, search vault, quản lý files trong Obsidian
B) MCP Client/Plugin — plugin Obsidian gọi vào AI qua MCP protocol
C) Cả hai — vừa server vừa client integration
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 2
Những tính năng cốt lõi nào bạn muốn MCP này hỗ trợ?

A) Chỉ đọc — search notes, đọc nội dung, lấy metadata (tags, links, frontmatter)
B) Đọc + Ghi cơ bản — tạo note mới, cập nhật nội dung note
C) Full CRUD — đọc, tạo, cập nhật, xóa notes, quản lý folders, attachments
D) Full CRUD + Advanced — bao gồm cả graph traversal, backlinks, canvas, templates
E) Other (please describe after [Answer]: tag below)

[Answer]: D

---

## Question 3
Ngôn ngữ/runtime bạn muốn dùng để implement MCP server?

A) TypeScript/Node.js (phổ biến nhất cho MCP, có SDK chính thức)
B) Python (có SDK chính thức, quen thuộc cho data/AI workflows)
C) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 4
Obsidian vault sẽ được truy cập như thế nào?

A) Local filesystem — vault nằm trên máy local, MCP server chạy local
B) Remote/network — vault trên NAS, cloud sync (iCloud, Dropbox), truy cập qua network
C) Cả hai — hỗ trợ cả local và remote
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 5
Mức độ bảo mật/authentication bạn cần?

A) Không cần auth — chỉ dùng cá nhân, local only
B) API key đơn giản — bảo vệ MCP server bằng token
C) OAuth / multi-user — nhiều người dùng với phân quyền riêng biệt
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6
AI client nào sẽ kết nối tới MCP server này?

A) Claude Desktop (Anthropic)
B) Cursor / các IDE AI
C) Nhiều client — phải tương thích chuẩn MCP chung
D) Other (please describe after [Answer]: tag below)

[Answer]: D - kiro CLI

---

## Question 7
Bạn có muốn hỗ trợ Obsidian-specific features không?

A) Không — chỉ cần đọc/ghi plain markdown files
B) Có — cần hỗ trợ: wiki-links [[...]], tags, frontmatter YAML, dataview queries
C) Có — hỗ trợ thêm: backlinks graph, canvas files, plugins data (Dataview, Tasks, v.v.)
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 8 — Extension: Security Baseline
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 9 — Extension: SBV Circular 64/2024/TT-NHNN Compliance
Should Circular 64 (Open API in Banking Sector) compliance rules be enforced for this project?

A) Yes — enforce all C64 rules (required for Open Banking / e-wallet projects)
B) No — skip Circular 64 rules (only for projects not involving Open API banking)

[Answer]: B

---

## Question 10 — Extension: Document Consistency
Should back-propagation consistency rules be enforced for this project?

A) Yes — automatically check upstream document impact whenever a document is updated (recommended for multi-unit projects)
B) No — skip automatic consistency checks (suitable for simple, single-unit projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 11 — Extension: Property-Based Testing
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints
B) Partial — enforce PBT rules only for pure functions and serialization round-trips
C) No — skip all PBT rules (suitable for simple CRUD or thin integration layers)
X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

Khi đã trả lời xong tất cả, hãy cho tôi biết để tôi tiếp tục phân tích.

## Related
- [[requirements]]
