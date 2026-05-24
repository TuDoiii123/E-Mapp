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

    print("=== ds_dvc_tructuyen (mẫu thật) ===")
    rows = db.session.execute(text(
        "SELECT * FROM public.ds_dvc_tructuyen WHERE tthc_ma != 'tthc_ma' LIMIT 5"
    )).fetchall()
    for r in rows:
        print(f"  ma={r[0]} | name={r[1][:60]} | url={r[3][:50] if r[3] else ''}")

    print("\n=== chitiet_dvc_tructuyen (mẫu thật - thanh_phan_ho_so) ===")
    rows = db.session.execute(text(
        "SELECT url_chi_tiet, thanh_phan_ho_so, co_quan_thuc_hien FROM public.chitiet_dvc_tructuyen "
        "WHERE trinh_tu_thuc_hien != 'trinh_tu_thuc_hien' AND thanh_phan_ho_so IS NOT NULL AND thanh_phan_ho_so != '' LIMIT 3"
    )).fetchall()
    for r in rows:
        print(f"\n  url={r[0][:60]}")
        print(f"  co_quan={r[2][:60] if r[2] else ''}")
        print(f"  thanh_phan_ho_so=\n{r[1][:500] if r[1] else ''}")

    print("\n=== dichvucong_thanhhoa (mẫu thật) ===")
    try:
        cols = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='dichvucong_thanhhoa' AND table_schema='public'"
        )).fetchall()
        col_names = [c[0] for c in cols]
        print(f"  columns: {col_names}")
        rows = db.session.execute(text(
            "SELECT * FROM public.dichvucong_thanhhoa WHERE id != 'id' LIMIT 3"
        )).fetchall()
        for r in rows:
            print(f"  {dict(zip(col_names, r))}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n=== service_requirements (mẫu thật) ===")
    try:
        rows = db.session.execute(text(
            "SELECT * FROM public.service_requirements LIMIT 5"
        )).fetchall()
        cols = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='service_requirements' AND table_schema='public'"
        )).fetchall()
        col_names = [c[0] for c in cols]
        print(f"  columns: {col_names}")
        for r in rows:
            print(f"  {dict(zip(col_names, r))}")
    except Exception as e:
        print(f"  ERROR: {e}")
