import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    rows = db.session.execute(text("""
        SELECT id, name, category, implementing_level,
               COALESCE(steps, '') AS steps,
               COALESCE(conditions, '') AS conds
        FROM public.procedures
        ORDER BY category, name
    """)).fetchall()

    total = len(rows)
    ok = sum(1 for r in rows if r.steps.strip() and r.conds.strip())
    missing = total - ok
    print(f"Tong: {total} thu tuc | OK (co steps+cond): {ok} | Thieu: {missing}\n")

    cats = {}
    for r in rows:
        has_steps = bool(r.steps.strip())
        has_cond  = bool(r.conds.strip())
        flag = []
        if not has_steps: flag.append('NO_STEPS')
        if not has_cond:  flag.append('NO_COND')
        status = '[' + ','.join(flag) + ']' if flag else '[OK]'
        cats.setdefault(r.category, []).append(
            f"  {status:25s} {r.id:15s} {r.name}"
        )

    for cat, items in sorted(cats.items()):
        print(f"=== {cat} ({len(items)}) ===")
        for i in items:
            print(i)
        print()
