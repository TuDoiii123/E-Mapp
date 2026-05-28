"""Dump toàn bộ URL chitiet_thutuc để xem có thủ tục nào phù hợp không."""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # Xem tất cả URL trong chitiet_thutuc (bỏ dòng header)
    rows = db.session.execute(text(
        "SELECT url_chi_tiet, trinh_tu_cach_thuc_thuc_hien, yeu_cau_hoac_dieu_kien_de_thuc_hien_tthc "
        "FROM public.chitiet_thutuc ORDER BY url_chi_tiet"
    )).fetchall()
    print(f"chitiet_thutuc: {len(rows)} rows\n")
    for r in rows:
        url = r.url_chi_tiet or ''
        if url == 'URL_Chi_Tiet' or not url:
            continue
        has_steps = bool((r.trinh_tu_cach_thuc_thuc_hien or '').strip()
                         and 'ten_file' not in (r.trinh_tu_cach_thuc_thuc_hien or ''))
        print(f"  {'[S]' if has_steps else '[ ]'}  {url[:100]}")

    print("\n\n=== SEARCH TRONG chitiet_dvc_tructuyen (keyword trong steps text) ===")
    # Tìm các thủ tục chưa có trong ds_dvc_tructuyen nhưng có content phù hợp
    missing_kw = {
        'khai-tu':    ['khai tử', 'đăng ký khai tử'],
        'thuong-tru': ['đăng ký thường trú', 'cư trú'],
        'ho-kinh-doanh': ['hộ kinh doanh'],
        'xay-dung':   ['giấy phép xây dựng nhà ở', 'cấp phép xây dựng'],
        'qsd-dat':    ['quyền sử dụng đất', 'giấy chứng nhận quyền'],
        'lai-xe':     ['giấy phép lái xe', 'đào tạo lái xe'],
        'cccd':       ['cấp thẻ căn cước', 'cấp mới căn cước', 'căn cước công dân lần đầu'],
    }
    all_dc = db.session.execute(text(
        "SELECT url_chi_tiet, trinh_tu_thuc_hien, yeu_cau_dieu_kien_thuc_hien "
        "FROM public.chitiet_dvc_tructuyen"
    )).fetchall()
    for label, kws in missing_kw.items():
        matches = [r for r in all_dc
                   if any(kw.lower() in (r.trinh_tu_thuc_hien or '').lower()
                          or kw.lower() in (r.url_chi_tiet or '').lower()
                          for kw in kws)]
        if matches:
            print(f"\n[{label}] {len(matches)} matches in chitiet_dvc_tructuyen:")
            seen = set()
            for r in matches:
                if r.url_chi_tiet in seen: continue
                seen.add(r.url_chi_tiet)
                # Find name from ds_dvc_tructuyen
                nm = db.session.execute(text(
                    "SELECT name FROM public.ds_dvc_tructuyen WHERE url_chi_tiet=:u LIMIT 1"
                ), {'u': r.url_chi_tiet}).scalar() or '?'
                print(f"  {nm[:70]}")
                print(f"    steps: {(r.trinh_tu_thuc_hien or '')[:150].replace(chr(10),' | ')}")
                if len(seen) >= 3: break
