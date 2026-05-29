# Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy E-Mapp lên Windows 11 cá nhân với Docker Compose + Watchtower (auto-deploy) + Cloudflare Tunnel (public access).

**Architecture:** Docker Compose chạy 2 container (frontend nginx, backend Flask). PostgreSQL 15 native Windows kết nối qua `host.docker.internal`. GitHub Actions build & push image Docker Hub mỗi khi push master. Watchtower poll Docker Hub 5 phút/lần và restart container khi có image mới. Cloudflare Tunnel expose domain ra internet mà không cần mở port.

**Tech Stack:** Docker Desktop, Docker Compose v2, nginx:alpine, python:3.11-slim, rsbuild, Flask, containrrr/watchtower, cloudflare/cloudflared, GitHub Actions, Docker Hub.

---

## Files tạo mới / sửa

| File | Action |
|---|---|
| `Backend/Dockerfile` | Tạo mới |
| `Backend/.dockerignore` | Tạo mới |
| `Frontend/Dockerfile` | Tạo mới |
| `Frontend/nginx.conf` | Tạo mới |
| `Frontend/.dockerignore` | Tạo mới |
| `docker-compose.yml` | Tạo mới (root) |
| `.env.example` | Tạo mới (root) |
| `.env` | Tạo mới (root, gitignored — không commit) |
| `.github/workflows/deploy.yml` | Tạo mới |
| `.gitignore` | Sửa — thêm `.env` |

---

## Task 1: Cài Docker Desktop

**Files:** Không có file code — bước manual.

- [ ] **Step 1: Tải Docker Desktop**

  Vào `https://www.docker.com/products/docker-desktop` → Download for Windows.

- [ ] **Step 2: Cài đặt**

  Chạy installer. Khi hỏi "Use WSL 2 instead of Hyper-V" → chọn **WSL 2**. Restart máy khi được yêu cầu.

- [ ] **Step 3: Bật Docker Desktop và verify**

  Mở Docker Desktop, đợi icon ở taskbar chuyển thành màu xanh (Running).

  Chạy trong terminal:
  ```powershell
  docker run hello-world
  ```
  Expected output: `Hello from Docker!`

- [ ] **Step 4: Verify docker compose**
  ```powershell
  docker compose version
  ```
  Expected: `Docker Compose version v2.x.x`

---

## Task 2: Tạo tài khoản Docker Hub + chuẩn bị secret

**Files:** Không có file code — bước manual.

- [ ] **Step 1: Tạo tài khoản Docker Hub**

  Vào `https://hub.docker.com` → Sign Up. Chọn username (ví dụ: `emapp` hoặc username cá nhân).

- [ ] **Step 2: Tạo Access Token**

  Vào Docker Hub → Account Settings → Security → New Access Token.
  - Description: `github-actions`
  - Permissions: `Read & Write`
  - Lưu token vào chỗ an toàn (chỉ hiện 1 lần).

- [ ] **Step 3: Thêm secret vào GitHub repo**

  Vào GitHub repo E-Mapp → Settings → Secrets and variables → Actions → New repository secret:
  - `DOCKERHUB_USERNAME` = username Docker Hub của bạn
  - `DOCKERHUB_TOKEN` = access token vừa tạo

  Thêm tiếp các secret môi trường:
  - `VITE_API_URL` = `https://api.emapp.yourdomain.vn` (cập nhật sau khi có domain)
  - `VITE_GOOGLE_MAPS_API_KEY` = Google Maps API key hiện tại của bạn

---

## Task 3: Backend Dockerfile

**Files:**
- Tạo: `Backend/Dockerfile`
- Tạo: `Backend/.dockerignore`

- [ ] **Step 1: Tạo .dockerignore**

  ```
  # Backend/.dockerignore
  __pycache__/
  *.pyc
  *.pyo
  .env
  .env.*
  !.env.example
  data/pdf_cache/
  uploads/
  *.log
  .git/
  node_modules/
  ```

- [ ] **Step 2: Tạo Dockerfile**

  Lưu ý: PyTorch phải dùng bản CPU-only, nếu không image sẽ ~4GB.

  ```dockerfile
  # Backend/Dockerfile
  FROM python:3.11-slim

  # Cài system deps cần cho psycopg2 và build tools
  RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc \
      libpq-dev \
      curl \
      && rm -rf /var/lib/apt/lists/*

  WORKDIR /app

  # Copy requirements trước để tận dụng Docker layer cache
  COPY requirements.txt .

  # Cài PyTorch CPU-only trước (nhỏ hơn ~3GB so với CUDA version)
  RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

  # Cài các package còn lại (loại torch ra tránh install lại)
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy toàn bộ source
  COPY . .

  # Tạo thư mục uploads (nếu route cần ghi file)
  RUN mkdir -p uploads data/pdf_cache

  EXPOSE 8888

  CMD ["python", "server.py"]
  ```

