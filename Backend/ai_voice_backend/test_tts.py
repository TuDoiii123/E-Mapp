"""Test TTS: bọc PCM→WAV và chọn mime type theo backend (mock, không gọi network)."""
import base64
import io
import wave

from ai_voice_backend.tts import TTSEngine, _pcm_to_wav, _parse_rate


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
