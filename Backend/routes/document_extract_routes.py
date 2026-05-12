"""
Document extraction & form-template management routes.

Endpoints:
  POST /api/extract/document            — trích xuất giấy tờ cá nhân (CCCD, GPLX, …)
  POST /api/extract/form-template       — thêm giấy tờ mẫu (admin)
  GET  /api/extract/form-templates      — danh sách giấy tờ mẫu
  GET  /api/extract/form-templates/<id> — chi tiết một giấy tờ mẫu
  DELETE /api/extract/form-templates/<id> — xóa giấy tờ mẫu (admin)
"""
import json
import os
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from werkzeug.utils import secure_filename

from models.db import db
from logger import get_logger

log = get_logger('document_extract_routes')

document_extract_bp = Blueprint('document_extract', __name__, url_prefix='/api/extract')

_ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'webp', 'heic', 'heif'}
_ALLOWED_DOCS  = _ALLOWED_IMAGE | {'pdf'}

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'templates')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _allowed(filename: str, allowed: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _now() -> str:
    return datetime.utcnow().isoformat() + 'Z'


def _new_id() -> str:
    return str(uuid.uuid4())


def _row_to_dict(row, include_structure: bool = True) -> dict:
    d = {
        'id':           row.id,
        'name':         row.name,
        'description':  row.description or '',
        'serviceId':    row.service_id,
        'filename':     row.filename,
        'originalName': row.original_name or '',
        'storagePath':  row.storage_path or '',
        'createdBy':    row.created_by,
        'createdAt':    row.created_at.isoformat() if row.created_at else None,
        'updatedAt':    row.updated_at.isoformat() if row.updated_at else None,
    }
    if include_structure:
        raw = row.extracted_structure
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (ValueError, TypeError):
                raw = {}
        d['extractedStructure'] = raw or {}
    return d


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

    ext         = file.filename.rsplit('.', 1)[1].lower()
    template_id = _new_id()
    filename    = f"template-{template_id}.{ext}"

    os.makedirs(_TEMPLATES_DIR, exist_ok=True)
    save_path = os.path.join(_TEMPLATES_DIR, filename)

    try:
        file.save(save_path)

        from services.image_extractor import extract_form_template
        extracted = extract_form_template(save_path)

        description = (request.form.get('description') or '').strip()
        service_id  = request.form.get('serviceId') or None
        storage_path = f'uploads/templates/{filename}'
        original_name = secure_filename(file.filename)

        db.session.execute(
            text('''
                INSERT INTO public.form_templates
                    (id, name, description, service_id, filename, original_name,
                     storage_path, extracted_structure, created_by)
                VALUES (:id, :name, :desc, :svc, :fn, :orig, :path, :struct::jsonb, :by)
            '''),
            {
                'id':     template_id,
                'name':   name,
                'desc':   description,
                'svc':    service_id,
                'fn':     filename,
                'orig':   original_name,
                'path':   storage_path,
                'struct': json.dumps(extracted, ensure_ascii=False),
                'by':     request.user_id,
            },
        )
        db.session.commit()

        record = {
            'id':                template_id,
            'name':              name,
            'description':       description,
            'serviceId':         service_id,
            'filename':          filename,
            'originalName':      original_name,
            'storagePath':       storage_path,
            'extractedStructure': extracted,
            'createdBy':         request.user_id,
            'createdAt':         _now(),
            'updatedAt':         _now(),
        }
        return jsonify({'success': True, 'data': record}), 201

    except EnvironmentError as e:
        log.error(f'add_form_template: env error: {e}')
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({'success': False, 'message': str(e)}), 503
    except Exception as e:
        db.session.rollback()
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
        service_id = (request.args.get('serviceId') or '').strip()
        q          = (request.args.get('q') or '').strip().lower()

        filters = ''
        params: dict = {}
        if service_id:
            filters += ' AND service_id = :svc'
            params['svc'] = service_id
        if q:
            filters += ' AND (LOWER(name) LIKE :q OR LOWER(description) LIKE :q)'
            params['q'] = f'%{q}%'

        rows = db.session.execute(
            text(f'''
                SELECT id, name, description, service_id, filename, original_name,
                       storage_path, created_by, created_at, updated_at
                FROM public.form_templates
                WHERE 1=1 {filters}
                ORDER BY created_at DESC
            '''),
            params,
        ).fetchall()

        result = [_row_to_dict(r, include_structure=False) for r in rows]
        return jsonify({'success': True, 'data': result, 'total': len(result)}), 200

    except Exception as e:
        log.error(f'list_form_templates: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@document_extract_bp.route('/form-templates/<template_id>', methods=['GET'])
def get_form_template(template_id):
    """Chi tiết một giấy tờ mẫu (bao gồm extractedStructure)."""
    try:
        row = db.session.execute(
            text('SELECT * FROM public.form_templates WHERE id = :id'),
            {'id': template_id},
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Không tìm thấy mẫu'}), 404
        return jsonify({'success': True, 'data': _row_to_dict(row, include_structure=True)}), 200
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
        row = db.session.execute(
            text('SELECT id, storage_path FROM public.form_templates WHERE id = :id'),
            {'id': template_id},
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Không tìm thấy mẫu'}), 404

        file_path = os.path.join(os.path.dirname(__file__), '..', row.storage_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.execute(
            text('DELETE FROM public.form_templates WHERE id = :id'),
            {'id': template_id},
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'Đã xóa giấy tờ mẫu'}), 200

    except Exception as e:
        db.session.rollback()
        log.error(f'delete_form_template: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
