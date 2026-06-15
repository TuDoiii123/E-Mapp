"""
Dialog Manager — FSM hội thoại đặt lịch hành chính multi-turn.

FSM là deterministic và là nguồn chân lý duy nhất cho các thông tin đặt lịch
(slots, tạo lịch hẹn, mã xác nhận). Thay vì trả thẳng câu trả lời cố định,
FSM phát ra các `DialogAction` (loại hành động + dữ liệu) — `ResponseGenerator`
(NLG, dùng Gemini, có fallback theo template + guardrail hậu kiểm) sẽ chuyển
các action này thành câu trả lời tiếng Việt tự nhiên.

Các bước (Step) tham khảo:
  GREETING → COLLECT_INTENT → COLLECT_LOCATION → COLLECT_DATE
           → SUGGEST_SLOTS → CONFIRM → DONE

Bước hiện tại không còn được lưu cứng mà được `_recompute_step` suy ra lại từ
state (slots đã có) ở mỗi turn. `process()` còn định tuyến các lượt off-script:
câu hỏi về thủ tục → tra cứu RAG (`rag_bridge`), chào hỏi/small talk → trả lời
small talk, và phát hiện đổi ý để tái tính lại bước phù hợp qua `_recompute_step`.

Tại mỗi bước, Gemini có thể trích xuất nhiều entities cùng lúc
(vd: "Tôi muốn làm CCCD ngày mai 9h tại UBND Hoàn Kiếm" → skip thẳng đến CONFIRM).
"""
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .nlu import NLUEngine, NLUResult, Entities, Intent
from .session_store import get_store
from .dialog_action import ActionType, DialogAction
from .rag_bridge import search as rag_search

log = get_logger('voice.dialog')


# ── Steps ─────────────────────────────────────────────────────────────────────

class Step:
    GREETING        = 'GREETING'
    COLLECT_INTENT  = 'COLLECT_INTENT'
    COLLECT_LOCATION= 'COLLECT_LOCATION'
    COLLECT_DATE    = 'COLLECT_DATE'
    SUGGEST_SLOTS   = 'SUGGEST_SLOTS'
    CONFIRM         = 'CONFIRM'
    DONE            = 'DONE'


# ── Dialog Response ───────────────────────────────────────────────────────────

@dataclass
class DialogResponse:
    reply:       str
    step:        str
    done:        bool        = False
    appointment: Optional[Dict] = None
    slots:       List[str]   = field(default_factory=list)
    state:       Optional[Dict] = None
    error:       Optional[str]  = None


_SESSION_TTL_SECONDS = int(os.getenv('VOICE_SESSION_TTL', '3600'))  # 1 giờ mặc định


