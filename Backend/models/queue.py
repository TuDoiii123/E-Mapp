"""
Queue / Ticket model
Lưu trữ hàng chờ: ưu tiên PostgreSQL, fallback JSON file.
"""
import math
import uuid
from datetime import datetime
from models.user import FileStorage

try:
    from models.db import db
    from sqlalchemy import text
    HAS_DB = True
except Exception:
    db = None
    text = None
    HAS_DB = False

# ── Trạng thái vé ─────────────────────────────────────────────────────────────
STATUS_WAITING   = 'waiting'
STATUS_CALLED    = 'called'
STATUS_SERVING   = 'serving'
STATUS_DONE      = 'done'
STATUS_ABSENT    = 'absent'
STATUS_CANCELLED = 'cancelled'

ACTIVE_STATUSES = {STATUS_WAITING, STATUS_CALLED, STATUS_SERVING}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _today() -> str:
    return datetime.now().strftime('%Y-%m-%d')

def _now_iso() -> str:
    return datetime.now().isoformat()

def _use_db() -> bool:
    if not HAS_DB or db is None:
        return False
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception:
        return False

def _ticket_code(prefix: str, number: int) -> str:
    return f"{prefix}{number:03d}"

def _row_to_dict(row) -> dict:
    """Convert SQLAlchemy Row → camelCase dict cho frontend."""
    r = dict(row._mapping)
    return {
        'id':            r['id'],
        'agencyId':      r['agency_id'],
        'serviceId':     r['service_id'],
        'serviceName':   r['service_name'],
        'ticketNumber':  r['ticket_number'],
        'prefix':        r['prefix'],
        'ticketCode':    _ticket_code(r['prefix'], r['ticket_number']),
        'userId':        r.get('user_id'),
        'userName':      r.get('user_name', ''),
        'counterNo':     r.get('counter_no'),
        'status':        r['status'],
        'priority':      r.get('priority', 0),
        'estimatedWait': r.get('estimated_wait', 0),
        'calledAt':      r['called_at'].isoformat() if r.get('called_at') else None,
        'servedAt':      r['served_at'].isoformat() if r.get('served_at') else None,
        'doneAt':        r['done_at'].isoformat()   if r.get('done_at')   else None,
        'createdAt':     r['created_at'].isoformat() if r.get('created_at') else _now_iso(),
        'updatedAt':     r['updated_at'].isoformat() if r.get('updated_at') else _now_iso(),
        'date':          str(r.get('date', _today())),
    }


# ── QueueTicket ───────────────────────────────────────────────────────────────

