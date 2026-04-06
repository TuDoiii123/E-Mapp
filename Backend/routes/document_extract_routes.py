"""
Document extraction & form-template management routes.

Endpoints:
  POST /api/extract/document          — trích xuất giấy tờ cá nhân (CCCD, GPLX, …)
  POST /api/extract/form-template     — thêm giấy tờ mẫu (admin)
  GET  /api/extract/form-templates    — danh sách giấy tờ mẫu
  GET  /api/extract/form-templates/<id> — chi tiết một giấy tờ mẫu
  DELETE /api/extract/form-templates/<id> — xóa giấy tờ mẫu (admin)
"""
import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from logger import get_logger

log = get_logger('document_extract_routes')

document_extract_bp = Blueprint('document_extract', __name__, url_prefix='/api/extract')

_ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'webp', 'heic', 'heif'}
_ALLOWED_DOCS  = _ALLOWED_IMAGE | {'pdf'}

_DATA_FILE      = os.path.join(os.path.dirname(__file__), '..', 'data', 'form_templates.json')
_TEMPLATES_DIR  = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'templates')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _allowed(filename: str, allowed: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _read_templates() -> list:
    if not os.path.exists(_DATA_FILE):
        return []
    with open(_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_templates(data: list) -> None:
    os.makedirs(os.path.dirname(_DATA_FILE), exist_ok=True)
    with open(_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _now() -> str:
    return datetime.utcnow().isoformat() + 'Z'


def _new_id() -> str:
    return str(int(datetime.utcnow().timestamp() * 1000))


# ── Routes ────────────────────────────────────────────────────────────────────

@document_extract_bp.route('/document', methods=['POST'])
def extract_document_route():
    """
    Trích xuất thông tin từ giấy tờ cá nhân (CCCD, GPLX, Giấy kết hôn, …).
    Nhận: multipart/form-data với field 'file' (ảnh hoặc PDF).
    Trả về: JSON trích xuất được.
    Yêu cầu đăng nhập.
    """
    if not hasattr(request, 'user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Thiếu file'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'success': False, 'message': 'File không hợp lệ'}), 400

    if not _allowed(file.filename, _ALLOWED_DOCS):
        return jsonify({
            'success': False,
            'message': f'Chỉ hỗ trợ: {", ".join(sorted(_ALLOWED_DOCS))}'
        }), 400

    # Save temporarily
    ext = file.filename.rsplit('.', 1)[1].lower()
    tmp_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{_new_id()}.{ext}")

    try:
        file.save(tmp_path)

        from services.image_extractor import extract_document
        result = extract_document(tmp_path)

        return jsonify({'success': True, 'data': result}), 200

    except EnvironmentError as e:
        log.error(f'extract_document: env error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 503
    except Exception as e:
        log.error(f'extract_document: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi trích xuất: {str(e)}'}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@document_extract_bp.route('/form-template', methods=['POST'])
def add_form_template():
    """
    Thêm giấy tờ mẫu vào hệ thống.
    Nhận: multipart/form-data
      - file       : ảnh hoặc PDF của biểu mẫu (bắt buộc)
      - name       : tên biểu mẫu (bắt buộc)
      - description: mô tả (tuỳ chọn)
      - serviceId  : ID dịch vụ liên kết (tuỳ chọn)
    Chỉ admin.
    """
    if not hasattr(request, 'user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Chỉ admin được thêm giấy tờ mẫu'}), 403

    name = (request.form.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'Thiếu tên biểu mẫu (name)'}), 400

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Thiếu file'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'success': False, 'message': 'File không hợp lệ'}), 400

    if not _allowed(file.filename, _ALLOWED_DOCS):
        return jsonify({
            'success': False,
            'message': f'Chỉ hỗ trợ: {", ".join(sorted(_ALLOWED_DOCS))}'
        }), 400

    ext      = file.filename.rsplit('.', 1)[1].lower()
    template_id = _new_id()
    filename = f"template-{template_id}.{ext}"

    os.makedirs(_TEMPLATES_DIR, exist_ok=True)
    save_path = os.path.join(_TEMPLATES_DIR, filename)

    try:
        file.save(save_path)

        from services.image_extractor import extract_form_template
        extracted = extract_form_template(save_path)

        record = {
            'id':          template_id,
            'name':        name,
            'description': (request.form.get('description') or '').strip(),
            'serviceId':   request.form.get('serviceId') or None,
            'filename':    filename,
            'originalName': secure_filename(file.filename),
            'storagePath': f'uploads/templates/{filename}',
            'extractedStructure': extracted,
            'createdBy':   request.user_id,
            'createdAt':   _now(),
            'updatedAt':   _now(),
        }

        templates = _read_templates()
        templates.append(record)
        _write_templates(templates)

        return jsonify({'success': True, 'data': record}), 201

    except EnvironmentError as e:
        log.error(f'add_form_template: env error: {e}')
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({'success': False, 'message': str(e)}), 503
    except Exception as e:
        log.error(f'add_form_template: {e}', exc_info=True)
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({'success': False, 'message': f'Lỗi xử lý: {str(e)}'}), 500


@document_extract_bp.route('/form-templates', methods=['GET'])
def list_form_templates():
    """
    Danh sách giấy tờ mẫu.
    Query params:
      serviceId — lọc theo dịch vụ
      q         — tìm theo tên
    Không yêu cầu đăng nhập.
    """
    try:
        templates = _read_templates()

        service_id = request.args.get('serviceId', '').strip()
        q          = request.args.get('q', '').strip().lower()

        if service_id:
            templates = [t for t in templates if t.get('serviceId') == service_id]
        if q:
            templates = [t for t in templates if q in t.get('name', '').lower()
                         or q in t.get('description', '').lower()]

        # Don't expose full extractedStructure in list view
        result = [
            {k: v for k, v in t.items() if k != 'extractedStructure'}
            for t in templates
        ]
        result.sort(key=lambda t: t.get('createdAt', ''), reverse=True)

        return jsonify({'success': True, 'data': result, 'total': len(result)}), 200

    except Exception as e:
        log.error(f'list_form_templates: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@document_extract_bp.route('/form-templates/<template_id>', methods=['GET'])
def get_form_template(template_id):
    """Chi tiết một giấy tờ mẫu (bao gồm extractedStructure)."""
    try:
        templates = _read_templates()
        record = next((t for t in templates if t['id'] == template_id), None)
        if not record:
            return jsonify({'success': False, 'message': 'Không tìm thấy mẫu'}), 404
        return jsonify({'success': True, 'data': record}), 200
    except Exception as e:
        log.error(f'get_form_template: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@document_extract_bp.route('/form-templates/<template_id>', methods=['DELETE'])
def delete_form_template(template_id):
    """Xóa giấy tờ mẫu. Chỉ admin."""
    if not hasattr(request, 'user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Chỉ admin được xóa'}), 403

    try:
        templates = _read_templates()
        record = next((t for t in templates if t['id'] == template_id), None)
        if not record:
            return jsonify({'success': False, 'message': 'Không tìm thấy mẫu'}), 404

        # Remove file
        file_path = os.path.join(os.path.dirname(__file__), '..', record['storagePath'])
        if os.path.exists(file_path):
            os.remove(file_path)

        templates = [t for t in templates if t['id'] != template_id]
        _write_templates(templates)

        return jsonify({'success': True, 'message': 'Đã xóa giấy tờ mẫu'}), 200

    except Exception as e:
        log.error(f'delete_form_template: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
