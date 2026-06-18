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
        _appt('c', '2026-06-18', 'confirmed'),
        _appt('d', '2026-06-17', 'cancelled'),
        _appt('e', '2026-06-17', 'confirmed', reminded=True),
    ]
    ids = [a['id'] for a in due_reminders(appts, _TODAY)]
    assert ids == ['a', 'b']


def test_due_handles_date_objects():
    appts = [_appt('a', date(2026, 6, 17))]
    assert [a['id'] for a in due_reminders(appts, _TODAY)] == ['a']
