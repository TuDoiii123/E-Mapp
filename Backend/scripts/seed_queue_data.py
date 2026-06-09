"""
Seed dữ liệu cho các bảng:
  - agency_counters       (quầy tiếp dân mỗi cơ quan)
  - service_stats         (thống kê thời gian xử lý trung bình)
  - agency_queue_realtime (trạng thái hàng chờ ban đầu)
  - form_templates        (mẫu đơn cho thủ tục phổ biến)

Chạy: python scripts/seed_queue_data.py
"""
import sys
import os
import uuid
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(override=True)

# ── Cấu hình số quầy mỗi cơ quan ─────────────────────────────────────────────
# (agency_id, num_counters, operator_names)
AGENCY_COUNTERS = [
    # Cấp tỉnh — nhiều quầy
    ('tthcc-thanhhoa',    8, ['Nguyễn Thị Hoa', 'Trần Văn Minh', 'Lê Thị Mai', 'Phạm Văn Đức',
                               'Hoàng Thị Lan', 'Vũ Văn Hải', 'Đặng Thị Thu', 'Bùi Văn Thắng']),
    ('ubnd-thanhhoa',     5, ['Nguyễn Văn An', 'Trần Thị Bích', 'Lê Văn Cường', 'Phạm Thị Dung', 'Hoàng Văn Em']),
    ('congan-thanhhoa',   6, ['Đại úy Nguyễn Văn Hùng', 'Thiếu úy Trần Thị Lan', 'Thượng sĩ Lê Văn Nam',
                               'Trung sĩ Phạm Thị Oanh', 'Hạ sĩ Vũ Văn Phong', 'Chiến sĩ Đặng Thị Quỳnh']),
    ('so-tu-phap',        5, ['Nguyễn Thị Rồng', 'Trần Văn Sơn', 'Lê Thị Tâm', 'Phạm Văn Uy', 'Hoàng Thị Vân']),
    ('cuc-thue-thanhhoa', 5, ['Nguyễn Văn Xuân', 'Trần Thị Yến', 'Lê Văn Zung', 'Phạm Thị Anh', 'Hoàng Văn Bình']),
    ('bhxh-thanhhoa',     5, ['Nguyễn Thị Cúc', 'Trần Văn Dũng', 'Lê Thị Em', 'Phạm Văn Giang', 'Hoàng Thị Hằng']),
    ('so-tnmt',           4, ['Nguyễn Văn Inh', 'Trần Thị Kim', 'Lê Văn Long', 'Phạm Thị My']),
    ('so-gtvt',           4, ['Nguyễn Thị Nga', 'Trần Văn Ổn', 'Lê Thị Phương', 'Phạm Văn Quý']),
    ('so-khdt',           4, ['Nguyễn Văn Rơi', 'Trần Thị Sương', 'Lê Văn Tuấn', 'Phạm Thị Uyên']),
    ('so-xay-dung',       3, ['Nguyễn Thị Vân', 'Trần Văn Xuân', 'Lê Thị Yến']),
    ('so-y-te',           3, ['Nguyễn Văn Zung', 'Trần Thị Anh', 'Lê Văn Bắc']),
    ('so-gd-dt',          3, ['Nguyễn Thị Cầm', 'Trần Văn Dần', 'Lê Thị Em']),
    ('so-ldtbxh',         3, ['Nguyễn Văn Giao', 'Trần Thị Hòa', 'Lê Văn Inh']),
    # Cấp huyện / thị xã / thành phố
    ('ubnd-tp-thanhhoa',  4, ['Nguyễn Thị Kim', 'Trần Văn Long', 'Lê Thị My', 'Phạm Văn Nga']),
    ('ubnd-bimson',       3, ['Nguyễn Văn Ổn', 'Trần Thị Phương', 'Lê Văn Quý']),
    ('ubnd-samson',       3, ['Nguyễn Thị Rồng', 'Trần Văn Sơn', 'Lê Thị Tâm']),
    ('ubnd-nghison',      3, ['Nguyễn Văn Uy', 'Trần Thị Vân', 'Lê Văn Xuân']),
    ('ubnd-quangxuong',   2, ['Nguyễn Thị Yến', 'Trần Văn Zung']),
    ('ubnd-dongson',      2, ['Nguyễn Văn An', 'Trần Thị Bích']),
    ('ubnd-trieuson',     2, ['Nguyễn Văn Cường', 'Trần Thị Dung']),
    ('ubnd-thoxuan',      2, ['Nguyễn Văn Em', 'Trần Thị Giao']),
    ('ubnd-yendinh',      2, ['Nguyễn Văn Hùng', 'Trần Thị Inh']),
    ('ubnd-vinhloc',      2, ['Nguyễn Văn Kim', 'Trần Thị Lan']),
    ('ubnd-hauloc',       2, ['Nguyễn Văn Minh', 'Trần Thị Nam']),
    ('ubnd-ngason',       2, ['Nguyễn Văn Ổn', 'Trần Thị Phương']),
    ('ubnd-hoanghoa',     2, ['Nguyễn Văn Quý', 'Trần Thị Rồng']),
]

