"""
Chatbot Config Routes — Quản lý persona, prompts, rules cho chatbot.

REST API:
  GET    /api/chatbot/config                 Full active config (persona + prompts + rules)
  POST   /api/chatbot/seed                   Seed default data

  GET    /api/chatbot/personas               Danh sách personas
  POST   /api/chatbot/personas               Tạo persona mới
  PUT    /api/chatbot/personas/<id>          Cập nhật persona
  DELETE /api/chatbot/personas/<id>          Xóa persona
  POST   /api/chatbot/personas/<id>/activate Kích hoạt persona

  GET    /api/chatbot/prompts                Danh sách prompts (?type=system)
  POST   /api/chatbot/prompts               Tạo prompt mới
  PUT    /api/chatbot/prompts/<id>          Cập nhật prompt
  DELETE /api/chatbot/prompts/<id>          Xóa prompt
  POST   /api/chatbot/preview-prompt        Preview prompt với variable substitution

  GET    /api/chatbot/rules                  Danh sách rules (?category=behavior)
  POST   /api/chatbot/rules                  Tạo rule mới
  PUT    /api/chatbot/rules/<id>            Cập nhật rule
  DELETE /api/chatbot/rules/<id>            Xóa rule

  GET    /api/chatbot/build-prompt           Xem prompt hoàn chỉnh theo type
"""
from flask import Blueprint, request, jsonify

from models.chatbot_config import ChatbotPersona, ChatbotPrompt, ChatbotRule
from logger import get_logger

log = get_logger('chatbot_config_routes')
chatbot_cfg_bp = Blueprint('chatbot_config', __name__, url_prefix='/api/chatbot')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ok(data, code=200):
    return jsonify({'success': True, 'data': data}), code

def _err(msg: str, code=400):
    return jsonify({'success': False, 'message': msg}), code

def _admin_only():
    role = getattr(request, 'role', None)
    if not role:
        from flask import g
        role = getattr(g, 'role', None)
    return role == 'admin'


def _invalidate_nlu_cache() -> None:
    """Xóa NLU prompt cache sau khi config thay đổi (non-fatal)."""
    try:
        from routes.voice_routes import _backend
        nlu = getattr(_backend, 'nlu', None) or getattr(_backend, '_nlu', None)
        if nlu and hasattr(nlu, 'invalidate_prompt_cache'):
            nlu.invalidate_prompt_cache()
            log.debug('NLU prompt cache invalidated')
    except Exception as exc:
        log.debug(f'NLU cache invalidate skipped: {exc}')


# ── Full config ───────────────────────────────────────────────────────────────

@chatbot_cfg_bp.route('/config', methods=['GET'])
def get_full_config():
    """Trả về toàn bộ cấu hình chatbot đang active."""
    try:
        persona  = ChatbotPersona.get_active()
        prompts  = ChatbotPrompt.find_all(active_only=True)
        rules    = ChatbotRule.find_all(active_only=True)
        return _ok({
            'persona': persona,
            'prompts': prompts,
            'rules':   rules,
        })
    except Exception as e:
        log.error(f'get_full_config: {e}', exc_info=True)
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/seed', methods=['POST'])
def seed_defaults():
    """Seed dữ liệu mặc định (chỉ admin)."""
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        from models.chatbot_config import seed_defaults as _seed
        _seed()
        return _ok({'message': 'Seed hoàn tất'})
    except Exception as e:
        log.error(f'seed_defaults: {e}', exc_info=True)
        return _err(str(e), 500)


# ── Personas ──────────────────────────────────────────────────────────────────

@chatbot_cfg_bp.route('/personas', methods=['GET'])
def list_personas():
    try:
        personas = ChatbotPersona.find_all()
        return _ok(personas)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/personas', methods=['POST'])
def create_persona():
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    if not data.get('name'):
        return _err('Thiếu name')
    try:
        p = ChatbotPersona.create(data)
        _invalidate_nlu_cache()
        return _ok(p, 201)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/personas/<persona_id>', methods=['PUT'])
