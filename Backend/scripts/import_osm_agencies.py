"""
Import cơ quan nhà nước TOÀN QUỐC từ OpenStreetMap vào agencies + ds_dichvucong.

Pipeline:
  1. Tải POI cơ quan từ Overpass (office=government / amenity=townhall) — cache vn_gov.json.
  2. Tải 34 ranh giới tỉnh (mô hình 2025) từ repo thanglequoc — cache prov_cache/.
  3. Point-in-polygon (ray-casting, không cần shapely) gán tỉnh cho từng POI.
  4. Sinh SQL: osm_agencies_all.sql (INSERT ON CONFLICT DO NOTHING).

Chạy:  cd Backend && python scripts/import_osm_agencies.py [--workdir DIR]
Import: pipe file SQL vào psql (xem k8s/README.md):
  cat osm_agencies_all.sql | ssh <vps> "kubectl exec -i -n emapp postgres-0 -- psql -U postgres -d postgres"

Chống rate-limit: mọi fetch đều cache ra đĩa + retry/backoff → chạy lại không refetch.
"""
import argparse
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter

RAWBASE = ("https://raw.githubusercontent.com/thanglequoc/vietnamese-provinces-database"
           "/master/dataset-generation-scripts/resources/gis/geojson_11Mar2026")
TREE_API = ("https://api.github.com/repos/thanglequoc/vietnamese-provinces-database"
            "/git/trees/master?recursive=1")
OVERPASS = 'https://overpass-api.de/api/interpreter'
OVERPASS_QUERY = """
[out:json][timeout:300];
area["ISO3166-1"="VN"][admin_level=2]->.vn;
(
  node["office"="government"](area.vn);
  way["office"="government"](area.vn);
  node["amenity"="townhall"](area.vn);
  way["amenity"="townhall"](area.vn);
);
out center tags;
"""
UA = 'E-Mapp/1.0 (agency import; contact tu.bui@huvisoft.com)'

# 34 tỉnh/thành mô hình 2025 — khớp bảng `provinces` (nguồn thanglequoc).
PROVINCES_2025 = [
    ("01", "Hà Nội"), ("04", "Cao Bằng"), ("08", "Tuyên Quang"), ("11", "Điện Biên"),
    ("12", "Lai Châu"), ("14", "Sơn La"), ("15", "Lào Cai"), ("19", "Thái Nguyên"),
    ("20", "Lạng Sơn"), ("22", "Quảng Ninh"), ("24", "Bắc Ninh"), ("25", "Phú Thọ"),
    ("31", "Hải Phòng"), ("33", "Hưng Yên"), ("37", "Ninh Bình"), ("38", "Thanh Hoá"),
    ("40", "Nghệ An"), ("42", "Hà Tĩnh"), ("44", "Quảng Trị"), ("46", "Huế"),
    ("48", "Đà Nẵng"), ("51", "Quảng Ngãi"), ("52", "Gia Lai"), ("56", "Khánh Hoà"),
    ("66", "Đắk Lắk"), ("68", "Lâm Đồng"), ("75", "Đồng Nai"), ("79", "Hồ Chí Minh"),
    ("80", "Tây Ninh"), ("82", "Đồng Tháp"), ("86", "Vĩnh Long"), ("91", "An Giang"),
    ("92", "Cần Thơ"), ("96", "Cà Mau"),
]


def strip_dia(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('đ', 'd').replace('Đ', 'D').lower().strip()


def http_json(url, timeout=120, data=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA},
                                 data=data.encode() if data else None)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def fetch_cached_json(path, producer, validate=lambda d: True):
    """Đọc từ cache nếu có; nếu không thì gọi producer() với retry/backoff rồi cache."""
    if os.path.exists(path) and os.path.getsize(path) > 100:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    last = None
    for attempt in range(5):
        try:
            d = producer()
            if not validate(d):
                raise ValueError('kết quả không hợp lệ')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False)
            return d
        except Exception as e:
            last = e
            wait = 2 ** attempt
            print(f'  fetch lỗi ({e}); thử lại sau {wait}s [{attempt + 1}/5]', flush=True)
            time.sleep(wait)
    raise RuntimeError(f'fetch thất bại sau 5 lần: {last}')


