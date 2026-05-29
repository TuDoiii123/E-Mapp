# Deployment Design: Docker Compose + Watchtower + Cloudflare Tunnel

**Date:** 2026-05-29  
**Project:** E-Mapp — Dịch vụ công số tỉnh Thanh Hóa  
**Stack:** React (rsbuild) + Python FastAPI + SQL Server (native Windows)

---

## Goal

Deploy E-Mapp lên máy Windows 11 cá nhân (8GB RAM), truy cập được từ internet, tự động deploy khi push code lên GitHub.

## Architecture

```
[Dev push lên GitHub master]
        ↓
[GitHub Actions: build image → push Docker Hub]
        ↓
[Watchtower (chạy trên máy): poll Docker Hub mỗi 5 phút]
        ↓
[Phát hiện image mới → pull & docker compose restart]
        ↓
[Cloudflare Tunnel: route domain → localhost]
        ↓
[Người dùng truy cập qua domain]
```

## Components

### 1. Dockerfiles

**Frontend** (`Frontend/Dockerfile`):
- Stage 1: Node 20 build React app với rsbuild
- Stage 2: nginx:alpine serve static files từ `/usr/share/nginx/html`
- Expose port 80

**Backend** (`Backend/Dockerfile`):
- Base: python:3.11-slim
- Cài dependencies từ `requirements.txt`
- Chạy `uvicorn server:app --host 0.0.0.0 --port 8888`
- Expose port 8888

### 2. docker-compose.yml (root)

Services:
- `frontend`: image `dockerhub-user/emapp-frontend:latest`, port 3000→80
- `backend`: image `dockerhub-user/emapp-backend:latest`, port 8888→8888
- `cloudflared`: image `cloudflare/cloudflared:latest`, tunnel đến Cloudflare
- `watchtower`: image `containrrr/watchtower`, poll interval 300s, chỉ watch `frontend` và `backend`

**PostgreSQL**: KHÔNG containerize — backend kết nối qua `host.docker.internal:5432` (PostgreSQL 15 đang chạy native Windows). SQL Server trên máy là của phần mềm khác (MISA, Buitu), không liên quan đến E-Mapp.

### 3. GitHub Actions (`.github/workflows/deploy.yml`)

Trigger: `push` trên branch `master`

Steps:
1. Checkout code
2. Login Docker Hub (dùng GitHub Secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`)
3. Build & push `emapp-frontend:latest`
4. Build & push `emapp-backend:latest`

### 4. Cloudflare Tunnel

- Tạo tunnel trên Cloudflare Dashboard → lấy tunnel token
- `cloudflared` container nhận token qua env var
- Route:
  - `emapp.yourdomain.vn` → `http://frontend:80`
  - `api.emapp.yourdomain.vn` → `http://backend:8888`
- HTTPS tự động qua Cloudflare (không cần cấu hình SSL thêm)

### 5. Watchtower

- Chạy dưới dạng container trong docker-compose
- Poll Docker Hub mỗi 5 phút
- Khi phát hiện image mới: pull → recreate container tương ứng
- Chỉ watch `frontend` và `backend` (không restart `cloudflared`, `watchtower`)

## Environment Variables

**Backend** (`.env` file, không commit lên Git):
```
DB_HOST=host.docker.internal
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_pg_password
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_gemini_key
CORS_ORIGINS=https://emapp.yourdomain.vn
```

**Frontend** (build-time env, baked vào image lúc GitHub Actions chạy):
```
VITE_API_URL=https://api.emapp.yourdomain.vn
VITE_GOOGLE_MAPS_API_KEY=...
```

## Prerequisites (cần chuẩn bị trước)

| # | Việc | Ghi chú |
|---|---|---|
| 1 | Cài Docker Desktop cho Windows | docker.com/products/docker-desktop |
| 2 | Tạo tài khoản Docker Hub | hub.docker.com |
| 3 | Tạo tài khoản Cloudflare | cloudflare.com |
| 4 | Mua domain `.vn` hoặc `.io.vn` | NIC.vn ~100-200k/năm |
| 5 | Thêm domain vào Cloudflare (đổi nameserver) | Cloudflare hướng dẫn |

## RAM Estimate (sau khi deploy)

| Thành phần | RAM |
|---|---|
| Windows 11 | ~3GB |
| PostgreSQL (native) | đã chạy, không tốn thêm |
| Frontend container (nginx) | ~50MB |
| Backend container (Flask + PyTorch CPU) | ~1–1.5GB |
| Cloudflared + Watchtower | ~100MB |
| **Tổng thêm vào** | **~1.5–2GB** — an toàn trong 8GB |

> **Lưu ý:** PyTorch phải cài bản CPU-only trong Dockerfile (`--index-url https://download.pytorch.org/whl/cpu`), không thì image sẽ ~4GB.

## Security Notes

- SQL Server password không commit lên Git (dùng `.env` + `.gitignore`)
- Cloudflare Tunnel không cần mở port firewall nào
- Docker Hub token dùng GitHub Secrets, không hardcode
- Backend nên bật CORS chỉ cho domain chính thức

## Out of Scope

- SSL certificate (Cloudflare lo)
- Load balancing / horizontal scaling
- Database backup automation
- Monitoring / alerting
