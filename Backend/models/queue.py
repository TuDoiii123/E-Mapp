"""
Queue / Ticket model
Lưu trữ hàng chờ theo từng cơ quan (agencyId) và loại dịch vụ (serviceId).
Hỗ trợ JSON file-based storage + optional PostgreSQL.
"""
import json
from pathlib import Path
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

# Trạng thái vé
STATUS_WAITING   = 'waiting'    # Đang chờ
STATUS_CALLED    = 'called'     # Đã được gọi
STATUS_SERVING   = 'serving'    # Đang phục vụ
STATUS_DONE      = 'done'       # Hoàn thành
STATUS_ABSENT    = 'absent'     # Vắng mặt khi gọi
STATUS_CANCELLED = 'cancelled'  # Đã hủy

ACTIVE_STATUSES  = {STATUS_WAITING, STATUS_CALLED, STATUS_SERVING}


class QueueTicket:
    """Mô hình vé số thứ tự"""

    def __init__(self, data: dict):
        now = datetime.now().isoformat()
        self.id          = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.agencyId    = data.get('agencyId', '')       # ID cơ quan
        self.serviceId   = data.get('serviceId', '')       # ID thủ tục
        self.serviceName = data.get('serviceName', '')
        self.ticketNumber= data.get('ticketNumber', 0)     # Số thứ tự (int)
        self.prefix      = data.get('prefix', 'A')         # Tiền tố: A, B, C...
        self.userId      = data.get('userId', '')
        self.userName    = data.get('userName', '')
        self.counterNo   = data.get('counterNo', None)     # Quầy phục vụ
        self.status      = data.get('status', STATUS_WAITING)
        self.priority    = data.get('priority', 0)         # 0=thường, 1=ưu tiên
        self.estimatedWait = data.get('estimatedWait', 0)  # giây
        self.calledAt    = data.get('calledAt', None)
        self.servedAt    = data.get('servedAt', None)
        self.doneAt      = data.get('doneAt', None)
        self.createdAt   = data.get('createdAt', now)
        self.updatedAt   = data.get('updatedAt', now)
        # Ngày (YYYY-MM-DD) — để tách queue theo ngày
        self.date        = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    def to_dict(self) -> dict:
        return {
            'id':            self.id,
            'agencyId':      self.agencyId,
            'serviceId':     self.serviceId,
            'serviceName':   self.serviceName,
            'ticketNumber':  self.ticketNumber,
            'prefix':        self.prefix,
            'ticketCode':    f"{self.prefix}{self.ticketNumber:03d}",
            'userId':        self.userId,
            'userName':      self.userName,
            'counterNo':     self.counterNo,
            'status':        self.status,
            'priority':      self.priority,
            'estimatedWait': self.estimatedWait,
            'calledAt':      self.calledAt,
            'servedAt':      self.servedAt,
            'doneAt':        self.doneAt,
            'createdAt':     self.createdAt,
            'updatedAt':     self.updatedAt,
            'date':          self.date,
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def _all() -> list:
        return FileStorage.read_json('queue_tickets.json')

    @staticmethod
    def _save(tickets: list) -> None:
        FileStorage.write_json('queue_tickets.json', tickets)

    # ── CRUD ─────────────────────────────────────────────────────────────────

    @staticmethod
    def find_all(agency_id: str = None, date: str = None,
                 status: str = None) -> list:
        tickets = QueueTicket._all()
        if agency_id:
            tickets = [t for t in tickets if t.get('agencyId') == agency_id]
        if date:
            tickets = [t for t in tickets if t.get('date') == date]
        if status:
            tickets = [t for t in tickets if t.get('status') == status]
        return sorted(tickets, key=lambda t: (t.get('priority', 0), t.get('ticketNumber', 0)))

    @staticmethod
    def find_by_id(ticket_id: str) -> dict | None:
        for t in QueueTicket._all():
            if t.get('id') == ticket_id:
                return t
        return None

    @staticmethod
    def find_by_user(user_id: str, date: str = None) -> list:
        date = date or QueueTicket._today()
        return [
            t for t in QueueTicket._all()
            if t.get('userId') == user_id and t.get('date') == date
        ]

    @staticmethod
    def next_ticket_number(agency_id: str, prefix: str, date: str) -> int:
        """Lấy số thứ tự tiếp theo của ngày hôm nay cho cơ quan + prefix"""
        existing = [
            t for t in QueueTicket._all()
            if t.get('agencyId') == agency_id
            and t.get('prefix') == prefix
            and t.get('date') == date
        ]
        if not existing:
            return 1
        return max(t.get('ticketNumber', 0) for t in existing) + 1

    @staticmethod
    def create(data: dict) -> dict:
        tickets = QueueTicket._all()
        date    = data.get('date', QueueTicket._today())
        prefix  = data.get('prefix', 'A')
        num     = QueueTicket.next_ticket_number(data['agencyId'], prefix, date)
        data['ticketNumber'] = num
        data['date']         = date

        ticket = QueueTicket(data)
        # Tính thời gian chờ ngay khi tạo
        ticket.estimatedWait = QueueService.estimate_wait(
            ticket.agencyId, ticket.serviceId, ticket.priority
        )
        tickets.append(ticket.to_dict())
        QueueTicket._save(tickets)
        return ticket.to_dict()

    @staticmethod
    def update(ticket_id: str, updates: dict) -> dict | None:
        tickets = QueueTicket._all()
        for i, t in enumerate(tickets):
            if t.get('id') == ticket_id:
                t.update(updates)
                t['updatedAt'] = datetime.now().isoformat()
                QueueTicket._save(tickets)
                return t
        return None

    @staticmethod
    def delete(ticket_id: str) -> bool:
        tickets = QueueTicket._all()
        new_list = [t for t in tickets if t.get('id') != ticket_id]
        if len(new_list) == len(tickets):
            return False
        QueueTicket._save(new_list)
        return True

    # ── Counter (quầy) ────────────────────────────────────────────────────────

    @staticmethod
    def call_next(agency_id: str, counter_no: int,
                  service_id: str = None) -> dict | None:
        """Gọi vé tiếp theo cho một quầy"""
        tickets = QueueTicket._all()
        # Ưu tiên theo priority DESC, ticketNumber ASC
        waiting = sorted(
            [
                t for t in tickets
                if t.get('agencyId') == agency_id
                and t.get('status') == STATUS_WAITING
                and t.get('date') == QueueTicket._today()
                and (service_id is None or t.get('serviceId') == service_id)
            ],
            key=lambda t: (-t.get('priority', 0), t.get('ticketNumber', 0))
        )
        if not waiting:
            return None

        next_ticket = waiting[0]
        for t in tickets:
            if t.get('id') == next_ticket['id']:
                t['status']    = STATUS_CALLED
                t['counterNo'] = counter_no
                t['calledAt']  = datetime.now().isoformat()
                t['updatedAt'] = datetime.now().isoformat()
                QueueTicket._save(tickets)
                return t
        return None


class AgencyCounter:
    """Quầy phục vụ của cơ quan"""

    @staticmethod
    def _all() -> list:
        return FileStorage.read_json('agency_counters.json')

    @staticmethod
    def _save(data: list) -> None:
        FileStorage.write_json('agency_counters.json', data)

    @staticmethod
    def find_by_agency(agency_id: str) -> list:
        return [c for c in AgencyCounter._all() if c.get('agencyId') == agency_id]

    @staticmethod
    def active_count(agency_id: str) -> int:
        counters = AgencyCounter.find_by_agency(agency_id)
        active = [c for c in counters if c.get('isActive', True)]
        return max(len(active), 1)

    @staticmethod
    def upsert(agency_id: str, counter_no: int, is_active: bool = True,
               operator_name: str = '') -> dict:
        counters = AgencyCounter._all()
        for c in counters:
            if c.get('agencyId') == agency_id and c.get('counterNo') == counter_no:
                c['isActive']     = is_active
                c['operatorName'] = operator_name
                c['updatedAt']    = datetime.now().isoformat()
                AgencyCounter._save(counters)
                return c
        new_counter = {
            'id':           str(int(datetime.now().timestamp() * 1000)),
            'agencyId':     agency_id,
            'counterNo':    counter_no,
            'isActive':     is_active,
            'operatorName': operator_name,
            'createdAt':    datetime.now().isoformat(),
            'updatedAt':    datetime.now().isoformat(),
        }
        counters.append(new_counter)
        AgencyCounter._save(counters)
        return new_counter


class ServiceStats:
    """Thống kê thời gian phục vụ theo lịch sử — dùng cho thuật toán tính chờ"""

    FILE = 'service_stats.json'

    @staticmethod
    def _all() -> dict:
        raw = FileStorage.read_json(ServiceStats.FILE)
        if isinstance(raw, list):
            return {}
        return raw

    @staticmethod
    def _save(data: dict) -> None:
        FileStorage.write_json(ServiceStats.FILE, data)

    @staticmethod
    def record_service_time(agency_id: str, service_id: str, seconds: float):
        """Ghi nhận thời gian phục vụ thực tế để cải thiện ước tính"""
        stats = ServiceStats._all()
        key   = f"{agency_id}::{service_id}"
        if key not in stats:
            stats[key] = {'count': 0, 'total_seconds': 0, 'avg': 0}
        entry = stats[key]
        entry['count']         += 1
        entry['total_seconds'] += seconds
        entry['avg']            = entry['total_seconds'] / entry['count']
        ServiceStats._save(stats)

    @staticmethod
    def avg_service_time(agency_id: str, service_id: str,
                         default_secs: float = 420.0) -> float:
        """Lấy thời gian phục vụ trung bình (giây). Mặc định 7 phút."""
        stats = ServiceStats._all()
        key   = f"{agency_id}::{service_id}"
        entry = stats.get(key)
        if entry and entry.get('count', 0) >= 5:
            return float(entry['avg'])
        return default_secs


class QueueService:
    """Thuật toán tính toán thời gian chờ ước tính"""

    # Hệ số giờ cao điểm (giờ → hệ số)
    PEAK_FACTOR = {
        8: 1.3, 9: 1.5, 10: 1.4, 11: 1.2,
        14: 1.3, 15: 1.4, 16: 1.2,
    }
    # Hệ số độ phức tạp dịch vụ (prefix → hệ số)
    SERVICE_COMPLEXITY = {
        'A': 1.0,   # Hành chính thông thường
        'B': 1.5,   # Đất đai, xây dựng
        'C': 1.2,   # Tư pháp, hộ tịch
        'D': 0.8,   # Xác nhận đơn giản
        'P': 0.5,   # Ưu tiên — xử lý nhanh
    }

    @staticmethod
    def estimate_wait(agency_id: str, service_id: str,
                      priority: int = 0, prefix: str = 'A') -> int:
        """
        Ước tính thời gian chờ (giây).

        Công thức:
            wait = ceil(tickets_ahead / counters) × avg_service_time
                   × peak_factor × complexity_factor
        """
        today = QueueTicket._today()

        # Đếm số vé đang chờ (cùng cơ quan, cùng ngày)
        waiting = QueueTicket.find_all(
            agency_id=agency_id, date=today, status=STATUS_WAITING
        )
        # Vé ưu tiên chen vào đầu
        if priority == 0:
            # Vé thường: đứng sau tất cả vé ưu tiên
            tickets_ahead = len(waiting)
        else:
            # Vé ưu tiên: chỉ đứng sau các vé ưu tiên đã có
            tickets_ahead = sum(1 for t in waiting if t.get('priority', 0) > 0)

        num_counters = AgencyCounter.active_count(agency_id)
        avg_time     = ServiceStats.avg_service_time(agency_id, service_id)
        peak_factor  = QueueService._peak_factor()
        complexity   = QueueService.SERVICE_COMPLEXITY.get(prefix, 1.0)

        if tickets_ahead == 0:
            # Sắp được gọi, còn đang phục vụ người trước
            return int(avg_time * complexity * 0.5)

        import math
        wait = math.ceil(tickets_ahead / num_counters) * avg_time
        wait *= peak_factor * complexity
        return int(wait)

    @staticmethod
    def _peak_factor() -> float:
        hour = datetime.now().hour
        return QueueService.PEAK_FACTOR.get(hour, 1.0)

    @staticmethod
    def queue_summary(agency_id: str) -> dict:
        """Tóm tắt trạng thái hàng chờ của cơ quan"""
        today   = QueueTicket._today()
        all_day = QueueTicket.find_all(agency_id=agency_id, date=today)

        waiting  = [t for t in all_day if t.get('status') == STATUS_WAITING]
        called   = [t for t in all_day if t.get('status') == STATUS_CALLED]
        serving  = [t for t in all_day if t.get('status') == STATUS_SERVING]
        done     = [t for t in all_day if t.get('status') == STATUS_DONE]

        # Số đang được gọi/phục vụ theo quầy
        counters_busy = {}
        for t in called + serving:
            cn = t.get('counterNo')
            if cn:
                counters_busy[str(cn)] = {
                    'ticketCode': t.get('ticketCode') or f"{t.get('prefix','A')}{t.get('ticketNumber',0):03d}",
                    'status':     t.get('status'),
                    'serviceName':t.get('serviceName', ''),
                }

        avg_service = 0
        if done:
            served_times = []
            for t in done:
                if t.get('servedAt') and t.get('doneAt'):
                    try:
                        s = datetime.fromisoformat(t['servedAt'])
                        d = datetime.fromisoformat(t['doneAt'])
                        served_times.append((d - s).total_seconds())
                    except Exception:
                        pass
            if served_times:
                avg_service = int(sum(served_times) / len(served_times))

        total_waiting = len(waiting)
        total_serving = len(serving) + len(called)

        if total_waiting <= 5:
            load_level = 'low'
        elif total_waiting <= 15:
            load_level = 'medium'
        else:
            load_level = 'high'

        return {
            'agencyId':        agency_id,
            'date':            today,
            'totalWaiting':    total_waiting,
            'totalCalled':     len(called),
            'totalServing':    len(serving),
            'totalDone':       len(done),
            'activeCounters':  AgencyCounter.active_count(agency_id),
            'countersBusy':    counters_busy,
            'avgServiceTimeSec': avg_service,
            'peakFactor':      QueueService._peak_factor(),
            'loadLevel':       load_level,
            'nowServing':      [
                {
                    'counterNo':  t.get('counterNo'),
                    'ticketCode': t.get('ticketCode') or f"{t.get('prefix','A')}{t.get('ticketNumber',0):03d}",
                    'serviceName':t.get('serviceName', ''),
                }
                for t in called + serving if t.get('counterNo')
            ],
        }

    @staticmethod
    def sync_to_postgres(agency_id: str, summary: dict) -> None:
        """Upsert queue snapshot vào bảng agency_queue_realtime."""
        if not HAS_DB or db is None:
            return
        try:
            upsert_sql = text("""
                INSERT INTO public.agency_queue_realtime
                    (agency_id, total_waiting, total_serving, load_level, updated_at)
                VALUES
                    (:agency_id, :total_waiting, :total_serving, :load_level, now())
                ON CONFLICT (agency_id) DO UPDATE SET
                    total_waiting = EXCLUDED.total_waiting,
                    total_serving = EXCLUDED.total_serving,
                    load_level    = EXCLUDED.load_level,
                    updated_at    = now()
            """)
            db.session.execute(upsert_sql, {
                'agency_id':    agency_id,
                'total_waiting': summary.get('totalWaiting', 0),
                'total_serving': summary.get('totalServing', 0) + summary.get('totalCalled', 0),
                'load_level':   summary.get('loadLevel', 'low'),
            })
            db.session.commit()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
