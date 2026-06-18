# Notification Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây Trung tâm Thông báo có backend thật cho E-Mapp: bảng `notifications` + API + sinh thông báo theo sự kiện (đổi trạng thái hồ sơ, rút hồ sơ, tạo lịch hẹn, nhắc lịch hẹn, broadcast hệ thống), đánh dấu đã đọc bền vững, nối `NotificationScreen` vào API; cộng push Web FCM (config-driven, degrade an toàn).

**Architecture:** In-app là lõi luôn chạy; push là best-effort bọc ngoài. Sự kiện gọi `notification_service.emit()` → ghi bảng `notifications` rồi gửi FCM (no-op nếu chưa cấu hình Firebase). Frontend poll `/api/notifications` khi mở màn.

**Tech Stack:** Python/Flask, Flask-SQLAlchemy (`db.session` + raw SQL), PostgreSQL local, pytest 7.4.3 (chạy từ `Backend/`), firebase-admin (lazy), React/Vite + firebase web SDK.

**Phases:** Task 1–9 = in-app core (build + test ngay, không phụ thuộc ngoài). Task 10–13 = push FCM + frontend (cần `FIREBASE_CREDENTIALS` backend & `VITE_FIREBASE_*` frontend để KÍCH HOẠT; code viết để degrade khi thiếu).

---

## File Structure

| File | Trách nhiệm |
|---|---|
| `Backend/models/db.py` | **SỬA** — DDL `notifications`, `push_tokens`, cột `appointments.reminder_sent` |
| `Backend/models/notification.py` | **MỚI** — `Notification`, `PushToken` (SQL qua db.session) |
| `Backend/services/notification_service.py` | **MỚI** — `status_notification`, `emit`, `emit_system_all` |
| `Backend/services/push_service.py` | **MỚI** — FCM lazy + degrade |
| `Backend/services/notification_scheduler.py` | **MỚI** — `due_reminders` + `run_reminder_loop` |
| `Backend/routes/notification_routes.py` | **MỚI** — API `/api/notifications/*` |
| `Backend/server.py` | **SỬA** — đăng ký blueprint + start scheduler |
| `Backend/routes/admin_routes.py` | **SỬA** — hook emit khi duyệt/từ chối hồ sơ |
| `Backend/routes/applications_routes.py` | **SỬA** — hook emit khi rút hồ sơ |
| `Backend/routes/appointments_routes.py` | **SỬA** — hook emit khi tạo lịch hẹn |
| `Backend/requirements.txt` | **SỬA** — thêm `firebase-admin` |
| `Backend/services/test_notification_service.py` | **MỚI** — test |
| `Backend/services/test_push_service.py` | **MỚI** — test |
| `Backend/services/test_notification_scheduler.py` | **MỚI** — test |
| `frontend/src/services/notificationService.ts` | **MỚI** — gọi API |
| `frontend/src/screens/user/NotificationScreen.tsx` | **SỬA** — nối API thật |
| `frontend/src/lib/push.ts` + `frontend/public/firebase-messaging-sw.js` | **MỚI** — push web |

**Lệnh test backend (từ `Backend/`):** `python -m pytest services/test_notification_service.py services/test_push_service.py services/test_notification_scheduler.py -q`
**Syntax gate:** `python -m compileall -q Backend/models Backend/services Backend/routes`

---

## Task 1: DB schema cho notifications

**Files:**
- Modify: `Backend/models/db.py` (thêm khối DDL trong `init_db`, cạnh khối "Chatbot config tables")

- [ ] **Step 1: Thêm khối DDL**

Trong `init_db(app)`, sau khối tạo `chatbot_*` tables (tìm `log.debug('Chatbot config tables OK')`), thêm khối mới:

```python
        # ── Notification tables ───────────────────────────────────────────────
        try:
            notif_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.notifications (
                id         VARCHAR(80)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
                user_id    VARCHAR(80)  NOT NULL,
                type       VARCHAR(30)  NOT NULL,
                title      VARCHAR(255) NOT NULL,
                content    TEXT         NOT NULL DEFAULT '',
                link       VARCHAR(60),
                ref_id     VARCHAR(80),
                priority   VARCHAR(10)  NOT NULL DEFAULT 'low',
                read_at    TIMESTAMPTZ,
                created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_notif_user
                ON public.notifications(user_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_notif_unread
                ON public.notifications(user_id, read_at);

            CREATE TABLE IF NOT EXISTS public.push_tokens (
                token      VARCHAR(255) PRIMARY KEY,
                user_id    VARCHAR(80)  NOT NULL,
                platform   VARCHAR(20)  NOT NULL DEFAULT 'web',
                created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_pushtok_user
                ON public.push_tokens(user_id);

            ALTER TABLE public.appointments
                ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN NOT NULL DEFAULT FALSE;
            ''')
            db.session.execute(notif_ddl)
            db.session.commit()
            log.debug('Notification tables OK')
        except Exception as e:
            log.warning(f'Ensuring notification tables failed: {e}')
            db.session.rollback()
```

