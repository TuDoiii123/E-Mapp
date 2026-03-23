"""
Flask application entry point.
All business logic lives in routes/ blueprints.
"""
import importlib
import os
import threading
import time
import traceback

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

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

app = Flask(__name__)

CORS(
    app,
    resources={
        r'/api/*': {
            'origins': [
                'http://localhost:5173',
                'http://localhost:3000',
                'http://localhost:3001',
            ],
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
    log.info('PostgreSQL database initialized')
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
]

for module_path, bp_name in _blueprints:
    try:
        module = importlib.import_module(module_path)
        app.register_blueprint(getattr(module, bp_name))
        log.info(f'{GREEN}✓{RESET} {bp_name} registered')
    except Exception as e:
        log.error(f'✗ {bp_name} failed to register: {e}', exc_info=True)

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
        log.info(f'{GREEN}✓{RESET} WebSocket /ws/queue/<agency_id> registered')
    except Exception as e:
        log.error(f'WebSocket registration failed: {e}', exc_info=True)

# ── Preload SuggestProcedure in background ────────────────────────────────────
def _preload_suggest():
    try:
        from routes.rag_routes import init_document_suggestion
        init_document_suggestion()
        log.info('SuggestProcedure model loaded')
    except Exception as e:
        log.error(f'[SuggestProcedure] preload failed: {e}', exc_info=True)

threading.Thread(target=_preload_suggest, daemon=True).start()

# ── Request / response logging ─────────────────────────────────────────────────
@app.before_request
def _before():
    request._start_time = time.monotonic()
    if request.method != 'OPTIONS':
        log_request(log, request.method, request.path)


@app.after_request
def _after(resp: Response) -> Response:
    # CORS headers
    try:
        path = request.path or ''
    except Exception:
        path = ''

    if path.startswith('/api/'):
        origin = request.headers.get('Origin')
        allowed = {'http://localhost:5173', 'http://localhost:3000', 'http://localhost:3001'}
        if origin and (origin in allowed or origin.startswith('http://localhost:')):
            resp.headers['Access-Control-Allow-Origin'] = origin
        elif not origin:
            resp.headers.setdefault('Access-Control-Allow-Origin', 'http://localhost:3000')
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
    if os.getenv('FLASK_ENV', 'development') != 'production':
        try:
            from scripts.seed_data import seed_data
            seed_data()
        except Exception as e:
            log.error(f'Error seeding data: {e}', exc_info=True)

    port = int(os.getenv('PORT', 8888))
    log.info(f'{BOLD}{CYAN}E-Mapp Backend{RESET} starting on port {BOLD}{port}{RESET}')
    app.run(host='0.0.0.0', port=port)