class QueueTicket:

    # ── JSON fallback helpers ─────────────────────────────────────────────────

    @staticmethod
    def _all_json() -> list:
        return FileStorage.read_json('queue_tickets.json')

    @staticmethod
    def _save_json(tickets: list) -> None:
        FileStorage.write_json('queue_tickets.json', tickets)

    # ── next ticket number ────────────────────────────────────────────────────

    @staticmethod
    def _next_number_db(agency_id: str, prefix: str, date: str) -> int:
        row = db.session.execute(text("""
            SELECT COALESCE(MAX(ticket_number), 0) + 1
            FROM public.queue_tickets
            WHERE agency_id = :aid AND prefix = :pfx AND date = :dt
        """), {'aid': agency_id, 'pfx': prefix, 'dt': date}).fetchone()
        return int(row[0]) if row else 1

    @staticmethod
    def _next_number_json(agency_id: str, prefix: str, date: str) -> int:
        existing = [
            t for t in QueueTicket._all_json()
            if t.get('agencyId') == agency_id
            and t.get('prefix') == prefix
            and t.get('date') == date
        ]
        return (max(t.get('ticketNumber', 0) for t in existing) + 1) if existing else 1

    # ── create ────────────────────────────────────────────────────────────────

    @staticmethod
    def create(data: dict) -> dict:
        date    = data.get('date', _today())
        prefix  = (data.get('prefix') or 'A').upper()
        aid     = data['agencyId']
        sid     = data.get('serviceId', '')
        uid     = data.get('userId')

        if _use_db():
            num = QueueTicket._next_number_db(aid, prefix, date)
            tid = str(uuid.uuid4())
            wait = QueueService.estimate_wait(aid, sid, data.get('priority', 0), prefix)
            db.session.execute(text("""
                INSERT INTO public.queue_tickets
                    (id, agency_id, service_id, service_name, ticket_number, prefix,
                     user_id, user_name, status, priority, estimated_wait, date)
                VALUES
                    (:id, :aid, :sid, :sname, :num, :pfx,
                     :uid, :uname, 'waiting', :prio, :wait, :dt)
            """), {
                'id': tid, 'aid': aid, 'sid': sid,
                'sname': data.get('serviceName', ''),
                'num': num, 'pfx': prefix,
                'uid': uid, 'uname': data.get('userName', ''),
                'prio': data.get('priority', 0),
                'wait': wait, 'dt': date,
            })
            db.session.commit()
            row = db.session.execute(
                text("SELECT * FROM public.queue_tickets WHERE id = :id"), {'id': tid}
            ).fetchone()
            return _row_to_dict(row)

        # JSON fallback
        tickets = QueueTicket._all_json()
        num  = QueueTicket._next_number_json(aid, prefix, date)
        tid  = str(uuid.uuid4())
        wait = QueueService.estimate_wait(aid, sid, data.get('priority', 0), prefix)
        ticket = {
            'id': tid, 'agencyId': aid, 'serviceId': sid,
            'serviceName': data.get('serviceName', ''),
            'ticketNumber': num, 'prefix': prefix,
            'ticketCode': _ticket_code(prefix, num),
            'userId': uid, 'userName': data.get('userName', ''),
            'counterNo': None, 'status': STATUS_WAITING,
            'priority': data.get('priority', 0),
            'estimatedWait': wait,
            'calledAt': None, 'servedAt': None, 'doneAt': None,
            'createdAt': _now_iso(), 'updatedAt': _now_iso(), 'date': date,
        }
        tickets.append(ticket)
        QueueTicket._save_json(tickets)
        return ticket

    # ── find ──────────────────────────────────────────────────────────────────

    @staticmethod
    def find_by_id(ticket_id: str) -> dict | None:
        if _use_db():
            row = db.session.execute(
                text("SELECT * FROM public.queue_tickets WHERE id = :id"),
                {'id': ticket_id}
            ).fetchone()
            return _row_to_dict(row) if row else None
        for t in QueueTicket._all_json():
            if t.get('id') == ticket_id:
                return t
        return None

    @staticmethod
    def find_by_user(user_id: str, date: str = None) -> list:
        date = date or _today()
        if _use_db():
            rows = db.session.execute(text("""
                SELECT * FROM public.queue_tickets
                WHERE user_id = :uid AND date = :dt
                ORDER BY created_at DESC
            """), {'uid': user_id, 'dt': date}).fetchall()
            return [_row_to_dict(r) for r in rows]
        return [
            t for t in QueueTicket._all_json()
            if t.get('userId') == user_id and t.get('date') == date
        ]

    @staticmethod
    def find_all(agency_id: str = None, date: str = None, status: str = None) -> list:
        if _use_db():
            where, params = [], {}
            if agency_id: where.append('agency_id = :aid');  params['aid'] = agency_id
            if date:      where.append('date = :dt');        params['dt']  = date
            if status:    where.append('status = :st');      params['st']  = status
            clause = ('WHERE ' + ' AND '.join(where)) if where else ''
            rows = db.session.execute(text(f"""
                SELECT * FROM public.queue_tickets {clause}
                ORDER BY priority DESC, ticket_number ASC
            """), params).fetchall()
            return [_row_to_dict(r) for r in rows]

        tickets = QueueTicket._all_json()
        if agency_id: tickets = [t for t in tickets if t.get('agencyId') == agency_id]
        if date:      tickets = [t for t in tickets if t.get('date') == date]
        if status:    tickets = [t for t in tickets if t.get('status') == status]
        return sorted(tickets, key=lambda t: (-t.get('priority', 0), t.get('ticketNumber', 0)))

    @staticmethod
    def _all() -> list:
        """Dùng nội bộ bởi QueueService."""
        return QueueTicket.find_all()

    # ── update ────────────────────────────────────────────────────────────────

    @staticmethod
    def update(ticket_id: str, updates: dict) -> dict | None:
        if _use_db():
            # Map camelCase → snake_case
            col_map = {
                'status': 'status', 'counterNo': 'counter_no',
                'calledAt': 'called_at', 'servedAt': 'served_at', 'doneAt': 'done_at',
                'estimatedWait': 'estimated_wait', 'priority': 'priority',
            }
            sets, params = [], {'id': ticket_id}
            for k, v in updates.items():
                col = col_map.get(k)
                if col:
                    sets.append(f"{col} = :{k}")
                    params[k] = v
            if not sets:
                return QueueTicket.find_by_id(ticket_id)
            sets.append("updated_at = now()")
            db.session.execute(
                text(f"UPDATE public.queue_tickets SET {', '.join(sets)} WHERE id = :id"),
                params
            )
            db.session.commit()
            return QueueTicket.find_by_id(ticket_id)

        tickets = QueueTicket._all_json()
        for i, t in enumerate(tickets):
            if t.get('id') == ticket_id:
                t.update(updates)
                t['updatedAt'] = _now_iso()
                QueueTicket._save_json(tickets)
                return t
        return None

    # ── call_next ─────────────────────────────────────────────────────────────

    @staticmethod
    def call_next(agency_id: str, counter_no: int, service_id: str = None) -> dict | None:
        if _use_db():
            where = "agency_id = :aid AND status = 'waiting' AND date = :dt"
            params: dict = {'aid': agency_id, 'dt': _today(), 'cnt': counter_no}
            if service_id:
                where += ' AND service_id = :sid'
                params['sid'] = service_id
            row = db.session.execute(text(f"""
                SELECT * FROM public.queue_tickets
                WHERE {where}
                ORDER BY priority DESC, ticket_number ASC
                LIMIT 1
            """), params).fetchone()
            if not row:
                return None
            ticket = _row_to_dict(row)
            return QueueTicket.update(ticket['id'], {
                'status': STATUS_CALLED,
                'counterNo': counter_no,
                'calledAt': _now_iso(),
            })

        tickets = QueueTicket._all_json()
        waiting = sorted(
            [
                t for t in tickets
                if t.get('agencyId') == agency_id
                and t.get('status') == STATUS_WAITING
                and t.get('date') == _today()
                and (service_id is None or t.get('serviceId') == service_id)
            ],
            key=lambda t: (-t.get('priority', 0), t.get('ticketNumber', 0))
        )
        if not waiting:
            return None
        nxt = waiting[0]
        for t in tickets:
            if t.get('id') == nxt['id']:
                t.update({'status': STATUS_CALLED, 'counterNo': counter_no,
                           'calledAt': _now_iso(), 'updatedAt': _now_iso()})
                QueueTicket._save_json(tickets)
                return t
        return None

    # ── active check ──────────────────────────────────────────────────────────

    @staticmethod
    def active_for_user(user_id: str, agency_id: str) -> dict | None:
        """Trả về vé đang active (chờ/gọi/phục vụ) của user tại cơ quan."""
        for t in QueueTicket.find_by_user(user_id):
            if t.get('agencyId') == agency_id and t.get('status') in ACTIVE_STATUSES:
                return t
        return None