- [ ] **Step 2: Verify tạo bảng trên Postgres local**

Run (từ `Backend/`, nạp .env):
```bash
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); ctx=app.app_context(); ctx.push(); print('tables:', [r[0] for r in db.session.execute(text(\"SELECT table_name FROM information_schema.tables WHERE table_name IN ('notifications','push_tokens')\")).fetchall()]); print('reminder_sent:', db.session.execute(text(\"SELECT column_name FROM information_schema.columns WHERE table_name='appointments' AND column_name='reminder_sent'\")).fetchone() is not None)"
```
Expected: `tables: ['notifications', 'push_tokens']` (thứ tự bất kỳ) và `reminder_sent: True`.

- [ ] **Step 3: Commit**

```bash
git add Backend/models/db.py
git commit -m "feat(notif): DDL bảng notifications + push_tokens + cột reminder_sent"
```

---

## Task 2: Model `Notification` + `PushToken`

**Files:**
- Create: `Backend/models/notification.py`

- [ ] **Step 1: Tạo `Backend/models/notification.py`**

```python
"""
Model Notification + PushToken — lưu PostgreSQL qua db.session (raw SQL).
"""
from models.db import db
from sqlalchemy import text


def _row_to_dict(row) -> dict:
    m = row._mapping
    return {
        'id':        m['id'],
        'type':      m['type'],
        'title':     m['title'],
        'content':   m['content'] or '',
        'link':      m['link'],
        'refId':     m['ref_id'],
        'priority':  m['priority'],
        'read':      m['read_at'] is not None,
        'time':      m['created_at'].isoformat() if m['created_at'] else None,
    }


class Notification:
    @staticmethod
    def create(user_id, type, title, content='', link=None, ref_id=None, priority='low') -> dict:
        row = db.session.execute(text('''
            INSERT INTO public.notifications (user_id, type, title, content, link, ref_id, priority)
            VALUES (:uid, :type, :title, :content, :link, :ref, :prio)
            RETURNING *
        '''), {'uid': user_id, 'type': type, 'title': title, 'content': content,
               'link': link, 'ref': ref_id, 'prio': priority}).fetchone()
        db.session.commit()
        return _row_to_dict(row)

    @staticmethod
    def list_for(user_id, only_unread=False, limit=50) -> list:
        clause = 'AND read_at IS NULL' if only_unread else ''
        rows = db.session.execute(text(f'''
            SELECT * FROM public.notifications
            WHERE user_id = :uid {clause}
            ORDER BY created_at DESC LIMIT :lim
        '''), {'uid': user_id, 'lim': limit}).fetchall()
        return [_row_to_dict(r) for r in rows]

    @staticmethod
    def unread_count(user_id) -> int:
        return int(db.session.execute(text('''
            SELECT COUNT(*) FROM public.notifications WHERE user_id = :uid AND read_at IS NULL
        '''), {'uid': user_id}).scalar() or 0)

    @staticmethod
    def mark_read(notif_id, user_id) -> bool:
        res = db.session.execute(text('''
            UPDATE public.notifications SET read_at = now()
            WHERE id = :id AND user_id = :uid AND read_at IS NULL
        '''), {'id': notif_id, 'uid': user_id})
        db.session.commit()
        return res.rowcount > 0

    @staticmethod
    def mark_all_read(user_id) -> int:
        res = db.session.execute(text('''
            UPDATE public.notifications SET read_at = now()
            WHERE user_id = :uid AND read_at IS NULL
        '''), {'uid': user_id})
        db.session.commit()
        return res.rowcount


class PushToken:
    @staticmethod
    def register(user_id, token, platform='web') -> None:
        db.session.execute(text('''
            INSERT INTO public.push_tokens (token, user_id, platform)
            VALUES (:tok, :uid, :pf)
            ON CONFLICT (token) DO UPDATE SET user_id = :uid, platform = :pf
        '''), {'tok': token, 'uid': user_id, 'pf': platform})
        db.session.commit()

    @staticmethod
    def list_tokens(user_id) -> list:
        rows = db.session.execute(text('''
            SELECT token FROM public.push_tokens WHERE user_id = :uid
        '''), {'uid': user_id}).fetchall()
        return [r[0] for r in rows]

    @staticmethod
    def remove(token) -> None:
        db.session.execute(text('DELETE FROM public.push_tokens WHERE token = :tok'), {'tok': token})
        db.session.commit()
```

- [ ] **Step 2: Verify import + compile**

Run (từ `Backend/`): `python -c "import ast; ast.parse(open('models/notification.py',encoding='utf-8').read()); print('parse OK')"`
Expected: `parse OK`
Run: `python -m compileall -q models/notification.py`
Expected: không lỗi.

