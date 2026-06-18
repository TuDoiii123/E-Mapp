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
