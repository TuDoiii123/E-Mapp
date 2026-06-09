"""
Admin Routes — CRUD tài khoản, địa điểm, thủ tục + review hồ sơ
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from models.user import User, FileStorage
from models.location import Location
from models.db import db
from logger import get_logger

log = get_logger('admin_routes')

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

_USER_COLS = 'id, cccd_number, full_name, date_of_birth, phone, email, role, is_vneid_verified, vneid_id, created_at, updated_at'


def _require_admin():
    if not getattr(request, 'user_id', None):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    return None


def _write_audit(action: str, resource: str, resource_id: str = None, detail: dict = None):
    """Ghi audit log vào DB — không raise exception nếu thất bại."""
    try:
        import json as _json
        db.session.execute(
            text('''INSERT INTO public.audit_logs
                        (actor_id, actor_role, action, resource, resource_id, detail, ip)
                    VALUES (:actor, :role, :action, :res, :res_id, :detail::jsonb, :ip)'''),
            {
                'actor':  getattr(request, 'user_id', None),
                'role':   getattr(request, 'role', None),
                'action': action,
                'res':    resource,
                'res_id': resource_id,
                'detail': _json.dumps(detail or {}, ensure_ascii=False),
                'ip':     request.headers.get('X-Forwarded-For', request.remote_addr or '')[:45],
            }
        )
        db.session.commit()
    except Exception as e:
        log.warning(f'[AUDIT] write failed: {e}')
        try: db.session.rollback()
        except Exception: pass


def _row_to_user(r) -> dict:
    """Chuyển row PostgreSQL → dict camelCase (không có password)."""
    return {
        'id':              r[0],
        'cccdNumber':      r[1],
        'fullName':        r[2],
        'dateOfBirth':     r[3],
        'phone':           r[4],
        'email':           r[5],
        'role':            r[6],
        'isVNeIDVerified': bool(r[7]),
        'vneidId':         r[8],
        'createdAt':       r[9].isoformat() if r[9] else None,
        'updatedAt':       r[10].isoformat() if r[10] else None,
    }


# ════════════════════════════════════════════════════════════════════════════════
# 1. HỒ SƠ — Review
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/applications/review', methods=['POST'])
def review_application():
    """Admin duyệt / từ chối hồ sơ — thao tác trực tiếp trên PostgreSQL."""
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

        allowed_actions = ['approve', 'reject', 'request_more_info']
        if action not in allowed_actions:
            return jsonify({'success': False, 'message': 'Action không hợp lệ'}), 400

        status_map = {'approve': 'approved', 'reject': 'rejected', 'request_more_info': 'more_info'}
        status = status_map[action]

        # Kiểm tra hồ sơ tồn tại trong PostgreSQL
        row = db.session.execute(
            text('SELECT id, status FROM public.applications WHERE id = :id'),
            {'id': application_id}
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Hồ sơ không tìm thấy'}), 404

        # Cập nhật trạng thái
        db.session.execute(
            text('UPDATE public.applications SET status = :status, updated_at = now() WHERE id = :id'),
            {'status': status, 'id': application_id}
        )
        # Ghi lịch sử
        db.session.execute(
            text('''INSERT INTO public.application_status_history
                        (application_id, status, note, by)
                    VALUES (:app_id, :status, :note, :by)'''),
            {'app_id': application_id, 'status': status,
             'note': note or f'Admin cập nhật: {status}', 'by': request.user_id}
        )
        db.session.commit()

        log.info(f'[AUDIT] admin={request.user_id} action={action} '
                 f'application={application_id} new_status={status}')
        _write_audit(action, 'application', application_id,
                     {'status': status, 'note': note, 'previous': row[1]})

        return jsonify({'success': True, 'message': 'Đã cập nhật trạng thái',
                        'data': {'applicationId': application_id, 'status': status}})
    except Exception as e:
        db.session.rollback()
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 2. TÀI KHOẢN — CRUD (PostgreSQL)
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/users', methods=['GET'])
def list_users():
    """Danh sách tất cả người dùng từ PostgreSQL."""
    err = _require_admin()
    if err:
        return err
    try:
        role = request.args.get('role')
        q    = (request.args.get('q') or '').strip().lower() or None

        conditions, params = [], {}
        if role:
            conditions.append('role = :role')
            params['role'] = role
        if q:
            conditions.append('(LOWER(full_name) LIKE :q OR cccd_number LIKE :q OR LOWER(email) LIKE :q)')
            params['q'] = f'%{q}%'

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        rows = db.session.execute(
            text(f'SELECT {_USER_COLS} FROM public.users {where} ORDER BY created_at DESC'),
            params
        ).fetchall()

        users = [_row_to_user(r) for r in rows]

        page  = max(int(request.args.get('page', 1)), 1)
        limit = min(int(request.args.get('limit', 20)), 100)
        total = len(users)
        users = users[(page - 1) * limit: page * limit]

        return jsonify({'success': True, 'data': users,
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
    """Admin tạo tài khoản mới."""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        required = ['cccdNumber', 'fullName', 'password']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Thiếu trường: {field}'}), 400

        data['id'] = str(uuid.uuid4())
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
    """Admin cập nhật thông tin / đổi role người dùng."""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
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
    """Admin xóa tài khoản khỏi PostgreSQL."""
    err = _require_admin()
    if err:
        return err
    try:
        if user_id == request.user_id:
            return jsonify({'success': False, 'message': 'Không thể xóa tài khoản đang dùng'}), 400

        result = db.session.execute(
            text('DELETE FROM public.users WHERE id = :id'),
            {'id': user_id}
        )
        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        db.session.commit()
        return jsonify({'success': True, 'message': 'Đã xóa tài khoản'})
    except Exception as e:
        db.session.rollback()
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<user_id>/reset-password', methods=['POST'])
def reset_password(user_id: str):
    """Admin đặt lại mật khẩu trong PostgreSQL."""
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        new_password = data.get('newPassword', '').strip()
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Mật khẩu tối thiểu 6 ký tự'}), 400

        hashed = generate_password_hash(new_password, method='pbkdf2:sha256')
        result = db.session.execute(
            text('UPDATE public.users SET password = :pw, updated_at = now() WHERE id = :id'),
            {'pw': hashed, 'id': user_id}
        )
        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
        db.session.commit()
        return jsonify({'success': True, 'message': 'Đã đặt lại mật khẩu'})
    except Exception as e:
        db.session.rollback()
        log.error(f'admin_routes error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 3. ĐỊA ĐIỂM — CRUD (file-based — Location model dùng locations.json)
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
# 4. THỦ TỤC HÀNH CHÍNH — CRUD (PostgreSQL — procedures table)
# ════════════════════════════════════════════════════════════════════════════════

import json as _json

def _proc_row(r) -> dict:
    return {
        'id':               r[0], 'name':              r[1],
        'code':             r[2] or '', 'category':    r[3] or '',
        'fee':              r[4] or 0,  'feeNote':     r[5] or '',
        'processingDays':   r[6] or 0,  'processingNote': r[7] or '',
        'legalBasis':       r[8] or [], 'implementingLevel': r[9] or 'ward',
        'agency':           r[10] or '', 'isOnline':   bool(r[11]),
        'isActive':         bool(r[12]),
    }


@admin_bp.route('/procedures', methods=['GET'])
def list_procedures():
    err = _require_admin()
    if err:
        return err
    try:
        category = (request.args.get('category') or '').strip()
        q        = (request.args.get('q') or '').strip().lower()
        page     = max(int(request.args.get('page', 1)), 1)
        limit    = min(int(request.args.get('limit', 20)), 100)

        conds, params = [], {}
        if category:
            conds.append('category = :cat')
            params['cat'] = category
        if q:
            conds.append("(LOWER(name) LIKE :q OR code LIKE :q)")
            params['q'] = f'%{q}%'
        where = ('WHERE ' + ' AND '.join(conds)) if conds else ''

        total = db.session.execute(
            text(f'SELECT COUNT(*) FROM public.procedures {where}'), params
        ).scalar() or 0

        rows = db.session.execute(text(f'''
            SELECT id, name, code, category, fee, fee_note, processing_days,
                   processing_note, legal_basis, implementing_level, agency, is_online, is_active
            FROM public.procedures {where}
            ORDER BY category, name
            LIMIT :limit OFFSET :offset
        '''), {**params, 'limit': limit, 'offset': (page-1)*limit}).fetchall()

        return jsonify({'success': True, 'data': [_proc_row(r) for r in rows],
                        'pagination': {'page': page, 'limit': limit, 'total': total}})
    except Exception as e:
        log.error(f'list_procedures error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['GET'])
def get_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        row = db.session.execute(
            text('SELECT id, name, code, category, fee, fee_note, processing_days, '
                 'processing_note, legal_basis, implementing_level, agency, is_online, is_active '
                 'FROM public.procedures WHERE id = :id'),
            {'id': proc_id}
        ).fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Thủ tục không tồn tại'}), 404
        return jsonify({'success': True, 'data': _proc_row(row)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures', methods=['POST'])
def create_procedure():
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Thiếu tên thủ tục'}), 400
        proc_id = data.get('id') or str(uuid.uuid4())
        db.session.execute(text('''
            INSERT INTO public.procedures
                (id, name, code, category, fee, fee_note, processing_days,
                 processing_note, legal_basis, implementing_level, agency)
            VALUES (:id, :name, :code, :cat, :fee, :fn, :days, :dn, :legal::jsonb, :level, :agency)
        '''), {
            'id':     proc_id, 'name':  data.get('name', ''),
            'code':   data.get('code', ''), 'cat': data.get('category', ''),
            'fee':    int(data.get('fee', 0)), 'fn': data.get('feeNote', ''),
            'days':   int(data.get('processingDays', 0)), 'dn': data.get('processingNote', ''),
            'legal':  _json.dumps(data.get('legalBasis', []), ensure_ascii=False),
            'level':  data.get('implementingLevel', 'ward'),
            'agency': data.get('agency', ''),
        })
        db.session.commit()
        _write_audit('create', 'procedure', proc_id, {'name': data.get('name')})
        return jsonify({'success': True, 'data': {'id': proc_id}}), 201
    except Exception as e:
        db.session.rollback()
        log.error(f'create_procedure error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['PUT'])
def update_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        data = request.get_json() or {}
        sets, params = [], {'id': proc_id}
        field_map = {
            'name': 'name', 'code': 'code', 'category': 'category',
            'fee': 'fee', 'feeNote': 'fee_note',
            'processingDays': 'processing_days', 'processingNote': 'processing_note',
            'implementingLevel': 'implementing_level', 'agency': 'agency',
            'isOnline': 'is_online', 'isActive': 'is_active',
        }
        for camel, snake in field_map.items():
            if camel in data:
                sets.append(f'{snake} = :{snake}')
                params[snake] = data[camel]
        if 'legalBasis' in data:
            sets.append('legal_basis = :legal::jsonb')
            params['legal'] = _json.dumps(data['legalBasis'], ensure_ascii=False)

        if not sets:
            return jsonify({'success': False, 'message': 'Không có trường nào để cập nhật'}), 400

        sets.append('updated_at = now()')
        result = db.session.execute(
            text(f"UPDATE public.procedures SET {', '.join(sets)} WHERE id = :id"),
            params
        )
        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        db.session.commit()
        _write_audit('update', 'procedure', proc_id, {'fields': list(field_map.keys())})
        return jsonify({'success': True, 'message': 'Đã cập nhật thủ tục'})
    except Exception as e:
        db.session.rollback()
        log.error(f'update_procedure error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/procedures/<proc_id>', methods=['DELETE'])
def delete_procedure(proc_id: str):
    err = _require_admin()
    if err:
        return err
    try:
        result = db.session.execute(
            text("UPDATE public.procedures SET is_active = FALSE, updated_at = now() WHERE id = :id"),
            {'id': proc_id}
        )
        if result.rowcount == 0:
            return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
        db.session.commit()
        _write_audit('deactivate', 'procedure', proc_id, {})
        return jsonify({'success': True, 'message': 'Đã vô hiệu hóa thủ tục'})
    except Exception as e:
        db.session.rollback()
        log.error(f'delete_procedure error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# 5. THỐNG KÊ TỔNG QUAN (PostgreSQL cho users/applications/tickets)
# ════════════════════════════════════════════════════════════════════════════════

# Nhãn tiếng Việt cho các nhóm thủ tục (procedures.category)
_CATEGORY_LABELS = {
    'civil':        'Hộ tịch & Tư pháp',
    'justice':      'Tư pháp & Công chứng',
    'land':         'Đất đai & Nhà ở',
    'construction': 'Xây dựng',
    'business':     'Doanh nghiệp & Đầu tư',
    'transport':    'Giao thông vận tải',
    'insurance':    'Bảo hiểm & Lao động',
    'other':        'Khác',
}

# Các trạng thái coi là "đang xử lý" (pending)
_PENDING_STATUSES = ('submitted', 'in_review', 'processing', 'more_info', 'need_info')


@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    err = _require_admin()
    if err:
        return err
    try:
        # ── Tham số filter (mặc định 14 ngày gần nhất) ──────────────────────
        try:
            days = max(1, min(int(request.args.get('days', 14)), 90))
        except (TypeError, ValueError):
            days = 14

        # ── Đếm tổng quan ───────────────────────────────────────────────────
        total_users = db.session.execute(
            text('SELECT COUNT(*) FROM public.users')
        ).scalar() or 0

        total_apps = db.session.execute(
            text('SELECT COUNT(*) FROM public.applications')
        ).scalar() or 0

        # ── Phân loại hồ sơ theo trạng thái (1 truy vấn) ────────────────────
        status_rows = db.session.execute(
            text('SELECT status, COUNT(*) FROM public.applications GROUP BY status')
        ).fetchall()
        status_breakdown = {(r[0] or 'unknown'): int(r[1]) for r in status_rows}

        approved_apps = status_breakdown.get('approved', 0)
        rejected_apps = status_breakdown.get('rejected', 0)
        pending_apps  = sum(status_breakdown.get(s, 0) for s in _PENDING_STATUSES)

        tickets_today = db.session.execute(
            text("SELECT COUNT(*) FROM public.queue_tickets WHERE date = CURRENT_DATE")
        ).scalar() or 0

        waiting_today = db.session.execute(
            text("SELECT COUNT(*) FROM public.queue_tickets WHERE date = CURRENT_DATE AND status = 'waiting'")
        ).scalar() or 0

        # ── Thời gian xử lý trung bình (ngày) ───────────────────────────────
        # Khoảng cách giữa lần 'submitted' đầu tiên và lần kết thúc
        # (approved/rejected) đầu tiên của mỗi hồ sơ — dựa trên lịch sử trạng thái.
        avg_processing_days = db.session.execute(text('''
            WITH spans AS (
                SELECT application_id,
                       MIN(created_at) FILTER (WHERE status = 'submitted')               AS started,
                       MIN(created_at) FILTER (WHERE status IN ('approved','rejected'))  AS finished
                FROM public.application_status_history
                GROUP BY application_id
            )
            SELECT AVG(EXTRACT(EPOCH FROM (finished - started)) / 86400.0)
            FROM spans
            WHERE started IS NOT NULL AND finished IS NOT NULL AND finished >= started
        ''')).scalar()
        avg_processing_days = round(float(avg_processing_days), 1) if avg_processing_days is not None else None

        # ── Chuỗi thời gian: hồ sơ + lịch hẹn theo ngày ─────────────────────
        ts_rows = db.session.execute(text('''
            SELECT d::date AS day,
                   COALESCE(a.cnt, 0) AS apps,
                   COALESCE(ap.cnt, 0) AS appts
            FROM generate_series(CURRENT_DATE - (:days - 1) * INTERVAL '1 day',
                                 CURRENT_DATE, INTERVAL '1 day') AS d
            LEFT JOIN (
                SELECT created_at::date AS day, COUNT(*) AS cnt
                FROM public.applications
                WHERE created_at >= CURRENT_DATE - (:days - 1) * INTERVAL '1 day'
                GROUP BY 1
            ) a ON a.day = d::date
            LEFT JOIN (
                SELECT date AS day, COUNT(*) AS cnt
                FROM public.appointments
                WHERE date >= CURRENT_DATE - (:days - 1) * INTERVAL '1 day'
                GROUP BY 1
            ) ap ON ap.day = d::date
            ORDER BY day
        '''), {'days': days}).fetchall()
        timeseries = [{
            'date':         r[0].isoformat() if r[0] else None,
            'applications': int(r[1]),
            'appointments': int(r[2]),
        } for r in ts_rows]

        # ── Top 5 thủ tục được nộp nhiều nhất ───────────────────────────────
        top_rows = db.session.execute(text('''
            SELECT p.id, p.name, COUNT(a.id) AS cnt
            FROM public.applications a
            JOIN public.procedures p ON a.service_id = p.id
            GROUP BY p.id, p.name
            ORDER BY cnt DESC
            LIMIT 5
        ''')).fetchall()
        top_procedures = [{'id': r[0], 'name': r[1], 'count': int(r[2])} for r in top_rows]

        # ── Cơ cấu hồ sơ theo lĩnh vực (procedures.category) ────────────────
        cat_rows = db.session.execute(text('''
            SELECT COALESCE(p.category, 'other') AS cat, COUNT(a.id) AS cnt
            FROM public.applications a
            JOIN public.procedures p ON a.service_id = p.id
            GROUP BY COALESCE(p.category, 'other')
            ORDER BY cnt DESC
        ''')).fetchall()
        cat_total = sum(int(r[1]) for r in cat_rows) or 0
        category_breakdown = [{
            'key':   r[0],
            'label': _CATEGORY_LABELS.get(r[0], r[0]),
            'count': int(r[1]),
            'pct':   round(int(r[1]) / cat_total * 100, 1) if cat_total else 0,
        } for r in cat_rows]

        # Locations vẫn đọc từ file; Procedures đọc từ PostgreSQL
        locs = FileStorage.read_json('locations.json')

        total_procedures = db.session.execute(
            text('SELECT COUNT(*) FROM public.procedures WHERE is_active = TRUE')
        ).scalar() or 0

        return jsonify({'success': True, 'data': {
            'totalUsers':           int(total_users),
            'totalLocations':       len(locs),
            'totalProcedures':      int(total_procedures),
            'totalApplications':    int(total_apps),
            'pendingApplications':  int(pending_apps),
            'approvedApplications': int(approved_apps),
            'rejectedApplications': int(rejected_apps),
            'statusBreakdown':      status_breakdown,
            'avgProcessingDays':    avg_processing_days,
            'ticketsToday':         int(tickets_today),
            'waitingToday':         int(waiting_today),
            'timeseries':           timeseries,
            'topProcedures':        top_procedures,
            'categoryBreakdown':    category_breakdown,
        }})
    except Exception as e:
        log.error(f'admin_stats error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/audit-logs', methods=['GET'])
def audit_logs():
    """Xem lịch sử thao tác admin — chỉ admin được xem."""
    err = _require_admin()
    if err:
        return err
    try:
        page     = max(int(request.args.get('page', 1)), 1)
        limit    = min(int(request.args.get('limit', 50)), 200)
        resource = (request.args.get('resource') or '').strip()
        actor    = (request.args.get('actorId') or '').strip()

        conditions, params = [], {}
        if resource:
            conditions.append('resource = :resource')
            params['resource'] = resource
        if actor:
            conditions.append('actor_id = :actor')
            params['actor'] = actor
        where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

        total = db.session.execute(
            text(f'SELECT COUNT(*) FROM public.audit_logs {where}'), params
        ).scalar() or 0

        rows = db.session.execute(text(f'''
            SELECT id, actor_id, actor_role, action, resource, resource_id,
                   detail, ip, created_at
            FROM public.audit_logs {where}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        '''), {**params, 'limit': limit, 'offset': (page - 1) * limit}).fetchall()

        data = [{
            'id': r[0], 'actorId': r[1], 'actorRole': r[2], 'action': r[3],
            'resource': r[4], 'resourceId': r[5], 'detail': r[6],
            'ip': r[7], 'createdAt': r[8].isoformat() if r[8] else None,
        } for r in rows]

        return jsonify({'success': True, 'data': data,
                        'pagination': {'page': page, 'limit': limit, 'total': total}})
    except Exception as e:
        log.error(f'audit_logs error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# SYSTEM SETTINGS
# ════════════════════════════════════════════════════════════════════════════════

def _parse_value(raw: str, typ: str):
    """Chuyển string → Python type theo type hint."""
    if typ == 'bool':
        return raw.lower() in ('true', '1', 'yes')
    if typ == 'number':
        try:    return float(raw)
        except: return 0
    if typ == 'json':
        import json as _json
        try:    return _json.loads(raw)
        except: return {}
    return raw  # string (mặc định)


@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Lấy tất cả cài đặt hệ thống dưới dạng key → {value, type, label, description}."""
    err = _require_admin()
    if err:
        return err
    try:
        rows = db.session.execute(
            text('SELECT key, value, type, label, description, updated_at '
                 'FROM public.system_settings ORDER BY key')
        ).fetchall()
        data = {
            r[0]: {
                'value':       _parse_value(r[1], r[2]),
                'rawValue':    r[1],
                'type':        r[2],
                'label':       r[3],
                'description': r[4],
                'updatedAt':   r[5].isoformat() if r[5] else None,
            }
            for r in rows
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        log.error(f'get_settings error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Cập nhật nhiều cài đặt cùng lúc. Body: { settings: { key: value, ... } }."""
    err = _require_admin()
    if err:
        return err
    try:
        payload  = request.get_json(silent=True) or {}
        updates  = payload.get('settings') or {}
        actor_id = getattr(request, 'user_id', None)

        if not updates:
            return jsonify({'success': False, 'message': 'Không có dữ liệu cập nhật'}), 400

        for key, val in updates.items():
            raw = str(val).lower() if isinstance(val, bool) else str(val)
            db.session.execute(
                text('''UPDATE public.system_settings
                        SET value = :val, updated_by = :actor, updated_at = now()
                        WHERE key = :key'''),
                {'val': raw, 'actor': actor_id, 'key': key}
            )
        db.session.commit()
        _write_audit('UPDATE', 'system_settings', detail={'keys': list(updates.keys())})
        return jsonify({'success': True, 'message': f'Đã cập nhật {len(updates)} cài đặt'})
    except Exception as e:
        db.session.rollback()
        log.error(f'update_settings error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/settings/<key>', methods=['PUT'])
def update_single_setting(key: str):
    """Cập nhật một cài đặt. Body: { value: ... }."""
    err = _require_admin()
    if err:
        return err
    try:
        payload  = request.get_json(silent=True) or {}
        val      = payload.get('value')
        actor_id = getattr(request, 'user_id', None)

        if val is None:
            return jsonify({'success': False, 'message': 'Thiếu value'}), 400

        raw = str(val).lower() if isinstance(val, bool) else str(val)
        result = db.session.execute(
            text('''UPDATE public.system_settings
                    SET value = :val, updated_by = :actor, updated_at = now()
                    WHERE key = :key
                    RETURNING key, value, type, label'''),
            {'val': raw, 'actor': actor_id, 'key': key}
        ).fetchone()
        db.session.commit()

        if not result:
            return jsonify({'success': False, 'message': f'Không tìm thấy setting: {key}'}), 404

        _write_audit('UPDATE', 'system_settings', resource_id=key, detail={'value': raw})
        return jsonify({'success': True, 'data': {
            'key':   result[0],
            'value': _parse_value(result[1], result[2]),
            'label': result[3],
        }})
    except Exception as e:
        db.session.rollback()
        log.error(f'update_single_setting error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════════
# EVALUATIONS — Admin quản lý đánh giá + phản hồi
# ════════════════════════════════════════════════════════════════════════════════

@admin_bp.route('/evaluations', methods=['GET'])
def admin_list_evaluations():
    """Danh sách tất cả đánh giá (phân trang, lọc theo minRating, sort)."""
    err = _require_admin()
    if err:
        return err
    try:
        page       = max(int(request.args.get('page', 1)), 1)
        limit      = min(int(request.args.get('limit', 10)), 100)
        min_rating = request.args.get('minRating', '')
        sort_dir   = 'DESC' if request.args.get('sort', 'newest') != 'oldest' else 'ASC'

        conditions, params = [], {}
        if min_rating:
            try:
                conditions.append('e.avg_rating >= :min_r')
                params['min_r'] = float(min_rating)
            except ValueError:
                pass

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

        count_row = db.session.execute(
            text(f'SELECT COUNT(*) FROM public.evaluations e {where}'),
            params,
        ).scalar() or 0

        rows = db.session.execute(
            text(f'''
                SELECT e.id, e.application_id, e.user_id, e.service_name,
                       e.attitude_rating, e.time_rating, e.facilities_rating,
                       e.avg_rating, e.comment, e.submitted_at,
                       e.admin_reply, e.admin_replied_at,
                       u.full_name AS user_name,
                       a.id        AS app_code
                FROM   public.evaluations e
                LEFT JOIN public.users       u ON u.id = e.user_id
                LEFT JOIN public.applications a ON a.id = e.application_id
                {where}
                ORDER BY e.submitted_at {sort_dir}
                LIMIT  :lim OFFSET :off
            '''),
            {**params, 'lim': limit, 'off': (page - 1) * limit},
        ).fetchall()

        data = []
        for r in rows:
            data.append({
                'id':               r.id,
                'applicationId':    r.application_id,
                'applicationCode':  ('#' + r.app_code[:8].upper()) if r.app_code else None,
                'userId':           r.user_id,
                'userName':         r.user_name or 'Khách vãng lai',
                'serviceName':      r.service_name or '',
                'attitudeRating':   r.attitude_rating,
                'timeRating':       r.time_rating,
                'facilitiesRating': r.facilities_rating,
                'avgRating':        round(float(r.avg_rating), 1),
                'comment':          r.comment or '',
                'submittedAt':      r.submitted_at.isoformat() if r.submitted_at else None,
                'adminReply':       r.admin_reply,
                'adminRepliedAt':   r.admin_replied_at.isoformat() if r.admin_replied_at else None,
            })

        return jsonify({
            'success': True,
            'data': data,
            'pagination': {'total': count_row, 'page': page, 'limit': limit},
        })
    except Exception as e:
        log.error(f'admin_list_evaluations: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/evaluations/<eval_id>/reply', methods=['POST'])
def admin_reply_evaluation(eval_id: str):
    """Thêm / cập nhật phản hồi admin cho một đánh giá.
    Body: { replyText: str }
    """
    err = _require_admin()
    if err:
        return err
    try:
        payload    = request.get_json(silent=True) or {}
        reply_text = (payload.get('replyText') or '').strip()[:2000]
        admin_id   = getattr(request, 'user_id', None)

        if not reply_text:
            return jsonify({'success': False, 'message': 'replyText không được trống'}), 400

        result = db.session.execute(
            text('''
                UPDATE public.evaluations
                SET    admin_reply       = :reply,
                       admin_replied_at  = now(),
                       admin_id          = :admin_id
                WHERE  id = :id
                RETURNING id
            '''),
            {'reply': reply_text, 'admin_id': admin_id, 'id': eval_id},
        ).fetchone()

        if not result:
            return jsonify({'success': False, 'message': 'Không tìm thấy đánh giá'}), 404

        db.session.commit()
        _write_audit('REPLY', 'evaluation', eval_id, {'length': len(reply_text)})

        return jsonify({'success': True, 'message': 'Đã lưu phản hồi', 'data': {'id': eval_id}})
    except Exception as e:
        db.session.rollback()
        log.error(f'admin_reply_evaluation: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/settings/public', methods=['GET'])
def get_public_settings():
    """Trả về các setting dành cho người dùng thường (không cần auth).
    Chỉ export: announcementActive, announcementText, announcementType, appName,
                enableChatbot, enableQueue, maintenanceMode
    """
    PUBLIC_KEYS = {
        'announcementActive', 'announcementText', 'announcementType',
        'appName', 'enableChatbot', 'enableQueue', 'maintenanceMode',
        'contactPhone', 'contactEmail',
    }
    try:
        rows = db.session.execute(
            text("SELECT key, value, type FROM public.system_settings WHERE key = ANY(:keys)"),
            {'keys': list(PUBLIC_KEYS)}
        ).fetchall()
        data = {r[0]: _parse_value(r[1], r[2]) for r in rows}
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
