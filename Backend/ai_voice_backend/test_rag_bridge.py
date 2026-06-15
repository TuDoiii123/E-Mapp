from ai_voice_backend import rag_bridge


def test_empty_query_returns_empty(monkeypatch):
    assert rag_bridge.search('') == []
    assert rag_bridge.search('   ') == []


def test_search_delegates_to_rag(monkeypatch):
    monkeypatch.setattr(rag_bridge, '_load_search',
                        lambda: (lambda q: ['Cần CMND cũ và sổ hộ khẩu.']))
    out = rag_bridge.search('làm căn cước cần gì')
    assert out == ['Cần CMND cũ và sổ hộ khẩu.']


def test_search_swallows_errors(monkeypatch):
    def boom():
        raise RuntimeError('model not ready')
    monkeypatch.setattr(rag_bridge, '_load_search', boom)
    assert rag_bridge.search('bất kỳ') == []