- [ ] **Step 3: Commit**

```bash
git add Backend/models/notification.py
git commit -m "feat(notif): model Notification + PushToken"
```

---

## Task 3: Helper `status_notification` (pure, TDD)

**Files:**
- Create: `Backend/services/notification_service.py` (chỉ helper trước; emit thêm ở Task 5)
- Test: `Backend/services/test_notification_service.py`

- [ ] **Step 1: Viết test**

```python
# Backend/services/test_notification_service.py
from services.notification_service import status_notification


def test_status_notification_known():
    assert status_notification('approved') == ('Hồ sơ đã được duyệt', 'medium')
    assert status_notification('more_info') == ('Cần bổ sung hồ sơ', 'high')
    assert status_notification('rejected') == ('Hồ sơ bị từ chối', 'high')
    assert status_notification('submitted') == ('Hồ sơ đã được tiếp nhận', 'low')
    assert status_notification('withdraw') == ('Đã rút hồ sơ', 'low')


def test_status_notification_unknown_defaults():
    assert status_notification('xyz') == ('Cập nhật hồ sơ', 'low')
```

- [ ] **Step 2: Run test → fail**

Run: `python -m pytest services/test_notification_service.py -q`
Expected: FAIL — `ModuleNotFoundError: services.notification_service`

- [ ] **Step 3: Tạo `Backend/services/notification_service.py`**

```python
"""
Notification service — sinh thông báo in-app (lõi) + đẩy push (best-effort).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('notification')

# status hồ sơ → (tiêu đề, mức ưu tiên). Khớp nhãn ở NotificationScreen.
_STATUS_MAP = {
    'submitted': ('Hồ sơ đã được tiếp nhận', 'low'),
    'in_review': ('Hồ sơ đang được xem xét', 'medium'),
    'more_info': ('Cần bổ sung hồ sơ', 'high'),
    'approved':  ('Hồ sơ đã được duyệt', 'medium'),
    'rejected':  ('Hồ sơ bị từ chối', 'high'),
    'withdraw':  ('Đã rút hồ sơ', 'low'),
}


def status_notification(status: str):
    """Trả (title, priority) cho 1 trạng thái hồ sơ."""
    return _STATUS_MAP.get(status, ('Cập nhật hồ sơ', 'low'))
```

- [ ] **Step 4: Run test → pass**

Run: `python -m pytest services/test_notification_service.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/services/notification_service.py Backend/services/test_notification_service.py
git commit -m "feat(notif): helper status_notification + test"
```

---

## Task 4: `push_service` (degrade an toàn, TDD)

**Files:**
- Create: `Backend/services/push_service.py`
- Test: `Backend/services/test_push_service.py`

- [ ] **Step 1: Viết test**

```python
# Backend/services/test_push_service.py
import services.push_service as ps


def test_send_noop_without_firebase(monkeypatch):
    # Không có FIREBASE_CREDENTIALS → _ensure() False → send no-op, không raise
    monkeypatch.delenv('FIREBASE_CREDENTIALS', raising=False)
    ps._initialized = False
    ps._enabled = False
    assert ps.send('user-1', 'tiêu đề', 'nội dung') is None


def test_send_swallows_errors(monkeypatch):
    monkeypatch.setattr(ps, '_ensure', lambda: True)
    def boom(uid):
        raise RuntimeError('token store down')
    monkeypatch.setattr(ps, '_get_tokens', boom)
    # lỗi nội bộ vẫn không raise
    assert ps.send('user-1', 't', 'b') is None
```

- [ ] **Step 2: Run test → fail**

Run: `python -m pytest services/test_push_service.py -q`
Expected: FAIL — `ModuleNotFoundError: services.push_service`

- [ ] **Step 3: Tạo `Backend/services/push_service.py`**

```python
"""
Web Push qua Firebase Cloud Messaging — config-driven + degrade.
Thiếu FIREBASE_CREDENTIALS hoặc thiếu SDK → no-op (in-app vẫn chạy).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('push')

_initialized = False
_enabled = False
_app = None


def _ensure() -> bool:
    """Khởi tạo firebase-admin 1 lần. Trả True nếu push khả dụng."""
    global _initialized, _enabled, _app
    if _initialized:
        return _enabled
    _initialized = True
    cred_path = os.getenv('FIREBASE_CREDENTIALS', '').strip()
    if not cred_path or not os.path.exists(cred_path):
        log.info('[push] FIREBASE_CREDENTIALS chưa cấu hình → push tắt (in-app vẫn chạy)')
        _enabled = False
        return False
    try:
        import firebase_admin
        from firebase_admin import credentials
        _app = firebase_admin.initialize_app(credentials.Certificate(cred_path))
        _enabled = True
    except Exception as e:  # noqa: BLE001
        log.warning(f'[push] init firebase-admin lỗi → push tắt: {e}')
        _enabled = False
    return _enabled


def _get_tokens(user_id):
    from models.notification import PushToken
    return PushToken.list_tokens(user_id)


def send(user_id, title, body, data=None):
    """Gửi push tới mọi token của user. Best-effort, không bao giờ raise."""
    if not _ensure():
        return None
    try:
        tokens = _get_tokens(user_id)
        if not tokens:
            return None
        from firebase_admin import messaging
        from models.notification import PushToken
        msg = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            tokens=tokens,
        )
        resp = messaging.send_each_for_multicast(msg)
        for tok, r in zip(tokens, resp.responses):
            if not r.success:
                PushToken.remove(tok)
    except Exception as e:  # noqa: BLE001
        log.debug(f'[push] send lỗi (bỏ qua): {e}')
    return None
```