# ── AgencyCounter ─────────────────────────────────────────────────────────────

class AgencyCounter:

    @staticmethod
    def _all_json() -> list:
        return FileStorage.read_json('agency_counters.json')

    @staticmethod
    def _save_json(data: list) -> None:
        FileStorage.write_json('agency_counters.json', data)

    @staticmethod
    def find_by_agency(agency_id: str) -> list:
        if _use_db():
            rows = db.session.execute(text("""
                SELECT * FROM public.agency_counters WHERE agency_id = :aid
            """), {'aid': agency_id}).fetchall()
            if rows:
                return [dict(r._mapping) for r in rows]
        return [c for c in AgencyCounter._all_json() if c.get('agencyId') == agency_id]

    @staticmethod
    def active_count(agency_id: str) -> int:
        counters = AgencyCounter.find_by_agency(agency_id)
        active = [c for c in counters if c.get('isActive', c.get('is_active', True))]
        return max(len(active), 1)

    @staticmethod
    def upsert(agency_id: str, counter_no: int,
               is_active: bool = True, operator_name: str = '') -> dict:
        if _use_db():
            cid = str(uuid.uuid4())
            db.session.execute(text("""
                INSERT INTO public.agency_counters
                    (id, agency_id, counter_no, is_active, operator_name)
                VALUES (:id, :aid, :cnt, :active, :op)
                ON CONFLICT (agency_id, counter_no) DO UPDATE SET
                    is_active = EXCLUDED.is_active,
                    operator_name = EXCLUDED.operator_name,
                    updated_at = now()
            """), {'id': cid, 'aid': agency_id, 'cnt': counter_no,
                   'active': is_active, 'op': operator_name})
            db.session.commit()
            row = db.session.execute(text("""
                SELECT * FROM public.agency_counters
                WHERE agency_id = :aid AND counter_no = :cnt
            """), {'aid': agency_id, 'cnt': counter_no}).fetchone()
            return dict(row._mapping) if row else {}

        counters = AgencyCounter._all_json()
        for c in counters:
            if c.get('agencyId') == agency_id and c.get('counterNo') == counter_no:
                c.update({'isActive': is_active, 'operatorName': operator_name,
                           'updatedAt': _now_iso()})
                AgencyCounter._save_json(counters)
                return c
        new_c = {
            'id': str(uuid.uuid4()), 'agencyId': agency_id, 'counterNo': counter_no,
            'isActive': is_active, 'operatorName': operator_name,
            'createdAt': _now_iso(), 'updatedAt': _now_iso(),
        }
        counters.append(new_c)
        AgencyCounter._save_json(counters)
        return new_c


