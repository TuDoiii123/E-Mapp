"""
Templates routes:
  GET  /api/templates/<filename>         → tải về file Word mẫu gốc
  GET  /api/templates/<filename>/preview → xem trước dưới dạng PDF (qua LibreOffice/docx2pdf)
  GET  /api/templates                    → liệt kê tất cả template có sẵn
"""
import os
import hashlib
import threading
from io import BytesIO
from flask import Blueprint, send_from_directory, send_file, jsonify, abort, request
from logger import get_logger

log = get_logger('templates_routes')

templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

_TEMPLATES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
)

_CACHE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'pdf_cache')
)

_ALLOWED_EXTS = {'doc', 'docx', 'pdf'}

# Set các file đang được convert ngầm (tránh chạy song song)
_converting: set[str] = set()
_converting_lock = threading.Lock()


def _schedule_bg_convert(fpath: str):
    """Chạy word_to_pdf trong background thread nếu chưa đang convert."""
    with _converting_lock:
        if fpath in _converting:
            return
        _converting.add(fpath)

    def _run():
        try:
            from services.pdf_converter import word_to_pdf
            pdf_path = word_to_pdf(fpath)
            if pdf_path:
                log.info(f'BG convert done: {os.path.basename(fpath)}')
            else:
                log.warning(f'BG convert failed: {os.path.basename(fpath)}')
        except Exception as e:
            log.warning(f'BG convert error {os.path.basename(fpath)}: {e}')
        finally:
            with _converting_lock:
                _converting.discard(fpath)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _warmup_pdf_cache():
    """Pre-convert các template phổ biến (chạy 1 lần khi server start)."""
    from services.pdf_converter import is_available
    if not is_available():
        return

    # Các template được map trong DB (ưu tiên convert trước)
    priority = [
        # .docx (OOXML) — Hộ tịch
        'mau-to-khai-dang-ky-ket-hon.docx',
        'mau-to-khai-dang-ky-thuong-tru.docx',
        'mau-to-khai-dang-ky-khai-tu.docx',
        'mau-to-khai-xac-nhan-tinh-trang-hon-nhan.docx',
        'mau-to-khai-cap-ban-sao-trich-luc-ho-tich.docx',
        'mau-to-khai-dang-ky-lai-khai-sinh.docx',
        # .docx — Đất đai / Xây dựng
        'mau-don-cap-gcnqsdd-so-do.docx',
        'mau-don-xin-cap-phep-xay-dung.docx',
        'mau-don-tach-thua-hop-thua-dat.docx',
        # .docx — Tư pháp / LLTP
        'mau-phieu-ly-lich-tu-phap-so1.docx',
        # .docx — Doanh nghiệp
        'mau-giay-de-nghi-dang-ky-ho-kinh-doanh.docx',
        'mau-giay-de-nghi-dang-ky-doanh-nghiep.docx',
        'mau-giai-the-doanh-nghiep.docx',
        'mau-thong-bao-thay-doi-noi-dung-dkdn.docx',
        # .docx — Giao thông
        'mau-don-de-nghi-cap-doi-gplx.docx',
        'mau-to-khai-dang-ky-xe-may-lan-dau.docx',
        # .docx — BHYT / BHXH
        'mau-to-khai-cap-the-bao-hiem-y-te.docx',
        'mau-TK1-TS-to-khai-tham-gia-bhxh-bhyt.docx',
        'mau-D02-LT-danh-sach-lao-dong-bhxh.docx',
        # .docx — Cư trú
        'mau-CT02-to-khai-tam-tru.docx',
        # .docx — Xây dựng
        'mau-thong-bao-hoan-cong-cong-trinh.docx',
        # .docx — Tư pháp
        'mau-don-yeu-cau-chung-thuc-ban-sao.docx',
        # .docx — Doanh nghiệp
        'mau-thong-bao-tam-ngung-kinh-doanh.docx',
        # .docx — Giao thông
        'mau-to-khai-dang-ky-xe-may-lan-dau.docx',
        # .docx — Hộ tịch
        'mau-to-khai-dang-ky-nuoi-con-nuoi.docx',
        # .docx — Chung
        'mau-giay-uy-quyen.docx',
        # .docx — Khác
        'mau-ban-khai-ca-nhan.docx',
        # .doc (OLE2) — win32com handles these
        'mau-to-khai-dang-ky-khai-sinh.doc',
        'mau-CC01-to-khai-CCCD.doc',
        'mau-CT01-to-khai-cu-tru.doc',
        'mau-don-dang-ky-bien-dong-dat-dai.doc',
        'mau-to-khai-tham-gia-bhxh-bhyt.doc',
        'mau-giay-kham-suc-khoe-lai-xe.doc',
        'mau-to-khai-nhan-cha-me-con.doc',
        'mau-to-khai-thay-doi-cai-chinh-ho-tich.doc',
        'mau-phieu-ly-lich-tu-phap-so2.doc',
        # .doc — đổi tên từ .docx (OLE2 nội dung gốc)
        'mau-to-khai-le-phi-truoc-ba.doc',
        'mau-to-khai-cap-ho-chieu.doc',
        'mau-bien-ban-vi-pham-hanh-chinh.doc',
        'mau-to-khai-thue-thu-nhap-ca-nhan.doc',
    ]

    def _run():
        from services.pdf_converter import word_to_pdf
        log.info(f'Warm-up PDF cache bắt đầu ({len(priority)} templates)...')
        ok = 0
        for fname in priority:
            fpath = os.path.join(_TEMPLATES_DIR, fname)
            if not os.path.exists(fpath):
                continue
            try:
                r = word_to_pdf(fpath)
                if r:
                    ok += 1
            except Exception as e:
                log.debug(f'Warm-up skip {fname}: {e}')
        log.info(f'Warm-up PDF cache xong: {ok}/{len(priority)} templates sẵn sàng')

    t = threading.Thread(target=_run, daemon=True, name='pdf-warmup')
    t.start()


