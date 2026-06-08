"""
Audit thực: đếm unique tthc_ma trong ds_dvc_tructuyen,
rồi so với chitiet_dvc_tructuyen + dichvucong_thanhhoa
để tìm loại thủ tục phổ biến chưa có trong procedures.
"""
import sys, re
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

with app.app_context():
    # ── 1. Unique tthc_ma trong ds_dvc_tructuyen ──────────────────────────
    rows_dvc = db.session.execute(text(
        "SELECT DISTINCT tthc_ma, name FROM public.ds_dvc_tructuyen "
        "WHERE tthc_ma ~ '^[0-9]' ORDER BY tthc_ma"
    )).fetchall()
    print(f"=== ds_dvc_tructuyen: {len(rows_dvc)} unique tthc_ma ===")
    for r in rows_dvc:
        print(f"  [{r.tthc_ma}] {r.name[:80]}")

    # ── 2. chitiet_dvc_tructuyen: lấy URL → tên từ ds_dvc_tructuyen ────────
    print(f"\n=== chitiet_dvc_tructuyen ===")
    unique_ct = db.session.execute(text("""
        SELECT d.url_chi_tiet,
               s.tthc_ma,
               s.name,
               CASE WHEN d.trinh_tu_thuc_hien IS NOT NULL AND d.trinh_tu_thuc_hien != ''
                    THEN 'Y' ELSE 'N' END AS has_steps
        FROM public.chitiet_dvc_tructuyen d
        LEFT JOIN public.ds_dvc_tructuyen s ON s.url_chi_tiet = d.url_chi_tiet
        WHERE d.url_chi_tiet != 'url_chi_tiet'
        GROUP BY d.url_chi_tiet, s.tthc_ma, s.name, has_steps
        ORDER BY s.tthc_ma NULLS LAST
        LIMIT 50
    """)).fetchall()
    print(f"  Sample 50 unique URLs:")
    for r in unique_ct:
        nm = (r.name or r.url_chi_tiet or '')[:70]
        print(f"  [{r.tthc_ma or '?':12s}] [steps={r.has_steps}] {nm}")

    # ── 3. dichvucong_thanhhoa: phân tích theo field (lĩnh vực) ───────────
    print(f"\n=== dichvucong_thanhhoa: top fields (linh vuc) ===")
    fields = db.session.execute(text("""
        SELECT field, COUNT(*) as cnt
        FROM public.dichvucong_thanhhoa
        WHERE field IS NOT NULL AND field != 'field' AND field != ''
        GROUP BY field ORDER BY cnt DESC LIMIT 30
    """)).fetchall()
    for r in fields:
        print(f"  {r.cnt:6d}  {r.field[:70]}")

    # ── 4. Procedures hiện có ─────────────────────────────────────────────
    existing = db.session.execute(text(
        "SELECT id, name, category FROM public.procedures"
    )).fetchall()
    existing_ids = {r.id for r in existing}
    print(f"\n=== Procedures hien co: {len(existing)} ===")
    cats = {}
    for r in existing:
        cats.setdefault(r.category, []).append(r.name[:60])
    for cat, names in sorted(cats.items()):
        print(f"  [{cat}] {len(names)} thu tuc")
        for n in names:
            print(f"    - {n}")
