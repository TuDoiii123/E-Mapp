import services.push_service as ps


def test_send_noop_without_firebase(monkeypatch):
    monkeypatch.delenv('FIREBASE_CREDENTIALS', raising=False)
    ps._initialized = False
    ps._enabled = False
    assert ps.send('user-1', 'tiêu đề', 'nội dung') is None


def test_send_swallows_errors(monkeypatch):
    monkeypatch.setattr(ps, '_ensure', lambda: True)
    def boom(uid):
        raise RuntimeError('token store down')
    monkeypatch.setattr(ps, '_get_tokens', boom)
    assert ps.send('user-1', 't', 'b') is None
