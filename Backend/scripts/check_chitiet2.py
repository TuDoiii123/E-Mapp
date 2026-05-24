# -*- coding: utf-8 -*-
import sys, os, io, logging
logging.disable(logging.CRITICAL)  # Suppress all logs
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv; load_dotenv()
from flask import Flask; app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER','postgres')}:{os.getenv('DB_PASSWORD','')}@"
    f"{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME','postgres')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

with app.app_context():
    from sqlalchemy import text

    r = db.session.execute(text(
        "SELECT COUNT(*) FROM public.chitiet_dvc_tructuyen "
        "WHERE length(thanh_phan_ho_so) > 10 AND thanh_phan_ho_so != 'thanh_phan_ho_so'"
    )).scalar()
    print(f"chitiet_dvc_tructuyen with real thanh_phan_ho_so: {r}")

    rows = db.session.execute(text(
        "SELECT url_chi_tiet, thanh_phan_ho_so FROM public.chitiet_dvc_tructuyen "
        "WHERE length(thanh_phan_ho_so) > 10 AND thanh_phan_ho_so != 'thanh_phan_ho_so' LIMIT 3"
    )).fetchall()
    for i, row in enumerate(rows):
        print(f"\n--- Sample {i+1} ---")
        print(f"URL: {row[0]}")
        print(f"HO_SO:\n{row[1][:500]}")

    print("\n\n=== ds_dvc_tructuyen (first 10 real rows) ===")
    rows2 = db.session.execute(text(
        "SELECT tthc_ma, name FROM public.ds_dvc_tructuyen WHERE tthc_ma != 'tthc_ma' LIMIT 10"
    )).fetchall()
    for r in rows2:
        print(f"  {r[0]} | {r[1][:70]}")

    print("\n=== service_requirements groups ===")
    rows3 = db.session.execute(text(
        "SELECT split_part(id, '-req-', 1) as grp, COUNT(*) "
        "FROM public.service_requirements GROUP BY grp ORDER BY grp"
    )).fetchall()
    for r in rows3:
        print(f"  {r[0]}: {r[1]} tài liệu")
