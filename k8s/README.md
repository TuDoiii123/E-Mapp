# Deploy E-Mapp (frontend + backend) lên k3s

Cluster: k3s single-node, Traefik ingress (class `traefik`), cert-manager
(`letsencrypt-prod`), StorageClass `local-path`.

Kiến trúc: **1 host phục vụ cả frontend + backend** (cùng origin → không dính CORS).
Ingress định tuyến: `/api`, `/ws` → backend; còn lại `/` → frontend.

Cấu hình đã chốt:
- **Image backend:** `tubeo78910/emapp-backend:latest` — CI tự build & push mỗi lần push `master`
- **Image frontend:** `tubeo78910/emapp-frontend:latest` — build với `VITE_API_URL=https://<host>/api`
- **Host:** `emapp.huvisoft.com` (cần trỏ DNS A về IP VPS `157.66.80.93`)
- **Postgres:** chạy in-cluster (`postgres.yaml`) — backend override `DB_HOST=postgres`

> ⚠️ Frontend bake `VITE_API_URL` lúc BUILD (rsbuild `source.define`, xem `Frontend/rsbuild.config.ts`).
> CI build-arg `VITE_API_URL` phải = `https://emapp.huvisoft.com/api` thì frontend mới gọi đúng API.

## 1. Tạo Secret env từ Backend/.env (không commit)
Chạy ở máy dev (có Backend/.env) — tiện nhất là chạy `create-vps-secret.cmd` ở gốc repo,
hoặc thủ công pipe qua SSH vào VPS:
```bash
k3s kubectl create namespace emapp --dry-run=client -o yaml | k3s kubectl apply -f -
k3s kubectl -n emapp create secret generic emapp-env --from-env-file=Backend/.env
```
> `CORS_ORIGINS` trong .env phải gồm domain frontend (Vercel) + domain backend.
> `DB_HOST` trong Secret không quan trọng — Deployment đã override thành `postgres`.

## 2. Apply Postgres (in-cluster) trước
```bash
k3s kubectl apply -f k8s/postgres.yaml
k3s kubectl -n emapp rollout status statefulset/postgres
```

## 3. Apply backend + frontend
```bash
k3s kubectl apply -f k8s/backend.yaml -f k8s/frontend.yaml
k3s kubectl -n emapp rollout status deploy/emapp-backend
k3s kubectl -n emapp rollout status deploy/emapp-frontend
k3s kubectl -n emapp get pods,svc,ingress
```

## 4. TLS
cert-manager tự xin Let's Encrypt qua HTTP-01 (cần DNS đã trỏ + port 80 mở).
Theo dõi: `k3s kubectl -n emapp get certificate`.

## Ghi chú
- ChromaDB hiện dùng dữ liệu baked trong image (ephemeral — reset khi pod restart).
  Nếu cần bền vững, thêm PVC `local-path` mount vào `/app/RAG/chroma_db`.
- Postgres in-cluster lưu data trên PVC `local-path` 5Gi (bền qua restart pod).
