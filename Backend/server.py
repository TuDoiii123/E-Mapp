import json
import os
import re
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from middleware.auth import init_auth
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from RAG.agent_core.graph import MultiRoleAgentGraph
import traceback
from RAG.connect_SQL.connect_SQL import connect_sql

# SuggestProcedure lazy resources
try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    import pandas as pd
    import torch
except Exception:
    # Modules may not be installed yet; handled during first suggest request
    SentenceTransformer = None  # type: ignore
    cos_sim = None  # type: ignore
    pd = None  # type: ignore
    torch = None  # type: ignore

# Load environment variables from .env
load_dotenv()


agent_graph: Optional[MultiRoleAgentGraph] = None
db_engine = None
VN_TZ = timezone(timedelta(hours=7))

# Initialize Flask app early to allow route decorators below
app = Flask(__name__)
# CORS for frontend origins (include common Vite ports)
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"]}},
    supports_credentials=True,
)

# Globals for document suggestion mode
_doc_model: Optional[SentenceTransformer] = None  # type: ignore
_doc_df: Optional['pd.DataFrame'] = None  # type: ignore
_doc_embeddings = None  # torch.Tensor | None
_doc_lock = None  # simple sentinel (we could use threading.Lock if needed)
_rank_df: Optional['pd.DataFrame'] = None  # query-procedure relevance data
_query_map: Dict[str, List[Dict[str, Any]]] = {}


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

# ==========================
# Appointments (Đặt lịch) API via Flask
# ==========================

APPOINTMENTS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'appointments.json')

