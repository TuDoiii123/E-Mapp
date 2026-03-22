"""
RAG / chatbot routes: chat, session history, procedure suggestion.
"""
import json
import os
import re
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

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    import pandas as pd
    import torch
except Exception:
    SentenceTransformer = None  # type: ignore
    cos_sim = None  # type: ignore
    pd = None  # type: ignore
    torch = None  # type: ignore

rag_bp = Blueprint('rag', __name__)

VN_TZ = timezone(timedelta(hours=7))

# ── Lazy singletons ────────────────────────────────────────────────────────────
_agent_graph: Optional[MultiRoleAgentGraph] = None
_db_engine = None
_doc_model = None
_doc_df = None
_doc_embeddings = None
_rank_df = None
_query_map: Dict[str, List[Dict[str, Any]]] = {}


def _get_agent() -> MultiRoleAgentGraph:
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = MultiRoleAgentGraph()
    return _agent_graph


def _get_db():
    global _db_engine
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
                    text('INSERT INTO ChatSessions (SessionId, FirstMessageSummary, CreatedAt) VALUES (:sid, :summary, :ts)'),
                    {'sid': sid, 'summary': summary, 'ts': timestamp},
                )
            result = conn.execute(
                text('''INSERT INTO dbo.conversation_history (session_id, user_message, bot_response, timestamp)
                        OUTPUT INSERTED.id VALUES (:sid, :user_msg, :bot_res, :ts)'''),
                {'sid': sid, 'user_msg': user_query, 'bot_res': ai_response, 'ts': timestamp},
            )
            conv_id = result.scalar_one()
            conn.execute(
                text('''INSERT INTO dbo.query_results (conversation_id, query_text, response_text, retrieved_docs, model_name, timestamp)
                        VALUES (:conv_id, :q_text, :res_text, :r_docs, :model, :ts)'''),
                {'conv_id': conv_id, 'q_text': user_query, 'res_text': ai_response,
                 'r_docs': intermediate_steps, 'model': 'gemini-2.0-flash', 'ts': timestamp},
            )
    except SQLAlchemyError as exc:
        print(f'[rag] DB log failed: {exc}')
        return None

    return sid


def _fetch_recent_sessions(limit: int = 5) -> List[Dict[str, Any]]:
    engine = _get_db()
    if engine is None:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text('SELECT TOP (:limit) SessionId, FirstMessageSummary, CreatedAt FROM dbo.ChatSessions ORDER BY CreatedAt DESC'),
                {'limit': limit}
            ).fetchall()
        return [{'sessionId': r.SessionId, 'summary': r.FirstMessageSummary,
                 'createdAt': r.CreatedAt.isoformat() if r.CreatedAt else None} for r in rows]
    except Exception:
        return []


def _fetch_session_messages(session_id: str) -> List[Dict[str, Any]]:
    engine = _get_db()
    if engine is None:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text('SELECT user_message, bot_response, timestamp FROM dbo.conversation_history WHERE session_id = :sid ORDER BY timestamp ASC'),
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


# ── SuggestProcedure ───────────────────────────────────────────────────────────
def init_document_suggestion():
    global _doc_model, _doc_df, _doc_embeddings, _rank_df, _query_map
    if _doc_model is not None and _doc_df is not None and _doc_embeddings is not None:
        return _doc_model, _doc_df, _doc_embeddings

    if SentenceTransformer is None or pd is None:
        raise RuntimeError('sentence-transformers / pandas not installed.')

    base_dir = os.path.dirname(os.path.dirname(__file__))  # Backend/
    csv_path = os.path.join(base_dir, 'SuggestProcedure', 'data', 'dichvucong_QuangNinh - dichvucong_QuangNinh.csv')
    model_path = os.path.join(base_dir, 'SuggestProcedure', 'model', 'fine_tuned_model')
    rank_path = os.path.join(base_dir, 'SuggestProcedure', 'data', 'query_procedure_ranking_quangninh.csv')

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}')

    fine_tuned_available = os.path.isdir(model_path)
    if not fine_tuned_available:
        print(f'[SuggestProcedure][WARN] Fine-tuned model not found: {model_path}')

    try:
        _doc_df = pd.read_csv(csv_path)
        if 'NAME' not in _doc_df.columns:
            raise RuntimeError("CSV missing 'NAME' column")

        if _rank_df is None and os.path.isfile(rank_path):
            try:
                _rank_df = pd.read_csv(rank_path)
                cols_lower = [c.lower() for c in _rank_df.columns]
                rename_map = {}
                for c in _rank_df.columns:
                    cl = c.lower()
                    if cl == 'relevance':
                        rename_map[c] = 'label'
                    elif cl in ('query_id', 'query_text', 'procedure_id', 'procedure_code', 'procedure_name'):
                        rename_map[c] = cl
                if rename_map:
                    _rank_df.rename(columns=rename_map, inplace=True)
                required_cols = {'query_text', 'procedure_id', 'procedure_name', 'label'}
                if not required_cols.issubset(set(_rank_df.columns)):
                    raise RuntimeError(f"Ranking CSV missing columns: {list(_rank_df.columns)}")
                _rank_df['label'] = pd.to_numeric(_rank_df['label'], errors='coerce')
                pos_rows = _rank_df[_rank_df['label'].fillna(0) > 0]
                for _, row in pos_rows.iterrows():
                    qtxt = str(row.get('query_text', '')).strip()
                    if not qtxt:
                        continue
                    key = re.sub(r'[^\w\s]', '', qtxt.lower()).strip()
                    _query_map.setdefault(key, []).append({
                        'procedure_id': row.get('procedure_id'),
                        'procedure_code': row.get('procedure_code'),
                        'procedure_name': row.get('procedure_name'),
                        'label': int(row.get('label', 1)),
                    })
                print(f'[SuggestProcedure] Query map built: {len(_query_map)} queries')
            except Exception as r_exc:
                print(f'[SuggestProcedure][WARN] Ranking CSV failed: {r_exc}')

        if fine_tuned_available:
            needed = ['config.json', 'model.safetensors', 'bpe.codes']
            if any(not os.path.isfile(os.path.join(model_path, f)) for f in needed):
                fine_tuned_available = False
                print('[SuggestProcedure][WARN] Fine-tuned model incomplete -> fallback')

        model_name = model_path if fine_tuned_available else 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        _doc_model = SentenceTransformer(model_name)
        names = _doc_df['NAME'].astype(str).tolist()
        _doc_embeddings = _doc_model.encode(names, convert_to_tensor=True)
        print('[SuggestProcedure] Embeddings ready')

    except Exception as exc:
        print(f'[SuggestProcedure][ERROR] {exc}\n{traceback.format_exc()}')
        fallback = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        try:
            _doc_model = SentenceTransformer(fallback)
            if _doc_df is None:
                _doc_df = pd.DataFrame({'ID': [], 'NAME': []})
            names = _doc_df['NAME'].astype(str).tolist()
            _doc_embeddings = _doc_model.encode(names or ['placeholder'], convert_to_tensor=True)
            print('[SuggestProcedure][FALLBACK] Ready')
        except Exception as fb_exc:
            print(f'[SuggestProcedure][FALLBACK][ERROR] {fb_exc}')
            _doc_model = _doc_df = _doc_embeddings = None
            raise

    return _doc_model, _doc_df, _doc_embeddings


