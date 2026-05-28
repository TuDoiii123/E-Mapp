"""Tìm kiếm rộng trong chitiet_thutuc và chitiet_dvc_tructuyen."""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

SEARCHES = {
    'cap-doi-cccd':              ['căn cước', 'CCCD', 'cấp thẻ'],
    'dang-ky-khai-tu':           ['khai tử', 'khai_tử', 'tử'],
    'dang-ky-thuong-tru':        ['thường trú', 'thường_trú', 'đăng ký cư trú', 'đăng ký thường'],
    'dang-ky-ho-kinh-doanh':     ['hộ kinh doanh', 'kinh doanh'],
    'cap-giay-phep-xay-dung':    ['xây dựng', 'giấy phép xây'],
    'cap-phieu-lltp':            ['lý lịch tư pháp', 'phiếu lý lịch', 'LLTP'],
    'cap-gcn-quyen-su-dung-dat': ['quyền sử dụng đất', 'sử dụng đất', 'chứng nhận quyền'],
    'cap-gplx':                  ['lái xe', 'giấy phép lái', 'GPLX'],
}

with app.app_context():
    # chitiet_thutuc: có url_chi_tiet và full text
    all_ct = db.session.execute(text(
        "SELECT url_chi_tiet, trinh_tu_cach_thuc_thuc_hien, yeu_cau_hoac_dieu_kien_de_thuc_hien_tthc "
        "FROM public.chitiet_thutuc"
    )).fetchall()

    # ds_dvc_tructuyen: tthc_ma + name + url
    all_dvc = db.session.execute(text(
        "SELECT tthc_ma, name, url_chi_tiet FROM public.ds_dvc_tructuyen"
    )).fetchall()

    for proc_id, kws in SEARCHES.items():
        print(f"\n{'='*70}\nPROC: {proc_id}")

        # 1. Tìm trong ds_dvc_tructuyen theo tên
        matches = [(r.tthc_ma, r.name, r.url_chi_tiet)
                   for r in all_dvc
                   if any(kw.lower() in (r.name or '').lower() for kw in kws)]

        seen_urls = set()
        unique = []
        for ma, nm, url in matches:
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append((ma, nm, url))

        print(f"  ds_dvc_tructuyen matches: {len(matches)} ({len(unique)} unique)")
        for ma, nm, url in unique[:3]:
            print(f"    [{ma}] {nm[:70]}")
            detail = db.session.execute(text(
                "SELECT trinh_tu_thuc_hien, yeu_cau_dieu_kien_thuc_hien "
                "FROM public.chitiet_dvc_tructuyen WHERE url_chi_tiet=:u LIMIT 1"
            ), {'u': url}).fetchone()
            if detail and detail.trinh_tu_thuc_hien:
                print(f"      steps: {(detail.trinh_tu_thuc_hien or '')[:120].replace(chr(10),' | ')}")
                print(f"      cond : {(detail.yeu_cau_dieu_kien_thuc_hien or '')[:100].replace(chr(10),' | ')}")
            else:
                print(f"      [no detail found]")

        # 2. Tìm trong chitiet_thutuc theo url (url chứa keyword từ tên thủ tục)
        url_kws = {
            'cap-doi-cccd':   ['can-cuoc', 'cccd', 'the-can-cuoc'],
            'dang-ky-khai-tu': ['khai-tu', 'khai_tu'],
            'dang-ky-thuong-tru': ['thuong-tru', 'thuong_tru', 'cu-tru'],
            'dang-ky-ho-kinh-doanh': ['ho-kinh-doanh', 'kinh-doanh'],
            'cap-giay-phep-xay-dung': ['xay-dung', 'phep-xay'],
            'cap-phieu-lltp': ['ly-lich-tu-phap', 'lltp'],
            'cap-gcn-quyen-su-dung-dat': ['quyen-su-dung-dat', 'gcn-qsd'],
            'cap-gplx': ['lai-xe', 'gplx'],
        }
        uk = url_kws.get(proc_id, [])
        ct_matches = [r for r in all_ct
                      if any(k in (r.url_chi_tiet or '').lower() for k in uk)]
        if ct_matches:
            print(f"  chitiet_thutuc URL matches: {len(ct_matches)}")
            for r in ct_matches[:2]:
                print(f"    url: {r.url_chi_tiet[:70]}")
                print(f"    steps: {(r.trinh_tu_cach_thuc_thuc_hien or '')[:120].replace(chr(10),' | ')}")
                print(f"    cond : {(r.yeu_cau_hoac_dieu_kien_de_thuc_hien_tthc or '')[:100].replace(chr(10),' | ')}")
