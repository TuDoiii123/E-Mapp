import sys; sys.path.insert(0,'.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # Requirements cua dang-ky-thuong-tru
    rows = db.session.execute(text(
        "SELECT id, doc_name, template_file FROM service_requirements "
        "WHERE service_id='dang-ky-thuong-tru' ORDER BY order_index"
    )).fetchall()
    print("dang-ky-thuong-tru:")
    for r in rows:
        print(f"  {r.id} | {r.doc_name[:50]} | {r.template_file}")

    # cap-ban-sao req-002
    r2 = db.session.execute(text(
        "SELECT id, doc_name, template_file FROM service_requirements "
        "WHERE id='cap-ban-sao-trich-luc-ho-tich-req-002'"
    )).fetchone()
    print(f"\ncap-ban-sao-req-002: {r2.doc_name} | {r2.template_file}")

    # Tat ca requirements co uy quyen
    uq = db.session.execute(text(
        "SELECT id, service_id, doc_name FROM service_requirements "
        "WHERE doc_name ILIKE '%ủy quyền%' OR doc_name ILIKE '%uỷ quyền%' "
        "ORDER BY service_id"
    )).fetchall()
    print("\nRequirements co uy quyen:")
    for r in uq:
        print(f"  [{r.service_id}] {r.id} | {r.doc_name[:60]}")
