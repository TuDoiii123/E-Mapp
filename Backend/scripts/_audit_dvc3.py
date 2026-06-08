"""
Khám phá dichvucong_thanhhoa + chitiet_thutuc:
tìm các loại thủ tục phổ biến chưa có trong procedures.
"""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

COMMON_KEYWORDS = [
    # Hộ tịch
    'khai sinh', 'khai tử', 'kết hôn', 'ly hôn', 'nuôi con nuôi',
    'giám hộ', 'thay đổi họ tên', 'cải chính hộ tịch',
    # Cư trú / CCCD
    'thường trú', 'tạm trú', 'tách hộ', 'căn cước', 'định danh',
    # Đất đai
    'quyền sử dụng đất', 'chuyển nhượng', 'tách thửa', 'cấp sổ đỏ',
    'đăng ký biến động', 'thế chấp',
    # Xây dựng
    'giấy phép xây dựng', 'hoàn công', 'quy hoạch',
    # Kinh doanh
    'hộ kinh doanh', 'doanh nghiệp', 'giải thể', 'tạm ngừng kinh doanh',
    # Giao thông
    'giấy phép lái xe', 'đăng kiểm', 'đăng ký xe', 'vận tải',
    # Tư pháp
    'lý lịch tư pháp', 'công chứng', 'chứng thực', 'hộ tịch',
    # Bảo hiểm / lao động
    'bảo hiểm xã hội', 'bảo hiểm y tế', 'lao động', 'việc làm',
    # Y tế
    'giấy phép hành nghề', 'khám sức khỏe', 'cơ sở khám chữa bệnh',
    # Thuế
    'mã số thuế', 'nộp thuế', 'hoàn thuế',
]

