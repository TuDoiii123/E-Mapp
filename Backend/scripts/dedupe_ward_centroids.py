"""
Dedupe marker UBND cấp xã: xã nào đã có UBND THẬT (toạ độ trụ sở — từ OSM hoặc
seed) thì bỏ dòng UBND centroid tổng hợp (id 'th-x-<ward_code>') của xã đó,
đồng thời CHUYỂN ward + ward_code 2025 sang dòng thật (giữ filter xã hoạt động).

Match theo tên xã trong tên cơ quan ('UBND xã Vĩnh Hùng' ↔ ward 'Vĩnh Hùng'),
có guard khoảng cách ≤ MAX_KM để không dính xã trùng tên ở khu vực khác
(vd 'Phường Lam Sơn' cũ ở TP Thanh Hóa ≠ xã Lam Sơn 2025 ở Thọ Xuân, cách ~40km).

Chạy:  python scripts/dedupe_ward_centroids.py --input <file> [--out <sql>]
  input: mỗi dòng 'id|name|ward|ward_code|lat|lng' (UBND thật) hoặc
         'id|ward|ward_code|lat|lng' (dòng th-x-*), lấy từ ds_dichvucong.
Xuất SQL: UPDATE dòng thật (ward, ward_code) + DELETE dòng centroid (2 bảng).
"""
import argparse
import math
import re
import unicodedata

MAX_KM = 12.0  # trụ sở xã cách centroid xã của nó hiếm khi quá ~10km


def strip_dia(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('đ', 'd').replace('Đ', 'D').lower().strip()


def ward_part(name):
    """'UBND xã Vĩnh Hùng' -> 'vinh hung' (None nếu không tách được)."""
    n = strip_dia(name)
    m = re.match(r'^ubnd\s+(xa|phuong|thi tran)\s+(.+)$', n)
    if not m:
        return None
    return re.sub(r'\s*\(.*\)$', '', m.group(2)).strip()


def haversine_km(lat1, lng1, lat2, lng2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def esc(s):
    return (s or '').replace("'", "''")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', default='dedupe_ward_centroids.sql')
    args = ap.parse_args()

    reals, cents = [], []
    for line in open(args.input, encoding='utf-8'):
        parts = line.rstrip('\n').split('|')
        if len(parts) == 6:
            i, name, w, wc, lat, lng = parts
            reals.append({'id': i, 'name': name, 'ward': w, 'ward_code': wc,
                          'lat': float(lat), 'lng': float(lng)})
        elif len(parts) == 5 and parts[0].startswith('th-x-'):
            i, w, wc, lat, lng = parts
            cents.append({'id': i, 'ward': w, 'ward_code': wc,
                          'lat': float(lat), 'lng': float(lng)})

    # tên xã 2025 trùng nhau trong tỉnh → bỏ qua (không dám match)
    from collections import Counter
    dup_names = {n for n, c in Counter(strip_dia(c['ward']) for c in cents).items() if c > 1}

    sql, deleted, updated = [], [], 0
    for c in cents:
        wname = strip_dia(c['ward'])
        if not wname or wname in dup_names:
            continue
        matches = [r for r in reals
                   if ward_part(r['name']) == wname
                   and haversine_km(r['lat'], r['lng'], c['lat'], c['lng']) <= MAX_KM]
        if not matches:
            continue
        for r in matches:  # dòng thật nhận ward/ward_code 2025 (nếu chưa khớp)
            if r['ward'] != c['ward'] or r['ward_code'] != c['ward_code']:
                sql.append(
                    f"UPDATE ds_dichvucong SET ward='{esc(c['ward'])}', ward_code='{esc(c['ward_code'])}' "
                    f"WHERE id='{esc(r['id'])}';")
                sql.append(
                    f"UPDATE agencies SET ward='{esc(c['ward'])}' WHERE id='{esc(r['id'])}';")
                updated += 1
        sql.append(f"DELETE FROM ds_dichvucong WHERE id='{esc(c['id'])}';")
        sql.append(f"DELETE FROM agencies WHERE id='{esc(c['id'])}';")
        deleted.append((c['id'], c['ward'], [m['id'] for m in matches]))

    out = "SET client_encoding='UTF8';\nBEGIN;\n" + "\n".join(sql) + "\nCOMMIT;\n"
    open(args.out, 'w', encoding='utf-8').write(out)
    print(f"Centroid xoá: {len(deleted)} | dòng thật gán ward: {updated}")
    for cid, w, mids in deleted:
        print(f"  {cid} ({w}) <- giữ {', '.join(mids)}")
    print('->', args.out)


if __name__ == '__main__':
    main()
