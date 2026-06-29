"""
Seed cache PDF preview của template vào Postgres (bảng template_pdf_cache).

Chạy MỘT LẦN ở máy có engine convert (LibreOffice/Word). Script convert toàn bộ
template .doc/.docx trong data/templates/ rồi upsert PDF (BYTEA) vào DB shared.
Sau đó production — nơi không có engine — đọc PDF trực tiếp từ DB.

Idempotent: chạy lại chỉ cập nhật bản đã đổi nội dung (so theo MD5).

Chạy: python scripts/seed_pdf_cache.py
"""
import sys
import os
import hashlib

# Console Windows (cp1252) không in được tiếng Việt → ép UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(override=True)

_TEMPLATES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
)
_EXTS = ('.doc', '.docx')


def seed_all():
    from flask import Flask
    from models.db import init_db
    from services.pdf_converter import word_to_pdf, is_available
    from services import pdf_cache_db

    if not is_available():
        print('❌ Không tìm thấy engine convert (LibreOffice/Word). '
              'Chạy script này ở máy có engine.')
        sys.exit(1)

    if not os.path.isdir(_TEMPLATES_DIR):
        print(f'❌ Không thấy thư mục template: {_TEMPLATES_DIR}')
        sys.exit(1)

    files = sorted(
        f for f in os.listdir(_TEMPLATES_DIR)
        if f.lower().endswith(_EXTS)
    )
    print(f'Tìm thấy {len(files)} template (.doc/.docx)\n')

    app = Flask(__name__)
    init_db(app)

    ok = 0
    fail = 0
    total_bytes = 0
    with app.app_context():
        for fn in files:
            fpath = os.path.join(_TEMPLATES_DIR, fn)
            try:
                with open(fpath, 'rb') as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()

                # Bỏ qua nếu DB đã có bản đúng hash
                meta = pdf_cache_db.get_meta(fn)
                if meta and meta.get('content_hash') == content_hash:
                    print(f'  = skip (đã có): {fn}')
                    ok += 1
                    continue

                pdf_path = word_to_pdf(fpath)
                if not (pdf_path and os.path.exists(pdf_path)):
                    print(f'  ✗ convert thất bại: {fn}')
                    fail += 1
                    continue

                with open(pdf_path, 'rb') as pf:
                    pdf_bytes = pf.read()

                if pdf_cache_db.put_pdf(fn, content_hash, pdf_bytes):
                    total_bytes += len(pdf_bytes)
                    ok += 1
                    print(f'  ✓ {fn}  ({len(pdf_bytes)//1024} KB)')
                else:
                    fail += 1
                    print(f'  ✗ ghi DB thất bại: {fn}')
            except Exception as e:
                fail += 1
                print(f'  ✗ lỗi {fn}: {e}')

    print(f'\nDone. OK={ok} Fail={fail}  Tổng PDF ghi mới ≈ {total_bytes//1024} KB')


if __name__ == '__main__':
    seed_all()
