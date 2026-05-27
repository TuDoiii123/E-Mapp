"""
AI Document Services:
  POST /api/ai/extract   — trích xuất thông tin từ ảnh/scan giấy tờ
  POST /api/ai/fill      — điền vào Word template với các trường đã cung cấp
  GET  /api/ai/fields/<template_file>  — lấy danh sách {{field}} trong template
"""
import os
import tempfile
import json
from flask import Blueprint, request, jsonify, send_file
from logger import get_logger

log = get_logger('ai_routes')

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

_TEMPLATES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
)

_ALLOWED_EXTRACT_EXTS = {'jpg', 'jpeg', 'png', 'webp', 'pdf'}


def _auth_required():
    """Trả về None nếu đã xác thực, hoặc response 401 nếu chưa."""
    if not hasattr(request, 'user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    return None


def _safe_template_path(template_file: str) -> str | None:
    """Trả về đường dẫn an toàn tới template, hoặc None nếu không hợp lệ."""
    fn = os.path.basename(template_file)
    if not fn or fn != template_file:
        return None
    ext = fn.rsplit('.', 1)[-1].lower() if '.' in fn else ''
    if ext not in ('doc', 'docx'):
        return None
    path = os.path.join(_TEMPLATES_DIR, fn)
    return path if os.path.exists(path) else None


# ── POST /api/ai/extract ─────────────────────────────────────────────────────

@ai_bp.route('/extract', methods=['POST'])
def extract_document():
    """
    Trích xuất thông tin có cấu trúc từ ảnh/scan giấy tờ.

    Request: multipart/form-data
      file  — ảnh hoặc PDF của giấy tờ (CCCD, GPLX, giấy khai sinh, v.v.)

    Response:
      { "success": true, "data": { "fields": { ... } } }
    """
    err = _auth_required()
    if err:
        return err

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Thiếu file'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'success': False, 'message': 'Tên file không hợp lệ'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in _ALLOWED_EXTRACT_EXTS:
        return jsonify({
            'success': False,
            'message': f'Định dạng không hỗ trợ. Chấp nhận: {", ".join(_ALLOWED_EXTRACT_EXTS)}'
        }), 400

    tmp = tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False)
    try:
        file.save(tmp.name)
        tmp.close()

        from services.image_extractor import extract_document as _extract
        fields = _extract(tmp.name)

        log.info(f'AI extract: {file.filename} → {len(fields) if isinstance(fields, dict) else "?"} fields')
        return jsonify({
            'success': True,
            'data': {'fields': fields}
        })

    except EnvironmentError as e:
        # GEMINI_API_KEY không được cấu hình
        log.warning(f'AI extract env error: {e}')
        return jsonify({
            'success': False,
            'message': 'Dịch vụ AI chưa được cấu hình. Vui lòng liên hệ quản trị viên.'
        }), 503
    except Exception as e:
        log.error(f'AI extract error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi trích xuất: {str(e)}'}), 500
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


# ── POST /api/ai/fill ────────────────────────────────────────────────────────

