# E-Mapp — Dịch vụ công số tỉnh Thanh Hóa

> Nền tảng dịch vụ hành chính công trực tuyến: nộp hồ sơ, đặt lịch hẹn, lấy số xếp hàng, tra cứu thủ tục, trợ lý AI (chatbot RAG + giọng nói) và bản đồ cơ quan hành chính.

**Repository:** https://github.com/TuDoiii123/E-Mapp

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng chính](#tính-năng-chính)
- [Kiến trúc](#kiến-trúc)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cài đặt & Chạy](#cài-đặt--chạy)
  - [1. Chạy nhanh bằng Docker Compose](#1-chạy-nhanh-bằng-docker-compose)
  - [2. Chạy thủ công (dev)](#2-chạy-thủ-công-dev)
- [Biến môi trường](#biến-môi-trường)
- [RAG & mô hình AI](#rag--mô-hình-ai)
- [Triển khai (Deploy)](#triển-khai-deploy)
- [Đóng góp](#đóng-góp)

---

## Tổng quan

**E-Mapp** là cổng dịch vụ công số giúp người dân tương tác với các thủ tục hành chính một cách trực tuyến, đồng thời cung cấp công cụ quản trị cho cán bộ. Hệ thống gồm một **frontend React** (web/app), một **backend Flask** với REST API + WebSocket, và một **module AI** (RAG chatbot, trợ lý giọng nói, trích xuất tài liệu, dự báo hàng đợi).

## Tính năng chính

| Nhóm | Mô tả |
|------|-------|
| **Tài khoản** | Đăng ký / đăng nhập bằng JWT, phân quyền người dân & cán bộ |
| **Hồ sơ trực tuyến** | Nộp & theo dõi hồ sơ theo luồng trạng thái (draft → submitted → in_review → approved/rejected/more_info) kèm lịch sử |
| **Tra cứu thủ tục** | Danh mục thủ tục hành chính theo lĩnh vực (dân sự, doanh nghiệp, đất đai…) |
| **Đặt lịch hẹn** | Đặt lịch theo khung giờ, hiển thị bằng FullCalendar |
| **Xếp hàng & dự báo** | Lấy số thứ tự thời gian thực qua WebSocket + dự báo thời gian chờ bằng mô hình LSTM |
| **Chatbot RAG** | Hỏi đáp tiếng Việt dựa trên ChromaDB + embedding tiếng Việt + Gemini |
| **Trợ lý giọng nói** | STT/TTS (Google Cloud) + hội thoại đa bước để đặt lịch bằng giọng nói |
| **Trích xuất tài liệu** | Đọc thông tin từ ảnh/PDF giấy tờ (Gemini Vision) |
| **Điền biểu mẫu** | Sinh & cache bản xem trước PDF của biểu mẫu (lưu trong PostgreSQL) |
| **Bản đồ** | Bản đồ cơ quan hành chính (Leaflet) + tính khoảng cách |
| **Thông báo** | Push notification qua Firebase |
| **Đánh giá** | Đánh giá chất lượng dịch vụ |

## Kiến trúc

```
┌────────────────┐      REST /api/*  +  WebSocket /ws/*      ┌────────────────────┐
│   Frontend     │ ─────────────────────────────────────────▶│   Backend (Flask)   │
│  React + TS    │                                            │   server.py :8888   │
│  (Rsbuild)     │◀───────────────────────────────────────── │   17 blueprints     │
└────────────────┘                                            └─────────┬───────────┘
                                                                        │
                          ┌────────────────────┬──────────────────┬─────┴───────────┐
                          ▼                    ▼                  ▼                 ▼
                   ┌────────────┐      ┌──────────────┐   ┌──────────────┐  ┌──────────────┐
                   │ PostgreSQL │      │  RAG / Chroma │   │ Google Cloud │  │   Firebase   │
                   │            │      │  + Gemini     │   │  STT / TTS   │  │  (push noti) │
                   └────────────┘      └──────────────┘   └──────────────┘  └──────────────┘
```

## Công nghệ sử dụng

**Frontend**
- React 19 + TypeScript, đóng gói bằng **Rsbuild**
- Tailwind CSS 4, HeroUI, Lucide icons, Framer Motion
- Leaflet (bản đồ), FullCalendar (lịch hẹn), Recharts (biểu đồ)
- Firebase (push notification)

**Backend**
- Python **Flask 3** (`server.py`, cổng `8888`), REST API tiền tố `/api/*`
- **PostgreSQL** qua `psycopg2` + Flask-SQLAlchemy
- Xác thực **JWT** (PyJWT) + bcrypt
- WebSocket qua `flask-sock` (`/ws/queue/<agency_id>`)
- **RAG:** ChromaDB + `sentence-transformers` (Vietnamese_Embedding) + Gemini
- **Voice:** Google Cloud Speech-to-Text / Text-to-Speech
- **Tài liệu:** PyMuPDF, python-docx
- **Dự báo hàng đợi:** PyTorch (LSTM)

**Hạ tầng**
- Docker & Docker Compose (frontend nginx, backend, Cloudflare Tunnel, Watchtower)
- GitHub Actions (CI/CD), Vercel (frontend), Oracle Cloud ARM (backend)

## Cấu trúc thư mục

```
E-Mapp/
├── Frontend/                 # React + TypeScript (Rsbuild)
│   ├── src/
│   ├── Dockerfile
│   └── vercel.json
├── Backend/                  # Flask API
│   ├── server.py             # Entry point (cổng 8888)
│   ├── routes/               # Các blueprint API (auth, applications, rag, voice, queue…)
│   ├── services/             # Business logic (appointments, queue_forecast, pdf_cache…)
│   ├── RAG/                  # Chatbot RAG: ChromaDB, agent, embedding, prompt
│   ├── SuggestProcedure/     # Gợi ý thủ tục (mô hình fine-tuned)
│   ├── ImageExtract/         # Trích xuất thông tin từ ảnh/giấy tờ
│   ├── middleware/           # Auth, logging…
│   └── requirements.txt
├── docs/                     # Tài liệu, UML
├── docker-compose.yml
└── .env.example
```

## Cài đặt & Chạy

### 1. Chạy nhanh bằng Docker Compose

```bash
git clone https://github.com/TuDoiii123/E-Mapp.git
cd E-Mapp

cp .env.example .env        # rồi điền các giá trị thật
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8888/api
- Health check: http://localhost:8888/api/health

### 2. Chạy thủ công (dev)

**Backend**

```bash
cd Backend
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

pip install -r requirements.txt
python server.py             # chạy tại http://127.0.0.1:8888
```

**Frontend**

```bash
cd Frontend
npm install
npm run dev                  # chế độ phát triển
npm run build                # build production
```

## Biến môi trường

Sao chép `.env.example` thành `.env` ở thư mục gốc và điền giá trị:

```dotenv
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=

# JWT
JWT_SECRET=change-this-to-a-long-random-string

# Gemini AI
GEMINI_API_KEY=
GEMINI_MODEL_NAME=models/gemini-2.5-flash
GEMINI_MODEL_RAG=gemini-2.5-flash

# CORS (thêm domain thật khi deploy)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Cloudflare Tunnel
TUNNEL_TOKEN=
```

> Không commit file `.env`. Dùng Google Application Credentials nếu bật tính năng giọng nói (Google Cloud STT/TTS).

## RAG & mô hình AI

Module RAG nằm trong `Backend/RAG/`. Mô hình embedding **không kèm theo repo** để giảm dung lượng — tải từ Hugging Face:

- Vietnamese Embedding: https://huggingface.co/AITeamVN/Vietnamese_Embedding

Vector store dùng **ChromaDB** (thư mục cục bộ, không commit). Script tạo DB từ FAQ nằm trong `Backend/RAG/create_vecto_db/`.

## Triển khai (Deploy)

- **Frontend** → Vercel (cấu hình `Frontend/vercel.json`, workflow `.github/workflows/vercel.yml`)
- **Backend** → Oracle Cloud ARM qua Docker, cập nhật tự động bằng Watchtower; expose qua Cloudflare Tunnel
- **CI/CD** → GitHub Actions (`.github/workflows/`)

## Đóng góp

1. Fork & tạo nhánh từ `master`
2. Commit theo quy ước (`feat:`, `fix:`, `chore:`…)
3. Mở Pull Request về https://github.com/TuDoiii123/E-Mapp

