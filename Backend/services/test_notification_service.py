from services.notification_service import status_notification


def test_status_notification_known():
    assert status_notification('approved') == ('Hồ sơ đã được duyệt', 'medium')
    assert status_notification('more_info') == ('Cần bổ sung hồ sơ', 'high')
    assert status_notification('rejected') == ('Hồ sơ bị từ chối', 'high')
    assert status_notification('submitted') == ('Hồ sơ đã được tiếp nhận', 'low')
    assert status_notification('withdraw') == ('Đã rút hồ sơ', 'low')


def test_status_notification_unknown_defaults():
    assert status_notification('xyz') == ('Cập nhật hồ sơ', 'low')
