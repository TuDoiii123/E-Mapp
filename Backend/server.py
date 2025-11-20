from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from middleware.auth import init_auth

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register blueprints (routes) if present
try:
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
except Exception:
    pass

try:
    from routes.services_routes import services_bp
    app.register_blueprint(services_bp)
except Exception:
    pass

try:
    from routes.applications_routes import applications_bp
    app.register_blueprint(applications_bp)
except Exception:
    pass

try:
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)
except Exception:
    pass

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