def _read_appointments() -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(APPOINTMENTS_FILE):
            os.makedirs(os.path.dirname(APPOINTMENTS_FILE), exist_ok=True)
            with open(APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        with open(APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _write_appointments(items: List[Dict[str, Any]]) -> None:
    with open(APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def _is_valid_time(t: str) -> bool:
    return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', t))

def _is_valid_date(d: str) -> bool:
    try:
        datetime.strptime(d, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/api/appointments', methods=['OPTIONS'])
def appointments_options_root():
    return ('', 204)

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        payload = request.get_json(silent=True) or {}
        print('[appointments][POST] payload:', payload)
        agency_id = payload.get('agencyId')
        service_code = payload.get('serviceCode')
        date_str = payload.get('date')
        time_str = payload.get('time')

        errors: List[Dict[str, str]] = []
        if not agency_id:
            errors.append({'msg': 'Cơ quan là bắt buộc', 'param': 'agencyId'})
        if not service_code:
            errors.append({'msg': 'Dịch vụ là bắt buộc', 'param': 'serviceCode'})
        if not date_str or not _is_valid_date(date_str):
            errors.append({'msg': 'Ngày không hợp lệ', 'param': 'date'})
        if not time_str or not _is_valid_time(time_str):
            errors.append({'msg': 'Thời gian không hợp lệ (HH:mm)', 'param': 'time'})
        if errors:
            return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ', 'errors': errors}), 400

        # Build naive datetime from date and time strings
        try:
            appointment_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except Exception as parse_exc:
            return jsonify({'success': False, 'message': f'Dữ liệu thời gian không hợp lệ: {parse_exc}'}), 400
        # Compare naive datetimes to avoid offset-naive vs offset-aware error
        now_naive = datetime.now()
        if appointment_dt < now_naive:
            return jsonify({'success': False, 'message': 'Không thể đặt lịch trong quá khứ'}), 400

        items = _read_appointments()
        same_date = [apt for apt in items if apt.get('agencyId') == agency_id and apt.get('date') == date_str]
        same_time_count = len([apt for apt in same_date if apt.get('time') == time_str])
        if same_time_count >= 5:
            return jsonify({'success': False, 'message': f'Thời điểm {time_str} ngày {date_str} đã đầy'}), 409

        new_item = {
            'id': f"apt-{int(time.time()*1000)}",
            'userId': payload.get('userId') or f"demo-user-{int(time.time()*1000)}",
            'agencyId': agency_id,
            'serviceCode': service_code,
            'date': date_str,
            'time': time_str,
            'status': payload.get('status') or 'pending',
        }
        items.append(new_item)
        _write_appointments(items)

        return jsonify({'success': True, 'message': 'Đặt lịch hẹn thành công', 'data': new_item}), 201
    except Exception as exc:
        import traceback as _tb
        print('[appointments][POST][ERROR]', exc)
        print(_tb.format_exc())
        return jsonify({'success': False, 'message': f'Lỗi khi tạo lịch hẹn: {exc}'}), 500

@app.route('/api/appointments/by-date', methods=['OPTIONS'])
def appointments_options_bydate():
    return ('', 204)

@app.route('/api/appointments/by-date', methods=['GET'])
def get_appointments_by_date():
    try:
        agency_id = request.args.get('agencyId')
        date_str = request.args.get('date')
        if not agency_id or not date_str:
            return jsonify({'success': False, 'message': 'Thiếu thông tin cơ quan hoặc ngày'}), 400
        items = _read_appointments()
        filtered = [apt for apt in items if apt.get('agencyId') == agency_id and apt.get('date') == date_str]
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công', 'data': {'appointments': filtered}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500

@app.route('/api/appointments/all', methods=['OPTIONS'])
def appointments_options_all():
    return ('', 204)

@app.route('/api/appointments/all', methods=['GET'])
def get_all_appointments():
    try:
        items = _read_appointments()
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công', 'data': {'appointments': items}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500

@app.route('/api/appointments/upcoming', methods=['OPTIONS'])
def appointments_options_upcoming():
    return ('', 204)

@app.route('/api/appointments/upcoming', methods=['GET'])
def get_upcoming_appointments():
    try:
        items = _read_appointments()
        now_naive = datetime.now()
        def _to_dt(a):
            try:
                return datetime.strptime(f"{a.get('date')} {a.get('time')}", '%Y-%m-%d %H:%M')
            except Exception:
                return None
        upcoming = [a for a in items if a.get('date') and a.get('time') and (_to_dt(a) and _to_dt(a) >= now_naive)]
        upcoming.sort(key=lambda a: _to_dt(a) or datetime.max)
        return jsonify({'success': True, 'message': 'Danh sách lịch hẹn sắp tới', 'data': {'appointments': upcoming}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy lịch hẹn sắp tới: {exc}'}), 500

# app already initialized at top of file

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


def _init_document_suggestion() -> Tuple[Optional[SentenceTransformer], Optional['pd.DataFrame'], Any]:  # returns (model, df, embeddings)
    global _doc_model, _doc_df, _doc_embeddings
    if _doc_model is not None and _doc_df is not None and _doc_embeddings is not None:
        return _doc_model, _doc_df, _doc_embeddings

    if SentenceTransformer is None or pd is None:
        raise RuntimeError("sentence-transformers / pandas not installed. Please install requirements.")

    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'SuggestProcedure', 'data', 'dichvucong_QuangNinh - dichvucong_QuangNinh.csv')
    model_path = os.path.join(base_dir, 'SuggestProcedure', 'model', 'fine_tuned_model')
    rank_path = os.path.join(base_dir, 'SuggestProcedure', 'data', 'query_procedure_ranking_quangninh.csv')
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f'CSV file not found: {csv_path}')
    fine_tuned_available = True
    if not os.path.isdir(model_path):
        print(f'[SuggestProcedure][WARN] Fine-tuned model directory not found: {model_path} -> will attempt fallback')
        fine_tuned_available = False
    if not os.path.isfile(rank_path):
        print(f'[SuggestProcedure][WARN] Ranking file missing: {rank_path} (query->procedure mapping disabled)')
    try:
        # Version sanity check before heavy init
        try:
            import sentence_transformers as st_lib  # type: ignore
            installed_version = getattr(st_lib, '__version__', 'unknown')
            required_version = '5.1.2'
            if installed_version != 'unknown':
                print(f"[SuggestProcedure] sentence-transformers installed: {installed_version}")
                if installed_version < required_version:
                    print(f"[SuggestProcedure][WARN] Model created with {required_version} but installed {installed_version}. Consider upgrading.")
        except Exception as ver_exc:
            print(f"[SuggestProcedure][WARN] Could not verify sentence-transformers version: {ver_exc}")
        print(f"[SuggestProcedure] Loading procedure CSV: {csv_path}")
        _doc_df = pd.read_csv(csv_path)
        if 'NAME' not in _doc_df.columns:
            raise RuntimeError("CSV missing required 'NAME' column")
        print(f"[SuggestProcedure] Rows loaded: {len(_doc_df)}")
        # Load ranking dataset (optional)
        global _rank_df, _query_map
        if _rank_df is None and os.path.isfile(rank_path):
            try:
                print(f"[SuggestProcedure] Loading ranking CSV: {rank_path}")
                _rank_df = pd.read_csv(rank_path)
                # Standardize column names if 'relevance' exists
                cols_lower = [c.lower() for c in _rank_df.columns]
                if 'relevance' in cols_lower and 'label' not in cols_lower:
                    # rename relevance -> label
                    rename_map = {}
                    for c in _rank_df.columns:
                        if c.lower() == 'relevance':
                            rename_map[c] = 'label'
                        elif c.lower() == 'query_id':
                            rename_map[c] = 'query_id'
                        elif c.lower() == 'query_text':
                            rename_map[c] = 'query_text'
                        elif c.lower() == 'procedure_id':
                            rename_map[c] = 'procedure_id'
                        elif c.lower() == 'procedure_code':
                            rename_map[c] = 'procedure_code'
                        elif c.lower() == 'procedure_name':
                            rename_map[c] = 'procedure_name'
                    _rank_df.rename(columns=rename_map, inplace=True)
                # Ensure required columns exist
                required_cols = {'query_text','procedure_id','procedure_name','label'}
                if not required_cols.issubset(set(_rank_df.columns)):
                    raise RuntimeError(f"Ranking CSV missing required columns. Found: {list(_rank_df.columns)}")
                # Build normalized query map of positives (label >0)
                def simple_norm(s: str) -> str:
                    return re.sub(r"[^\w\s]","", str(s).lower()).strip()
                pos_rows = _rank_df.copy()
                # Coerce label to numeric
                pos_rows['label'] = pd.to_numeric(pos_rows['label'], errors='coerce')
                pos_rows = pos_rows[pos_rows['label'].fillna(0) > 0]
                for _, row in pos_rows.iterrows():
                    qtxt = str(row.get('query_text','')).strip()
                    if not qtxt:
                        continue
                    key = simple_norm(qtxt)
                    entry = {
                        'procedure_id': row.get('procedure_id'),
                        'procedure_code': row.get('procedure_code'),
                        'procedure_name': row.get('procedure_name'),
                        'label': int(row.get('label',1))
                    }
                    _query_map.setdefault(key, []).append(entry)
                print(f"[SuggestProcedure] Query map built: {len(_query_map)} positive queries")
            except Exception as r_exc:
                print(f"[SuggestProcedure][WARN] Failed loading ranking CSV: {r_exc}")
        # Validate fine-tuned model directory contents before loading
        if fine_tuned_available:
            needed_files = ['config.json','model.safetensors','bpe.codes']  # minimal set
            missing = [f for f in needed_files if not os.path.isfile(os.path.join(model_path,f))]
            if missing:
                print(f"[SuggestProcedure][WARN] Fine-tuned model missing files {missing} -> skip to fallback")
                fine_tuned_available = False
        if fine_tuned_available:
            print(f"[SuggestProcedure] Loading model: {model_path}")
            _doc_model = SentenceTransformer(model_path)
        else:
            print(f"[SuggestProcedure] Using fallback model directly due to unavailable fine-tuned model")
            _doc_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        names = _doc_df['NAME'].astype(str).tolist()
        print(f"[SuggestProcedure] Encoding {len(names)} procedure names")
        _doc_embeddings = _doc_model.encode(names, convert_to_tensor=True)
        print("[SuggestProcedure] Embeddings ready")
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"[SuggestProcedure][ERROR] Initialization failed: {exc}\n{tb}")
        # Attempt fallback public model
        fallback_model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        try:
            print(f"[SuggestProcedure][FALLBACK] Trying fallback model: {fallback_model_name}")
            _doc_model = SentenceTransformer(fallback_model_name)
            # If CSV loaded before failing at model load, keep rows; else create minimal placeholder
            if _doc_df is None:
                _doc_df = pd.DataFrame({'ID': [], 'NAME': []})
            names = _doc_df['NAME'].astype(str).tolist()
            if names:
                _doc_embeddings = _doc_model.encode(names, convert_to_tensor=True)
            else:
                _doc_embeddings = _doc_model.encode(["placeholder"], convert_to_tensor=True)
            print("[SuggestProcedure][FALLBACK] Fallback embeddings ready")
        except Exception as fb_exc:
            print(f"[SuggestProcedure][FALLBACK][ERROR] Fallback model also failed: {fb_exc}\n{traceback.format_exc()}")
            _doc_model = None
            _doc_df = None
            _doc_embeddings = None
            raise
    return _doc_model, _doc_df, _doc_embeddings


def suggest_procedures(query: str, top_k: int = 4, threshold: float = 0.5) -> Dict[str, Any]:
    try:
        model, df, embeddings = _init_document_suggestion()
        if model is None or df is None or embeddings is None:
            return {"suggestions": [], "explanation": "Model not initialized", "error": "init_failed"}
        # Link base config and LLM enrichment toggle
        link_base = os.getenv('PROCEDURE_LINK_BASE', 'https://dichvucong.gov.vn/thu-tuc/')
        enable_llm = os.getenv('ENABLE_LLM_LINK_ENRICH', '0') == '1'

        def build_link(procedure_id: Any, name: str) -> str:
            # Basic slug generation from name
            slug = re.sub(r'[^a-zA-Z0-9\- ]', '', name.lower()).strip().replace(' ', '-')
            if procedure_id is None or str(procedure_id).strip() == '':
                return f"{link_base}{slug}"  # fallback without id
            return f"{link_base}{procedure_id}-{slug}"

        def llm_enrich_link(raw_link: str, proc_name: str) -> str:
            if not enable_llm:
                return raw_link
            try:
                agent = get_agent_graph()
                prompt = f"Cho biết URL chính thức (nếu tồn tại) của thủ tục hành chính: '{proc_name}'. Nếu không chắc chắn, giữ nguyên: {raw_link}. Chỉ trả về một URL duy nhất."  # Vietnamese prompt
                state = agent.create_new_state(user_question=prompt, session_id='')
                result = agent.run(state)
                answer = (result.get('final_answer') or '').strip()
                # Simple URL extraction
                m = re.search(r'https?://\S+', answer)
                if m:
                    return m.group(0)
                return raw_link
            except Exception:
                return raw_link
        # 1. Direct label-based lookup from ranking file if available
        global _query_map
        def simple_norm(s: str) -> str:
            return re.sub(r"[^\w\s]","", s.lower()).strip()
        norm_q = simple_norm(query)
        label_hits = _query_map.get(norm_q, [])
        suggestions: List[Dict[str, Any]] = []
        if label_hits:
            # Prioritize labeled positives
            for hit in label_hits[:top_k]:
                pid = hit.get('procedure_id')
                pname = hit.get('procedure_name')
                raw_link = build_link(pid, str(pname))
                enriched_link = llm_enrich_link(raw_link, str(pname))
                suggestions.append({
                    'procedure_internal_id': pid,
                    'procedure_name': pname,
                    'procedure_code': hit.get('procedure_code'),
                    'label': hit.get('label'),
                    'similarity_score': 1.0,
                    'source': 'ranking_label',
                    'link': enriched_link
                })
        # 2. Embedding similarity (augment / fill if needed)
        remaining = top_k - len(suggestions)
        if remaining > 0:
            q_emb = model.encode(query, convert_to_tensor=True)
            scores = cos_sim(q_emb, embeddings)[0].cpu().numpy().tolist()
            scored = []
            for idx, score in enumerate(scores):
                if score >= threshold:
                    pid = int(df['ID'].iloc[idx]) if 'ID' in df.columns else idx
                    pname = df['NAME'].iloc[idx]
                    raw_link = build_link(pid, str(pname))
                    enriched_link = llm_enrich_link(raw_link, str(pname))
                    scored.append({
                        'procedure_internal_id': pid,
                        'procedure_name': pname,
                        'procedure_code': None,
                        'label': None,
                        'similarity_score': round(float(score), 4),
                        'source': 'embedding',
                        'link': enriched_link
                    })
            scored.sort(key=lambda x: x['similarity_score'], reverse=True)
            # Avoid duplicates (if ranking already added same procedure_name)
            existing_names = {s['procedure_name'] for s in suggestions}
            for item in scored:
                if item['procedure_name'] not in existing_names:
                    suggestions.append(item)
                if len(suggestions) >= top_k:
                    break
        explanation = 'Không tìm thấy thủ tục phù hợp.' if not suggestions else 'Các thủ tục liên quan được đề xuất.'
        return {
            'suggestions': suggestions,
            'explanation': explanation,
            'total_candidates': len(suggestions)
        }
    except Exception as exc:
        return {"suggestions": [], "explanation": f"Lỗi khởi tạo hoặc truy vấn: {exc}", "error": "exception"}


@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or '').strip()
    session_id = payload.get('sessionId') or None
    intent = (payload.get('intent') or '').strip().lower()

    if not user_message:
        return jsonify({'success': False, 'message': 'message is required'}), 400

    start_time = time.perf_counter()

    if intent == 'document_suggestion':
        # Fast path: use local embedding search instead of full agent graph
        try:
            suggestion_result = suggest_procedures(user_message)
            final_answer = suggestion_result['explanation']
            raw_analysis = {'mode': 'document_suggestion'}
            raw_tool_results = suggestion_result
        except Exception as exc:
            final_answer = f'Không thể gợi ý giấy tờ: {exc}'
            raw_analysis = None
            raw_tool_results = None
    else:
        try:
            agent = get_agent_graph()
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


@app.route('/api/suggest-procedure', methods=['POST'])
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
        # Return 200 with structured failure (frontend can display explanation)
        return jsonify({
            'success': False,
            'error': result.get('error'),
            'message': result.get('explanation'),
            'latencyMs': latency_ms
        }), 200
    # Build a single text response for logging if we are integrating with history
    suggestions = result.get('suggestions', [])
    expl = result.get('explanation', '')
    if suggestions:
        lines = []
        for idx, s in enumerate(suggestions, start=1):
            name = s.get('procedure_name') or 'Không rõ tên thủ tục'
            lines.append(f"{idx}. {name}")
        response_text = f"{expl}\n" + "\n".join(lines)
    else:
        response_text = f"{expl}\nKhông có gợi ý phù hợp." if expl else 'Không có gợi ý phù hợp.'

    # Log to conversation history similar to RAG
    try:
        new_session_id = log_chat_interaction(session_id, query, response_text, json.dumps(suggestions, ensure_ascii=False))
    except Exception:
        new_session_id = session_id  # fail silent, keep previous

    return jsonify({
        'success': True,
        'data': {
            'suggestions': suggestions,
            'explanation': expl,
            'totalCandidates': result.get('total_candidates', 0),
            'latencyMs': latency_ms,
            'sessionId': new_session_id
        }
    })


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
