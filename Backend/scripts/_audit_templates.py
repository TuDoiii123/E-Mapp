import sys, os
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # Procedures chua co bat ky template nao
    rows = db.session.execute(text("""
        SELECT sr.service_id, sr.doc_name
        FROM service_requirements sr
        WHERE (sr.template_file IS NULL OR sr.template_file = '')
          AND sr.service_id NOT LIKE '%.%'
          AND sr.service_id NOT IN (
              SELECT DISTINCT service_id FROM service_requirements
              WHERE template_file IS NOT NULL AND template_file != ''
          )
        ORDER BY sr.service_id, sr.id
    """)).fetchall()

    print("Procedures CHUA CO template:")
    prev = None
    for r in rows:
        if r.service_id != prev:
            print(f"  [{r.service_id}]")
            prev = r.service_id
        print(f"    - {r.doc_name[:65]}")

    # Danh sach file hien co
    tdir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'templates'))
    files = sorted(f for f in os.listdir(tdir) if f.endswith(('.doc', '.docx', '.pdf')))
    print(f"\nFile template hien co ({len(files)}):")
    for f in files:
        size = os.path.getsize(os.path.join(tdir, f)) // 1024
        print(f"  {f:55s} {size:5d} KB")
