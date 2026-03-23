"""
Queue Routes — REST API + WebSocket realtime

REST:
  POST   /api/queue/ticket              Lấy số thứ tự
  GET    /api/queue/status/<ticket_id>  Trạng thái vé
  GET    /api/queue/my                  Vé của tôi hôm nay
  DELETE /api/queue/ticket/<id>         Hủy vé
  GET    /api/queue/summary/<agency_id> Tóm tắt hàng chờ
  GET    /api/queue/list/<agency_id>    Danh sách vé (admin)
  POST   /api/queue/call-next           Gọi vé tiếp theo (quầy)
  PUT    /api/queue/ticket/<id>/status  Cập nhật trạng thái vé (quầy)
  GET    /api/queue/counters/<agency_id>Danh sách quầy
  POST   /api/queue/counters            Tạo/cập nhật quầy

WebSocket:
  WS  /ws/queue/<agency_id>            Stream realtime hàng chờ
"""
import json
import time
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify

from models.queue import (
    QueueTicket, AgencyCounter, QueueService,
    STATUS_WAITING, STATUS_CALLED, STATUS_SERVING,
    STATUS_DONE, STATUS_ABSENT, STATUS_CANCELLED,
)

queue_bp = Blueprint('queue', __name__, url_prefix='/api/queue')

# ── WebSocket subscriber registry ────────────────────────────────────────────
# { agency_id: [ws_connection, ...] }
_subscribers: dict[str, list] = {}
_sub_lock = threading.Lock()

def _broadcast(agency_id: str, payload: dict):
    """Gửi bản tin delta đến tất cả client đang subscribe agency này."""
    msg = json.dumps(payload, ensure_ascii=False)
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
                try:
                    bucket.remove(ws)
                except ValueError:
                    pass

def _push_summary(agency_id: str):
    """Tính summary mới, broadcast WebSocket, và sync snapshot lên PostgreSQL."""
    try:
        summary = QueueService.queue_summary(agency_id)
        _broadcast(agency_id, {'type': 'summary', 'data': summary})
        QueueService.sync_to_postgres(agency_id, summary)
    except Exception as e:
        print(f'[Queue WS] push_summary error: {e}')

# ── WebSocket endpoint ────────────────────────────────────────────────────────

def register_websocket(sock_app):
    """
    Gọi hàm này từ server.py sau khi khởi tạo Sock(app).
    Dùng flask-sock: `from flask_sock import Sock; sock = Sock(app)`
    """
    @sock_app.route('/ws/queue/<agency_id>')
    def ws_queue(ws, agency_id: str):
        """
        WebSocket handler — tối ưu độ trễ:
        - Gửi snapshot ngay khi kết nối
        - Heartbeat mỗi 15 giây (ping/pong) để phát hiện disconnect nhanh
        - Chỉ gửi delta khi có thay đổi (triggered by REST calls)
        - Binary-safe JSON (utf-8)
        """
        # Gửi snapshot ngay
        try:
            summary = QueueService.queue_summary(agency_id)
            ws.send(json.dumps({'type': 'snapshot', 'data': summary}, ensure_ascii=False))
        except Exception:
            pass

        # Đăng ký subscriber
        with _sub_lock:
            _subscribers.setdefault(agency_id, []).append(ws)

        try:
            while True:
                # Heartbeat: chờ message từ client (ping) hoặc timeout
                try:
                    msg = ws.receive(timeout=15)
                    if msg is None:
                        break  # Client đóng kết nối
                    data = json.loads(msg)
                    if data.get('type') == 'ping':
                        ws.send(json.dumps({'type': 'pong', 'ts': time.time()}))
                    elif data.get('type') == 'subscribe':
                        # Client yêu cầu snapshot lại
                        summary = QueueService.queue_summary(agency_id)
                        ws.send(json.dumps({'type': 'snapshot', 'data': summary}, ensure_ascii=False))
                except Exception:
                    # timeout hoặc lỗi đọc → gửi heartbeat từ server
                    try:
                        ws.send(json.dumps({'type': 'ping', 'ts': time.time()}))
                    except Exception:
                        break  # Kết nối chết
        finally:
            with _sub_lock:
                bucket = _subscribers.get(agency_id, [])
                try:
                    bucket.remove(ws)
                except ValueError:
                    pass

# ── REST: Lấy số thứ tự ──────────────────────────────────────────────────────

