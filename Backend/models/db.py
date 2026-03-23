"""
Database connection and configuration for PostgreSQL backend
"""
import os
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy import text

db = SQLAlchemy()


def get_db_url():
    """Construct PostgreSQL connection URL from environment variables"""
    db_host     = os.getenv('DB_HOST', 'localhost').strip()
    db_port     = os.getenv('DB_PORT', '5432').strip()
    db_name     = os.getenv('DB_NAME', 'postgres').strip()
    db_user     = os.getenv('DB_USER', 'postgres').strip()
    db_password = os.getenv('DB_PASSWORD', '').strip()

    # URL-encode password để xử lý ký tự đặc biệt (@, #, %, ...)
    encoded_pw = quote_plus(db_password)

    return f'postgresql://{db_user}:{encoded_pw}@{db_host}:{db_port}/{db_name}'


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

        # RAG chatbot + CAG cache tables
        try:
            rag_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(120) UNIQUE NOT NULL,
                first_message_summary TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.conversation_history (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(120) NOT NULL
                    REFERENCES public.chat_sessions(session_id) ON DELETE CASCADE,
                user_message TEXT NOT NULL,
                bot_response TEXT,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_conv_session
                ON public.conversation_history(session_id);
            CREATE INDEX IF NOT EXISTS idx_conv_timestamp
                ON public.conversation_history(timestamp);

            CREATE TABLE IF NOT EXISTS public.query_results (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER
                    REFERENCES public.conversation_history(id) ON DELETE CASCADE,
                query_text TEXT,
                response_text TEXT,
                retrieved_docs TEXT,
                model_name VARCHAR(100),
                timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.agency_queue_realtime (
                agency_id     VARCHAR(120) PRIMARY KEY,
                total_waiting INTEGER NOT NULL DEFAULT 0,
                total_serving INTEGER NOT NULL DEFAULT 0,
                load_level    VARCHAR(20) NOT NULL DEFAULT 'low',
                updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.rag_semantic_cache (
                id          SERIAL PRIMARY KEY,
                query_hash  VARCHAR(64) UNIQUE NOT NULL,
                query_text  TEXT NOT NULL,
                query_vector TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                hit_count   INTEGER NOT NULL DEFAULT 0,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                last_hit_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                expires_at  TIMESTAMPTZ NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON public.rag_semantic_cache(expires_at);
            CREATE INDEX IF NOT EXISTS idx_cache_last_hit
                ON public.rag_semantic_cache(last_hit_at DESC);
            ''')
            db.session.execute(rag_ddl)
            db.session.commit()
        except Exception as e:
            print('Warning: ensuring RAG/CAG tables failed:', e)

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