# ── Thống kê thời gian xử lý trung bình (giây) ────────────────────────────────
# Nguồn: ước tính từ quy trình thực tế tại các cơ quan Thanh Hóa
SERVICE_STATS = [
    # (service_id, avg_seconds, sample_count)
    # Hộ tịch
    ('khai_sinh',           420,   150),   # 7 phút
    ('dang_ky_ket_hon',     600,   120),   # 10 phút
    ('khai_tu',             480,   80),    # 8 phút
    ('thay_doi_ho_tich',    540,   60),    # 9 phút
    ('nuoi_con_nuoi',       900,   30),    # 15 phút
    # Căn cước / hộ chiếu
    ('cap_cccd',            300,   300),   # 5 phút — nhanh do scan
    ('cap_ho_chieu',        600,   200),   # 10 phút
    ('dang_ky_cu_tru',      420,   180),   # 7 phút
    # Đất đai
    ('cap_giay_to_dat',     900,   100),   # 15 phút
    ('chuyen_nhuong_dat',   1200,  70),    # 20 phút
    ('the_chap_quyen_sddat',1080,  50),    # 18 phút
    # Tư pháp
    ('chung_thuc',          300,   400),   # 5 phút — đơn giản
    ('cong_chung',          720,   200),   # 12 phút
    ('ly_lich_tu_phap',     480,   90),    # 8 phút
    # Xây dựng
    ('cap_phep_xay_dung',   900,   80),    # 15 phút
    ('cap_phep_cai_tao',    780,   60),    # 13 phút
    # Kinh doanh
    ('dang_ky_ho_kinh_doanh', 720, 90),   # 12 phút
    ('dang_ky_cong_ty_tnhh',  900, 70),   # 15 phút
    ('cap_phep_kinh_doanh', 840,   50),    # 14 phút
    # Giao thông
    ('cap_gplx',            480,   250),   # 8 phút
    ('doi_gplx',            360,   300),   # 6 phút
    ('dang_ky_xe',          540,   200),   # 9 phút
    # BHXH
    ('cap_so_bhxh',         360,   150),   # 6 phút
    ('huong_bhxh_mot_lan',  600,   80),    # 10 phút
    ('cap_the_bhyt',        300,   200),   # 5 phút
    # Thuế
    ('dang_ky_ma_so_thue',  480,   120),   # 8 phút
    ('ke_khai_thue',        900,   100),   # 15 phút
    # Y tế
    ('cap_chung_nhan_sk',   420,   100),   # 7 phút
    ('hanh_nghe_y',         600,   40),    # 10 phút
    # Giáo dục
    ('cong_nhan_bang',      480,   50),    # 8 phút
    ('tiep_nhan_hs',        360,   80),    # 6 phút
    # Generic fallback
    ('general',             420,   500),   # 7 phút mặc định
]

