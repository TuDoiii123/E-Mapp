"""
Database connection and configuration for PostgreSQL backend
"""
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool

db = SQLAlchemy()


def get_db_url():
    """Construct PostgreSQL connection URL from environment variables"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', 5432)
    db_name = os.getenv('DB_NAME', 'postgres')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'tubeo123')
    
    return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return db


def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        return result.fetchone() is not None
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
