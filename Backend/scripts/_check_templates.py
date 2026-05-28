import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # All templates
    rows = db.session.execute(text("""
        SELECT ft.id, ft.name, ft.service_id, ft.filename,
               ft.original_name, ft.storage_path
        FROM form_templates ft
        ORDER BY ft.service_id, ft.id
    """)).fetchall()
    print(f"Total form_templates: {len(rows)}")
    for r in rows:
        has_file = "OK" if r.storage_path else "NO FILE"
        print(f"  svc={r.service_id or '---':40s} | {(r.name or '')[:45]:45s} | {r.filename or 'NULL':30s} [{has_file}]")

    # service_id => procedures.id khop?
    print("\n--- service_id unique ---")
    svc_ids = db.session.execute(text(
        "SELECT DISTINCT service_id FROM form_templates WHERE service_id IS NOT NULL ORDER BY service_id"
    )).fetchall()
    for r in svc_ids:
        print(f"  {r.service_id}")

    # Procedures co template
    print("\n--- Procedures co template (khop service_id) ---")
    matched = db.session.execute(text("""
        SELECT p.id, p.name, COUNT(ft.id) as tmpl_count
        FROM procedures p
        JOIN form_templates ft ON ft.service_id = p.id
        GROUP BY p.id, p.name
        ORDER BY p.id
    """)).fetchall()
    for r in matched:
        print(f"  {r.id:40s} {r.tmpl_count} template(s) -- {r.name}")

    # Procedures CHUA co template
    print("\n--- Procedures CHUA co template ---")
    missing = db.session.execute(text("""
        SELECT p.id, p.name, p.category
        FROM procedures p
        WHERE p.is_active = true
          AND p.id NOT LIKE '%.%'
          AND p.id NOT IN (
              SELECT DISTINCT service_id FROM form_templates WHERE service_id IS NOT NULL
          )
        ORDER BY p.category, p.id
    """)).fetchall()
    for r in missing:
        print(f"  [{r.category:12s}] {r.id:45s} {r.name}")
    print(f"\nMissing: {len(missing)}")
