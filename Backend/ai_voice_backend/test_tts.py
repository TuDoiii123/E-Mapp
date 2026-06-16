"""Test TTS: bọc PCM→WAV và chọn mime type theo backend (mock, không gọi network)."""
import base64
import io
import types as _types
import wave

import ai_voice_backend.tts as T
from ai_voice_backend.tts import TTSEngine, _pcm_to_wav, _parse_rate


def _fake_audio_resp():
    inline = _types.SimpleNamespace(
        mime_type='audio/L16;codec=pcm;rate=24000', data=b'\x00\x01' * 50)
    part = _types.SimpleNamespace(inline_data=inline)
    content = _types.SimpleNamespace(parts=[part])
    return _types.SimpleNamespace(candidates=[_types.SimpleNamespace(content=content)])


class _FakeModels:
    def __init__(self, fail_times):
        self.calls = 0
        self._fail_times = fail_times

    def generate_content(self, **kw):
        self.calls += 1
        if self.calls <= self._fail_times:
            raise RuntimeError('transient 503')
        return _fake_audio_resp()


class _FakeClient:
    def __init__(self, fail_times):
        self.models = _FakeModels(fail_times)


def test_pcm_to_wav_is_valid_riff():
    pcm = b'\x01\x02' * 100          # 200 bytes PCM 16-bit
    wav = _pcm_to_wav(pcm, rate=24000, channels=1, sampwidth=2)
    assert wav[:4] == b'RIFF'
    assert wav[8:12] == b'WAVE'
    # đọc lại bằng module wave để chắc header đúng
    with wave.open(io.BytesIO(wav), 'rb') as w:
        assert w.getframerate() == 24000
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.readframes(w.getnframes()) == pcm


def test_parse_rate_from_gemini_mime():
    assert _parse_rate('audio/L16;codec=pcm;rate=24000') == 24000
    assert _parse_rate('audio/L16;rate=16000') == 16000
    assert _parse_rate('audio/unknown', default=24000) == 24000


def test_synthesize_response_mime_gemini(monkeypatch):
    eng = TTSEngine()
    monkeypatch.setattr(eng, '_synthesize_gcloud', lambda spoken: None)
    monkeypatch.setattr(eng, '_synthesize_gemini', lambda spoken: b'FAKEWAV')
    resp = eng.synthesize_response('xin chào')
    assert resp == {'mimeType': 'audio/wav',
                    'base64': base64.b64encode(b'FAKEWAV').decode('ascii')}


def test_synthesize_response_mime_gcloud(monkeypatch):
    eng = TTSEngine()
    monkeypatch.setattr(eng, '_synthesize_gcloud', lambda spoken: b'FAKEMP3')
    # gemini không nên được gọi vì gcloud đã có kết quả
    monkeypatch.setattr(eng, '_synthesize_gemini',
                        lambda spoken: (_ for _ in ()).throw(AssertionError('không nên gọi')))
    resp = eng.synthesize_response('xin chào')
    assert resp['mimeType'] == 'audio/mpeg'
    assert resp['base64'] == base64.b64encode(b'FAKEMP3').decode('ascii')


def test_synthesize_none_when_no_backend(monkeypatch):
    eng = TTSEngine()
    monkeypatch.setattr(eng, '_synthesize_gcloud', lambda spoken: None)
    monkeypatch.setattr(eng, '_synthesize_gemini', lambda spoken: None)
    assert eng.synthesize('xin chào') is None
    assert eng.synthesize_response('xin chào') is None


def test_synthesize_empty_text_returns_none():
    eng = TTSEngine()
    assert eng.synthesize('') is None
    assert eng.synthesize('   ') is None


def test_gemini_retries_once_then_succeeds(monkeypatch):
    monkeypatch.setattr(T, 'GEMINI_API_KEY', 'x')        # qua guard thiếu key
    monkeypatch.setattr(T.time, 'sleep', lambda s: None)  # không sleep thật
    eng = TTSEngine()
    eng._genai_client = _FakeClient(fail_times=1)         # lỗi lần 1, ok lần 2
    out = eng._synthesize_gemini('xin chào')
    assert out is not None and out[:4] == b'RIFF'         # WAV hợp lệ
    assert eng._genai_client.models.calls == 2            # đã retry


def test_gemini_gives_up_after_retry(monkeypatch):
    monkeypatch.setattr(T, 'GEMINI_API_KEY', 'x')
    monkeypatch.setattr(T.time, 'sleep', lambda s: None)
    eng = TTSEngine()
    eng._genai_client = _FakeClient(fail_times=99)        # luôn lỗi
    assert eng._synthesize_gemini('xin chào') is None
    assert eng._genai_client.models.calls == 2            # thử đúng 2 lần rồi bỏ
