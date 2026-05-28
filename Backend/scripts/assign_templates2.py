"""
Gan template_file bo sung cho cac requirements chua co.
"""
import sys, os
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

TDIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'templates'))

ASSIGNMENTS = [
    # Tạm trú — dùng CT02 thay vì CT01
    ('dang-ky-tam-tru-req-000',      'mau-CT02-to-khai-tam-tru.docx'),

    # Hoàn công — mới tạo
    ('hoan-cong-cong-trinh-req-000', 'mau-thong-bao-hoan-cong-cong-trinh.docx'),

    # Chứng thực bản sao
    ('chung-thuc-ban-sao-req-000',   'mau-don-yeu-cau-chung-thuc-ban-sao.docx'),

    # Tạm ngừng KD — dùng mẫu II-19 riêng
    ('tam-ngung-kinh-doanh-req-000', 'mau-thong-bao-tam-ngung-kinh-doanh.docx'),

    # BHXH — thêm TK1-TS chi tiết hơn
    ('dang-ky-bhxh-bhyt-req-000',    'mau-TK1-TS-to-khai-tham-gia-bhxh-bhyt.docx'),
    ('cap-so-bhxh-the-bhyt-req-000', 'mau-TK1-TS-to-khai-tham-gia-bhxh-bhyt.docx'),

    # Đăng ký xe máy — mẫu riêng cho xe máy
    ('dang-ky-xe-moto-req-000',      'mau-to-khai-dang-ky-xe-may-lan-dau.docx'),

    # D02-LT cho BHXH
    ('dang-ky-bhxh-bhyt-req-003',    'mau-D02-LT-danh-sach-lao-dong-bhxh.docx'),
]

with app.app_context():
    updated = 0
    for req_id, tmpl in ASSIGNMENTS:
        if not os.path.exists(os.path.join(TDIR, tmpl)):
            print(f'  SKIP (no file) {tmpl}')
            continue
        row = db.session.execute(text(
            'SELECT id, template_file FROM service_requirements WHERE id = :rid'
        ), {'rid': req_id}).fetchone()
        if not row:
            print(f'  SKIP (req not found) {req_id}')
            continue
        if row.template_file == tmpl:
            print(f'  ALREADY {req_id}')
            continue
        db.session.execute(text(
            'UPDATE service_requirements SET template_file = :t WHERE id = :r'
        ), {'t': tmpl, 'r': req_id})
        old = row.template_file or '(none)'
        print(f'  + {req_id[:50]:50s} {old} -> {tmpl}')
        updated += 1

    db.session.commit()
    total = db.session.execute(text(
        "SELECT COUNT(*) FROM service_requirements WHERE template_file IS NOT NULL AND template_file != ''"
    )).scalar()
    print(f'\nUpdated: {updated} | Total with template: {total}')
