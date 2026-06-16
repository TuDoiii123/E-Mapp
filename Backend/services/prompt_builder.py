"""
Prompt Builder — Xây dựng prompt động từ cấu hình DB.

Tải persona + system prompt + rules từ chatbot_config và ghép thành
prompt hoàn chỉnh để inject vào Gemini.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from logger import get_logger

log = get_logger('prompt_builder')

# Org name dùng cho biến {org_name}
ORG_NAME = 'E-Mapp Dịch vụ công điện tử'


def _load_models():
    """Lazy import để tránh circular imports."""
    from models.chatbot_config import ChatbotPersona, ChatbotPrompt, ChatbotRule
    return ChatbotPersona, ChatbotPrompt, ChatbotRule


# ── Substitution ──────────────────────────────────────────────────────────────

def _substitute(template: str, vars_: dict) -> str:
    """
    Thay thế {variable} trong template bằng giá trị trong vars_.
    Biến không có trong vars_ được giữ nguyên.
    """
    def replace(m: re.Match) -> str:
        key = m.group(1)
        return str(vars_.get(key, m.group(0)))

    return re.sub(r'\{(\w+)\}', replace, template)


# ── Core builder ──────────────────────────────────────────────────────────────

def build_system_prompt(prompt_type: str = 'system') -> str:
    """
    Xây dựng system prompt hoàn chỉnh cho chatbot.

    1. Tải persona đang active → lấy name, tone, greeting
    2. Tải active rules → ghép thành rules_section
    3. Tải active prompt theo type → substitute biến
    4. Trả về chuỗi prompt cuối cùng

    Parameters
    ----------
    prompt_type : loại prompt ('system', 'nlu', 'rag_answer', 'dialog_confirm', ...)
    """
    try:
        ChatbotPersona, ChatbotPrompt, ChatbotRule = _load_models()

        # 1. Persona
        persona = ChatbotPersona.get_active()
        bot_name = (persona or {}).get('name', 'Trợ lý công')
        tone     = (persona or {}).get('tone', 'formal')
        greeting = (persona or {}).get('greeting', 'Xin chào!')

        # 2. Rules → rules_section
        rules = ChatbotRule.find_all(active_only=True)
        if rules:
            lines = [f'- {r["rule_text"]}' for r in rules]
            rules_section = '\n'.join(lines)
        else:
            rules_section = '- Hỗ trợ người dùng tra cứu thủ tục hành chính.'

        # 3. Active prompt template
        prompt_obj = ChatbotPrompt.get_active(prompt_type)
        if not prompt_obj:
            log.warning(f'[PromptBuilder] Không có prompt active cho type={prompt_type}, dùng fallback.')
            return _fallback_prompt(prompt_type, bot_name, org_name=ORG_NAME,
                                    rules_section=rules_section, today=date.today().isoformat())

        template = prompt_obj.get('content', '')

        # 4. Substitute
        final = _substitute(template, {
            'bot_name':      bot_name,
            'org_name':      ORG_NAME,
            'today':         date.today().isoformat(),
            'rules_section': rules_section,
            'tone':          tone,
            'greeting':      greeting,
        })
        return final

    except Exception as e:
        log.error(f'[PromptBuilder] build_system_prompt lỗi: {e}', exc_info=True)
        return _fallback_prompt(prompt_type)


def build_nlu_prompt() -> str:
    """Trả về prompt cho NLU engine."""
    return build_system_prompt('nlu')


def build_rag_prompt() -> str:
    """Trả về prompt cho RAG answer generation."""
    return build_system_prompt('rag_answer')


def build_dialog_confirm_prompt() -> str:
    """Trả về prompt xác nhận thông tin đặt lịch."""
    return build_system_prompt('dialog_confirm')


def build_error_fallback_prompt() -> str:
    """Trả về prompt xử lý lỗi / không hiểu."""
    return build_system_prompt('error_fallback')


# ── Preview (admin) ───────────────────────────────────────────────────────────

def preview_prompt(prompt_id: str, extra_vars: Optional[dict] = None) -> dict:
    """
    Sinh preview cho một prompt cụ thể.
    Dùng cho admin endpoint /api/chatbot/preview-prompt.

    Returns
    -------
    dict với keys: rendered, variables_used, missing_variables
    """
    try:
        ChatbotPersona, ChatbotPrompt, ChatbotRule = _load_models()

        prompt_obj = ChatbotPrompt.find_by_id(prompt_id)
        if not prompt_obj:
            return {'error': 'Prompt không tồn tại'}

        persona = ChatbotPersona.get_active()
        bot_name = (persona or {}).get('name', 'Trợ lý công')

        rules = ChatbotRule.find_all(active_only=True)
        rules_section = '\n'.join(f'- {r["rule_text"]}' for r in rules) if rules else ''

        base_vars = {
            'bot_name':      bot_name,
            'org_name':      ORG_NAME,
            'today':         date.today().isoformat(),
            'rules_section': rules_section,
            'tone':          (persona or {}).get('tone', 'formal'),
            'greeting':      (persona or {}).get('greeting', ''),
        }
        if extra_vars:
            base_vars.update(extra_vars)

        template = prompt_obj.get('content', '')

        # Tìm tất cả biến trong template
        found_vars = re.findall(r'\{(\w+)\}', template)
        missing    = [v for v in found_vars if v not in base_vars]

        rendered = _substitute(template, base_vars)

        return {
            'rendered':          rendered,
            'variables_used':    list(set(found_vars) & base_vars.keys()),
            'missing_variables': missing,
            'template_length':   len(template),
            'rendered_length':   len(rendered),
        }

    except Exception as e:
        log.error(f'[PromptBuilder] preview_prompt lỗi: {e}', exc_info=True)
        return {'error': str(e)}


# ── Fallback prompts ──────────────────────────────────────────────────────────

def _fallback_prompt(
    prompt_type: str,
    bot_name: str = 'Trợ lý công',
    org_name: str = ORG_NAME,
    rules_section: str = '',
    today: str = '',
) -> str:
    today = today or date.today().isoformat()

    if prompt_type == 'nlu':
        return (
            f'Bạn là AI phân tích ngôn ngữ tự nhiên tiếng Việt cho {org_name}.\n'
            'Nhiệm vụ: phân tích câu người dùng và trả về JSON có cấu trúc.\n\n'
            'Schema:\n'
            '{\n'
            '  "intent": "<BOOK_APPOINTMENT|QUERY_PROCEDURE|QUERY_LOCATION|QUERY_STATUS|'
            'CANCEL|CONFIRM|DENY|GREETING|FAREWELL|UNKNOWN>",\n'
            '  "entities": {\n'
            '    "service_type": null,\n'
            '    "location": null,\n'
            '    "appointment_date": "<YYYY-MM-DD>",\n'
            '    "appointment_time": "<HH:MM:SS>",\n'
            '    "phone": null,\n'
            '    "citizen_name": null,\n'
            '    "note": null\n'
            '  }\n'
            '}\n\n'
            'Ngày → LUÔN trả YYYY-MM-DD: tương đối ("ngày mai", "thứ 2") tính từ hôm nay; '
            'tường minh ("ngày 1 tháng 7 năm 2026", "1/7/2026") đổi thẳng '
            '(vd "ngày 1 tháng 7 năm 2026" → "2026-07-01").\n'
            f'Hôm nay: {today}. Chỉ trả JSON thuần.'
        )

    if prompt_type == 'rag_answer':
        return (
            f'Bạn là chuyên gia hành chính công Việt Nam, trả lời câu hỏi trực tiếp và đầy đủ.\n'
            'Luôn trả lời dựa trên kiến thức chuyên môn. Không nói "không có thông tin", "hệ thống chưa có", không redirect user tự tra cứu.\n'
            'Không dùng markdown: không ###, **, *, ---, ```.'
        )

    # Default system
    return (
        f'Bạn là {bot_name} — chuyên gia hành chính công của {org_name}.\n'
        f'Hôm nay: {today}.\n\n'
        'Quy tắc:\n' + (rules_section or '- Hỗ trợ người dùng tra cứu thủ tục hành chính.') + '\n'
        'Luôn trả lời trực tiếp, không nói "hệ thống chưa có", không redirect user tự tra cứu.\n'
        'Không dùng markdown: không ###, **, *, ---, ```.'
    )
