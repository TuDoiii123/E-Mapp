"""
STT Engine — Speech-to-Text tiếng Việt.

Ưu tiên:
  1. Gemini multimodal  (gửi audio bytes trực tiếp → không cần GCP credentials)
  2. Google Cloud Speech (chất lượng cao, cần credentials)
  3. Mock mode          (dev, trả về chuỗi mẫu)

Gemini audio input hỗ trợ: audio/webm, audio/mp4, audio/mpeg, audio/wav, audio/ogg
"""
import base64
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .config import (
    GEMINI_API_KEY, GEMINI_MODEL,
    STT_LANGUAGE, STT_MOCK, STT_DEFAULT_MOCK,
)

log = get_logger('voice.stt')

# Mime-type map theo đuôi file
_MIME_MAP = {
    'webm': 'audio/webm',
    'mp4':  'audio/mp4',
    'mp3':  'audio/mpeg',
    'wav':  'audio/wav',
    'ogg':  'audio/ogg',
    'm4a':  'audio/mp4',
}


class STTEngine:
    """
    Speech-to-Text engine cho tiếng Việt.

    Thứ tự thử:
      GEMINI (nếu có GEMINI_API_KEY) → GOOGLE_CLOUD → MOCK
    """

    def __init__(self) -> None:
        self._gemini_model = None
        self._gcloud_client = None
        self._backend: Optional[str] = None

    # ── public ────────────────────────────────────────────────────────────────

    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = 'audio/webm',
        mock_text: Optional[str] = None,
    ) -> str:
        """
        Chuyển audio bytes → chuỗi tiếng Việt.

        Parameters
        ----------
        audio_bytes : raw audio
        mime_type   : MIME type của audio, dùng để gửi lên Gemini
        mock_text   : override mock text (dùng từ header X-Debug-Transcription)
        """
        if not audio_bytes:
            return ''

        # 1. Thử Gemini multimodal
        if GEMINI_API_KEY:
            result = self._transcribe_gemini(audio_bytes, mime_type)
            if result:
                log.info(f'[STT] Gemini: "{result[:80]}"')
                return result

        # 2. Thử Google Cloud Speech
        result = self._transcribe_gcloud(audio_bytes)
        if result:
            log.info(f'[STT] Google Cloud: "{result[:80]}"')
            return result

        # 3. Mock mode
        if STT_MOCK:
            text = mock_text or STT_DEFAULT_MOCK
            log.info(f'[STT] MOCK: "{text}"')
            return text

        log.warning('[STT] Tất cả backends đều không khả dụng, trả về chuỗi rỗng')
        return ''

    def transcribe_file(self, filepath: str) -> str:
        """Đọc file audio và transcribe."""
        ext = os.path.splitext(filepath)[-1].lstrip('.').lower()
        mime = _MIME_MAP.get(ext, 'audio/webm')
        with open(filepath, 'rb') as f:
            return self.transcribe(f.read(), mime)

    @property
    def backend(self) -> str:
        """Tên backend đang dùng."""
        if GEMINI_API_KEY:
            return 'gemini'
        try:
            from google.cloud import speech  # noqa
            return 'google_cloud'
        except ImportError:
            pass
        return 'mock'

    # ── Gemini multimodal STT ─────────────────────────────────────────────────

    def _transcribe_gemini(self, audio_bytes: bytes, mime_type: str) -> str:
        """
        Dùng Gemini multimodal để nhận dạng giọng nói tiếng Việt.
        Không cần Google Cloud credentials — chỉ cần GEMINI_API_KEY.
        """
        try:
            import google.generativeai as genai

            if self._gemini_model is None:
                genai.configure(api_key=GEMINI_API_KEY)
                self._gemini_model = genai.GenerativeModel(GEMINI_MODEL)

            audio_b64 = base64.b64encode(audio_bytes).decode('ascii')
            response  = self._gemini_model.generate_content([
                {
                    'parts': [
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': audio_b64,
                            }
                        },
                        (
                            'Hãy chuyển đổi nội dung âm thanh tiếng Việt này thành văn bản. '
                            'Chỉ trả lời đúng văn bản đã nhận dạng, không giải thích thêm. '
                            'Nếu không nghe được gì, trả về chuỗi rỗng.'
                        ),
                    ]
                }
            ])
            text = (getattr(response, 'text', None) or '').strip()
            return text
        except Exception as e:
            log.debug(f'[STT][Gemini] {e}')
            return ''

    # ── Google Cloud Speech ───────────────────────────────────────────────────

    def _transcribe_gcloud(self, audio_bytes: bytes) -> str:
        """Google Cloud Speech-to-Text API."""
        try:
            from google.cloud import speech as g_speech
        except ImportError:
            return ''
        try:
            if self._gcloud_client is None:
                self._gcloud_client = g_speech.SpeechClient()

            audio  = g_speech.RecognitionAudio(content=audio_bytes)
            config = g_speech.RecognitionConfig(
                encoding=g_speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                language_code=STT_LANGUAGE,
                enable_automatic_punctuation=True,
                model='latest_long',
            )
            res  = self._gcloud_client.recognize(config=config, audio=audio)
            text = ' '.join(r.alternatives[0].transcript for r in res.results).strip()
            return text
        except Exception as e:
            log.debug(f'[STT][GCloud] {e}')
            return ''
