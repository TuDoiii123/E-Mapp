"""
Notification API. Tất cả yêu cầu đăng nhập (request.user_id); broadcast yêu cầu admin.
"""
from flask import Blueprint, jsonify, request

from logger import get_logger
from models.notification import Notification, PushToken
from services.notification_service import emit_system_all

log = get_logger('notification_routes')
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')


def _uid():
    return getattr(request, 'user_id', None)


@notification_bp.route('', methods=['GET'])
def list_notifications():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    only_unread = request.args.get('unread') in ('1', 'true')
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
    except ValueError:
        limit = 50
    data = Notification.list_for(_uid(), only_unread=only_unread, limit=limit)
    return jsonify({'success': True, 'data': data, 'total': len(data)}), 200


@notification_bp.route('/unread-count', methods=['GET'])
def unread_count():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    return jsonify({'success': True, 'count': Notification.unread_count(_uid())}), 200


@notification_bp.route('/<notif_id>/read', methods=['POST'])
def mark_read(notif_id):
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    ok = Notification.mark_read(notif_id, _uid())
    return jsonify({'success': ok}), (200 if ok else 404)


@notification_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    n = Notification.mark_all_read(_uid())
    return jsonify({'success': True, 'updated': n}), 200


@notification_bp.route('/push-token', methods=['POST'])
def register_push_token():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    if not token:
        return jsonify({'success': False, 'message': 'Thiếu token'}), 400
    PushToken.register(_uid(), token, data.get('platform', 'web'))
    return jsonify({'success': True}), 200


@notification_bp.route('/push-token', methods=['DELETE'])
def remove_push_token():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    if token:
        PushToken.remove(token)
    return jsonify({'success': True}), 200


@notification_bp.route('/broadcast', methods=['POST'])
def broadcast():
    if not _uid():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Chỉ admin'}), 403
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Thiếu title'}), 400
    sent = emit_system_all(title, data.get('content', ''), data.get('link'))
    return jsonify({'success': True, 'sent': sent}), 200
