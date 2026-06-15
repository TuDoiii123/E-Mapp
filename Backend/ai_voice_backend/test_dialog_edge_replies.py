"""Test các câu 'rìa' (chào / hủy / đã đặt xong) đi qua NLG thay vì chuỗi cứng."""
from ai_voice_backend.dialog_manager import DialogManager, Step
from ai_voice_backend.nlu import NLUResult, Entities, Intent
from ai_voice_backend.response_generator import ResponseGenerator


def _dm():
    dm = DialogManager()
    dm._nlg = ResponseGenerator(enabled=False)  # template → output deterministic
    return dm


def _force_nlu(dm, intent, entities=None):
    dm._nlu.analyze = lambda text, history=None: NLUResult(
        intent=intent, entities=entities or Entities())


def test_start_reply_via_nlg_template():
    dm = _dm()
    resp = dm.start('s1')
    assert resp.step == Step.COLLECT_INTENT
    assert resp.done is False
    assert 'thủ tục' in resp.reply.lower()             # GREET template
    # câu chào được lưu vào lịch sử
    assert dm._store.get('s1')['history'][-1]['role'] == 'bot'


def test_already_done_via_nlg_template():
    dm = _dm()
    sid = 'd1'; dm.reset(sid)
    st = dm._init_state(); st['step'] = Step.DONE
    dm._store.set(sid, st)
    _force_nlu(dm, Intent.UNKNOWN)
    resp = dm.process(sid, 'cảm ơn nhé')
    assert resp.done is True
    assert resp.step == Step.DONE
    assert 'trước đó' in resp.reply.lower()             # ALREADY_DONE template


def test_cancel_via_nlg_and_step_consistent():
    dm = _dm()
    sid = 'x1'; dm.reset(sid)
    st = dm._init_state()
    st['entities'] = Entities(service_type='Làm căn cước', location='UBND').to_dict()
    dm._store.set(sid, st)
    _force_nlu(dm, Intent.CANCEL)
    resp = dm.process(sid, 'thôi hủy đi')
    assert 'hủy' in resp.reply.lower()                  # CANCELLED template
    assert resp.step == Step.GREETING
    assert resp.state['step'] == Step.GREETING          # không còn lệch step
    assert dm._store.get(sid) is None                   # phiên đã xóa
