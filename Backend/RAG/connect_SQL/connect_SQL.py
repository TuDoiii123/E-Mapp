from sqlalchemy import create_engine
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent / "config.json"


def connect_sql():
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.warning("Không tìm thấy config SQL: %s", _CONFIG_PATH)
        return None

    conn_cfg = config.get("connection", {})
    DB_SERVER = conn_cfg.get("server", "")
    DB_DATABASE = conn_cfg.get("database", "")
    DB_USERNAME = conn_cfg.get("username", "")
    DB_PASSWORD = conn_cfg.get("password", "")

    # Nếu chưa cấu hình, bỏ qua kết nối
    if not DB_SERVER or not DB_DATABASE:
        logger.info("SQL Server chưa được cấu hình (config.json trống).")
        return None

    ODBC_DRIVER = "ODBC Driver 17 for SQL Server"
    CONNECTION_STRING = (
        f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}"
        f"?driver={ODBC_DRIVER.replace(' ', '+')}"
    )

    try:
        engine = create_engine(CONNECTION_STRING)
        with engine.connect():
            pass
        logger.info("Kết nối tới SQL Server thành công!")
        return engine
    except Exception as e:
        logger.error("Lỗi kết nối SQL Server: %s", e)
        return None

