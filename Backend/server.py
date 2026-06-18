"""
Flask application entry point.
All business logic lives in routes/ blueprints.
"""
import importlib
import logging as _logging
import os
import threading
import time
import traceback

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# ── Suppress noisy third-party loggers TRƯỚC KHI import bất kỳ thứ nặng nào ──
for _lib in (
    'werkzeug',            # Flask dev server request logs (ta có log riêng)
    'sqlalchemy.engine',   # SQL query echoing
    'sqlalchemy.pool',
    'sqlalchemy.orm',
    'sqlalchemy.dialects',
    'langgraph',
    'chromadb',
    'sentence_transformers',
    'httpx',
    'httpcore',
    'urllib3',
    'urllib3.connectionpool',
    'google.auth',
    'google.auth.transport',
    'google.api_core',
    'grpc',
    'absl',
):
    _logging.getLogger(_lib).setLevel(_logging.WARNING)

from logger import get_logger, log_request, log_response, RESET, BOLD, CYAN, GREEN, YELLOW, RED

log = get_logger('server')

# WebSocket support
try:
    from flask_sock import Sock
    _SOCK_AVAILABLE = True
except ImportError:
    _SOCK_AVAILABLE = False
    log.warning('flask-sock not installed — WebSocket disabled. Run: pip install flask-sock')

load_dotenv(override=True)

# Bật per-request HTTP log bằng cách set LOG_HTTP=1 trong .env (mặc định tắt)
_LOG_HTTP = os.getenv('LOG_HTTP', '0') == '1'

# Origins đọc từ env — khi deploy thêm domain thật vào CORS_ORIGINS trong .env
# Ví dụ: CORS_ORIGINS=https://emapp.thanhhoa.gov.vn,https://admin.emapp.vn
_DEFAULT_ORIGINS = 'http://localhost:5173,http://localhost:3000,http://localhost:3001'
_CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv('CORS_ORIGINS', _DEFAULT_ORIGINS).split(',')
    if o.strip()
]
_CORS_ORIGIN_SET: set[str] = set(_CORS_ORIGINS)
log.debug(f'CORS allowed origins: {_CORS_ORIGINS}')

app = Flask(__name__)

CORS(
    app,
    resources={
        r'/api/*': {
            'origins': _CORS_ORIGINS,
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
            'supports_credentials': True,
            'max_age': 86400,
        }
    },
    supports_credentials=True,
)

# ── Database (optional PostgreSQL) ────────────────────────────────────────────
try:
    from models.db import init_db
    init_db(app)
    log.debug('PostgreSQL database initialized')
except Exception as e:
    log.warning(f'Database initialization skipped: {e}')

# ── Auth middleware ────────────────────────────────────────────────────────────
from middleware.auth import init_auth
init_auth(app)

# ── Blueprints ─────────────────────────────────────────────────────────────────
_blueprints = [
    ('routes.auth_routes',          'auth_bp'),
    ('routes.services_routes',      'services_bp'),
    ('routes.applications_routes',  'applications_bp'),
    ('routes.admin_routes',         'admin_bp'),
    ('routes.appointments_routes',  'appointments_bp'),
    ('routes.voice_routes',         'voice_bp'),
    ('routes.rag_routes',           'rag_bp'),
    ('routes.queue_routes',         'queue_bp'),
    ('routes.document_extract_routes', 'document_extract_bp'),
    ('routes.map_routes',              'map_bp'),
    ('routes.chatbot_config_routes',   'chatbot_cfg_bp'),
    ('routes.evaluation_routes',       'evaluation_bp'),
    ('routes.procedures_routes',       'procedures_bp'),
    ('routes.templates_routes',        'templates_bp'),
    ('routes.ai_routes',               'ai_bp'),
    ('routes.notification_routes',     'notification_bp'),
]

_bp_ok: list = []
_bp_fail: list = []
for module_path, bp_name in _blueprints:
    try:
        module = importlib.import_module(module_path)
        app.register_blueprint(getattr(module, bp_name))
        _bp_ok.append(bp_name)
    except Exception as e:
        _bp_fail.append(bp_name)
        log.error(f'✗ {bp_name} failed to register: {e}')

_bp_summary = f'{GREEN}✓{RESET} {len(_bp_ok)}/{len(_blueprints)} blueprints'
if _bp_fail:
    _bp_summary += f' | {RED}✗ failed: {", ".join(_bp_fail)}{RESET}'
log.info(_bp_summary)

