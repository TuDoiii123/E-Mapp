import json
import os
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from middleware.auth import init_auth
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from RAG.agent_core.graph import MultiRoleAgentGraph
from RAG.connect_SQL.connect_SQL import connect_sql

# Load environment variables from .env
load_dotenv()


agent_graph: Optional[MultiRoleAgentGraph] = None
db_engine = None
VN_TZ = timezone(timedelta(hours=7))


def get_agent_graph() -> MultiRoleAgentGraph:
    global agent_graph
    if agent_graph is None:
        agent_graph = MultiRoleAgentGraph()
    return agent_graph


def get_db_engine():
    global db_engine
    if db_engine is None:
        db_engine = connect_sql()
    return db_engine


def clean_retrieved_docs(raw_text: Any) -> str:
    if isinstance(raw_text, dict):
        return json.dumps(raw_text, ensure_ascii=False)
    if isinstance(raw_text, list):
        try:
            return json.dumps(raw_text, ensure_ascii=False)
        except TypeError:
            return json.dumps([str(item) for item in raw_text], ensure_ascii=False)
    if isinstance(raw_text, str):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", raw_text.strip())
        try:
            json_obj = json.loads(cleaned)
            return json.dumps(json_obj, ensure_ascii=False)
        except json.JSONDecodeError:
            return cleaned
    return json.dumps(str(raw_text), ensure_ascii=False)


def log_chat_interaction(
    session_id: Optional[str],
    user_query: str,
    ai_response: str,
    intermediate_steps: str,
) -> str:
    engine = get_db_engine()
    if engine is None:
        raise RuntimeError("Database connection is not configured")

    timestamp = datetime.now(VN_TZ).replace(tzinfo=None)
    is_new_session = not session_id
    session_identifier = session_id or f"st_session_{uuid.uuid4()}"

    summary = user_query[:30] + ("..." if len(user_query) > 30 else "")

    try:
        with engine.begin() as conn:
            if is_new_session:
                conn.execute(
                    text(
                        """
                        INSERT INTO ChatSessions (SessionId, FirstMessageSummary, CreatedAt)
                        VALUES (:sid, :summary, :timestamp)
                        """
                    ),
                    {"sid": session_identifier, "summary": summary, "timestamp": timestamp},
                )

            result = conn.execute(
                text(
                    """
                    INSERT INTO dbo.conversation_history (session_id, user_message, bot_response, timestamp)
                    OUTPUT INSERTED.id
                    VALUES (:sid, :user_msg, :bot_res, :timestamp)
                    """
                ),
                {
                    "sid": session_identifier,
                    "user_msg": user_query,
                    "bot_res": ai_response,
                    "timestamp": timestamp,
                },
            )

            conversation_id = result.scalar_one()

            conn.execute(
                text(
                    """
                    INSERT INTO dbo.query_results (conversation_id, query_text, response_text, retrieved_docs, model_name, timestamp)
                    VALUES (:conv_id, :q_text, :res_text, :r_docs, :model, :timestamp)
                    """
                ),
                {
                    "conv_id": conversation_id,
                    "q_text": user_query,
                    "res_text": ai_response,
                    "r_docs": intermediate_steps,
                    "model": "gemini-2.0-flash",
                    "timestamp": timestamp,
                },
            )
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Failed to log conversation: {exc}") from exc

    return session_identifier


def fetch_recent_sessions(limit: int = 5) -> List[Dict[str, Any]]:
    engine = get_db_engine()
    if engine is None:
        return []

    query = text(
        """
        SELECT TOP (:limit) SessionId, FirstMessageSummary, CreatedAt
        FROM dbo.ChatSessions
        ORDER BY CreatedAt DESC
        """
    )

    with engine.connect() as conn:
        rows = conn.execute(query, {"limit": limit}).fetchall()

    return [
        {
            "sessionId": row.SessionId,
            "summary": row.FirstMessageSummary,
            "createdAt": row.CreatedAt.isoformat() if hasattr(row, "CreatedAt") and row.CreatedAt else None,
        }
        for row in rows
    ]


def fetch_session_messages(session_id: str) -> List[Dict[str, Any]]:
    engine = get_db_engine()
    if engine is None:
        return []

    query = text(
        """
        SELECT user_message, bot_response, timestamp
        FROM dbo.conversation_history
        WHERE session_id = :session_id
        ORDER BY timestamp ASC
        """
    )

    with engine.connect() as conn:
        rows = conn.execute(query, {"session_id": session_id}).fetchall()

    messages: List[Dict[str, Any]] = []

    for row in rows:
        if getattr(row, "user_message", None):
            messages.append(
                {
                    "role": "user",
                    "content": row.user_message,
                    "timestamp": row.timestamp.isoformat() if getattr(row, "timestamp", None) else None,
                }
            )
        if getattr(row, "bot_response", None):
            messages.append(
                {
                    "role": "assistant",
                    "content": row.bot_response,
                    "timestamp": row.timestamp.isoformat() if getattr(row, "timestamp", None) else None,
                }
            )

    return messages

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize database (optional PostgreSQL support)
try:
    from models.db import init_db
    init_db(app)
    print('PostgreSQL database initialized')
