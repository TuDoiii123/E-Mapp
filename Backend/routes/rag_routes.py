"""
RAG / chatbot routes: chat, session history, procedure suggestion.
"""
import json
import os
import re
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from RAG.agent_core.graph import MultiRoleAgentGraph
from RAG.connect_SQL.connect_SQL import connect_sql
from RAG.tools.suggest import init_suggest, suggest_procedures
from logger import get_logger

log = get_logger('rag_routes')

rag_bp = Blueprint('rag', __name__)

VN_TZ = timezone(timedelta(hours=7))

# ── Lazy singletons (thread-safe) ─────────────────────────────────────────────
_agent_graph: Optional[MultiRoleAgentGraph] = None
_db_engine = None
_agent_lock = threading.Lock()
_db_lock    = threading.Lock()


def _get_agent() -> MultiRoleAgentGraph:
    global _agent_graph
    if _agent_graph is None:
        with _agent_lock:
            if _agent_graph is None:
                _agent_graph = MultiRoleAgentGraph()
    return _agent_graph


def _get_db():
    global _db_engine
    if _db_engine is None:
        with _db_lock:
            if _db_engine is None:
                _db_engine = connect_sql()
    return _db_engine


def _tts_mp3_base64(text: str) -> Optional[str]:
    """Synthesize Vietnamese speech, return base64 MP3 or None."""
    try:
        from google.cloud import texttospeech as g_tts  # type: ignore
        client = g_tts.TextToSpeechClient()
        res = client.synthesize_speech(
            input=g_tts.SynthesisInput(text=text),
            voice=g_tts.VoiceSelectionParams(language_code='vi-VN', ssml_gender=g_tts.SsmlVoiceGender.NEUTRAL),
            audio_config=g_tts.AudioConfig(audio_encoding=g_tts.AudioEncoding.MP3),
        )
        import base64
        return base64.b64encode(res.audio_content).decode('ascii')
    except Exception:
        return None


def _clean_docs(raw: Any) -> str:
    if isinstance(raw, (dict, list)):
        try:
            return json.dumps(raw, ensure_ascii=False)
        except TypeError:
            return json.dumps(str(raw), ensure_ascii=False)
    if isinstance(raw, str):
        cleaned = re.sub(r'^```[a-zA-Z]*\s*|\s*```$', '', raw.strip())
        try:
            return json.dumps(json.loads(cleaned), ensure_ascii=False)
        except json.JSONDecodeError:
            return cleaned
    return json.dumps(str(raw), ensure_ascii=False)


# ── DB logging ─────────────────────────────────────────────────────────────────
def _log_chat(session_id: Optional[str], user_query: str, ai_response: str, intermediate_steps: str) -> Optional[str]:
    """Persist chat to SQL Server. Returns session_id or None on failure/no-db."""
    engine = _get_db()
    if engine is None:
        return None

    timestamp = datetime.now(VN_TZ).replace(tzinfo=None)
    is_new = not session_id
    sid = session_id or f'st_session_{uuid.uuid4()}'
    summary = user_query[:30] + ('...' if len(user_query) > 30 else '')

    try:
        with engine.begin() as conn:
            if is_new:
                conn.execute(
                    text('''INSERT INTO chat_sessions (session_id, first_message_summary, created_at)
                            VALUES (:sid, :summary, :ts)
                            ON CONFLICT (session_id) DO NOTHING'''),
                    {'sid': sid, 'summary': summary, 'ts': timestamp},
                )
            result = conn.execute(
                text('''INSERT INTO conversation_history (session_id, user_message, bot_response, timestamp)
                        VALUES (:sid, :user_msg, :bot_res, :ts)
                        RETURNING id'''),
                {'sid': sid, 'user_msg': user_query, 'bot_res': ai_response, 'ts': timestamp},
            )
            conv_id = result.scalar_one()
            conn.execute(
                text('''INSERT INTO query_results (conversation_id, query_text, response_text, retrieved_docs, model_name, timestamp)
                        VALUES (:conv_id, :q_text, :res_text, :r_docs, :model, :ts)'''),
                {'conv_id': conv_id, 'q_text': user_query, 'res_text': ai_response,
                 'r_docs': intermediate_steps, 'model': os.getenv('GEMINI_MODEL_RAG', 'gemini-2.0-flash'), 'ts': timestamp},
            )
    except SQLAlchemyError as exc:
        log.warning(f'[rag] DB log failed: {exc}', exc_info=True)
        return None

    return sid