- [ ] **Step 3: Test build local**

  Từ thư mục root của project:
  ```powershell
  docker build -t emapp-backend:test ./Backend
  ```
  Expected: Build thành công, không có lỗi. Có thể mất 5–15 phút lần đầu do tải PyTorch.

- [ ] **Step 4: Test chạy container**

  Cần PostgreSQL đang chạy. Tạm thời test với biến môi trường:
  ```powershell
  docker run --rm -p 8888:8888 `
    -e DB_HOST=host.docker.internal `
    -e DB_PORT=5432 `
    -e DB_NAME=postgres `
    -e DB_USER=postgres `
    -e DB_PASSWORD=your_actual_pg_password `
    -e JWT_SECRET=test-secret `
    emapp-backend:test
  ```
  Expected: Server khởi động, log hiện `Running on http://0.0.0.0:8888`.

  Test endpoint:
  ```powershell
  curl http://localhost:8888/api/services
  ```
  Expected: JSON response (200 hoặc có data).

- [ ] **Step 5: Commit**
  ```powershell
  git add Backend/Dockerfile Backend/.dockerignore
  git commit -m "feat(deploy): add Backend Dockerfile (Flask + PyTorch CPU)"
  ```

---

## Task 4: Frontend Dockerfile + nginx

**Files:**
- Tạo: `Frontend/Dockerfile`
- Tạo: `Frontend/nginx.conf`
- Tạo: `Frontend/.dockerignore`

- [ ] **Step 1: Tạo .dockerignore**

  ```
  # Frontend/.dockerignore
  node_modules/
  dist/
  build/
  .env
  .env.*
  !.env.example
  *.log
  .git/
  ```

- [ ] **Step 2: Tạo nginx.conf**

  App dùng state-based routing (không có React Router), nhưng nginx vẫn cần serve `index.html` cho tất cả route để tránh 404 khi F5.

  ```nginx
  # Frontend/nginx.conf
  server {
      listen 80;
      server_name _;
      root /usr/share/nginx/html;
      index index.html;

      # Gzip compression
      gzip on;
      gzip_types text/plain text/css application/javascript application/json image/svg+xml;
      gzip_min_length 1024;

      # Cache static assets
      location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
          expires 1y;
          add_header Cache-Control "public, immutable";
      }

      # SPA fallback — mọi route → index.html
      location / {
          try_files $uri $uri/ /index.html;
      }
  }
  ```

- [ ] **Step 3: Tạo Dockerfile**

  `VITE_API_URL` được inject lúc build (GitHub Actions truyền vào `--build-arg`).

  ```dockerfile
  # Frontend/Dockerfile
  FROM node:20-alpine AS builder

  WORKDIR /app

  # Copy package files
  COPY package.json package-lock.json ./

  # Install dependencies
  RUN npm ci

  # Copy source
  COPY . .

  # Build args cho env vars (baked vào static files)
  ARG VITE_API_URL
  ARG VITE_GOOGLE_MAPS_API_KEY
  ENV VITE_API_URL=$VITE_API_URL
  ENV VITE_GOOGLE_MAPS_API_KEY=$VITE_GOOGLE_MAPS_API_KEY

  # Build với rsbuild
  RUN npm run build

  # Stage 2: nginx serve
  FROM nginx:alpine

  # Copy custom nginx config
  COPY nginx.conf /etc/nginx/conf.d/default.conf

  # Copy built files từ stage 1
  # rsbuild output vào build/ (theo rsbuild.config.ts: distPath.root = 'build')
  COPY --from=builder /app/build /usr/share/nginx/html

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]
  ```

- [ ] **Step 4: Confirm rsbuild output path**

  Đã confirm: `rsbuild.config.ts` khai báo `distPath: { root: 'build' }`. Dockerfile đã dùng `/app/build`. Không cần sửa thêm.

- [ ] **Step 5: Test build local** (cần truyền VITE_API_URL)
  ```powershell
  docker build -t emapp-frontend:test `
    --build-arg VITE_API_URL=http://localhost:8888 `
    --build-arg VITE_GOOGLE_MAPS_API_KEY=test `
    ./Frontend
  ```
  Expected: Build thành công.

