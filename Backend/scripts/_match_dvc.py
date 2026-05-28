"""
Tìm dữ liệu steps/conditions từ chitiet_dvc_tructuyen cho các procedure slug-ID còn thiếu.
"""
import sys, re
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

MISSING_IDS = [
    'cap-doi-cccd',
    'dang-ky-ket-hon',
    'dang-ky-khai-sinh',
    'dang-ky-khai-tu',
    'dang-ky-thuong-tru',
    'dang-ky-ho-kinh-doanh',
    'cap-giay-phep-xay-dung',
    'cap-phieu-lltp',
    'cap-gcn-quyen-su-dung-dat',
    'cap-gplx',
]

# keywords để tìm trong ds_dvc_tructuyen
KEYWORDS = {
    'cap-doi-cccd':              ['căn cước công dân', 'cccd', 'cấp thẻ căn cước'],
    'dang-ky-ket-hon':           ['đăng ký kết hôn'],
    'dang-ky-khai-sinh':         ['đăng ký khai sinh'],
    'dang-ky-khai-tu':           ['đăng ký khai tử'],
    'dang-ky-thuong-tru':        ['đăng ký thường trú'],
    'dang-ky-ho-kinh-doanh':     ['hộ kinh doanh', 'đăng ký hộ kinh doanh'],
    'cap-giay-phep-xay-dung':    ['giấy phép xây dựng', 'cấp phép xây dựng'],
    'cap-phieu-lltp':            ['lý lịch tư pháp', 'phiếu lý lịch'],
    'cap-gcn-quyen-su-dung-dat': ['giấy chứng nhận quyền sử dụng đất', 'sổ đỏ', 'gcn quyền sử dụng'],
    'cap-gplx':                  ['giấy phép lái xe', 'gplx'],
}

with app.app_context():
    # Lấy tất cả từ ds_dvc_tructuyen (có tên + url)
    all_dvc = db.session.execute(text(
        "SELECT tthc_ma, name, url_chi_tiet FROM public.ds_dvc_tructuyen"
    )).fetchall()

    for proc_id in MISSING_IDS:
        kws = KEYWORDS[proc_id]
        # Tìm match theo tên (case insensitive)
        matches = [r for r in all_dvc
                   if any(kw.lower() in (r.name or '').lower() for kw in kws)]
        print(f"\n{'='*70}")
        print(f"PROC: {proc_id}  ({len(matches)} matches)")
        for m in matches[:5]:
            print(f"  [{m.tthc_ma}] {m.name[:80]}")
            # Lấy chi tiết từ chitiet_dvc_tructuyen theo URL
            detail = db.session.execute(text(
                "SELECT trinh_tu_thuc_hien, yeu_cau_dieu_kien_thuc_hien "
                "FROM public.chitiet_dvc_tructuyen WHERE url_chi_tiet = :url LIMIT 1"
            ), {'url': m.url_chi_tiet}).fetchone()
            if detail:
                steps_preview = (detail.trinh_tu_thuc_hien or '')[:200].replace('\n', ' | ')
                cond_preview  = (detail.yeu_cau_dieu_kien_thuc_hien or '')[:150].replace('\n', ' | ')
                print(f"    steps  : {steps_preview}")
                print(f"    cond   : {cond_preview}")
            else:
                print(f"    [no chitiet found for url: {m.url_chi_tiet[:60]}]")
