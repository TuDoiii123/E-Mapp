# E-Mapp Backend

Backend API cho **Cổng Dịch vụ Công Số tỉnh Thanh Hóa** — xác thực, tìm kiếm dịch vụ, đặt lịch hẹn, xếp hàng, chatbot RAG và voice AI.

---

## Cấu trúc thư mục

```
Backend/
├── server.py               # Điểm khởi động Flask
├── routes/                 # Blueprints API
├── models/                 # SQLAlchemy models + file JSON fallback
├── middleware/auth.py       # Xác thực JWT
├── services/               # Logic nghiệp vụ
├── RAG/                    # Chatbot AI (LangGraph + Gemini + ChromaDB)
├── SuggestProcedure/       # Gợi ý thủ tục (sentence-transformers)
├── ImageExtract/           # Trích xuất ảnh (Gemini Vision)
└── scripts/                # Seed data, import CSV, geocode...
```

---

## Cài đặt & Chạy

### 1. Môi trường ảo

```bash
cd Backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Tạo file `.env`

```env
# ── Bắt buộc ─────────────────────────────────────────────
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
PORT=8888
FLASK_ENV=development

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=models/gemini-2.5-flash-lite

# ── Tùy chọn ─────────────────────────────────────────────
# PostgreSQL (nếu không cấu hình → dùng file JSON)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=public_services
DB_USER=postgres
DB_PASSWORD=postgres

# Google Cloud TTS/STT (nếu dùng voice)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Bật per-request HTTP log
# LOG_HTTP=1
```

### 3. Khởi động

```bash
python server.py
```

Server chạy tại `http://localhost:8888`. Kiểm tra: `http://localhost:8888/api/health`

---

## PostgreSQL (Tùy chọn)

Nếu không cấu hình PostgreSQL, backend tự động dùng file JSON trong `data/` — hoàn toàn bình thường.

### Tạo database

```bash
psql -U postgres
```
```sql
CREATE DATABASE public_services;
GRANT ALL PRIVILEGES ON DATABASE public_services TO postgres;
\q
```

### Khởi tạo schema

```bash
python scripts/init_db.py
```

> **Lưu ý:** Nếu thấy `Database initialization skipped` khi khởi động → backend đang dùng file JSON, không phải lỗi.

---

## Hệ thống RAG (Chatbot AI)

### Tải model embedding (nếu chưa có)

```bash
cd Backend/RAG
python -c "
from huggingface_hub import snapshot_download
snapshot_download('AITeamVN/Vietnamese_Embedding', local_dir='models/Vietnamese_Embedding', ignore_patterns=['*.onnx','onnx/*'])
"
```

### Tạo / rebuild vector database

```bash
cd Backend/RAG
python create_vecto_db/create_faq_db.py      # FAQ chung
python create_vecto_db/embed_thanhhoa.py     # Dịch vụ công Thanh Hóa
```

Vector DB lưu tại `RAG/chroma_db/` với 3 collection: `thanhhoa_congan`, `thanhhoa_ubnd`, `thanhhoa_diadiem`.

### Lịch sử chat (SQL Server — tùy chọn)

Chỉnh `RAG/connect_SQL/config.json`. Nếu để trống, RAG vẫn hoạt động, chỉ không lưu lịch sử.

---

## Seed dữ liệu

```bash
python scripts/seed_data.py                          # Dữ liệu mẫu
python scripts/create_admin.py                       # Tài khoản admin
python scripts/import_dichvu_to_public_services.py   # Import DVC từ CSV
```

> **Đăng ký demo:** OTP mặc định là `123456`.

---

## API Endpoints

### Xác thực

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/register` | Đăng ký |
| POST | `/api/auth/login` | Đăng nhập |
| GET | `/api/auth/profile` | Thông tin người dùng |
| PUT | `/api/auth/profile` | Cập nhật hồ sơ |

### Dịch vụ công

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/services/` | Danh sách |
| GET | `/api/services/search?q=` | Tìm kiếm |
| GET | `/api/services/nearby?lat=&lng=&radius=` | Gần vị trí |
| GET | `/api/services/categories/list` | Danh mục |

### Đặt lịch hẹn

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/appointments` | Tạo lịch hẹn |
| GET | `/api/appointments/upcoming` | Lịch sắp tới |
| GET | `/api/appointments/all` | Tất cả lịch |

### Chatbot RAG

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/rag/chat` | Hỏi đáp (sync) |
| POST | `/api/rag/chat/stream` | Hỏi đáp (SSE stream) |
| GET | `/api/rag/sessions` | Lịch sử phiên |
| POST | `/api/suggest-procedure` | Gợi ý thủ tục |

### Voice AI

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/voice/stt` | Speech-to-Text |
| POST | `/api/voice/tts` | Text-to-Speech |
| POST | `/api/voice/dialog` | Hội thoại đặt lịch |
| POST | `/api/voice/appointments/auto-create` | Tự động đặt lịch từ giọng nói |

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `password authentication failed` | Sai credentials DB | Kiểm tra `DB_USER`/`DB_PASSWORD` trong `.env` |
| `database "public_services" does not exist` | Chưa tạo DB | Chạy `psql -U postgres -c "CREATE DATABASE public_services;"` |
| `EADDRINUSE` / `Address already in use` | Port 8888 bị chiếm | Đổi `PORT` trong `.env` hoặc tắt tiến trình đang dùng port đó |
| `Failed to fetch` ở Frontend | Backend chưa chạy hoặc sai URL | Kiểm tra `http://localhost:8888/api/health` và `VITE_API_URL` trong Frontend |
| `JWT_SECRET chưa được đặt` | Dùng secret mặc định | Đặt `JWT_SECRET` thực sự trong `.env` trước khi deploy |

---

## Lưu ý

- File upload lưu local tại `uploads/` — chưa tích hợp cloud storage.
- VNeID verification hiện là **mock demo** — chưa kết nối API thật.
- Voice STT/TTS yêu cầu Google Cloud credentials; nếu không có thì dùng mock: `VOICE_STT_DEV_MOCK=1`.
