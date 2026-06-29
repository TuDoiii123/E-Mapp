# Hướng dẫn deploy: Backend → Oracle Always Free, Frontend → Vercel

- **Ngày:** 2026-06-29
- **Branch:** `feat/deploy-oracle-vercel`

Mục tiêu: backend (Flask + RAG/torch + ChromaDB) chạy free vĩnh viễn trên
Oracle Cloud Always Free (ARM Ampere A1), frontend (rsbuild/React) chạy trên
Vercel.

## Thay đổi trong repo (đã làm)

- `Backend/Dockerfile`: cài torch theo kiến trúc — x86_64 dùng index CPU của
  PyTorch, ARM (aarch64) cài từ PyPI → build được trên Oracle Ampere A1.
- `Frontend/vercel.json`: build bằng rsbuild (`npm run build`, output `build/`),
  SPA rewrite mọi route → `/index.html`.
- CORS: **không sửa code** — `server.py` đã đọc `CORS_ORIGINS` từ env. Chỉ cần
  thêm domain Vercel vào biến này (xem bước CORS).

---

## Phần A — Backend trên Oracle Always Free

### A1. Tạo VM
1. Đăng ký https://www.oracle.com/cloud/free/ (cần thẻ để verify, không bị trừ
   tiền với Always Free).
2. Create Instance → Shape: **Ampere (ARM) — VM.Standard.A1.Flex**, chọn
   **2–4 OCPU + 12–24GB RAM** (đều nằm trong Always Free).
3. Image: **Ubuntu 22.04 (aarch64)**. Tải/ lưu SSH key.
4. Networking → mở cổng nếu cần (nếu dùng Cloudflare tunnel thì KHÔNG cần mở
   8888 ra ngoài — tunnel lo việc expose).

### A2. Cài Docker trên VM
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER   # logout/login lại để áp dụng
```

### A3. Lấy code + cấu hình env
```bash
git clone https://github.com/TuDoiii123/E-Mapp.git
cd E-Mapp
cp Backend/.env.example Backend/.env   # rồi điền giá trị thật
```
Điền `Backend/.env`: `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`, `JWT_SECRET`,
các `GOOGLE_*`/`GEMINI_*`, `TUNNEL_TOKEN`, và **`CORS_ORIGINS`** (xem bước CORS).

### A4. Build & chạy (native arm64 — không cần registry/QEMU)
```bash
docker compose up -d --build backend cloudflared
docker compose logs -f backend   # xem khởi động, init_db tạo bảng
```
> Build trên chính VM ARM nên image là arm64 đúng kiến trúc. Nhờ Dockerfile đã
> sửa, bước cài torch chạy ngon trên aarch64.

> **Không bật `frontend` ở compose nữa** vì frontend giờ ở Vercel. Có thể chạy
> chọn lọc service như trên (`backend cloudflared`), hoặc xoá block `frontend`
> khỏi `docker-compose.yml`.

### A5. Seed PDF cache (1 lần)
Bảng `template_pdf_cache` đã được seed từ máy dev (75 template). Nếu cần seed
lại và VM **không** có LibreOffice, cài thêm rồi chạy:
```bash
sudo apt-get install -y libreoffice
docker compose exec backend python scripts/seed_pdf_cache.py
```
(Hoặc bỏ qua — vì DB shared đã có sẵn dữ liệu seed từ trước.)

### A6. Auto-deploy (tuỳ chọn)
- **Đơn giản:** mỗi lần cập nhật → `git pull && docker compose up -d --build backend`.
- **Watchtower:** chỉ hữu ích nếu CI build & push image **arm64** lên registry.
  Hiện `.github/workflows/deploy.yml` build amd64 → KHÔNG chạy trên ARM. Muốn
  giữ watchtower thì cần thêm `platforms: linux/arm64` (buildx + QEMU, build
  chậm) hoặc dùng self-hosted ARM runner. Khuyến nghị: dùng cách `git pull` cho
  gọn, hoặc tách bàn riêng sau.

---

## Phần B — Frontend trên Vercel

### B1. Tạo project
1. Vercel → New Project → import repo `TuDoiii123/E-Mapp`.
2. **Root Directory: `Frontend`** (quan trọng — không phải gốc repo).
3. Framework Preset: **Other** (đã có `vercel.json` lo build/output).

### B2. Environment Variables (Production + Preview)
| Key | Giá trị |
|---|---|
| `VITE_API_URL` | URL backend qua Cloudflare tunnel, vd `https://api.emapp.xyz` |
| `VITE_GOOGLE_MAPS_API_KEY` | API key Google Maps |

> Env được **bake lúc build**. Đổi env phải **redeploy** mới có hiệu lực.

### B3. Deploy
Deploy → Vercel chạy `npm install && npm run build`, serve `build/`, SPA
rewrite đã cấu hình trong `vercel.json`.

---

## Phần C — CORS (nối Vercel ↔ backend)

Frontend Vercel ở domain khác backend → phải cho phép trong CORS. Thêm domain
Vercel vào `CORS_ORIGINS` trong `Backend/.env` (phân tách bằng dấu phẩy):
```
CORS_ORIGINS=https://<project>.vercel.app,https://emapp.xyz
```
Rồi `docker compose up -d backend` để áp dụng. (Mỗi lần Vercel tạo domain
preview mới, nếu cần gọi API thật thì thêm domain đó vào.)

---

## Checklist nghiệm thu
- [ ] `docker compose logs backend` thấy `init_db` OK, server lắng nghe 8888.
- [ ] Gọi `https://<backend>/api/templates` trả JSON (qua tunnel).
- [ ] Preview PDF: `GET /api/templates/preview/<file>.docx` trả `application/pdf`
      (đi nhánh DB, không cần LibreOffice trên VM).
- [ ] Mở site Vercel → gọi API thật không lỗi CORS (DevTools → Network).
- [ ] Refresh sâu 1 route con (vd `/admin/...`) trên Vercel → không 404 (SPA OK).
