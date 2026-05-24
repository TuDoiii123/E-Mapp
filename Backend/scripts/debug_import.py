# -*- coding: utf-8 -*-
import sys, os, io, re, logging
logging.disable(logging.CRITICAL)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv; load_dotenv()
from flask import Flask; app = Flask(__name__)
u = os.getenv('DB_USER','postgres'); p = os.getenv('DB_PASSWORD','')
h = os.getenv('DB_HOST','localhost'); port = os.getenv('DB_PORT','5432'); dbn = os.getenv('DB_NAME','postgres')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{u}:{p}@{h}:{port}/{dbn}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy(app)

with app.app_context():
    from sqlalchemy import text

    # 1. Check procedures constraints
    cons = db.session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name='procedures' AND table_schema='public'
    """)).fetchall()
    print("Procedures constraints:", cons)

    # 2. Try inserting one procedure manually
    try:
        db.session.execute(text("""
            INSERT INTO public.procedures (id, name, code, category, fee, fee_note,
                processing_days, processing_note, legal_basis, implementing_level,
                agency, is_online, is_active, created_at, updated_at)
            VALUES ('1.001193', 'Thủ tục đăng ký khai sinh', '1.001193', 'civil',
                0, '', NULL, '', '[]'::jsonb, '', 'UBND cấp xã',
                true, true, NOW(), NOW())
        """))
        db.session.commit()
        print("✅ Test insert OK")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Test insert FAILED: {e}")

    # 3. Check URL format in chitiet
    rows = db.session.execute(text(
        "SELECT url_chi_tiet FROM public.chitiet_dvc_tructuyen LIMIT 5"
    )).fetchall()
    print("\nSample chitiet URLs:")
    for r in rows:
        print(f"  {r[0]}")

    # 4. Check URL format in ds_dvc
    rows2 = db.session.execute(text(
        "SELECT tthc_ma, url_chi_tiet FROM public.ds_dvc_tructuyen WHERE tthc_ma != 'tthc_ma' LIMIT 5"
    )).fetchall()
    print("\nSample ds_dvc_tructuyen:")
    for r in rows2:
        print(f"  ma={r[0]} | url={r[1]}")
