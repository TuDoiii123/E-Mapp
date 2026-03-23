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
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .nlu import NLUEngine, NLUResult, Entities, Intent
from .session_store import get_store

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
    'căn cước': 'Làm căn cước công dân',
    'cccd':     'Làm căn cước công dân',
    'khai sinh':'Đăng ký khai sinh',
    'hộ chiếu': 'Làm hộ chiếu',
    'passport': 'Làm hộ chiếu',
    'hộ khẩu':  'Đăng ký hộ khẩu',
    'giấy phép lái xe': 'Cấp giấy phép lái xe',
}


class DialogManager:
    """
    Quản lý hội thoại đặt lịch hành chính multi-turn.

    Mỗi session_id tương ứng với một cuộc hội thoại độc lập.
    State được persist qua SessionStore.
    """

    def __init__(self) -> None:
        self._nlu   = NLUEngine()
        self._store = get_store()

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
        response = self._dispatch(session_id, state, nlu, user_text)

        # Lưu state
        history.append({'role': 'bot', 'content': response.reply})
        state['history'] = history[-10:]
        self._store.set(session_id, state)

        return response

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

    def _dispatch(self, session_id: str, state: Dict, nlu: NLUResult,
                  user_text: str) -> DialogResponse:
        entities: Entities = Entities.from_dict(state['entities'])
        step = state['step']

        # ── COLLECT_INTENT ────────────────────────────────────────────────────
        if step == Step.COLLECT_INTENT:
            if not entities.service_type:
                return DialogResponse(reply=_PROMPTS[Step.COLLECT_INTENT],
                                      step=step, state=state)
            state['step'] = Step.COLLECT_LOCATION

        # ── COLLECT_LOCATION ──────────────────────────────────────────────────
        if state['step'] == Step.COLLECT_LOCATION:
            if not entities.location:
                return DialogResponse(reply=_PROMPTS[Step.COLLECT_LOCATION],
                                      step=state['step'], state=state)
            state['step'] = Step.COLLECT_DATE

        # ── COLLECT_DATE ──────────────────────────────────────────────────────
        if state['step'] == Step.COLLECT_DATE:
            if not entities.appointment_date:
                return DialogResponse(reply=_PROMPTS[Step.COLLECT_DATE],
                                      step=state['step'], state=state)
            state['step'] = Step.SUGGEST_SLOTS

        # ── SUGGEST_SLOTS ─────────────────────────────────────────────────────
        if state['step'] == Step.SUGGEST_SLOTS:
            slots = self._get_slots(entities.location, entities.appointment_date)
            if not slots:
                state['step'] = Step.COLLECT_DATE
                return DialogResponse(
                    reply=(f'Ngày {entities.appointment_date} tại {entities.location} '
                           f'không còn khung giờ trống. Bạn có thể chọn ngày khác không?'),
                    step=state['step'], state=state,
                )
            state['suggested_slots'] = slots
            state['step'] = Step.CONFIRM
            times = ', '.join(s[:5] for s in slots)
            reply = (
                f'Ngày {entities.appointment_date} tại {entities.location} '
                f'còn trống các khung giờ: {times}. '
                f'Bạn muốn chọn giờ nào?'
            )
            return DialogResponse(reply=reply, step=state['step'],
                                  slots=slots, state=state)

        # ── CONFIRM ───────────────────────────────────────────────────────────
        if state['step'] == Step.CONFIRM:
            slots = state.get('suggested_slots', [])

            # Nếu chưa có giờ, xử lý như chọn giờ
            if not entities.appointment_time:
                if not slots:
                    state['step'] = Step.SUGGEST_SLOTS
                    return self._dispatch(session_id, state, nlu, user_text)
                # Thử lấy giờ từ text trực tiếp
                entities_updated = Entities.from_dict(state['entities'])
                if not entities_updated.appointment_time:
                    times_text = ', '.join(s[:5] for s in slots)
                    return DialogResponse(
                        reply=f'Bạn vui lòng chọn một trong các khung giờ: {times_text}.',
                        step=state['step'], slots=slots, state=state,
                    )

            # Kiểm tra giờ chọn có trong danh sách gợi ý
            chosen_time = entities.appointment_time
            if slots and chosen_time not in slots:
                # Tìm slot khớp gần nhất (HH:MM)
                hhmm = chosen_time[:5]
                matched = next((s for s in slots if s.startswith(hhmm)), None)
                if matched:
                    chosen_time = matched
                    state['entities']['appointment_time'] = matched
                    entities = Entities.from_dict(state['entities'])
                else:
                    times_text = ', '.join(s[:5] for s in slots)
                    return DialogResponse(
                        reply=f'Khung giờ đó không còn trống. Vui lòng chọn lại: {times_text}.',
                        step=state['step'], slots=slots, state=state,
                    )

            # Xác nhận trước khi đặt — nếu chưa confirm
            if nlu.intent not in (Intent.CONFIRM,) and not state.get('confirmed'):
                d_str = self._fmt_date(entities.appointment_date)
                reply = (
                    f'Xác nhận thông tin đặt lịch:\n'
                    f'• Thủ tục: {entities.service_type}\n'
                    f'• Địa điểm: {entities.location}\n'
                    f'• Ngày: {d_str}\n'
                    f'• Giờ: {chosen_time[:5]}\n'
                    f'Bạn có xác nhận không? (Có / Không)'
                )
                state['confirmed'] = False
                return DialogResponse(reply=reply, step=state['step'], state=state)

            # Thực hiện đặt lịch
            state['confirmed'] = True
            return self._create_appointment(session_id, state, entities)

        return DialogResponse(reply='Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.',
                              step=step, state=state)

    # ── appointment creation ──────────────────────────────────────────────────

    def _create_appointment(self, session_id: str, state: Dict,
                            entities: Entities) -> DialogResponse:
        try:
            from services.appointments import create_appointment, suggest_slots

            svc_code = self._service_code(entities.service_type or '')
            agency_id = self._agency_id(entities.location or '')
            hhmm = (entities.appointment_time or '09:00:00')[:5]

            ok, appt, err = create_appointment({
                'agencyId':    agency_id,
                'serviceCode': svc_code,
                'date':        entities.appointment_date,
                'time':        hhmm,
                'phone':       entities.phone,
                'fullName':    entities.citizen_name or 'Người dân',
                'info':        entities.note or 'Đặt lịch qua voice AI',
            })
        except Exception as e:
            log.error(f'[Dialog] create_appointment error: {e}', exc_info=True)
            return DialogResponse(
                reply='Hệ thống đang gặp lỗi khi đặt lịch. Vui lòng thử lại sau.',
                step=Step.CONFIRM, error=str(e), state=state,
            )

        if not ok:
            return DialogResponse(
                reply=f'Không thể đặt lịch: {err}. Bạn có muốn chọn thời gian khác không?',
                step=Step.COLLECT_DATE, error=err, state=state,
            )

        state['step'] = Step.DONE
        d_str = self._fmt_date(entities.appointment_date)
        msg = (
            'Đặt lịch thành công! Thông tin chi tiết:\n'
            f'• Thủ tục : {entities.service_type}\n'
            f'• Địa điểm: {entities.location}\n'
            f'• Ngày giờ: {d_str} lúc {hhmm}\n'
            f'• Mã lịch : {appt.get("id", "N/A")}\n'
            f'• Số thứ tự: {appt.get("queueNumber", "N/A")}\n'
            'Hẹn gặp bạn tại cơ quan nhé!'
        )
        log.info(f'[Dialog][{session_id}] appointment created: {appt.get("id")}')
        return DialogResponse(reply=msg, step=Step.DONE, done=True,
                              appointment=appt, state=state)

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
        return state

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
