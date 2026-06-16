"""
TTS Engine — Text-to-Speech tiếng Việt.

Backend (thử theo thứ tự):
  1. Google Cloud TTS  (chất lượng Chirp3-HD cao nhất, cần GCP credentials) → MP3
  2. Gemini TTS        (dùng GEMINI_API_KEY, KHÔNG cần GCP credentials)      → WAV
  3. Silent fallback   (trả None khi không có backend)

Output: bytes audio (MP3 hoặc WAV) + mime tương ứng, hoặc base64-encoded string.
Text luôn được chuẩn hóa (ngày/giờ/số/viết tắt) trước khi đọc.
"""
import base64
import io
import re
import sys
import wave
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .config import (
    GEMINI_API_KEY, GEMINI_MODEL,
    TTS_LANGUAGE, TTS_VOICE_NAME,
    TTS_SPEAKING_RATE, TTS_PITCH,
    GEMINI_TTS_MODEL, GEMINI_TTS_VOICE,
)
from .text_normalizer import normalize, to_ssml

log = get_logger('voice.tts')


def _is_natural_voice(voice_name: str) -> bool:
    """Giọng thế hệ mới (Chirp3-HD, Studio, Journey) KHÔNG nhận SSML/pitch —
    chỉ nhận text thô. Trả True để TTS biết dùng text + bỏ pitch."""
    v = (voice_name or '').lower()
    return any(tag in v for tag in ('chirp', 'studio', 'journey', '-hd'))


def _parse_rate(mime: str, default: int = 24000) -> int:
    """Lấy sample rate từ mime kiểu 'audio/L16;codec=pcm;rate=24000'."""
    m = re.search(r'rate=(\d+)', mime or '')
    return int(m.group(1)) if m else default


def _pcm_to_wav(pcm: bytes, rate: int = 24000, channels: int = 1,
                sampwidth: int = 2) -> bytes:
    """Bọc PCM thô (Gemini trả về) thành WAV phát được trên trình duyệt."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(channels)
        w.setsampwidth(sampwidth)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


class TTSEngine:
    """
    Text-to-Speech engine, giọng tiếng Việt.

    Sử dụng:
        engine = TTSEngine()
        mp3_bytes = engine.synthesize("Xin chào, tôi có thể giúp gì cho bạn?")
        b64_str   = engine.synthesize_b64("Xin chào")
    """

    def __init__(self) -> None:
        self._gcloud_client = None
        self._genai_client = None

    # ── public ────────────────────────────────────────────────────────────────

    def synthesize(self, text: str) -> Optional[bytes]:
        """Chuyển text → audio bytes (MP3 hoặc WAV). Trả None nếu không có backend."""
        res = self._synthesize(text)
        return res[0] if res else None

    def synthesize_b64(self, text: str) -> Optional[str]:
        """Chuyển text → base64-encoded audio string."""
        res = self._synthesize(text)
        if res is None:
            return None
        return base64.b64encode(res[0]).decode('ascii')

    def synthesize_response(self, text: str) -> Optional[dict]:
        """Trả dict {'mimeType': ..., 'base64': '...'} (mime đúng theo backend) hoặc None."""
        res = self._synthesize(text)
        if res is None:
            return None
        audio, mime = res
        return {'mimeType': mime, 'base64': base64.b64encode(audio).decode('ascii')}

    @property
    def available(self) -> bool:
        """True nếu có ít nhất một backend TTS hoạt động (có cả key lẫn SDK)."""
        if GEMINI_API_KEY:
            try:
                from google import genai  # noqa
                return True
            except ImportError:
                pass
        try:
            from google.cloud import texttospeech  # type: ignore  # noqa
            return True
        except ImportError:
            return False

    # ── pipeline ───────────────────────────────────────────────────────────────

    def _synthesize(self, text: str) -> Optional[Tuple[bytes, str]]:
        """Chuẩn hóa text 1 lần rồi thử lần lượt các backend. Trả (audio, mime)."""
        if not text or not text.strip():
            return None
        spoken = normalize(text)

        # 1. Google Cloud TTS → MP3
        mp3 = self._synthesize_gcloud(spoken)
        if mp3:
            log.info(f'[TTS] Google Cloud: {len(mp3)} bytes — "{text[:50]}"')
            return mp3, 'audio/mpeg'

        # 2. Gemini TTS → WAV
        wav = self._synthesize_gemini(spoken)
        if wav:
            log.info(f'[TTS] Gemini: {len(wav)} bytes — "{text[:50]}"')
            return wav, 'audio/wav'

        log.warning('[TTS] Không có backend TTS khả dụng '
                    '(thiếu Google Cloud credentials và GEMINI_API_KEY)')
        return None

    # ── Google Cloud TTS ──────────────────────────────────────────────────────

    def _synthesize_gcloud(self, spoken: str) -> Optional[bytes]:
        try:
            from google.cloud import texttospeech as g_tts  # type: ignore
        except ImportError:
            return None
        try:
            if self._gcloud_client is None:
                self._gcloud_client = g_tts.TextToSpeechClient()

            # Chọn giọng đọc — luôn kèm language_code cho chắc
            if TTS_VOICE_NAME:
                voice_params = g_tts.VoiceSelectionParams(
                    language_code=TTS_LANGUAGE,
                    name=TTS_VOICE_NAME,
                )
            else:
                voice_params = g_tts.VoiceSelectionParams(
                    language_code=TTS_LANGUAGE,
                    ssml_gender=g_tts.SsmlVoiceGender.FEMALE,
                )

            natural = _is_natural_voice(TTS_VOICE_NAME)

            # Chirp3-HD/Studio: text thô, không pitch. Neural2/Wavenet: SSML + pitch.
            if natural:
                synth_input = g_tts.SynthesisInput(text=spoken)
            else:
                synth_input = g_tts.SynthesisInput(ssml=to_ssml(spoken))

            audio_cfg = g_tts.AudioConfig(
                audio_encoding=g_tts.AudioEncoding.MP3,
                speaking_rate=TTS_SPEAKING_RATE,
            )
            if not natural:
                audio_cfg.pitch = TTS_PITCH  # Chirp3-HD báo lỗi nếu set pitch

            res = self._gcloud_client.synthesize_speech(
                input=synth_input,
                voice=voice_params,
                audio_config=audio_cfg,
            )
            return res.audio_content
        except Exception as e:
            log.debug(f'[TTS][GCloud] {e}')
            return None

    # ── Gemini TTS (không cần GCP credentials) ─────────────────────────────────

    def _synthesize_gemini(self, spoken: str) -> Optional[bytes]:
        """Gọi Gemini TTS qua GEMINI_API_KEY → bọc PCM thành WAV. Lỗi → None."""
        if not GEMINI_API_KEY:
            return None
        try:
            from google import genai  # SDK mới (google-genai)
            from google.genai import types
        except ImportError:
            log.debug('[TTS][Gemini] chưa cài SDK google-genai')
            return None
        try:
            if self._genai_client is None:
                self._genai_client = genai.Client(api_key=GEMINI_API_KEY)
            resp = self._genai_client.models.generate_content(
                model=GEMINI_TTS_MODEL,
                contents=spoken,
                config=types.GenerateContentConfig(
                    response_modalities=['AUDIO'],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=GEMINI_TTS_VOICE))),
                ),
            )
            inline = resp.candidates[0].content.parts[0].inline_data
            return _pcm_to_wav(inline.data, rate=_parse_rate(inline.mime_type))
        except Exception as e:
            log.debug(f'[TTS][Gemini] {e}')
            return None
