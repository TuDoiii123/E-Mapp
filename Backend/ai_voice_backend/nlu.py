"""
NLU Engine — Natural Language Understanding tiếng Việt.

Dùng Gemini để:
  1. Phát hiện intent (BookAppointment, QueryService, Cancel, Confirm, Deny, Unknown)
  2. Trích xuất entities (service_type, location, date, time, phone, name, note)
  3. Phân tích hội thoại multi-turn với context lịch sử

Fallback regex khi Gemini không khả dụng.
"""
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .config import GEMINI_API_KEY, GEMINI_MODEL

log = get_logger('voice.nlu')


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Entities:
    service_type:     Optional[str] = None
    location:         Optional[str] = None
    appointment_date: Optional[str] = None   # YYYY-MM-DD
    appointment_time: Optional[str] = None   # HH:MM:SS
    phone:            Optional[str] = None
    citizen_name:     Optional[str] = None
    note:             Optional[str] = None

    def merge(self, other: 'Entities') -> 'Entities':
        """Ghép entities mới vào entities hiện tại (không ghi đè nếu đã có)."""
        return Entities(
            service_type     = other.service_type     or self.service_type,
            location         = other.location         or self.location,
            appointment_date = other.appointment_date or self.appointment_date,
            appointment_time = other.appointment_time or self.appointment_time,
            phone            = other.phone            or self.phone,
            citizen_name     = other.citizen_name     or self.citizen_name,
            note             = other.note             or self.note,
        )

    def missing(self) -> List[str]:
        """Danh sách trường bắt buộc còn thiếu."""
        required = ['service_type', 'location', 'appointment_date', 'appointment_time']
        return [k for k in required if not getattr(self, k)]

    def to_dict(self) -> Dict:
        return {
            'service_type':     self.service_type,
            'location':         self.location,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'phone':            self.phone,
            'citizen_name':     self.citizen_name,
            'note':             self.note,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> 'Entities':
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class NLUResult:
    intent:   str          # BOOK_APPOINTMENT | QUERY_SERVICE | CONFIRM | DENY | CANCEL | UNKNOWN
    entities: Entities     = field(default_factory=Entities)
    raw:      Dict[str, Any] = field(default_factory=dict)


# ── Intent labels ─────────────────────────────────────────────────────────────

class Intent:
    BOOK_APPOINTMENT = 'BOOK_APPOINTMENT'
    QUERY_SERVICE    = 'QUERY_SERVICE'
    CONFIRM          = 'CONFIRM'
    DENY             = 'DENY'
    CANCEL           = 'CANCEL'
    UNKNOWN          = 'UNKNOWN'


# ── NLU Engine ────────────────────────────────────────────────────────────────

class NLUEngine:
    """
    Phân tích ngôn ngữ tự nhiên tiếng Việt.

    Gemini được dùng cho:
      - Phát hiện intent chính xác
      - Trích xuất entities chuẩn hóa (ngày YYYY-MM-DD, giờ HH:MM:SS)
      - Xử lý biểu đạt tự nhiên ("ngày mai", "sáng sớm", "quận Hoàn Kiếm")

    Regex fallback khi Gemini không khả dụng.
    """

    _SYSTEM_PROMPT = (
        'Bạn là AI phân tích ngôn ngữ tự nhiên tiếng Việt cho hệ thống đặt lịch hành chính công.\n'
        'Nhiệm vụ: phân tích câu người dùng và trả về JSON có cấu trúc.\n\n'
        'Schema bắt buộc:\n'
        '{\n'
        '  "intent": "<BOOK_APPOINTMENT|QUERY_SERVICE|CONFIRM|DENY|CANCEL|UNKNOWN>",\n'
        '  "entities": {\n'
        '    "service_type":     "<tên thủ tục hoặc null>",\n'
        '    "location":         "<tên cơ quan/quận/huyện hoặc null>",\n'
        '    "appointment_date": "<YYYY-MM-DD hoặc null>",\n'
        '    "appointment_time": "<HH:MM:SS hoặc null>",\n'
        '    "phone":            "<số điện thoại hoặc null>",\n'
        '    "citizen_name":     "<họ tên hoặc null>",\n'
        '    "note":             "<ghi chú hoặc null>"\n'
        '  }\n'
        '}\n\n'
        'Quy tắc:\n'
        '- Ngày tương đối ("ngày mai", "thứ 2") → chuyển sang YYYY-MM-DD so với hôm nay.\n'
        '- Giờ ("9 giờ", "9h", "9:00") → HH:MM:SS.\n'
        '- Chỉ trả JSON thuần, không giải thích.\n'
    )

    def __init__(self) -> None:
        self._model = None

    def analyze(self, text: str, history: Optional[List[Dict]] = None) -> NLUResult:
        """
        Phân tích câu người dùng.

        Parameters
        ----------
        text    : câu người dùng
        history : danh sách lượt hội thoại trước [{role, content}]
        """
        if not text:
            return NLUResult(intent=Intent.UNKNOWN)

        raw = self._call_gemini(text, history or [])

        if raw:
            return self._parse_gemini_response(raw)

        # Regex fallback
        return self._regex_fallback(text)

    def extract_entities_only(self, text: str, context: Optional[Dict] = None) -> Entities:
        """Chỉ trích entities, không cần xác định intent."""
        result = self.analyze(text)
        return result.entities

    # ── Gemini call ───────────────────────────────────────────────────────────

    def _call_gemini(self, text: str, history: List[Dict]) -> Dict:
        if not GEMINI_API_KEY:
            return {}
        try:
            import google.generativeai as genai
            from datetime import date

            if self._model is None:
                genai.configure(api_key=GEMINI_API_KEY)
                self._model = genai.GenerativeModel(GEMINI_MODEL)

            today_str = date.today().isoformat()
            history_text = ''
            if history:
                lines = [f'  [{h["role"]}]: {h["content"]}' for h in history[-4:]]
                history_text = 'Lịch sử hội thoại:\n' + '\n'.join(lines) + '\n\n'

            prompt = (
                f'{self._SYSTEM_PROMPT}\n'
                f'Hôm nay: {today_str}\n\n'
                f'{history_text}'
                f'Câu người dùng: "{text}"\n\n'
                'Trả lời JSON:'
            )

            resp = self._model.generate_content(prompt)
            raw  = (getattr(resp, 'text', None) or '').strip()
            m    = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception as e:
            log.debug(f'[NLU][Gemini] {e}')
        return {}

    def _parse_gemini_response(self, raw: Dict) -> NLUResult:
        intent_str = (raw.get('intent') or Intent.UNKNOWN).upper()
        valid_intents = {
            Intent.BOOK_APPOINTMENT, Intent.QUERY_SERVICE,
            Intent.CONFIRM, Intent.DENY, Intent.CANCEL, Intent.UNKNOWN,
        }
        intent = intent_str if intent_str in valid_intents else Intent.UNKNOWN

        ent_raw  = raw.get('entities') or {}
        entities = Entities(
            service_type     = ent_raw.get('service_type')     or None,
            location         = ent_raw.get('location')         or None,
            appointment_date = ent_raw.get('appointment_date') or None,
            appointment_time = self._normalize_time(ent_raw.get('appointment_time')),
            phone            = ent_raw.get('phone')            or None,
            citizen_name     = ent_raw.get('citizen_name')     or None,
            note             = ent_raw.get('note')             or None,
        )
        return NLUResult(intent=intent, entities=entities, raw=raw)

    # ── Regex fallback ────────────────────────────────────────────────────────

    def _regex_fallback(self, text: str) -> NLUResult:
        t = text.lower()

        # Intent detection
        if re.search(r'(đặt lịch|hẹn|thủ tục|làm|đăng ký|xin)', t):
            intent = Intent.BOOK_APPOINTMENT
        elif re.search(r'(hỏi|thông tin|giờ làm|địa chỉ|cần gì)', t):
            intent = Intent.QUERY_SERVICE
        elif re.search(r'\b(đồng ý|xác nhận|ok|được|ừ|vâng|chọn)\b', t):
            intent = Intent.CONFIRM
        elif re.search(r'\b(không|hủy|thôi|bỏ)\b', t):
            intent = Intent.DENY
        else:
            intent = Intent.UNKNOWN

        # Service type
        service = None
        if re.search(r'căn cước|cccd', t):
            service = 'Làm căn cước công dân'
        elif re.search(r'khai sinh', t):
            service = 'Đăng ký khai sinh'
        elif re.search(r'hộ chiếu|passport', t):
            service = 'Làm hộ chiếu'
        elif re.search(r'hộ khẩu', t):
            service = 'Đăng ký hộ khẩu'

        # Location
        loc_match = re.search(r'(ubnd[^,.\n]*|ủy ban[^,.\n]*|quận[^,.\n]*|huyện[^,.\n]*)', t)
        location  = loc_match.group(1).strip() if loc_match else None

        # Date YYYY-MM-DD or DD/MM/YYYY
        date_str = None
        m = re.search(r'(20\d{2})-(\d{1,2})-(\d{1,2})', text)
        if m:
            date_str = f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
        else:
            m = re.search(r'(\d{1,2})/(\d{1,2})/(20\d{2})', text)
            if m:
                date_str = f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'

        # Time
        time_str = None
        m = re.search(r'\b(\d{1,2})\s*(?:giờ|h|:)(\d{2})?\b', t)
        if m:
            hh = int(m.group(1))
            mm = int(m.group(2)) if m.group(2) else 0
            time_str = f'{hh:02d}:{mm:02d}:00'

        # Phone
        phone = None
        pm = re.search(r'(0\d{9,10})', text)
        if pm:
            phone = pm.group(1)

        entities = Entities(
            service_type=service, location=location,
            appointment_date=date_str, appointment_time=time_str,
            phone=phone,
        )
        return NLUResult(intent=intent, entities=entities, raw={})

    @staticmethod
    def _normalize_time(t: Optional[str]) -> Optional[str]:
        if not t:
            return None
        if re.match(r'^\d{2}:\d{2}:\d{2}$', t):
            return t
        m = re.match(r'^(\d{1,2}):(\d{2})$', t)
        if m:
            return f'{int(m.group(1)):02d}:{m.group(2)}:00'
        m = re.match(r'^(\d{1,2})$', t)
        if m:
            return f'{int(m.group(1)):02d}:00:00'
        return t