with app.app_context():
    # ── 1. dichvucong_thanhhoa: xem top fields và sample ──────────────────
    print("=== dichvucong_thanhhoa: sample 5 rows ===")
    sample = db.session.execute(text(
        "SELECT * FROM public.dichvucong_thanhhoa WHERE id != 'id' LIMIT 5"
    )).fetchall()
    for r in sample:
        d = dict(r._mapping)
        print(f"  code={d.get('code','?')} | name={str(d.get('name',''))[:60]} | field={d.get('field','?')}")

    print("\n=== dichvucong_thanhhoa: top 20 field (linh vuc) ===")
    field_rows = db.session.execute(text("""
        SELECT field, COUNT(*) as cnt
        FROM public.dichvucong_thanhhoa
        WHERE id != 'id' AND field IS NOT NULL AND field != ''
        GROUP BY field ORDER BY cnt DESC LIMIT 20
    """)).fetchall()
    for r in field_rows:
        print(f"  {int(r.cnt):5d}  {r.field[:60]}")

    # ── 2. chitiet_thutuc: phân loại URL theo nhóm thủ tục ────────────────
    print("\n=== chitiet_thutuc: phan loai URL ===")
    ct_rows = db.session.execute(text(
        "SELECT url_chi_tiet FROM public.chitiet_thutuc "
        "WHERE url_chi_tiet != 'URL_Chi_Tiet' AND url_chi_tiet IS NOT NULL "
        "ORDER BY url_chi_tiet"
    )).fetchall()
    urls = [r.url_chi_tiet for r in ct_rows]

    def classify(url):
        u = url.lower()
        if 'can-cuoc' in u or 'cccd' in u: return 'CCCD/Can cuoc'
        if 'ly-lich-tu-phap' in u: return 'Ly lich tu phap'
        if 'dinh-danh' in u: return 'Dinh danh dien tu'
        if 'cu-tru' in u or 'thuong-tru' in u or 'tam-tru' in u: return 'Cu tru'
        if 'con-dau' in u: return 'Con dau'
        if 'xuat-nhap-canh' in u or 'ho-chieu' in u: return 'Xuat nhap canh'
        if 'phuong-tien' in u or 'xe-may' in u or 'oto' in u: return 'Phuong tien GT'
        if 'phong-chay' in u or 'pccc' in u: return 'PCCC'
        if 'vu-khi' in u or 'vat-lieu-no' in u: return 'Vu khi/vat lieu no'
        if 'kinh-doanh' in u: return 'Kinh doanh co dieu kien'
        if 'khieu-nai' in u or 'to-cao' in u: return 'Khieu nai to cao'
        if 'chinh-sach' in u: return 'Chinh sach xa hoi'
        if 'tuyen-sinh' in u or 'hoc-sinh' in u: return 'Giao duc'
        return 'Khac: ' + url.split('/')[4] if len(url.split('/')) > 4 else 'Khac'

    grouped = {}
    for u in urls:
        g = classify(u)
        grouped.setdefault(g, []).append(u)

    existing_cats_in_proc = {'CCCD', 'Cu tru', 'GPLX', 'Dat dai', 'Ly lich', 'Xay dung', 'Kinh doanh'}
    for g, us in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print(f"  [{len(us):3d} rows] {g}")

    # ── 3. Danh sách đề xuất thêm vào procedures ─────────────────────────
    print("\n=== DE XUAT THEM VAO PROCEDURES ===")
    proposals = [
        # Civil / Ho tich
        ('civil',        'dang-ky-lai-khai-sinh',    'Đăng ký lại khai sinh',                       'ward'),
        ('civil',        'dang-ky-nhan-con',          'Nhận cha, mẹ, con',                           'ward'),
        ('civil',        'thay-doi-ho-ten',           'Thay đổi, cải chính hộ tịch / họ tên',        'ward'),
        ('civil',        'cap-trich-luc-ho-tich',     'Cấp bản sao trích lục hộ tịch',               'ward'),
        ('civil',        'xac-nhan-tinh-trang-hon-nhan', 'Xác nhận tình trạng hôn nhân',             'ward'),
        # Cu tru
        ('civil',        'dang-ky-tam-tru',           'Đăng ký tạm trú',                             'ward'),
        ('civil',        'tach-ho-khau',              'Tách hộ khẩu / điều chỉnh thông tin cư trú',  'ward'),
        # CCCD / Dinh danh
        ('civil',        'cap-tai-khoan-dinh-danh',   'Cấp tài khoản định danh điện tử (VNeID)',      'province'),
        # Dat dai
        ('land',         'chuyen-nhuong-quyen-su-dung-dat', 'Đăng ký chuyển nhượng QSDĐ',            'district'),
        ('land',         'tach-thua-dat',             'Tách thửa / Hợp thửa đất',                    'district'),
        ('land',         'dang-ky-bien-dong-dat-dai', 'Đăng ký biến động đất đai',                   'district'),
        # Xay dung
        ('construction', 'hoan-cong-cong-trinh',      'Thông báo hoàn thành công trình xây dựng',    'district'),
        # Kinh doanh
        ('business',     'thay-doi-noi-dung-dkdn',    'Thay đổi nội dung đăng ký doanh nghiệp',      'province'),
        ('business',     'giai-the-doanh-nghiep',     'Đăng ký giải thể doanh nghiệp',               'province'),
        ('business',     'tam-ngung-kinh-doanh',      'Tạm ngừng / tiếp tục kinh doanh',             'province'),
        # Tu phap
        ('justice',      'chung-thuc-ban-sao',        'Chứng thực bản sao từ bản chính',             'ward'),
        ('justice',      'cap-phieu-lltp-so2',        'Cấp phiếu lý lịch tư pháp (số 2)',            'province'),
        # Giao thong
        ('transport',    'doi-cap-lai-gplx',          'Đổi / Cấp lại giấy phép lái xe',              'province'),
        ('transport',    'dang-ky-xe-may',            'Đăng ký xe mô tô / xe máy lần đầu',           'province'),
        # Bao hiem / Lao dong
        ('insurance',    'dang-ky-bhxh-bhyt',         'Đăng ký tham gia BHXH, BHYT lần đầu',         'province'),
        ('insurance',    'cap-so-bhxh',               'Cấp sổ BHXH / thẻ BHYT',                     'province'),
    ]
    by_cat = {}
    for cat, pid, name, level in proposals:
        by_cat.setdefault(cat, []).append((pid, name, level))
    for cat in sorted(by_cat.keys()):
        print(f"\n  [{cat}]")
        for pid, name, level in by_cat[cat]:
            print(f"    + {pid:40s}  [{level}] {name}")