except Exception as e:
    print(f'Database initialization skipped: {e}')

# Register blueprints (routes) if present
try:
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    print('[OK] auth_routes registered')
except Exception as e:
    print(f'[ERROR] auth_routes failed: {e}')

try:
    from routes.services_routes import services_bp
    app.register_blueprint(services_bp)
    print('[OK] services_routes registered')
except Exception as e:
    print(f'[ERROR] services_routes failed: {e}')

try:
    from routes.applications_routes import applications_bp
    app.register_blueprint(applications_bp)
    print('[OK] applications_routes registered')
except Exception as e:
    print(f'[ERROR] applications_routes failed: {e}')

try:
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    print('[OK] admin_routes registered')
except Exception as e:
    print(f'[ERROR] admin_routes failed: {e}')

# Initialize auth loader
init_auth(app)


@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or '').strip()
    session_id = payload.get('sessionId') or None

    if not user_message:
        return jsonify({'success': False, 'message': 'message is required'}), 400

    try:
        agent = get_agent_graph()
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Failed to initialize agent: {exc}'}), 500

    start_time = time.perf_counter()

    try:
        state = agent.create_new_state(user_question=user_message, session_id=session_id or '')
        result = agent.run(state)
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Agent execution failed: {exc}'}), 500

    final_answer = result.get('final_answer') or 'Xin lỗi, tôi chưa thể trả lời câu hỏi này.'
    raw_analysis = result.get('llm_analysis')
    raw_tool_results = result.get('tool_results')

    llm_analysis: Any = raw_analysis
    if llm_analysis is not None:
        try:
            json.dumps(llm_analysis, ensure_ascii=False)
        except (TypeError, ValueError):
            llm_analysis = clean_retrieved_docs(llm_analysis)

    tool_results: Any = raw_tool_results
    if tool_results is not None:
        try:
            json.dumps(tool_results, ensure_ascii=False)
        except (TypeError, ValueError):
            tool_results = clean_retrieved_docs(tool_results)

    warnings: List[str] = []
    stored_session_id = session_id

    try:
        source_for_logging = raw_analysis if raw_analysis is not None else raw_tool_results
        intermediate_str = clean_retrieved_docs(source_for_logging if source_for_logging is not None else [])
        stored_session_id = log_chat_interaction(
            session_id=session_id,
            user_query=user_message,
            ai_response=final_answer,
            intermediate_steps=intermediate_str,
        )
    except Exception as exc:
        warnings.append(str(exc))

    response_payload: Dict[str, Any] = {
        'success': True,
        'data': {
            'sessionId': stored_session_id,
            'response': final_answer,
            'analysis': llm_analysis,
            'toolResults': tool_results,
            'latencyMs': round((time.perf_counter() - start_time) * 1000, 2),
        },
    }

    if warnings:
        response_payload['warnings'] = warnings

    return jsonify(response_payload)


@app.route('/api/rag/sessions', methods=['GET'])
def rag_sessions():
    limit = request.args.get('limit', default=5, type=int)
    if limit is None or limit <= 0:
        limit = 5

    try:
        sessions = fetch_recent_sessions(limit)
    except Exception as exc:
        return jsonify({'success': False, 'message': str(exc)}), 500

    return jsonify({'success': True, 'data': {'sessions': sessions}})


@app.route('/api/rag/sessions/<session_id>', methods=['GET'])
def rag_session_messages(session_id: str):
    if not session_id:
        return jsonify({'success': False, 'message': 'sessionId is required'}), 400

    try:
        messages = fetch_session_messages(session_id)
    except Exception as exc:
        return jsonify({'success': False, 'message': str(exc)}), 500

    return jsonify({'success': True, 'data': {'sessionId': session_id, 'messages': messages}})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Public Services Backend API',
        'timestamp': None
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Route not found'}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    # Generic error handler
    return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Seed data automatically in development if seed script exists
    if os.getenv('FLASK_ENV', 'development') != 'production':
        try:
            from scripts.seed_data import seed_data
            seed_data()
        except Exception as e:
            print('Error seeding data:', e)

    port = int(os.getenv('PORT', 8888))
    app.run(host='0.0.0.0', port=port)