- [ ] **Step 6: Test chạy container**
  ```powershell
  docker run --rm -p 3000:80 emapp-frontend:test
  ```
  Mở browser: `http://localhost:3000` → App load được (dù API chưa kết nối là bình thường).

- [ ] **Step 7: Commit**
  ```powershell
  git add Frontend/Dockerfile Frontend/nginx.conf Frontend/.dockerignore
  git commit -m "feat(deploy): add Frontend Dockerfile (rsbuild + nginx)"
  ```

---

## Task 5: docker-compose.yml + .env

**Files:**
- Tạo: `docker-compose.yml` (root)
- Tạo: `.env.example` (root)
- Sửa: `.gitignore`

- [ ] **Step 1: Cập nhật .gitignore**

  Mở `.gitignore` (hoặc tạo nếu chưa có ở root), thêm:
  ```
  .env
  .env.local
  ```

- [ ] **Step 2: Tạo .env.example**

  ```ini
  # .env.example — copy thành .env và điền giá trị thật
  
  # PostgreSQL (đang chạy native trên Windows)
  DB_HOST=host.docker.internal
  DB_PORT=5432
  DB_NAME=postgres
  DB_USER=postgres
  DB_PASSWORD=

  # JWT
  JWT_SECRET=change-this-to-random-string

  # Gemini AI
  GEMINI_API_KEY=
  GEMINI_MODEL_NAME=models/gemini-2.5-flash
  GEMINI_MODEL_RAG=gemini-2.5-flash

  # CORS — domain thật sau khi setup Cloudflare
  CORS_ORIGINS=http://localhost:3000,http://localhost:5173

  # Cloudflare Tunnel token (lấy từ Cloudflare Dashboard sau Task 8)
  TUNNEL_TOKEN=

  # Docker Hub username (để Watchtower biết pull từ đâu)
  DOCKERHUB_USERNAME=your_dockerhub_username
  ```

- [ ] **Step 3: Tạo file .env thật**

  ```powershell
  copy .env.example .env
  ```
  Mở `.env` và điền:
  - `DB_PASSWORD` = password PostgreSQL hiện tại trên máy bạn
  - `JWT_SECRET` = chuỗi random dài (ví dụ: chạy `[System.Guid]::NewGuid().ToString()` trong PowerShell để lấy)
  - `GEMINI_API_KEY` = API key Gemini của bạn
  - `DOCKERHUB_USERNAME` = username Docker Hub vừa tạo ở Task 2
  - `TUNNEL_TOKEN` = để trống tạm, điền sau Task 8

- [ ] **Step 4: Tạo docker-compose.yml**

  Thay `YOUR_DOCKERHUB_USERNAME` bằng username Docker Hub của bạn.

  ```yaml
  # docker-compose.yml
  services:
    frontend:
      image: ${DOCKERHUB_USERNAME}/emapp-frontend:latest
      restart: unless-stopped
      ports:
        - "3000:80"
      labels:
        - "com.centurylinklabs.watchtower.enable=true"

    backend:
      image: ${DOCKERHUB_USERNAME}/emapp-backend:latest
      restart: unless-stopped
      ports:
        - "8888:8888"
      environment:
        DB_HOST: ${DB_HOST}
        DB_PORT: ${DB_PORT}
        DB_NAME: ${DB_NAME}
        DB_USER: ${DB_USER}
        DB_PASSWORD: ${DB_PASSWORD}
        JWT_SECRET: ${JWT_SECRET}
        GEMINI_API_KEY: ${GEMINI_API_KEY}
        GEMINI_MODEL_NAME: ${GEMINI_MODEL_NAME}
        GEMINI_MODEL_RAG: ${GEMINI_MODEL_RAG}
        CORS_ORIGINS: ${CORS_ORIGINS}
      extra_hosts:
        - "host.docker.internal:host-gateway"
      labels:
        - "com.centurylinklabs.watchtower.enable=true"

    cloudflared:
      image: cloudflare/cloudflared:latest
      restart: unless-stopped
      command: tunnel --no-autoupdate run
      environment:
        TUNNEL_TOKEN: ${TUNNEL_TOKEN}

    watchtower:
      image: containrrr/watchtower
      restart: unless-stopped
      volumes:
        - /var/run/docker.sock:/var/run/docker.sock
      command: --interval 300 --label-enable
      environment:
        WATCHTOWER_CLEANUP: "true"
  ```

