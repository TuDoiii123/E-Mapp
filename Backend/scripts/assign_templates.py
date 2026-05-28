"""
Gán template_file cho service_requirements theo từng procedure.
Chỉ UPDATE, không INSERT/DELETE.
Dùng WHERE id = '...' để chính xác.
"""
import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

# Mapping: req_id → template_file
ASSIGNMENTS = [
    # ── Hộ tịch ──────────────────────────────────────────────────────────────
    ('cap-ban-sao-trich-luc-ho-tich-req-000',
     'mau-to-khai-cap-ban-sao-trich-luc-ho-tich.docx'),

    ('dang-ky-lai-khai-sinh-req-000',
     'mau-to-khai-dang-ky-lai-khai-sinh.docx'),

    ('dang-ky-nhan-con-req-000',
     'mau-to-khai-nhan-cha-me-con.doc'),

    ('thay-doi-canh-chinh-ho-tich-req-000',
     'mau-to-khai-thay-doi-cai-chinh-ho-tich.doc'),

    # ── Cư trú ───────────────────────────────────────────────────────────────
    ('dang-ky-tam-tru-req-000',
     'mau-CT01-to-khai-cu-tru.doc'),

    ('tach-ho-khau-req-000',
     'mau-CT01-to-khai-cu-tru.doc'),

    # ── Lý lịch tư pháp ──────────────────────────────────────────────────────
    ('cap-phieu-lltp-so2-req-001',
     'mau-phieu-ly-lich-tu-phap-so2.doc'),

    # ── Đất đai ──────────────────────────────────────────────────────────────
    ('dang-ky-bien-dong-dat-dai-req-002',
     'mau-don-dang-ky-bien-dong-dat-dai.doc'),

    ('tach-thua-dat-req-001',
     'mau-don-tach-thua-hop-thua-dat.docx'),

    # Chuyển nhượng: tờ khai lệ phí trước bạ + đơn biến động
    ('chuyen-nhuong-quyen-su-dung-dat-req-003',
     'mau-to-khai-le-phi-truoc-ba.docx'),

    # ── Doanh nghiệp ─────────────────────────────────────────────────────────
    ('thay-doi-noi-dung-dkdn-req-000',
     'mau-thong-bao-thay-doi-noi-dung-dkdn.docx'),

    ('giai-the-doanh-nghiep-req-000',
     'mau-giai-the-doanh-nghiep.docx'),

    ('tam-ngung-kinh-doanh-req-000',
     'mau-thong-bao-thay-doi-noi-dung-dkdn.docx'),

    # ── Giao thông ───────────────────────────────────────────────────────────
    ('doi-cap-lai-gplx-req-000',
     'mau-don-de-nghi-cap-doi-gplx.docx'),

    ('doi-cap-lai-gplx-req-003',
     'mau-giay-kham-suc-khoe-lai-xe.doc'),

    ('dang-ky-xe-moto-req-000',
     'mau-khai-dang-ky-xe-co-gioi.docx'),

    # ── Bảo hiểm ─────────────────────────────────────────────────────────────
    ('dang-ky-bhxh-bhyt-req-000',
     'mau-to-khai-tham-gia-bhxh-bhyt.doc'),

    ('cap-so-bhxh-the-bhyt-req-000',
     'mau-to-khai-tham-gia-bhxh-bhyt.doc'),

    ('cap-so-bhxh-the-bhyt-req-002',
     'mau-to-khai-cap-the-bao-hiem-y-te.docx'),
]

with app.app_context():
    import os
    tdir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'templates'))

    updated = 0
    skipped = 0
    missing_file = []

    for req_id, tmpl in ASSIGNMENTS:
        # Kiểm tra file tồn tại
        fpath = os.path.join(tdir, tmpl)
        if not os.path.exists(fpath):
            missing_file.append((req_id, tmpl))
            print(f"  SKIP (no file) {req_id} => {tmpl}")
            continue

        # Kiểm tra req tồn tại
        row = db.session.execute(text(
            "SELECT id, template_file FROM service_requirements WHERE id = :rid"
        ), {'rid': req_id}).fetchone()

        if not row:
            print(f"  SKIP (req not found) {req_id}")
            skipped += 1
            continue

        if row.template_file == tmpl:
            print(f"  ALREADY {req_id}")
            continue

        db.session.execute(text(
            "UPDATE service_requirements SET template_file = :tmpl WHERE id = :rid"
        ), {'tmpl': tmpl, 'rid': req_id})
        print(f"  + SET {req_id[:55]:55s} => {tmpl}")
        updated += 1

    db.session.commit()

    print(f"\n=== Ket qua ===")
    print(f"  Updated:       {updated}")
    print(f"  Skipped:       {skipped}")
    print(f"  Missing file:  {len(missing_file)}")
    if missing_file:
        for rid, f in missing_file:
            print(f"    - {f}")

    # Tong ket
    total_with = db.session.execute(text(
        "SELECT COUNT(*) FROM service_requirements WHERE template_file IS NOT NULL AND template_file != ''"
    )).scalar()
    total_all = db.session.execute(text(
        "SELECT COUNT(*) FROM service_requirements"
    )).scalar()
    print(f"\n  Requirements co template: {total_with}/{total_all}")