- [ ] **Step 4: Run test → pass**

Run: `python -m pytest services/test_push_service.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/services/push_service.py Backend/services/test_push_service.py
git commit -m "feat(notif): push_service FCM degrade an toàn"
```

---

## Task 5: `emit` + `emit_system_all` (TDD, mock model + push)

**Files:**
- Modify: `Backend/services/notification_service.py`
- Test: `Backend/services/test_notification_service.py` (thêm)

- [ ] **Step 1: Thêm test**

```python
import services.notification_service as nsvc


def test_emit_creates_and_pushes(monkeypatch):
    created = {}
    monkeypatch.setattr(nsvc.Notification, 'create',
                        lambda **kw: (created.update(kw) or {'id': 'n1', **kw}))
    pushed = {}
    monkeypatch.setattr(nsvc.push_service, 'send',
                        lambda uid, title, body, data=None: pushed.update(
                            {'uid': uid, 'title': title}))
    out = nsvc.emit('user-1', 'document', 'Tiêu đề', 'Nội dung',
                    link='search', ref_id='app-9', priority='high')
    assert out['id'] == 'n1'
    assert created['user_id'] == 'user-1' and created['priority'] == 'high'
    assert pushed['uid'] == 'user-1' and pushed['title'] == 'Tiêu đề'


def test_emit_skips_when_no_user(monkeypatch):
    monkeypatch.setattr(nsvc.Notification, 'create',
                        lambda **kw: (_ for _ in ()).throw(AssertionError('không nên gọi')))
    assert nsvc.emit('', 'document', 't', 'b') is None


def test_emit_survives_push_failure(monkeypatch):
    monkeypatch.setattr(nsvc.Notification, 'create', lambda **kw: {'id': 'n2', **kw})
    def boom(*a, **k):
        raise RuntimeError('fcm down')
    monkeypatch.setattr(nsvc.push_service, 'send', boom)
    out = nsvc.emit('user-1', 'system', 't', 'b')
    assert out['id'] == 'n2'   # push lỗi không làm emit vỡ
```

- [ ] **Step 2: Run test → fail**

Run: `python -m pytest services/test_notification_service.py -q -k "emit"`
Expected: FAIL — `AttributeError: module ... has no attribute 'Notification'` / `emit`

- [ ] **Step 3: Bổ sung vào `notification_service.py`**

Thêm import ở đầu (sau `log = ...`):
```python
from models.notification import Notification
from services import push_service
```

Thêm hàm:
```python
def emit(user_id, type, title, content='', link=None, ref_id=None, priority='low'):
    """Ghi 1 notification in-app rồi đẩy push (best-effort). Bỏ qua nếu thiếu user_id."""
    if not user_id:
        return None
    n = Notification.create(user_id=user_id, type=type, title=title, content=content,
                            link=link, ref_id=ref_id, priority=priority)
    try:
        push_service.send(user_id, title, content,
                          {'link': link or '', 'refId': ref_id or ''})
    except Exception as e:  # noqa: BLE001
        log.debug(f'[notif] push bỏ qua: {e}')
    return n


def emit_system_all(title, content='', link=None):
    """Fan-out thông báo hệ thống tới mọi user."""
    from models.db import db
    from sqlalchemy import text
    try:
        ids = [r[0] for r in db.session.execute(text('SELECT id FROM public.users')).fetchall()]
    except Exception as e:  # noqa: BLE001
        log.warning(f'[notif] emit_system_all không lấy được users: {e}')
        return 0
    sent = 0
    for uid in ids:
        try:
            emit(uid, 'system', title, content, link=link, priority='medium')
            sent += 1
        except Exception as e:  # noqa: BLE001
            log.debug(f'[notif] emit_system_all bỏ qua {uid}: {e}')
    return sent
```

- [ ] **Step 4: Run test → pass**

Run: `python -m pytest services/test_notification_service.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/services/notification_service.py Backend/services/test_notification_service.py
git commit -m "feat(notif): emit + emit_system_all (mock-tested)"
```

---

