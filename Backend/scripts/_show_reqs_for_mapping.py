import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

NEED_TEMPLATES = [
    'cap-ban-sao-trich-luc-ho-tich',
    'cap-phieu-lltp-so2',
    'cap-so-bhxh-the-bhyt',
    'cap-tai-khoan-dinh-danh',
    'chung-thuc-ban-sao',
    'chuyen-nhuong-quyen-su-dung-dat',
    'dang-ky-bhxh-bhyt',
    'dang-ky-bien-dong-dat-dai',
    'dang-ky-lai-khai-sinh',
    'dang-ky-nhan-con',
    'dang-ky-tam-tru',
    'dang-ky-xe-moto',
    'doi-cap-lai-gplx',
    'giai-the-doanh-nghiep',
    'hoan-cong-cong-trinh',
    'tach-ho-khau',
    'tach-thua-dat',
    'tam-ngung-kinh-doanh',
    'thay-doi-canh-chinh-ho-tich',
    'thay-doi-noi-dung-dkdn',
]

with app.app_context():
    for sid in NEED_TEMPLATES:
        rows = db.session.execute(text("""
            SELECT id, doc_name, template_file, order_index
            FROM service_requirements
            WHERE service_id = :sid
            ORDER BY order_index
        """), {'sid': sid}).fetchall()
        print(f"\n[{sid}]")
        for r in rows:
            tmpl = r.template_file or '(none)'
            print(f"  {r.id[:40]:40s} {r.doc_name[:60]:60s} => {tmpl}")
