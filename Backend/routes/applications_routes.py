from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import threading
from datetime import datetime
from models.application import Application
from models.document import Document
from models.status_tracking import StatusTracking
from services.document_processor import process_document

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB


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
        except:
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
                        print(f'Document processing failed: {e}')
                
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
                        print(f'Document processing failed: {e}')
                
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
        return jsonify({
            'success': False,
            'message': 'Lỗi khi upload file'
        }), 500
