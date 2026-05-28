import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    rows = db.session.execute(text("""
        SELECT id, name,
               COALESCE(steps,'') as steps,
               COALESCE(conditions,'') as conds
        FROM public.procedures WHERE id NOT LIKE '%.%'
        ORDER BY id
    """)).fetchall()
    for r in rows:
        lines_s = [l.strip() for l in r.steps.splitlines() if l.strip()]
        lines_c = [l.strip() for l in r.conds.splitlines() if l.strip()]
        print(f"\n[{r.id}]  steps={len(lines_s)}, conds={len(lines_c)}")
        for i, l in enumerate(lines_s[:4], 1):
            print(f"  S{i}: {l[:90]}")
        if lines_c:
            print(f"  C1: {lines_c[0][:90]}")
