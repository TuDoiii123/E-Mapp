"""
Kết nối database cho RAG — dùng chung PostgreSQL với phần còn lại của app.
Đọc config từ biến môi trường (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).
"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from logger import get_logger

log = get_logger('connect_SQL')

_engine = None


def connect_sql():
    """Trả về SQLAlchemy engine kết nối PostgreSQL. Singleton, tạo 1 lần."""
    global _engine
    if _engine is not None:
        return _engine

    host     = os.getenv('DB_HOST', 'localhost').strip()
    port     = os.getenv('DB_PORT', '5432').strip()
    db_name  = os.getenv('DB_NAME', 'postgres').strip()
    user     = os.getenv('DB_USER', 'postgres').strip()
    password = os.getenv('DB_PASSWORD', '').strip()

    if not password:
        log.warning('[RAG] DB_PASSWORD not set — connection may fail')

    url = f'postgresql://{user}:{quote_plus(password)}@{host}:{port}/{db_name}'

    try:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={'connect_timeout': 10},
        )
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        log.info(f'[RAG] PostgreSQL connected: {host}:{port}/{db_name}')
        _engine = engine
        return _engine
    except Exception as exc:
        log.error(f'[RAG] PostgreSQL connection failed: {exc}', exc_info=True)
        return None
