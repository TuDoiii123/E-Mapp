import os
import jwt
from flask import request, jsonify
from models.user import User

JWT_SECRET = os.getenv('JWT_SECRET', 'default-secret-key-change-in-production')


def load_user_from_token():
    """Decode JWT (if present) and attach user info to `request` proxy."""
    auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) < 2:
        return None
    token = parts[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': 'TokenExpired'}
    except jwt.InvalidTokenError:
        return {'error': 'InvalidToken'}

    user_id = payload.get('userId')
    if not user_id:
        return None

    user = User.find_by_id(user_id)
    if not user:
        return None

    # Attach attributes on the `request` object (flask's request is a proxy)
    try:
        request.user = user
        request.user_id = user.get('id')
        request.role = user.get('role')
    except Exception:
        # If assignment fails for some reason, attach to flask.g instead
        from flask import g
        g.user = user
        g.user_id = user.get('id')
        g.role = user.get('role')

    return user


def init_auth(app):
    """Register a before_request handler that loads user from Authorization header (if present)."""
    @app.before_request
    def _load_user():
        result = load_user_from_token()
        # If token invalid, we don't abort here — endpoints can check for auth explicitly.
        if isinstance(result, dict) and result.get('error') == 'TokenExpired':
            # set a flag so handlers can use it if they want
            request._token_error = 'expired'
        elif isinstance(result, dict) and result.get('error') == 'InvalidToken':
            request._token_error = 'invalid'


def require_role(*allowed_roles):
    """Decorator to require a role. Usage: @require_role('admin')"""
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Prefer request attributes
            role = getattr(request, 'role', None)
            if not role:
                from flask import g
                role = getattr(g, 'role', None)

            if not role:
                return jsonify({'success': False, 'message': 'Chưa xác thực'}), 401

            if role not in allowed_roles:
                return jsonify({'success': False, 'message': 'Bạn không có quyền truy cập tài nguyên này'}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


require_admin = require_role('admin')
require_citizen = require_role('citizen')


def authenticate_token():
    """Decorator to require an authenticated user (any role)."""
    from functools import wraps

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                from flask import g
                user = getattr(g, 'user', None)
            if not user:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            return fn(*args, **kwargs)
        return wrapper

    return decorator