- [ ] **Step 5: Test docker compose (chưa có image trên Docker Hub)**

  Lần đầu chưa có image nên cần build local trước.
  Thay `YOUR_USERNAME` bằng username Docker Hub của bạn:
  ```powershell
  # Build local image với tên giống Docker Hub
  docker build -t YOUR_USERNAME/emapp-backend:latest ./Backend
  docker build -t YOUR_USERNAME/emapp-frontend:latest `
    --build-arg VITE_API_URL=http://localhost:8888 `
    --build-arg VITE_GOOGLE_MAPS_API_KEY=test `
    ./Frontend
  ```

  Start services (bỏ qua cloudflared tạm vì TUNNEL_TOKEN chưa có):
  ```powershell
  docker compose up frontend backend watchtower -d
  ```
  Expected: 3 container running.

  Check:
  ```powershell
  docker compose ps
  ```
  Expected: tất cả status `running`.

  Test frontend: Mở `http://localhost:3000`
  Test backend: `curl http://localhost:8888/api/services`

- [ ] **Step 6: Commit**
  ```powershell
  git add docker-compose.yml .env.example .gitignore
  git commit -m "feat(deploy): add docker-compose with Watchtower + Cloudflare Tunnel"
  ```

---

## Task 6: GitHub Actions CI/CD

**Files:**
- Tạo: `.github/workflows/deploy.yml`

- [ ] **Step 1: Tạo thư mục**
  ```powershell
  New-Item -ItemType Directory -Force -Path .github/workflows
  ```

- [ ] **Step 2: Tạo workflow file**

  ```yaml
  # .github/workflows/deploy.yml
  name: Build and Push Docker Images

  on:
    push:
      branches:
        - master

  jobs:
    build-and-push:
      runs-on: ubuntu-latest

      steps:
        - name: Checkout code
          uses: actions/checkout@v4

        - name: Login to Docker Hub
          uses: docker/login-action@v3
          with:
            username: ${{ secrets.DOCKERHUB_USERNAME }}
            password: ${{ secrets.DOCKERHUB_TOKEN }}

        - name: Set up Docker Buildx
          uses: docker/setup-buildx-action@v3

        - name: Build and push Backend
          uses: docker/build-push-action@v5
          with:
            context: ./Backend
            push: true
            tags: ${{ secrets.DOCKERHUB_USERNAME }}/emapp-backend:latest
            cache-from: type=gha
            cache-to: type=gha,mode=max

        - name: Build and push Frontend
          uses: docker/build-push-action@v5
          with:
            context: ./Frontend
            push: true
            tags: ${{ secrets.DOCKERHUB_USERNAME }}/emapp-frontend:latest
            build-args: |
              VITE_API_URL=${{ secrets.VITE_API_URL }}
              VITE_GOOGLE_MAPS_API_KEY=${{ secrets.VITE_GOOGLE_MAPS_API_KEY }}
            cache-from: type=gha
            cache-to: type=gha,mode=max
  ```

- [ ] **Step 3: Commit và push để test**
  ```powershell
  git add .github/workflows/deploy.yml
  git commit -m "feat(deploy): add GitHub Actions CI/CD for Docker Hub push"
  git push origin master
  ```

- [ ] **Step 4: Verify trên GitHub**

  Vào GitHub repo → tab Actions → xem workflow run.
  Expected: Cả 2 job (backend + frontend) đều green ✓.

  Vào Docker Hub → xem repo `your-username/emapp-backend` và `emapp-frontend` đã có image `latest`.

---

## Task 7: Setup Cloudflare Tunnel + Domain

**Files:**
- Sửa: `.env` (thêm TUNNEL_TOKEN)
- Sửa: `.env.example` (cập nhật CORS_ORIGINS comment)

**Điều kiện:** Đã có domain và đã thêm vào Cloudflare (nameserver đã trỏ về Cloudflare).

- [ ] **Step 1: Thêm domain vào Cloudflare**

  1. Vào `https://dash.cloudflare.com` → Add a Site → nhập domain của bạn
  2. Chọn plan Free → Continue
  3. Cloudflare sẽ cho bạn 2 nameserver (ví dụ: `ada.ns.cloudflare.com`)
  4. Vào nhà đăng ký domain (NIC.vn) → đổi nameserver sang 2 nameserver của Cloudflare
  5. Đợi 5–30 phút để propagate

- [ ] **Step 2: Tạo Cloudflare Tunnel**

  Trong Cloudflare Dashboard:
  1. Vào **Zero Trust** (menu bên trái) → **Networks** → **Tunnels**
  2. Click **Create a tunnel** → Cloudflared → đặt tên tunnel: `emapp-tunnel`
  3. Chọn **Docker** làm connector → Cloudflare sẽ cho bạn lệnh có dạng:
     ```
     docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run --token eyJ...
     ```
  4. **Copy phần token** sau `--token` (chuỗi dài bắt đầu bằng `eyJ`)

