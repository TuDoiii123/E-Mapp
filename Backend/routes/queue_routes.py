"""
Queue Routes — REST API + WebSocket realtime

REST:
  POST   /api/queue/ticket               Lấy số thứ tự (auth hoặc guest)
  GET    /api/queue/status/<ticket_id>   Trạng thái vé
  GET    /api/queue/my                   Vé của tôi hôm nay (auth)
  DELETE /api/queue/ticket/<id>          Hủy vé
  GET    /api/queue/summary/<agency_id>  Tóm tắt hàng chờ (public)
  GET    /api/queue/list/<agency_id>     Danh sách vé (admin)
  POST   /api/queue/call-next            Gọi vé tiếp theo (staff/admin)
  PUT    /api/queue/ticket/<id>/status   Cập nhật trạng thái (staff/admin)
  GET    /api/queue/counters/<agency_id> Danh sách quầy
  POST   /api/queue/counters             Tạo/cập nhật quầy (staff/admin)
  GET    /api/queue/map-overview         Snapshot tất cả cơ quan cho map (public)

WebSocket:
  WS /ws/queue/<agency_id>              Realtime stream hàng chờ
"""
import json
import time
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify

from models.queue import (
    QueueTicket, AgencyCounter, QueueService, ServiceStats,
    STATUS_WAITING, STATUS_CALLED, STATUS_SERVING,
    STATUS_DONE, STATUS_ABSENT, STATUS_CANCELLED,
    ACTIVE_STATUSES, _today,
)
from logger import get_logger

log = get_logger('queue_routes')
queue_bp = Blueprint('queue', __name__, url_prefix='/api/queue')

# ── WebSocket subscriber registry ────────────────────────────────────────────
_subscribers: dict[str, list] = {}
_sub_lock = threading.Lock()


def _broadcast(agency_id: str, payload: dict):
    msg  = json.dumps(payload, ensure_ascii=False)
    with _sub_lock:
        conns = list(_subscribers.get(agency_id, []))
    dead = []
    for ws in conns:
        try:
            ws.send(msg)
        except Exception:
            dead.append(ws)
    if dead:
        with _sub_lock:
            bucket = _subscribers.get(agency_id, [])
            for ws in dead:
                try: bucket.remove(ws)
                except ValueError: pass


def _push_summary(agency_id: str):
    try:
        summary = QueueService.queue_summary(agency_id)
        _broadcast(agency_id, {'type': 'summary', 'data': summary})
        QueueService.sync_to_postgres(agency_id, summary)
    except Exception as e:
        log.error(f'[Queue WS] push_summary error: {e}')


# ── WebSocket handler ─────────────────────────────────────────────────────────

def register_websocket(sock_app):
    @sock_app.route('/ws/queue/<agency_id>')
    def ws_queue(ws, agency_id: str):
        try:
            summary = QueueService.queue_summary(agency_id)
            ws.send(json.dumps({'type': 'snapshot', 'data': summary}, ensure_ascii=False))
        except Exception:
            pass

        with _sub_lock:
            _subscribers.setdefault(agency_id, []).append(ws)

        try:
            while True:
                try:
                    msg = ws.receive(timeout=15)
                    if msg is None:
                        break
                    data = json.loads(msg)
                    if data.get('type') == 'ping':
                        ws.send(json.dumps({'type': 'pong', 'ts': time.time()}))
                    elif data.get('type') == 'subscribe':
                        summary = QueueService.queue_summary(agency_id)
                        ws.send(json.dumps({'type': 'snapshot', 'data': summary}, ensure_ascii=False))
                except Exception:
                    try:
                        ws.send(json.dumps({'type': 'ping', 'ts': time.time()}))
                    except Exception:
                        break
        finally:
            with _sub_lock:
                bucket = _subscribers.get(agency_id, [])
                try: bucket.remove(ws)
                except ValueError: pass


# ── Helper ────────────────────────────────────────────────────────────────────

def _ok(data, code=200):
    return jsonify({'success': True, 'data': data}), code

def _err(msg: str, code=400):
    return jsonify({'success': False, 'message': msg}), code

def _current_user():
    uid  = getattr(request, 'user_id', None)
    role = getattr(request, 'role', None)
    if not uid:
        from flask import g
        uid  = getattr(g, 'user_id', None)
        role = getattr(g, 'role', None)
    return uid, role


# ── REST: Lấy số thứ tự ──────────────────────────────────────────────────────

