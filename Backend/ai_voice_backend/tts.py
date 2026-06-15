"""
TTS Engine — Text-to-Speech tiếng Việt.

Backend:
  1. Google Cloud TTS  (chất lượng cao, cần GCP credentials)
  2. Gemini TTS        (dùng Gemini 2.5 Flash / Preview nếu hỗ trợ)
  3. Silent fallback   (trả None khi không có backend)

Output: bytes MP3 hoặc base64-encoded string.
"""
import base64
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .config import (
    GEMINI_API_KEY, GEMINI_MODEL,
    TTS_LANGUAGE, TTS_VOICE_NAME,
    TTS_SPEAKING_RATE, TTS_PITCH,
)
from .text_normalizer import normalize, to_ssml

log = get_logger('voice.tts')


def _is_natural_voice(voice_name: str) -> bool:
    """Giọng thế hệ mới (Chirp3-HD, Studio, Journey) KHÔNG nhận SSML/pitch —
    chỉ nhận text thô. Trả True để TTS biết dùng text + bỏ pitch."""
    v = (voice_name or '').lower()
    return any(tag in v for tag in ('chirp', 'studio', 'journey', '-hd'))


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

    # ── public ────────────────────────────────────────────────────────────────

    def synthesize(self, text: str) -> Optional[bytes]:
        """Chuyển text → MP3 bytes. Trả None nếu không có backend."""
        if not text or not text.strip():
            return None

        # 1. Google Cloud TTS
        result = self._synthesize_gcloud(text)
        if result:
            log.info(f'[TTS] Google Cloud: {len(result)} bytes — "{text[:50]}"')
            return result

        # 2. Thông báo không có backend
        log.warning('[TTS] Không có backend TTS khả dụng (Google Cloud TTS chưa cấu hình)')
        return None

    def synthesize_b64(self, text: str) -> Optional[str]:
        """Chuyển text → base64-encoded MP3 string."""
        mp3 = self.synthesize(text)
        if mp3 is None:
            return None
        return base64.b64encode(mp3).decode('ascii')

    def synthesize_response(self, text: str) -> Optional[dict]:
        """Trả dict {'mimeType': 'audio/mpeg', 'base64': '...'} hoặc None."""
        b64 = self.synthesize_b64(text)
        if b64 is None:
            return None
        return {'mimeType': 'audio/mpeg', 'base64': b64}

    @property
    def available(self) -> bool:
        """True nếu có ít nhất một backend TTS hoạt động."""
        try:
            from google.cloud import texttospeech  # type: ignore  # noqa
            return True
        except ImportError:
            return False

    # ── Google Cloud TTS ──────────────────────────────────────────────────────

    def _synthesize_gcloud(self, text: str) -> Optional[bytes]:
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

            # Chuẩn hóa text → đọc tự nhiên (ngày/giờ/số/viết tắt)
            spoken = normalize(text)
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