# ── WebSocket (flask-sock) ────────────────────────────────────────────────────
if _SOCK_AVAILABLE:
    sock = Sock(app)
    app.config['SOCK_SERVER_OPTIONS'] = {
        'ping_interval': 15,
        'ping_timeout':  10,
    }
    try:
        from routes.queue_routes import register_websocket
        register_websocket(sock)
        log.debug('WebSocket /ws/queue/<agency_id> registered')
    except Exception as e:
        log.error(f'WebSocket registration failed: {e}')

# ── Preload SuggestProcedure in background ────────────────────────────────────
def _preload_suggest():
    try:
        from routes.rag_routes import init_document_suggestion
        init_document_suggestion()
        log.debug('SuggestProcedure model loaded')
    except Exception as e:
        log.warning(f'[SuggestProcedure] preload failed: {e}')

threading.Thread(target=_preload_suggest, daemon=True).start()

# ── Auto-seed procedures nếu bảng trống ──────────────────────────────────────
def _auto_seed_procedures():
    """Tự động seed procedures nếu chưa có dữ liệu (fresh deployment)."""
    try:
        with app.app_context():
            from models.db import db
            from sqlalchemy import text as _text
            count = db.session.execute(
                _text('SELECT COUNT(*) FROM public.procedures')
            ).scalar() or 0
            if count == 0:
                log.info('[AutoSeed] procedures table empty — running seed_procedures...')
                import sys, os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
                from seed_procedures import seed_service_requirements, seed_procedure_metadata
                seed_procedure_metadata()
                seed_service_requirements()
                log.info('[AutoSeed] procedures seeded OK')
            else:
                log.debug(f'[AutoSeed] procedures OK ({count} rows)')
    except Exception as e:
        log.warning(f'[AutoSeed] procedures seed failed (run manually): {e}')

threading.Thread(target=_auto_seed_procedures, daemon=True).start()


# ── Auto-seed queue data (counters, stats, realtime) ─────────────────────────
def _auto_seed_queue_data():
    """Seed agency_counters, service_stats, agency_queue_realtime nếu chưa có."""
    try:
        with app.app_context():
            from models.db import db
            from sqlalchemy import text as _text
            count = db.session.execute(
                _text('SELECT COUNT(*) FROM public.agency_counters')
            ).scalar() or 0
            if count == 0:
                log.info('[AutoSeed] agency_counters empty — running seed_queue_data...')
                import sys as _sys, os as _os
                _sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), 'scripts'))
                from seed_queue_data import (
                    seed_agency_counters, seed_agency_queue_realtime,
                    seed_service_stats, seed_form_templates,
                )
                seed_agency_counters(db.session, _text)
                seed_agency_queue_realtime(db.session, _text)
                seed_service_stats(db.session, _text)
                seed_form_templates(db.session, _text)
                log.info('[AutoSeed] queue data seeded OK')
            else:
                log.debug(f'[AutoSeed] agency_counters OK ({count} rows)')
    except Exception as e:
        log.warning(f'[AutoSeed] queue seed failed (run manually): {e}')

threading.Thread(target=_auto_seed_queue_data, daemon=True).start()


# ── RAG session cleanup (chạy mỗi 6 giờ, xóa sessions > 30 ngày) ─────────────
def _cleanup_rag_sessions():
    while True:
        time.sleep(6 * 3600)
        try:
            from models.db import db
            from sqlalchemy import text as _text
            with app.app_context():
                result = db.session.execute(_text(
                    "DELETE FROM public.chat_sessions WHERE created_at < now() - INTERVAL '30 days'"
                ))
                db.session.commit()
                if result.rowcount:
                    log.info(f'[RAG cleanup] Deleted {result.rowcount} old chat sessions')
        except Exception as e:
            log.warning(f'[RAG cleanup] Failed: {e}')

threading.Thread(target=_cleanup_rag_sessions, daemon=True).start()

try:
    from services.notification_scheduler import run_reminder_loop
    threading.Thread(target=run_reminder_loop, args=(app,), daemon=True).start()
    log.info('[notif] reminder scheduler started')
except Exception as _e:
    log.warning(f'[notif] không start được scheduler: {_e}')

# ── Rate limiter đơn giản (in-memory, per-IP) ─────────────────────────────────
from collections import defaultdict
_rate_store: dict = defaultdict(list)
_rate_lock = threading.Lock()
_RATE_RULES: dict[str, tuple[int, int]] = {
    # endpoint_prefix: (max_requests, window_seconds)
    '/api/auth/login':     (10, 60),
    '/api/auth/register':  (5,  60),
    '/api/rag/chat':       (20, 60),
    '/api/queue/ticket':   (10, 60),
}

_rate_last_cleanup = 0.0

