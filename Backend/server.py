"""
Flask application entry point.
All business logic lives in routes/ blueprints.
"""
import os
import threading

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

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
    print('PostgreSQL database initialized')
except Exception as e:
    print(f'Database initialization skipped: {e}')

# ── Auth middleware ────────────────────────────────────────────────────────────
from middleware.auth import init_auth
init_auth(app)

# ── Blueprints ─────────────────────────────────────────────────────────────────
_blueprints = [
    ('routes.auth_routes', 'auth_bp'),
    ('routes.services_routes', 'services_bp'),
    ('routes.applications_routes', 'applications_bp'),
    ('routes.admin_routes', 'admin_bp'),
    ('routes.appointments_routes', 'appointments_bp'),
    ('routes.voice_routes', 'voice_bp'),
    ('routes.rag_routes', 'rag_bp'),
]

for module_path, bp_name in _blueprints:
    try:
        import importlib
        module = importlib.import_module(module_path)
        app.register_blueprint(getattr(module, bp_name))
        print(f'[OK] {bp_name} registered')
    except Exception as e:
        print(f'[ERROR] {bp_name} failed: {e}')

# ── Preload SuggestProcedure in background ────────────────────────────────────
def _preload_suggest():
    try:
        from routes.rag_routes import init_document_suggestion
        init_document_suggestion()
    except Exception as e:
        print(f'[SuggestProcedure][preload] {e}')

_t = threading.Thread(target=_preload_suggest, daemon=True)
_t.start()

# ── CORS fallback + catch-all preflight ───────────────────────────────────────
@app.route('/api/<path:any_path>', methods=['OPTIONS'])
def api_catch_all_options(any_path: str):
    return ('', 200)


@app.after_request
def add_cors_headers(resp: Response):
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
        resp.headers.setdefault('Access-Control-Allow-Headers', req_hdrs or 'Content-Type,Authorization,X-Requested-With,Accept')
        if request.headers.get('Access-Control-Request-Private-Network', '').lower() == 'true':
            resp.headers['Access-Control-Allow-Private-Network'] = 'true'
        resp.headers.setdefault('Access-Control-Max-Age', '86400')
    return resp


# ── Health check ───────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Public Services Backend API'})


# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    try:
        method = request.method or ''
        path = request.path or ''
    except Exception:
        method = path = ''
    if method == 'OPTIONS' and path.startswith('/api/'):
        return ('', 200)
    return jsonify({'success': False, 'message': 'Route not found'}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    if os.getenv('FLASK_ENV', 'development') != 'production':
        try:
            from scripts.seed_data import seed_data
            seed_data()
        except Exception as e:
            print('Error seeding data:', e)

    port = int(os.getenv('PORT', 8888))
    app.run(host='0.0.0.0', port=port)
