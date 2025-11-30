import json
import os
import re
import time
import uuid
import base64
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request, Response, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from middleware.auth import init_auth
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from RAG.agent_core.graph import MultiRoleAgentGraph
try:
    # Optional Google Cloud clients for STT/TTS
    from google.cloud import speech as g_speech  # type: ignore
    from google.cloud import texttospeech as g_tts  # type: ignore
except Exception:
    g_speech = None  # type: ignore
    g_tts = None  # type: ignore
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore
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

# Gemini config (optional)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "models/gemini-2.5-flash-lite")
_gemini_model = None
if GEMINI_API_KEY and genai is not None:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        print("[Gemini] Configured model:", GEMINI_MODEL_NAME)
    except Exception as _g_exc:
        print("[Gemini] Init failed:", _g_exc)

# Initialize Flask app early to allow route decorators below
app = Flask(__name__)
# CORS for frontend origins (include common Vite ports)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://localhost:3001",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True,
            "max_age": 86400,
        }
    },
    supports_credentials=True,
)
# Globals for document suggestion mode
_doc_model: Optional[SentenceTransformer] = None  # type: ignore
_doc_df: Optional['pd.DataFrame'] = None  # type: ignore
_doc_embeddings = None  # torch.Tensor | None
_doc_lock = None  # simple sentinel (we could use threading.Lock if needed)
_rank_df: Optional['pd.DataFrame'] = None  # query-procedure relevance data
_query_map: Dict[str, List[Dict[str, Any]]] = {}

# ==========================
# Simple in-memory dialog store (voice assistant)
# ==========================
class _DialogStep:
    ASK_INTENT = "ASK_INTENT"
    ASK_LOCATION = "ASK_LOCATION"
    ASK_DATE = "ASK_DATE"
    SUGGEST_SLOT = "SUGGEST_SLOT"
    CONFIRM = "CONFIRM"
    DONE = "DONE"


_dialog_store: Dict[str, Dict[str, Any]] = {}
_auto_state_store: Dict[str, Dict[str, Any]] = {}

def _get_speech_client():
    if g_speech is None:
        return None
    try:
        return g_speech.SpeechClient()
    except Exception:
        return None

def _get_tts_client():
    if g_tts is None:
        return None
    try:
        return g_tts.TextToSpeechClient()
    except Exception:
        return None


def _tts_mp3_base64(text: str) -> Optional[str]:
    """Synthesize Vietnamese speech and return base64-encoded MP3 or None if unavailable.
    Prefer ai_voice_backend.services.tts if available to keep logic centralized.
    """
    # Try shared service module first
    try:
        from ai_voice_backend.services.tts import text_to_speech  # type: ignore
        audio_bytes = text_to_speech(text)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('ascii')
    except Exception:
        pass
    # Fallback to direct client
    client = _get_tts_client()
    if client is None:
        return None
    try:
        voice_name = os.getenv('GOOGLE_TTS_VOICE_NAME')
        speaking_rate = float(os.getenv('GOOGLE_TTS_SPEAKING_RATE', '1.0'))
        pitch = float(os.getenv('GOOGLE_TTS_PITCH', '0.0'))
        voice_params = {'language_code': 'vi-VN', 'ssml_gender': g_tts.SsmlVoiceGender.NEUTRAL}
        if voice_name:
            voice_params = {'name': voice_name}
        res = client.synthesize_speech(
            input=g_tts.SynthesisInput(text=text),
            voice=g_tts.VoiceSelectionParams(**voice_params),
            audio_config=g_tts.AudioConfig(
                audio_encoding=g_tts.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
            ),
        )
        return base64.b64encode(res.audio_content).decode('ascii')
    except Exception:
        return None


def _call_gemini_json(prompt: str, tag: str = "GENERIC") -> Dict[str, Any]:
    """Call Gemini, try to extract a JSON object from response text.
    Returns {} on errors or if not configured.
    """
    if _gemini_model is None:
        return {}
    try:
        resp = _gemini_model.generate_content(prompt)
        raw = (getattr(resp, 'text', None) or '').strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            print(f"[Gemini:{tag}] No JSON found. Raw: {raw[:200]}...")
            return {}
        return json.loads(m.group(0))
    except Exception as e:
        print(f"[Gemini:{tag}] Error:", repr(e))
        return {}


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

