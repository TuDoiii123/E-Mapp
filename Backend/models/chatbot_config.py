"""
Chatbot Configuration Models
Quản lý: Persona, Prompts, Rules cho voice/text chatbot.

Lưu trữ: PostgreSQL (chính) → JSON file (fallback).
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

try:
    from models.db import db
    from sqlalchemy import text
    HAS_DB = True
except Exception:
    db = None
    text = None
    HAS_DB = False

_DATA_DIR = Path(__file__).parent.parent / 'data'
_DATA_DIR.mkdir(exist_ok=True)

# ── JSON fallback helpers ─────────────────────────────────────────────────────

def _jread(filename: str) -> list | dict:
    p = _DATA_DIR / filename
    if p.exists():
        try:
            return json.loads(p.read_text('utf-8'))
        except Exception:
            pass
    return []

def _jwrite(filename: str, data) -> None:
    (_DATA_DIR / filename).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), 'utf-8'
    )

def _now() -> str:
    return datetime.now().isoformat()

def _uid() -> str:
    return str(uuid.uuid4())

def _use_db() -> bool:
    if not HAS_DB or db is None:
        return False
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT CONFIG — seed khi chưa có data
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_PERSONA = {
    'name':        'Trợ lý Dịch vụ Công',
    'tone':        'formal',
    'language':    'vi',
    'greeting':    (
        'Xin chào! Tôi là trợ lý hành chính công số. '
        'Tôi có thể giúp bạn tra cứu thủ tục, đặt lịch hẹn, '
        'hoặc tìm kiếm thông tin dịch vụ công. Bạn cần hỗ trợ gì?'
    ),
    'farewell':    'Cảm ơn bạn đã sử dụng dịch vụ. Chúc bạn một ngày tốt lành!',
    'description': 'Nhân vật mặc định — lịch sự, chuyên nghiệp, hỗ trợ thủ tục hành chính.',
    'is_active':   True,
}

DEFAULT_PROMPTS = [
    {
        'type':    'system',
        'name':    'System Prompt Chính',
        'content': (
            'Bạn là {bot_name}, trợ lý hành chính công số của {org_name}.\n\n'
            'VAI TRÒ:\n'
            '- Hỗ trợ công dân tra cứu thủ tục hành chính, giấy tờ cần chuẩn bị.\n'
            '- Đặt lịch hẹn trực tuyến tại các cơ quan hành chính.\n'
            '- Cung cấp thông tin địa điểm, giờ làm việc, liên hệ cơ quan.\n'
            '- Tra cứu trạng thái hồ sơ.\n\n'
            'PHẠM VI:\n'
            '- Chỉ trả lời các câu hỏi liên quan đến dịch vụ công và thủ tục hành chính.\n'
            '- Không cung cấp tư vấn pháp lý chuyên sâu.\n'
            '- Không xử lý thông tin tài chính, ngân hàng.\n\n'
            'PHONG CÁCH:\n'
            '- Sử dụng tiếng Việt chuẩn, lịch sự, dễ hiểu.\n'
            '- Trả lời ngắn gọn, đúng trọng tâm.\n'
            '- Xưng hô "tôi" / "bạn" hoặc "anh/chị" tùy ngữ cảnh.\n\n'
            'NGÀY HÔM NAY: {today}\n\n'
            '{rules_section}'
        ),
        'description': 'System prompt chính — nạp vào đầu mỗi cuộc hội thoại',
        'variables':   ['bot_name', 'org_name', 'today', 'rules_section'],
    },
    {
        'type':    'nlu',
        'name':    'NLU — Phân tích ý định và trích xuất thực thể',
        'content': (
            'Bạn là engine NLU tiếng Việt cho hệ thống hành chính công.\n\n'
            'NHIỆM VỤ: Phân tích câu người dùng và trả về JSON.\n\n'
            'SCHEMA:\n'
            '{\n'
            '  "intent": "<BOOK_APPOINTMENT|QUERY_PROCEDURE|QUERY_LOCATION|QUERY_STATUS|CANCEL|CONFIRM|DENY|GREETING|FAREWELL|UNKNOWN>",\n'
            '  "confidence": <0.0–1.0>,\n'
            '  "entities": {\n'
            '    "service_type":     "<tên thủ tục hoặc null>",\n'
            '    "location":         "<tên cơ quan/quận hoặc null>",\n'
            '    "appointment_date": "<YYYY-MM-DD hoặc null>",\n'
            '    "appointment_time": "<HH:MM:SS hoặc null>",\n'
            '    "phone":            "<số điện thoại hoặc null>",\n'
            '    "citizen_name":     "<họ tên hoặc null>",\n'
            '    "note":             "<ghi chú hoặc null>",\n'
            '    "procedure_code":   "<mã thủ tục hoặc null>",\n'
            '    "doc_id":           "<mã hồ sơ hoặc null>"\n'
            '  }\n'
            '}\n\n'
            'QUY TẮC:\n'
            '- Ngày tương đối ("ngày mai", "thứ 2", "tuần sau") → YYYY-MM-DD tính từ hôm nay {today}.\n'
            '- Giờ ("9 giờ", "9h", "9:00", "sáng sớm") → HH:MM:SS.\n'
            '- Nhận dạng tên thủ tục theo tiếng Việt thông thường.\n'
            '- Chỉ trả JSON thuần, không giải thích.\n\n'
            'LỊCH SỬ HỘI THOẠI:\n{history}\n\n'
            'CÂU NGƯỜI DÙNG: "{user_text}"\n\n'
            'JSON:'
        ),
        'description': 'Prompt phân tích NLU — intent + entities',
        'variables':   ['today', 'history', 'user_text'],
    },
    {
        'type':    'rag_answer',
        'name':    'RAG — Trả lời từ tài liệu tham khảo',
        'content': (
            'Bạn là trợ lý hành chính công. Dựa trên TÀI LIỆU bên dưới, hãy trả lời câu hỏi của người dùng.\n\n'
            'QUY TẮC:\n'
            '- Chỉ dùng thông tin trong TÀI LIỆU để trả lời.\n'
            '- Nếu không tìm thấy thông tin, nói rõ "Tôi chưa có thông tin về vấn đề này".\n'
            '- Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng.\n'
            '- Không bịa đặt thông tin.\n\n'
            'TÀI LIỆU THAM KHẢO:\n{context}\n\n'
            'CÂU HỎI: {question}\n\n'
            'TRẢ LỜI:'
        ),
        'description': 'Prompt sinh câu trả lời từ tài liệu RAG',
        'variables':   ['context', 'question'],
    },
    {
        'type':    'dialog_confirm',
        'name':    'Xác nhận đặt lịch',
        'content': (
            'Xác nhận thông tin đặt lịch của bạn:\n'
            '• Thủ tục : {service_type}\n'
            '• Địa điểm: {location}\n'
            '• Ngày    : {date}\n'
            '• Giờ     : {time}\n\n'
            'Bạn có xác nhận không? (Có / Không)'
        ),
        'description': 'Template xác nhận đặt lịch trước khi submit',
        'variables':   ['service_type', 'location', 'date', 'time'],
    },
    {
        'type':    'error_fallback',
        'name':    'Fallback khi lỗi',
        'content': (
            'Xin lỗi, tôi không hiểu yêu cầu của bạn. '
            'Bạn có thể nói rõ hơn không? '
            'Ví dụ: "Tôi muốn làm căn cước công dân" hoặc "Giờ làm việc của UBND quận".'
        ),
        'description': 'Phản hồi mặc định khi không hiểu ý định',
        'variables':   [],
    },
]

DEFAULT_RULES = [
    # ── Hành vi ──────────────────────────────────────────────────────────────
    {'category': 'behavior', 'priority': 100,
     'rule_text': 'Luôn trả lời bằng tiếng Việt, trừ khi người dùng dùng ngôn ngữ khác.'},
    {'category': 'behavior', 'priority': 99,
     'rule_text': 'Không tự ý bịa đặt thông tin về thủ tục, phí, thời hạn. Chỉ dùng dữ liệu từ hệ thống.'},
    {'category': 'behavior', 'priority': 98,
     'rule_text': 'Khi không chắc chắn, đề nghị người dùng liên hệ trực tiếp cơ quan có thẩm quyền.'},
    {'category': 'behavior', 'priority': 97,
     'rule_text': 'Xưng hô lịch sự, dùng "anh/chị" khi không rõ giới tính, dùng "bạn" trong ngữ cảnh thân mật hơn.'},
    # ── Giới hạn chủ đề ──────────────────────────────────────────────────────
    {'category': 'scope',    'priority': 90,
     'rule_text': 'Chỉ trả lời về: thủ tục hành chính, dịch vụ công, lịch hẹn, địa điểm cơ quan.'},
    {'category': 'scope',    'priority': 89,
     'rule_text': 'Từ chối lịch sự các câu hỏi không liên quan đến dịch vụ công.'},
    {'category': 'scope',    'priority': 88,
     'rule_text': 'Không tư vấn pháp lý chuyên sâu; hướng dẫn người dùng tìm luật sư hoặc cơ quan tư pháp.'},
    # ── Bảo mật / Quyền riêng tư ─────────────────────────────────────────────
    {'category': 'security', 'priority': 80,
     'rule_text': 'Không yêu cầu hoặc lưu giữ thông tin nhạy cảm: mật khẩu, thẻ tín dụng, OTP ngân hàng.'},
    {'category': 'security', 'priority': 79,
     'rule_text': 'Thông tin CCCD, hộ khẩu chỉ hỏi khi thực sự cần thiết cho đặt lịch và không lưu trữ lâu dài.'},
    # ── Đặt lịch ─────────────────────────────────────────────────────────────
    {'category': 'booking',  'priority': 70,
     'rule_text': 'Khi đặt lịch, bắt buộc thu thập đủ: loại thủ tục, địa điểm, ngày, giờ trước khi xác nhận.'},
    {'category': 'booking',  'priority': 69,
     'rule_text': 'Chỉ gợi ý các khung giờ còn trống trong giờ hành chính (7:30–11:30 và 13:30–17:00).'},
    {'category': 'booking',  'priority': 68,
     'rule_text': 'Luôn xác nhận lại thông tin đặt lịch trước khi lưu vào hệ thống.'},
    # ── Chất lượng trả lời ───────────────────────────────────────────────────
    {'category': 'quality',  'priority': 60,
     'rule_text': 'Câu trả lời voice tối đa 3 câu, dễ nghe, không dùng ký tự đặc biệt.'},
    {'category': 'quality',  'priority': 59,
     'rule_text': 'Câu trả lời text có thể dài hơn, dùng danh sách khi liệt kê nhiều mục.'},
    {'category': 'quality',  'priority': 58,
     'rule_text': 'Khi hỏi thiếu thông tin, chỉ hỏi một câu hỏi mỗi lần.'},
]


# ═══════════════════════════════════════════════════════════════════════════════
# ChatbotPersona
# ═══════════════════════════════════════════════════════════════════════════════

class ChatbotPersona:

    @staticmethod
    def get_active() -> dict:
        if _use_db():
            row = db.session.execute(text(
                "SELECT * FROM public.chatbot_personas WHERE is_active = TRUE ORDER BY updated_at DESC LIMIT 1"
            )).fetchone()
            if row:
                return dict(row._mapping)
        data = _jread('chatbot_personas.json')
        if isinstance(data, list):
            active = [p for p in data if p.get('is_active', True)]
            return active[0] if active else {}
        return data if data else {}

    @staticmethod
    def find_all() -> list:
        if _use_db():
            rows = db.session.execute(text(
                "SELECT * FROM public.chatbot_personas ORDER BY updated_at DESC"
            )).fetchall()
            return [dict(r._mapping) for r in rows]
        data = _jread('chatbot_personas.json')
        return data if isinstance(data, list) else []

    @staticmethod
    def find_by_id(pid: str) -> dict | None:
        if _use_db():
            row = db.session.execute(text(
                "SELECT * FROM public.chatbot_personas WHERE id = :id"
            ), {'id': pid}).fetchone()
            return dict(row._mapping) if row else None
        for p in ChatbotPersona.find_all():
            if p.get('id') == pid:
                return p
        return None

    @staticmethod
    def create(data: dict) -> dict:
        pid = _uid()
        now = _now()
        obj = {**DEFAULT_PERSONA, **data, 'id': pid, 'created_at': now, 'updated_at': now}
        if _use_db():
            db.session.execute(text("""
                INSERT INTO public.chatbot_personas
                    (id, name, tone, language, greeting, farewell, description, is_active)
                VALUES (:id, :name, :tone, :language, :greeting, :farewell, :description, :is_active)
            """), {k: obj.get(k) for k in ['id','name','tone','language','greeting','farewell','description','is_active']})
            db.session.commit()
            return ChatbotPersona.find_by_id(pid) or obj
        personas = ChatbotPersona.find_all()
        personas.append(obj)
        _jwrite('chatbot_personas.json', personas)
        return obj

    @staticmethod
    def update(pid: str, data: dict) -> dict | None:
        data.pop('id', None)
        data['updated_at'] = _now()
        if _use_db():
            sets   = ', '.join(f"{k} = :{k}" for k in data)
            params = {**data, 'id': pid}
            db.session.execute(text(f"UPDATE public.chatbot_personas SET {sets} WHERE id = :id"), params)
            db.session.commit()
            return ChatbotPersona.find_by_id(pid)
        personas = ChatbotPersona.find_all()
        for p in personas:
            if p.get('id') == pid:
                p.update(data)
                _jwrite('chatbot_personas.json', personas)
                return p
        return None

    @staticmethod
    def set_active(pid: str) -> dict | None:
        """Đặt persona thành active (chỉ 1 active tại một thời điểm)."""
        if _use_db():
            db.session.execute(text("UPDATE public.chatbot_personas SET is_active = FALSE"))
            db.session.execute(text(
                "UPDATE public.chatbot_personas SET is_active = TRUE, updated_at = now() WHERE id = :id"
            ), {'id': pid})
            db.session.commit()
            return ChatbotPersona.find_by_id(pid)
        personas = ChatbotPersona.find_all()
        for p in personas:
            p['is_active'] = (p.get('id') == pid)
        _jwrite('chatbot_personas.json', personas)
        return next((p for p in personas if p.get('id') == pid), None)

    @staticmethod
    def delete(pid: str) -> bool:
        if _use_db():
            db.session.execute(text("DELETE FROM public.chatbot_personas WHERE id = :id"), {'id': pid})
            db.session.commit()
            return True
        personas = [p for p in ChatbotPersona.find_all() if p.get('id') != pid]
        _jwrite('chatbot_personas.json', personas)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# ChatbotPrompt
# ═══════════════════════════════════════════════════════════════════════════════

class ChatbotPrompt:

    TYPES = ('system', 'nlu', 'rag_answer', 'dialog_confirm', 'error_fallback', 'custom')

    @staticmethod
    def find_all(prompt_type: str = None, active_only: bool = False) -> list:
        if _use_db():
            where, params = [], {}
            if prompt_type: where.append('type = :type');       params['type'] = prompt_type
            if active_only: where.append('is_active = TRUE')
            clause = ('WHERE ' + ' AND '.join(where)) if where else ''
            rows = db.session.execute(text(
                f"SELECT * FROM public.chatbot_prompts {clause} ORDER BY type, updated_at DESC"
            ), params).fetchall()
            return [dict(r._mapping) for r in rows]
        data = _jread('chatbot_prompts.json')
        result = data if isinstance(data, list) else []
        if prompt_type: result = [p for p in result if p.get('type') == prompt_type]
        if active_only: result = [p for p in result if p.get('is_active', True)]
        return result

    @staticmethod
    def get_active(prompt_type: str) -> dict | None:
        prompts = ChatbotPrompt.find_all(prompt_type=prompt_type, active_only=True)
        return prompts[0] if prompts else None

    @staticmethod
    def find_by_id(pid: str) -> dict | None:
        if _use_db():
            row = db.session.execute(text(
                "SELECT * FROM public.chatbot_prompts WHERE id = :id"
            ), {'id': pid}).fetchone()
            return dict(row._mapping) if row else None
        for p in ChatbotPrompt.find_all():
            if p.get('id') == pid:
                return p
        return None

    @staticmethod
    def create(data: dict) -> dict:
        pid = _uid()
        now = _now()
        vars_ = data.get('variables', [])
        obj = {**data, 'id': pid, 'created_at': now, 'updated_at': now,
               'is_active': data.get('is_active', True),
               'variables': vars_ if isinstance(vars_, list) else []}
        if _use_db():
            db.session.execute(text("""
                INSERT INTO public.chatbot_prompts
                    (id, type, name, content, description, variables, is_active, persona_id)
                VALUES (:id, :type, :name, :content, :description, :variables, :is_active, :persona_id)
            """), {**obj, 'variables': json.dumps(obj['variables']),
                   'persona_id': obj.get('persona_id')})
            db.session.commit()
            return ChatbotPrompt.find_by_id(pid) or obj
        prompts = ChatbotPrompt.find_all()
        prompts.append(obj)
        _jwrite('chatbot_prompts.json', prompts)
        return obj

    @staticmethod
    def update(pid: str, data: dict) -> dict | None:
        data.pop('id', None)
        data['updated_at'] = _now()
        if 'variables' in data and isinstance(data['variables'], list):
            data['variables'] = json.dumps(data['variables'])
        if _use_db():
            sets   = ', '.join(f"{k} = :{k}" for k in data)
            params = {**data, 'id': pid}
            db.session.execute(text(f"UPDATE public.chatbot_prompts SET {sets} WHERE id = :id"), params)
            db.session.commit()
            return ChatbotPrompt.find_by_id(pid)
        prompts = ChatbotPrompt.find_all()
        for p in prompts:
            if p.get('id') == pid:
                p.update(data)
                _jwrite('chatbot_prompts.json', prompts)
                return p
        return None

    @staticmethod
    def delete(pid: str) -> bool:
        if _use_db():
            db.session.execute(text("DELETE FROM public.chatbot_prompts WHERE id = :id"), {'id': pid})
            db.session.commit()
            return True
        prompts = [p for p in ChatbotPrompt.find_all() if p.get('id') != pid]
        _jwrite('chatbot_prompts.json', prompts)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# ChatbotRule
# ═══════════════════════════════════════════════════════════════════════════════

class ChatbotRule:

    CATEGORIES = ('behavior', 'scope', 'security', 'booking', 'quality', 'custom')

    @staticmethod
    def find_all(category: str = None, active_only: bool = True) -> list:
        if _use_db():
            where, params = [], {}
            if category:    where.append('category = :cat'); params['cat'] = category
            if active_only: where.append('is_active = TRUE')
            clause = ('WHERE ' + ' AND '.join(where)) if where else ''
            rows = db.session.execute(text(
                f"SELECT * FROM public.chatbot_rules {clause} ORDER BY priority DESC, category"
            ), params).fetchall()
            return [dict(r._mapping) for r in rows]
        data = _jread('chatbot_rules.json')
        rules = data if isinstance(data, list) else []
        if category:    rules = [r for r in rules if r.get('category') == category]
        if active_only: rules = [r for r in rules if r.get('is_active', True)]
        return sorted(rules, key=lambda r: -r.get('priority', 0))

    @staticmethod
    def find_by_id(rid: str) -> dict | None:
        if _use_db():
            row = db.session.execute(text(
                "SELECT * FROM public.chatbot_rules WHERE id = :id"
            ), {'id': rid}).fetchone()
            return dict(row._mapping) if row else None
        for r in ChatbotRule.find_all(active_only=False):
            if r.get('id') == rid:
                return r
        return None

    @staticmethod
    def create(data: dict) -> dict:
        rid = _uid()
        now = _now()
        obj = {**data, 'id': rid, 'is_active': data.get('is_active', True),
               'priority': data.get('priority', 0),
               'created_at': now, 'updated_at': now}
        if _use_db():
            db.session.execute(text("""
                INSERT INTO public.chatbot_rules (id, category, rule_text, priority, is_active)
                VALUES (:id, :category, :rule_text, :priority, :is_active)
            """), {k: obj[k] for k in ['id','category','rule_text','priority','is_active']})
            db.session.commit()
            return ChatbotRule.find_by_id(rid) or obj
        rules = ChatbotRule.find_all(active_only=False)
        rules.append(obj)
        _jwrite('chatbot_rules.json', rules)
        return obj

    @staticmethod
    def update(rid: str, data: dict) -> dict | None:
        data.pop('id', None)
        data['updated_at'] = _now()
        if _use_db():
            sets   = ', '.join(f"{k} = :{k}" for k in data)
            params = {**data, 'id': rid}
            db.session.execute(text(f"UPDATE public.chatbot_rules SET {sets} WHERE id = :id"), params)
            db.session.commit()
            return ChatbotRule.find_by_id(rid)
        rules = ChatbotRule.find_all(active_only=False)
        for r in rules:
            if r.get('id') == rid:
                r.update(data)
                _jwrite('chatbot_rules.json', rules)
                return r
        return None

    @staticmethod
    def delete(rid: str) -> bool:
        if _use_db():
            db.session.execute(text("DELETE FROM public.chatbot_rules WHERE id = :id"), {'id': rid})
            db.session.commit()
            return True
        rules = [r for r in ChatbotRule.find_all(active_only=False) if r.get('id') != rid]
        _jwrite('chatbot_rules.json', rules)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# Seed default data
# ═══════════════════════════════════════════════════════════════════════════════

def seed_defaults() -> None:
    """Khởi tạo dữ liệu mặc định nếu chưa có. An toàn để gọi nhiều lần."""
    # Persona
    if not ChatbotPersona.find_all():
        ChatbotPersona.create(DEFAULT_PERSONA)

    # Prompts
    existing_types = {p['type'] for p in ChatbotPrompt.find_all(active_only=False)}
    for pt in DEFAULT_PROMPTS:
        if pt['type'] not in existing_types:
            ChatbotPrompt.create(pt)

    # Rules
    if not ChatbotRule.find_all(active_only=False):
        for rule in DEFAULT_RULES:
            ChatbotRule.create(rule)