## Task 6: Scheduler nhắc lịch hẹn (`due_reminders` pure, TDD)

**Files:**
- Create: `Backend/services/notification_scheduler.py`
- Test: `Backend/services/test_notification_scheduler.py`

- [ ] **Step 1: Viết test**

```python
# Backend/services/test_notification_scheduler.py
from datetime import date
from services.notification_scheduler import due_reminders

_TODAY = date(2026, 6, 16)   # nhắc cho ngày mai = 2026-06-17


def _appt(id, d, status='confirmed', reminded=False):
    return {'id': id, 'user_id': 'u-' + id, 'date': d,
            'status': status, 'reminder_sent': reminded}


def test_due_picks_tomorrow_pending_or_confirmed():
    appts = [
        _appt('a', '2026-06-17', 'confirmed'),
        _appt('b', '2026-06-17', 'pending'),
        _appt('c', '2026-06-18', 'confirmed'),   # không phải ngày mai
        _appt('d', '2026-06-17', 'cancelled'),    # status loại
        _appt('e', '2026-06-17', 'confirmed', reminded=True),  # đã nhắc
    ]
    ids = [a['id'] for a in due_reminders(appts, _TODAY)]
    assert ids == ['a', 'b']


def test_due_handles_date_objects():
    appts = [_appt('a', date(2026, 6, 17))]
    assert [a['id'] for a in due_reminders(appts, _TODAY)] == ['a']
```

- [ ] **Step 2: Run test → fail**

Run: `python -m pytest services/test_notification_scheduler.py -q`
Expected: FAIL — `ModuleNotFoundError: services.notification_scheduler`

- [ ] **Step 3: Tạo `Backend/services/notification_scheduler.py`**

```python
"""
Scheduler nhắc lịch hẹn — daemon thread quét appointment đến hạn (ngày mai)
và sinh thông báo nhắc. Theo pattern thread nền trong server.py.
"""
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('notif.scheduler')

_REMINDABLE = {'pending', 'confirmed'}
_INTERVAL_SECONDS = 1800   # 30 phút


def _as_date(d):
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    return datetime.strptime(str(d)[:10], '%Y-%m-%d').date()


def due_reminders(appointments, today):
    """Lọc appointment cần nhắc: date == today+1, status remindable, chưa nhắc."""
    target = today + timedelta(days=1)
    out = []
    for a in appointments:
        try:
            if (_as_date(a.get('date')) == target
                    and a.get('status') in _REMINDABLE
                    and not a.get('reminder_sent')):
                out.append(a)
        except Exception:
            continue
    return out


def run_reminder_loop(app):
    """Daemon: định kỳ quét + nhắc. Bọc try/except, không bao giờ crash."""
    from models.db import db
    from sqlalchemy import text
    from services.notification_service import emit
    while True:
        try:
            with app.app_context():
                rows = db.session.execute(text('''
                    SELECT id, user_id, date, status, reminder_sent
                    FROM public.appointments
                    WHERE reminder_sent = FALSE AND status IN ('pending','confirmed')
                      AND date = (CURRENT_DATE + INTERVAL '1 day')
                ''')).fetchall()
                for r in rows:
                    m = r._mapping
                    if not m['user_id']:
                        continue
                    emit(m['user_id'], 'appointment', 'Nhắc lịch hẹn ngày mai',
                         f"Bạn có lịch hẹn vào ngày mai. Mã: {m['id']}",
                         link='appointments', ref_id=m['id'], priority='medium')
                    db.session.execute(text(
                        'UPDATE public.appointments SET reminder_sent = TRUE WHERE id = :id'),
                        {'id': m['id']})
                db.session.commit()
        except Exception as e:  # noqa: BLE001
            log.debug(f'[notif.scheduler] vòng quét lỗi (bỏ qua): {e}')
        time.sleep(_INTERVAL_SECONDS)
```

- [ ] **Step 4: Run test → pass**

Run: `python -m pytest services/test_notification_scheduler.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/services/notification_scheduler.py Backend/services/test_notification_scheduler.py
git commit -m "feat(notif): scheduler nhắc lịch hẹn (due_reminders pure-tested)"
```

---

## Task 7: API routes `/api/notifications/*`

**Files:**
- Create: `Backend/routes/notification_routes.py`
- Modify: `Backend/server.py` (đăng ký blueprint)

- [ ] **Step 1: Tạo `Backend/routes/notification_routes.py`**

```python
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
```

- [ ] **Step 2: Đăng ký blueprint trong `server.py`**

Trong danh sách `_blueprints` (tìm `('routes.ai_routes', 'ai_bp'),`), thêm dòng:
```python
    ('routes.notification_routes',  'notification_bp'),
```

- [ ] **Step 3: Verify compile + smoke (server local)**

Run: `python -m compileall -q Backend/routes/notification_routes.py`
Expected: không lỗi.

