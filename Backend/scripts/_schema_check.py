import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    cols = db.session.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='procedures'
        ORDER BY ordinal_position
    """)).fetchall()
    print("procedures columns:")
    for c in cols:
        print(f"  {c.column_name:30s} {c.data_type}")

    # Xem 1 row mẫu
    row = db.session.execute(text(
        "SELECT * FROM public.procedures WHERE id='dang-ky-ket-hon' LIMIT 1"
    )).fetchone()
    if row:
        print("\nSample row (dang-ky-ket-hon):")
        for k, v in dict(row._mapping).items():
            val = str(v)[:80] if v is not None else 'NULL'
            print(f"  {k}: {val}")
