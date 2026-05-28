import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    rows = db.session.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    )).fetchall()
    print("Tables:")
    for r in rows:
        print(f"  {r.tablename}")
