"""
Database connection and configuration for PostgreSQL backend
"""
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy import text

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
        # Create any SQLAlchemy models (if defined) and ensure 'users' table exists
        try:
            db.create_all()
        except Exception as e:
            # non-fatal: continue to ensure users table via raw SQL
            print('Warning: db.create_all() failed:', e)

        # Run explicit DDL to ensure users table exists for raw SQL access
        try:
            users_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.users (
              id VARCHAR(80) PRIMARY KEY,
              cccd_number VARCHAR(50) UNIQUE,
              full_name VARCHAR(255),
              date_of_birth VARCHAR(50),
              phone VARCHAR(50),
              email VARCHAR(255) UNIQUE,
              password VARCHAR(255),
              role VARCHAR(50) NOT NULL DEFAULT 'citizen',
              is_vneid_verified BOOLEAN NOT NULL DEFAULT FALSE,
              vneid_id VARCHAR(255),
              created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
            CREATE INDEX IF NOT EXISTS idx_users_cccd ON public.users(cccd_number);
            ''')
            db.session.execute(users_ddl)
            db.session.commit()
        except Exception as e:
            print('Warning: ensuring users table failed:', e)

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