@ai_bp.route('/fill', methods=['POST'])
def fill_template():
    """
    Điền thông tin vào Word template và trả về file .docx đã điền.

    Request: application/json
      {
        "templateFile": "mau-to-khai-dang-ky-khai-sinh.doc",
        "fields": { "ho_ten": "Nguyễn Văn A", "ngay_sinh": "01/01/2024", ... }
      }

    Response: file .docx (attachment)
    """
    err = _auth_required()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    template_file = (data.get('templateFile') or '').strip()
    fields = data.get('fields') or {}

    if not template_file:
        return jsonify({'success': False, 'message': 'Thiếu templateFile'}), 400

    template_path = _safe_template_path(template_file)
    if not template_path:
        return jsonify({
            'success': False,
            'message': f'Template không tồn tại hoặc không hợp lệ: {template_file}'
        }), 404

    try:
        from services.template_filler import fill_template as _fill
        filled_bytes = _fill(template_path, fields)

        stem = os.path.splitext(template_file)[0]
        download_name = f'{stem}_dien.docx'

        log.info(f'AI fill: {template_file} với {len(fields)} trường')
        return send_file(
            filled_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=download_name,
        )

    except ImportError as e:
        log.warning(f'python-docx chưa cài: {e}')
        return jsonify({
            'success': False,
            'message': 'python-docx chưa được cài đặt. Chạy: pip install python-docx'
        }), 503
    except Exception as e:
        log.error(f'AI fill error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ── GET /api/ai/fields/<template_file> ──────────────────────────────────────

@ai_bp.route('/fields/<path:template_file>', methods=['GET'])
def get_template_fields(template_file: str):
    """
    GET /api/ai/fields/<template_file>
    Lấy danh sách tất cả {{field_name}} trong template.
    Dùng để frontend biết cần điền những trường gì.
    """
    err = _auth_required()
    if err:
        return err

    template_path = _safe_template_path(template_file)
    if not template_path:
        return jsonify({
            'success': False,
            'message': f'Template không tồn tại: {template_file}'
        }), 404

    try:
        from services.template_filler import get_template_fields as _get_fields
        fields = _get_fields(template_path)
        return jsonify({
            'success': True,
            'data': {
                'templateFile': template_file,
                'fields': fields,
                'count': len(fields),
            }
        })
    except Exception as e:
        log.error(f'get_template_fields error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ── POST /api/ai/extract-and-fill ───────────────────────────────────────────

@ai_bp.route('/extract-and-fill', methods=['POST'])
def extract_and_fill():
    """
    Tiện ích: Upload ảnh giấy tờ nguồn + tên template → trích xuất + điền → trả về .docx.

    Request: multipart/form-data
      file         — ảnh/PDF giấy tờ nguồn để trích xuất
      templateFile — tên file template cần điền

    Response: file .docx đã điền hoặc JSON với fields đã trích xuất
    """
    err = _auth_required()
    if err:
        return err

    template_file = (request.form.get('templateFile') or '').strip()
    return_fields_only = request.form.get('fieldsOnly', '').lower() == 'true'

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Thiếu file ảnh nguồn'}), 400

    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in (file.filename or '') else ''
    if ext not in _ALLOWED_EXTRACT_EXTS:
        return jsonify({'success': False, 'message': 'Định dạng ảnh không hỗ trợ'}), 400

    tmp = tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False)
    try:
        file.save(tmp.name)
        tmp.close()

        # Bước 1: Trích xuất fields từ ảnh
        from services.image_extractor import extract_document as _extract
        extracted = _extract(tmp.name)

        if return_fields_only or not template_file:
            return jsonify({
                'success': True,
                'data': {'fields': extracted}
            })

        # Bước 2: Điền vào template
        template_path = _safe_template_path(template_file)
        if not template_path:
            return jsonify({
                'success': False,
                'message': f'Template không tìm thấy: {template_file}',
                'data': {'fields': extracted}
            }), 404

        from services.template_filler import fill_template as _fill
        # Flatten extracted dict nếu có nested structure
        flat_fields = _flatten_fields(extracted)
        filled_bytes = _fill(template_path, flat_fields)

        stem = os.path.splitext(template_file)[0]
        download_name = f'{stem}_dien.docx'

        log.info(f'extract-and-fill: {file.filename} → {template_file} ({len(flat_fields)} fields)')
        return send_file(
            filled_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=download_name,
        )

    except EnvironmentError as e:
        log.warning(f'extract-and-fill env error: {e}')
        return jsonify({'success': False, 'message': 'Dịch vụ AI chưa được cấu hình.'}), 503
    except Exception as e:
        log.error(f'extract-and-fill error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def _flatten_fields(data: dict, prefix: str = '') -> dict[str, str]:
    """Làm phẳng dict lồng nhau thành {key: value} cho template filler."""
    result = {}
    for k, v in data.items():
        full_key = f'{prefix}_{k}' if prefix else k
        if isinstance(v, dict):
            result.update(_flatten_fields(v, full_key))
        elif isinstance(v, list):
            result[full_key] = ', '.join(str(i) for i in v)
        else:
            result[full_key] = v
    return result
