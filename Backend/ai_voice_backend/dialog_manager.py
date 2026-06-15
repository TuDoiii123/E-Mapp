"""
Dialog Manager — State machine hội thoại đặt lịch hành chính multi-turn.

Luồng:
  GREETING
      ↓
  COLLECT_INTENT   → nhận biết thủ tục người dùng muốn làm
      ↓
  COLLECT_LOCATION → hỏi địa điểm (cơ quan/quận)
      ↓
  COLLECT_DATE     → hỏi ngày hẹn
      ↓
  SUGGEST_SLOTS    → gợi ý các khung giờ còn trống
      ↓
  CONFIRM          → xác nhận lại toàn bộ thông tin
      ↓
  DONE             → đặt lịch thành công, trả mã xác nhận

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


# ── Prompts per step ──────────────────────────────────────────────────────────

_PROMPTS = {
    Step.COLLECT_INTENT:   'Bạn muốn làm thủ tục gì? Ví dụ: làm căn cước công dân, đăng ký khai sinh.',
    Step.COLLECT_LOCATION: 'Bạn muốn đến cơ quan nào? Ví dụ: UBND quận Hoàn Kiếm, UBND huyện Thạch Thành.',
    Step.COLLECT_DATE:     'Bạn muốn đặt lịch ngày nào? (Ví dụ: ngày 25/07/2025 hoặc thứ 2 tuần sau)',
    Step.SUGGEST_SLOTS:    'Tôi đang kiểm tra các khung giờ còn trống cho bạn...',
    Step.CONFIRM:          'Bạn có muốn xác nhận đặt lịch không?',
}

_SERVICE_MAP = {
    # CCCD
    'căn cước': 'Làm căn cước công dân',
    'cccd':     'Làm căn cước công dân',
    'chứng minh nhân dân': 'Làm căn cước công dân',
    'định danh': 'Làm căn cước công dân',
    # Khai sinh
    'khai sinh': 'Đăng ký khai sinh',
    'sinh con':  'Đăng ký khai sinh',
    'trẻ sơ sinh': 'Đăng ký khai sinh',
    # Kết hôn
    'kết hôn':  'Đăng ký kết hôn',
    'hôn nhân': 'Đăng ký kết hôn',
    'đám cưới': 'Đăng ký kết hôn',
    # Hộ khẩu / Cư trú
    'hộ khẩu':   'Đăng ký hộ khẩu',
    'thường trú': 'Đăng ký thường trú',
    'tạm trú':    'Đăng ký tạm trú',
    'nhập khẩu':  'Đăng ký hộ khẩu',
    # Hộ chiếu
    'hộ chiếu': 'Làm hộ chiếu',
    'passport': 'Làm hộ chiếu',
    # GPLX
    'giấy phép lái xe': 'Cấp giấy phép lái xe',
    'bằng lái':  'Cấp giấy phép lái xe',
    'bằng lái xe': 'Cấp giấy phép lái xe',
    'gplx':      'Cấp giấy phép lái xe',
    # Đất đai
    'sổ đỏ':     'Cấp giấy chứng nhận quyền sử dụng đất',
    'sổ hồng':   'Cấp giấy chứng nhận quyền sử dụng đất',
    'đất đai':   'Cấp giấy chứng nhận quyền sử dụng đất',
    'quyền sử dụng đất': 'Cấp giấy chứng nhận quyền sử dụng đất',
}


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
                return DialogResponse(
                    reply='Lịch hẹn đã được đặt xong trước đó. '
                          'Nếu muốn đặt lịch mới, hãy cho tôi biết thủ tục bạn cần.',
                    step=Step.DONE,
                    done=True,
                    state=state,
                )

        # Phân tích NLU
        history = state.get('history', [])
        nlu     = self._nlu.analyze(user_text, history)
        log.info(f'[Dialog][{session_id}] step={state["step"]} intent={nlu.intent}')

        # Cập nhật entities vào state
        saved = Entities.from_dict(state.get('entities', {}))
        merged = saved.merge(nlu.entities)
        state['entities'] = merged.to_dict()

        # Thêm vào lịch sử hội thoại
        history.append({'role': 'user', 'content': user_text})
        state['history'] = history[-10:]  # giữ 10 lượt gần nhất

        # Xử lý intent CANCEL / DENY
        if nlu.intent == Intent.CANCEL:
            self._store.clear(session_id)
            return DialogResponse(reply='Đã hủy phiên đặt lịch. Khi cần bạn có thể bắt đầu lại.',
                                  step=Step.GREETING, state=state)

        # Điều hướng theo step hiện tại
        action = self._dispatch(session_id, state, nlu, user_text)
        from .response_generator import ResponseGenerator
        if not hasattr(self, '_nlg'):
            self._nlg = ResponseGenerator()
        reply = self._nlg.generate(action, user_text, state.get('history', []))

        # Lưu state
        history.append({'role': 'bot', 'content': reply})
        state['history'] = history[-10:]
        self._store.set(session_id, state)
        return DialogResponse(
            reply=reply, step=state['step'],
            done=(state['step'] == Step.DONE),
            appointment=state.get('appointment'),
            slots=state.get('suggested_slots', []), state=state)

    def start(self, session_id: str) -> DialogResponse:
        """Bắt đầu phiên mới."""
        state = self._init_state()
        self._store.set(session_id, state)
        return DialogResponse(
            reply=(
                'Xin chào! Tôi là trợ lý đặt lịch hành chính. '
                'Bạn muốn làm thủ tục gì? '
                'Ví dụ: "Tôi muốn làm căn cước công dân" hoặc "Đăng ký khai sinh".'
            ),
            step=Step.COLLECT_INTENT,
            state=state,
        )

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
