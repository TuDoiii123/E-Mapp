from ai_voice_backend.nlu import NLUEngine, Intent


def test_query_procedure_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'QUERY_PROCEDURE', 'entities': {}})
    assert res.intent == Intent.QUERY_PROCEDURE


def test_greeting_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'GREETING', 'entities': {}})
    assert res.intent == Intent.GREETING


def test_unknown_intent_falls_back():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'XYZ', 'entities': {}})
    assert res.intent == Intent.UNKNOWN


from ai_voice_backend.dialog_manager import DialogManager, Step
from ai_voice_backend.nlu import NLUResult, Entities
from ai_voice_backend.dialog_action import ActionType


def _dm():
    return DialogManager()


def test_recompute_step_missing_service():
    dm = _dm()
    e = Entities()
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.COLLECT_INTENT


def test_recompute_step_missing_date():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND Hoàn Kiếm')
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.COLLECT_DATE


def test_recompute_step_ready_for_slots_when_no_cached_slots():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND',
                 appointment_date='2026-07-01', appointment_time='09:00:00')
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.SUGGEST_SLOTS


def test_recompute_step_confirm_when_all_present():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND',
                 appointment_date='2026-07-01', appointment_time='09:00:00')
    assert dm._recompute_step(e, {'suggested_slots': ['09:00:00']}) == Step.CONFIRM


def test_dispatch_ask_date_returns_action():
    dm = _dm()
    state = dm._init_state()
    state['entities'] = Entities(service_type='Làm căn cước',
                                 location='UBND Hoàn Kiếm').to_dict()
    nlu = NLUResult(intent=Intent.BOOK_APPOINTMENT, entities=Entities())
    action = dm._dispatch('s1', state, nlu, 'tôi muốn làm căn cước ở Hoàn Kiếm')
    assert action.type == ActionType.ASK_DATE


from ai_voice_backend import dialog_manager as DM


def _force_nlu(dm, intent, entities):
    dm._nlu.analyze = lambda text, history=None: NLUResult(intent=intent, entities=entities)


def test_procedure_question_keeps_step_and_uses_rag(monkeypatch):
    from ai_voice_backend.response_generator import ResponseGenerator
    monkeypatch.setattr(DM, 'rag_search', lambda q: ['Cần CMND cũ và sổ hộ khẩu.'],
                        raising=False)
    dm = DialogManager()
    dm._nlg = ResponseGenerator(enabled=False)   # template, không gọi Gemini
    sid = 'p1'
    dm.reset(sid)
    # đã có service → bước hiện tại phải là hỏi địa điểm
    st = dm._init_state(); st['entities'] = Entities(service_type='Làm căn cước').to_dict()
    dm._store.set(sid, st)
    _force_nlu(dm, Intent.QUERY_PROCEDURE, Entities())
    resp = dm.process(sid, 'làm căn cước cần giấy gì')
    # vẫn ở COLLECT_LOCATION (không bị đẩy bước), reply có nội dung RAG
    assert dm._store.get(sid)['step'] == Step.COLLECT_LOCATION
    assert 'CMND' in resp.reply


def test_change_of_mind_resets_and_refetches(monkeypatch):
    from ai_voice_backend.response_generator import ResponseGenerator
    dm = DialogManager()
    dm._nlg = ResponseGenerator(enabled=False)
    monkeypatch.setattr(dm, '_get_slots', lambda loc, date: ['08:00:00'])  # slot mới
    sid = 'c1'; dm.reset(sid)
    st = dm._init_state()
    st['entities'] = Entities(service_type='Làm căn cước', location='UBND',
                              appointment_date='2026-07-01',
                              appointment_time='09:00:00').to_dict()
    st['suggested_slots'] = ['09:00:00']; st['confirmed'] = True
    st['step'] = Step.CONFIRM
    dm._store.set(sid, st)
    # người dùng đổi sang ngày khác → phải reset confirm + lấy slot mới
    _force_nlu(dm, Intent.BOOK_APPOINTMENT, Entities(appointment_date='2026-07-05'))
    dm.process(sid, 'à cho mình đổi sang ngày mùng 5')
    after = dm._store.get(sid)
    assert after['confirmed'] is False
    assert after['entities']['appointment_date'] == '2026-07-05'
    assert after['suggested_slots'] == ['08:00:00']   # slot cũ '09:00:00' đã bị thay
    assert after['step'] == Step.SUGGEST_SLOTS


def test_full_booking_flow_offline(monkeypatch):
    """NLU + NLG bị mock; kiểm tra FSM dẫn dắt đúng tới CONFIRM."""
    dm = DialogManager()
    sid = 'flow1'; dm.reset(sid)
    # ép NLG dùng template (tắt Gemini) để output deterministic
    from ai_voice_backend.response_generator import ResponseGenerator
    dm._nlg = ResponseGenerator(enabled=False)
    # ép suggest_slots trả về cố định
    monkeypatch.setattr(dm, '_get_slots',
                        lambda loc, date: ['08:00:00', '09:00:00'])

    # turn 1: cung cấp đủ service + location + date
    _force_nlu(dm, Intent.BOOK_APPOINTMENT,
               Entities(service_type='Làm căn cước', location='UBND Hoàn Kiếm',
                        appointment_date='2026-07-01'))
    r1 = dm.process(sid, 'làm căn cước ở Hoàn Kiếm ngày 1 tháng 7')
    assert '08:00' in r1.reply and '09:00' in r1.reply   # OFFER_SLOTS

    # turn 2: chọn giờ
    _force_nlu(dm, Intent.BOOK_APPOINTMENT,
               Entities(appointment_time='09:00:00'))
    r2 = dm.process(sid, 'chọn 9 giờ')
    assert 'xác nhận' in r2.reply.lower()                # CONFIRM_DETAILS