def _check_rate_limit(ip: str, path: str) -> bool:
    """Return True nếu bị rate limited. Kèm cleanup định kỳ để tránh memory leak."""
    global _rate_last_cleanup
    now = time.monotonic()

    # Dọn dẹp entries cũ mỗi 60 giây
    if now - _rate_last_cleanup > 60:
        with _rate_lock:
            if now - _rate_last_cleanup > 60:
                stale_keys = [k for k, v in list(_rate_store.items()) if not v or now - max(v) > 120]
                for k in stale_keys:
                    del _rate_store[k]
                _rate_last_cleanup = now

    for prefix, (limit, window) in _RATE_RULES.items():
        if not path.startswith(prefix):
            continue
        key = f'{ip}:{prefix}'
        with _rate_lock:
            hits = _rate_store[key]
            _rate_store[key] = [t for t in hits if now - t < window]
            if len(_rate_store[key]) >= limit:
                return True
            _rate_store[key].append(now)
    return False

# ── Request / response logging ─────────────────────────────────────────────────
@app.before_request
def _before():
    request._start_time = time.monotonic()
    if request.method == 'OPTIONS':
        return

    path = request.path or ''
    ip   = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
    if _check_rate_limit(ip, path):
        return jsonify({'success': False, 'message': 'Quá nhiều yêu cầu, vui lòng thử lại sau.'}), 429

    log_request(log, request.method, path)


@app.after_request
def _after(resp: Response) -> Response:
    # CORS headers
    try:
        path = request.path or ''
    except Exception:
        path = ''

    if path.startswith('/api/'):
        origin = request.headers.get('Origin')
        # Chấp nhận localhost với port nằm trong _CORS_ORIGINS hoặc là dev ports quen thuộc
        _DEV_PORTS = {'5173', '3000', '3001', '4173', '8080'}
        def _is_allowed_origin(o: str) -> bool:
            if o in _CORS_ORIGIN_SET:
                return True
            if o.startswith('http://localhost:'):
                port = o.split(':')[-1]
                return port in _DEV_PORTS
            return False
        if origin and _is_allowed_origin(origin):
            resp.headers['Access-Control-Allow-Origin'] = origin
        elif not origin:
            resp.headers.setdefault('Access-Control-Allow-Origin', _CORS_ORIGINS[0])
        resp.headers.setdefault('Vary', 'Origin')
        resp.headers.setdefault('Access-Control-Allow-Credentials', 'true')
        resp.headers.setdefault('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,PATCH,OPTIONS')
        req_hdrs = request.headers.get('Access-Control-Request-Headers', '')
        resp.headers.setdefault('Access-Control-Allow-Headers',
                                req_hdrs or 'Content-Type,Authorization,X-Requested-With,Accept')
        if request.headers.get('Access-Control-Request-Private-Network', '').lower() == 'true':
            resp.headers['Access-Control-Allow-Private-Network'] = 'true'
        resp.headers.setdefault('Access-Control-Max-Age', '86400')

    # Response log (skip OPTIONS noise)
    if request.method != 'OPTIONS':
        elapsed = (time.monotonic() - getattr(request, '_start_time', time.monotonic())) * 1000
        log_response(log, request.method, path, resp.status_code, elapsed)

    return resp


# ── CORS fallback + catch-all preflight ───────────────────────────────────────
@app.route('/api/<path:any_path>', methods=['OPTIONS'])
def api_catch_all_options(any_path: str):
    return ('', 200)


# ── Health check ───────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Public Services Backend API'})


# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    try:
        method = request.method or ''
        path   = request.path or ''
    except Exception:
        method = path = ''
    if method == 'OPTIONS' and path.startswith('/api/'):
        return ('', 200)
    log.warning(f'404 {method} {path}')
    return jsonify({'success': False, 'message': 'Route not found'}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    try:
        method = request.method or ''
        path   = request.path or ''
    except Exception:
        method = path = ''
    log.error(f'Unhandled exception on {method} {path}: {e}', exc_info=True)
    return jsonify({'success': False, 'message': str(e)}), 500


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Seed data chạy nền (không chặn startup)
    if os.getenv('FLASK_ENV', 'development') != 'production':
        def _seed_dev():
            try:
                with app.app_context():
                    from scripts.seed_data import seed_data
                    seed_data()
            except Exception as e:
                log.warning(f'[seed_data] {e}')
        threading.Thread(target=_seed_dev, daemon=True).start()

    port = int(os.getenv('PORT', 8888))
    log.info(f'{BOLD}{CYAN}■ E-Mapp Backend{RESET}  port {BOLD}{port}{RESET}  '
             f'{CYAN}LOG_HTTP={_LOG_HTTP}{RESET}')
    app.run(host='0.0.0.0', port=port)
