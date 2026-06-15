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


from ai_voice_backend.response_generator import ResponseGenerator as _RG


def test_guardrail_appends_missing_booking_code():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.BOOKING_SUCCESS,
                     {'service': 'Làm căn cước', 'location': 'UBND',
                      'date': '01/07/2026', 'time': '09:00',
                      'code': 'AP-999', 'queue': '12'})
    # giả lập câu LLM bỏ sót mã + số thứ tự
    fixed = g._guardrail(a, 'Đặt lịch thành công, hẹn gặp bạn!')
    assert 'AP-999' in fixed and '12' in fixed


def test_guardrail_appends_missing_slots():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'location': 'UBND',
                      'slots': ['08:00', '09:00']})
    fixed = g._guardrail(a, 'Còn vài khung giờ trống bạn nhé.')
    assert '08:00' in fixed and '09:00' in fixed


def test_guardrail_noop_when_facts_present():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.BOOKING_SUCCESS, {'code': 'AP-1', 'queue': '3'})
    reply = 'Xong rồi, mã AP-1, số thứ tự 3 nhé.'
    assert g._guardrail(a, reply) == reply


def test_uses_gemini_reply_when_enabled(monkeypatch):
    g = _RG(enabled=True)
    monkeypatch.setattr(g, '_call_gemini',
                        lambda action, user_text, history: 'Dạ, bạn muốn ngày nào ạ?')
    out = g.generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert out == 'Dạ, bạn muốn ngày nào ạ?'


def test_falls_back_when_gemini_returns_empty(monkeypatch):
    g = _RG(enabled=True)
    monkeypatch.setattr(g, '_call_gemini', lambda action, user_text, history: '')
    out = g.generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert 'ngày' in out.lower()


def test_build_prompt_includes_facts_and_user_text():
    g = _RG(enabled=True)
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'slots': ['08:00']})
    prompt = g._build_prompt(a, 'ngày mai nhé', [])
    assert '08:00' in prompt and 'ngày mai nhé' in prompt
    assert 'OFFER_SLOTS' in prompt
