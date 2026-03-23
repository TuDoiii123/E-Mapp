"""
VoiceBackend — facade tổng hợp STT + TTS + NLU + Dialog.

Đây là điểm duy nhất mà voice_routes.py cần import.

Sử dụng:
    from ai_voice_backend import VoiceBackend
    vb = VoiceBackend()

    # Speech-to-Text
    text = vb.stt(audio_bytes, mime_type='audio/webm')

    # Text-to-Speech
    mp3  = vb.tts("Xin chào bạn")
    b64  = vb.tts_b64("Xin chào bạn")

    # NLU thuần
    result = vb.analyze(text)

    # Hội thoại đặt lịch multi-turn
    resp = vb.dialog(session_id, text, speak=True)

    # One-shot: phân tích text và đặt lịch ngay
    resp = vb.auto_book(session_id, text)
"""
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

from .stt            import STTEngine
from .tts            import TTSEngine
from .nlu            import NLUEngine, NLUResult
from .dialog_manager import DialogManager, DialogResponse
from .config         import DIALOG_TTS_ENABLED

log = get_logger('voice.backend')


class VoiceBackend:
    """
    Facade thống nhất cho toàn bộ AI Voice Backend.

    Lazy-init: các engine chỉ khởi tạo khi được gọi lần đầu.
    """

    def __init__(self) -> None:
        self._stt    = STTEngine()
        self._tts    = TTSEngine()
        self._nlu    = NLUEngine()
        self._dialog = DialogManager()
        log.info('[VoiceBackend] initialized — STT/TTS/NLU/Dialog ready')

    # ── STT ───────────────────────────────────────────────────────────────────

    def stt(
        self,
        audio_bytes: bytes,
        mime_type: str = 'audio/webm',
        mock_text: Optional[str] = None,
    ) -> str:
        """Speech-to-Text. Trả về chuỗi tiếng Việt đã nhận dạng."""
        return self._stt.transcribe(audio_bytes, mime_type, mock_text)

    # ── TTS ───────────────────────────────────────────────────────────────────

    def tts(self, text: str) -> Optional[bytes]:
        """Text-to-Speech. Trả về MP3 bytes hoặc None."""
        return self._tts.synthesize(text)

    def tts_b64(self, text: str) -> Optional[str]:
        """Text-to-Speech. Trả về base64 string hoặc None."""
        return self._tts.synthesize_b64(text)

    def tts_response(self, text: str) -> Optional[dict]:
        """Trả {'mimeType': 'audio/mpeg', 'base64': '...'} hoặc None."""
        return self._tts.synthesize_response(text)

    # ── NLU ───────────────────────────────────────────────────────────────────

    def analyze(self, text: str) -> NLUResult:
        """Phân tích intent + entities từ câu tiếng Việt."""
        return self._nlu.analyze(text)

    # ── Dialog ────────────────────────────────────────────────────────────────

    def dialog_start(self, session_id: str) -> DialogResponse:
        """Bắt đầu phiên hội thoại mới."""
        return self._dialog.start(session_id)

    def dialog(
        self,
        session_id: str,
        user_text: str,
        speak: bool = False,
    ) -> DialogResponse:
        """
        Xử lý một lượt hội thoại đặt lịch.

        Parameters
        ----------
        session_id : định danh phiên (mỗi người dùng một session)
        user_text  : câu nói của người dùng (đã qua STT)
        speak      : nếu True, đính kèm audio TTS trong response
        """
        resp = self._dialog.process(session_id, user_text)

        # Đính kèm TTS nếu được yêu cầu
        if speak or DIALOG_TTS_ENABLED:
            audio = self.tts_response(resp.reply)
            if audio:
                resp.__dict__['audio'] = audio  # attach to response object

        return resp

    def dialog_reset(self, session_id: str) -> None:
        """Xóa trạng thái phiên hội thoại."""
        self._dialog.reset(session_id)

    # ── Auto-book (one-shot) ──────────────────────────────────────────────────

    def auto_book(
        self,
        session_id: str,
        user_text: str,
        speak: bool = False,
    ) -> DialogResponse:
        """
        One-shot: cố gắng trích xuất đủ thông tin từ một câu và đặt lịch ngay.
        Nếu thiếu thông tin → tiếp tục hội thoại multi-turn.
        """
        return self.dialog(session_id, user_text, speak=speak)

    # ── STT → Dialog pipeline ─────────────────────────────────────────────────

    def process_audio(
        self,
        session_id: str,
        audio_bytes: bytes,
        mime_type: str = 'audio/webm',
        speak: bool = True,
        mock_text: Optional[str] = None,
    ) -> dict:
        """
        Pipeline đầy đủ: Audio → STT → Dialog → TTS.

        Returns dict:
          {
            'transcription': str,    # văn bản nhận dạng từ audio
            'reply':         str,    # câu trả lời của bot
            'step':          str,    # bước hội thoại hiện tại
            'done':          bool,   # True nếu đã đặt lịch xong
            'appointment':   dict|None,
            'audio':         dict|None,  # {'mimeType', 'base64'}
          }
        """
        # 1. STT
        text = self.stt(audio_bytes, mime_type, mock_text)
        if not text:
            no_audio_reply = 'Tôi không nghe rõ, bạn có thể nói lại không?'
            return {
                'transcription': '',
                'reply':         no_audio_reply,
                'step':          'COLLECT_INTENT',
                'done':          False,
                'appointment':   None,
                'audio':         self.tts_response(no_audio_reply) if speak else None,
            }

        # 2. Dialog
        resp = self.dialog(session_id, text, speak=speak)

        return {
            'transcription': text,
            'reply':         resp.reply,
            'step':          resp.step,
            'done':          resp.done,
            'appointment':   resp.appointment,
            'audio':         resp.__dict__.get('audio') if speak else None,
            'error':         resp.error,
        }
