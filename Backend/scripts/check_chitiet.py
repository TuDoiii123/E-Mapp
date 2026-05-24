# -*- coding: utf-8 -*-
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv; load_dotenv()
from flask import Flask; app = Flask(__name__)
from models.db import init_db, db; init_db(app)

with app.app_context():
    from sqlalchemy import text
    r = db.session.execute(text(
        "SELECT COUNT(*) FROM public.chitiet_dvc_tructuyen "
        "WHERE length(thanh_phan_ho_so) > 10 AND thanh_phan_ho_so != 'thanh_phan_ho_so'"
    )).scalar()
    print(f"chitiet with real thanh_phan_ho_so: {r}")

    rows = db.session.execute(text(
        "SELECT url_chi_tiet, thanh_phan_ho_so FROM public.chitiet_dvc_tructuyen "
        "WHERE length(thanh_phan_ho_so) > 10 AND thanh_phan_ho_so != 'thanh_phan_ho_so' LIMIT 3"
    )).fetchall()
    for row in rows:
        print(f"\nURL: {row[0]}")
        print(f"HO_SO: {row[1][:400]}")

    # Check ds_dvc_tructuyen to match
    print("\n\n=== ds_dvc_tructuyen sample ===")
    rows2 = db.session.execute(text(
        "SELECT tthc_ma, name, url_chi_tiet FROM public.ds_dvc_tructuyen "
        "WHERE tthc_ma != 'tthc_ma' LIMIT 8"
    )).fetchall()
    for r in rows2:
        print(f"  {r[0]} | {r[1][:60]}")

    # Service_requirements breakdown by prefix
    print("\n=== service_requirements groups ===")
    rows3 = db.session.execute(text(
        "SELECT DISTINCT split_part(id, '-req-', 1) as grp, COUNT(*) "
        "FROM public.service_requirements GROUP BY grp ORDER BY grp"
    )).fetchall()
    for r in rows3:
        print(f"  {r[0]}: {r[1]} docs")
