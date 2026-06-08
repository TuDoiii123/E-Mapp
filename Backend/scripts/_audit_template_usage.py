import sys, os
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

TDIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'templates'))

with app.app_context():
    # Tat ca template_file dang duoc dung trong DB
    used = db.session.execute(text("""
        SELECT DISTINCT template_file, service_id, doc_name
        FROM service_requirements
        WHERE template_file IS NOT NULL AND template_file != ''
        ORDER BY template_file
    """)).fetchall()
    used_files = {}
    for r in used:
        used_files.setdefault(r.template_file, []).append(f"{r.service_id} / {r.doc_name[:40]}")

    # Tat ca file tren disk
    disk_files = sorted(f for f in os.listdir(TDIR) if f.endswith(('.doc', '.docx', '.pdf')))

    used_set   = set(used_files.keys())
    disk_set   = set(disk_files)
    unused     = sorted(disk_set - used_set)
    missing    = sorted(used_set - disk_set)   # duoc dung nhung file khong ton tai

    print(f"Tong file tren disk : {len(disk_files)}")
    print(f"Dang duoc assign    : {len(used_set)}")
    print(f"Chua duoc dung      : {len(unused)}")
    print(f"Assign nhung mat file: {len(missing)}")

    if missing:
        print("\n!!! ASSIGN NHUNG KHONG CO FILE:")
        for f in missing:
            print(f"  {f}")

    print("\n=== DA DUOC DUNG ===")
    for f in sorted(used_files):
        print(f"  {f}")
        for ref in used_files[f]:
            print(f"      -> {ref}")

    print(f"\n=== CHUA DUOC DUNG ({len(unused)} files) ===")
    for f in unused:
        size = os.path.getsize(os.path.join(TDIR, f)) // 1024
        print(f"  {f:55s} {size:4d}KB")