class DialogManager:
    """
    Quản lý hội thoại đặt lịch hành chính multi-turn.

    Mỗi session_id tương ứng với một cuộc hội thoại độc lập.
    State được persist qua SessionStore với TTL tự động dọn.
    """

    def __init__(self) -> None:
        self._nlu   = NLUEngine()
        self._store = get_store()
        self._cleanup_expired()

    # ── public ────────────────────────────────────────────────────────────────

    def process(self, session_id: str, user_text: str) -> DialogResponse:
        """
        Xử lý một lượt hội thoại.

        Returns DialogResponse với reply text và trạng thái hiện tại.
        """
        state = self._load_state(session_id)

        # Cho phép restart nếu đã DONE
        if state['step'] == Step.DONE:
            import re
            if re.search(r'(đặt lịch|thủ tục|căn cước|khai sinh|hộ chiếu|hồ sơ)', user_text, re.I):
                state = self._init_state()
            else:
                history = state.get('history', [])
                history.append({'role': 'user', 'content': user_text})
                return self._finish(session_id, state,
                                    DialogAction(ActionType.ALREADY_DONE),
                                    user_text, history)

        # Phân tích NLU
        history = state.get('history', [])
        nlu     = self._nlu.analyze(user_text, history)
        log.info(f'[Dialog][{session_id}] step={state["step"]} intent={nlu.intent}')

        # Cập nhật entities vào state — phát hiện đổi ý (đổi ngày/địa điểm/dịch vụ)
        saved  = Entities.from_dict(state.get('entities', {}))
        new_e  = nlu.entities
        changed_fields = ('appointment_date', 'location', 'service_type')
        changed = any(getattr(new_e, fld) and getattr(new_e, fld) != getattr(saved, fld)
                      for fld in changed_fields)
        merged = saved.merge(new_e)
        state['entities'] = merged.to_dict()
        if changed:
            state['suggested_slots'] = []
            state['confirmed'] = False
            if not new_e.appointment_time:
                state['entities']['appointment_time'] = None
        # Luôn đồng bộ step với entity hiện có (off-script không đẩy bước nhưng vẫn cần đúng step)
        state['step'] = self._recompute_step(
            Entities.from_dict(state['entities']), state)

        # Thêm vào lịch sử hội thoại
        history.append({'role': 'user', 'content': user_text})
        state['history'] = history[-10:]  # giữ 10 lượt gần nhất

        # Xử lý intent CANCEL — câu hủy đi qua NLG, không persist (đã xóa phiên)
        if nlu.intent == Intent.CANCEL:
            reply = self._get_nlg().generate(
                DialogAction(ActionType.CANCELLED), user_text, history)
            self._store.clear(session_id)
            state['step'] = Step.GREETING   # đồng bộ step trả về với state
            return DialogResponse(reply=reply, step=Step.GREETING, state=state)

        # Off-script: hỏi thủ tục/dịch vụ hoặc tán gẫu, không đẩy bước booking
        if nlu.intent in (Intent.QUERY_PROCEDURE, Intent.QUERY_SERVICE):
            snippets = rag_search(user_text)
            action = DialogAction(ActionType.ANSWER_PROCEDURE,
                                  {'snippets': snippets,
                                   'steer': self._steer_prompt(state)})
            return self._finish(session_id, state, action, user_text, history)

        if nlu.intent in (Intent.GREETING, Intent.SMALL_TALK):
            action = DialogAction(ActionType.SMALL_TALK,
                                  {'steer': self._steer_prompt(state)})
            return self._finish(session_id, state, action, user_text, history)

        # Điều hướng theo step hiện tại
        action = self._dispatch(session_id, state, nlu, user_text)
        return self._finish(session_id, state, action, user_text, history)

    def start(self, session_id: str) -> DialogResponse:
        """Bắt đầu phiên mới — câu chào đi qua NLG (tự nhiên hơn)."""
        state = self._init_state()
        return self._finish(session_id, state, DialogAction(ActionType.GREET),
                            '', state['history'])

    def reset(self, session_id: str) -> None:
        self._store.clear(session_id)

    # ── dispatch ──────────────────────────────────────────────────────────────

    def _recompute_step(self, entities: Entities, state: Dict) -> str:
        if not entities.service_type:
            return Step.COLLECT_INTENT
        if not entities.location:
            return Step.COLLECT_LOCATION
        if not entities.appointment_date:
            return Step.COLLECT_DATE
        if not state.get('suggested_slots'):
            return Step.SUGGEST_SLOTS
        if not entities.appointment_time:
            return Step.SUGGEST_SLOTS
        return Step.CONFIRM

    def _steer_prompt(self, state: Dict) -> str:
        entities = Entities.from_dict(state['entities'])
        step = self._recompute_step(entities, state)
        return {
            Step.COLLECT_INTENT:   'Bạn muốn làm thủ tục gì?',
            Step.COLLECT_LOCATION: 'Bạn muốn đến cơ quan nào?',
            Step.COLLECT_DATE:     'Bạn muốn đặt lịch ngày nào?',
            Step.SUGGEST_SLOTS:    'Mình kiểm tra khung giờ giúp bạn nhé?',
            Step.CONFIRM:          'Bạn xác nhận đặt lịch chứ?',
        }.get(step, 'Mình giúp bạn đặt lịch nhé?')

    def _get_nlg(self):
        """Lazy-init ResponseGenerator (NLG). Test có thể gán sẵn self._nlg."""
        if getattr(self, '_nlg', None) is None:
            from .response_generator import ResponseGenerator
            self._nlg = ResponseGenerator()
        return self._nlg

    def _finish(self, session_id: str, state: Dict, action: DialogAction,
                user_text: str, history: List[Dict]) -> DialogResponse:
        reply = self._get_nlg().generate(action, user_text, history)
        history.append({'role': 'bot', 'content': reply})
        state['history'] = history[-10:]
        self._store.set(session_id, state)
        return DialogResponse(
            reply=reply, step=state['step'],
            done=(state['step'] == Step.DONE),
            appointment=state.get('appointment'),
            slots=state.get('suggested_slots', []), state=state)

    def _dispatch(self, session_id: str, state: Dict, nlu: NLUResult,
                  user_text: str) -> DialogAction:
        entities: Entities = Entities.from_dict(state['entities'])
        state['step'] = self._recompute_step(entities, state)
        step = state['step']

        if step == Step.COLLECT_INTENT:
            return DialogAction(ActionType.ASK_INTENT)
        if step == Step.COLLECT_LOCATION:
            return DialogAction(ActionType.ASK_LOCATION)
        if step == Step.COLLECT_DATE:
            return DialogAction(ActionType.ASK_DATE)

        if step == Step.SUGGEST_SLOTS:
            slots = self._get_slots(entities.location, entities.appointment_date)
            d_str = self._fmt_date(entities.appointment_date)
            if not slots:
                state['suggested_slots'] = []
                return DialogAction(ActionType.NO_SLOTS,
                                    {'date': d_str, 'location': entities.location})
            state['suggested_slots'] = slots
            short = [s[:5] for s in slots]
            return DialogAction(ActionType.OFFER_SLOTS,
                                {'date': d_str, 'location': entities.location,
                                 'slots': short})

        if step == Step.CONFIRM:
            slots = state.get('suggested_slots', [])
            short = [s[:5] for s in slots]
            chosen = entities.appointment_time
            if chosen and slots and chosen not in slots:
                matched = next((s for s in slots if s.startswith(chosen[:5])), None)
                if matched:
                    chosen = matched
                    state['entities']['appointment_time'] = matched
                    entities = Entities.from_dict(state['entities'])
                else:
                    return DialogAction(ActionType.SLOT_TAKEN, {'slots': short})
            if nlu.intent != Intent.CONFIRM and not state.get('confirmed'):
                return DialogAction(ActionType.CONFIRM_DETAILS, {
                    'service': entities.service_type, 'location': entities.location,
                    'date': self._fmt_date(entities.appointment_date),
                    'time': (chosen or '')[:5]})
            state['confirmed'] = True
            return self._create_appointment_action(session_id, state, entities)

        return DialogAction(ActionType.ASK_INTENT)

    # ── appointment creation ──────────────────────────────────────────────────

    def _create_appointment_action(self, session_id: str, state: Dict,
                                    entities: Entities) -> DialogAction:
        try:
            from services.appointments import create_appointment
            svc_code = self._service_code(entities.service_type or '')
            agency_id = self._agency_id(entities.location or '')
            raw_time = entities.appointment_time or '09:00:00'
            from datetime import datetime as _dt
            for fmt in ('%H:%M:%S', '%H:%M', '%H'):
                try:
                    hhmm = _dt.strptime(raw_time, fmt).strftime('%H:%M'); break
                except ValueError:
                    continue
            else:
                hhmm = raw_time[:5] if len(raw_time) >= 5 else '09:00'
            ok, appt, err = create_appointment({
                'agencyId': agency_id, 'serviceCode': svc_code,
                'date': entities.appointment_date, 'time': hhmm,
                'phone': entities.phone, 'fullName': entities.citizen_name or 'Người dân',
                'info': entities.note or 'Đặt lịch qua voice AI'})
        except Exception as e:
            log.error(f'[Dialog] create_appointment error: {e}', exc_info=True)
            state['step'] = Step.CONFIRM
            return DialogAction(ActionType.BOOKING_ERROR, {'error': str(e)})
        if not ok:
            state['step'] = Step.COLLECT_DATE
            state['suggested_slots'] = []
            return DialogAction(ActionType.BOOKING_ERROR, {'error': err or 'lỗi'})
        state['step'] = Step.DONE
        state['appointment'] = appt
        log.info(f'[Dialog][{session_id}] appointment created: {appt.get("id")}')
        return DialogAction(ActionType.BOOKING_SUCCESS, {
            'service': entities.service_type, 'location': entities.location,
            'date': self._fmt_date(entities.appointment_date), 'time': hhmm,
            'code': appt.get('id', 'N/A'), 'queue': appt.get('queueNumber', 'N/A')})

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_slots(self, location: Optional[str], date: Optional[str]) -> List[str]:
        try:
            from services.appointments import suggest_slots
            agency_id = self._agency_id(location or '')
            return suggest_slots(date or '', agency_id)
        except Exception:
            # fallback: trả về các slot mặc định trong giờ hành chính
            return ['08:00:00', '09:00:00', '10:00:00', '14:00:00', '15:00:00']

    def _load_state(self, session_id: str) -> Dict:
        state = self._store.get(session_id)
        if state is None:
            state = self._init_state()
            self._store.set(session_id, state)
        else:
            # Kiểm tra TTL — session quá cũ thì reset
            try:
                created = datetime.fromisoformat(state.get('created_at', ''))
                if (datetime.now() - created).total_seconds() > _SESSION_TTL_SECONDS:
                    self._store.clear(session_id)
                    state = self._init_state()
                    self._store.set(session_id, state)
            except Exception:
                pass
        return state

    def _cleanup_expired(self) -> None:
        """Xóa tất cả sessions đã quá TTL — chạy khi khởi tạo."""
        try:
            now = datetime.now()
            to_delete = []
            for sid, state in self._store.all().items():
                try:
                    created = datetime.fromisoformat(state.get('created_at', ''))
                    if (now - created).total_seconds() > _SESSION_TTL_SECONDS:
                        to_delete.append(sid)
                except Exception:
                    to_delete.append(sid)
            for sid in to_delete:
                self._store.clear(sid)
            if to_delete:
                log.info(f'[Dialog] Cleaned up {len(to_delete)} expired sessions')
        except Exception as e:
            log.debug(f'[Dialog] Session cleanup error: {e}')

    @staticmethod
    def _init_state() -> Dict:
        return {
            'step':            Step.COLLECT_INTENT,
            'entities':        Entities().to_dict(),
            'suggested_slots': [],
            'confirmed':       False,
            'history':         [],
            'created_at':      datetime.now().isoformat(),
        }

    @staticmethod
    def _service_code(service: str) -> str:
        s = service.lower()
        if 'căn cước' in s or 'cccd' in s: return 'CCCD'
        if 'khai sinh' in s:               return 'KHAISINH'
        if 'hộ chiếu' in s:               return 'PASSPORT'
        if 'hộ khẩu' in s:                return 'HOKHAU'
        if 'giấy phép lái xe' in s:        return 'GPLX'
        return 'SERVICE'

    @staticmethod
    def _agency_id(location: str) -> str:
        loc = location.lower()
        if 'ubnd' in loc or 'ủy ban' in loc:
            import re
            m = re.search(r'(?:quận|huyện|phường|xã)\s+([\w\s]+)', loc)
            if m:
                slug = m.group(1).strip().replace(' ', '-')
                return f'ubnd-{slug}'
            return 'ubnd-001'
        return 'agency-001'

    @staticmethod
    def _fmt_date(date_iso: Optional[str]) -> str:
        if not date_iso:
            return 'chưa xác định'
        try:
            return datetime.strptime(date_iso, '%Y-%m-%d').strftime('%d/%m/%Y')
        except Exception:
            return date_iso