# Khởi chạy warm-up sau khi blueprint được register
@templates_bp.record_once
def _on_register(state):
    with state.app.app_context():
        threading.Thread(target=_warmup_pdf_cache, daemon=True).start()


def _safe_filename(filename: str) -> str | None:
    """Trả về tên file an toàn hoặc None nếu không hợp lệ (ngăn path traversal)."""
    fn = os.path.basename(filename)
    if not fn or fn != filename or '..' in fn:
        return None
    ext = fn.rsplit('.', 1)[-1].lower() if '.' in fn else ''
    if ext not in _ALLOWED_EXTS:
        return None
    return fn


@templates_bp.route('', methods=['GET'])
def list_templates():
    """
    GET /api/templates
    Liệt kê tất cả file template.
    """
    try:
        if not os.path.isdir(_TEMPLATES_DIR):
            return jsonify({'success': True, 'data': {'templates': []}}), 200

        files = []
        for fname in sorted(os.listdir(_TEMPLATES_DIR)):
            ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
            if ext in _ALLOWED_EXTS:
                fpath = os.path.join(_TEMPLATES_DIR, fname)
                files.append({
                    'filename': fname,
                    'size': os.path.getsize(fpath),
                    'downloadUrl': f'/api/templates/download/{fname}',
                    'previewUrl':  f'/api/templates/preview/{fname}',
                })
        return jsonify({'success': True, 'data': {'templates': files, 'count': len(files)}})
    except Exception as e:
        log.error(f'list_templates error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@templates_bp.route('/download/<path:filename>', methods=['GET'])
def serve_template(filename: str):
    """
    GET /api/templates/download/<filename>
    Tải về file Word mẫu gốc. Không cần auth — mọi người đều được xem mẫu.
    """
    fn = _safe_filename(filename)
    if not fn:
        abort(400)

    fpath = os.path.join(_TEMPLATES_DIR, fn)
    if not os.path.exists(fpath):
        log.warning(f'Template không tồn tại: {fn}')
        return jsonify({'success': False, 'message': f'Template không tìm thấy: {fn}'}), 404

    ext = fn.rsplit('.', 1)[-1].lower()
    mime_map = {
        'doc':  'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'pdf':  'application/pdf',
    }
    return send_from_directory(
        _TEMPLATES_DIR, fn,
        as_attachment=True,
        mimetype=mime_map.get(ext, 'application/octet-stream'),
    )


@templates_bp.route('/preview/<path:filename>', methods=['GET'])
def preview_template(filename: str):
    """
    GET /api/templates/preview/<filename>
    Phục vụ bản PDF để xem trước trong trình duyệt.
    Nếu LibreOffice không có hoặc chuyển đổi thất bại → trả về file Word gốc.
    """
    fn = _safe_filename(filename)
    if not fn:
        abort(400)

    fpath = os.path.join(_TEMPLATES_DIR, fn)
    if not os.path.exists(fpath):
        log.warning(f'Template không tồn tại: {fn}')
        return jsonify({'success': False, 'message': f'Template không tìm thấy: {fn}'}), 404

    ext = fn.rsplit('.', 1)[-1].lower()

    # Nếu là PDF rồi thì trả thẳng
    if ext == 'pdf':
        return send_file(fpath, mimetype='application/pdf')

    # Thử chuyển đổi Word → PDF
    if ext in ('doc', 'docx'):
        stem = fn.rsplit('.', 1)[0]

        # MD5 nội dung template gốc — dùng để so cache DB và phát hiện stale
        try:
            with open(fpath, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            log.warning(f'Không đọc được template {fn}: {e}')
            content_hash = None

        # 1. DB-first: phục vụ PDF từ Postgres nếu có và hash khớp.
        #    Đây là đường production đi — không cần LibreOffice/Word.
        if content_hash:
            from services import pdf_cache_db
            meta = pdf_cache_db.get_meta(fn)
            if meta and meta.get('content_hash') == content_hash:
                pdf_bytes = pdf_cache_db.get_pdf(fn)
                if pdf_bytes:
                    log.debug(f'Cache hit (DB): {fn}')
                    return send_file(BytesIO(pdf_bytes), mimetype='application/pdf',
                                     download_name=f'{stem}.pdf')

        # 2. Cache đĩa trực tiếp theo pattern <stem>_*.pdf (không cần gọi word_to_pdf)
        import glob as _glob
        cached = sorted(_glob.glob(os.path.join(_CACHE_DIR, f'{stem}_*.pdf')))
        if cached:
            log.debug(f'Cache hit (disk): {os.path.basename(cached[-1])}')
            return send_file(cached[-1], mimetype='application/pdf')

        # 3. Convert local (máy có engine) → write-through vào DB
        try:
            from services.pdf_converter import word_to_pdf
            pdf_path = word_to_pdf(fpath)
            if pdf_path and os.path.exists(pdf_path):
                log.debug(f'Serving PDF preview for {fn}')
                if content_hash:
                    try:
                        from services import pdf_cache_db
                        with open(pdf_path, 'rb') as pf:
                            pdf_cache_db.put_pdf(fn, content_hash, pf.read())
                    except Exception as e:
                        log.warning(f'Write-through DB lỗi cho {fn}: {e}')
                return send_file(pdf_path, mimetype='application/pdf')
            _schedule_bg_convert(fpath)
        except Exception as e:
            log.warning(f'PDF conversion failed for {fn}: {e}')

        # 4. Fallback: trả về file Word inline
        mime = ('application/msword' if ext == 'doc'
                else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        log.debug(f'Serving Word fallback for {fn}')
        return send_file(fpath, mimetype=mime)

    abort(415)
