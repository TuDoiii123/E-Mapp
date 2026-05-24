# -*- coding: utf-8 -*-
"""
Import procedures + service_requirements từ dữ liệu crawl trong DB.
Chạy: python scripts/import_procedures_from_crawl.py
"""
import sys, os, io, re, logging
logging.disable(logging.CRITICAL)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv; load_dotenv()

from flask import Flask
app = Flask(__name__)
u = os.getenv('DB_USER', 'postgres'); pw = os.getenv('DB_PASSWORD', '')
h = os.getenv('DB_HOST', 'localhost'); pt = os.getenv('DB_PORT', '5432')
dbn = os.getenv('DB_NAME', 'postgres')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{u}:{pw}@{h}:{pt}/{dbn}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy(app)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_ma(url: str) -> str:
    m = re.search(r'ma_thu_tuc=([^&\s]+)', url or '')
    return m.group(1).strip() if m else ''

FILE_EXT = re.compile(r'\S+\.(doc|docx|pdf|xls|xlsx|png|jpg|zip)\s*$', re.IGNORECASE)
QUANTITY_RE = re.compile(r'b[aả]n\s+ch[íi]nh\s*:\s*(\d+)', re.IGNORECASE)

SKIP_SET = {
    'bao gồm', 'tên giấy tờ', 'mẫu đơn, tờ khai', 'số lượng',
    'mẫu đơn tờ khai', 'thanh_phan_ho_so', 'bao gom', 'ten giay to',
    'so luong', 'thu tuc', 'trinh tu thuc hien', 'cach thuc thuc hien',
}

def parse_ho_so(raw: str) -> list[dict]:
    if not raw or len(raw) < 15:
        return []
    docs, order = [], 0
    current = None
    for line in raw.splitlines():
        line = line.strip()
        if not line or len(line) < 5:
            continue
        low = line.lower().strip('-• *\t')
        if low in SKIP_SET or low.startswith('trường hợp') and len(low) < 20:
            continue
        if FILE_EXT.match(line):
            continue
        q = QUANTITY_RE.search(line)
        if q:
            if current:
                current['is_required'] = int(q.group(1)) > 0
            continue
        if 'bản sao' in low and len(line) < 30:
            continue
        # New doc item
        name = re.sub(r'^[-•*\s]+', '', line).strip()
        if len(name) < 5:
            continue
        if current:
            docs.append(current)
        current = {
            'doc_name': name[:255],
            'doc_description': '',
            'is_required': True,
            'doc_type': 'original',
            'order_index': order,
        }
        order += 1
    if current:
        docs.append(current)
    return docs[:15]

CATEGORY_KW = [
    ('land',         ['đất đai', 'bất động sản', 'qsdđ', 'sổ đỏ', 'sổ hồng', 'nhà ở']),
    ('civil',        ['hộ tịch', 'khai sinh', 'kết hôn', 'cư trú', 'hộ khẩu', 'cccd', 'căn cước', 'khai tử', 'quốc tịch']),
    ('business',     ['doanh nghiệp', 'kinh doanh', 'hộ kinh doanh', 'thành lập', 'đăng ký kinh']),
    ('construction', ['xây dựng', 'giấy phép xây', 'quy hoạch']),
    ('transport',    ['lái xe', 'gplx', 'vận tải', 'xe ô tô', 'xe máy', 'đăng kiểm']),
    ('tax',          ['thuế', 'mã số thuế', 'hóa đơn']),
    ('insurance',    ['bảo hiểm', 'bhxh', 'bhyt', 'hưu trí', 'thai sản']),
    ('health',       ['y tế', 'sức khỏe', 'hành nghề y', 'dược']),
    ('education',    ['giáo dục', 'bằng cấp', 'học bạ', 'trường']),
    ('justice',      ['tư pháp', 'công chứng', 'lý lịch', 'chứng thực']),
]

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KW:
        if any(k in t for k in kws):
            return cat
    return 'civil'

PROC_ICON = {
    'land': '🏠', 'civil': '👤', 'business': '🏢', 'construction': '🏗️',
    'transport': '🚗', 'tax': '💰', 'insurance': '🛡️', 'health': '⚕️',
    'education': '🎓', 'justice': '⚖️',
}

