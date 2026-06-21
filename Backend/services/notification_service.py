"""
Notification service — sinh thông báo in-app (lõi) + đẩy push (best-effort).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('notification')

from models.notification import Notification
from services import push_service

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
