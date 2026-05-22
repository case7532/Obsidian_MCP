# Context7 - Hướng dẫn sử dụng tối ưu

## Khi nào dùng Context7

- Cần tra cứu API, cú pháp, hoặc best practices của một thư viện/framework
- Cần code example chính xác theo phiên bản đang dùng
- Không chắc chắn về cách sử dụng một feature cụ thể

## Khi nào KHÔNG dùng

- Câu hỏi chung về logic, thuật toán, kiến trúc
- Đã biết rõ API cần dùng
- Thao tác với code hiện có trong project (dùng code tool thay thế)

## Quy trình 2 bước bắt buộc

```
Bước 1: resolve-library-id → Lấy library ID chính xác
Bước 2: query-docs → Tra cứu documentation với library ID đó
```

## Nguyên tắc tối ưu context

### 1. Query cụ thể, không chung chung

```
❌ "hooks"
❌ "auth"
✅ "How to set up authentication with JWT in Express.js"
✅ "React useEffect cleanup function examples"
✅ "Next.js App Router dynamic route params"
```

### 2. Giới hạn số lần gọi

- Tối đa **3 lần** `resolve-library-id` mỗi câu hỏi
- Tối đa **3 lần** `query-docs` mỗi câu hỏi
- Nếu không tìm được sau 3 lần → dùng kết quả tốt nhất có được

### 3. Chọn library theo tiêu chí ưu tiên

1. Tên khớp chính xác với query
2. Source Reputation: High > Medium > Low
3. Benchmark Score cao
4. Số Code Snippets nhiều

### 4. Tận dụng version cụ thể

Nếu project dùng version cố định, truyền version vào library ID:

```
/vercel/next.js/v14.3.0-canary.87
```

### 5. Kết hợp với code tool

- Dùng `code` tool để hiểu codebase hiện tại
- Dùng `context7` để tra cứu API/docs của thư viện bên ngoài
- Không dùng context7 để tìm hiểu code nội bộ project

## Ví dụ workflow thực tế

```
User: "Thêm middleware xác thực cho API route trong Next.js App Router"

1. resolve-library-id("Next.js", "middleware authentication App Router")
   → /vercel/next.js

2. query-docs("/vercel/next.js", "middleware authentication App Router route handler")
   → Nhận code examples + API reference

3. Áp dụng vào code project
```