# ── Mẫu đơn thủ tục (form_templates) ─────────────────────────────────────────
FORM_TEMPLATES = [
    {
        'id': 'ft-khai-sinh',
        'name': 'Tờ khai đăng ký khai sinh',
        'description': 'Mẫu tờ khai đăng ký khai sinh theo Thông tư 04/2020/TT-BTP',
        'service_id': 'khai_sinh',
        'filename': 'to_khai_khai_sinh.pdf',
        'original_name': 'Tờ khai đăng ký khai sinh (Mẫu 01/ĐKKhaiSinh).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ho_ten_cha', 'label': 'Họ tên cha', 'type': 'text', 'required': True},
                {'name': 'ho_ten_me', 'label': 'Họ tên mẹ', 'type': 'text', 'required': True},
                {'name': 'ho_ten_con', 'label': 'Họ tên trẻ', 'type': 'text', 'required': True},
                {'name': 'ngay_sinh', 'label': 'Ngày sinh', 'type': 'date', 'required': True},
                {'name': 'gioi_tinh', 'label': 'Giới tính', 'type': 'select', 'options': ['Nam', 'Nữ'], 'required': True},
                {'name': 'noi_sinh', 'label': 'Nơi sinh', 'type': 'text', 'required': True},
                {'name': 'que_quan', 'label': 'Quê quán', 'type': 'text', 'required': True},
                {'name': 'dan_toc', 'label': 'Dân tộc', 'type': 'text', 'required': False, 'default': 'Kinh'},
                {'name': 'quoc_tich', 'label': 'Quốc tịch', 'type': 'text', 'required': False, 'default': 'Việt Nam'},
                {'name': 'noi_thuong_tru', 'label': 'Nơi thường trú', 'type': 'textarea', 'required': True},
                {'name': 'so_cccd_cha', 'label': 'Số CCCD cha', 'type': 'text', 'required': True},
                {'name': 'so_cccd_me', 'label': 'Số CCCD mẹ', 'type': 'text', 'required': True},
            ]
        },
    },
    {
        'id': 'ft-ket-hon',
        'name': 'Tờ khai đăng ký kết hôn',
        'description': 'Mẫu tờ khai đăng ký kết hôn theo Thông tư 04/2020/TT-BTP',
        'service_id': 'dang_ky_ket_hon',
        'filename': 'to_khai_ket_hon.pdf',
        'original_name': 'Tờ khai đăng ký kết hôn (Mẫu 01/ĐKKHôn).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ho_ten_ben_nam', 'label': 'Họ tên bên nam', 'type': 'text', 'required': True},
                {'name': 'ngay_sinh_nam', 'label': 'Ngày sinh (nam)', 'type': 'date', 'required': True},
                {'name': 'so_cccd_nam', 'label': 'Số CCCD bên nam', 'type': 'text', 'required': True},
                {'name': 'noi_cu_tru_nam', 'label': 'Nơi cư trú (nam)', 'type': 'textarea', 'required': True},
                {'name': 'ho_ten_ben_nu', 'label': 'Họ tên bên nữ', 'type': 'text', 'required': True},
                {'name': 'ngay_sinh_nu', 'label': 'Ngày sinh (nữ)', 'type': 'date', 'required': True},
                {'name': 'so_cccd_nu', 'label': 'Số CCCD bên nữ', 'type': 'text', 'required': True},
                {'name': 'noi_cu_tru_nu', 'label': 'Nơi cư trú (nữ)', 'type': 'textarea', 'required': True},
                {'name': 'noi_dang_ky', 'label': 'Nơi đăng ký kết hôn', 'type': 'text', 'required': True},
            ]
        },
    },
    {
        'id': 'ft-cap-cccd',
        'name': 'Tờ khai cấp thẻ CCCD',
        'description': 'Mẫu tờ khai cấp, đổi, cấp lại thẻ căn cước công dân',
        'service_id': 'cap_cccd',
        'filename': 'to_khai_cap_cccd.pdf',
        'original_name': 'Tờ khai cấp thẻ CCCD (CC02).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ho_ten', 'label': 'Họ tên khai sinh', 'type': 'text', 'required': True},
                {'name': 'ten_goi_khac', 'label': 'Tên gọi khác', 'type': 'text', 'required': False},
                {'name': 'ngay_sinh', 'label': 'Ngày sinh', 'type': 'date', 'required': True},
                {'name': 'gioi_tinh', 'label': 'Giới tính', 'type': 'select', 'options': ['Nam', 'Nữ'], 'required': True},
                {'name': 'dan_toc', 'label': 'Dân tộc', 'type': 'text', 'required': True},
                {'name': 'quoc_tich', 'label': 'Quốc tịch', 'type': 'text', 'required': True, 'default': 'Việt Nam'},
                {'name': 'ton_giao', 'label': 'Tôn giáo', 'type': 'text', 'required': False},
                {'name': 'que_quan', 'label': 'Quê quán', 'type': 'text', 'required': True},
                {'name': 'noi_thuong_tru', 'label': 'Nơi thường trú', 'type': 'textarea', 'required': True},
                {'name': 'noi_o_hien_tai', 'label': 'Nơi ở hiện tại', 'type': 'textarea', 'required': False},
                {'name': 'ly_do_cap', 'label': 'Lý do cấp', 'type': 'select',
                 'options': ['Cấp mới', 'Cấp đổi', 'Cấp lại do mất/hỏng'], 'required': True},
                {'name': 'so_cmnd_cu', 'label': 'Số CMND/CCCD cũ (nếu đổi)', 'type': 'text', 'required': False},
            ]
        },
    },
    {
        'id': 'ft-chung-thuc',
        'name': 'Phiếu yêu cầu chứng thực',
        'description': 'Phiếu yêu cầu chứng thực bản sao từ bản gốc / chứng thực chữ ký',
        'service_id': 'chung_thuc',
        'filename': 'phieu_yc_chung_thuc.pdf',
        'original_name': 'Phiếu yêu cầu chứng thực (Nghị định 23/2015/NĐ-CP).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ho_ten_nguoi_yeu_cau', 'label': 'Họ tên người yêu cầu', 'type': 'text', 'required': True},
                {'name': 'so_cccd', 'label': 'Số CCCD/Hộ chiếu', 'type': 'text', 'required': True},
                {'name': 'dia_chi', 'label': 'Địa chỉ', 'type': 'textarea', 'required': True},
                {'name': 'loai_chung_thuc', 'label': 'Loại chứng thực', 'type': 'select',
                 'options': ['Bản sao từ bản gốc', 'Chứng thực chữ ký', 'Chứng thực bản dịch'], 'required': True},
                {'name': 'ten_giay_to', 'label': 'Tên giấy tờ cần chứng thực', 'type': 'text', 'required': True},
                {'name': 'so_ban_sao', 'label': 'Số bản sao yêu cầu', 'type': 'number', 'required': True, 'default': 1},
                {'name': 'muc_dich', 'label': 'Mục đích sử dụng', 'type': 'text', 'required': False},
            ]
        },
    },
    {
        'id': 'ft-cap-phep-xd',
        'name': 'Đơn đề nghị cấp phép xây dựng',
        'description': 'Đơn đề nghị cấp giấy phép xây dựng nhà ở riêng lẻ',
        'service_id': 'cap_phep_xay_dung',
        'filename': 'don_cap_phep_xay_dung.pdf',
        'original_name': 'Đơn đề nghị cấp GPXD (Mẫu 01, NĐ 15/2021/NĐ-CP).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ho_ten_chu_dau_tu', 'label': 'Họ tên chủ đầu tư', 'type': 'text', 'required': True},
                {'name': 'so_cccd', 'label': 'Số CCCD', 'type': 'text', 'required': True},
                {'name': 'dia_chi_chu_dau_tu', 'label': 'Địa chỉ chủ đầu tư', 'type': 'textarea', 'required': True},
                {'name': 'vi_tri_cong_trinh', 'label': 'Vị trí công trình (số nhà, đường, phường/xã)', 'type': 'textarea', 'required': True},
                {'name': 'dien_tich_dat', 'label': 'Diện tích đất (m²)', 'type': 'number', 'required': True},
                {'name': 'dien_tich_xay_dung', 'label': 'Diện tích xây dựng (m²)', 'type': 'number', 'required': True},
                {'name': 'so_tang', 'label': 'Số tầng', 'type': 'number', 'required': True},
                {'name': 'chieu_cao', 'label': 'Chiều cao tổng (m)', 'type': 'number', 'required': True},
                {'name': 'muc_dich_sd', 'label': 'Mục đích sử dụng', 'type': 'select',
                 'options': ['Nhà ở gia đình', 'Nhà ở kết hợp kinh doanh', 'Công trình khác'], 'required': True},
                {'name': 'so_gcnqsdd', 'label': 'Số GCN quyền sử dụng đất', 'type': 'text', 'required': True},
            ]
        },
    },
    {
        'id': 'ft-dang-ky-ho-kinh-doanh',
        'name': 'Giấy đề nghị đăng ký hộ kinh doanh',
        'description': 'Mẫu giấy đề nghị đăng ký hộ kinh doanh (Phụ lục III-1, NĐ 01/2021/NĐ-CP)',
        'service_id': 'dang_ky_ho_kinh_doanh',
        'filename': 'giay_dn_dang_ky_hkd.pdf',
        'original_name': 'Giấy đề nghị đăng ký hộ kinh doanh (Phụ lục III-1).pdf',
        'extracted_structure': {
            'fields': [
                {'name': 'ten_hkd', 'label': 'Tên hộ kinh doanh', 'type': 'text', 'required': True},
                {'name': 'loai_hinh', 'label': 'Loại hình kinh doanh', 'type': 'text', 'required': True},
                {'name': 'dia_chi_tru_so', 'label': 'Địa chỉ trụ sở', 'type': 'textarea', 'required': True},
                {'name': 'dien_thoai', 'label': 'Điện thoại', 'type': 'tel', 'required': True},
                {'name': 'email', 'label': 'Email (nếu có)', 'type': 'email', 'required': False},
                {'name': 'von_kinh_doanh', 'label': 'Vốn kinh doanh (đồng)', 'type': 'number', 'required': True},
                {'name': 'ho_ten_chu_hkd', 'label': 'Họ tên chủ hộ kinh doanh', 'type': 'text', 'required': True},
                {'name': 'so_cccd_chu', 'label': 'Số CCCD chủ hộ', 'type': 'text', 'required': True},
                {'name': 'noi_cap_cccd', 'label': 'Nơi cấp CCCD', 'type': 'text', 'required': True},
                {'name': 'ngay_cap_cccd', 'label': 'Ngày cấp CCCD', 'type': 'date', 'required': True},
                {'name': 'noi_thuong_tru', 'label': 'Nơi thường trú chủ hộ', 'type': 'textarea', 'required': True},
            ]
        },
    },
]


