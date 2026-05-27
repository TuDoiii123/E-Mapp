"""
Templates routes:
  GET  /api/templates/<filename>         → tải về file Word mẫu gốc
  GET  /api/templates/<filename>/preview → xem trước dưới dạng PDF (qua LibreOffice)
  GET  /api/templates                    → liệt kê tất cả template có sẵn
"""
import os
from flask import Blueprint, send_from_directory, send_file, jsonify, abort, request
from logger import get_logger

log = get_logger('templates_routes')

templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

_TEMPLATES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
)

_ALLOWED_EXTS = {'doc', 'docx', 'pdf'}


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
                    'downloadUrl': f'/api/templates/{fname}',
                    'previewUrl':  f'/api/templates/{fname}/preview',
                })
        return jsonify({'success': True, 'data': {'templates': files, 'count': len(files)}})
    except Exception as e:
        log.error(f'list_templates error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@templates_bp.route('/<path:filename>', methods=['GET'])
def serve_template(filename: str):
    """
    GET /api/templates/<filename>
    Tải về file Word mẫu gốc. Không cần auth — mọi người đều được xem mẫu.
    """
    # Tách /preview suffix nếu có lẫn lộn
    if filename.endswith('/preview'):
        filename = filename[:-8]

    fn = _safe_filename(filename)
    if not fn:
        abort(400)

    fpath = os.path.join(_TEMPLATES_DIR, fn)
    if not os.path.exists(fpath):
        log.warning(f'Template không tồn tại: {fn}')
        abort(404)

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


@templates_bp.route('/<path:filename>/preview', methods=['GET'])
def preview_template(filename: str):
    """
    GET /api/templates/<filename>/preview
    Phục vụ bản PDF để xem trước trong trình duyệt.
    Nếu LibreOffice không có hoặc chuyển đổi thất bại → trả về file Word gốc.
    """
    fn = _safe_filename(filename)
    if not fn:
        abort(400)

    fpath = os.path.join(_TEMPLATES_DIR, fn)
    if not os.path.exists(fpath):
        log.warning(f'Template không tồn tại: {fn}')
        abort(404)

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
        except Exception as e:
            log.warning(f'PDF conversion failed for {fn}: {e}')

        # Fallback: trả về file Word inline
        mime = ('application/msword' if ext == 'doc'
                else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        log.debug(f'Serving Word fallback for {fn}')
        return send_file(fpath, mimetype=mime)

    abort(415)