# Helper: create appointment item internally (used by voice endpoints)
def _create_appointment_internal(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    agency_id = payload.get('agencyId')
    service_code = payload.get('serviceCode')
    date_str = payload.get('date')
    time_str = payload.get('time')
    errors: List[str] = []
    if not agency_id:
        errors.append('Thiếu agencyId')
    if not service_code:
        errors.append('Thiếu serviceCode')
    if not date_str or not _is_valid_date(date_str):
        errors.append('Ngày không hợp lệ')
    if not time_str or not _is_valid_time(time_str):
        errors.append('Giờ không hợp lệ')
    if errors:
        return False, {}, ", ".join(errors)

    try:
        appt_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    except Exception as e:
        return False, {}, f"Lỗi thời gian: {e}"
    if appt_dt < datetime.now():
        return False, {}, 'Không thể đặt lịch trong quá khứ'

    items = _read_appointments()
    same_date = [a for a in items if a.get('agencyId') == agency_id and a.get('date') == date_str]
    slot_count = len([a for a in same_date if a.get('time') == time_str])
    if slot_count >= 5:
        return False, {}, f'Thời điểm {time_str} ngày {date_str} đã đầy'

    new_item = {
        'id': f"apt-{int(time.time()*1000)}",
        'userId': payload.get('userId') or f"voice-user-{int(time.time()*1000)}",
        'agencyId': agency_id,
        'serviceCode': service_code,
        'date': date_str,
        'time': time_str,
        'status': payload.get('status') or 'pending',
        'fullName': payload.get('fullName'),
        'phone': payload.get('phone'),
        'info': payload.get('info'),
        'queueNumber': slot_count + 1,
    }
    items.append(new_item)
    _write_appointments(items)
    return True, new_item, None


def _suggest_slots_json(location: str, date_iso: str) -> List[str]:
    """Suggest available slots for given location+date based on JSON store occupancy."""
    candidate_slots = ["08:00", "09:00", "10:00", "14:00", "15:00"]
    items = _read_appointments()
    # In this JSON-based demo, we don't have explicit location mapping; assume agency-001 for all
    used = set([a.get('time') for a in items if a.get('date') == date_iso and a.get('agencyId') == 'agency-001'])
    # Capacity per slot: 5
    available = []
    for s in candidate_slots:
        count = sum(1 for a in items if a.get('date') == date_iso and a.get('time') == s)
        if count < 5:
            available.append(s+":00")  # return HH:MM:SS
    return available

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
        # Build detailed display message
        location_display = ('UBND Quận' if agency_id == 'ubnd-001' else 'Cơ quan hành chính')
        service_display = 'Làm CCCD' if service_code == 'CCCD' else ('Đăng ký khai sinh' if service_code == 'KHAISINH' else ('Làm hộ chiếu' if service_code == 'PASSPORT' else 'Dịch vụ hành chính'))
        detailed_msg = (
            "Đặt lịch thành công, thông tin chi tiết đặt lịch:\n"
            f"Thời gian: {date_str} {time_str}\n"
            f"Địa điểm: {location_display}\n"
            f"Dịch vụ: {service_display}\n"
            f"Mã số: {new_item.get('id')}"
        )
        return jsonify({'status': 'success', 'message': detailed_msg, 'missing': None, 'appointment': new_item})
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

# ==========================
# Voice endpoints (STT / TTS / Dialog / Auto-create)
# ==========================

@app.route('/api/voice/stt', methods=['POST'])
def api_voice_stt():
    if request.content_type and 'multipart/form-data' in request.content_type.lower():
        file = request.files.get('file')
    else:
        file = None
    if file is None:
        # Trả 200 với trạng thái lỗi để FE không bị throw do res.ok=false
        return jsonify({'status': 'error', 'message': 'Thiếu file audio trong form-data (field "file")'}), 200
    client = _get_speech_client()
    if client is None:
        # Dev mock để test luồng mà không cần Google Cloud
        enable_mock = os.getenv('VOICE_STT_DEV_MOCK', '1') == '1'
        if enable_mock:
            debug_text = request.headers.get('X-Debug-Transcription') or 'đặt lịch căn cước ngày mai 09:00'
            return jsonify({'status': 'success', 'text': debug_text}), 200
        return jsonify({'status': 'error', 'message': 'Google Speech chưa được cấu hình'}), 200
    try:
        audio_bytes = file.read()
        audio = g_speech.RecognitionAudio(content=audio_bytes)
        config = g_speech.RecognitionConfig(
            encoding=g_speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code='vi-VN',
            enable_automatic_punctuation=True,
        )
        res = client.recognize(config=config, audio=audio)
        if not res.results:
            return jsonify({'status': 'error', 'message': 'Không nghe thấy gì trong audio.'}), 200
        text_out = ' '.join([r.alternatives[0].transcript for r in res.results]).strip()
        return jsonify({'status': 'success', 'text': text_out}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 200

@app.route('/api/voice/stt', methods=['OPTIONS'])
def api_voice_stt_options():
    resp = make_response('', 200)
    return resp


@app.route('/api/voice/tts', methods=['POST'])
def api_voice_tts():
    payload = request.get_json(silent=True) or {}
    text = (payload.get('text') or '').strip()
    if not text:
        return jsonify({'status': 'error', 'message': 'Thiếu text cho TTS'}), 400
    client = _get_tts_client()
    if client is None:
        return jsonify({'status': 'error', 'message': 'Google TTS chưa được cấu hình'}), 500
    try:
        res = client.synthesize_speech(
            input=g_tts.SynthesisInput(text=text),
            voice=g_tts.VoiceSelectionParams(language_code='vi-VN', ssml_gender=g_tts.SsmlVoiceGender.NEUTRAL),
            audio_config=g_tts.AudioConfig(audio_encoding=g_tts.AudioEncoding.MP3),
        )
        return Response(res.audio_content, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/voice/tts', methods=['OPTIONS'])
def api_voice_tts_options():
    resp = make_response('', 200)
    return resp


@app.route('/api/voice/voices', methods=['GET'])
def api_voice_list_voices():
    """List available Google TTS voices, filterable by ?lang=vi-VN"""
    client = _get_tts_client()
    if client is None:
        return jsonify({'success': False, 'message': 'Google TTS chưa được cấu hình'}), 500
    try:
        lang = request.args.get('lang') or None
        resp = client.list_voices()
        voices = []
        for v in resp.voices:
            langs = list(v.language_codes)
            if lang and lang not in langs:
                continue
            voices.append({
                'name': v.name,
                'languageCodes': langs,
                'ssmlGender': g_tts.SsmlVoiceGender(v.ssml_gender).name if hasattr(v, 'ssml_gender') else None,
                'naturalSampleRateHertz': getattr(v, 'natural_sample_rate_hertz', None),
            })
        return jsonify({'success': True, 'data': {'voices': voices}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def _parse_date_vi(text_in: str) -> Optional[str]:
    # Try YYYY-MM-DD
    m = re.search(r'(20\d{2})-(\d{1,2})-(\d{1,2})', text_in)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # Try DD/MM/YYYY
    m = re.search(r'(\d{1,2})/(\d{1,2})/(20\d{2})', text_in)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def _extract_time(text_in: str, allowed: Optional[List[str]] = None) -> Optional[str]:
    # Accept HH:MM or HHhMM or HH giờ MM
    m = re.search(r'\b(\d{1,2})(?:[:hH ](\d{2}))\b', text_in)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2))
        cand = f"{hh:02d}:{mm:02d}:00"
        if not allowed or cand in allowed:
            return cand
    # Fallback whole hour
    m = re.search(r'\b(\d{1,2})\s*(?:giờ|h)\b', text_in)
    if m:
        hh = int(m.group(1))
        cand = f"{hh:02d}:00:00"
        if not allowed or cand in allowed:
            return cand
    return None


@app.route('/api/voice/appointments/auto-create', methods=['POST'])
def api_voice_auto_create():
    payload = request.get_json(silent=True) or {}
    user_text = (payload.get('text') or '').strip()
    phone = (payload.get('phone') or '').strip() or None
    session_id = (payload.get('session_id') or payload.get('sessionId') or 'default').strip() or 'default'
    speak = bool(payload.get('speak') or os.getenv('VOICE_DIALOG_TTS', '1') == '1')
    if not user_text:
        return jsonify({'status': 'error', 'message': 'Thiếu text.'}), 400
    # Load aggregated state for this session (stateless FE compatibility)
    agg = _auto_state_store.get(session_id) or {
        'service_type': None,
        'location': None,
        'appointment_date': None,
        'appointment_time': None,
    }

    # If Gemini configured, use LLM parsing for richer extraction
    if _gemini_model is not None:
        prompt = f"""
Bạn là trợ lý hành chính công Việt Nam.

Nhiệm vụ: Đọc câu tiếng Việt và trích xuất thông tin đặt lịch hẹn thủ tục hành chính.
Chỉ trả lời đúng JSON hợp lệ, không giải thích thêm.

Trường cần trích xuất:

Câu người dùng:
"{user_text}".
"""
        data = _call_gemini_json(prompt, 'AUTO_CREATE')
        if not data:
            # fallback to rule-based
            data = {}
        service_type = data.get('service_type') or agg.get('service_type')
        location = data.get('location') or agg.get('location')
        date_iso = (data.get('appointment_date') or agg.get('appointment_date') or _parse_date_vi(user_text))
        appt_time = data.get('appointment_time') or agg.get('appointment_time')
        # Fallback: nếu Gemini không trích được giờ, thử bắt HH:MM từ người dùng
        if not appt_time:
            parsed = _extract_time(user_text)
            if parsed:
                appt_time = parsed
        missing = []
        if not service_type:
            missing.append('service_type')
        if not location:
            missing.append('location')
        if not date_iso:
            missing.append('appointment_date')
        if not appt_time:
            missing.append('appointment_time')
        if missing:
            # Không trả về lỗi thiếu trường nữa; hướng dẫn hỏi tiếp theo dạng hội thoại
            first = missing[0]
            prompts = {
                'service_type': 'Bạn muốn làm thủ tục gì? Ví dụ: làm căn cước công dân.',
                'location': 'Bạn muốn làm ở đâu? Bạn có thể nói tên quận/huyện hoặc cơ quan (ví dụ: UBND quận Hoàn Kiếm).',
                'appointment_date': 'Bạn có thể cung cấp ngày (định dạng YYYY-MM-DD hoặc DD/MM/YYYY) để mình gợi ý khung giờ trống?',
                'appointment_time': 'Bạn thích khung giờ nào? Ví dụ: 09:00 hoặc 14:00.',
            }
            # Nếu thiếu giờ nhưng có ngày+địa điểm, thử gợi ý slot để người dùng chọn
            extra: Dict[str, Any] = {}
            if first == 'appointment_time' and location and date_iso:
                try:
                    extra['suggestedSlots'] = _suggest_slots_json(location, date_iso)
                except Exception:
                    pass
            # Persist partial state before asking next
            _auto_state_store[session_id] = {
                'service_type': service_type,
                'location': location,
                'appointment_date': date_iso,
                'appointment_time': appt_time,
            }
            return jsonify({'status': 'continue', 'message': prompts.get(first, 'Bạn có thể cung cấp thông tin tiếp theo giúp mình?'), 'next': first, 'state': _auto_state_store[session_id], **extra}), 200

        try:
            # Normalize HH:MM
            dt_obj = datetime.strptime(date_iso, '%Y-%m-%d')
            t_obj = datetime.strptime(appt_time, '%H:%M:%S')
            hhmm = t_obj.strftime('%H:%M')
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Định dạng ngày/giờ không hợp lệ: {e}'}), 200

        # Map service_type/location → simple codes for demo
        svc_lower = (service_type or '').lower()
        svc = 'SERVICE_CODE'
        if 'căn cước' in svc_lower or 'cccd' in svc_lower:
            svc = 'CCCD'
        elif 'khai sinh' in svc_lower:
            svc = 'KHAISINH'
        elif 'hộ chiếu' in svc_lower or 'passport' in svc_lower:
            svc = 'PASSPORT'
        agency_id = 'ubnd-001' if ('ubnd' in (location or '').lower() or 'ủy ban' in (location or '').lower()) else 'agency-001'

        ok, appt, err = _create_appointment_internal({
            'agencyId': agency_id,
            'serviceCode': svc,
            'date': date_iso,
            'time': hhmm,
            'phone': phone or data.get('phone'),
            'fullName': data.get('citizen_name') or 'Người dân',
            'info': data.get('note') or 'Đặt lịch qua voice'
        })
        if not ok:
            return jsonify({'status': 'error', 'message': err or 'Không tạo được lịch'}), 200
        # Clear session state after success
        _auto_state_store.pop(session_id, None)
        # Build detailed display message
        # Display uses user-provided phrases when available
        location_display = (location or ('UBND Quận' if agency_id == 'ubnd-001' else 'Cơ quan hành chính'))
        service_display = (service_type or ('Làm CCCD' if svc == 'CCCD' else ('Đăng ký khai sinh' if svc == 'KHAISINH' else ('Làm hộ chiếu' if svc == 'PASSPORT' else 'Dịch vụ hành chính'))))
        detailed_msg = (
            "Đặt lịch thành công, thông tin chi tiết đặt lịch:\n"
            f"Thời gian: {date_iso} {hhmm}\n"
            f"Địa điểm: {location_display} (theo người dùng yêu cầu đầu vào voice)\n"
            f"Dịch vụ: {service_display}\n"
            f"Mục đích: {appt.get('info') or 'Đặt lịch qua voice'}\n"
            f"Mã số: {appt.get('queueNumber', 1)}\n"
            f"Mã ID: {appt.get('id')}"
        )
        resp_payload = {'status': 'success', 'message': detailed_msg, 'missing': None, 'appointment': appt}
        if speak:
            audio_b64 = _tts_mp3_base64(detailed_msg)
            if audio_b64:
                resp_payload['audio'] = { 'mimeType': 'audio/mpeg', 'base64': audio_b64 }
        return jsonify(resp_payload)

    # Fallback simple rule-based extraction when Gemini not configured
    svc = agg.get('service_type') and ('CCCD' if re.search(r"căn cước|cccd", str(agg.get('service_type')), re.I) else 'SERVICE_CODE') or 'SERVICE_CODE'
    svc_lower = user_text.lower()
    if 'căn cước' in svc_lower or 'cccd' in svc_lower:
        svc = 'CCCD'
    elif 'khai sinh' in svc_lower:
        svc = 'KHAISINH'
    elif 'hộ chiếu' in svc_lower or 'passport' in svc_lower:
        svc = 'PASSPORT'

    agency_id = 'agency-001'
    if 'ubnd' in svc_lower or 'ủy ban' in svc_lower or 'uy ban' in svc_lower:
        agency_id = 'ubnd-001'

    date_iso = agg.get('appointment_date') or _parse_date_vi(user_text)
    if not date_iso:
        # Không báo thiếu trường; yêu cầu người dùng cung cấp ngày
        _auto_state_store[session_id] = {
            'service_type': 'CCCD' if svc == 'CCCD' else agg.get('service_type'),
            'location': agg.get('location'),
            'appointment_date': None,
            'appointment_time': agg.get('appointment_time'),
        }
        return jsonify({'status': 'continue', 'message': 'Bạn có thể cung cấp ngày (YYYY-MM-DD hoặc DD/MM/YYYY) để mình gợi ý khung giờ trống?', 'next': 'appointment_date', 'state': _auto_state_store[session_id]}), 200

    candidate_slots = ["08:00", "09:00", "10:00", "14:00", "15:00"]
    picked = _extract_time(user_text, [s+":00" for s in candidate_slots]) or agg.get('appointment_time')
    time_pick = picked or candidate_slots[0] + ":00"

    ok, appt, err = _create_appointment_internal({
        'agencyId': agency_id,
        'serviceCode': svc,
        'date': date_iso,
        'time': time_pick[:5],
        'phone': phone,
        'info': 'Đặt lịch qua voice',
    })
    if not ok:
        return jsonify({'status': 'error', 'message': err or 'Không tạo được lịch'}), 200
    # Build detailed display message
    location_display = ('UBND Quận' if agency_id == 'ubnd-001' else 'Cơ quan hành chính')
    # Try to reflect user's phrase in fallback via heuristic
    service_display = ('Làm CCCD' if svc == 'CCCD' else ('Đăng ký khai sinh' if svc == 'KHAISINH' else ('Làm hộ chiếu' if svc == 'PASSPORT' else 'Dịch vụ hành chính')))
    detailed_msg = (
        "Đặt lịch thành công, thông tin chi tiết đặt lịch:\n"
        f"Thời gian: {date_iso} {time_pick[:5]}\n"
        f"Địa điểm: {location_display} (theo người dùng yêu cầu đầu vào voice)\n"
        f"Dịch vụ: {service_display}\n"
        f"Mục đích: {appt.get('info') or 'Đặt lịch qua voice'}\n"
        f"Mã số: {appt.get('queueNumber', 1)}\n"
        f"Mã ID: {appt.get('id')}"
    )
    resp_payload = {
        'status': 'success',
        'message': detailed_msg,
        'missing': None,
        'appointment': appt,
    }
    if speak:
        audio_b64 = _tts_mp3_base64(detailed_msg)
        if audio_b64:
            resp_payload['audio'] = { 'mimeType': 'audio/mpeg', 'base64': audio_b64 }
    return jsonify(resp_payload)

@app.route('/api/voice/appointments/auto-create', methods=['OPTIONS'])
def api_voice_auto_create_options():
    resp = make_response('', 200)
    return resp


# ==========================
# Dialog flow endpoint (LLM-assisted if available)
# ==========================

def _dialog_suggest_slots(state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    loc = state.get('location')
    date_iso = state.get('appointment_date')
    if not loc or not date_iso:
        state['step'] = _DialogStep.ASK_DATE
        return ("Để gợi ý giờ trống, mình cần biết rõ ngày và địa điểm nhé.", state)
    available = _suggest_slots_json(loc, date_iso)
    if not available:
        state['step'] = _DialogStep.ASK_DATE
        # Gợi ý cơ quan thay thế khi quá đông
        alt_office = 'Cơ quan A'
        return (f"Ngày {date_iso} tại {loc} sẽ khá đông, anh/chị có thể lựa chọn thay thế là {alt_office}. Vui lòng cung cấp ngày khác để em gợi ý khung giờ trống nhé.", state)
    state['suggested_slots'] = available
    state['step'] = _DialogStep.CONFIRM
    times_text = ", ".join(s[:5] for s in available)
    return (f"Ngày {date_iso} tại {loc} còn trống các khung giờ: {times_text}. Anh/chị muốn chọn giờ nào ạ?", state)


@app.route('/api/voice/dialog', methods=['POST'])
def api_voice_dialog():
    payload = request.get_json(silent=True) or {}
    session_id = (payload.get('session_id') or payload.get('sessionId') or 'default').strip() or 'default'
    user_text = (payload.get('text') or '').strip()
    phone = (payload.get('phone') or '').strip() or None
    speak = bool(payload.get('speak') or os.getenv('VOICE_DIALOG_TTS', '0') == '1')

    def _reply_payload(reply_text: str, step: str, done: bool, state_obj: Dict[str, Any], extra: Optional[Dict[str, Any]] = None):
        resp: Dict[str, Any] = {
            'reply': reply_text,
            'step': step,
            'done': done,
            'state': state_obj,
        }
        if speak and reply_text:
            audio_b64 = _tts_mp3_base64(reply_text)
            if audio_b64:
                resp['audio'] = { 'mimeType': 'audio/mpeg', 'base64': audio_b64 }
        if extra:
            resp.update(extra)
        return jsonify(resp)
    if not user_text:
        return _reply_payload('Mình chưa nghe rõ, anh/chị có thể nói lại giúp em được không?', _DialogStep.ASK_INTENT, False, None)  # type: ignore

    state = _dialog_store.get(session_id)
    if state is None:
        state = {
            'step': _DialogStep.ASK_INTENT,
            'citizen_name': None,
            'phone': phone,
            'service_type': None,
            'location': None,
            'appointment_date': None,
            'appointment_time': None,
            'note': None,
            'suggested_slots': None,
        }
        _dialog_store[session_id] = state

    # DONE -> allow restart on intent keywords
    if state.get('step') == _DialogStep.DONE:
        if re.search(r"(đặt lịch|thủ tục|căn cước|cccd|hồ sơ|khai sinh)", user_text, re.IGNORECASE):
            state.update({
                'step': _DialogStep.ASK_INTENT,
                'service_type': None,
                'location': None,
                'appointment_date': None,
                'appointment_time': None,
                'note': None,
                'suggested_slots': None,
            })
        else:
            return _reply_payload('Lịch hẹn trước đó đã được đặt xong. Nếu muốn đặt lịch mới, hãy nói thủ tục bạn cần.', state['step'], True, state)

    # ASK_INTENT
    if state.get('step') == _DialogStep.ASK_INTENT:
        service_type = None
        if _gemini_model is not None:
            data = _call_gemini_json(f"Hãy trích service_type từ: \n\n\"\"\"{user_text}\"\"\". Trả JSON {{\"service_type\": string hoặc null}}.", 'ASK_INTENT')
            service_type = data.get('service_type') if isinstance(data, dict) else None
        # fallback keyword
        if not service_type:
            if re.search(r"căn cước|cccd", user_text, re.I):
                service_type = 'Làm căn cước công dân'
            elif re.search(r"khai sinh", user_text, re.I):
                service_type = 'Đăng ký khai sinh'
        if not service_type:
            return _reply_payload('Bạn muốn làm thủ tục gì? Ví dụ: “Tôi muốn đặt lịch làm thủ tục CCCD”.', _DialogStep.ASK_INTENT, False, state)
        state['service_type'] = service_type
        state['step'] = _DialogStep.ASK_LOCATION
        return _reply_payload(f"Bạn muốn {service_type.lower()} ở đâu? Ví dụ: UBND quận Hoàn Kiếm.", state['step'], False, state)

    # ASK_LOCATION
    if state.get('step') == _DialogStep.ASK_LOCATION:
        location = None
        if _gemini_model is not None:
            data = _call_gemini_json(f"Trích location từ: \n\n\"\"\"{user_text}\"\"\". Trả JSON {{\"location\": string hoặc null}}.", 'ASK_LOCATION')
            location = data.get('location') if isinstance(data, dict) else None
        if not location:
            # take any organization-like phrase
            m = re.search(r"(ubnd[^,.]*|ủy ban[^,.]*)", user_text, re.I)
            if m:
                location = m.group(1)
        if not location:
            return _reply_payload('Bạn muốn làm ở đâu? Bạn có thể nói tên quận/huyện hoặc cơ quan.', _DialogStep.ASK_LOCATION, False, state)
        # Ưu tiên gợi ý cơ quan gần nhất nếu có dịch vụ khoảng cách
        nearest = None
        try:
            from services.distance import suggest_nearest_office
            nearest = suggest_nearest_office(user_text)
        except Exception:
            nearest = None
        state['location'] = nearest or location
        state['step'] = _DialogStep.ASK_DATE
        loc_display = state['location']
        return _reply_payload(f"Địa chỉ bạn muốn tới là {loc_display}, bạn có thể cung cấp ngày để tôi lựa chọn khung giờ phù hợp nhất", state['step'], False, state)

    # ASK_DATE
    if state.get('step') == _DialogStep.ASK_DATE:
        appt_date = None
        if _gemini_model is not None:
            data = _call_gemini_json(f"Trích appointment_date (YYYY-MM-DD) từ: \n\n\"\"\"{user_text}\"\"\". Trả JSON {{\"appointment_date\": string hoặc null}}.", 'ASK_DATE')
            appt_date = data.get('appointment_date') if isinstance(data, dict) else None
        if not appt_date:
            appt_date = _parse_date_vi(user_text)
        if not appt_date:
            return _reply_payload('Anh/chị vui lòng cho biết ngày cụ thể nhé.', _DialogStep.ASK_DATE, False, state)
        state['appointment_date'] = appt_date
        reply, new_state = _dialog_suggest_slots(state)
        _dialog_store[session_id] = new_state
        return _reply_payload(reply, new_state['step'], False, new_state)

    # SUGGEST_SLOT (rare direct)
    if state.get('step') == _DialogStep.SUGGEST_SLOT:
        reply, new_state = _dialog_suggest_slots(state)
        _dialog_store[session_id] = new_state
        return _reply_payload(reply, new_state['step'], False, new_state)

    # CONFIRM
    if state.get('step') == _DialogStep.CONFIRM:
        slots = state.get('suggested_slots') or []
        if not slots:
            reply, new_state = _dialog_suggest_slots(state)
            _dialog_store[session_id] = new_state
            return _reply_payload(reply, new_state['step'], False, new_state)
        # Extract time
        appt_time = None
        if _gemini_model is not None:
            data = _call_gemini_json(
                f"Các khung giờ gợi ý: {slots}. Từ câu sau, trích appointment_time (HH:MM:SS) nếu phù hợp. Câu: \"{user_text}\". Trả JSON {{\"appointment_time\": string hoặc null}}.",
                'CONFIRM_SLOT'
            )
            appt_time = data.get('appointment_time') if isinstance(data, dict) else None
            if appt_time and len(appt_time) == 5:
                for s in slots:
                    if s.startswith(appt_time):
                        appt_time = s
                        break
        if not appt_time:
            # heuristic
            m = re.search(r"\b(\d{1,2}):(\d{2})\b", user_text)
            if m:
                cand = f"{int(m.group(1)):02d}:{m.group(2)}:00"
                if cand in slots:
                    appt_time = cand
        if not appt_time or appt_time not in slots:
            return _reply_payload('Anh/chị vui lòng chọn một trong các khung giờ em vừa gợi ý nhé.', _DialogStep.CONFIRM, False, state)
        state['appointment_time'] = appt_time
        # Create appointment (JSON store demo)
        date_iso = state.get('appointment_date')
        hhmm = appt_time[:5]
        svc = 'SERVICE_CODE'
        svc_lower = (state.get('service_type') or '').lower()
        if 'căn cước' in svc_lower or 'cccd' in svc_lower:
            svc = 'CCCD'
        elif 'khai sinh' in svc_lower:
            svc = 'KHAISINH'
        elif 'hộ chiếu' in svc_lower or 'passport' in svc_lower:
            svc = 'PASSPORT'
        agency_id = 'ubnd-001' if ('ubnd' in (state.get('location') or '').lower() or 'ủy ban' in (state.get('location') or '').lower()) else 'agency-001'
        ok, appt, err = _create_appointment_internal({
            'agencyId': agency_id,
            'serviceCode': svc,
            'date': date_iso,
            'time': hhmm,
            'phone': state.get('phone'),
            'fullName': state.get('citizen_name') or 'Người dân',
            'info': 'Đặt lịch qua voicebot'
        })
        if not ok:
            return _reply_payload(err or 'Không tạo được lịch', _DialogStep.CONFIRM, False, state)
        state['step'] = _DialogStep.DONE
        _dialog_store[session_id] = state
        d_str = datetime.strptime(date_iso, '%Y-%m-%d').strftime('%d/%m/%Y') if date_iso else ''
        t_str = hhmm
        # Build detailed display message for dialog confirmation
        service_display = (state.get('service_type') or ('Làm CCCD' if svc == 'CCCD' else ('Đăng ký khai sinh' if svc == 'KHAISINH' else ('Làm hộ chiếu' if svc == 'PASSPORT' else 'Dịch vụ hành chính'))))
        location_display = state.get('location') or ('UBND Quận' if agency_id == 'ubnd-001' else 'Cơ quan hành chính')
        reply = (
            "Đặt lịch thành công, thông tin chi tiết đặt lịch:\n"
            f"Thời gian: {d_str} {t_str}\n"
            f"Địa điểm: {location_display} (theo người dùng yêu cầu đầu vào voice)\n"
            f"Dịch vụ: {service_display}\n"
            f"Mục đích: {appt.get('info') or 'Đặt lịch qua voicebot'}\n"
            f"Mã số: {appt.get('queueNumber', 1)}\n"
            f"Mã ID: {appt.get('id')}"
        )
        return _reply_payload(reply, state['step'], True, state, {'appointment': appt})

    return _reply_payload('Mình đang gặp lỗi kỹ thuật, anh/chị thử nói lại giúp em được không?', state.get('step') or _DialogStep.ASK_INTENT, False, state)

# Catch-all preflight for any /api/* path to guarantee 2xx + CORS headers
@app.route('/api/<path:any_path>', methods=['OPTIONS'])
def api_catch_all_options(any_path: str):
    return ('', 200)

# Fallback: ensure CORS headers are present for all /api/* responses
@app.after_request
def add_cors_headers(resp: Response):
    try:
        path = request.path or ''
    except Exception:
        path = ''
    if path.startswith('/api/'):
        origin = request.headers.get('Origin')
        allowed = {'http://localhost:5173', 'http://localhost:3000', 'http://localhost:3001'}
        # Allow any localhost origin in dev (e.g., 5173, 3000, 3001, 8080, etc.)
        if origin and (origin in allowed or origin.startswith('http://localhost:')):
            resp.headers['Access-Control-Allow-Origin'] = origin
        elif not origin:
            # Non-browser clients may omit Origin; choose a sensible default for dev
            resp.headers.setdefault('Access-Control-Allow-Origin', 'http://localhost:3000')
        resp.headers.setdefault('Vary', 'Origin')
        resp.headers.setdefault('Access-Control-Allow-Credentials', 'true')
        resp.headers.setdefault('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,PATCH,OPTIONS')
        req_hdrs = request.headers.get('Access-Control-Request-Headers', '')
        default_hdrs = 'Content-Type,Authorization,X-Requested-With,Accept'
        resp.headers.setdefault('Access-Control-Allow-Headers', req_hdrs or default_hdrs)
        # Chrome may send Access-Control-Request-Private-Network for local addresses
        if request.headers.get('Access-Control-Request-Private-Network', '').lower() == 'true':
            resp.headers['Access-Control-Allow-Private-Network'] = 'true'
        resp.headers.setdefault('Access-Control-Max-Age', '86400')
    return resp

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
    # Mặc định bật TTS cho chatbot nếu không chỉ định (fix trường hợp không có tiếng)
    speak = True if (payload.get('speak') is None and payload.get('tts') is None and os.getenv('CHATBOT_TTS') is None) else bool(payload.get('speak') or payload.get('tts') or os.getenv('CHATBOT_TTS', '0') == '1')

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

    audio_obj = None
    if final_answer:
        # Luôn cố synthesize nếu speak=true mặc định hoặc người dùng bật
        if speak:
            audio_b64 = _tts_mp3_base64(final_answer)
            if audio_b64:
                audio_obj = { 'mimeType': 'audio/mpeg', 'base64': audio_b64 }

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
    try:
        path = request.path or ''
        method = request.method or ''
    except Exception:
        path = ''
        method = ''
    # Treat unknown preflight requests under /api/* as OK to satisfy browsers
    if method == 'OPTIONS' and path.startswith('/api/'):
        return ('', 200)
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
