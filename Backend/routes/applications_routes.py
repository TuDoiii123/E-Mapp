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

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

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

def _pg_create_application(applicant_id: str, service_id: str, data: dict,
                            signature_type: str | None = None) -> dict:
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


def _pg_update_application(app_id: str, updates: dict) -> dict:
    sets = ', '.join(f'{k} = :{k}' for k in updates)
    updates['app_id'] = app_id
    sql = text(f'''
        UPDATE public.applications
        SET {sets}, updated_at = now()
        WHERE id = :app_id
        RETURNING id, applicant_id, service_id, status, data, signature_type,
                  submitted_at, created_at, updated_at
    ''')
    row = db.session.execute(sql, updates).fetchone()
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
    d['statusLabel'] = STATUS_LABELS.get(d.get('status', ''), d.get('status', ''))
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


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
                if not allowed_file(file.filename):
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
            Application.update(id, {'currentStatus': status})
            StatusTracking.create({
                'applicationId': id,
                'status': status,
                'note': note,
                'by': request.user_id
            })
            
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
                if not allowed_file(file.filename):
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
    Tra cứu hồ sơ theo mã hồ sơ hoặc số CCCD.
    Query params:
      q     — mã hồ sơ (id prefix) hoặc CCCD
      cccd  — tìm chính xác theo CCCD của người nộp
      status — lọc theo trạng thái
    Công dân chỉ thấy hồ sơ của mình; admin thấy tất cả.
    """
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        q      = (request.args.get('q') or '').strip().lower()
        cccd   = (request.args.get('cccd') or '').strip()
        status = (request.args.get('status') or '').strip()
        is_admin = getattr(request, 'role', '') == 'admin'

        from models.user import FileStorage
        all_apps = FileStorage.read_json('applications.json')

        results = []
        for app in all_apps:
            # Phân quyền: công dân chỉ thấy hồ sơ của mình
            if not is_admin and app.get('applicantId') != request.user_id:
                continue

            # Lọc CCCD: tra cứu applicantId (user_id) qua bảng users
            if cccd:
                users = FileStorage.read_json('users.json')
                owner = next(
                    (u for u in users if u.get('cccdNumber') == cccd), None
                )
                if not owner or app.get('applicantId') != owner.get('id'):
                    continue

            # Lọc mã hồ sơ hoặc từ khóa
            if q and not (
                q in app.get('id', '').lower()
                or q in (app.get('data', {}).get('applicantName') or '').lower()
            ):
                continue

            # Lọc trạng thái
            if status and app.get('currentStatus') != status:
                continue

            # Lấy thêm lịch sử trạng thái và thông tin dịch vụ
            history = Application.get_status_history(app['id'])
            results.append({
                **app,
                'statusHistory': history,
            })

        # Sắp xếp mới nhất lên đầu
        results.sort(key=lambda a: a.get('createdAt', ''), reverse=True)

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 10)), 50)
        total = len(results)
        results = results[(page - 1) * limit: page * limit]

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
    """Danh sách hồ sơ của người dùng hiện tại"""
    try:
        if not hasattr(request, 'user_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401

        from models.user import FileStorage
        all_apps = FileStorage.read_json('applications.json')
        mine = [a for a in all_apps if a.get('applicantId') == request.user_id]
        mine.sort(key=lambda a: a.get('createdAt', ''), reverse=True)

        status = request.args.get('status')
        if status:
            mine = [a for a in mine if a.get('currentStatus') == status]

        return jsonify({'success': True, 'data': mine, 'total': len(mine)})
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
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'Định dạng không được hỗ trợ. Chấp nhận: {", ".join(ALLOWED_EXTENSIONS)}'
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
