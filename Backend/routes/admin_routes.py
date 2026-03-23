"""
Admin Routes — CRUD tài khoản, địa điểm, thủ tục + review hồ sơ
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from models.application import Application
from models.status_tracking import StatusTracking
from models.user import User, FileStorage
from models.location import Location
from logger import get_logger

log = get_logger('admin_routes')

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _require_admin():
    if not getattr(request, 'user_id', None):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    return None


# ════════════════════════════════════════════════════════════════════════════════
# 1. HỒ SƠ — Review
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/applications/review', methods=['POST'])
def review_application():
    """Admin duyệt / từ chối hồ sơ"""
    err = _require_admin()
    if err:
        return err
    try:
        data           = request.get_json() or {}
        application_id = data.get('applicationId')
        action         = data.get('action')
        note           = data.get('note', '')

        if not application_id or not action:
            return jsonify({'success': False, 'message': 'Thiếu dữ liệu'}), 400

        app = Application.find_by_id(application_id)
        if not app:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404

        allowed_actions = ['approve', 'reject', 'request_more_info']
        if action not in allowed_actions:
            return jsonify({'success': False, 'message': 'Action không hợp lệ'}), 400

        status_map = {'approve': 'approved', 'reject': 'rejected', 'request_more_info': 'more_info'}
        status = status_map[action]

        Application.update(application_id, {'currentStatus': status})
        StatusTracking.create({'applicationId': application_id, 'status': status,
                               'note': note, 'by': request.user_id})

        return jsonify({'success': True, 'message': 'Đã cập nhật trạng thái',
                        'data': {'applicationId': application_id, 'status': status}})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 2. TÀI KHOẢN — CRUD
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/users', methods=['GET'])
def list_users():
    """Danh sách tất cả người dùng"""
    err = _require_admin()
    if err:
        return err
    try:
        users = FileStorage.read_json('users.json')
        # Ẩn password
        safe = [{k: v for k, v in u.items() if k != 'password'} for u in users]

        # Lọc theo role
        role = request.args.get('role')
        if role:
            safe = [u for u in safe if u.get('role') == role]

        # Tìm kiếm theo tên / CCCD
        q = (request.args.get('q') or '').strip().lower()
        if q:
            safe = [u for u in safe
                    if q in (u.get('fullName') or '').lower()
                    or q in (u.get('cccdNumber') or '').lower()
                    or q in (u.get('email') or '').lower()]

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 20)), 100)
        total = len(safe)
        safe  = safe[(page - 1) * limit: page * limit]

        return jsonify({'success': True, 'data': safe,
                        'pagination': {'page': page, 'limit': limit, 'total': total}})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id: str):
    err = _require_admin()
    if err:
        return err
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    return jsonify({'success': True, 'data': user})


@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Admin tạo tài khoản mới (ví dụ: tạo tài khoản nhân viên)"""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        required = ['cccdNumber', 'fullName', 'password']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Thiếu trường: {field}'}), 400

        data['id'] = str(int(datetime.now().timestamp() * 1000))
        user = User.create(data)
        return jsonify({'success': True, 'data': user}), 201
    except ValueError as e:
        log.error(f'admin_routes ValueError: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 409
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id: str):
    """Admin cập nhật thông tin / đổi role người dùng"""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        # Không cho đổi password qua route này
        data.pop('password', None)
        user = User.update(user_id, data)
        return jsonify({'success': True, 'data': user})
    except ValueError as e:
        log.error(f'admin_routes ValueError: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id: str):
    """Admin xóa tài khoản (soft: đặt role = disabled)"""
    err = _require_admin()
    if err:
        return err
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        # Ngăn admin tự xóa chính mình
        if user_id == request.user_id:
            return jsonify({'success': False, 'message': 'Không thể xóa tài khoản đang dùng'}), 400

        users = FileStorage.read_json('users.json')
        new_list = [u for u in users if u.get('id') != user_id]
        FileStorage.write_json('users.json', new_list)
        return jsonify({'success': True, 'message': 'Đã xóa tài khoản'})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<user_id>/reset-password', methods=['POST'])
def reset_password(user_id: str):
    """Admin đặt lại mật khẩu"""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        new_password = data.get('newPassword', '').strip()
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Mật khẩu tối thiểu 6 ký tự'}), 400

        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash(new_password, method='pbkdf2:sha256')

        users = FileStorage.read_json('users.json')
        found = False
        for u in users:
            if u.get('id') == user_id:
                u['password']  = hashed
                u['updatedAt'] = datetime.now().isoformat()
                found = True
                break
        if not found:
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
        FileStorage.write_json('users.json', users)
        return jsonify({'success': True, 'message': 'Đã đặt lại mật khẩu'})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 3. ĐỊA ĐIỂM — CRUD
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/locations', methods=['GET'])
def list_locations():
    err = _require_admin()
    if err:
        return err
    try:
        locs = Location.find_all()
        province = request.args.get('province')
        district = request.args.get('district')
        level    = request.args.get('level')
        q        = (request.args.get('q') or '').strip().lower()

        if province:
            locs = [l for l in locs if l.get('province') == province]
        if district:
            locs = [l for l in locs if l.get('district') == district]
        if level:
            locs = [l for l in locs if l.get('level') == level]
        if q:
            locs = [l for l in locs
                    if q in (l.get('name') or '').lower()
                    or q in (l.get('address') or '').lower()]

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 50)), 200)
        total = len(locs)
        locs  = locs[(page - 1) * limit: page * limit]
        return jsonify({'success': True, 'data': locs,
                        'pagination': {'page': page, 'limit': limit, 'total': total}})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/locations/<location_id>', methods=['GET'])
