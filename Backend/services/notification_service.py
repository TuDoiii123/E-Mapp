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