Smoke (tùy chọn, nếu chạy server): khởi động `python server.py`, rồi:
`curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8888/api/notifications`
Expected: `401` (chưa đăng nhập → đúng, chứng tỏ route đã đăng ký).

- [ ] **Step 4: Commit**

```bash
git add Backend/routes/notification_routes.py Backend/server.py
git commit -m "feat(notif): API /api/notifications + đăng ký blueprint"
```

---

## Task 8: Hook sinh thông báo vào sự kiện

**Files:**
- Modify: `Backend/routes/admin_routes.py` (sau `db.session.commit()` ~dòng 119, trong endpoint duyệt hồ sơ)
- Modify: `Backend/routes/applications_routes.py` (endpoint `/<id>/withdraw`)
- Modify: `Backend/routes/appointments_routes.py` (sau khi tạo appointment thành công)

- [ ] **Step 1: Hook duyệt hồ sơ (admin_routes.py)**

Ngay sau `db.session.commit()` (dòng ~119, trước `log.info('[AUDIT]...`), thêm:
```python
        # Sinh thông báo cho người nộp
        try:
            applicant = db.session.execute(
                text('SELECT applicant_id FROM public.applications WHERE id = :id'),
                {'id': application_id}).fetchone()
            if applicant and applicant[0]:
                from services.notification_service import emit, status_notification
                title, prio = status_notification(status)
                emit(applicant[0], 'document', title,
                     f'Hồ sơ mã {application_id}', link='search',
                     ref_id=application_id, priority=prio)
        except Exception as _e:
            log.debug(f'[notif] hook duyệt hồ sơ bỏ qua: {_e}')
```

- [ ] **Step 2: Hook rút hồ sơ (applications_routes.py)**

Trong endpoint `@applications_bp.route('/<app_id>/withdraw', methods=['PUT'])`, sau khi cập nhật trạng thái thành công (trước khi return success), thêm:
```python
        try:
            from services.notification_service import emit, status_notification
            title, prio = status_notification('withdraw')
            emit(getattr(request, 'user_id', None), 'document', title,
                 f'Hồ sơ mã {app_id}', link='search', ref_id=app_id, priority=prio)
        except Exception as _e:
            log.debug(f'[notif] hook rút hồ sơ bỏ qua: {_e}')
```

- [ ] **Step 3: Hook tạo lịch hẹn (appointments_routes.py)**

Tìm endpoint tạo appointment (POST tạo lịch). Sau khi tạo thành công và có `user_id`, trước return, thêm (đổi tên biến `new_appt`/`user_id` cho khớp code thực tế trong hàm):
```python
        try:
            from services.notification_service import emit
            _uid = getattr(request, 'user_id', None)
            if _uid:
                emit(_uid, 'appointment', 'Đặt lịch hẹn thành công',
                     f"Lịch hẹn mã {new_appt.get('id')} đã được tạo.",
                     link='appointments', ref_id=new_appt.get('id'), priority='medium')
        except Exception as _e:
            log.debug(f'[notif] hook tạo lịch hẹn bỏ qua: {_e}')
```
**Lưu ý cho người triển khai:** mở `appointments_routes.py`, tìm hàm POST tạo lịch (route không có `<...>/status`), xác định biến chứa appointment vừa tạo (vd `appt`, `new_appt`, `item`) và sửa `new_appt.get('id')` cho khớp. Nếu route dùng `request.user_id`, giữ như trên.

- [ ] **Step 4: Verify compile**

Run: `python -m compileall -q Backend/routes/admin_routes.py Backend/routes/applications_routes.py Backend/routes/appointments_routes.py`
Expected: không lỗi.

- [ ] **Step 5: Commit**

```bash
git add Backend/routes/admin_routes.py Backend/routes/applications_routes.py Backend/routes/appointments_routes.py
git commit -m "feat(notif): hook emit khi duyệt/rút hồ sơ + tạo lịch hẹn"
```

---

## Task 9: Khởi động scheduler + dependency

**Files:**
- Modify: `Backend/server.py` (start daemon thread)
- Modify: `Backend/requirements.txt`

- [ ] **Step 1: Start scheduler thread trong server.py**

Cạnh các thread nền khác (vd sau `threading.Thread(target=_cleanup_rag_sessions, ...).start()`), thêm:
```python
try:
    from services.notification_scheduler import run_reminder_loop
    threading.Thread(target=run_reminder_loop, args=(app,), daemon=True).start()
    log.info('[notif] reminder scheduler started')
except Exception as _e:
    log.warning(f'[notif] không start được scheduler: {_e}')
```
(`app` là Flask app đã tạo trong server.py.)

- [ ] **Step 2: Thêm dependency**

Thêm vào `Backend/requirements.txt`:
```
firebase-admin
```

- [ ] **Step 3: Verify compile**

Run: `python -m compileall -q Backend/server.py`
Expected: không lỗi.

