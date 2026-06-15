from ai_voice_backend.dialog_action import ActionType, DialogAction
from ai_voice_backend.response_generator import ResponseGenerator


def _gen():
    # enabled=False → luôn dùng template, không gọi Gemini
    return ResponseGenerator(enabled=False)


def test_fallback_ask_date():
    out = _gen().generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert 'ngày' in out.lower()


def test_fallback_offer_slots_lists_times():
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'location': 'UBND Hoàn Kiếm',
                      'slots': ['08:00', '09:00']})
    out = _gen().generate(a, 'ngày mai', [])
    assert '08:00' in out and '09:00' in out


def test_fallback_booking_success_has_code_and_queue():
    a = DialogAction(ActionType.BOOKING_SUCCESS,
                     {'service': 'Làm căn cước', 'location': 'UBND Hoàn Kiếm',
                      'date': '01/07/2026', 'time': '09:00',
                      'code': 'AP-123', 'queue': '7'})
    out = _gen().generate(a, 'xác nhận', [])
    assert 'AP-123' in out and '7' in out


def test_fallback_answer_procedure_uses_snippets():
    a = DialogAction(ActionType.ANSWER_PROCEDURE,
                     {'snippets': ['Cần CMND cũ và sổ hộ khẩu.'],
                      'steer': 'Bạn muốn đặt lịch ngày nào?'})
    out = _gen().generate(a, 'cần giấy gì', [])
    assert 'CMND' in out
    assert 'ngày nào' in out


def test_fallback_answer_procedure_empty_snippets():
    a = DialogAction(ActionType.ANSWER_PROCEDURE,
                     {'snippets': [], 'steer': 'Bạn muốn làm thủ tục gì?'})
    out = _gen().generate(a, 'hỏi linh tinh', [])
    assert 'chưa có thông tin' in out.lower()