@queue_bp.route('/ticket', methods=['POST'])
def take_ticket():
    """Người dùng lấy số thứ tự"""
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({'success': False, 'message': 'Chưa đăng nhập'}), 401

        data = request.get_json() or {}
        agency_id    = data.get('agencyId', '').strip()
        service_id   = data.get('serviceId', '').strip()
        service_name = data.get('serviceName', '')
        priority     = int(data.get('priority', 0))
        prefix       = data.get('prefix', 'A').upper()
        user_name    = data.get('userName', '')

        if not agency_id:
            return jsonify({'success': False, 'message': 'Thiếu agencyId'}), 400

        # Kiểm tra đã có vé chờ chưa
        existing = [
            t for t in QueueTicket.find_by_user(user_id)
            if t.get('agencyId') == agency_id
            and t.get('status') in (STATUS_WAITING, STATUS_CALLED, STATUS_SERVING)
        ]
        if existing:
            return jsonify({
                'success': False,
                'message': 'Bạn đã có vé đang chờ tại cơ quan này',
                'data': existing[0]
            }), 409

        ticket = QueueTicket.create({
            'agencyId':    agency_id,
            'serviceId':   service_id,
            'serviceName': service_name,
            'userId':      user_id,
            'userName':    user_name,
            'priority':    priority,
            'prefix':      prefix,
        })

        # Broadcast cập nhật
        threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()

        return jsonify({'success': True, 'data': ticket}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@queue_bp.route('/status/<ticket_id>', methods=['GET'])
def ticket_status(ticket_id: str):
    """Trạng thái vé + thời gian chờ ước tính"""
    ticket = QueueTicket.find_by_id(ticket_id)
    if not ticket:
        return jsonify({'success': False, 'message': 'Vé không tồn tại'}), 404

    # Tính lại ước tính nếu vé còn chờ
    if ticket.get('status') == STATUS_WAITING:
        wait = QueueService.estimate_wait(
            ticket['agencyId'], ticket.get('serviceId', ''),
            ticket.get('priority', 0), ticket.get('prefix', 'A')
        )
        ticket['estimatedWait'] = wait

    return jsonify({'success': True, 'data': ticket})


@queue_bp.route('/my', methods=['GET'])
def my_tickets():
    """Vé của tôi hôm nay"""
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'}), 401

    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    tickets = QueueTicket.find_by_user(user_id, date)

    # Tính lại wait cho vé còn chờ
    for t in tickets:
        if t.get('status') == STATUS_WAITING:
            t['estimatedWait'] = QueueService.estimate_wait(
                t['agencyId'], t.get('serviceId', ''),
                t.get('priority', 0), t.get('prefix', 'A')
            )
    return jsonify({'success': True, 'data': tickets})


@queue_bp.route('/ticket/<ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id: str):
    """Hủy vé (chỉ khi đang WAITING)"""
    user_id = getattr(request, 'user_id', None)
    ticket  = QueueTicket.find_by_id(ticket_id)

    if not ticket:
        return jsonify({'success': False, 'message': 'Vé không tồn tại'}), 404
    if ticket.get('userId') != user_id and getattr(request, 'role', '') != 'admin':
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
    if ticket.get('status') not in (STATUS_WAITING,):
        return jsonify({'success': False, 'message': 'Không thể hủy vé ở trạng thái này'}), 400

    updated = QueueTicket.update(ticket_id, {'status': STATUS_CANCELLED})
    threading.Thread(target=_push_summary, args=(ticket['agencyId'],), daemon=True).start()
    return jsonify({'success': True, 'data': updated})


# ── REST: Tóm tắt + Danh sách (admin / bảng hiển thị) ──────────────────────

@queue_bp.route('/summary/<agency_id>', methods=['GET'])
def queue_summary(agency_id: str):
    """Tóm tắt hàng chờ — dùng cho bảng hiển thị công cộng"""
    summary = QueueService.queue_summary(agency_id)
    return jsonify({'success': True, 'data': summary})


@queue_bp.route('/list/<agency_id>', methods=['GET'])
def queue_list(agency_id: str):
    """Danh sách toàn bộ vé (admin)"""
    if getattr(request, 'role', '') != 'admin':
        return jsonify({'success': False, 'message': 'Cần quyền admin'}), 403

    date   = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    status = request.args.get('status', None)
    tickets = QueueTicket.find_all(agency_id=agency_id, date=date, status=status)
    return jsonify({'success': True, 'data': tickets, 'total': len(tickets)})


# ── REST: Quầy phục vụ ────────────────────────────────────────────────────────

@queue_bp.route('/call-next', methods=['POST'])
def call_next():
    """Quầy gọi vé tiếp theo"""
    if getattr(request, 'role', '') not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    data       = request.get_json() or {}
    agency_id  = data.get('agencyId', '').strip()
    counter_no = int(data.get('counterNo', 1))
    service_id = data.get('serviceId', None)

    if not agency_id:
        return jsonify({'success': False, 'message': 'Thiếu agencyId'}), 400

    ticket = QueueTicket.call_next(agency_id, counter_no, service_id)
    if not ticket:
        return jsonify({'success': True, 'data': None, 'message': 'Không còn vé chờ'})

    threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()
    return jsonify({'success': True, 'data': ticket})


@queue_bp.route('/ticket/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id: str):
    """Quầy cập nhật trạng thái vé (serving → done/absent)"""
    if getattr(request, 'role', '') not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    data       = request.get_json() or {}
    new_status = data.get('status', '').strip()

    allowed = {STATUS_SERVING, STATUS_DONE, STATUS_ABSENT, STATUS_CANCELLED}
    if new_status not in allowed:
        return jsonify({'success': False, 'message': f'Trạng thái không hợp lệ. Dùng: {allowed}'}), 400

    ticket = QueueTicket.find_by_id(ticket_id)
    if not ticket:
        return jsonify({'success': False, 'message': 'Vé không tồn tại'}), 404

    updates: dict = {'status': new_status}

    # Ghi thời gian thực tế
    if new_status == STATUS_SERVING and not ticket.get('servedAt'):
        updates['servedAt'] = datetime.now().isoformat()
    elif new_status == STATUS_DONE:
        if not ticket.get('doneAt'):
            updates['doneAt'] = datetime.now().isoformat()
        # Ghi nhận thời gian phục vụ thực tế cho thuật toán
        if ticket.get('servedAt'):
            try:
                s = datetime.fromisoformat(ticket['servedAt'])
                d = datetime.now()
                secs = (d - s).total_seconds()
                if secs > 0:
                    from models.queue import ServiceStats
                    ServiceStats.record_service_time(
                        ticket['agencyId'], ticket.get('serviceId', ''), secs
                    )
            except Exception:
                pass

    updated = QueueTicket.update(ticket_id, updates)
    threading.Thread(target=_push_summary, args=(ticket['agencyId'],), daemon=True).start()
    return jsonify({'success': True, 'data': updated})


# ── REST: Quản lý quầy ────────────────────────────────────────────────────────

@queue_bp.route('/counters/<agency_id>', methods=['GET'])
def get_counters(agency_id: str):
    counters = AgencyCounter.find_by_agency(agency_id)
    return jsonify({'success': True, 'data': counters})


@queue_bp.route('/counters', methods=['POST'])
def upsert_counter():
    if getattr(request, 'role', '') not in ('admin', 'staff'):
        return jsonify({'success': False, 'message': 'Cần quyền nhân viên'}), 403

    data          = request.get_json() or {}
    agency_id     = data.get('agencyId', '').strip()
    counter_no    = int(data.get('counterNo', 1))
    is_active     = bool(data.get('isActive', True))
    operator_name = data.get('operatorName', '')

    if not agency_id:
        return jsonify({'success': False, 'message': 'Thiếu agencyId'}), 400

    counter = AgencyCounter.upsert(agency_id, counter_no, is_active, operator_name)
    threading.Thread(target=_push_summary, args=(agency_id,), daemon=True).start()
    return jsonify({'success': True, 'data': counter})


# ── REST: Map overview (realtime snapshot cho Google Maps) ────────────────────

@queue_bp.route('/map-overview', methods=['GET'])
def map_overview():
    """
    Trả về snapshot hàng chờ realtime của TẤT CẢ cơ quan.
    Frontend dùng để tô màu marker trên Google Maps.
    Kết hợp dữ liệu từ PostgreSQL (nếu có) với live scan từ JSON storage.
    """
    try:
        from models.db import db
        from sqlalchemy import text as sa_text

        # Ưu tiên lấy từ PostgreSQL (snapshot mới nhất được ghi khi có activity)
        rows = db.session.execute(sa_text("""
            SELECT agency_id, total_waiting, total_serving, load_level,
                   EXTRACT(EPOCH FROM (now() - updated_at)) AS age_seconds
            FROM public.agency_queue_realtime
            ORDER BY updated_at DESC
        """)).fetchall()

        result = {}
        for row in rows:
            result[row[0]] = {
                'agencyId':     row[0],
                'totalWaiting': row[1],
                'totalServing': row[2],
                'loadLevel':    row[3],
                'ageSeconds':   int(row[4]),
            }

        return jsonify({'success': True, 'data': result})

    except Exception:
        # Fallback: scan live từ JSON file nếu DB không khả dụng
        try:
            all_tickets = QueueTicket._all()
            today = datetime.now().strftime('%Y-%m-%d')

            agency_ids = {t.get('agencyId') for t in all_tickets if t.get('agencyId')}
            result = {}
            for aid in agency_ids:
                summary = QueueService.queue_summary(aid)
                result[aid] = {
                    'agencyId':     aid,
                    'totalWaiting': summary['totalWaiting'],
                    'totalServing': summary['totalServing'] + summary['totalCalled'],
                    'loadLevel':    summary.get('loadLevel', 'low'),
                    'ageSeconds':   0,
                }
            return jsonify({'success': True, 'data': result})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
