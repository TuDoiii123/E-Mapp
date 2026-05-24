# -*- coding: utf-8 -*-
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
app = Flask(__name__)
from models.db import init_db, db
init_db(app)

with app.app_context():
    from sqlalchemy import text

    crawled_tables = ['dichvucong_thanhhoa','chitiet_thutuc','ds_dichvucong','ds_dvc_tructuyen','chitiet_dvc_tructuyen','ds_theloai']
    for tbl in crawled_tables:
        try:
            cols = db.session.execute(text(
                f"SELECT column_name FROM information_schema.columns WHERE table_name='{tbl}' AND table_schema='public'"
            )).fetchall()
            count = db.session.execute(text(f"SELECT COUNT(*) FROM public.{tbl}")).scalar()
            col_names = [c[0] for c in cols]
            print(f"\n=== {tbl} ({count} rows) ===")
            print(f"  columns: {col_names}")
            rows = db.session.execute(text(f"SELECT * FROM public.{tbl} LIMIT 3")).fetchall()
            for r in rows:
                print(f"  {dict(zip(col_names, r))}")
        except Exception as e:
            print(f"  ERROR {tbl}: {e}")

    # Check service_requirements
    try:
        count = db.session.execute(text("SELECT COUNT(*) FROM public.service_requirements")).scalar()
        print(f"\n=== service_requirements ({count} rows) ===")
        cols = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='service_requirements' AND table_schema='public'"
        )).fetchall()
        col_names = [c[0] for c in cols]
        print(f"  columns: {col_names}")
        rows = db.session.execute(text("SELECT * FROM public.service_requirements LIMIT 5")).fetchall()
        for r in rows:
            print(f"  {dict(zip(col_names, r))}")
    except Exception as e:
        print(f"  ERROR: {e}")