# Mapping existing service_requirements groups → TTHC codes
LEGACY_MAP = {
    'ket_hon': '1.000894',
    'khai_sinh': '1.001193',
    'cap_cccd': '2.001642',
    'doi_cccd': '2.001642',
    'dang_ky_thuong_tru': '1.003018',
    'xac_nhan_cu_tru': '1.003018',
    'cap_gplx_b1': '1.000703',
    'doi_gplx': '2.002286',
    'cap_phep_xay_dung': '1.003705',
    'cap_gcn_dat': '1.003966',
    'chuyen_nhuong_qsdd': '1.005189',
    'dang_ky_ho_kinh_doanh': '1.001090',
    'dang_ky_cong_ty_tnhh': '2.00161',
    'dang_ky_ma_so_thue': '1.007017',
    'cap_phieu_lltp': '1.001135',
    'nhap_quoc_tich': '1.005235',
    'khai_tu': '1.004879',
    'cap_so_bhxh': '1.007009',
    'huong_bhxh_mot_lan': '1.006545',
    'cap_giay_kham_suc_khoe': '1.000920',
    'cong_nhan_bang': '2.000033',
    'cong_chung_hop_dong': '1.007030',
}

# ── Main ──────────────────────────────────────────────────────────────────────

with app.app_context():
    from sqlalchemy import text

    # 1. Lấy ds_dvc_tructuyen (bỏ header BOM)
    print("📥 Đọc ds_dvc_tructuyen...")
    dvc = db.session.execute(text(
        "SELECT TRIM(BOTH FROM REPLACE(tthc_ma, E'\\uFEFF', '')), "
        "       TRIM(name), url_chi_tiet "
        "FROM public.ds_dvc_tructuyen "
        "WHERE TRIM(BOTH FROM REPLACE(tthc_ma, E'\\uFEFF', '')) != 'tthc_ma' "
        "AND tthc_ma IS NOT NULL AND length(TRIM(name)) > 3"
    )).fetchall()
    print(f"   → {len(dvc)} thủ tục")

    # 2. Lấy chitiet_dvc_tructuyen với thanh_phan_ho_so
    print("📥 Đọc chitiet_dvc_tructuyen...")
    chitiet = db.session.execute(text(
        "SELECT TRIM(url_chi_tiet), thanh_phan_ho_so, TRIM(co_quan_thuc_hien) "
        "FROM public.chitiet_dvc_tructuyen "
        "WHERE length(thanh_phan_ho_so) > 10 "
        "AND TRIM(BOTH FROM REPLACE(thanh_phan_ho_so, E'\\uFEFF', '')) != 'thanh_phan_ho_so'"
    )).fetchall()

    # Index chitiet theo ma_thu_tuc
    chitiet_map = {}
    for url, ho_so, co_quan in chitiet:
        ma = extract_ma(url or '')
        if ma and ma not in chitiet_map:
            chitiet_map[ma] = {'ho_so': ho_so or '', 'co_quan': co_quan or ''}
    print(f"   → {len(chitiet_map)} với ma_thu_tuc từ URL")

    # Also index by raw URL for fallback
    chitiet_url_map = {(url or '').strip(): {'ho_so': ho_so or '', 'co_quan': co_quan or ''}
                       for url, ho_so, co_quan in chitiet}

    # 3. Lấy dichvucong_thanhhoa để bổ sung agency
    dch = db.session.execute(text(
        "SELECT TRIM(REPLACE(code, E'\\uFEFF', '')), TRIM(agency_name), TRIM(field) "
        "FROM public.dichvucong_thanhhoa "
        "WHERE TRIM(REPLACE(id, E'\\uFEFF', '')) != 'id'"
    )).fetchall()
    dch_map = {r[0]: {'agency': r[1] or '', 'field': r[2] or ''} for r in dch if r[0]}
    print(f"   → {len(dch_map)} dichvucong entries")

    # 4. Import procedures
    print("\n🔄 Import procedures...")
    ok, skip = 0, 0
    proc_ids = []

    for tthc_ma, name, url in dvc:
        if not tthc_ma or not name:
            continue

        detail = chitiet_map.get(tthc_ma) or chitiet_url_map.get(url, {})
        dch_info = dch_map.get(tthc_ma, {})
        agency = detail.get('co_quan') or dch_info.get('agency', '')
        category = detect_category(name + ' ' + agency)

        try:
            db.session.execute(text("""
                INSERT INTO public.procedures
                    (id, name, code, category, fee, fee_note,
                     processing_days, processing_note, legal_basis,
                     implementing_level, agency, is_online, is_active,
                     created_at, updated_at)
                VALUES
                    (:id, :name, :code, :cat, 0, '',
                     7, '', '[]'::jsonb,
                     '', :agency, true, true,
                     NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name, category = EXCLUDED.category,
                    agency = EXCLUDED.agency, updated_at = NOW()
            """), {'id': tthc_ma, 'name': name, 'code': tthc_ma,
                   'cat': category, 'agency': agency[:500]})
            proc_ids.append(tthc_ma)
            ok += 1
        except Exception as e:
            skip += 1
            if skip <= 3:
                print(f"   ⚠ skip {tthc_ma}: {str(e)[:80]}")

    db.session.commit()
    print(f"   ✅ {ok} inserted/updated, {skip} skipped")

    # 5. Import service_requirements từ chitiet
    print("\n🔄 Parse + import service_requirements...")
    total_docs, procs_with_docs = 0, 0

    for proc_id in proc_ids:
        detail = chitiet_map.get(proc_id, {})
        docs = parse_ho_so(detail.get('ho_so', ''))
        if not docs:
            continue
        procs_with_docs += 1
        for doc in docs:
            req_id = f"{proc_id}-req-{doc['order_index']:03d}"
            try:
                db.session.execute(text("""
                    INSERT INTO public.service_requirements
                        (id, service_id, doc_name, doc_description,
                         is_required, doc_type, order_index)
                    VALUES (:id, :sid, :name, :desc, :req, :dtype, :ord)
                    ON CONFLICT (id) DO UPDATE SET
                        doc_name = EXCLUDED.doc_name,
                        doc_description = EXCLUDED.doc_description,
                        is_required = EXCLUDED.is_required,
                        doc_type = EXCLUDED.doc_type
                """), {
                    'id': req_id, 'sid': proc_id,
                    'name': doc['doc_name'], 'desc': doc['doc_description'],
                    'req': doc['is_required'], 'dtype': doc['doc_type'],
                    'ord': doc['order_index'],
                })
                total_docs += 1
            except Exception:
                pass

    db.session.commit()
    print(f"   ✅ {total_docs} giấy tờ cho {procs_with_docs} thủ tục từ chitiet")

    # 6. Link legacy service_requirements (service_id=NULL)
    print("\n🔗 Link legacy requirements...")
    linked = 0
    for grp, proc_id in LEGACY_MAP.items():
        exists = db.session.execute(text(
            "SELECT 1 FROM public.procedures WHERE id=:id"), {'id': proc_id}
        ).scalar()
        if not exists:
            continue
        r = db.session.execute(text("""
            UPDATE public.service_requirements
            SET service_id = :pid
            WHERE id LIKE :pat AND service_id IS NULL
        """), {'pid': proc_id, 'pat': f'{grp}-%'})
        linked += r.rowcount
    db.session.commit()
    print(f"   ✅ {linked} legacy requirements linked")

    # 7. Seed default requirements cho các procedures quan trọng chưa có
    print("\n🌱 Seed defaults cho procedures chưa có giấy tờ...")
    DEFAULTS = {
        '1.000894': [  # Kết hôn
            ('Tờ khai đăng ký kết hôn (Mẫu TP/HT-2014-TKKH)', 'Hai bên điền đủ và ký tên', True, 'original'),
            ('CCCD / Căn cước công dân (hai bên)', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy xác nhận tình trạng hôn nhân', 'UBND cấp xã cấp trong 6 tháng', True, 'original'),
            ('Giấy khai sinh (hai bên)', 'Bản chính hoặc bản sao chứng thực', True, 'certified_copy'),
            ('Ảnh 4×6 cm (2 ảnh/người)', 'Ảnh chụp trong 6 tháng, nền trắng', True, 'original'),
        ],
        '1.001193': [  # Khai sinh
            ('Giấy chứng sinh', 'Do bệnh viện/cơ sở y tế cấp', True, 'original'),
            ('CCCD / Căn cước bố hoặc mẹ', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy đăng ký kết hôn bố mẹ', 'Bản chính hoặc sao chứng thực', False, 'certified_copy'),
            ('Tờ khai đăng ký khai sinh', 'Điền đầy đủ thông tin', True, 'original'),
        ],
        '2.001642': [  # Cấp CCCD
            ('CCCD cũ / Chứng minh nhân dân', 'Bản gốc hiện có', True, 'original'),
            ('Sổ hộ khẩu hoặc xác nhận cư trú', 'Bản chính', False, 'original'),
            ('Ảnh 4×6 cm (2 ảnh)', 'Ảnh chụp trong 6 tháng, nền trắng', True, 'original'),
        ],
        '1.003018': [  # Đăng ký thường trú
            ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Hợp đồng thuê nhà / Giấy tờ nhà ở hợp lệ', 'Bản gốc hoặc sao công chứng', True, 'certified_copy'),
            ('Đơn đề nghị đăng ký thường trú (Mẫu HK01)', 'Điền đầy đủ và ký tên', True, 'original'),
            ('Giấy tờ chứng minh quan hệ nhân thân', 'Nếu đăng ký cùng chủ hộ', False, 'certified_copy'),
        ],
        '1.003705': [  # Cấp phép xây dựng
            ('CCCD / Căn cước công dân chủ đầu tư', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy tờ về quyền sử dụng đất', 'Sổ đỏ/sổ hồng bản gốc', True, 'original'),
            ('Bản vẽ thiết kế xây dựng', '3 bộ, có chữ ký của đơn vị thiết kế', True, 'original'),
            ('Đơn xin cấp giấy phép xây dựng', 'Mẫu theo quy định', True, 'original'),
            ('Giấy phép môi trường (nếu có)', 'Đối với công trình có tác động môi trường', False, 'original'),
        ],
        '1.003966': [  # Cấp GCN QSD đất
            ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy tờ về nguồn gốc đất', 'Bản gốc các loại giấy tờ hợp lệ', True, 'original'),
            ('Đơn đăng ký cấp GCN QSD đất', 'Mẫu theo quy định', True, 'original'),
            ('Trích đo địa chính thửa đất', 'Do đơn vị đo đạc có chức năng thực hiện', True, 'original'),
            ('Biên lai nộp lệ phí', 'Theo mức thu của địa phương', True, 'original'),
        ],
    }
    seeded = 0
    for proc_id, doc_list in DEFAULTS.items():
        exists_proc = db.session.execute(text(
            "SELECT 1 FROM public.procedures WHERE id=:id"), {'id': proc_id}
        ).scalar()
        if not exists_proc:
            continue
        has_reqs = db.session.execute(text(
            "SELECT COUNT(*) FROM public.service_requirements WHERE service_id=:sid"
        ), {'sid': proc_id}).scalar()
        if has_reqs:
            continue  # Đã có data từ chitiet
        for i, (name, desc, req, dtype) in enumerate(doc_list):
            req_id = f"{proc_id}-req-{i:03d}"
            try:
                db.session.execute(text("""
                    INSERT INTO public.service_requirements
                        (id, service_id, doc_name, doc_description, is_required, doc_type, order_index)
                    VALUES (:id, :sid, :name, :desc, :req, :dtype, :ord)
                    ON CONFLICT (id) DO NOTHING
                """), {'id': req_id, 'sid': proc_id, 'name': name, 'desc': desc,
                       'req': req, 'dtype': dtype, 'ord': i})
                seeded += 1
            except Exception:
                pass
    db.session.commit()
    print(f"   ✅ {seeded} default giấy tờ seeded")

    # Tổng kết
    t_procs = db.session.execute(text("SELECT COUNT(*) FROM public.procedures")).scalar()
    t_reqs  = db.session.execute(text("SELECT COUNT(*) FROM public.service_requirements WHERE service_id IS NOT NULL")).scalar()
    print(f"\n{'='*55}")
    print(f"✅ TỔNG KẾT:")
    print(f"   procedures với dữ liệu thực:   {t_procs}")
    print(f"   service_requirements linked:    {t_reqs}")
    print(f"{'='*55}")