@queue_bp.route('/ticket', methods=['POST'])
def take_ticket():
    """
    Lấy số thứ tự.
    - Nếu đã đăng nhập: gắn userId, kiểm tra trùng vé.
    - Nếu là khách (guest): vẫn cho lấy, userId = None.
    """
    user_id, _ = _current_user()

    data = request.get_json() or {}
    agency_id    = (data.get('agencyId') or '').strip()
    service_id   = (data.get('serviceId') or '').strip()
    service_name = data.get('serviceName', '')
    priority     = int(data.get('priority', 0))
    prefix       = (data.get('prefix') or 'A').upper()
    user_name    = data.get('userName', '')

    if not agency_id:
        return _err('Thiếu agencyId', 400)

    # Kiểm tra trùng vé (chỉ khi đăng nhập)
    if user_id:
        existing = QueueTicket.active_for_user(user_id, agency_id)
        if existing:
            return jsonify({
                'success': False,
                'message': 'Bạn đã có vé đang chờ tại cơ quan này',
                'data': existing,
            }), 409

    try:
        ticket = QueueTicket.create({
            'agencyId':    agency_id,
            'serviceId':   service_id,
            'serviceName': service_name,
            'userId':      user_id,
            'userName':    user_name,
            'priority':    priority,
            'prefix':      prefix,
        })
        threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()
        return _ok(ticket, 201)
    except Exception as e:
        log.error(f'take_ticket error: {e}', exc_info=True)
        return _err(str(e), 500)


# ── REST: Trạng thái vé ────────────────────────────────────────────────────────

@queue_bp.route('/status/<ticket_id>', methods=['GET'])
def ticket_status(ticket_id: str):
    ticket = QueueTicket.find_by_id(ticket_id)
    if not ticket:
        return _err('Vé không tồn tại', 404)
    if ticket.get('status') == STATUS_WAITING:
        ticket['estimatedWait'] = QueueService.estimate_wait(
            ticket['agencyId'], ticket.get('serviceId', ''),
            ticket.get('priority', 0), ticket.get('prefix', 'A')
        )
    return _ok(ticket)


# ── REST: Vé của tôi ──────────────────────────────────────────────────────────

@queue_bp.route('/my', methods=['GET'])
def my_tickets():
    user_id, _ = _current_user()
    if not user_id:
        return _err('Chưa đăng nhập', 401)
    date    = request.args.get('date', _today())
    tickets = QueueTicket.find_by_user(user_id, date)
    for t in tickets:
        if t.get('status') == STATUS_WAITING:
            t['estimatedWait'] = QueueService.estimate_wait(
                t['agencyId'], t.get('serviceId', ''),
                t.get('priority', 0), t.get('prefix', 'A')
            )
    return _ok(tickets)


# ── REST: Hủy vé ──────────────────────────────────────────────────────────────

