# Spec: Cache PDF template trong PostgreSQL

- **Ngày:** 2026-06-29
- **Branch:** `feat/template-pdf-db`
- **Trạng thái:** Đã duyệt thiết kế, chờ viết plan

## 1. Bối cảnh & vấn đề

Template hành chính nằm dưới dạng `.doc/.docx` trong `Backend/data/templates/`.
Khi người dùng xem trước (`GET /api/templates/preview/<file>`), backend convert
Word → PDF qua LibreOffice/win32com/docx2pdf rồi cache ra đĩa
(`Backend/data/pdf_cache/`).

Trên production (Docker), cơ chế này **hỏng**:

1. `Backend/Dockerfile` **không cài LibreOffice**; Linux container không có
   Word/win32com → `pdf_converter.is_available()` = `False` → preview fallback
   ra file Word thô mà trình duyệt không xem inline được.
2. `Backend/.dockerignore` loại `data/pdf_cache/` → cache PDF đã commit trong
   git **không** được copy vào image.
3. Cache đĩa là ephemeral, mất sau mỗi lần deploy/rebuild.

Kết quả: preview PDF gần như không hoạt động trên prod.

**Yếu tố then chốt:** PostgreSQL là DB **external/shared** (qua `DB_HOST`), nên
dữ liệu trong DB sống sót qua mọi lần deploy và mọi container đọc được. Máy dev
(Windows) **có** engine convert; prod thì **không**. → Convert ở nơi có engine,
lưu kết quả vào DB, prod chỉ đọc.

## 2. Mục tiêu / phi mục tiêu

**Mục tiêu**
- PDF preview bền vững qua deploy, **không phụ thuộc LibreOffice trên prod**.
- Thay đổi tối thiểu, không đụng template gốc, không đổi Dockerfile/`.dockerignore`.

**Phi mục tiêu**
- Không quản lý template qua DB (upload/sửa bằng admin) — vẫn là file tĩnh.
- Không chuyển endpoint `download` sang DB (chỉ `preview`).
- Không giữ nhiều phiên bản PDF cho 1 template (1 PDF / filename).

## 3. Kiến trúc

Ba phần, ranh giới rõ ràng:

1. **Schema** — bảng `public.template_pdf_cache` (DDL idempotent trong `models/db.py`).
2. **Tầng truy cập DB** — module mới `services/pdf_cache_db.py` (chỉ I/O DB,
   không biết gì về convert).
3. **Đường preview** — `routes/templates_routes.py` đọc DB trước, write-through
   khi convert local.
4. **Seeding** — script `scripts/seed_pdf_cache.py` chạy ở máy có engine.

`pdf_converter.py` giữ nguyên (thuần file, không thêm phụ thuộc DB) để vẫn dùng
được trong script độc lập.

### 3.1 Schema

Thêm 1 khối DDL idempotent vào `init_db()` (theo đúng pattern các bảng hiện có):