def seed_agency_counters(db_session, text):
    """Seed agency_counters — bỏ qua nếu đã có."""
    from sqlalchemy.exc import IntegrityError

    inserted = 0
    for agency_id, num_counters, operators in AGENCY_COUNTERS:
        for i in range(num_counters):
            counter_no = i + 1
            counter_id = f'ctr-{agency_id}-{counter_no}'
            operator = operators[i] if i < len(operators) else f'Nhân viên {counter_no}'
            try:
                db_session.execute(text('''
                    INSERT INTO public.agency_counters (id, agency_id, counter_no, is_active, operator_name)
                    VALUES (:id, :agency_id, :counter_no, TRUE, :operator)
                    ON CONFLICT (agency_id, counter_no) DO NOTHING
                '''), {
                    'id': counter_id,
                    'agency_id': agency_id,
                    'counter_no': counter_no,
                    'operator': operator,
                })
                inserted += 1
            except Exception:
                db_session.rollback()
    db_session.commit()
    return inserted


# Một vài cơ quan được gán tải mẫu trung bình/đông để bản đồ có cả điểm
# xanh (vắng), vàng (trung bình) và đỏ (đông) thay vì toàn bộ đều xanh.
# (agency_id, total_waiting, total_serving, load_level)
SAMPLE_LOAD_OVERRIDES = {
    'tthcc-thanhhoa':     (18, 6, 'high'),    # đông — đỏ
    'congan-thanhhoa':    (20, 8, 'high'),    # đông — đỏ
    'cuc-thue-thanhhoa':  (9,  4, 'medium'),  # trung bình — vàng
    'so-tu-phap':         (8,  3, 'medium'),  # trung bình — vàng
    'ubnd-tp-thanhhoa':   (7,  3, 'medium'),  # trung bình — vàng
}


