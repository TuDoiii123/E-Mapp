"""
Templates routes:
  GET  /api/templates/<filename>         → tải về file Word mẫu gốc
  GET  /api/templates/<filename>/preview → xem trước dưới dạng PDF (qua LibreOffice/docx2pdf)
  GET  /api/templates                    → liệt kê tất cả template có sẵn
"""
import os
import threading
from flask import Blueprint, send_from_directory, send_file, jsonify, abort, request
from logger import get_logger

log = get_logger('templates_routes')

templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

_TEMPLATES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
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
        # .docx (OOXML)
        'mau-to-khai-dang-ky-ket-hon.docx',
        'mau-to-khai-dang-ky-thuong-tru.docx',
        'mau-to-khai-dang-ky-khai-tu.docx',
        'mau-to-khai-xac-nhan-tinh-trang-hon-nhan.docx',
        'mau-don-cap-gcnqsdd-so-do.docx',
        'mau-don-xin-cap-phep-xay-dung.docx',
        'mau-phieu-ly-lich-tu-phap-so1.docx',
        'mau-giay-de-nghi-dang-ky-ho-kinh-doanh.docx',
        'mau-giay-de-nghi-dang-ky-doanh-nghiep.docx',
        'mau-ban-khai-ca-nhan.docx',
        # .doc (OLE2) — win32com handles these
        'mau-to-khai-dang-ky-khai-sinh.doc',
        'mau-CC01-to-khai-CCCD.doc',
        'mau-CT01-to-khai-cu-tru.doc',
        'mau-don-dang-ky-bien-dong-dat-dai.doc',
        'mau-to-khai-tham-gia-bhxh-bhyt.doc',
        'mau-giay-kham-suc-khoe-lai-xe.doc',
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
        try:
            from services.pdf_converter import word_to_pdf
            pdf_path = word_to_pdf(fpath)
            if pdf_path and os.path.exists(pdf_path):
                log.debug(f'Serving PDF preview for {fn}')
                return send_file(pdf_path, mimetype='application/pdf')
            # Chưa có cache → bắt đầu convert ngầm, trả Word trước
            # Client sẽ retry; lần sau sẽ có PDF từ cache
            _schedule_bg_convert(fpath)
        except Exception as e:
            log.warning(f'PDF conversion failed for {fn}: {e}')

        # Fallback: trả về file Word inline (browser có thể render hoặc download)
        mime = ('application/msword' if ext == 'doc'
                else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        log.debug(f'Serving Word fallback for {fn}')
        return send_file(fpath, mimetype=mime)

    abort(415)