- [ ] **Step 4: Commit**

```bash
git add Backend/server.py Backend/requirements.txt
git commit -m "feat(notif): start reminder scheduler + thêm firebase-admin"
```

---

## Task 10: Frontend service `notificationService.ts`

**Files:**
- Create: `frontend/src/services/notificationService.ts`

- [ ] **Step 1: Xem pattern service hiện có**

Đọc `frontend/src/services/adminService.ts` để biết cách gọi API (base URL, header auth, hàm `get/post`). Tái dùng cùng helper/axios/fetch wrapper đó.

- [ ] **Step 2: Tạo `frontend/src/services/notificationService.ts`**

```typescript
// Dùng cùng http helper như adminService. Nếu adminService export `api`/`http`,
// import nó; ví dụ dưới giả định có `apiGet/apiPost/apiDelete` (đổi cho khớp dự án).
import { apiGet, apiPost, apiDelete } from './adminService';

export interface NotificationDTO {
  id: string; type: string; title: string; content: string;
  link?: string; refId?: string; priority: string; read: boolean; time: string;
}

export async function list(unread = false, limit = 50): Promise<NotificationDTO[]> {
  const r = await apiGet(`/api/notifications?unread=${unread ? 1 : 0}&limit=${limit}`);
  return Array.isArray(r.data) ? r.data : [];
}
export async function unreadCount(): Promise<number> {
  const r = await apiGet('/api/notifications/unread-count');
  return r.count ?? 0;
}
export async function markRead(id: string): Promise<void> {
  await apiPost(`/api/notifications/${id}/read`, {});
}
export async function markAllRead(): Promise<void> {
  await apiPost('/api/notifications/read-all', {});
}
export async function registerPushToken(token: string): Promise<void> {
  await apiPost('/api/notifications/push-token', { token, platform: 'web' });
}
```
**Lưu ý người triển khai:** nếu `adminService.ts` không export `apiGet/apiPost/apiDelete`, thay bằng đúng tên helper/axios instance mà dự án dùng (giữ nguyên endpoint).

- [ ] **Step 3: Verify build/typecheck**

Run (từ `frontend/`): `npm run build` (hoặc `npx tsc --noEmit`)
Expected: build/typecheck thành công, không lỗi import.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/services/notificationService.ts
git commit -m "feat(notif): frontend notificationService"
```

---

## Task 11: Nối `NotificationScreen` vào API thật

**Files:**
- Modify: `frontend/src/screens/user/NotificationScreen.tsx`

- [ ] **Step 1: Thay nguồn dữ liệu**

Trong `NotificationScreen.tsx`:
(a) thêm import: `import * as notifSvc from '../../services/notificationService';`
(b) thay `useEffect` đang gọi `adminSvc.getMyApplications()` để map notifications — chuyển sang gọi API thật cho danh sách thông báo, giữ `adminSvc.getMyApplications()` riêng cho tab "Lịch sử":
```tsx
  const [notifs, setNotifs] = useState<any[]>([]);
  useEffect(() => {
    notifSvc.list().then(setNotifs).catch(() => setNotifs([]));
    adminSvc.getMyApplications()
      .then(r => setApplications(Array.isArray(r.data) ? r.data : []))
      .catch(() => setApplications([]))
      .finally(() => setLoading(false));
  }, []);
```
(c) thay biến `notifications` (đang map từ applications) bằng dữ liệu API + đồng bộ readSet local cho phản hồi tức thì:
```tsx
  const notifications = notifs.map(n => ({
    id: n.id, type: n.type, title: n.title, content: n.content,
    time: n.time ? new Date(n.time).toLocaleDateString('vi-VN') : '',
    read: readSet.has(String(n.id)) || n.read,
    priority: n.priority, documentId: n.refId, link: n.link,
  }));
```
(d) `handleMarkAllRead` → gọi API:
```tsx
  const handleMarkAllRead = () => {
    setReadSet(new Set(notifications.map(n => String(n.id))));
    notifSvc.markAllRead().catch(() => {});
  };
```
(e) khi click 1 thông báo → mark read + điều hướng theo `link`:
```tsx
  onClick={() => {
    setReadSet(prev => new Set(prev).add(String(notification.id)));
    notifSvc.markRead(String(notification.id)).catch(() => {});
    onNavigate(notification.link || 'search');
  }}
```

- [ ] **Step 2: Verify build**

Run (từ `frontend/`): `npm run build`
Expected: build thành công.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/screens/user/NotificationScreen.tsx
git commit -m "feat(notif): NotificationScreen dùng API thật + mark-read bền vững"
```

---

## Task 12: Push web (Firebase) — config-driven

**Files:**
- Create: `frontend/src/lib/push.ts`
- Create: `frontend/public/firebase-messaging-sw.js`
- Modify: nơi khởi tạo app (vd `frontend/src/App.tsx`) gọi `initPush()` sau đăng nhập

