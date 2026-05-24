"""Check existing service_requirements and procedures in DB."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
app = Flask(__name__)
from models.db import init_db, db
init_db(app)

with app.app_context():
    from sqlalchemy import text
    # List tables
    tables = db.session.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    )).fetchall()
    print("=== TABLES ===")
    for t in tables:
        print(" ", t[0])

    # Check procedures
    print("\n=== PROCEDURES (first 10) ===")
    try:
        rows = db.session.execute(text(
            "SELECT id, name, category FROM public.procedures LIMIT 10"
        )).fetchall()
        for r in rows:
            print(f"  [{r[0]}] {r[1]} | {r[2]}")
        print(f"  ... total: {db.session.execute(text('SELECT COUNT(*) FROM public.procedures')).scalar()}")
    except Exception as e:
        print("  ERROR:", e)

    # Check service_requirements
    print("\n=== SERVICE_REQUIREMENTS (first 20) ===")
    try:
        rows = db.session.execute(text(
            "SELECT id, service_id, doc_name, doc_type, is_required FROM public.service_requirements LIMIT 20"
        )).fetchall()
        for r in rows:
            print(f"  [{r[1]}] {r[2]} | {r[3]} | required={r[4]}")
        total = db.session.execute(text('SELECT COUNT(*) FROM public.service_requirements')).scalar()
        print(f"  ... total: {total}")
    except Exception as e:
        print("  ERROR:", e)