@queue_bp.route('/ticket/<ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id: str):
    user_id, role = _current_user()
    ticket = QueueTicket.find_by_id(ticket_id)
    if not ticket:
        return _err('Vé không tồn tại', 404)

    # Cho phép hủy nếu: chủ vé hoặc admin
    if ticket.get('userId') and ticket.get('userId') != user_id and role != 'admin':
        return _err('Không có quyền hủy vé này', 403)
    if ticket.get('status') not in (STATUS_WAITING,):
        return _err('Không thể hủy vé ở trạng thái này', 400)

    updated = QueueTicket.update(ticket_id, {'status': STATUS_CANCELLED})
    threading.Thread(target=_push_summary, args=(ticket['agencyId'],), daemon=True).start()
    return _ok(updated)


# ── REST: Tóm tắt (public) ────────────────────────────────────────────────────

@queue_bp.route('/summary/<agency_id>', methods=['GET'])
def queue_summary(agency_id: str):
    summary = QueueService.queue_summary(agency_id)
    return _ok(summary)


# ── REST: Danh sách vé (admin) ────────────────────────────────────────────────

@queue_bp.route('/list/<agency_id>', methods=['GET'])
def queue_list(agency_id: str):
    _, role = _current_user()
    if role != 'admin':
        return _err('Cần quyền admin', 403)
    date   = request.args.get('date', _today())
    status = request.args.get('status')
    tickets = QueueTicket.find_all(agency_id=agency_id, date=date, status=status)
    return jsonify({'success': True, 'data': tickets, 'total': len(tickets)})


# ── REST: Quầy gọi số ────────────────────────────────────────────────────────

@queue_bp.route('/call-next', methods=['POST'])
def call_next():
    _, role = _current_user()
    if role not in ('admin', 'staff'):
        return _err('Cần quyền nhân viên', 403)
    data       = request.get_json() or {}
    agency_id  = (data.get('agencyId') or '').strip()
    counter_no = int(data.get('counterNo', 1))
    service_id = data.get('serviceId')
    if not agency_id:
        return _err('Thiếu agencyId', 400)
    ticket = QueueTicket.call_next(agency_id, counter_no, service_id)
    if not ticket:
        return jsonify({'success': True, 'data': None, 'message': 'Không còn vé chờ'})
    threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()
    return _ok(ticket)


# ── REST: Cập nhật trạng thái vé (quầy) ──────────────────────────────────────

@queue_bp.route('/ticket/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id: str):
    _, role = _current_user()
    if role not in ('admin', 'staff'):
        return _err('Cần quyền nhân viên', 403)
    data       = request.get_json() or {}
    new_status = (data.get('status') or '').strip()
    allowed    = {STATUS_SERVING, STATUS_DONE, STATUS_ABSENT, STATUS_CANCELLED}
    if new_status not in allowed:
        return _err(f'Trạng thái không hợp lệ. Dùng: {allowed}', 400)

    ticket = QueueTicket.find_by_id(ticket_id)
    if not ticket:
        return _err('Vé không tồn tại', 404)

    updates: dict = {'status': new_status}
    if new_status == STATUS_SERVING and not ticket.get('servedAt'):
        updates['servedAt'] = datetime.now().isoformat()
    elif new_status == STATUS_DONE:
        if not ticket.get('doneAt'):
            updates['doneAt'] = datetime.now().isoformat()
        if ticket.get('servedAt'):
            try:
                s    = datetime.fromisoformat(ticket['servedAt'])
                secs = (datetime.now() - s).total_seconds()
                if secs > 0:
                    threading.Thread(
                        target=ServiceStats.record_service_time,
                        args=(ticket['agencyId'], ticket.get('serviceId', ''), secs),
                        daemon=True,
                    ).start()
            except Exception:
                pass

    updated = QueueTicket.update(ticket_id, updates)
    threading.Thread(target=_push_summary, args=(ticket['agencyId'],), daemon=True).start()
    return _ok(updated)


# ── REST: Quản lý quầy ────────────────────────────────────────────────────────

@queue_bp.route('/counters/<agency_id>', methods=['GET'])
def get_counters(agency_id: str):
    return _ok(AgencyCounter.find_by_agency(agency_id))


@queue_bp.route('/counters', methods=['POST'])
def upsert_counter():
    _, role = _current_user()
    if role not in ('admin', 'staff'):
        return _err('Cần quyền nhân viên', 403)
    data          = request.get_json() or {}
    agency_id     = (data.get('agencyId') or '').strip()
    counter_no    = int(data.get('counterNo', 1))
    is_active     = bool(data.get('isActive', True))
    operator_name = data.get('operatorName', '')
    if not agency_id:
        return _err('Thiếu agencyId', 400)
    counter = AgencyCounter.upsert(agency_id, counter_no, is_active, operator_name)
    threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()
    return _ok(counter, 201)


# ── REST: Map overview ────────────────────────────────────────────────────────

@queue_bp.route('/map-overview', methods=['GET'])
def map_overview():
    """
    Snapshot hàng chờ realtime của TẤT CẢ cơ quan trên bản đồ.
    - Đọc nhanh từ agency_queue_realtime (PostgreSQL) nếu có.
    - Bổ sung tất cả agencies từ PublicService (hiển thị 0 nếu chưa có queue).
    - Fallback scan JSON nếu DB không khả dụng.
    """
    try:
        from models.public_service import PublicService
        all_services = PublicService.find_all()
        # Tạo map agency_id → {totalWaiting: 0, ...} cho mọi cơ quan
        result: dict[str, dict] = {}
        for svc in all_services:
            aid = str(svc.get('id', ''))
            if not aid:
                continue
            result[aid] = {
                'agencyId':     aid,
                'totalWaiting': 0,
                'totalServing': 0,
                'loadLevel':    'low',
                'ageSeconds':   0,
            }
    except Exception:
        result = {}

    # Đọc snapshot nhanh từ PostgreSQL
    try:
        from models.db import db
        from sqlalchemy import text as sa_text
        rows = db.session.execute(sa_text("""
            SELECT agency_id, total_waiting, total_serving, load_level,
                   EXTRACT(EPOCH FROM (now() - updated_at))::int AS age_seconds
            FROM public.agency_queue_realtime
        """)).fetchall()
        for row in rows:
            result[row[0]] = {
                'agencyId':     row[0],
                'totalWaiting': row[1],
                'totalServing': row[2],
                'loadLevel':    row[3],
                'ageSeconds':   row[4],
            }
    except Exception:
        # Fallback: live scan từ JSON (chậm hơn, chỉ có agencies đang hoạt động)
        try:
            today    = _today()
            all_t    = QueueTicket._all_json() if hasattr(QueueTicket, '_all_json') else []
            agency_ids = {t.get('agencyId') for t in all_t if t.get('agencyId') and t.get('date') == today}
            for aid in agency_ids:
                summary = QueueService.queue_summary(aid)
                result[aid] = {
                    'agencyId':     aid,
                    'totalWaiting': summary['totalWaiting'],
                    'totalServing': summary['totalServing'] + summary['totalCalled'],
                    'loadLevel':    summary.get('loadLevel', 'low'),
                    'ageSeconds':   0,
                }
        except Exception as e:
            log.error(f'map_overview fallback error: {e}', exc_info=True)

    return jsonify({'success': True, 'data': result})