def update_persona(persona_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    try:
        p = ChatbotPersona.update(persona_id, data)
        if not p:
            return _err('Persona không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok(p)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/personas/<persona_id>', methods=['DELETE'])
def delete_persona(persona_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        ok = ChatbotPersona.delete(persona_id)
        if not ok:
            return _err('Persona không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok({'deleted': persona_id})
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/personas/<persona_id>/activate', methods=['POST'])
def activate_persona(persona_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        p = ChatbotPersona.set_active(persona_id)
        if not p:
            return _err('Persona không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok(p)
    except Exception as e:
        return _err(str(e), 500)


# ── Prompts ───────────────────────────────────────────────────────────────────

@chatbot_cfg_bp.route('/prompts', methods=['GET'])
def list_prompts():
    prompt_type = request.args.get('type')
    active_only = request.args.get('active', 'false').lower() == 'true'
    try:
        prompts = ChatbotPrompt.find_all(prompt_type=prompt_type, active_only=active_only)
        return _ok(prompts)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/prompts', methods=['POST'])
def create_prompt():
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    for f in ('type', 'name', 'content'):
        if not data.get(f):
            return _err(f'Thiếu trường: {f}')
    try:
        p = ChatbotPrompt.create(data)
        _invalidate_nlu_cache()
        return _ok(p, 201)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    try:
        p = ChatbotPrompt.update(prompt_id, data)
        if not p:
            return _err('Prompt không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok(p)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        ok = ChatbotPrompt.delete(prompt_id)
        if not ok:
            return _err('Prompt không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok({'deleted': prompt_id})
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/preview-prompt', methods=['POST'])
def preview_prompt():
    """
    Preview prompt với variable substitution.
    Body: { promptId: str, extraVars?: dict }
    """
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data      = request.get_json() or {}
    prompt_id = data.get('promptId')
    if not prompt_id:
        return _err('Thiếu promptId')
    try:
        from services.prompt_builder import preview_prompt as _preview
        result = _preview(prompt_id, data.get('extraVars'))
        if 'error' in result:
            return _err(result['error'], 404)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


# ── Rules ─────────────────────────────────────────────────────────────────────

@chatbot_cfg_bp.route('/rules', methods=['GET'])
def list_rules():
    category    = request.args.get('category')
    active_only = request.args.get('active', 'false').lower() == 'true'
    try:
        rules = ChatbotRule.find_all(category=category, active_only=active_only)
        return _ok(rules)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/rules', methods=['POST'])
def create_rule():
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    for f in ('category', 'rule_text'):
        if not data.get(f):
            return _err(f'Thiếu trường: {f}')
    try:
        r = ChatbotRule.create(data)
        _invalidate_nlu_cache()
        return _ok(r, 201)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    data = request.get_json() or {}
    try:
        r = ChatbotRule.update(rule_id, data)
        if not r:
            return _err('Rule không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok(r)
    except Exception as e:
        return _err(str(e), 500)


@chatbot_cfg_bp.route('/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id: str):
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        ok = ChatbotRule.delete(rule_id)
        if not ok:
            return _err('Rule không tồn tại', 404)
        _invalidate_nlu_cache()
        return _ok({'deleted': rule_id})
    except Exception as e:
        return _err(str(e), 500)


# ── Build prompt (debug / admin) ──────────────────────────────────────────────

@chatbot_cfg_bp.route('/invalidate-cache', methods=['POST'])
def invalidate_prompt_cache():
    """Xóa cache prompt của NLU engine sau khi cập nhật config."""
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    try:
        from routes.voice_routes import _backend
        nlu = getattr(_backend, 'nlu', None) or getattr(_backend, '_nlu', None)
        if nlu and hasattr(nlu, 'invalidate_prompt_cache'):
            nlu.invalidate_prompt_cache()
        return _ok({'message': 'Cache đã được xóa'})
    except Exception as e:
        log.warning(f'invalidate_cache: {e}')
        return _ok({'message': 'Cache cleared (NLU not loaded yet)'})


@chatbot_cfg_bp.route('/build-prompt', methods=['GET'])
def build_prompt_view():
    """
    Xem prompt hoàn chỉnh theo type.
    Query: ?type=system|nlu|rag_answer|dialog_confirm|error_fallback
    """
    if not _admin_only():
        return _err('Cần quyền admin', 403)
    prompt_type = request.args.get('type', 'system')
    try:
        from services.prompt_builder import build_system_prompt
        rendered = build_system_prompt(prompt_type)
        return _ok({'type': prompt_type, 'prompt': rendered, 'length': len(rendered)})
    except Exception as e:
        return _err(str(e), 500)