```sql
CREATE TABLE IF NOT EXISTS public.template_pdf_cache (
    filename     VARCHAR(255) PRIMARY KEY,   -- tên template gốc, vd 'mau-...docx'
    content_hash VARCHAR(32)  NOT NULL,       -- MD5 nội dung template (phát hiện stale)
    pdf_data     BYTEA        NOT NULL,       -- bytes PDF đã convert
    size_bytes   INTEGER      NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

- Khóa chính `filename` → mỗi template đúng 1 bản PDF.
- `content_hash` = MD5 nội dung file template gốc → phát hiện template đã đổi.

### 3.2 Module `services/pdf_cache_db.py`

API (mọi hàm bọc `try/except`, lỗi DB → trả `None`/no-op + log warning, **không**
làm vỡ đường preview):

```python
def get_pdf(filename: str) -> bytes | None
def get_meta(filename: str) -> dict | None      # {'content_hash': str, 'size_bytes': int}
def put_pdf(filename: str, content_hash: str, pdf_bytes: bytes) -> bool   # upsert
```

`put_pdf` dùng `INSERT ... ON CONFLICT (filename) DO UPDATE` (cập nhật
`pdf_data`, `content_hash`, `size_bytes`, `updated_at`). Đọc/ghi BYTEA qua
`db.session` của SQLAlchemy. Cần app context (đã có khi chạy trong request hoặc
trong script bọc `app.app_context()`).

### 3.3 Sửa `preview_template` (templates_routes.py)

Với `.doc/.docx`, thứ tự mới:

1. Tính MD5 nội dung template gốc (`content_hash`).
2. **DB trước:** `get_meta(fn)`; nếu tồn tại và `content_hash` khớp →
   `get_pdf(fn)` → `send_file(BytesIO(pdf), mimetype='application/pdf')`.
   *(Đây là đường prod đi — không cần engine.)*
3. **DB miss/stale:** thử `word_to_pdf(fpath)` (máy dev). Nếu thành công →
   đọc bytes PDF → `put_pdf(fn, content_hash, bytes)` (write-through) →
   `send_file`.
4. **Fallback cũ giữ nguyên:** glob cache đĩa `<stem>_*.pdf` → cuối cùng trả
   file Word inline.

Nhánh PDF gốc (`ext == 'pdf'`) và `download` không đổi.

### 3.4 Seeding — `scripts/seed_pdf_cache.py`

- Chạy **một lần ở máy có engine** (dev Windows / hoặc bất kỳ host có LibreOffice).
- Lặp qua danh sách template (tái dùng `priority` list trong `templates_routes`
  hoặc quét toàn bộ `data/templates/`), với mỗi file: `word_to_pdf` → đọc bytes
  → `put_pdf`.
- Bọc `app.app_context()`; in tổng kết: số file seed, tổng dung lượng.
- Idempotent: chạy lại chỉ update bản đã đổi.

Ngoài script, write-through ở bước 3.3.3 khiến mỗi lần dev mở preview cũng tự
seed dần vào DB.

## 4. Luồng dữ liệu

```
[Dev/máy có engine]                          [Prod/không engine]
seed_pdf_cache.py / preview convert            GET /preview/<file>
        │ word_to_pdf                                  │
        │ put_pdf(bytes) ──────► Postgres ◄──────── get_pdf → send_file
                                (shared DB)
```

## 5. Xử lý lỗi & trường hợp biên

- **DB down:** mọi hàm `pdf_cache_db` trả `None`/no-op → preview tự rơi xuống
  nhánh convert/đĩa/Word. Không vỡ.
- **Template đổi nội dung:** hash lệch → máy có engine reconvert + update DB;
  prod phục vụ bản cũ tới khi chạy lại `seed_pdf_cache.py` (chấp nhận được —
  template hiếm đổi).
- **Dung lượng:** ~40 file × ~150KB ≈ 6MB trong Postgres — không đáng kể.
- **Path traversal:** `_safe_filename` hiện có giữ nguyên, áp dụng trước khi
  query DB.

## 6. Kiểm thử & nghiệm thu

- **Roundtrip:** `put_pdf` rồi `get_pdf`/`get_meta` trả đúng bytes/hash (verify
  qua script seed, cần DB thật).
- **Nghiệm thu thủ công:**
  1. Chạy `python scripts/seed_pdf_cache.py` ở máy dev.
  2. `SELECT count(*), sum(size_bytes) FROM public.template_pdf_cache;` → khớp số template.
  3. Tạm vô hiệu engine (đổi tên LibreOffice / chạy nơi không có Word) → gọi
     `GET /api/templates/preview/<file>.docx` → vẫn trả `application/pdf` (đi
     đúng nhánh DB).
- **Không hồi quy:** preview của file `.pdf` gốc và endpoint `download` vẫn hoạt động.

## 7. Phạm vi thay đổi (ước lượng)

| File | Thay đổi |
|---|---|
| `Backend/models/db.py` | +1 khối DDL `template_pdf_cache` |
| `Backend/services/pdf_cache_db.py` | mới, ~60 dòng |
| `Backend/routes/templates_routes.py` | sửa `preview_template` (DB-first + write-through) |
| `Backend/scripts/seed_pdf_cache.py` | mới, script seed |

Không đụng: template gốc, `Dockerfile`, `.dockerignore`, `pdf_converter.py`.