- [ ] **Step 3: Cấu hình Public Hostname trong tunnel**

  Vẫn trong wizard tạo tunnel, thêm 2 public hostname:

  | Subdomain | Domain | Service |
  |---|---|---|
  | `emapp` | `yourdomain.vn` | `http://frontend:80` |
  | `api.emapp` | `yourdomain.vn` | `http://backend:8888` |

  Save tunnel.

- [ ] **Step 4: Thêm TUNNEL_TOKEN vào .env**

  Mở file `.env`, điền:
  ```
  TUNNEL_TOKEN=eyJ...token-đã-copy...
  ```

- [ ] **Step 5: Start cloudflared**
  ```powershell
  docker compose up cloudflared -d
  ```
  Check log:
  ```powershell
  docker compose logs cloudflared
  ```
  Expected: Log hiện `Registered tunnel connection` hoặc `Connection established`.

- [ ] **Step 6: Test public access**

  Mở browser: `https://emapp.yourdomain.vn`
  Expected: App load được qua HTTPS.

  Test API: `https://api.emapp.yourdomain.vn/api/services`
  Expected: JSON response.

---

## Task 8: Cập nhật CORS + Frontend API URL cho production

**Files:**
- Sửa: `.env` (cập nhật CORS_ORIGINS)
- Sửa: GitHub Secret `VITE_API_URL`

- [ ] **Step 1: Cập nhật CORS_ORIGINS trong .env**

  Mở `.env`, sửa:
  ```
  CORS_ORIGINS=https://emapp.yourdomain.vn,http://localhost:3000,http://localhost:5173
  ```

- [ ] **Step 2: Restart backend để nhận CORS mới**
  ```powershell
  docker compose restart backend
  ```

- [ ] **Step 3: Cập nhật GitHub Secret VITE_API_URL**

  Vào GitHub repo → Settings → Secrets → sửa `VITE_API_URL`:
  ```
  https://api.emapp.yourdomain.vn
  ```

- [ ] **Step 4: Push một commit nhỏ để trigger rebuild frontend**
  ```powershell
  git commit --allow-empty -m "chore: trigger rebuild frontend with production API URL"
  git push origin master
  ```
  Đợi GitHub Actions build xong (~5 phút).
  Đợi Watchtower tự restart frontend container (~5 phút tiếp).

- [ ] **Step 5: Kiểm tra final**

  1. Mở `https://emapp.yourdomain.vn` → đăng nhập thử
  2. Test gọi API từ browser (F12 → Network) → đảm bảo gọi đến `api.emapp.yourdomain.vn`
  3. Không có lỗi CORS trong console

---

## Task 9: Test auto-deploy end-to-end

**Files:** Không có file thay đổi thật — chỉ test luồng.

- [ ] **Step 1: Sửa một thứ nhỏ để test**

  Ví dụ: sửa title trong `Frontend/src/screens/user/MapScreen.tsx` hoặc bất kỳ file nào.

- [ ] **Step 2: Commit và push**
  ```powershell
  git add .
  git commit -m "test: verify auto-deploy pipeline"
  git push origin master
  ```

- [ ] **Step 3: Theo dõi GitHub Actions**

  Vào GitHub → Actions → xem build chạy. Expected: green trong ~5–8 phút.

- [ ] **Step 4: Đợi Watchtower**

  Watchtower poll mỗi 5 phút. Sau tối đa 10 phút kể từ khi Actions xong:
  ```powershell
  docker compose logs watchtower
  ```
  Expected: Log có dạng `Found new emapp-frontend:latest image ... Restarting container`.

- [ ] **Step 5: Verify thay đổi live**

  Mở `https://emapp.yourdomain.vn` → xác nhận thay đổi đã xuất hiện mà không cần làm gì thêm. ✓

---

## Troubleshooting nhanh

| Vấn đề | Kiểm tra |
|---|---|
| Backend không kết nối được PostgreSQL | Chạy `docker compose exec backend python -c "from models.db import test_connection; print(test_connection())"` |
| `host.docker.internal` không resolve | Kiểm tra `extra_hosts` trong docker-compose.yml; Docker Desktop Windows thường tự có |
| Cloudflared không kết nối | Kiểm tra TUNNEL_TOKEN đúng chưa: `docker compose logs cloudflared` |
| Watchtower không pull image mới | Image trên Docker Hub phải là `latest` và đúng username |
| CORS error trên browser | Kiểm tra CORS_ORIGINS trong .env đã có domain production chưa |
