from flask import Blueprint, request, jsonify
from models.application import Application
from models.status_tracking import StatusTracking

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/applications/review', methods=['POST'])
def review_application():
    """Admin reviews application"""
    try:
        # Check authentication and admin role
        if not hasattr(request, 'user_id'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401
        
        if getattr(request, 'role', None) != 'admin':
            return jsonify({
                'success': False,
                'message': 'Forbidden'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            }), 400
        
        application_id = data.get('applicationId')
        action = data.get('action')
        note = data.get('note', '')
        
        if not application_id or not action:
            return jsonify({
                'success': False,
                'message': 'Thiếu dữ liệu'
            }), 400
        
        app = Application.find_by_id(application_id)
        if not app:
            return jsonify({
                'success': False,
                'message': 'Hồ sơ không tìm thấy'
            }), 404
        
        # Validate action
        allowed_actions = ['approve', 'reject', 'request_more_info']
        if action not in allowed_actions:
            return jsonify({
                'success': False,
                'message': 'Action không hợp lệ'
            }), 400
        
        # Map action to status
        status_map = {
            'approve': 'approved',
            'reject': 'rejected',
            'request_more_info': 'more_info'
        }
        status = status_map.get(action, 'in_review')
        
        # Update application
        Application.update(application_id, {'currentStatus': status})
        
        # Create status tracking record
        StatusTracking.create({
            'applicationId': application_id,
            'status': status,
            'note': note,
            'by': request.user_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Đã cập nhật trạng thái',
            'data': {
                'applicationId': application_id,
                'status': status
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Lỗi khi review hồ sơ'
        }), 500