# ── ServiceStats ──────────────────────────────────────────────────────────────

class ServiceStats:

    @staticmethod
    def record_service_time(agency_id: str, service_id: str, seconds: float):
        if _use_db():
            db.session.execute(text("""
                INSERT INTO public.service_stats (agency_id, service_id, sample_count, total_seconds, avg_seconds)
                VALUES (:aid, :sid, 1, :secs, :secs)
                ON CONFLICT (agency_id, service_id) DO UPDATE SET
                    sample_count  = service_stats.sample_count + 1,
                    total_seconds = service_stats.total_seconds + :secs,
                    avg_seconds   = (service_stats.total_seconds + :secs) / (service_stats.sample_count + 1),
                    updated_at    = now()
            """), {'aid': agency_id, 'sid': service_id, 'secs': seconds})
            db.session.commit()
            return

        raw = FileStorage.read_json('service_stats.json')
        stats = raw if isinstance(raw, dict) else {}
        key = f"{agency_id}::{service_id}"
        e = stats.get(key, {'count': 0, 'total_seconds': 0, 'avg': 0})
        e['count'] += 1
        e['total_seconds'] += seconds
        e['avg'] = e['total_seconds'] / e['count']
        stats[key] = e
        FileStorage.write_json('service_stats.json', stats)

    @staticmethod
    def avg_service_time(agency_id: str, service_id: str, default_secs: float = 420.0) -> float:
        if _use_db():
            row = db.session.execute(text("""
                SELECT avg_seconds, sample_count FROM public.service_stats
                WHERE agency_id = :aid AND service_id = :sid
            """), {'aid': agency_id, 'sid': service_id}).fetchone()
            if row and row[1] >= 5:
                return float(row[0])
        else:
            raw = FileStorage.read_json('service_stats.json')
            stats = raw if isinstance(raw, dict) else {}
            entry = stats.get(f"{agency_id}::{service_id}")
            if entry and entry.get('count', 0) >= 5:
                return float(entry['avg'])
        return default_secs


# ── QueueService ──────────────────────────────────────────────────────────────

