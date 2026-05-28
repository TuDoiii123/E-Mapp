import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    tables = [
        'chitiet_thutuc',
        'chitiet_dvc_tructuyen',
        'dichvucong_thanhhoa',
        'ds_dichvucong',
        'ds_dvc_tructuyen',
    ]
    for tbl in tables:
        try:
            cnt = db.session.execute(text(f"SELECT COUNT(*) FROM public.{tbl}")).scalar()
            cols = db.session.execute(text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name='{tbl}'
                ORDER BY ordinal_position
            """)).fetchall()
            print(f"\n{'='*60}")
            print(f"TABLE: {tbl}  ({cnt} rows)")
            print(f"{'='*60}")
            for c in cols:
                print(f"  {c.column_name:40s} {c.data_type}")

            # Sample 2 rows
            rows = db.session.execute(text(f"SELECT * FROM public.{tbl} LIMIT 2")).fetchall()
            if rows:
                print(f"  --- sample ---")
                for row in rows:
                    d = dict(row._mapping)
                    for k, v in d.items():
                        val = str(v)[:120] if v else 'NULL'
                        print(f"    {k}: {val}")
                    print()
        except Exception as e:
            print(f"[ERR] {tbl}: {e}")
