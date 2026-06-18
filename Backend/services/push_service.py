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