- [ ] **Step 1: Cài firebase**

Run (từ `frontend/`): `npm install firebase`

- [ ] **Step 2: Tạo `frontend/src/lib/push.ts`**

```typescript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, isSupported } from 'firebase/messaging';
import { registerPushToken } from '../services/notificationService';

const cfg = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
};

export async function initPush(): Promise<void> {
  // Thiếu cấu hình → bỏ qua êm (in-app vẫn chạy)
  if (!cfg.apiKey || !cfg.projectId || !(await isSupported().catch(() => false))) return;
  try {
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') return;
    const app = initializeApp(cfg);
    const messaging = getMessaging(app);
    const token = await getToken(messaging, {
      vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
    });
    if (token) await registerPushToken(token);
  } catch (e) {
    console.warn('[push] init bỏ qua:', e);
  }
}
```

- [ ] **Step 3: Tạo `frontend/public/firebase-messaging-sw.js`**

```javascript
// Service worker nhận push nền. Dùng compat SDK qua importScripts.
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

// CHÚ Ý: điền config Firebase web của bạn vào đây (không có biến env trong SW).
firebase.initializeApp({
  apiKey: '', authDomain: '', projectId: '', messagingSenderId: '', appId: '',
});
const messaging = firebase.messaging();
messaging.onBackgroundMessage((payload) => {
  const n = payload.notification || {};
  self.registration.showNotification(n.title || 'E-Mapp', { body: n.body || '' });
});
```

- [ ] **Step 4: Gọi `initPush()` sau đăng nhập**

Trong `frontend/src/App.tsx`, sau khi xác định user đã đăng nhập, gọi một lần:
```tsx
import { initPush } from './lib/push';
// trong useEffect chạy khi user đã đăng nhập:
useEffect(() => { if (isAuthenticated) { initPush(); } }, [isAuthenticated]);
```
**Lưu ý người triển khai:** đổi `isAuthenticated` cho khớp biến trạng thái đăng nhập thực tế trong App.tsx.

- [ ] **Step 5: Verify build**

Run (từ `frontend/`): `npm run build`
Expected: build thành công (push tự tắt khi thiếu `VITE_FIREBASE_*`).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/push.ts frontend/public/firebase-messaging-sw.js frontend/src/App.tsx frontend/package.json frontend/package-lock.json
git commit -m "feat(notif): push web Firebase (config-driven, degrade)"
```

---

## Task 13: Kiểm thử tích hợp + chạy toàn bộ

- [ ] **Step 1: Toàn bộ test backend**

Run (từ `Backend/`): `python -m pytest services/test_notification_service.py services/test_push_service.py services/test_notification_scheduler.py -q`
Expected: tất cả PASS (9 test).

- [ ] **Step 2: Syntax gate**

Run: `python -m compileall -q Backend/models Backend/services Backend/routes Backend/server.py`
Expected: không lỗi.

- [ ] **Step 3: Smoke end-to-end (DB local + server)**

Khởi động `python server.py`. Tạo nhanh 1 notification rồi đọc qua API (dùng 1 user_id có thật + JWT của họ — hoặc test trực tiếp model trong app context):
```bash
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; app=Flask(__name__); init_db(app); ctx=app.app_context(); ctx.push(); from models.notification import Notification; n=Notification.create(user_id='smoke-user', type='system', title='Test', content='Hello'); print('created', n['id']); print('list', len(Notification.list_for('smoke-user'))); print('unread', Notification.unread_count('smoke-user')); print('markall', Notification.mark_all_read('smoke-user')); print('unread sau', Notification.unread_count('smoke-user'))"
```
Expected: created <id>; list 1; unread 1; markall 1; unread sau 0.

- [ ] **Step 4: Dọn dữ liệu smoke (tùy chọn)**

```bash
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); app.app_context().push(); db.session.execute(text(\"DELETE FROM public.notifications WHERE user_id='smoke-user'\")); db.session.commit(); print('cleaned')"
```

- [ ] **Step 5: Commit (nếu có thay đổi nhỏ phát sinh)**

```bash
git add -A && git commit -m "test(notif): smoke tích hợp notification end-to-end" || echo "không có thay đổi"
```

---

## Ghi chú triển khai
- **In-app hoạt động độc lập** với Firebase: Task 1–9 đủ để có Trung tâm Thông báo chạy thật.
- **Push chỉ kích hoạt** khi có `FIREBASE_CREDENTIALS` (backend) + `VITE_FIREBASE_*` (frontend) + điền config trong `firebase-messaging-sw.js`. Thiếu → tự tắt, không lỗi.
- Test backend không cần DB/Firebase (pure + mock); chỉ Task 1/13 smoke cần Postgres local.
- Hook (Task 8) bọc try/except — không bao giờ làm hỏng nghiệp vụ chính.
