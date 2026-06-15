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
