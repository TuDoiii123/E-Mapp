"""
Gán ward (xã/phường mô hình 2025) cho cơ quan trong ds_dichvucong bằng
reverse-geocode toạ độ (Nominatim) → chuẩn hoá tên → match bảng `wards`.

Vì cải cách 2025 gộp/đổi tên xã, KHÔNG match được theo tên trong address cũ.
Point-in-polygon thì cần 166 file ranh giới (~25MB) + map 2 hệ mã GIS/admin khác nhau.
→ Dùng reverse-geocode: OSM đã cập nhật xã 2025, tên khớp bảng wards (~88%).

Chạy trong pod backend:  python scripts/assign_wards_by_geocode.py
Cần: DB_* env (đã có trong Secret), mạng ra Nominatim.
"""
import os, re, time, json, sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import psycopg2

NOMINATIM = 'https://nominatim.openstreetmap.org/reverse'
UA = 'E-Mapp/1.0 (admin-divisions ward assignment)'


def norm(s: str) -> str:
    s = (s or '').strip()
    s = re.sub(r'^(Phường|Xã|Thị trấn|TT\.|P\.|X\.)\s+', '', s, flags=re.IGNORECASE)
    return s.strip().lower()


def reverse_ward(lat, lng):
    """Trả tên xã/phường 2025 từ toạ độ. OSM bỏ cấp huyện nên xã thường nằm ở
    quận/huyện (county/city_district) hoặc suburb."""
    q = f'{NOMINATIM}?lat={lat}&lon={lng}&format=jsonv2&addressdetails=1&accept-language=vi'
    req = urllib.request.Request(q, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        addr = json.loads(r.read().decode('utf-8')).get('address', {})
    for k in ('city_district', 'county', 'suburb', 'quarter', 'village', 'town'):
        if addr.get(k):
            return addr[k]
    return None


def main():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'), port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'postgres'), user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
    )
    cur = conn.cursor()
    cur.execute("ALTER TABLE ds_dichvucong ADD COLUMN IF NOT EXISTS ward_code VARCHAR(20)")
    conn.commit()

    cur.execute("SELECT code, name FROM wards WHERE province_code='38'")
    ward_map = {norm(n): (c, n) for c, n in cur.fetchall()}

    cur.execute("SELECT id, latitude, longitude FROM ds_dichvucong WHERE latitude IS NOT NULL")
    rows = cur.fetchall()

    matched = 0
    for i, (aid, lat, lng) in enumerate(rows, 1):
        name = None
        try:
            name = reverse_ward(lat, lng)
        except Exception as e:
            print(f'[{i}/{len(rows)}] {aid}: geocode lỗi {e}')
        hit = ward_map.get(norm(name)) if name else None
        if hit:
            cur.execute("UPDATE ds_dichvucong SET ward=%s, ward_code=%s WHERE id=%s",
                        (hit[1], hit[0], aid))
            matched += 1
            print(f'[{i}/{len(rows)}] {aid} -> {hit[1]}')
        else:
            print(f'[{i}/{len(rows)}] {aid} -> MISS ({name})')
        time.sleep(1.2)  # rate limit Nominatim 1 req/s
    conn.commit()
    print(f'\n=== Gán ward: {matched}/{len(rows)} ===')


if __name__ == '__main__':
    main()