def load_province_slugs(workdir):
    """Danh sách slug thư mục tỉnh trong geojson_11Mar2026 (từ GitHub tree API)."""
    fp = os.path.join(workdir, 'prov_folders.json')

    def produce():
        tree = http_json(TREE_API)['tree']
        pat = re.compile(r'geojson_11Mar2026/([^/]+)/province\.geojson$')
        return sorted({m.group(1) for t in tree if (m := pat.search(t['path']))})

    return fetch_cached_json(fp, produce, validate=lambda d: len(d) == 34)


def load_province_polygons(workdir, slugs):
    """Tải + cache province.geojson từng tỉnh, trả [(code, name, rings, bbox)]."""
    cache = os.path.join(workdir, 'prov_cache')
    os.makedirs(cache, exist_ok=True)
    adm_by_norm = {strip_dia(name): (code, name) for code, name in PROVINCES_2025}

    provinces = []
    for slug in slugs:
        norm = strip_dia(re.sub(r'^(tinh|thanh_pho|tp|thu_do)_', '',
                                re.sub(r'^\d+_', '', slug)).replace('_', ' '))
        adm = adm_by_norm.get(norm)
        if not adm:
            adm = next(((c, n) for k, (c, n) in adm_by_norm.items()
                        if norm in k or k in norm), None)
        if not adm:
            print('  KHÔNG MAP slug:', slug); continue

        fp = os.path.join(cache, slug + '.geojson')
        url = f'{RAWBASE}/{urllib.parse.quote(slug)}/province.geojson'
        try:
            gj = fetch_cached_json(fp, lambda u=url: http_json(u))
        except RuntimeError as e:
            print('  BỎ QUA', slug, e); continue

        rings = []
        for feat in gj.get('features', []):
            g = feat.get('geometry') or {}
            coords = g.get('coordinates') or []
            if g.get('type') == 'MultiPolygon':
                rings += [poly[0] for poly in coords if poly]
            elif g.get('type') == 'Polygon' and coords:
                rings.append(coords[0])
        if not rings:
            continue
        xs = [p[0] for rg in rings for p in rg]
        ys = [p[1] for rg in rings for p in rg]
        provinces.append((adm[0], adm[1], rings, (min(xs), min(ys), max(xs), max(ys))))
    return provinces


def in_ring(x, y, ring):
    inside = False
    n = len(ring); j = n - 1
    for i in range(n):
        xi, yi = ring[i]; xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def make_find_province(provinces):
    def find(lon, lat):
        for code, name, rings, (mnx, mny, mxx, mxy) in provinces:
            if not (mnx <= lon <= mxx and mny <= lat <= mxy):
                continue
            if any(in_ring(lon, lat, r) for r in rings):
                return code, name
        return None, None
    return find


def categorize(name):
    n = strip_dia(name)
    # nl giữ dấu (NFC) để phân biệt 'Sở' với 'số'/'trụ sở' — bỏ dấu đều thành 'so'
    nl = unicodedata.normalize('NFC', name).lower()
    if 'cong an' in n:
        return 'police'
    if 'thue' in n or 'kho bac' in n:
        return 'tax'
    if 'bao hiem' in n or 'bhxh' in n:
        return 'bhxh'
    if 'benh vien' in n or 'y te' in n or 'tram y' in n:
        return 'health'
    if 'trung tam' in n and ('hanh chinh' in n or 'phuc vu' in n or 'dich vu cong' in n):
        return 'trung-tam'
    if nl.startswith('sở ') or ', sở ' in nl:
        return 'so-nganh'
    return 'ubnd'


def level_of(name):
    # Giữ dấu (NFC): 'thị xã' phải xét TRƯỚC 'xã' (chuỗi 'thị xã' chứa 'xã'),
    # nhưng 'phường X, quận Y' vẫn phải ra ward → chỉ 'thị xã' đứng trước nhóm ward
    nl = unicodedata.normalize('NFC', name).lower()
    if nl.startswith('sở '):
        return 'province'
    if 'thị xã' in nl:
        return 'district'
    if 'phường' in nl or 'thị trấn' in nl or re.search(r'\bxã\b', nl):
        return 'ward'
    if 'huyện' in nl or 'thành phố' in nl or 'quận' in nl or re.search(r'\btp\.?\s', nl):
        return 'district'
    if 'tỉnh' in nl:
        return 'province'
    return 'ward'


