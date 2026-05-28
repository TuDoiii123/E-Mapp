import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # 1. Service requirements co/chua co template_file
    rows = db.session.execute(text("""
        SELECT sr.service_id, sr.doc_name, sr.template_file, sr.is_required, sr.doc_type
        FROM service_requirements sr
        WHERE sr.template_file IS NOT NULL AND sr.template_file != ''
        ORDER BY sr.service_id
    """)).fetchall()
    print(f"Requirements co template_file: {len(rows)}")
    for r in rows:
        print(f"  [{r.service_id}] {r.doc_name[:50]:50s} => {r.template_file}")

    # 2. Danh sach file trong data/templates
    import os
    tdir = os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')
    tdir = os.path.normpath(tdir)
    files = sorted(f for f in os.listdir(tdir) if f.endswith(('.doc', '.docx')))
    print(f"\nTemplate files in {tdir}: {len(files)}")
    for f in files:
        size = os.path.getsize(os.path.join(tdir, f))
        print(f"  {f:55s} {size//1024:5d} KB")

    # 3. Tong requirements chua co template
    total = db.session.execute(text(
        "SELECT COUNT(*) FROM service_requirements WHERE template_file IS NULL OR template_file=''"
    )).scalar()
    print(f"\nRequirements chua co template_file: {total}")

    # 4. Mau requirements theo procedure
    print("\n--- Requirements per procedure (sample) ---")
    sample = db.session.execute(text("""
        SELECT p.id, p.name, COUNT(sr.id) as reqs,
               SUM(CASE WHEN sr.template_file IS NOT NULL AND sr.template_file != '' THEN 1 ELSE 0 END) as with_tmpl
        FROM procedures p
        JOIN service_requirements sr ON sr.service_id = p.id
        WHERE p.id NOT LIKE '%.%' AND p.is_active = true
        GROUP BY p.id, p.name
        ORDER BY p.id
        LIMIT 40
    """)).fetchall()
    for r in sample:
        flag = "OK" if r.with_tmpl > 0 else "--"
        print(f"  [{flag}] {r.id:45s} {r.reqs} reqs, {r.with_tmpl} with template")
