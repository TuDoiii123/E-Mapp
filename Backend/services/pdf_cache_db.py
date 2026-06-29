"""
Tầng truy cập DB cho cache PDF preview của template.

Lưu PDF (đã convert từ Word) dạng BYTEA trong bảng `public.template_pdf_cache`
để production — nơi không có LibreOffice/Word — vẫn phục vụ được preview.

Mọi hàm an toàn với lỗi DB: trả None / no-op + log warning, KHÔNG raise, để
đường preview luôn có thể fallback sang convert local / cache đĩa / file Word.
"""
from models.db import db
from sqlalchemy import text
from logger import get_logger

log = get_logger('pdf_cache_db')


def get_pdf(filename: str) -> bytes | None:
    """Đọc bytes PDF của template từ DB. None nếu không có / lỗi."""
    try:
        row = db.session.execute(
            text('SELECT pdf_data FROM public.template_pdf_cache WHERE filename = :fn'),
            {'fn': filename},
        ).first()
        if row and row[0] is not None:
            return bytes(row[0])
        return None
    except Exception as e:
        log.warning(f'get_pdf({filename}) lỗi: {e}')
        db.session.rollback()
        return None


def get_meta(filename: str) -> dict | None:
    """Đọc metadata (content_hash, size_bytes) để so sánh stale. None nếu không có / lỗi."""
    try:
        row = db.session.execute(
            text('''SELECT content_hash, size_bytes
                    FROM public.template_pdf_cache WHERE filename = :fn'''),
            {'fn': filename},
        ).first()
        if row:
            return {'content_hash': row[0], 'size_bytes': int(row[1] or 0)}
        return None
    except Exception as e:
        log.warning(f'get_meta({filename}) lỗi: {e}')
        db.session.rollback()
        return None


def put_pdf(filename: str, content_hash: str, pdf_bytes: bytes) -> bool:
    """Upsert PDF vào DB. Trả True nếu thành công."""
    try:
        db.session.execute(
            text('''
                INSERT INTO public.template_pdf_cache
                    (filename, content_hash, pdf_data, size_bytes, updated_at)
                VALUES (:fn, :hash, :data, :size, now())
                ON CONFLICT (filename) DO UPDATE SET
                    content_hash = EXCLUDED.content_hash,
                    pdf_data     = EXCLUDED.pdf_data,
                    size_bytes   = EXCLUDED.size_bytes,
                    updated_at   = now()
            '''),
            {
                'fn': filename,
                'hash': content_hash,
                'data': pdf_bytes,
                'size': len(pdf_bytes),
            },
        )
        db.session.commit()
        return True
    except Exception as e:
        log.warning(f'put_pdf({filename}) lỗi: {e}')
        db.session.rollback()
        return False
