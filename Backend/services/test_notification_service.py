from services.notification_service import status_notification


def test_status_notification_known():
    assert status_notification('approved') == ('Hồ sơ đã được duyệt', 'medium')
    assert status_notification('more_info') == ('Cần bổ sung hồ sơ', 'high')
    assert status_notification('rejected') == ('Hồ sơ bị từ chối', 'high')
    assert status_notification('submitted') == ('Hồ sơ đã được tiếp nhận', 'low')
    assert status_notification('withdraw') == ('Đã rút hồ sơ', 'low')


def test_status_notification_unknown_defaults():
    assert status_notification('xyz') == ('Cập nhật hồ sơ', 'low')


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
    assert out['id'] == 'n2'
