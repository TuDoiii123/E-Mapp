# E-Mapp Backend

Backend API cho ứng dụng **Dịch vụ công số tỉnh Thanh Hóa** — hỗ trợ tìm kiếm dịch vụ công, đặt lịch hẹn, xác thực người dùng và chatbot RAG hỏi đáp thủ tục hành chính.

---

## Kiến trúc tổng quan

```
Backend/
├── server.py               # Flask app chính – khởi động server
├── routes/                 # Các blueprint API
│   ├── auth_routes.py      # Đăng ký / đăng nhập
│   ├── services_routes.py  # Tìm kiếm dịch vụ công
│   ├── applications_routes.py  # Nộp hồ sơ
│   └── admin_routes.py     # Quản trị
├── models/                 # Data models (PostgreSQL + file JSON fallback)
│   ├── db.py               # Kết nối PostgreSQL
│   ├── user.py             # Model người dùng
│   └── public_service.py   # Model dịch vụ công
├── middleware/
│   └── auth.py             # Xác thực JWT
├── services/
│   ├── distance.py         # Tính khoảng cách Haversine
│   └── vneid.py            # Tích hợp VNeID (demo)
├── RAG/                    # Hệ thống chatbot AI (LangGraph + Gemini + ChromaDB)
│   ├── agent_core/         # LangGraph graph và các node
│   ├── tools/              # RAG tool (ChromaDB search)
│   ├── utils/              # LLM wrapper (Gemini)
│   ├── connect_SQL/        # Kết nối SQL Server (lịch sử hội thoại)
│   ├── create_vecto_db/    # Script tạo vector database
│   └── models/             # Mô hình embedding AITeamVN/Vietnamese_Embedding
├── SuggestProcedure/       # Gợi ý thủ tục hành chính (sentence-transformers)
├── ImageExtract/           # Trích xuất thông tin từ ảnh (Gemini Vision)
└── scripts/                # Tiện ích: seed data, import CSV, geocode...
```

---

## Yêu cầu

- Python 3.10+
- PostgreSQL (tùy chọn — nếu không có thì dùng file JSON)
- SQL Server + ODBC Driver 17 (tùy chọn — lưu lịch sử chat RAG)

---

## Cài đặt

### 1. Tạo môi trường ảo và cài thư viện

```bash
cd Backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Cấu hình file `.env`

Tạo file `.env` tại thư mục `Backend/`:

```env
# ── Bắt buộc ──────────────────────────────────────
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d

# Google Gemini API (dùng 1 key hoặc 3 key riêng cho từng LLM)
GOOGLE_API_KEY=your_gemini_api_key

# Nếu muốn dùng 3 key riêng biệt (tùy chọn):
# GOOGLE_API_KEY_1=key_for_analyzer
# GOOGLE_API_KEY_2=key_for_synthesizer
# GOOGLE_API_KEY_3=key_for_summarizer

# ── Tùy chọn ──────────────────────────────────────
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emapp
DB_USER=postgres
DB_PASSWORD=your_db_password

# Gemini Voice AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=models/gemini-2.5-flash-lite

# Google Cloud TTS/STT (nếu dùng voice)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### 3. Cấu hình SQL Server (tùy chọn — lưu lịch sử chat)

Chỉnh sửa `RAG/connect_SQL/config.json`:

```json
{
  "connection": {
    "server": "localhost",
    "database": "emapp_chat",
    "username": "sa",
    "password": "your_password"
  }
}
```

Nếu để trống, hệ thống RAG vẫn hoạt động bình thường — chỉ không lưu lịch sử chat.

### 4. Khởi động server

```bash
python server.py
```

Server chạy tại: `http://localhost:8888`

---

## Hệ thống RAG (Chatbot AI)

### Mô hình embedding

Model `AITeamVN/Vietnamese_Embedding` được đặt tại:
```
RAG/models/Vietnamese_Embedding/
```

Nếu chưa có, tải về bằng lệnh:

```bash
cd Backend/RAG
python -c "
from huggingface_hub import snapshot_download
snapshot_download('AITeamVN/Vietnamese_Embedding', local_dir='models/Vietnamese_Embedding', ignore_patterns=['*.onnx','onnx/*'])
"
```

### Tạo vector database

Vector DB được tạo sẵn tại `RAG/chroma_db/chroma_db_faqs/`.

Để rebuild từ file CSV dữ liệu FAQ:

```bash
cd Backend/RAG
python create_vecto_db/create_faq_db.py
```

Để embed dữ liệu dịch vụ công Thanh Hóa:

```bash
cd Backend/RAG
python create_vecto_db/embed_thanhhoa.py
```

Kết quả lưu tại `RAG/chroma_db/thanhhoa/` với 3 collection:
- `thanhhoa_congan` — 159 thủ tục hành chính Công an
- `thanhhoa_ubnd` — Dịch vụ công UBND
- `thanhhoa_diadiem` — Địa điểm DVC

### Luồng xử lý chatbot

```
Câu hỏi người dùng
    ↓
[user_input_node]   — nhận input
    ↓
[role_manager]      — load prompt + lịch sử hội thoại
    ↓
[task_analyzer]     — Gemini phân tích + chọn tool
    ↓
[tool_executor]     — gọi search_project_documents (ChromaDB)
    ↓
[llm_response]      — Gemini tổng hợp câu trả lời
```

---

## API Endpoints chính

### Xác thực

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/register` | Đăng ký tài khoản |
| POST | `/api/auth/login` | Đăng nhập |
| GET | `/api/auth/profile` | Lấy thông tin người dùng |
| PUT | `/api/auth/profile` | Cập nhật hồ sơ |

**Đăng ký (demo):** OTP mặc định là `123456`.

### Dịch vụ công

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/services/` | Danh sách dịch vụ |
| GET | `/api/services/search?q=...` | Tìm kiếm |
| GET | `/api/services/nearby?lat=&lng=&radius=` | Tìm gần vị trí |
| GET | `/api/services/<id>` | Chi tiết dịch vụ |
| GET | `/api/services/categories/list` | Danh mục |

### Đặt lịch hẹn

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/appointments` | Tạo lịch hẹn |
| GET | `/api/appointments/by-date?agencyId=&date=` | Lịch theo ngày |
| GET | `/api/appointments/upcoming` | Lịch sắp tới |
| GET | `/api/appointments/all` | Tất cả lịch |

### Chatbot RAG

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/chat` | Gửi câu hỏi hành chính |

```json
// Request
{ "message": "Làm CCCD cần những giấy tờ gì?", "session_id": "abc123" }

// Response
{ "success": true, "data": { "answer": "...", "session_id": "abc123" } }
```

### Voice AI

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/voice/stt` | Speech-to-Text (Google Cloud) |
| POST | `/api/voice/tts` | Text-to-Speech |
| POST | `/api/voice/dialog` | Hội thoại đặt lịch |
| POST | `/api/voice/appointments/auto-create` | Tự động đặt lịch từ voice |

### Gợi ý thủ tục

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/suggest?q=...&top_k=4` | Gợi ý thủ tục hành chính |

---

## Seed dữ liệu

```bash
# Seed dữ liệu dịch vụ công mẫu
python scripts/seed_data.py

# Tạo tài khoản admin
python scripts/create_admin.py

# Import dữ liệu DVC từ CSV
python scripts/import_dichvu_to_public_services.py
```

---

## Lưu ý

- Dữ liệu người dùng được lưu vào **PostgreSQL** (nếu cấu hình) hoặc file `data/users.json` (fallback).
- File upload được lưu local tại `uploads/` — chưa tích hợp cloud storage.
- VNeID verification hiện là **demo mock** — chưa kết nối API thật.
- Voice STT/TTS yêu cầu **Google Cloud credentials** — nếu không có thì dùng mock mode (`VOICE_STT_DEV_MOCK=1`).
