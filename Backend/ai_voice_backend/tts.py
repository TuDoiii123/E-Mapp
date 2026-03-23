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

log = get_logger('voice.tts')


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
            from google.cloud import texttospeech  # noqa
            return True
        except ImportError:
            return False

    # ── Google Cloud TTS ──────────────────────────────────────────────────────

    def _synthesize_gcloud(self, text: str) -> Optional[bytes]:
        try:
            from google.cloud import texttospeech as g_tts
        except ImportError:
            return None
        try:
            if self._gcloud_client is None:
                self._gcloud_client = g_tts.TextToSpeechClient()

            # Chọn giọng đọc
            if TTS_VOICE_NAME:
                voice_params = g_tts.VoiceSelectionParams(name=TTS_VOICE_NAME)
            else:
                voice_params = g_tts.VoiceSelectionParams(
                    language_code=TTS_LANGUAGE,
                    ssml_gender=g_tts.SsmlVoiceGender.FEMALE,
                )

            res = self._gcloud_client.synthesize_speech(
                input=g_tts.SynthesisInput(text=text),
                voice=voice_params,
                audio_config=g_tts.AudioConfig(
                    audio_encoding=g_tts.AudioEncoding.MP3,
                    speaking_rate=TTS_SPEAKING_RATE,
                    pitch=TTS_PITCH,
                ),
            )
            return res.audio_content
        except Exception as e:
            log.debug(f'[TTS][GCloud] {e}')
            return None