def _fetch_recent_sessions(limit: int = 5) -> List[Dict[str, Any]]:
    engine = _get_db()
    if engine is None:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text('SELECT session_id, first_message_summary, created_at FROM chat_sessions ORDER BY created_at DESC LIMIT :limit'),
                {'limit': limit}
            ).fetchall()
        return [{'sessionId': r.session_id, 'summary': r.first_message_summary,
                 'createdAt': r.created_at.isoformat() if r.created_at else None} for r in rows]
    except Exception:
        return []


def _fetch_session_messages(session_id: str) -> List[Dict[str, Any]]:
    engine = _get_db()
    if engine is None:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text('SELECT user_message, bot_response, timestamp FROM conversation_history WHERE session_id = :sid ORDER BY timestamp ASC'),
                {'sid': session_id}
            ).fetchall()
        msgs = []
        for row in rows:
            ts = row.timestamp.isoformat() if getattr(row, 'timestamp', None) else None
            if getattr(row, 'user_message', None):
                msgs.append({'role': 'user', 'content': row.user_message, 'timestamp': ts})
            if getattr(row, 'bot_response', None):
                msgs.append({'role': 'assistant', 'content': row.bot_response, 'timestamp': ts})
        return msgs
    except Exception:
        return []


def init_document_suggestion():
    """Alias để server.py preload vẫn hoạt động."""
    return init_suggest()


# ── Routes ─────────────────────────────────────────────────────────────────────
@rag_bp.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or '').strip()
    session_id = payload.get('sessionId') or None
    intent = (payload.get('intent') or '').strip().lower()
    speak = bool(payload.get('speak') or payload.get('tts') or os.getenv('CHATBOT_TTS', '0') == '1')

    if not user_message:
        return jsonify({'success': False, 'message': 'message is required'}), 400

    start_time = time.perf_counter()

    # ── Phát hiện câu hỏi về giấy tờ / thủ tục (không cần gọi RAG agent) ──────
    _DOC_QUERY_RE = re.compile(
        r'(cần giấy tờ gì|cần những gì|hồ sơ gồm|giấy tờ cần|chuẩn bị gì'
        r'|thủ tục gồm|cần photo|cần bản sao|tài liệu nào|điều kiện gì'
        r'|làm thủ tục gì|thủ tục nào|gợi ý thủ tục)',
        re.IGNORECASE,
    )

    if intent == 'document_suggestion' or (intent == '' and _DOC_QUERY_RE.search(user_message)):
        try:
            from services.suggest_service import suggest_with_requirements, format_for_chat
            sug_result  = suggest_with_requirements(user_message, top_k=4, threshold=0.4)
            final_answer = format_for_chat(sug_result.get('suggestions', []))
            if not sug_result.get('suggestions'):
                # Fallback: dùng suggest_procedures cũ
                suggestion_result = suggest_procedures(user_message)
                final_answer = suggestion_result.get('explanation', 'Không tìm thấy thủ tục phù hợp.')
            raw_analysis    = {'mode': 'document_suggestion_with_requirements'}
            raw_tool_results = sug_result
        except Exception as _sug_exc:
            log.warning(f'[rag/chat] suggest_with_requirements failed: {_sug_exc}')
            suggestion_result = suggest_procedures(user_message)
            final_answer     = suggestion_result['explanation']
            raw_analysis     = {'mode': 'document_suggestion'}
            raw_tool_results  = suggestion_result
    else:
        try:
            agent = _get_agent()
        except Exception as exc:
            log.error(f'[rag/chat] Failed to initialize agent: {exc}', exc_info=True)
            return jsonify({'success': False, 'message': f'Failed to initialize agent: {exc}'}), 500
        try:
            state = agent.create_new_state(user_question=user_message, session_id=session_id or '')
            result = agent.run(state)
        except Exception as exc:
            err_str = str(exc)
            is_quota = '429' in err_str or 'quota' in err_str.lower() or 'ResourceExhausted' in type(exc).__name__
            if is_quota:
                log.warning('[rag/chat] Gemini quota exceeded.')
                return jsonify({'success': False, 'message': 'Hệ thống AI đang quá tải, vui lòng thử lại sau ít phút.', 'code': 'quota_exceeded'}), 503
            log.error('[rag/chat] Agent execution failed: %s', exc, exc_info=True)
            return jsonify({'success': False, 'message': 'Xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.'}), 500

        final_answer = result.get('final_answer') or 'Xin lỗi, tôi chưa thể trả lời câu hỏi này.'
        raw_analysis = result.get('llm_analysis')
        raw_tool_results = result.get('tool_results')

    def _safe_json(v: Any) -> Any:
        try:
            json.dumps(v, ensure_ascii=False)
            return v
        except (TypeError, ValueError):
            return _clean_docs(v)

    llm_analysis = _safe_json(raw_analysis)
    tool_results = _safe_json(raw_tool_results)
    warnings: List[str] = []
    stored_session_id = session_id

    try:
        source = raw_analysis if raw_analysis is not None else raw_tool_results
        intermediate_str = _clean_docs(source if source is not None else [])
        result_sid = _log_chat(session_id, user_message, final_answer, intermediate_str)
        if result_sid:
            stored_session_id = result_sid
    except Exception as exc:
        log.warning(f'[rag/chat] DB log failed: {exc}', exc_info=True)
        warnings.append(str(exc))

    audio_obj = None
    if speak and final_answer:
        audio_b64 = _tts_mp3_base64(final_answer)
        if audio_b64:
            audio_obj = {'mimeType': 'audio/mpeg', 'base64': audio_b64}

    response_payload: Dict[str, Any] = {
        'success': True,
        'data': {
            'sessionId': stored_session_id,
            'response': final_answer,
            'analysis': llm_analysis,
            'toolResults': tool_results,
            'latencyMs': round((time.perf_counter() - start_time) * 1000, 2),
            **({'audio': audio_obj} if audio_obj else {}),
        },
    }
    if warnings:
        response_payload['warnings'] = warnings
    return jsonify(response_payload)


