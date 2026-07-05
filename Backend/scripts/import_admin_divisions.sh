#!/usr/bin/env bash
# Nạp danh mục hành chính VN (tỉnh/xã, mô hình 2025 — bỏ cấp huyện) vào Postgres.
# Nguồn: repo thanglequoc/vietnamese-provinces-database (script PostgreSQL chính thức).
# Tạo/đổ vào các bảng: administrative_regions, administrative_units, provinces, wards.
#
# Cách dùng:
#   1) Local/psql trực tiếp:   DATABASE_URL=postgres://user:pass@host:5432/db ./import_admin_divisions.sh
#   2) Trên k3s (postgres-0):  xem k8s/README.md — pipe file qua kubectl exec.
set -euo pipefail

RAW="https://raw.githubusercontent.com/thanglequoc/vietnamese-provinces-database/master/postgresql"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ Tải script SQL từ repo..."
curl -fsSL "$RAW/postgres_CreateTables_vn_units.sql" -o "$TMP/create.sql"
curl -fsSL "$RAW/postgres_ImportData_vn_units.sql"  -o "$TMP/import.sql"

: "${DATABASE_URL:?Cần đặt DATABASE_URL=postgres://user:pass@host:port/db}"

echo "→ Tạo bảng..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$TMP/create.sql"
echo "→ Nạp dữ liệu (34 tỉnh, ~3.321 xã)..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$TMP/import.sql"

echo "→ Kiểm tra:"
psql "$DATABASE_URL" -tAc "SELECT 'provinces='||count(*) FROM provinces; " || true
psql "$DATABASE_URL" -tAc "SELECT 'wards='||count(*) FROM wards;"           || true
echo "✓ Xong."
