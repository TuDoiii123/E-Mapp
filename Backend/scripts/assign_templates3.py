"""
1. Assign mau-to-khai-dang-ky-thuong-tru.docx -> dang-ky-thuong-tru-req-000
2. Tao procedure dang-ky-nuoi-con-nuoi + assign mau-to-khai-dang-ky-nuoi-con-nuoi.docx
3. Assign mau-giay-uy-quyen.docx -> tat ca req co uy quyen
4. Xoa mau-khai-dang-ky-xe-co-gioi.docx (trung voi file moi)
"""
import sys, os, uuid
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

TDIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'templates'))


def upd(cur, req_id, tmpl):
    cur.execute(text(
        "UPDATE service_requirements SET template_file=:t WHERE id=:r"
    ), {'t': tmpl, 'r': req_id})
    print(f"  SET {req_id[:55]:55s} => {tmpl}")


with app.app_context():
    # ── 1. thuong-tru dung form rieng thay vi CT01 ─────────────────────────
    print("=== 1. dang-ky-thuong-tru ===")
    upd(db.session, 'dang-ky-thuong-tru-req-000', 'mau-to-khai-dang-ky-thuong-tru.docx')

    # ── 2. Tao procedure + requirement cho nuoi-con-nuoi ───────────────────
    print("\n=== 2. dang-ky-nuoi-con-nuoi ===")
    exists = db.session.execute(text(
        "SELECT id FROM procedures WHERE id='dang-ky-nuoi-con-nuoi'"
    )).fetchone()

    if not exists:
        steps = (
            "Bước 1: Chuẩn bị hồ sơ theo danh mục quy định\n"
            "Bước 2: Nộp hồ sơ tại Phòng Tư pháp huyện/quận\n"
            "Bước 3: Cán bộ thẩm tra, xác minh hồ sơ và điều kiện nuôi con nuôi\n"
            "Bước 4: UBND huyện ra quyết định, tổ chức giao nhận con nuôi tại Phòng Tư pháp"
        )
        conditions = (
            "Người nhận nuôi phải từ 20 tuổi trở lên và hơn con nuôi ít nhất 20 tuổi\n"
            "Không bị hạn chế hoặc mất năng lực hành vi dân sự\n"
            "Có điều kiện về sức khoẻ, kinh tế, chỗ ở để nuôi dưỡng trẻ\n"
            "Không đang chấp hành hình phạt tù hoặc bị truy cứu trách nhiệm hình sự"
        )
        db.session.execute(text("""
            INSERT INTO procedures (
                id, name, code, category, fee, fee_note,
                processing_days, processing_note, implementing_level,
                agency, is_online, is_active, steps, conditions
            ) VALUES (
                'dang-ky-nuoi-con-nuoi',
                'Đăng ký nuôi con nuôi trong nước',
                'TTLT-2014-09',
                'civil',
                400000,
                'Miễn phí với gia đình chính sách, hộ nghèo',
                30,
                '30 ngày kể từ ngày nhận đủ hồ sơ hợp lệ',
                'district',
                'Phòng Tư pháp cấp huyện',
                false,
                true,
                :steps,
                :conditions
            ) ON CONFLICT (id) DO NOTHING
        """), {'steps': steps, 'conditions': conditions})
        print("  + Tao procedure dang-ky-nuoi-con-nuoi")
    else:
        print("  ALREADY EXISTS: dang-ky-nuoi-con-nuoi")

    # Insert requirements
    reqs = [
        ('dang-ky-nuoi-con-nuoi-req-000', 'Tờ khai đăng ký nuôi con nuôi (Mẫu TP/CCN-2014-TKNNN.1)',
         '', True, 'original', 0, 'mau-to-khai-dang-ky-nuoi-con-nuoi.docx'),
        ('dang-ky-nuoi-con-nuoi-req-001', 'CCCD / Căn cước của cha/mẹ nuôi',
         '', True, 'original', 1, None),
        ('dang-ky-nuoi-con-nuoi-req-002', 'Giấy khai sinh / trích lục khai sinh của trẻ',
         '', True, 'certified_copy', 2, None),
        ('dang-ky-nuoi-con-nuoi-req-003', 'Giấy chứng nhận tình trạng hôn nhân của cha/mẹ nuôi',
         '', True, 'original', 3, None),
        ('dang-ky-nuoi-con-nuoi-req-004', 'Phiếu lý lịch tư pháp của cha/mẹ nuôi',
         '', True, 'original', 4, None),
        ('dang-ky-nuoi-con-nuoi-req-005', 'Văn bản đồng ý của cha/mẹ đẻ hoặc người giám hộ',
         '', True, 'original', 5, None),
    ]
    for rid, name, desc, req, dtype, order, tmpl in reqs:
        db.session.execute(text("""
            INSERT INTO service_requirements
                (id, service_id, doc_name, doc_description, is_required, doc_type, order_index, template_file)
            VALUES (:id, 'dang-ky-nuoi-con-nuoi', :name, :desc, :req, :dtype, :order, :tmpl)
            ON CONFLICT (id) DO NOTHING
        """), {'id': rid, 'name': name, 'desc': desc, 'req': req,
               'dtype': dtype, 'order': order, 'tmpl': tmpl})
        print(f"  + req {rid}")

    # ── 3. Assign giay-uy-quyen vao tat ca req co uy quyen ─────────────────
    print("\n=== 3. mau-giay-uy-quyen.docx ===")
    uy_quyen_reqs = [
        'cap-ban-sao-trich-luc-ho-tich-req-002',
        'cap-phieu-lltp-req-003',
        'dang-ky-ho-kinh-doanh-req-003',
        '1.001193-req-008',
        '1.004873-req-007',
        'cap_phieu_lltp-req-003',
    ]
    for rid in uy_quyen_reqs:
        row = db.session.execute(text(
            "SELECT id, template_file FROM service_requirements WHERE id=:r"
        ), {'r': rid}).fetchone()
        if not row:
            print(f"  SKIP (not found) {rid}")
            continue
        if row.template_file == 'mau-giay-uy-quyen.docx':
            print(f"  ALREADY {rid}")
            continue
        upd(db.session, rid, 'mau-giay-uy-quyen.docx')

    db.session.commit()

    # ── 4. Xoa file trung ──────────────────────────────────────────────────
    print("\n=== 4. Xoa mau-khai-dang-ky-xe-co-gioi.docx ===")
    old_file = os.path.join(TDIR, 'mau-khai-dang-ky-xe-co-gioi.docx')
    if os.path.exists(old_file):
        # Kiem tra DB truoc khi xoa
        still_used = db.session.execute(text(
            "SELECT COUNT(*) FROM service_requirements WHERE template_file='mau-khai-dang-ky-xe-co-gioi.docx'"
        )).scalar()
        if still_used:
            print(f"  WARNING: van con {still_used} req dung file nay, skip xoa")
        else:
            os.remove(old_file)
            print("  Xoa thanh cong")
    else:
        print("  File khong ton tai (da xoa truoc)")

    # ── Tong ket ──────────────────────────────────────────────────────────
    total_tmpl = db.session.execute(text(
        "SELECT COUNT(*) FROM service_requirements WHERE template_file IS NOT NULL AND template_file!=''"
    )).scalar()
    total_proc = db.session.execute(text("SELECT COUNT(*) FROM procedures WHERE is_active=true")).scalar()
    files = [f for f in os.listdir(TDIR) if f.endswith(('.doc','.docx','.pdf'))]
    print(f"\n=== Tong ket ===")
    print(f"  Procedures active : {total_proc}")
    print(f"  Req co template   : {total_tmpl}")
    print(f"  Files tren disk   : {len(files)}")
