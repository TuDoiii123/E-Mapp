"""
ResponseGenerator (NLG) — biến DialogAction + facts thành câu tiếng Việt tự nhiên.

Thứ tự ưu tiên:
  1. enabled=False hoặc Gemini lỗi → template fallback (deterministic).
  2. Gemini OK → câu tự nhiên, sau đó qua guardrail hậu kiểm.

Guardrail: facts được bơm vào prompt; số/mã/giờ quan trọng bị thiếu trong câu LLM
sẽ được nối thêm dòng deterministic (thêm ở task sau).
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .dialog_action import ActionType, DialogAction
from .config import VOICE_NLG_ENABLED

log = get_logger('voice.nlg')


class ResponseGenerator:
    def __init__(self, enabled: Optional[bool] = None) -> None:
        self._enabled = VOICE_NLG_ENABLED if enabled is None else enabled
        self._model = None

    def generate(self, action: DialogAction, user_text: str,
                 history: Optional[List[Dict]] = None) -> str:
        reply = ''
        if self._enabled:
            reply = self._call_gemini(action, user_text, history or [])
        if not reply:
            reply = self._fallback(action)
        return reply

    # ── template fallback ──────────────────────────────────────────────────
    def _fallback(self, action: DialogAction) -> str:
        f = action.facts
        t = action.type
        if t == ActionType.GREET:
            return ('Xin chào! Tôi là trợ lý đặt lịch hành chính. '
                    'Bạn muốn làm thủ tục gì?')
        if t == ActionType.ASK_INTENT:
            return 'Bạn muốn làm thủ tục gì? Ví dụ: làm căn cước, đăng ký khai sinh.'
        if t == ActionType.ASK_LOCATION:
            return 'Bạn muốn đến cơ quan nào? Ví dụ: UBND quận Hoàn Kiếm.'
        if t == ActionType.ASK_DATE:
            return 'Bạn muốn đặt lịch ngày nào?'
        if t == ActionType.OFFER_SLOTS:
            times = ', '.join(f.get('slots', []))
            return (f"Ngày {f.get('date','')} tại {f.get('location','')} còn trống "
                    f"các khung giờ: {times}. Bạn muốn chọn giờ nào?")
        if t == ActionType.NO_SLOTS:
            return (f"Ngày {f.get('date','')} tại {f.get('location','')} không còn "
                    f"khung giờ trống. Bạn chọn ngày khác nhé?")
        if t == ActionType.ASK_TIME_AGAIN:
            times = ', '.join(f.get('slots', []))
            return f'Bạn vui lòng chọn một trong các khung giờ: {times}.'
        if t == ActionType.SLOT_TAKEN:
            times = ', '.join(f.get('slots', []))
            return f'Khung giờ đó không còn trống. Vui lòng chọn lại: {times}.'
        if t == ActionType.CONFIRM_DETAILS:
            return (f"Xác nhận: {f.get('service','')} tại {f.get('location','')}, "
                    f"ngày {f.get('date','')} lúc {f.get('time','')}. "
                    f"Bạn xác nhận chứ? (Có / Không)")
        if t == ActionType.BOOKING_SUCCESS:
            return (f"Đặt lịch thành công! {f.get('service','')} tại "
                    f"{f.get('location','')}, ngày {f.get('date','')} lúc {f.get('time','')}. "
                    f"Mã lịch {f.get('code','')}, số thứ tự {f.get('queue','')}. "
                    f"Hẹn gặp bạn nhé!")
        if t == ActionType.BOOKING_ERROR:
            return (f"Xin lỗi, chưa đặt được lịch: {f.get('error','')}. "
                    f"Bạn muốn thử thời gian khác không?")
        if t == ActionType.ANSWER_PROCEDURE:
            snippets = f.get('snippets', [])
            steer = f.get('steer', '')
            if not snippets:
                return ('Xin lỗi, mình chưa có thông tin về việc đó. ' + steer).strip()
            return (snippets[0] + ' ' + steer).strip()
        if t == ActionType.SMALL_TALK:
            return ('Mình ở đây để giúp bạn đặt lịch hành chính. '
                    + f.get('steer', '')).strip()
        if t == ActionType.CANCELLED:
            return 'Đã hủy phiên đặt lịch. Khi cần bạn cứ bắt đầu lại nhé.'
        if t == ActionType.ALREADY_DONE:
            return ('Lịch hẹn đã đặt xong trước đó. Nếu muốn đặt lịch mới, '
                    'hãy cho mình biết thủ tục bạn cần.')
        return 'Xin lỗi, đã có lỗi xảy ra. Bạn thử lại giúp mình nhé.'

    # ── Gemini (đặt stub ở task sau) ─────────────────────────────────────────
    def _call_gemini(self, action: DialogAction, user_text: str,
                     history: List[Dict]) -> str:
        return ''  # tạm thời: chưa gọi LLM (task sau sẽ cài)