class QueueService:

    PEAK_FACTOR = {8: 1.3, 9: 1.5, 10: 1.4, 11: 1.2, 14: 1.3, 15: 1.4, 16: 1.2}
    SERVICE_COMPLEXITY = {'A': 1.0, 'B': 1.5, 'C': 1.2, 'D': 0.8, 'E': 1.0, 'P': 0.5}

    @staticmethod
    def _peak_factor() -> float:
        return QueueService.PEAK_FACTOR.get(datetime.now().hour, 1.0)

    @staticmethod
    def estimate_wait(agency_id: str, service_id: str,
                      priority: int = 0, prefix: str = 'A') -> int:
        today = _today()
        waiting = QueueTicket.find_all(agency_id=agency_id, date=today, status=STATUS_WAITING)
        tickets_ahead = len(waiting) if priority == 0 else sum(
            1 for t in waiting if t.get('priority', 0) > 0
        )
        num_counters = AgencyCounter.active_count(agency_id)
        avg_time     = ServiceStats.avg_service_time(agency_id, service_id)
        peak_factor  = QueueService._peak_factor()
        complexity   = QueueService.SERVICE_COMPLEXITY.get(prefix, 1.0)

        if tickets_ahead == 0:
            return int(avg_time * complexity * 0.5)
        wait = math.ceil(tickets_ahead / num_counters) * avg_time * peak_factor * complexity
        return int(wait)

    @staticmethod
    def queue_summary(agency_id: str) -> dict:
        today    = _today()
        all_day  = QueueTicket.find_all(agency_id=agency_id, date=today)

        waiting  = [t for t in all_day if t['status'] == STATUS_WAITING]
        called   = [t for t in all_day if t['status'] == STATUS_CALLED]
        serving  = [t for t in all_day if t['status'] == STATUS_SERVING]
        done     = [t for t in all_day if t['status'] == STATUS_DONE]

        # now_serving: quầy đang phục vụ
        now_serving = [
            {
                'counterNo':   t.get('counterNo'),
                'ticketCode':  t.get('ticketCode') or _ticket_code(t.get('prefix', 'A'), t.get('ticketNumber', 0)),
                'serviceName': t.get('serviceName', ''),
            }
            for t in (called + serving) if t.get('counterNo')
        ]

        # avg service time
        served_times = []
        for t in done:
            if t.get('servedAt') and t.get('doneAt'):
                try:
                    s = datetime.fromisoformat(t['servedAt'])
                    d = datetime.fromisoformat(t['doneAt'])
                    served_times.append((d - s).total_seconds())
                except Exception:
                    pass
        avg_service = int(sum(served_times) / len(served_times)) if served_times else 0

        tw = len(waiting)
        load_level = 'high' if tw > 15 else ('medium' if tw > 5 else 'low')

        return {
            'agencyId':          agency_id,
            'date':              today,
            'totalWaiting':      tw,
            'totalCalled':       len(called),
            'totalServing':      len(serving),
            'totalDone':         len(done),
            'activeCounters':    AgencyCounter.active_count(agency_id),
            'avgServiceTimeSec': avg_service,
            'peakFactor':        QueueService._peak_factor(),
            'loadLevel':         load_level,
            'nowServing':        now_serving,
        }

    @staticmethod
    def sync_to_postgres(agency_id: str, summary: dict) -> None:
        """Upsert snapshot vào agency_queue_realtime (dùng cho map-overview nhanh)."""
        if not _use_db():
            return
        try:
            db.session.execute(text("""
                INSERT INTO public.agency_queue_realtime
                    (agency_id, total_waiting, total_serving, load_level, updated_at)
                VALUES (:aid, :tw, :ts, :ll, now())
                ON CONFLICT (agency_id) DO UPDATE SET
                    total_waiting = EXCLUDED.total_waiting,
                    total_serving = EXCLUDED.total_serving,
                    load_level    = EXCLUDED.load_level,
                    updated_at    = now()
            """), {
                'aid': agency_id,
                'tw':  summary.get('totalWaiting', 0),
                'ts':  summary.get('totalServing', 0) + summary.get('totalCalled', 0),
                'll':  summary.get('loadLevel', 'low'),
            })
            db.session.commit()
        except Exception:
            try: db.session.rollback()
            except Exception: pass
