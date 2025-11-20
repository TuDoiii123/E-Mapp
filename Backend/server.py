from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from middleware.auth import init_auth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

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
