"""
So sánh ds_dvc_tructuyen với procedures để tìm loại thủ tục chưa có.
"""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # 1. Danh sách procedures hiện có
    existing = db.session.execute(text(
        "SELECT id, name, category FROM public.procedures ORDER BY category, name"
    )).fetchall()
    existing_ids = {r.id for r in existing}
    existing_names_lower = {r.name.lower().strip() for r in existing}

    print(f"=== PROCEDURES HIEN CO: {len(existing)} ===")
    for r in existing:
        print(f"  [{r.category}] {r.id} -- {r.name}")

    # 2. Danh sách DVC trực tuyến (ds_dvc_tructuyen), bỏ header row
    dvc = db.session.execute(text(
        "SELECT tthc_ma, name, url_chi_tiet FROM public.ds_dvc_tructuyen "
        "WHERE tthc_ma != 'tthc_ma' ORDER BY name"
    )).fetchall()

    print(f"\n=== DS DVC TRUC TUYEN: {len(dvc)} entries ===")

    # 3. Tìm những DVC chưa có trong procedures (theo tthc_ma)
    missing_by_ma = [r for r in dvc if r.tthc_ma not in existing_ids]

    # 4. Group theo tên thủ tục (bỏ duplicate tthc_ma)
    seen_ma = set()
    unique_missing = []
    for r in missing_by_ma:
        if r.tthc_ma not in seen_ma:
            seen_ma.add(r.tthc_ma)
            unique_missing.append(r)

    print(f"\n=== CHUA CO TRONG PROCEDURES ({len(unique_missing)} unique ma) ===")

    # Phân nhóm theo lĩnh vực từ URL
    def guess_category(url: str, name: str) -> str:
        u = (url or '').lower()
        n = (name or '').lower()
        if any(k in u or k in n for k in ['ho-tich', 'khai-sinh', 'ket-hon', 'khai-tu', 'hon-nhan', 'nuoc-ngoai']):
            return 'civil'
        if any(k in u or k in n for k in ['can-cuoc', 'cccd', 'cu-tru', 'thuong-tru', 'tam-tru']):
            return 'civil'
        if any(k in u or k in n for k in ['kinh-doanh', 'doanh-nghiep', 'thuong-mai', 'dang-ky-kinh']):
            return 'business'
        if any(k in u or k in n for k in ['xay-dung', 'cong-trinh', 'quy-hoach']):
            return 'construction'
        if any(k in u or k in n for k in ['dat-dai', 'quyen-su-dung', 'so-do', 'so-hong', 'tai-nguyen']):
            return 'land'
        if any(k in u or k in n for k in ['giao-thong', 'lai-xe', 'phuong-tien', 'van-tai', 'dang-kiem']):
            return 'transport'
        if any(k in u or k in n for k in ['tu-phap', 'ly-lich', 'cong-chung', 'chung-thuc']):
            return 'justice'
        if any(k in u or k in n for k in ['thue', 'thu-phi', 'ngan-sach']):
            return 'tax'
        if any(k in u or k in n for k in ['bhxh', 'bao-hiem', 'lao-dong', 'viec-lam']):
            return 'insurance'
        if any(k in u or k in n for k in ['y-te', 'suc-khoe', 'duoc', 'benh-vien']):
            return 'health'
        if any(k in u or k in n for k in ['giao-duc', 'truong', 'hoc', 'bang-cap']):
            return 'education'
        return 'other'

    by_cat = {}
    for r in unique_missing:
        cat = guess_category(r.url_chi_tiet, r.name)
        by_cat.setdefault(cat, []).append(r)

    for cat in sorted(by_cat.keys()):
        items = by_cat[cat]
        print(f"\n  [{cat}] ({len(items)} thủ tục)")
        for r in items:
            print(f"    [{r.tthc_ma}] {r.name[:80]}")

    print(f"\n=== TONG KET ===")
    print(f"  Procedures hien co: {len(existing)}")
    print(f"  DVC truc tuyen (unique ma): {len(seen_ma) + len(existing_ids.intersection({r.tthc_ma for r in dvc}))}")
    print(f"  Chua co trong procedures: {len(unique_missing)}")
    print(f"  Da co (khop tthc_ma): {len(existing_ids.intersection({r.tthc_ma for r in dvc}))}")

    # 5. Thủ tục nào trong procedures có tthc_ma trùng DVC
    matched = [(r.tthc_ma, r.name) for r in dvc if r.tthc_ma in existing_ids]
    seen_matched = set()
    print(f"\n=== DA CO TRONG PROCEDURES (khop theo ID) ===")
    for ma, nm in matched:
        if ma not in seen_matched:
            seen_matched.add(ma)
            print(f"  [{ma}] {nm[:70]}")
