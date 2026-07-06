"""
Sinh UBND cấp xã (mô hình 2025) cho 1 tỉnh từ ranh giới xã của repo thanglequoc,
toạ độ = centroid (shoelace trên polygon lớn nhất) — KHÔNG cần geocode → không rate-limit.

Nguồn: json/geojson/<slug>/wards/<ward_code>_<ten>.geojson — mỗi file 1 Feature,
properties.code khớp bảng `wards` → ward + ward_code chuẩn 2025.

Chạy:  cd Backend && python scripts/build_ward_ubnd_centroids.py            # Thanh Hoá
       python scripts/build_ward_ubnd_centroids.py --slug 1_thu_do_ha_noi --province "Hà Nội"
Import: pipe file th_ubnd_xa.sql (hoặc <slug>_ubnd_xa.sql) vào psql như k8s/README.md.

Lưu ý: centroid là TÂM HÌNH HỌC của xã, không phải trụ sở thật — chấp nhận cho demo;
khi có toạ độ trụ sở thật (OSM/khảo sát) thì UPDATE đè sau.
"""
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request

TREE_API = ("https://api.github.com/repos/thanglequoc/vietnamese-provinces-database"
            "/git/trees/master?recursive=1")
RAWBASE = "https://raw.githubusercontent.com/thanglequoc/vietnamese-provinces-database/master/"
UA = 'E-Mapp/1.0 (ward centroid; contact tu.bui@huvisoft.com)'


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8')


def fetch_cached(url, fp):
    """GET với cache đĩa + retry/backoff — chạy lại không refetch."""
    if os.path.exists(fp) and os.path.getsize(fp) > 50:
        with open(fp, encoding='utf-8') as f:
            return json.load(f)
    last = None
    for attempt in range(5):
        try:
            raw = http_get(url)
            d = json.loads(raw)
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(raw)
            return d
        except Exception as e:
            last = e
            wait = 2 ** attempt
            print(f'  fetch lỗi {os.path.basename(fp)} ({e}); thử lại {wait}s [{attempt + 1}/5]', flush=True)
            time.sleep(wait)
    print('  BỎ QUA', url, last)
    return None


def ring_area_centroid(ring):
    """Shoelace: trả (area_signed, cx, cy)."""
    a = cx = cy = 0.0
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i][0], ring[i][1]
        x1, y1 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    if abs(a) < 1e-12:  # suy biến → trung bình đỉnh
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        return 0.0, sum(xs) / n, sum(ys) / n
    return a, cx / (6 * a), cy / (6 * a)


def centroid_of(gj):
    """Centroid polygon lớn nhất trong Feature/FeatureCollection → (lng, lat)."""
    feats = gj.get('features', [gj] if gj.get('type') == 'Feature' else [])
    best = None
    for feat in feats:
        g = feat.get('geometry') or {}
        typ, coords = g.get('type'), g.get('coordinates') or []
        polys = coords if typ == 'MultiPolygon' else ([coords] if typ == 'Polygon' else [])
        for poly in polys:
            if not poly or not poly[0]:
                continue
            a, cx, cy = ring_area_centroid(poly[0])
            if best is None or abs(a) > best[0]:
                best = (abs(a), cx, cy)
    return (best[1], best[2]) if best else None


def esc(s):
    return (s or '').replace("'", "''")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', default='38_thanh_hoa',
                    help='thư mục tỉnh trong json/geojson/ (mặc định 38_thanh_hoa)')
    ap.add_argument('--province', default='Thanh Hoá',
                    help='tên tỉnh ghi vào cột province (khớp bảng provinces)')
    ap.add_argument('--prefix', default=None,
                    help='prefix id cơ quan (mặc định: th-x- cho Thanh Hoá, <mã tỉnh>-x- cho tỉnh khác)')
    ap.add_argument('--workdir', default=os.path.join(os.path.dirname(__file__), 'ward_centroid_work'))
    args = ap.parse_args()
    os.makedirs(args.workdir, exist_ok=True)
    cache = os.path.join(args.workdir, f'ward_cache_{args.slug}')
    os.makedirs(cache, exist_ok=True)
    prefix = args.prefix or ('th-x-' if args.slug == '38_thanh_hoa' else f"{args.slug.split('_')[0]}-x-")

    # danh sách file ward của tỉnh (GitHub tree API, cache)
    tree_fp = os.path.join(args.workdir, 'repo_tree.json')
    tree = fetch_cached(TREE_API, tree_fp)
    if not tree:
        raise SystemExit('Không lấy được cây repo')
    want = f'json/geojson/{args.slug}/wards/'
    paths = sorted(t['path'] for t in tree['tree']
                   if t['type'] == 'blob' and t['path'].startswith(want) and t['path'].endswith('.geojson'))
    print(f'{args.slug}: {len(paths)} xã', flush=True)

    rows = []
    for i, path in enumerate(paths, 1):
        gj = fetch_cached(RAWBASE + urllib.parse.quote(path), os.path.join(cache, os.path.basename(path)))
        if not gj:
            continue
        feat = gj['features'][0] if gj.get('type') == 'FeatureCollection' else gj
        props = feat.get('properties', {})
        code, name = props.get('code'), props.get('name') or ''
        full = props.get('fullName') or name
        c = centroid_of(gj)
        if not c or not code:
            print('  bỏ qua (thiếu centroid/code):', path); continue
        lng, lat = c
        rows.append({
            'id': f'{prefix}{code}', 'name': f'UBND {full}',
            'address': f'{full}, {args.province}',
            'lat': round(lat, 6), 'lng': round(lng, 6),
            'ward': name, 'ward_code': str(code),
        })
        if i % 40 == 0:
            print(f'  ...{i}/{len(paths)}', flush=True)
    print('Sinh được UBND xã:', len(rows), '/', len(paths))

    out_fp = os.path.join(args.workdir, f'{args.slug}_ubnd_xa.sql')
    out = [
        "SET client_encoding='UTF8';\n"
        f"-- UBND cấp xã {args.province} (centroid ranh giới xã 2025) — build_ward_ubnd_centroids.py\n"
        "ALTER TABLE agencies ADD COLUMN IF NOT EXISTS ward VARCHAR(100) NOT NULL DEFAULT '';\n"
        "ALTER TABLE ds_dichvucong ADD COLUMN IF NOT EXISTS ward_code VARCHAR(20);\n"
        "BEGIN;\n"
    ]
    for r in rows:
        out.append(
            "INSERT INTO agencies (id,name,address,ward,district,province,latitude,longitude,level,is_active) "
            f"VALUES ('{esc(r['id'])}','{esc(r['name'])}','{esc(r['address'])}','{esc(r['ward'])}',"
            f"'','{esc(args.province)}',{r['lat']},{r['lng']},'ward',TRUE) "
            "ON CONFLICT (id) DO NOTHING;")
        out.append(
            "INSERT INTO ds_dichvucong (id,name,description,category_id,address,latitude,longitude,level,status,province,district,ward,ward_code) "
            f"VALUES ('{esc(r['id'])}','{esc(r['name'])}','{esc(r['name'])}','ubnd','{esc(r['address'])}',"
            f"{r['lat']},{r['lng']},'ward','normal','{esc(args.province)}','','{esc(r['ward'])}','{esc(r['ward_code'])}') "
            "ON CONFLICT (id) DO NOTHING;")
    out.append("COMMIT;\n")
    with open(out_fp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print('->', out_fp, f'({len(rows)} cơ quan)')


if __name__ == '__main__':
    main()
