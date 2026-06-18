from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import json
import threading
from datetime import datetime, timezone
from sqlalchemy import text
from models.application import Application
from models.document import Document
from models.status_tracking import StatusTracking
from models.service_requirement import ServiceRequirement
from models.db import db
from services.document_processor import process_document
from logger import get_logger

log = get_logger('applications_routes')

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
ALLOWED_MIME_TYPES = {
    'application/pdf', 'text/plain',
    'image/jpeg', 'image/png', 'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Magic bytes cho các định dạng không phải text
_MAGIC_BYTES: list[tuple[bytes, str]] = [
    (b'\x25\x50\x44\x46', 'pdf'),           # %PDF
    (b'\xff\xd8\xff',      'jpeg'),          # JPEG
    (b'\x89\x50\x4e\x47', 'png'),           # PNG
    (b'\x47\x49\x46\x38', 'gif'),           # GIF87a / GIF89a
    (b'\x50\x4b\x03\x04', 'docx'),          # ZIP/OOXML (.docx, .xlsx, ...)
    (b'\xD0\xCF\x11\xE0', 'doc'),           # OLE2 Compound Document (.doc, .xls)
]

STATUS_LABELS = {
    'draft':            'Bản nháp',
    'submitted':        'Đã nộp',
    'in_review':        'Đang xem xét',
    'approved':         'Đã duyệt',
    'rejected':         'Từ chối',
    'more_info':        'Yêu cầu bổ sung',
    'withdraw':         'Đã rút',
}


# ── PostgreSQL helpers ────────────────────────────────────────────────────────

_VALID_SERVICE_IDS: set | None = None

def _get_valid_service_ids() -> set:
    """Cache danh sách service_id hợp lệ từ DB (lazy load)."""
    global _VALID_SERVICE_IDS
    if _VALID_SERVICE_IDS is None:
        try:
            rows = db.session.execute(
                text("SELECT id FROM public.procedures WHERE is_active = TRUE")
            ).fetchall()
            _VALID_SERVICE_IDS = {r[0] for r in rows}
        except Exception:
            _VALID_SERVICE_IDS = set()
    return _VALID_SERVICE_IDS


def _pg_create_application(applicant_id: str, service_id: str, data: dict,
                            signature_type: str | None = None) -> dict:
    # Validate service_id
    if not service_id or not str(service_id).strip():
        raise ValueError('service_id không được để trống')

    # Validate applicant_id tồn tại trong users
    user_exists = db.session.execute(
        text('SELECT 1 FROM public.users WHERE id = :uid'),
        {'uid': applicant_id}
    ).fetchone()
    if not user_exists:
        raise ValueError(f'Người dùng không tồn tại: {applicant_id}')

    app_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    sql = text('''
        INSERT INTO public.applications
            (id, applicant_id, service_id, status, data, signature_type, created_at, updated_at)
        VALUES (:id, :aid, :sid, 'draft', :data, :sig, now(), now())
        RETURNING id, applicant_id, service_id, status, data, signature_type,
                  submitted_at, created_at, updated_at
    ''')
    row = db.session.execute(sql, {
        'id':  app_id,
        'aid': applicant_id,
        'sid': service_id,
        'data': json.dumps(data, ensure_ascii=False),
        'sig': signature_type,
    }).fetchone()
    db.session.execute(text('''
        INSERT INTO public.application_status_history
            (application_id, status, note, by)
        VALUES (:app_id, 'draft', 'Tạo bản nháp', :by)
    '''), {'app_id': app_id, 'by': applicant_id})
    db.session.commit()
    return _pg_row_to_dict(row)


def _pg_get_application(app_id: str) -> dict | None:
    sql = text('''
        SELECT id, applicant_id, service_id, status, data, signature_type,
               submitted_at, created_at, updated_at
        FROM public.applications WHERE id = :id
    ''')
    row = db.session.execute(sql, {'id': app_id}).fetchone()
    return _pg_row_to_dict(row) if row else None


_ALLOWED_UPDATE_COLS = frozenset({'status', 'data', 'signature_type', 'submitted_at'})


def _pg_update_application(app_id: str, updates: dict) -> dict:
    safe = {k: v for k, v in updates.items() if k in _ALLOWED_UPDATE_COLS}
    if not safe:
        raise ValueError(f'No valid columns to update. Allowed: {_ALLOWED_UPDATE_COLS}')
    sets = ', '.join(f'{k} = :{k}' for k in safe)
    safe['app_id'] = app_id
    sql = text(f'''
        UPDATE public.applications
        SET {sets}, updated_at = now()
        WHERE id = :app_id
        RETURNING id, applicant_id, service_id, status, data, signature_type,
                  submitted_at, created_at, updated_at
    ''')
    row = db.session.execute(sql, safe).fetchone()
    db.session.commit()
    return _pg_row_to_dict(row) if row else None


def _pg_get_documents(app_id: str) -> list[dict]:
    sql = text('''
        SELECT id, application_id, requirement_id, filename, original_name,
               mime_type, size, storage_path, created_at
        FROM public.application_documents
        WHERE application_id = :app_id
        ORDER BY created_at
    ''')
    rows = db.session.execute(sql, {'app_id': app_id}).fetchall()
    keys = ['id', 'applicationId', 'requirementId', 'filename', 'originalName',
            'mimeType', 'size', 'storagePath', 'createdAt']
    return [dict(zip(keys, r)) for r in rows]


def _pg_get_history(app_id: str) -> list[dict]:
    sql = text('''
        SELECT id, application_id, status, note, by, created_at
        FROM public.application_status_history
        WHERE application_id = :app_id
        ORDER BY created_at
    ''')
    rows = db.session.execute(sql, {'app_id': app_id}).fetchall()
    keys = ['id', 'applicationId', 'status', 'note', 'by', 'createdAt']
    result = [dict(zip(keys, r)) for r in rows]
    for r in result:
        r['statusLabel'] = STATUS_LABELS.get(r['status'], r['status'])
    return result


def _pg_get_history_batch(app_ids: list[str]) -> dict[str, list[dict]]:
    """Batch fetch history cho nhiều applications — tránh N+1 query."""
    if not app_ids:
        return {}
    sql = text('''
        SELECT id, application_id, status, note, by, created_at
        FROM public.application_status_history
        WHERE application_id = ANY(:ids)
        ORDER BY application_id, created_at
    ''')
    rows = db.session.execute(sql, {'ids': app_ids}).fetchall()
    result: dict[str, list] = {aid: [] for aid in app_ids}
    for r in rows:
        entry = {
            'id': r[0], 'applicationId': r[1], 'status': r[2],
            'note': r[3], 'by': r[4], 'createdAt': r[5].isoformat() if r[5] else None,
            'statusLabel': STATUS_LABELS.get(r[2], r[2]),
        }
        result.setdefault(r[1], []).append(entry)
    return result


def _pg_add_document(app_id: str, requirement_id: str | None,
                     filename: str, original_name: str, mime_type: str,
                     size: int, storage_path: str) -> dict:
    doc_id = str(uuid.uuid4())
    sql = text('''
        INSERT INTO public.application_documents
            (id, application_id, requirement_id, filename, original_name,
             mime_type, size, storage_path)
        VALUES (:id, :app_id, :req_id, :fname, :oname, :mime, :size, :path)
        RETURNING id, application_id, requirement_id, filename, original_name,
                  mime_type, size, storage_path, created_at
    ''')
    row = db.session.execute(sql, {
        'id': doc_id, 'app_id': app_id, 'req_id': requirement_id,
        'fname': filename, 'oname': original_name,
        'mime': mime_type, 'size': size, 'path': storage_path,
    }).fetchone()
    db.session.commit()
    keys = ['id', 'applicationId', 'requirementId', 'filename', 'originalName',
            'mimeType', 'size', 'storagePath', 'createdAt']
    return dict(zip(keys, row))


def _pg_row_to_dict(row) -> dict:
    keys = ['id', 'applicantId', 'serviceId', 'status', 'data',
            'signatureType', 'submittedAt', 'createdAt', 'updatedAt']
    d = dict(zip(keys, row))
    if isinstance(d.get('data'), str):
        try:
            d['data'] = json.loads(d['data'])
        except Exception:
            pass
    d['statusLabel']   = STATUS_LABELS.get(d.get('status', ''), d.get('status', ''))
    # Aliases cho frontend compatibility
    d['currentStatus'] = d['status']
    d['procedureId']   = d.get('serviceId')
    d['procedureName'] = (d.get('data') or {}).get('serviceName') or d.get('serviceId', '')
    d['applicantName'] = (d.get('data') or {}).get('applicantName', '')
    return d


def _pg_my_applications(applicant_id: str, status_filter: str | None = None) -> list[dict]:
    if status_filter:
        sql = text('''
            SELECT id, applicant_id, service_id, status, data, signature_type,
                   submitted_at, created_at, updated_at
            FROM public.applications
            WHERE applicant_id = :aid AND status = :status
            ORDER BY created_at DESC
        ''')
        rows = db.session.execute(sql, {'aid': applicant_id, 'status': status_filter}).fetchall()
    else:
        sql = text('''
            SELECT id, applicant_id, service_id, status, data, signature_type,
                   submitted_at, created_at, updated_at
            FROM public.applications
            WHERE applicant_id = :aid
            ORDER BY created_at DESC
        ''')
        rows = db.session.execute(sql, {'aid': applicant_id}).fetchall()
    return [_pg_row_to_dict(r) for r in rows]


def allowed_file(filename: str, mime_type: str = '') -> bool:
    """Kiểm tra extension và MIME type (client-supplied)."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    clean_mime = (mime_type or '').split(';')[0].strip().lower()
    if clean_mime and clean_mime not in ALLOWED_MIME_TYPES:
        return False
    return True


def _valid_magic(file_storage) -> bool:
    """Kiểm tra magic bytes — không phụ thuộc vào tên file hay Content-Type header."""
    try:
        header = file_storage.stream.read(8)
        file_storage.stream.seek(0)
    except Exception:
        return False
    if not header:
        return False
    # PDF / JPEG / PNG / GIF: kiểm tra magic
    for magic, _ in _MAGIC_BYTES:
        if header[:len(magic)] == magic:
            return True
    # txt: không có magic cố định — chấp nhận nếu header là UTF-8/ASCII hợp lệ
    try:
        header.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


def get_uploads_dir():
    """Get uploads directory"""
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir


@applications_bp.route('/create', methods=['POST'])
def create_application():
    """Citizen creates application and uploads files"""
    try:
        # Check authentication
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        applicant_id = request.user_id
        service_id = request.form.get('serviceId')
        data_str = request.form.get('data', '{}')
        
        # Parse data
        try:
            data = json.loads(data_str)
        except (json.JSONDecodeError, ValueError):
            data = {}
        
        # Validate serviceId
        if not service_id:
            return jsonify({
                'success': False,
                'message': 'Thiếu serviceId'
            }), 400
        
        # Check if serviceId exists
        from models.public_service import PublicService
        service = PublicService.find_by_id(service_id)
        if not service:
            return jsonify({
                'success': False,
                'message': 'serviceId không hợp lệ'
            }), 400
        
        # Check for uploaded files
        if 'files' not in request.files or len(request.files.getlist('files')) == 0:
            return jsonify({
                'success': False,
                'message': 'Phải upload ít nhất 1 file hoặc ảnh khi nộp hồ sơ'
            }), 400
        
        # Create application
        app = Application.create({
            'applicantId': applicant_id,
            'serviceId': service_id,
            'data': data
        })
        
        # Handle uploaded files
        files = request.files.getlist('files')
        uploads_dir = get_uploads_dir()
        
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename, file.content_type) or not _valid_magic(file):
                    continue
                
                # Save file
                timestamp = int(datetime.now().timestamp() * 1000)
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{timestamp}-{app.get('id')}.{ext}"
                filepath = os.path.join(uploads_dir, filename)
                
                file.save(filepath)
                
                # Create document record
                doc = Document.create({
                    'applicationId': app.get('id'),
                    'filename': filename,
                    'originalName': secure_filename(file.filename),
                    'mimeType': file.content_type or 'application/octet-stream',
                    'size': os.path.getsize(filepath),
                    'storagePath': f'uploads/{filename}'
                })
                
                # Attach document to application
                app = Application.attach_document(app.get('id'), doc)
                
                # Process document asynchronously
                def process_async():
                    try:
                        text = process_document(filepath, file.filename)
                        if text:
                            Document.update(doc.get('id'), {'processedText': text})
                    except Exception as e:
                        log.error(f'Document processing failed: {e}', exc_info=True)
                
                thread = threading.Thread(target=process_async)
                thread.daemon = True
                thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Ứng dụng đã được tạo',
            'data': {
                'application': app
            }
        }), 201
    
    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e) or 'Lỗi tạo hồ sơ'
        }), 500


@applications_bp.route('/<id>/update', methods=['PUT'])
def update_application(id):
    """Update application"""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        app = Application.find_by_id(id)
        if not app:
            return jsonify({
                'success': False,
                'message': 'Hồ sơ không tìm thấy'
            }), 404
        
        if app.get('applicantId') != request.user_id:
            return jsonify({
                'success': False,
                'message': 'Không có quyền'
            }), 403
        
        data = request.get_json()
        if not data:
            data = {}
        
        updates = {}
        if 'data' in data:
            updates['data'] = data.get('data')
        if 'serviceId' in data:
            updates['serviceId'] = data.get('serviceId')
        
        updated = Application.update(id, updates)
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật hồ sơ thành công',
            'data': {
                'application': updated
            }
        }), 200
    
    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Lỗi cập nhật hồ sơ'
        }), 500


@applications_bp.route('/<id>/status', methods=['PUT'])
def update_status(id):
    """Update application status"""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        app = Application.find_by_id(id)
        if not app:
            return jsonify({
                'success': False,
                'message': 'Hồ sơ không tìm thấy'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        status = data.get('status')
        note = data.get('note', '')
        
        # Only applicant can update their own status to specific values
        allowed_by_applicant = ['request_more_info', 'withdraw']
        
        if request.user_id == app.get('applicantId') and status in allowed_by_applicant:
            # Ưu tiên cập nhật PostgreSQL; fallback file-based nếu cần
            pg_app = _pg_get_application(id)
            if pg_app:
                db.session.execute(text('''
                    UPDATE public.applications SET status = :st, updated_at = now()
                    WHERE id = :id
                '''), {'st': status, 'id': id})
                db.session.execute(text('''
                    INSERT INTO public.application_status_history
                        (application_id, status, note, by)
                    VALUES (:app_id, :st, :note, :by)
                '''), {'app_id': id, 'st': status, 'note': note, 'by': request.user_id})
                db.session.commit()
            else:
                Application.update(id, {'currentStatus': status})
                StatusTracking.create({'applicationId': id, 'status': status,
                                       'note': note, 'by': request.user_id})
            
            return jsonify({
                'success': True,
                'message': 'Trạng thái đã được thêm',
                'data': {
                    'status': status
                }
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Không cho phép thay đổi trạng thái'
        }), 403
    
    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Lỗi thay đổi trạng thái'
        }), 500


@applications_bp.route('/<id>', methods=['GET'])
def get_application(id):
    """Get application with documents and status"""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        app = Application.find_by_id(id)
        if not app:
            return jsonify({
                'success': False,
                'message': 'Hồ sơ không tìm thấy'
            }), 404
        
        # Check authorization (applicant or admin)
        if app.get('applicantId') != request.user_id and getattr(request, 'role', None) != 'admin':
            return jsonify({
                'success': False,
                'message': 'Không có quyền'
            }), 403
        
        documents = Application.get_documents(id)
        status_history = Application.get_status_history(id)
        
        return jsonify({
            'success': True,
            'data': {
                'application': app,
                'documents': documents,
                'statusHistory': status_history
            }
        }), 200
    
    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Lỗi lấy hồ sơ'
        }), 500


@applications_bp.route('/<id>/upload', methods=['POST'])
def attach_files(id):
    """Attach additional files to application"""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        app = Application.find_by_id(id)
        if not app:
            return jsonify({
                'success': False,
                'message': 'Hồ sơ không tìm thấy'
            }), 404
        
        if app.get('applicantId') != request.user_id:
            return jsonify({
                'success': False,
                'message': 'Không có quyền'
            }), 403
        
        # Check for uploaded files
        if 'files' not in request.files or len(request.files.getlist('files')) == 0:
            return jsonify({
                'success': False,
                'message': 'Phải upload ít nhất 1 file hoặc ảnh'
            }), 400
        
        attached = []
        files = request.files.getlist('files')
        uploads_dir = get_uploads_dir()
        
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename, file.content_type) or not _valid_magic(file):
                    continue
                
                # Save file
                timestamp = int(datetime.now().timestamp() * 1000)
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{timestamp}-{app.get('id')}.{ext}"
                filepath = os.path.join(uploads_dir, filename)
                
                file.save(filepath)
                
                # Create document record
                doc = Document.create({
                    'applicationId': app.get('id'),
                    'filename': filename,
                    'originalName': secure_filename(file.filename),
                    'mimeType': file.content_type or 'application/octet-stream',
                    'size': os.path.getsize(filepath),
                    'storagePath': f'uploads/{filename}'
                })
                
                # Attach document to application
                Application.attach_document(app.get('id'), doc)
                attached.append(doc)
                
                # Process document asynchronously
                def process_async():
                    try:
                        text = process_document(filepath, file.filename)
                        if text:
                            Document.update(doc.get('id'), {'processedText': text})
                    except Exception as e:
                        log.error(f'Document processing failed: {e}', exc_info=True)
                
                thread = threading.Thread(target=process_async)
                thread.daemon = True
                thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Files uploaded and attached',
            'data': {
                'attached': attached
            }
        }), 200

    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Lỗi khi upload file'
        }), 500


@applications_bp.route('/search', methods=['GET'])
def search_applications():
    """
    Tra cứu hồ sơ theo mã hồ sơ hoặc số CCCD — đọc từ PostgreSQL.
    Query params:
      q      — mã hồ sơ (id prefix) hoặc tên người nộp
      cccd   — tìm chính xác theo CCCD của người nộp
      status — lọc theo trạng thái
    Công dân chỉ thấy hồ sơ của mình; admin thấy tất cả.
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        q        = (request.args.get('q') or '').strip()
        cccd     = (request.args.get('cccd') or '').strip()
        status   = (request.args.get('status') or '').strip()
        is_admin = getattr(request, 'role', '') == 'admin'

        conditions, params = [], {}

        # Phân quyền: công dân chỉ thấy hồ sơ của mình
        if not is_admin:
            conditions.append('a.applicant_id = :uid')
            params['uid'] = request.user_id

        # Lọc CCCD: join qua bảng users
        if cccd:
            conditions.append('u.cccd_number = :cccd')
            params['cccd'] = cccd

        # Lọc mã hồ sơ hoặc tên người nộp (dùng materialized column thay JSONB)
        if q:
            conditions.append(
                "(LOWER(a.id) LIKE :q OR LOWER(COALESCE(a.applicant_name, a.data->>'applicantName', '')) LIKE :q)"
            )
            params['q'] = f'%{q.lower()}%'

        # Lọc trạng thái
        if status:
            conditions.append('a.status = :status')
            params['status'] = status

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        join  = 'LEFT JOIN public.users u ON u.id = a.applicant_id' if cccd else ''

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 10)), 50)
        offset = (page - 1) * limit

        # COUNT query để tránh fetch toàn bộ rồi slice
        count_where = where.replace('a.id, a.applicant_id', 'COUNT(*)')
        total_row = db.session.execute(text(f'''
            SELECT COUNT(*) FROM public.applications a {join} {where}
        '''), params).fetchone()
        total = total_row[0] if total_row else 0

        rows = db.session.execute(text(f'''
            SELECT a.id, a.applicant_id, a.service_id, a.status, a.data,
                   a.signature_type, a.submitted_at, a.created_at, a.updated_at
            FROM public.applications a
            {join}
            {where}
            ORDER BY a.created_at DESC
            LIMIT :limit OFFSET :offset
        '''), {**params, 'limit': limit, 'offset': offset}).fetchall()

        dicts = [_pg_row_to_dict(r) for r in rows]

        # Batch fetch history (1 query thay vì N queries)
        app_ids   = [d['id'] for d in dicts]
        hist_map  = _pg_get_history_batch(app_ids)
        for d in dicts:
            d['statusHistory'] = hist_map.get(d['id'], [])
        results = dicts

        return jsonify({
            'success': True,
            'data': results,
            'pagination': {'page': page, 'limit': limit, 'total': total},
        })

    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/my', methods=['GET'])