def get_location(location_id: str):
    err = _require_admin()
    if err:
        return err
    loc = Location.find_by_id(location_id)
    if not loc:
        return jsonify({'success': False, 'message': 'Địa điểm không tồn tại'}), 404
    return jsonify({'success': True, 'data': loc})


@admin_bp.route('/locations', methods=['POST'])
def create_location():
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Thiếu tên địa điểm'}), 400
        loc = Location.create(data)
        return jsonify({'success': True, 'data': loc}), 201
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/locations/<location_id>', methods=['PUT'])
def update_location(location_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        data  = request.get_json() or {}
        locs  = FileStorage.read_json('locations.json')
        found = False
        for l in locs:
            if l.get('id') == location_id:
                l.update(data)
                l['updatedAt'] = datetime.now().isoformat()
                found = True
                break
        if not found:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        FileStorage.write_json('locations.json', locs)
        updated = next(l for l in locs if l['id'] == location_id)
        return jsonify({'success': True, 'data': updated})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/locations/<location_id>', methods=['DELETE'])
def delete_location(location_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        locs     = FileStorage.read_json('locations.json')
        new_list = [l for l in locs if l.get('id') != location_id]
        if len(new_list) == len(locs):
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        FileStorage.write_json('locations.json', new_list)
        return jsonify({'success': True, 'message': 'Đã xóa địa điểm'})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 4. THỦ TỤC HÀNH CHÍNH — CRUD
# ════════════════════════════════════════════════════════════════════════════════

def _read_procedures() -> list:
    return FileStorage.read_json('public_services.json')

def _save_procedures(data: list):
    FileStorage.write_json('public_services.json', data)


@admin_bp.route('/procedures', methods=['GET'])
def list_procedures():
    err = _require_admin()
    if err:
        return err
    try:
        procs    = _read_procedures()
        category = request.args.get('category')
        province = request.args.get('province')
        q        = (request.args.get('q') or '').strip().lower()

        if category:
            procs = [p for p in procs if p.get('categoryId') == category
                     or p.get('category') == category]
        if province:
            procs = [p for p in procs if p.get('province') == province]
        if q:
            procs = [p for p in procs
                     if q in (p.get('name') or '').lower()
                     or q in (p.get('description') or '').lower()]

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 20)), 100)
        total = len(procs)
        procs = procs[(page - 1) * limit: page * limit]
        return jsonify({'success': True, 'data': procs,
                        'pagination': {'page': page, 'limit': limit, 'total': total}})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['GET'])
def get_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    procs = _read_procedures()
    proc  = next((p for p in procs if p.get('id') == proc_id), None)
    if not proc:
        return jsonify({'success': False, 'message': 'Thủ tục không tồn tại'}), 404
    return jsonify({'success': True, 'data': proc})


@admin_bp.route('/procedures', methods=['POST'])
def create_procedure():
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Thiếu tên thủ tục'}), 400
        procs = _read_procedures()
        data['id']        = data.get('id') or str(int(datetime.now().timestamp() * 1000))
        data['createdAt'] = datetime.now().isoformat()
        data['updatedAt'] = datetime.now().isoformat()
        data.setdefault('status', 'active')
        procs.append(data)
        _save_procedures(procs)
        return jsonify({'success': True, 'data': data}), 201
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['PUT'])
def update_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        data  = request.get_json() or {}
        procs = _read_procedures()
        found = False
        for p in procs:
            if p.get('id') == proc_id:
                p.update(data)
                p['id']        = proc_id  # không cho đổi id
                p['updatedAt'] = datetime.now().isoformat()
                found = True
                break
        if not found:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        _save_procedures(procs)
        updated = next(p for p in procs if p['id'] == proc_id)
        return jsonify({'success': True, 'data': updated})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['DELETE'])
def delete_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        procs    = _read_procedures()
        new_list = [p for p in procs if p.get('id') != proc_id]
        if len(new_list) == len(procs):
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        _save_procedures(new_list)
        return jsonify({'success': True, 'message': 'Đã xóa thủ tục'})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 5. THỐNG KÊ TỔNG QUAN
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    err = _require_admin()
    if err:
        return err
    try:
        users      = FileStorage.read_json('users.json')
        locs       = FileStorage.read_json('locations.json')
        procs      = FileStorage.read_json('public_services.json')
        apps       = FileStorage.read_json('applications.json')
        tickets    = FileStorage.read_json('queue_tickets.json')
        today      = datetime.now().strftime('%Y-%m-%d')

        return jsonify({'success': True, 'data': {
            'totalUsers':       len(users),
            'totalLocations':   len(locs),
            'totalProcedures':  len(procs),
            'totalApplications':len(apps),
            'pendingApplications': len([a for a in apps if a.get('currentStatus') in ('submitted', 'in_review')]),
            'ticketsToday':     len([t for t in tickets if t.get('date') == today]),
            'waitingToday':     len([t for t in tickets if t.get('date') == today and t.get('status') == 'waiting']),
        }})
    except Exception as e:
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