def seed_agency_queue_realtime(db_session, text):
    """Seed agency_queue_realtime với tải mẫu — đa số vắng (xanh), một vài
    cơ quan trung bình (vàng) hoặc đông (đỏ) để bản đồ có đủ 3 màu."""
    agency_ids = [row[0] for row in AGENCY_COUNTERS]
    inserted = 0
    for agency_id in agency_ids:
        waiting, serving, level = SAMPLE_LOAD_OVERRIDES.get(agency_id, (0, 0, 'low'))
        try:
            db_session.execute(text('''
                INSERT INTO public.agency_queue_realtime
                    (agency_id, total_waiting, total_serving, load_level, updated_at)
                VALUES (:agency_id, :waiting, :serving, :level, now())
                ON CONFLICT (agency_id) DO UPDATE SET
                    total_waiting = EXCLUDED.total_waiting,
                    total_serving = EXCLUDED.total_serving,
                    load_level    = EXCLUDED.load_level,
                    updated_at    = now()
            '''), {'agency_id': agency_id, 'waiting': waiting, 'serving': serving, 'level': level})
            inserted += 1
        except Exception:
            db_session.rollback()
    db_session.commit()
    return inserted


def seed_service_stats(db_session, text):
    """Seed service_stats với thời gian xử lý trung bình cho các cơ quan chính."""
    # Các cơ quan tỉnh → seed đủ bộ service
    province_agencies = [
        'tthcc-thanhhoa', 'ubnd-thanhhoa', 'congan-thanhhoa',
        'so-tu-phap', 'so-tnmt', 'so-gtvt', 'so-xay-dung',
        'so-khdt', 'cuc-thue-thanhhoa', 'bhxh-thanhhoa', 'so-y-te', 'so-gd-dt', 'so-ldtbxh',
    ]
    # Các cơ quan huyện → chỉ seed dịch vụ phổ biến
    district_services = ['khai_sinh', 'dang_ky_ket_hon', 'khai_tu', 'cap_cccd',
                         'dang_ky_cu_tru', 'chung_thuc', 'cap_phep_xay_dung', 'general']
    district_agencies = [a for a, _, _ in AGENCY_COUNTERS if a not in province_agencies]

    inserted = 0
    for agency_id in province_agencies:
        for service_id, avg_sec, sample_count in SERVICE_STATS:
            try:
                db_session.execute(text('''
                    INSERT INTO public.service_stats
                        (agency_id, service_id, sample_count, total_seconds, avg_seconds, updated_at)
                    VALUES (:agency_id, :service_id, :sample_count, :total_sec, :avg_sec, now())
                    ON CONFLICT (agency_id, service_id) DO NOTHING
                '''), {
                    'agency_id': agency_id,
                    'service_id': service_id,
                    'sample_count': sample_count,
                    'total_sec': avg_sec * sample_count,
                    'avg_sec': avg_sec,
                })
                inserted += 1
            except Exception:
                db_session.rollback()

    for agency_id in district_agencies:
        for service_id, avg_sec, sample_count in SERVICE_STATS:
            if service_id not in district_services:
                continue
            try:
                db_session.execute(text('''
                    INSERT INTO public.service_stats
                        (agency_id, service_id, sample_count, total_seconds, avg_seconds, updated_at)
                    VALUES (:agency_id, :service_id, :sample_count, :total_sec, :avg_sec, now())
                    ON CONFLICT (agency_id, service_id) DO NOTHING
                '''), {
                    'agency_id': agency_id,
                    'service_id': service_id,
                    'sample_count': max(sample_count // 3, 10),
                    'total_sec': avg_sec * max(sample_count // 3, 10),
                    'avg_sec': avg_sec,
                })
                inserted += 1
            except Exception:
                db_session.rollback()

    db_session.commit()
    return inserted


def seed_form_templates(db_session, text):
    """Seed form_templates — mẫu đơn cho thủ tục phổ biến."""
    inserted = 0
    for tpl in FORM_TEMPLATES:
        try:
            db_session.execute(text('''
                INSERT INTO public.form_templates
                    (id, name, description, service_id, filename, original_name, extracted_structure)
                VALUES (:id, :name, :desc, :service_id, :filename, :orig_name, :structure::jsonb)
                ON CONFLICT (id) DO NOTHING
            '''), {
                'id': tpl['id'],
                'name': tpl['name'],
                'desc': tpl['description'],
                'service_id': tpl['service_id'],
                'filename': tpl['filename'],
                'orig_name': tpl['original_name'],
                'structure': json.dumps(tpl['extracted_structure'], ensure_ascii=False),
            })
            inserted += 1
        except Exception as e:
            db_session.rollback()
            print(f'  ! form_template {tpl["id"]} failed: {e}')
    db_session.commit()
    return inserted


def seed_all():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from flask import Flask
    from models.db import init_db, db
    from sqlalchemy import text

    app = Flask(__name__)
    init_db(app)

    with app.app_context():
        print('── agency_counters ──────────────────')
        n = seed_agency_counters(db.session, text)
        print(f'  + {n} counter rows inserted (ON CONFLICT DO NOTHING)')

        print('── agency_queue_realtime ────────────')
        n = seed_agency_queue_realtime(db.session, text)
        print(f'  + {n} realtime rows inserted')

        print('── service_stats ────────────────────')
        n = seed_service_stats(db.session, text)
        print(f'  + {n} stat rows inserted')

        print('── form_templates ───────────────────')
        n = seed_form_templates(db.session, text)
        print(f'  + {n} form templates inserted')

        print('\nDone.')


if __name__ == '__main__':
    seed_all()