def my_applications():
    """Danh sách hồ sơ của người dùng hiện tại — đọc từ PostgreSQL."""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        status = (request.args.get('status') or '').strip() or None
        apps   = _pg_my_applications(request.user_id, status)
        return jsonify({'success': True, 'data': apps, 'total': len(apps)})
    except Exception as e:
        log.error(f'applications_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
#  NEW — Online submission flow (PostgreSQL-backed)
# ══════════════════════════════════════════════════════════════════════════════

@applications_bp.route('/requirements/<service_id>', methods=['GET'])
def get_service_requirements(service_id):
    """
    Bước 2: Lấy danh sách giấy tờ yêu cầu cho một dịch vụ.

    GET /api/applications/requirements/<service_id>

    Response:
      {
        "success": true,
        "serviceId": "...",
        "requirements": [
          {
            "id": "...",
            "docName": "CCCD / Căn cước công dân",
            "docDescription": "Bản gốc còn hiệu lực",
            "isRequired": true,
            "docType": "original",    // original | copy | certified_copy
            "orderIndex": 0
          }, ...
        ]
      }
    """
    try:
        requirements = ServiceRequirement.find_by_service_id(service_id)
        return jsonify({
            'success':      True,
            'serviceId':    service_id,
            'requirements': requirements,
            'total':        len(requirements),
        })
    except Exception as e:
        log.error(f'get_service_requirements error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/draft', methods=['POST'])
def create_draft():
    """
    Bước 3 (khởi tạo): Tạo bản nháp hồ sơ — chưa cần file.
    Trả về app_id để frontend dùng khi upload từng file.

    POST /api/applications/draft
    Body (JSON):
      {
        "serviceId": "...",
        "signatureType": "electronic" | "vneid" | "usb_token",  // tuỳ chọn
        "data": {                                                  // thông tin khai
          "applicantName": "...",
          "applicantDob":  "...",
          "applicantPhone": "...",
          ...
        }
      }

    Response:
      { "success": true, "data": { "application": { ... } } }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        body = request.get_json(silent=True) or {}
        service_id     = (body.get('serviceId') or '').strip()
        signature_type = body.get('signatureType')
        form_data      = body.get('data', {})

        if not service_id:
            return jsonify({'success': False, 'message': 'Thiếu serviceId'}), 400

        app = _pg_create_application(
            applicant_id   = request.user_id,
            service_id     = service_id,
            data           = form_data,
            signature_type = signature_type,
        )
        log.info(f'Draft created: {app["id"]} by {request.user_id}')
        return jsonify({'success': True, 'data': {'application': app}}), 201

    except Exception as e:
        log.error(f'create_draft error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/documents', methods=['POST'])
def upload_document(app_id):
    """
    Bước 3 (upload): Đính kèm file cho một yêu cầu giấy tờ cụ thể.
    Gọi nhiều lần — mỗi lần một file tương ứng một requirement.

    POST /api/applications/<app_id>/documents
    Form fields:
      requirementId  — id của requirement (từ /requirements/<service_id>)
      file           — file upload (1 file)

    Response:
      { "success": true, "data": { "document": { ... } } }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] not in ('draft', 'more_info'):
            return jsonify({
                'success': False,
                'message': f'Không thể upload khi hồ sơ ở trạng thái "{app["statusLabel"]}"'
            }), 400

        if 'file' not in request.files or not request.files['file'].filename:
            return jsonify({'success': False, 'message': 'Thiếu file'}), 400

        file = request.files['file']
        if not allowed_file(file.filename, file.content_type):
            return jsonify({
                'success': False,
                'message': f'Định dạng không được hỗ trợ. Chấp nhận: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        if not _valid_magic(file):
            return jsonify({
                'success': False,
                'message': 'File không hợp lệ (nội dung không khớp định dạng khai báo)'
            }), 400

        requirement_id = (request.form.get('requirementId') or '').strip() or None

        # Lưu file
        uploads_dir = get_uploads_dir()
        ts  = int(datetime.now().timestamp() * 1000)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename     = f'{ts}-{app_id[:8]}.{ext}'
        filepath     = os.path.join(uploads_dir, filename)
        file.save(filepath)

        doc = _pg_add_document(
            app_id        = app_id,
            requirement_id= requirement_id,
            filename      = filename,
            original_name = secure_filename(file.filename),
            mime_type     = file.content_type or 'application/octet-stream',
            size          = os.path.getsize(filepath),
            storage_path  = f'uploads/{filename}',
        )

        # Trích xuất text bất đồng bộ (Gemini)
        def _extract():
            try:
                text_content = process_document(filepath, file.filename)
                if text_content:
                    db.session.execute(text('''
                        UPDATE public.application_documents
                        SET processed_text = :txt
                        WHERE id = :id
                    '''), {'txt': text_content, 'id': doc['id']})
                    db.session.commit()
            except Exception as ex:
                log.error(f'Document extraction failed: {ex}')

        t = threading.Thread(target=_extract, daemon=True)
        t.start()

        log.info(f'Document uploaded: {doc["id"]} → app {app_id}')
        return jsonify({'success': True, 'data': {'document': doc}}), 201

    except Exception as e:
        log.error(f'upload_document error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/submit', methods=['PUT'])
def submit_application(app_id):
    """
    Bước 4: Xác nhận nộp hồ sơ chính thức.
    Chuyển trạng thái draft → submitted, ghi nhận thời gian nộp.

    PUT /api/applications/<app_id>/submit
    Body (JSON, tuỳ chọn):
      {
        "signatureType": "electronic" | "vneid" | "usb_token",
        "data": { ... }   // cập nhật thông tin khai nếu cần
      }

    Validation:
      - Hồ sơ phải đang ở trạng thái 'draft'
      - Phải có ít nhất 1 file đính kèm
      - Tất cả giấy tờ bắt buộc (isRequired=true) phải đã upload

    Response:
      { "success": true, "data": { "application": { ... }, "documents": [...], "statusHistory": [...] } }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] != 'draft':
            return jsonify({
                'success': False,
                'message': f'Hồ sơ đang ở trạng thái "{app["statusLabel"]}", không thể nộp lại'
            }), 400

        # Kiểm tra file đính kèm
        docs = _pg_get_documents(app_id)
        if not docs:
            return jsonify({
                'success': False,
                'message': 'Phải đính kèm ít nhất 1 giấy tờ trước khi nộp'
            }), 400

        # Kiểm tra giấy tờ bắt buộc còn thiếu
        requirements = ServiceRequirement.find_by_service_id(app['serviceId'] or '')
        required_ids  = {r['id'] for r in requirements if r['isRequired']}
        uploaded_req_ids = {d['requirementId'] for d in docs if d.get('requirementId')}
        missing = [
            r['docName'] for r in requirements
            if r['isRequired'] and r['id'] not in uploaded_req_ids
        ]
        if missing:
            return jsonify({
                'success': False,
                'message': 'Còn thiếu giấy tờ bắt buộc',
                'missing': missing,
            }), 400

        # Cập nhật body (signatureType, data bổ sung)
        body = request.get_json(silent=True) or {}
        updates: dict = {
            'status':       'submitted',
            'submitted_at': 'now()',
        }
        if body.get('signatureType'):
            updates['signature_type'] = body['signatureType']
        if body.get('data'):
            merged = {**(app.get('data') or {}), **body['data']}
            updates['data'] = json.dumps(merged, ensure_ascii=False)

        # submitted_at = now() không thể dùng param bình thường
        db.session.execute(text('''
            UPDATE public.applications
            SET status = 'submitted',
                submitted_at = now(),
                updated_at   = now()
                ''' + (", signature_type = :sig" if body.get('signatureType') else '') + '''
                ''' + (", data = :data"           if body.get('data')          else '') + '''
            WHERE id = :app_id
        '''), {
            'app_id': app_id,
            **({'sig':  body['signatureType']}  if body.get('signatureType') else {}),
            **({'data': updates.get('data', '')} if body.get('data')          else {}),
        })

        # Ghi lịch sử
        db.session.execute(text('''
            INSERT INTO public.application_status_history
                (application_id, status, note, by)
            VALUES (:app_id, 'submitted', 'Nộp hồ sơ chính thức', :by)
        '''), {'app_id': app_id, 'by': request.user_id})
        db.session.commit()

        app_updated = _pg_get_application(app_id)
        history     = _pg_get_history(app_id)

        log.info(f'Application submitted: {app_id} by {request.user_id}')
        return jsonify({
            'success': True,
            'message': 'Nộp hồ sơ thành công',
            'data': {
                'application':   app_updated,
                'documents':     docs,
                'statusHistory': history,
            }
        })

    except Exception as e:
        log.error(f'submit_application error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/draft', methods=['DELETE'])
def delete_draft(app_id):
    """
    Xoá bản nháp (chỉ khi còn ở trạng thái draft).

    DELETE /api/applications/<app_id>/draft
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] != 'draft':
            return jsonify({
                'success': False,
                'message': f'Chỉ có thể xoá bản nháp, hồ sơ hiện đang "{app["statusLabel"]}"'
            }), 400

        # Xoá file vật lý
        docs = _pg_get_documents(app_id)
        uploads_dir = get_uploads_dir()
        for doc in docs:
            fpath = os.path.join(uploads_dir, doc.get('filename', ''))
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass

        # Xoá DB (ON DELETE CASCADE xử lý documents + status_history)
        db.session.execute(
            text('DELETE FROM public.applications WHERE id = :id'),
            {'id': app_id}
        )
        db.session.commit()

        log.info(f'Draft deleted: {app_id} by {request.user_id}')
        return jsonify({'success': True, 'message': 'Đã xoá bản nháp'})

    except Exception as e:
        log.error(f'delete_draft error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/my/online', methods=['GET'])
def my_online_applications():
    """
    Danh sách hồ sơ trực tuyến (PostgreSQL) của người dùng hiện tại.

    Query params:
      status — lọc theo trạng thái (draft | submitted | in_review | ...)
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        status = (request.args.get('status') or '').strip() or None
        apps   = _pg_my_applications(request.user_id, status)

        # Gắn thêm số lượng documents cho mỗi hồ sơ
        for app in apps:
            docs = _pg_get_documents(app['id'])
            app['documentCount'] = len(docs)

        return jsonify({'success': True, 'data': apps, 'total': len(apps)})

    except Exception as e:
        log.error(f'my_online_applications error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/online', methods=['GET'])
def get_online_application(app_id):
    """
    Chi tiết hồ sơ trực tuyến kèm documents và lịch sử trạng thái.

    GET /api/applications/<app_id>/online
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id and getattr(request, 'role', '') != 'admin':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403

        docs    = _pg_get_documents(app_id)
        history = _pg_get_history(app_id)

        # Lấy danh sách yêu cầu để frontend biết còn thiếu gì
        requirements = ServiceRequirement.find_by_service_id(app['serviceId'] or '')
        uploaded_req_ids = {d['requirementId'] for d in docs if d.get('requirementId')}
        for req in requirements:
            req['uploaded'] = req['id'] in uploaded_req_ids

        return jsonify({
            'success': True,
            'data': {
                'application':   app,
                'documents':     docs,
                'statusHistory': history,
                'requirements':  requirements,
            }
        })

    except Exception as e:
        log.error(f'get_online_application error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Gợi ý thủ tục + giấy tờ (SuggestProcedure integration) ──────────────────

@applications_bp.route('/suggest-requirements', methods=['POST'])
def suggest_requirements():
    """
    Gợi ý thủ tục hành chính và danh sách giấy tờ cần thiết.

    POST /api/applications/suggest-requirements
    Body: {
      "query":     "tôi muốn làm căn cước",
      "topK":      4,       // optional, default 4
      "threshold": 0.45     // optional, default 0.45
    }

    Response:
    {
      "success": true,
      "data": {
        "query": "...",
        "suggestions": [
          {
            "procedure_name": "Cấp căn cước công dân",
            "similarity_score": 0.92,
            "service_key": "cccd",
            "requirements": [
              { "docName": "CCCD cũ", "isRequired": true, ... },
              ...
            ],
            "link": "https://dichvucong.gov.vn/..."
          }
        ],
        "explanation": "Tìm thấy 2 thủ tục liên quan...",
        "total": 2
      }
    }
    """
    try:
        payload   = request.get_json(silent=True) or {}
        query     = (payload.get('query') or '').strip()
        top_k     = int(payload.get('topK') or 4)
        threshold = float(payload.get('threshold') or 0.45)

        if not query:
            return jsonify({'success': False, 'message': 'Thiếu query'}), 400

        from services.suggest_service import suggest_with_requirements
        result = suggest_with_requirements(query=query, top_k=top_k, threshold=threshold)

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        log.error(f'suggest_requirements error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
#  USER FLOW — Quản lý hồ sơ sau khi tạo nháp
# ══════════════════════════════════════════════════════════════════════════════

@applications_bp.route('/<app_id>/data', methods=['PUT'])
def update_draft_data(app_id):
    """
    Cập nhật thông tin khai (form data) cho hồ sơ đang ở draft / more_info.

    PUT /api/applications/<app_id>/data
    Body: { "data": { "applicantName": "...", ... } }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] not in ('draft', 'more_info'):
            return jsonify({'success': False, 'message': 'Chỉ được sửa khi hồ sơ ở trạng thái nháp'}), 400

        body = request.get_json(silent=True) or {}
        new_data = body.get('data', {})
        merged   = {**(app.get('data') or {}), **new_data}

        db.session.execute(text('''
            UPDATE public.applications
            SET data = :data, updated_at = now()
            WHERE id = :app_id
        '''), {'data': json.dumps(merged, ensure_ascii=False), 'app_id': app_id})
        db.session.commit()

        return jsonify({'success': True, 'data': {'application': _pg_get_application(app_id)}})

    except Exception as e:
        log.error(f'update_draft_data error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/check-missing', methods=['GET'])
def check_missing_documents(app_id):
    """
    Kiểm tra giấy tờ bắt buộc còn thiếu.

    GET /api/applications/<app_id>/check-missing
    Response:
      {
        "success": true,
        "data": {
          "missing":    [{ "id", "docName", "docDescription", "docType" }],
          "uploaded":   [{ "id", "docName", ... }],
          "canSubmit":  true | false
        }
      }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403

        requirements        = ServiceRequirement.find_by_service_id(app['serviceId'] or '')
        docs                = _pg_get_documents(app_id)
        uploaded_req_ids    = {d['requirementId'] for d in docs if d.get('requirementId')}

        missing  = [r for r in requirements if r['isRequired'] and r['id'] not in uploaded_req_ids]
        uploaded = [r for r in requirements if r['id'] in uploaded_req_ids]

        return jsonify({'success': True, 'data': {
            'missing':   missing,
            'uploaded':  uploaded,
            'canSubmit': len(missing) == 0 and len(docs) > 0,
        }})

    except Exception as e:
        log.error(f'check_missing_documents error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/documents/<doc_id>', methods=['DELETE'])
def delete_document(app_id, doc_id):
    """
    Xoá một file đính kèm (chỉ khi hồ sơ còn ở draft / more_info).

    DELETE /api/applications/<app_id>/documents/<doc_id>
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] not in ('draft', 'more_info'):
            return jsonify({'success': False, 'message': 'Không thể xoá file ở trạng thái này'}), 400

        # Lấy thông tin file
        row = db.session.execute(text('''
            SELECT id, filename FROM public.application_documents
            WHERE id = :doc_id AND application_id = :app_id
        '''), {'doc_id': doc_id, 'app_id': app_id}).fetchone()

        if not row:
            return jsonify({'success': False, 'message': 'Tài liệu không tìm thấy'}), 404

        filename = row[1]

        # Xoá DB record
        db.session.execute(text(
            'DELETE FROM public.application_documents WHERE id = :doc_id'
        ), {'doc_id': doc_id})
        db.session.commit()

        # Xoá file vật lý (non-fatal)
        fpath = os.path.join(get_uploads_dir(), filename)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except OSError:
                pass

        log.info(f'Document deleted: {doc_id} from app {app_id}')
        return jsonify({'success': True, 'message': 'Đã xoá tài liệu'})

    except Exception as e:
        log.error(f'delete_document error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/resubmit', methods=['PUT'])
def resubmit_application(app_id):
    """
    Nộp lại hồ sơ sau khi bổ sung giấy tờ theo yêu cầu (trạng thái more_info).

    PUT /api/applications/<app_id>/resubmit
    Body (tùy chọn): { "note": "Tôi đã bổ sung đầy đủ giấy tờ theo yêu cầu" }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] != 'more_info':
            return jsonify({'success': False,
                            'message': 'Chỉ có thể nộp lại khi hồ sơ ở trạng thái "Yêu cầu bổ sung"'}), 400

        docs = _pg_get_documents(app_id)
        if not docs:
            return jsonify({'success': False, 'message': 'Phải có ít nhất 1 tài liệu'}), 400

        # Kiểm tra giấy tờ bắt buộc
        requirements      = ServiceRequirement.find_by_service_id(app['serviceId'] or '')
        uploaded_req_ids  = {d['requirementId'] for d in docs if d.get('requirementId')}
        missing           = [r['docName'] for r in requirements if r['isRequired'] and r['id'] not in uploaded_req_ids]
        if missing:
            return jsonify({'success': False, 'message': 'Còn thiếu giấy tờ bắt buộc', 'missing': missing}), 400

        body = request.get_json(silent=True) or {}
        note = body.get('note', 'Nộp lại hồ sơ sau khi bổ sung giấy tờ')

        db.session.execute(text('''
            UPDATE public.applications
            SET status = 'submitted', updated_at = now()
            WHERE id = :app_id
        '''), {'app_id': app_id})
        db.session.execute(text('''
            INSERT INTO public.application_status_history (application_id, status, note, by)
            VALUES (:app_id, 'submitted', :note, :by)
        '''), {'app_id': app_id, 'note': note, 'by': request.user_id})
        db.session.commit()

        log.info(f'Application resubmitted: {app_id}')
        return jsonify({'success': True, 'message': 'Nộp lại hồ sơ thành công',
                        'data': {'application': _pg_get_application(app_id)}})

    except Exception as e:
        log.error(f'resubmit_application error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/withdraw', methods=['PUT'])
def withdraw_application(app_id):
    """
    Rút hồ sơ (chuyển sang trạng thái withdraw).
    Cho phép khi hồ sơ đang ở draft, submitted, hoặc in_review.

    PUT /api/applications/<app_id>/withdraw
    Body (tùy chọn): { "reason": "..." }
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404
        if app['applicantId'] != request.user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        if app['status'] not in ('draft', 'submitted', 'in_review', 'more_info'):
            return jsonify({'success': False,
                            'message': f'Không thể rút hồ sơ ở trạng thái "{app["statusLabel"]}"'}), 400

        body   = request.get_json(silent=True) or {}
        reason = body.get('reason', 'Người dùng rút hồ sơ')

        db.session.execute(text('''
            UPDATE public.applications
            SET status = 'withdraw', updated_at = now()
            WHERE id = :app_id
        '''), {'app_id': app_id})
        db.session.execute(text('''
            INSERT INTO public.application_status_history (application_id, status, note, by)
            VALUES (:app_id, 'withdraw', :note, :by)
        '''), {'app_id': app_id, 'note': reason, 'by': request.user_id})
        db.session.commit()

        try:
            from services.notification_service import emit, status_notification
            _title, _prio = status_notification('withdraw')
            emit(getattr(request, 'user_id', None), 'document', _title,
                 f'Hồ sơ mã {app_id}', link='search', ref_id=app_id, priority=_prio)
        except Exception as _e:
            log.debug(f'[notif] hook rút hồ sơ bỏ qua: {_e}')

        return jsonify({'success': True, 'message': 'Đã rút hồ sơ',
                        'data': {'application': _pg_get_application(app_id)}})

    except Exception as e:
        log.error(f'withdraw_application error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """
    Phục vụ file đính kèm.
    GET /api/applications/uploads/<filename>
    Chỉ chủ hồ sơ hoặc admin/staff mới xem được.
    """
    from flask import send_from_directory, abort
    try:
        uploads_dir = get_uploads_dir()
        # Basic auth check — chủ hồ sơ hoặc nhân viên
        user_id = getattr(request, 'user_id', None)
        role    = getattr(request, 'role', None)
        if not user_id:
            from flask import g
            user_id = getattr(g, 'user_id', None)
            role    = getattr(g, 'role', None)

        if role not in ('admin', 'staff'):
            # Kiểm tra ownership qua DB
            row = db.session.execute(text('''
                SELECT a.applicant_id
                FROM public.application_documents d
                JOIN public.applications a ON a.id = d.application_id
                WHERE d.filename = :fname
                LIMIT 1
            '''), {'fname': filename}).fetchone()
            if not row or row[0] != user_id:
                abort(403)

        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        log.error(f'serve_upload error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Không thể tải file'}), 500


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN / OFFICER REVIEW FLOW
# ══════════════════════════════════════════════════════════════════════════════

def _require_staff():
    """Trả về (user_id, role) hoặc abort 403."""
    user_id = getattr(request, 'user_id', None)
    role    = getattr(request, 'role', None)
    if not user_id:
        from flask import g
        user_id = getattr(g, 'user_id', None)
        role    = getattr(g, 'role', None)
    return user_id, role


@applications_bp.route('/admin/list', methods=['GET'])
def admin_list_applications():
    """
    Danh sách hồ sơ cho cán bộ xem xét (admin / staff).

    GET /api/applications/admin/list
    Query params:
      status     — lọc theo trạng thái (submitted, in_review, ...)
      service_id — lọc theo dịch vụ
      date_from  — YYYY-MM-DD
      date_to    — YYYY-MM-DD
      page       — trang (default 1)
      per_page   — số hồ sơ mỗi trang (default 20, max 100)
      q          — tìm theo tên người nộp (fulltext trong data->>'applicantName')
    """
    user_id, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    status     = request.args.get('status', '').strip() or None
    service_id = request.args.get('service_id', '').strip() or None
    date_from  = request.args.get('date_from', '').strip() or None
    date_to    = request.args.get('date_to', '').strip() or None
    q          = request.args.get('q', '').strip() or None
    page       = max(1, int(request.args.get('page', 1)))
    # Accept both 'limit' (frontend) and 'per_page' (legacy) as page size param
    per_page   = min(100, max(1, int(request.args.get('limit') or request.args.get('per_page', 20))))
    offset     = (page - 1) * per_page

    try:
        conditions = []
        params: dict = {'limit': per_page, 'offset': offset}

        if status:
            conditions.append('a.status = :status')
            params['status'] = status
        if service_id:
            conditions.append('a.service_id = :service_id')
            params['service_id'] = service_id
        if date_from:
            conditions.append('a.submitted_at::date >= :date_from')
            params['date_from'] = date_from
        if date_to:
            conditions.append('a.submitted_at::date <= :date_to')
            params['date_to'] = date_to
        if q:
            conditions.append("a.data->>'applicantName' ILIKE :q")
            params['q'] = f'%{q}%'

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

        rows = db.session.execute(text(f'''
            SELECT a.id, a.applicant_id, a.service_id, a.status, a.data,
                   a.signature_type, a.submitted_at, a.created_at, a.updated_at,
                   (SELECT COUNT(*) FROM public.application_documents d WHERE d.application_id = a.id) AS doc_count,
                   u.cccd_number AS applicant_cccd,
                   u.full_name   AS applicant_full_name
            FROM public.applications a
            LEFT JOIN public.users u ON u.id = a.applicant_id
            {where}
            ORDER BY a.submitted_at DESC NULLS LAST, a.created_at DESC
            LIMIT :limit OFFSET :offset
        '''), params).fetchall()

        total_row = db.session.execute(text(f'''
            SELECT COUNT(*) FROM public.applications a {where}
        '''), {k: v for k, v in params.items() if k not in ('limit', 'offset')}).fetchone()
        total = total_row[0] if total_row else 0

        items = []
        for r in rows:
            d = _pg_row_to_dict(r[:9])
            d['docCount']      = r[9]
            d['applicantCccd'] = r[10]
            # Ưu tiên tên từ DB nếu data không có
            if not d.get('applicantName') and r[11]:
                d['applicantName'] = r[11]
            items.append(d)

        return jsonify({'success': True, 'data': {
            'items':    items,
            'total':    total,
            'page':     page,
            'perPage':  per_page,
            'pages':    (total + per_page - 1) // per_page,
        }})

    except Exception as e:
        log.error(f'admin_list_applications error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/review', methods=['PUT'])
def review_application(app_id):
    """
    Cán bộ xử lý hồ sơ — thay đổi trạng thái.

    PUT /api/applications/<app_id>/review
    Body:
      {
        "status": "in_review" | "approved" | "rejected" | "more_info",
        "note":   "Lý do hoặc ghi chú"
      }

    Luồng hợp lệ:
      submitted  → in_review
      in_review  → approved | rejected | more_info
      more_info  → in_review (sau khi người dùng nộp lại)
    """
    user_id, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    body       = request.get_json(silent=True) or {}
    new_status = (body.get('status') or '').strip()
    note       = body.get('note', '')

    allowed_statuses = {'in_review', 'approved', 'rejected', 'more_info'}
    if new_status not in allowed_statuses:
        return jsonify({'success': False,
                        'message': f'Trạng thái không hợp lệ. Cho phép: {allowed_statuses}'}), 400

    try:
        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404

        # Validate transition
        current = app['status']
        valid_transitions = {
            'submitted': {'in_review'},
            'in_review': {'approved', 'rejected', 'more_info'},
            'more_info':  {'in_review'},
        }
        allowed = valid_transitions.get(current, set())
        if new_status not in allowed:
            return jsonify({'success': False,
                            'message': f'Không thể chuyển từ "{STATUS_LABELS.get(current, current)}" sang "{STATUS_LABELS.get(new_status, new_status)}"'}), 400

        db.session.execute(text('''
            UPDATE public.applications
            SET status = :status, updated_at = now()
            WHERE id = :app_id
        '''), {'status': new_status, 'app_id': app_id})
        db.session.execute(text('''
            INSERT INTO public.application_status_history (application_id, status, note, by)
            VALUES (:app_id, :status, :note, :by)
        '''), {'app_id': app_id, 'status': new_status,
               'note': note or STATUS_LABELS.get(new_status, new_status), 'by': user_id})
        db.session.commit()

        log.info(f'Application {app_id} reviewed: {current} → {new_status} by {user_id}')
        return jsonify({'success': True, 'message': f'Đã cập nhật trạng thái: {STATUS_LABELS.get(new_status)}',
                        'data': {'application': _pg_get_application(app_id),
                                 'statusHistory': _pg_get_history(app_id)}})

    except Exception as e:
        log.error(f'review_application error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/<app_id>/notes', methods=['POST'])
def add_application_note(app_id):
    """
    Thêm ghi chú vào hồ sơ (cán bộ hoặc người dùng).

    POST /api/applications/<app_id>/notes
    Body: { "note": "Nội dung ghi chú" }
    """
    user_id, role = _require_staff()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    body = request.get_json(silent=True) or {}
    note = (body.get('note') or '').strip()
    if not note:
        return jsonify({'success': False, 'message': 'Thiếu nội dung ghi chú'}), 400

    try:
        app = _pg_get_application(app_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404

        # Người dùng chỉ ghi chú cho hồ sơ của mình
        if role not in ('admin', 'staff') and app['applicantId'] != user_id:
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403

        db.session.execute(text('''
            INSERT INTO public.application_status_history (application_id, status, note, by)
            VALUES (:app_id, :status, :note, :by)
        '''), {'app_id': app_id, 'status': app['status'], 'note': note, 'by': user_id})
        db.session.commit()

        return jsonify({'success': True, 'message': 'Đã thêm ghi chú',
                        'data': {'statusHistory': _pg_get_history(app_id)}})

    except Exception as e:
        log.error(f'add_application_note error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/admin/stats', methods=['GET'])
def admin_application_stats():
    """
    Thống kê hồ sơ cho dashboard quản trị.

    GET /api/applications/admin/stats
    Query: date_from, date_to (YYYY-MM-DD, mặc định 30 ngày gần nhất)

    Response:
      {
        "byStatus":  { "submitted": 12, "approved": 8, ... },
        "byService": [ { "serviceId": "...", "count": 5 }, ... ],
        "byDate":    [ { "date": "2026-04-01", "count": 3 }, ... ],
        "total":     25
      }
    """
    _, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    date_from = request.args.get('date_from', '').strip() or None
    date_to   = request.args.get('date_to', '').strip() or None

    try:
        date_filter = ''
        params: dict = {}
        if date_from:
            date_filter += ' AND created_at::date >= :date_from'
            params['date_from'] = date_from
        if date_to:
            date_filter += ' AND created_at::date <= :date_to'
            params['date_to'] = date_to

        by_status_rows = db.session.execute(text(f'''
            SELECT status, COUNT(*) as cnt
            FROM public.applications
            WHERE 1=1 {date_filter}
            GROUP BY status
        '''), params).fetchall()

        by_service_rows = db.session.execute(text(f'''
            SELECT service_id, COUNT(*) as cnt
            FROM public.applications
            WHERE 1=1 {date_filter}
            GROUP BY service_id
            ORDER BY cnt DESC
            LIMIT 10
        '''), params).fetchall()

        by_date_rows = db.session.execute(text(f'''
            SELECT created_at::date AS day, COUNT(*) as cnt
            FROM public.applications
            WHERE 1=1 {date_filter}
            GROUP BY day
            ORDER BY day
        '''), params).fetchall()

        by_status  = {r[0]: r[1] for r in by_status_rows}
        total      = sum(by_status.values())
        by_service = [{'serviceId': r[0], 'count': r[1]} for r in by_service_rows]
        by_date    = [{'date': str(r[0]), 'count': r[1]} for r in by_date_rows]

        return jsonify({'success': True, 'data': {
            'byStatus':  by_status,
            'byService': by_service,
            'byDate':    by_date,
            'total':     total,
        }})

    except Exception as e:
        log.error(f'admin_application_stats error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN — Quản lý danh sách giấy tờ yêu cầu (service_requirements)
# ══════════════════════════════════════════════════════════════════════════════

@applications_bp.route('/requirements', methods=['POST'])
def create_requirement():
    """
    Tạo giấy tờ yêu cầu cho dịch vụ.

    POST /api/applications/requirements
    Body:
      {
        "serviceId":       "cccd",
        "docName":         "CCCD / Căn cước công dân",
        "docDescription":  "Bản gốc còn hiệu lực",
        "isRequired":      true,
        "docType":         "original",   // original | copy | certified_copy
        "orderIndex":      0
      }
    """
    _, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    body = request.get_json(silent=True) or {}
    for f in ('serviceId', 'docName'):
        if not body.get(f):
            return jsonify({'success': False, 'message': f'Thiếu trường: {f}'}), 400

    try:
        req = ServiceRequirement.create({
            'serviceId':      body['serviceId'],
            'docName':        body['docName'],
            'docDescription': body.get('docDescription', ''),
            'isRequired':     bool(body.get('isRequired', True)),
            'docType':        body.get('docType', 'original'),
            'orderIndex':     int(body.get('orderIndex', 0)),
        })
        return jsonify({'success': True, 'data': {'requirement': req}}), 201

    except Exception as e:
        log.error(f'create_requirement error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/requirements/<req_id>', methods=['PUT'])
def update_requirement(req_id):
    """
    Cập nhật giấy tờ yêu cầu.
    PUT /api/applications/requirements/<req_id>
    """
    _, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    body = request.get_json(silent=True) or {}
    try:
        sets, params = [], {'req_id': req_id}
        field_map = {
            'docName':        'doc_name',
            'docDescription': 'doc_description',
            'isRequired':     'is_required',
            'docType':        'doc_type',
            'orderIndex':     'order_index',
        }
        for js_key, db_col in field_map.items():
            if js_key in body:
                sets.append(f'{db_col} = :{db_col}')
                params[db_col] = body[js_key]

        if not sets:
            return jsonify({'success': False, 'message': 'Không có trường nào để cập nhật'}), 400

        row = db.session.execute(text(f'''
            UPDATE public.service_requirements
            SET {", ".join(sets)}
            WHERE id = :req_id
            RETURNING id, service_id, doc_name, doc_description, is_required, doc_type, order_index
        '''), params).fetchone()

        if not row:
            return jsonify({'success': False, 'message': 'Không tìm thấy yêu cầu'}), 404

        db.session.commit()
        keys = ['id', 'serviceId', 'docName', 'docDescription', 'isRequired', 'docType', 'orderIndex']
        return jsonify({'success': True, 'data': {'requirement': dict(zip(keys, row))}})

    except Exception as e:
        log.error(f'update_requirement error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/requirements/<req_id>', methods=['DELETE'])
def delete_requirement(req_id):
    """
    Xoá giấy tờ yêu cầu.
    DELETE /api/applications/requirements/<req_id>
    """
    _, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    try:
        result = db.session.execute(text(
            'DELETE FROM public.service_requirements WHERE id = :req_id'
        ), {'req_id': req_id})
        db.session.commit()

        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Không tìm thấy yêu cầu'}), 404

        return jsonify({'success': True, 'message': 'Đã xoá giấy tờ yêu cầu'})

    except Exception as e:
        log.error(f'delete_requirement error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@applications_bp.route('/requirements/<service_id>/bulk', methods=['PUT'])
def bulk_update_requirements(service_id):
    """
    Cập nhật toàn bộ danh sách giấy tờ cho một dịch vụ (thay thế hoàn toàn).

    PUT /api/applications/requirements/<service_id>/bulk
    Body: {
      "requirements": [
        { "docName": "...", "docDescription": "...", "isRequired": true, "docType": "original", "orderIndex": 0 },
        ...
      ]
    }
    """
    _, role = _require_staff()
    if role not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    body = request.get_json(silent=True) or {}
    reqs = body.get('requirements', [])
    if not isinstance(reqs, list):
        return jsonify({'success': False, 'message': 'requirements phải là mảng'}), 400

    try:
        # Xoá cũ
        ServiceRequirement.delete_by_service_id(service_id)

        # Tạo mới
        created = []
        for i, r in enumerate(reqs):
            r['serviceId']  = service_id
            r['orderIndex'] = r.get('orderIndex', i)
            created.append(ServiceRequirement.create(r))

        return jsonify({'success': True, 'data': {
            'serviceId':    service_id,
            'requirements': created,
            'total':        len(created),
        }})

    except Exception as e:
        log.error(f'bulk_update_requirements error: {e}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