@rag_bp.route('/api/rag/sessions', methods=['GET'])
def rag_sessions():
    limit = request.args.get('limit', default=5, type=int)
    if not limit or limit <= 0:
        limit = 5
    try:
        sessions = _fetch_recent_sessions(limit)
    except Exception as exc:
        log.error(f'[rag/sessions] {exc}', exc_info=True)
        return jsonify({'success': False, 'message': str(exc)}), 500
    return jsonify({'success': True, 'data': {'sessions': sessions}})


@rag_bp.route('/api/rag/sessions/<session_id>', methods=['GET'])
def rag_session_messages(session_id: str):
    if not session_id:
        return jsonify({'success': False, 'message': 'sessionId is required'}), 400
    try:
        messages = _fetch_session_messages(session_id)
    except Exception as exc:
        log.error(f'[rag/session_messages] {exc}', exc_info=True)
        return jsonify({'success': False, 'message': str(exc)}), 500
    return jsonify({'success': True, 'data': {'sessionId': session_id, 'messages': messages}})


@rag_bp.route('/api/suggest-procedure', methods=['POST'])
def api_suggest_procedure():
    payload = request.get_json(silent=True) or {}
    query = (payload.get('query') or '').strip()
    top_k = int(payload.get('topK') or 4)
    threshold = float(payload.get('threshold') or 0.5)
    session_id = (payload.get('sessionId') or '').strip() or None

    if not query:
        return jsonify({'success': False, 'message': 'query is required'}), 400

    start_time = time.perf_counter()
    result = suggest_procedures(query=query, top_k=top_k, threshold=threshold)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if result.get('error'):
        return jsonify({'success': False, 'error': result['error'],
                        'message': result.get('explanation'), 'latencyMs': latency_ms}), 200

    suggestions = result.get('suggestions', [])
    expl = result.get('explanation', '')
    if suggestions:
        lines = [f"{i}. {s.get('procedure_name') or 'Không rõ tên thủ tục'}" for i, s in enumerate(suggestions, 1)]
        response_text = f'{expl}\n' + '\n'.join(lines)
    else:
        response_text = f'{expl}\nKhông có gợi ý phù hợp.' if expl else 'Không có gợi ý phù hợp.'

    try:
        new_sid = _log_chat(session_id, query, response_text, json.dumps(suggestions, ensure_ascii=False))
    except Exception:
        new_sid = session_id

    return jsonify({
        'success': True,
        'data': {
            'suggestions': suggestions,
            'explanation': expl,
            'totalCandidates': result.get('total_candidates', 0),
            'latencyMs': latency_ms,
            'sessionId': new_sid,
        },
    })