def suggest_procedures(query: str, top_k: int = 4, threshold: float = 0.5) -> Dict[str, Any]:
    try:
        model, df, embeddings = init_document_suggestion()
        if model is None or df is None or embeddings is None:
            return {'suggestions': [], 'explanation': 'Model not initialized', 'error': 'init_failed'}

        link_base = os.getenv('PROCEDURE_LINK_BASE', 'https://dichvucong.gov.vn/thu-tuc/')

        def _build_link(pid: Any, name: str) -> str:
            slug = re.sub(r'[^a-zA-Z0-9\- ]', '', name.lower()).strip().replace(' ', '-')
            return f'{link_base}{pid}-{slug}' if pid and str(pid).strip() else f'{link_base}{slug}'

        norm_q = re.sub(r'[^\w\s]', '', query.lower()).strip()
        label_hits = _query_map.get(norm_q, [])
        suggestions: List[Dict[str, Any]] = []
        for hit in label_hits[:top_k]:
            pid = hit.get('procedure_id')
            pname = hit.get('procedure_name')
            suggestions.append({
                'procedure_internal_id': pid,
                'procedure_name': pname,
                'procedure_code': hit.get('procedure_code'),
                'label': hit.get('label'),
                'similarity_score': 1.0,
                'source': 'ranking_label',
                'link': _build_link(pid, str(pname)),
            })

        remaining = top_k - len(suggestions)
        if remaining > 0:
            q_emb = model.encode(query, convert_to_tensor=True)
            scores = cos_sim(q_emb, embeddings)[0].cpu().numpy().tolist()
            existing_names = {s['procedure_name'] for s in suggestions}
            scored = sorted(
                [{'procedure_internal_id': int(df['ID'].iloc[i]) if 'ID' in df.columns else i,
                  'procedure_name': df['NAME'].iloc[i],
                  'procedure_code': None, 'label': None,
                  'similarity_score': round(float(s), 4), 'source': 'embedding',
                  'link': _build_link(int(df['ID'].iloc[i]) if 'ID' in df.columns else i, str(df['NAME'].iloc[i]))}
                 for i, s in enumerate(scores) if s >= threshold],
                key=lambda x: x['similarity_score'], reverse=True,
            )
            for item in scored:
                if item['procedure_name'] not in existing_names:
                    suggestions.append(item)
                if len(suggestions) >= top_k:
                    break

        explanation = 'Không tìm thấy thủ tục phù hợp.' if not suggestions else 'Các thủ tục liên quan được đề xuất.'
        return {'suggestions': suggestions, 'explanation': explanation, 'total_candidates': len(suggestions)}
    except Exception as exc:
        return {'suggestions': [], 'explanation': f'Lỗi: {exc}', 'error': 'exception'}


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

    if intent == 'document_suggestion':
        suggestion_result = suggest_procedures(user_message)
        final_answer = suggestion_result['explanation']
        raw_analysis = {'mode': 'document_suggestion'}
        raw_tool_results = suggestion_result
    else:
        try:
            agent = _get_agent()
        except Exception as exc:
            return jsonify({'success': False, 'message': f'Failed to initialize agent: {exc}'}), 500
        try:
            state = agent.create_new_state(user_question=user_message, session_id=session_id or '')
            result = agent.run(state)
        except Exception as exc:
            return jsonify({'success': False, 'message': f'Agent execution failed: {exc}'}), 500

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
        return jsonify({'success': False, 'message': str(exc)}), 500
    return jsonify({'success': True, 'data': {'sessions': sessions}})


@rag_bp.route('/api/rag/sessions/<session_id>', methods=['GET'])
def rag_session_messages(session_id: str):
    if not session_id:
        return jsonify({'success': False, 'message': 'sessionId is required'}), 400
    try:
        messages = _fetch_session_messages(session_id)
    except Exception as exc:
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