def addr_of(t):
    parts = [t.get(k) for k in ('addr:housenumber', 'addr:street', 'addr:subdistrict',
                                'addr:district', 'addr:city', 'addr:province')]
    return ', '.join(p for p in parts if p)


def esc(s):
    return (s or '').replace("'", "''")


SQL_HEADER = (
    "SET client_encoding='UTF8';\n"
    "-- Import cơ quan OSM (point-in-polygon gán tỉnh) — sinh bởi import_osm_agencies.py\n"
    "ALTER TABLE agencies ADD COLUMN IF NOT EXISTS ward VARCHAR(100) NOT NULL DEFAULT '';\n"
    "ALTER TABLE ds_dichvucong ADD COLUMN IF NOT EXISTS ward_code VARCHAR(20);\n"
    "BEGIN;\n"
)


def emit_sql(rows, path):
    out = [SQL_HEADER]
    for r in rows:
        out.append(
            "INSERT INTO agencies (id,name,address,ward,district,province,latitude,longitude,level,is_active) "
            f"VALUES ('{esc(r['id'])}','{esc(r['name'])}','{esc(r['address'])}','{esc(r['ward'])}',"
            f"'{esc(r['district'])}','{esc(r['province'])}',{r['lat']},{r['lng']},'{esc(r['level'])}',TRUE) "
            "ON CONFLICT (id) DO NOTHING;")
        out.append(
            "INSERT INTO ds_dichvucong (id,name,description,category_id,address,latitude,longitude,level,status,province,district,ward) "
            f"VALUES ('{esc(r['id'])}','{esc(r['name'])}','{esc(r['name'])}','{esc(r['cat'])}','{esc(r['address'])}',"
            f"{r['lat']},{r['lng']},'{esc(r['level'])}','normal','{esc(r['province'])}','{esc(r['district'])}','{esc(r['ward'])}') "
            "ON CONFLICT (id) DO NOTHING;")
    out.append("COMMIT;\n")
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'  -> {os.path.basename(path)}: {len(rows)} cơ quan')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workdir', default=os.path.join(os.path.dirname(__file__), 'osm_import_work'),
                    help='thư mục cache + output (mặc định: scripts/osm_import_work)')
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)

    # 1. POI cơ quan từ Overpass (cache vn_gov.json)
    gov_fp = os.path.join(args.workdir, 'vn_gov.json')
    gov = fetch_cached_json(
        gov_fp,
        lambda: http_json(OVERPASS, timeout=360, data='data=' + urllib.parse.quote(OVERPASS_QUERY)),
        validate=lambda d: len(d.get('elements', [])) > 1000,
    )['elements']
    print('POI Overpass:', len(gov), flush=True)

    # 2. Ranh giới 34 tỉnh
    slugs = load_province_slugs(args.workdir)
    provinces = load_province_polygons(args.workdir, slugs)
    print('Polygon tỉnh:', len(provinces), '/', len(slugs), flush=True)
    find_province = make_find_province(provinces)

    # 3. Gán tỉnh cho POI
    rows, seen = [], set()
    for e in gov:
        t = e.get('tags', {})
        name = t.get('name')
        if not name:
            continue
        lat = e.get('lat') or (e.get('center') or {}).get('lat')
        lon = e.get('lon') or (e.get('center') or {}).get('lon')
        if lat is None or lon is None:
            continue
        _, prov = find_province(lon, lat)
        if not prov:
            continue
        oid = f"osm-{e['type']}-{e['id']}"
        if oid in seen:
            continue
        seen.add(oid)
        rows.append({
            'id': oid, 'name': name[:250], 'address': addr_of(t)[:400] or prov,
            'lat': round(float(lat), 6), 'lng': round(float(lon), 6), 'province': prov,
            'district': (t.get('addr:district') or '')[:100],
            'ward': (t.get('addr:subdistrict') or '')[:100],
            'cat': categorize(name), 'level': level_of(name),
        })

    byp = Counter(r['province'] for r in rows)
    print('Gán được tỉnh:', len(rows), '| số tỉnh phủ:', len(byp))
    print('Top:', byp.most_common(5))

    # 4. SQL
    emit_sql(rows, os.path.join(args.workdir, 'osm_agencies_all.sql'))
    print('XONG.')


if __name__ == '__main__':
    main()
