import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # List all tables in public schema
    rows = db.session.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)).fetchall()
    print("=== TABLES ===")
    for r in rows:
        print(" ", r.table_name)

    print()

    # Check tables that might contain DVC/procedure data
    candidates = ['public_services', 'services', 'dvc_procedures', 'dichvu',
                  'thu_tuc', 'procedures_detail', 'dvc', 'service_detail']
    for tbl in candidates:
        try:
            cnt = db.session.execute(text(f"SELECT COUNT(*) FROM public.{tbl}")).scalar()
            cols = db.session.execute(text(f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name='{tbl}'
                ORDER BY ordinal_position
            """)).fetchall()
            print(f"=== {tbl} ({cnt} rows) ===")
            print("  Cols:", [c.column_name for c in cols])
        except:
            pass
