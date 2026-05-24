"""
Seed dữ liệu cơ quan hành chính tỉnh Thanh Hóa.

Chạy: cd Backend && python scripts/seed_thanhhoa_agencies.py

Ghi vào:
  - data/public_services.json   (fallback JSON)
  - PostgreSQL: ds_theloai, ds_dichvucong, agencies  (nếu kết nối được)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
JSON_OUT = DATA_DIR / 'public_services.json'

# ── Giờ làm việc mặc định ─────────────────────────────────────────────────────
WH = {
    'monday': '7:30-17:00', 'tuesday': '7:30-17:00',
    'wednesday': '7:30-17:00', 'thursday': '7:30-17:00',
    'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Closed',
}

# ── Danh mục ──────────────────────────────────────────────────────────────────
CATEGORIES = [
    {'id': 'ubnd',      'name': 'UBND / Hành chính công', 'code': 'ubnd'},
    {'id': 'police',    'name': 'Công an',                 'code': 'police'},
    {'id': 'health',    'name': 'Y tế',                    'code': 'health'},
    {'id': 'so-nganh',  'name': 'Sở / Ban / Ngành',        'code': 'so-nganh'},
    {'id': 'trung-tam', 'name': 'Trung tâm dịch vụ công',  'code': 'trung-tam'},
    {'id': 'tax',       'name': 'Thuế / Kho bạc',          'code': 'tax'},
    {'id': 'bhxh',      'name': 'Bảo hiểm xã hội',         'code': 'bhxh'},
]

# ── Dữ liệu cơ quan ──────────────────────────────────────────────────────────
# (id, name, categoryId, address, lat, lng, phone, level, services, district)
AGENCIES_RAW = [
    # ══ CẤP TỈNH ══════════════════════════════════════════════════════════════
    ('th-ubnd-tinh',   'UBND Tỉnh Thanh Hóa',
     'ubnd',  '28 Đại lộ Lê Lợi, P. Điện Biên, TP. Thanh Hóa',
     19.8067, 105.7783, '0237.3852.005', 'province',
     ['Hành chính tổng hợp', 'Tiếp công dân', 'Giải quyết khiếu nại tố cáo'],
     'TP. Thanh Hóa'),

    ('th-congantnh',   'Công an Tỉnh Thanh Hóa',
     'police', '2 Hải Thượng Lãn Ông, P. Tân Sơn, TP. Thanh Hóa',
     19.8079, 105.7766, '0237.3852.190', 'province',
     ['CCCD', 'Đăng ký xe', 'Xuất nhập cảnh', 'Phòng cháy chữa cháy'],
     'TP. Thanh Hóa'),

    ('th-sotuphanh',   'Sở Tư pháp Thanh Hóa',
     'so-nganh', '34 Đại lộ Lê Lợi, TP. Thanh Hóa',
     19.8057, 105.7791, '0237.3852.336', 'province',
     ['Hộ tịch', 'Công chứng', 'Chứng thực', 'Trợ giúp pháp lý'],
     'TP. Thanh Hóa'),

    ('th-sotnmt',      'Sở Tài nguyên & Môi trường Thanh Hóa',
     'so-nganh', '56 Đại lộ Lê Lợi, TP. Thanh Hóa',
     19.8051, 105.7801, '0237.3851.717', 'province',
     ['Đất đai', 'Giấy CNQSDĐ', 'Môi trường', 'Khoáng sản'],
     'TP. Thanh Hóa'),

    ('th-sokhdt',      'Sở Kế hoạch & Đầu tư Thanh Hóa',
     'so-nganh', '16 Đại lộ Lê Lợi, TP. Thanh Hóa',
     19.8070, 105.7792, '0237.3852.251', 'province',
     ['Đăng ký doanh nghiệp', 'Đầu tư', 'Đấu thầu'],
     'TP. Thanh Hóa'),

    ('th-soxaydung',   'Sở Xây dựng Thanh Hóa',
     'so-nganh', '35 Quang Trung, TP. Thanh Hóa',
     19.8075, 105.7788, '0237.3851.436', 'province',
     ['Cấp phép xây dựng', 'Quy hoạch', 'Nhà ở'],
     'TP. Thanh Hóa'),

    ('th-sogtvt',      'Sở Giao thông Vận tải Thanh Hóa',
     'so-nganh', '38 Quang Trung, TP. Thanh Hóa',
     19.8060, 105.7785, '0237.3852.064', 'province',
     ['Đăng kiểm xe', 'Giấy phép lái xe', 'Vận tải'],
     'TP. Thanh Hóa'),

    ('th-soyte',       'Sở Y tế Thanh Hóa',
     'so-nganh', '103 Quang Trung, TP. Thanh Hóa',
     19.8069, 105.7796, '0237.3852.578', 'province',
     ['Cấp phép hành nghề y', 'An toàn thực phẩm', 'Dược'],
     'TP. Thanh Hóa'),

    ('th-soldtbxh',    'Sở Lao động TB&XH Thanh Hóa',
     'so-nganh', '20 Hải Thượng Lãn Ông, TP. Thanh Hóa',
     19.8063, 105.7770, '0237.3852.213', 'province',
     ['Bảo hiểm thất nghiệp', 'Việc làm', 'Trẻ em', 'Người có công'],
     'TP. Thanh Hóa'),

    ('th-sogddt',      'Sở Giáo dục & Đào tạo Thanh Hóa',
     'so-nganh', '01 Đại lộ Lê Lợi, TP. Thanh Hóa',
     19.8071, 105.7780, '0237.3852.375', 'province',
     ['Bằng cấp', 'Chứng chỉ', 'Phổ cập giáo dục'],
     'TP. Thanh Hóa'),

    ('th-sotttt',      'Sở Thông tin & Truyền thông Thanh Hóa',
     'so-nganh', '24 Đào Duy Từ, TP. Thanh Hóa',
     19.8076, 105.7785, '0237.3851.666', 'province',
     ['Báo chí', 'Viễn thông', 'An toàn thông tin'],
     'TP. Thanh Hóa'),

    ('th-sotaichinh',  'Sở Tài chính Thanh Hóa',
     'so-nganh', '30 Đào Duy Từ, TP. Thanh Hóa',
     19.8054, 105.7787, '0237.3852.147', 'province',
     ['Ngân sách', 'Đầu tư công', 'Tài sản công'],
     'TP. Thanh Hóa'),

    ('th-cuethuetnh',  'Cục Thuế Tỉnh Thanh Hóa',
     'tax', '4 Hải Thượng Lãn Ông, TP. Thanh Hóa',
     19.8047, 105.7803, '0237.3853.268', 'province',
     ['Kê khai thuế', 'Hoàn thuế', 'Đăng ký thuế', 'Mã số thuế'],
     'TP. Thanh Hóa'),

    ('th-bhxhtinh',    'BHXH Tỉnh Thanh Hóa',
     'bhxh', '6 Trần Phú, TP. Thanh Hóa',
     19.8041, 105.7809, '0237.3852.408', 'province',
     ['BHXH bắt buộc', 'BHYT', 'BHTN', 'Sổ BHXH'],
     'TP. Thanh Hóa'),

    ('th-khobac-tinh', 'Kho bạc Nhà nước Tỉnh Thanh Hóa',
     'tax', '8 Trần Phú, TP. Thanh Hóa',
     19.8035, 105.7815, '0237.3852.553', 'province',
     ['Kiểm soát chi', 'Thanh toán ngân sách', 'Vay vốn'],
     'TP. Thanh Hóa'),

    ('th-tthcc-tinh',  'Trung tâm Phục vụ HC Công Tỉnh Thanh Hóa',
     'trung-tam', '22 Đại lộ Lê Lợi, TP. Thanh Hóa',
     19.8063, 105.7785, '0237.3727.333', 'province',
     ['Một cửa liên thông', 'Tiếp nhận hồ sơ', 'Trả kết quả'],
     'TP. Thanh Hóa'),

    # ══ TP. THANH HÓA ═════════════════════════════════════════════════════════
    ('th-ubnd-tpth',   'UBND TP. Thanh Hóa',
     'ubnd', '28 Trần Phú, TP. Thanh Hóa',
     19.8046, 105.7788, '0237.3852.158', 'city',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'TP. Thanh Hóa'),

    ('th-congan-tpth', 'Công an TP. Thanh Hóa',
     'police', '18 Lý Nam Đế, TP. Thanh Hóa',
     19.8079, 105.7759, '0237.3851.113', 'city',
     ['CCCD', 'Đăng ký tạm trú', 'Cảnh sát giao thông'],
     'TP. Thanh Hóa'),

    ('th-tthcc-tpth',  'Trung tâm Dịch vụ Công TP. Thanh Hóa',
     'trung-tam', '15 Trần Phú, TP. Thanh Hóa',
     19.8055, 105.7793, '0237.3727.100', 'city',
     ['Một cửa', 'Tiếp nhận hồ sơ', 'Giải quyết TTHC'],
     'TP. Thanh Hóa'),

    # Phường TP. Thanh Hóa
    ('th-pw-dienbien',   'UBND Phường Điện Biên',
     'ubnd', 'Phường Điện Biên, TP. Thanh Hóa',
     19.8046, 105.7792, '0237.3852.xxx', 'ward',
     ['Hộ tịch', 'Chứng thực', 'Đất đai'], 'TP. Thanh Hóa'),

    ('th-pw-lamson',     'UBND Phường Lam Sơn',
     'ubnd', 'Phường Lam Sơn, TP. Thanh Hóa',
     19.8062, 105.7797, '0237.3851.xxx', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-baDinh',     'UBND Phường Ba Đình',
     'ubnd', 'Phường Ba Đình, TP. Thanh Hóa',
     19.8105, 105.7783, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-phuSon',     'UBND Phường Phú Sơn',
     'ubnd', 'Phường Phú Sơn, TP. Thanh Hóa',
     19.8030, 105.7869, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-namNgan',    'UBND Phường Nam Ngạn',
     'ubnd', 'Phường Nam Ngạn, TP. Thanh Hóa',
     19.7969, 105.7803, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-truongThi',  'UBND Phường Trường Thi',
     'ubnd', 'Phường Trường Thi, TP. Thanh Hóa',
     19.8135, 105.7759, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-hamRong',    'UBND Phường Hàm Rồng',
     'ubnd', 'Phường Hàm Rồng, TP. Thanh Hóa',
     19.8286, 105.7718, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-dongTho',    'UBND Phường Đông Thọ',
     'ubnd', 'Phường Đông Thọ, TP. Thanh Hóa',
     19.8048, 105.7853, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-dongVe',     'UBND Phường Đông Vệ',
     'ubnd', 'Phường Đông Vệ, TP. Thanh Hóa',
     19.8002, 105.7877, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-dongHai',    'UBND Phường Đông Hải',
     'ubnd', 'Phường Đông Hải, TP. Thanh Hóa',
     19.7922, 105.7977, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-taoCuyen',   'UBND Phường Tào Xuyên',
     'ubnd', 'Phường Tào Xuyên, TP. Thanh Hóa',
     19.8386, 105.7893, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-dongCuong',  'UBND Phường Đông Cương',
     'ubnd', 'Phường Đông Cương, TP. Thanh Hóa',
     19.8167, 105.7893, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-ngocTrao',   'UBND Phường Ngọc Trạo',
     'ubnd', 'Phường Ngọc Trạo, TP. Thanh Hóa',
     19.8020, 105.7742, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-anHung',     'UBND Phường An Hưng',
     'ubnd', 'Phường An Hưng, TP. Thanh Hóa',
     19.8173, 105.7696, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-quangHung',  'UBND Phường Quảng Hưng',
     'ubnd', 'Phường Quảng Hưng, TP. Thanh Hóa',
     19.7872, 105.7693, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-quangThang', 'UBND Phường Quảng Thắng',
     'ubnd', 'Phường Quảng Thắng, TP. Thanh Hóa',
     19.7774, 105.7755, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-quangTam',   'UBND Phường Quảng Tâm',
     'ubnd', 'Phường Quảng Tâm, TP. Thanh Hóa',
     19.7703, 105.7817, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-pw-thieuDuong', 'UBND Phường Thiệu Dương',
     'ubnd', 'Phường Thiệu Dương, TP. Thanh Hóa',
     19.8179, 105.8007, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-xa-dongTan',    'UBND Xã Đông Tân',
     'ubnd', 'Xã Đông Tân, TP. Thanh Hóa',
     19.7892, 105.8013, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-xa-dongLinh',   'UBND Xã Đông Lĩnh',
     'ubnd', 'Xã Đông Lĩnh, TP. Thanh Hóa',
     19.7808, 105.8107, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    ('th-xa-thieuKhanh', 'UBND Xã Thiệu Khánh',
     'ubnd', 'Xã Thiệu Khánh, TP. Thanh Hóa',
     19.7904, 105.7715, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TP. Thanh Hóa'),

    # ══ Y TẾ TP. THANH HÓA ═══════════════════════════════════════════════════
    ('th-bv-dakhoa',    'Bệnh viện Đa khoa Tỉnh Thanh Hóa',
     'health', '96 Hải Thượng Lãn Ông, TP. Thanh Hóa',
     19.8079, 105.7831, '0237.3855.333', 'province',
     ['Khám ngoại trú', 'Nội trú', 'Cấp cứu', 'Xét nghiệm'],
     'TP. Thanh Hóa'),

    ('th-bv-nhi',       'Bệnh viện Nhi Thanh Hóa',
     'health', '18 Lê Thánh Tông, TP. Thanh Hóa',
     19.8069, 105.7851, '0237.3852.399', 'province',
     ['Khám nhi', 'Nhi nội', 'Nhi ngoại', 'Sơ sinh'],
     'TP. Thanh Hóa'),

    ('th-bv-phuson',    'Bệnh viện Phụ sản Thanh Hóa',
     'health', '33 Nguyễn Trãi, TP. Thanh Hóa',
     19.8055, 105.7842, '0237.3852.157', 'province',
     ['Sản khoa', 'Phụ khoa', 'Kế hoạch hóa gia đình'],
     'TP. Thanh Hóa'),

    ('th-bv-ungbuou',   'Bệnh viện Ung bướu Thanh Hóa',
     'health', '15 Hải Thượng Lãn Ông, TP. Thanh Hóa',
     19.8091, 105.7723, '0237.3852.490', 'province',
     ['Điều trị ung thư', 'Hóa trị', 'Xạ trị'],
     'TP. Thanh Hóa'),

    ('th-bv-phcn',      'Bệnh viện Phục hồi Chức năng Thanh Hóa',
     'health', '85 Trần Phú, TP. Thanh Hóa',
     19.8043, 105.7854, '0237.3855.177', 'province',
     ['Phục hồi chức năng', 'Vật lý trị liệu'],
     'TP. Thanh Hóa'),

    ('th-ttyte-tpth',   'Trung tâm Y tế TP. Thanh Hóa',
     'health', '21 Trần Phú, TP. Thanh Hóa',
     19.8059, 105.7868, '0237.3852.112', 'city',
     ['Khám chữa bệnh', 'Y tế dự phòng', 'Tiêm chủng'],
     'TP. Thanh Hóa'),

    ('th-bv-71tw',      'Bệnh viện 71 TW (Lao & Phổi)',
     'health', 'Đường Nguyễn Trãi kéo dài, TP. Thanh Hóa',
     19.8231, 105.7897, '0237.3855.050', 'province',
     ['Điều trị lao', 'Bệnh phổi'],
     'TP. Thanh Hóa'),

    # ══ TX. BỈM SƠN ════════════════════════════════════════════════════════════
    ('th-ubnd-bimson',  'UBND TX. Bỉm Sơn',
     'ubnd', 'Phường Ba Đình, TX. Bỉm Sơn',
     20.0896, 105.8614, '0237.3671.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng'], 'TX. Bỉm Sơn'),

    ('th-congan-bimson','Công an TX. Bỉm Sơn',
     'police', 'Phường Lam Sơn, TX. Bỉm Sơn',
     20.0883, 105.8602, '0237.3671.113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú tạm vắng'], 'TX. Bỉm Sơn'),

    ('th-ttyte-bimson', 'Trung tâm Y tế TX. Bỉm Sơn',
     'health', 'Phường Đông Sơn, TX. Bỉm Sơn',
     20.0870, 105.8589, '0237.3671.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'TX. Bỉm Sơn'),

    ('th-tthcc-bimson', 'Trung tâm Dịch vụ Công TX. Bỉm Sơn',
     'trung-tam', 'Phường Ba Đình, TX. Bỉm Sơn',
     20.0901, 105.8625, '0237.3671.200', 'district',
     ['Một cửa', 'Tiếp nhận hồ sơ'], 'TX. Bỉm Sơn'),

    ('th-pw-bsbadinh',  'UBND Phường Ba Đình (Bỉm Sơn)',
     'ubnd', 'Phường Ba Đình, TX. Bỉm Sơn',
     20.0877, 105.8574, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TX. Bỉm Sơn'),

    ('th-pw-bslamson',  'UBND Phường Lam Sơn (Bỉm Sơn)',
     'ubnd', 'Phường Lam Sơn, TX. Bỉm Sơn',
     20.0850, 105.8597, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TX. Bỉm Sơn'),

    ('th-pw-bsngoctrao','UBND Phường Ngọc Trạo (Bỉm Sơn)',
     'ubnd', 'Phường Ngọc Trạo, TX. Bỉm Sơn',
     20.0823, 105.8620, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TX. Bỉm Sơn'),

    ('th-pw-bsdongson', 'UBND Phường Đông Sơn (Bỉm Sơn)',
     'ubnd', 'Phường Đông Sơn, TX. Bỉm Sơn',
     20.0940, 105.8603, '', 'ward',
     ['Hộ tịch', 'Chứng thực'], 'TX. Bỉm Sơn'),

    # ══ TX. SẦM SƠN ═══════════════════════════════════════════════════════════
    ('th-ubnd-samson',  'UBND TX. Sầm Sơn',
     'ubnd', 'Đường Lê Lợi, TX. Sầm Sơn',
     19.7434, 105.9027, '0237.3822.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Du lịch'], 'TX. Sầm Sơn'),

    ('th-congan-samson','Công an TX. Sầm Sơn',
     'police', 'TX. Sầm Sơn',
     19.7420, 105.9015, '0237.3822.113', 'district',
     ['CCCD', 'Đăng ký xe', 'An ninh trật tự'], 'TX. Sầm Sơn'),

    ('th-ttyte-samson', 'Trung tâm Y tế TX. Sầm Sơn',
     'health', 'TX. Sầm Sơn',
     19.7456, 105.9052, '0237.3822.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'TX. Sầm Sơn'),

    # ══ CÁC HUYỆN ═════════════════════════════════════════════════════════════
    ('th-ubnd-hoangHoa',   'UBND Huyện Hoằng Hóa',
     'ubnd', 'TT. Bút Sơn, H. Hoằng Hóa',
     19.8453, 105.8833, '0237.3866.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng'], 'H. Hoằng Hóa'),

    ('th-ubnd-dongSon',    'UBND Huyện Đông Sơn',
     'ubnd', 'TT. Rừng Thông, H. Đông Sơn',
     19.8002, 105.6724, '0237.3851.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Đông Sơn'),

    ('th-ubnd-thieuHoa',   'UBND Huyện Thiệu Hóa',
     'ubnd', 'TT. Thiệu Hóa, H. Thiệu Hóa',
     19.8851, 105.7023, '0237.3865.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Thiệu Hóa'),

    ('th-ubnd-yenDinh',    'UBND Huyện Yên Định',
     'ubnd', 'TT. Quán Lào, H. Yên Định',
     20.0596, 105.5787, '0237.3860.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Yên Định'),

    ('th-ubnd-thoXuan',    'UBND Huyện Thọ Xuân',
     'ubnd', 'TT. Thọ Xuân, H. Thọ Xuân',
     19.8167, 105.5333, '0237.3863.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Khu công nghiệp'], 'H. Thọ Xuân'),

    ('th-ubnd-trieuSon',   'UBND Huyện Triệu Sơn',
     'ubnd', 'TT. Triệu Sơn, H. Triệu Sơn',
     19.9175, 105.6928, '0237.3862.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Triệu Sơn'),

    ('th-ubnd-hauLoc',     'UBND Huyện Hậu Lộc',
     'ubnd', 'TT. Hậu Lộc, H. Hậu Lộc',
     19.9483, 105.9413, '0237.3867.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Thủy sản'], 'H. Hậu Lộc'),

    ('th-ubnd-haTrung',    'UBND Huyện Hà Trung',
     'ubnd', 'TT. Hà Trung, H. Hà Trung',
     20.0673, 105.8123, '0237.3869.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Hà Trung'),

    ('th-ubnd-ngaSon',     'UBND Huyện Nga Sơn',
     'ubnd', 'TT. Nga Sơn, H. Nga Sơn',
     20.0013, 106.0167, '0237.3870.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Cói thủ công nghiệp'], 'H. Nga Sơn'),

    ('th-ubnd-quangXuong', 'UBND Huyện Quảng Xương',
     'ubnd', 'TT. Quảng Xương, H. Quảng Xương',
     19.6833, 105.7667, '0237.3875.001', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Quảng Xương'),

    ('th-ubnd-nghiSon',    'UBND H. Tĩnh Gia (Nghi Sơn)',
     'ubnd', 'TT. Tĩnh Gia, H. Tĩnh Gia',
     19.3500, 105.8167, '0237.3876.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Khu kinh tế Nghi Sơn'], 'H. Tĩnh Gia'),

    ('th-ubnd-nongCong',   'UBND Huyện Nông Cống',
     'ubnd', 'TT. Nông Cống, H. Nông Cống',
     19.6667, 105.6667, '0237.3876.002', 'district',
     ['Hộ tịch', 'Đất đai'], 'H. Nông Cống'),

    ('th-ubnd-nhuXuan',    'UBND Huyện Như Xuân',
     'ubnd', 'TT. Yên Cát, H. Như Xuân',
     19.6167, 105.4000, '0237.3877.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp'], 'H. Như Xuân'),

    ('th-ubnd-nhuThanh',   'UBND Huyện Như Thanh',
     'ubnd', 'TT. Bến Sung, H. Như Thanh',
     19.7167, 105.5167, '0237.3877.002', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp'], 'H. Như Thanh'),

    ('th-ubnd-thuongXuan', 'UBND Huyện Thường Xuân',
     'ubnd', 'TT. Thường Xuân, H. Thường Xuân',
     19.7217, 105.3276, '0237.3878.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Dân tộc thiểu số'], 'H. Thường Xuân'),

    ('th-ubnd-vinhLoc',    'UBND Huyện Vĩnh Lộc',
     'ubnd', 'TT. Vĩnh Lộc, H. Vĩnh Lộc',
     20.1722, 105.4993, '0237.3879.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Di sản Thành Nhà Hồ'], 'H. Vĩnh Lộc'),

    ('th-ubnd-camThuy',    'UBND Huyện Cẩm Thủy',
     'ubnd', 'TT. Cẩm Thủy, H. Cẩm Thủy',
     20.2667, 105.4333, '0237.3880.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp'], 'H. Cẩm Thủy'),

    ('th-ubnd-thachThanh', 'UBND Huyện Thạch Thành',
     'ubnd', 'TT. Kim Tân, H. Thạch Thành',
     20.3478, 105.5823, '0237.3881.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Công nghiệp'], 'H. Thạch Thành'),

    ('th-ubnd-ngocLac',    'UBND Huyện Ngọc Lặc',
     'ubnd', 'TT. Ngọc Lặc, H. Ngọc Lặc',
     20.0983, 105.3835, '0237.3882.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Dân tộc thiểu số'], 'H. Ngọc Lặc'),

    ('th-ubnd-langChanh',  'UBND Huyện Lang Chánh',
     'ubnd', 'TT. Lang Chánh, H. Lang Chánh',
     20.1526, 105.2493, '0237.3883.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Dân tộc thiểu số'], 'H. Lang Chánh'),

    ('th-ubnd-quanSon',    'UBND Huyện Quan Sơn',
     'ubnd', 'TT. Quan Sơn, H. Quan Sơn',
     20.5167, 104.9500, '0237.3884.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Biên giới', 'Dân tộc thiểu số'], 'H. Quan Sơn'),

    ('th-ubnd-quanHoa',    'UBND Huyện Quan Hóa',
     'ubnd', 'TT. Quan Hóa, H. Quan Hóa',
     20.7686, 105.0293, '0237.3885.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Dân tộc thiểu số'], 'H. Quan Hóa'),

    ('th-ubnd-muongLat',   'UBND Huyện Mường Lát',
     'ubnd', 'TT. Mường Lát, H. Mường Lát',
     20.9167, 104.0333, '0237.3886.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Biên giới', 'Dân tộc thiểu số'], 'H. Mường Lát'),

    ('th-ubnd-baThuoc',    'UBND Huyện Bá Thước',
     'ubnd', 'TT. Cành Nàng, H. Bá Thước',
     20.3389, 105.1833, '0237.3887.001', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Dân tộc thiểu số'], 'H. Bá Thước'),

    # ══ CÔNG AN HUYỆN ═════════════════════════════════════════════════════════
    ('th-ca-hoangHoa',  'Công an H. Hoằng Hóa',
     'police', 'TT. Bút Sơn, H. Hoằng Hóa',
     19.8453, 105.8847, '0237.3866.113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú tạm vắng'], 'H. Hoằng Hóa'),

    ('th-ca-dongSon',   'Công an H. Đông Sơn',
     'police', 'TT. Rừng Thông, H. Đông Sơn',
     19.8012, 105.6712, '0237.3851.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Đông Sơn'),

    ('th-ca-thieuHoa',  'Công an H. Thiệu Hóa',
     'police', 'TT. Thiệu Hóa, H. Thiệu Hóa',
     19.8841, 105.7011, '0237.3865.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Thiệu Hóa'),

    ('th-ca-thoXuan',   'Công an H. Thọ Xuân',
     'police', 'TT. Thọ Xuân, H. Thọ Xuân',
     19.8177, 105.5321, '0237.3863.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Thọ Xuân'),

    ('th-ca-trieuSon',  'Công an H. Triệu Sơn',
     'police', 'TT. Triệu Sơn, H. Triệu Sơn',
     19.9185, 105.6918, '0237.3862.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Triệu Sơn'),

    ('th-ca-hauLoc',    'Công an H. Hậu Lộc',
     'police', 'TT. Hậu Lộc, H. Hậu Lộc',
     19.9493, 105.9403, '0237.3867.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Hậu Lộc'),

    ('th-ca-quangXuong','Công an H. Quảng Xương',
     'police', 'TT. Quảng Xương, H. Quảng Xương',
     19.6843, 105.7657, '0237.3875.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Quảng Xương'),

    ('th-ca-nongCong',  'Công an H. Nông Cống',
     'police', 'TT. Nông Cống, H. Nông Cống',
     19.6677, 105.6657, '0237.3876.113', 'district',
     ['CCCD', 'Đăng ký xe'], 'H. Nông Cống'),

    # ══ TRUNG TÂM Y TẾ HUYỆN ═══════════════════════════════════════════════
    ('th-ttyte-hoangHoa',   'TT Y tế H. Hoằng Hóa',
     'health', 'TT. Bút Sơn, H. Hoằng Hóa',
     19.8463, 105.8820, '0237.3866.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng', 'Y tế dự phòng'], 'H. Hoằng Hóa'),

    ('th-ttyte-dongSon',    'TT Y tế H. Đông Sơn',
     'health', 'TT. Rừng Thông, H. Đông Sơn',
     19.7995, 105.6740, '0237.3851.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Đông Sơn'),

    ('th-ttyte-thoXuan',    'TT Y tế H. Thọ Xuân',
     'health', 'TT. Thọ Xuân, H. Thọ Xuân',
     19.8180, 105.5320, '0237.3863.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Thọ Xuân'),

    ('th-ttyte-nghiSon',    'BV Đa khoa Nghi Sơn',
     'health', 'TT. Tĩnh Gia, H. Tĩnh Gia',
     19.3510, 105.8155, '0237.3876.115', 'district',
     ['Khám chữa bệnh', 'Cấp cứu', 'Tiêm chủng'], 'H. Tĩnh Gia'),

    ('th-ttyte-hauLoc',     'TT Y tế H. Hậu Lộc',
     'health', 'TT. Hậu Lộc, H. Hậu Lộc',
     19.9490, 105.9420, '0237.3867.115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Hậu Lộc'),
]


def build_service_record(row: tuple) -> dict:
    (sid, name, cat_id, address, lat, lng,
     phone, level, services, district) = row
    return {
        'id':          sid,
        'name':        name,
        'description': name,
        'categoryId':  cat_id,
        'locationId':  None,
        'address':     address,
        'latitude':    lat,
        'longitude':   lng,
        'phone':       phone,
        'email':       '',
        'website':     '',
        'workingHours': WH.copy(),
        'services':    services,
        'level':       level,
        'rating':      0,
        'status':      'normal',
        'distance':    None,
        'province':    'Thanh Hóa',
        'district':    district,
        'ward':        '',
        'createdAt':   datetime.now().isoformat(),
        'updatedAt':   datetime.now().isoformat(),
    }


def seed_json():
    records = [build_service_record(r) for r in AGENCIES_RAW]
    DATA_DIR.mkdir(exist_ok=True)
    JSON_OUT.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'[JSON] Đã ghi {len(records)} cơ quan → {JSON_OUT}')


def seed_postgres():
    sys.path.insert(0, str(ROOT))
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / '.env')
    except ImportError:
        pass

    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError:
        print('[DB] Chưa cài psycopg2 — bỏ qua bước seed PostgreSQL')
        return

    conn_str = (
        f"host={os.getenv('DB_HOST','localhost')} "
        f"port={os.getenv('DB_PORT','5432')} "
        f"dbname={os.getenv('DB_NAME','postgres')} "
        f"user={os.getenv('DB_USER','postgres')} "
        f"password={os.getenv('DB_PASSWORD','')} "
        f"options='-c client_encoding=UTF8'"
    )
    try:
        conn = psycopg2.connect(conn_str)
        conn.autocommit = False
        cur = conn.cursor()
        print('[DB] Kết nối PostgreSQL OK')
    except Exception as e:
        print(f'[DB] Không kết nối được PostgreSQL: {e}')
        return

    try:
        # 1. ds_theloai (categories) — drop nếu cấu trúc cũ sai
        cur.execute("DROP TABLE IF EXISTS public.ds_theloai CASCADE")
        cur.execute('''
            CREATE TABLE public.ds_theloai (
                id         VARCHAR(50)  PRIMARY KEY,
                name       VARCHAR(100) NOT NULL,
                code       VARCHAR(50)  UNIQUE,
                created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
            )
        ''')
        for cat in CATEGORIES:
            cur.execute('''
                INSERT INTO public.ds_theloai (id, name, code)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            ''', (cat['id'], cat['name'], cat['code']))
        print(f'[DB] Seeded {len(CATEGORIES)} danh mục → ds_theloai')

        # 2. ds_dichvucong
        cur.execute("DROP TABLE IF EXISTS public.ds_dichvucong CASCADE")
        cur.execute('''
            CREATE TABLE public.ds_dichvucong (
                id          VARCHAR(80)  PRIMARY KEY,
                name        VARCHAR(255) NOT NULL,
                description TEXT         NOT NULL DEFAULT '',
                category_id VARCHAR(50),
                address     TEXT         NOT NULL DEFAULT '',
                latitude    DOUBLE PRECISION,
                longitude   DOUBLE PRECISION,
                phone       VARCHAR(50)  NOT NULL DEFAULT '',
                email       VARCHAR(100) NOT NULL DEFAULT '',
                website     VARCHAR(255) NOT NULL DEFAULT '',
                level       VARCHAR(30)  NOT NULL DEFAULT 'district',
                status      VARCHAR(20)  NOT NULL DEFAULT 'normal',
                rating      FLOAT        NOT NULL DEFAULT 0,
                field       VARCHAR(255) NOT NULL DEFAULT '',
                province    VARCHAR(100) NOT NULL DEFAULT '',
                district    VARCHAR(100) NOT NULL DEFAULT '',
                ward        VARCHAR(100) NOT NULL DEFAULT '',
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            )
        ''')

        rows_dv = []
        for row in AGENCIES_RAW:
            (sid, name, cat_id, address, lat, lng,
             phone, level, services, district) = row
            rows_dv.append((
                sid, name, name, cat_id, address,
                lat, lng, phone, '', '', level, 'normal', 0,
                ', '.join(services), 'Thanh Hóa', district, '',
            ))

        execute_values(cur, '''
            INSERT INTO public.ds_dichvucong
              (id, name, description, category_id, address,
               latitude, longitude, phone, email, website,
               level, status, rating, field, province, district, ward)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
              name        = EXCLUDED.name,
              address     = EXCLUDED.address,
              latitude    = EXCLUDED.latitude,
              longitude   = EXCLUDED.longitude,
              phone       = EXCLUDED.phone,
              level       = EXCLUDED.level,
              field       = EXCLUDED.field,
              updated_at  = now()
        ''', rows_dv)
        print(f'[DB] Seeded {len(rows_dv)} cơ quan → ds_dichvucong')

        # 3. agencies (FK table)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS public.agencies (
                id        VARCHAR(255) PRIMARY KEY,
                name      VARCHAR(255) NOT NULL DEFAULT '',
                address   TEXT         NOT NULL DEFAULT '',
                district  VARCHAR(100) NOT NULL DEFAULT '',
                province  VARCHAR(100) NOT NULL DEFAULT '',
                latitude  DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                level     VARCHAR(30)  NOT NULL DEFAULT 'district',
                phone     VARCHAR(50)  NOT NULL DEFAULT '',
                is_active BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        ''')
        rows_ag = []
        for row in AGENCIES_RAW:
            (sid, name, cat_id, address, lat, lng,
             phone, level, services, district) = row
            rows_ag.append((sid, name, address, district, 'Thanh Hóa', lat, lng, level, phone))

        execute_values(cur, '''
            INSERT INTO public.agencies
              (id, name, address, district, province, latitude, longitude, level, phone)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
              name      = EXCLUDED.name,
              address   = EXCLUDED.address,
              latitude  = EXCLUDED.latitude,
              longitude = EXCLUDED.longitude,
              updated_at = now()
        ''', rows_ag)
        print(f'[DB] Seeded {len(rows_ag)} cơ quan → agencies')

        conn.commit()
        print('[DB] COMMIT OK')
    except Exception as e:
        conn.rollback()
        print(f'[DB] Lỗi seed: {e}')
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    print('=== Seed dữ liệu cơ quan Thanh Hóa ===')
    seed_json()
    seed_postgres()
    print('=== XONG ===')
    print(f'Tổng: {len(AGENCIES_RAW)} cơ quan, {len(CATEGORIES)} danh mục')
