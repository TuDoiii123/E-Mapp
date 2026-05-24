"""
Seed dữ liệu cơ quan hành chính thành phố Hà Nội.

Chạy: cd Backend && python scripts/seed_hanoi_agencies.py

Ghi vào:
  - PostgreSQL: ds_theloai, ds_dichvucong, agencies
  - data/hanoi_agencies.json  (fallback)

Phạm vi:
  - 15 cơ quan cấp thành phố (UBND TP, Sở/Ban/Ngành, Cục Thuế, BHXH, Kho bạc, TTHCC)
  - 12 quận nội thành  (mỗi quận: UBND + Công an + TT Dịch vụ công)
  - 1 thị xã Sơn Tây   (UBND + Công an + TT Dịch vụ công)
  - 17 huyện ngoại thành (mỗi huyện: UBND + Công an + TT Y tế)
  Tổng: ~85 cơ quan
"""

import json, os, sys
from pathlib import Path
from datetime import datetime

ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
JSON_OUT = DATA_DIR / 'hanoi_agencies.json'

# ── Giờ làm việc mặc định ─────────────────────────────────────────────────────
WH = {
    'monday':    '7:30-12:00, 13:30-17:00',
    'tuesday':   '7:30-12:00, 13:30-17:00',
    'wednesday': '7:30-12:00, 13:30-17:00',
    'thursday':  '7:30-12:00, 13:30-17:00',
    'friday':    '7:30-12:00, 13:30-17:00',
    'saturday':  '7:30-11:30',
    'sunday':    'Closed',
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

    # ══════════════════════════════════════════════════════════════════════════
    # CẤP THÀNH PHỐ HÀ NỘI
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-tp',
     'UBND Thành phố Hà Nội',
     'ubnd', '12 Lê Lai, P. Cửa Nam, Q. Hoàn Kiếm, Hà Nội',
     21.0270, 105.8458, '024.3825.5412', 'province',
     ['Hành chính tổng hợp', 'Tiếp công dân', 'Giải quyết khiếu nại tố cáo', 'Chỉ đạo điều hành'],
     'Q. Hoàn Kiếm'),

    ('hn-congan-tp',
     'Công an Thành phố Hà Nội',
     'police', '89 Trần Hưng Đạo, P. Cửa Nam, Q. Hoàn Kiếm, Hà Nội',
     21.0223, 105.8457, '024.3942.0699', 'province',
     ['CCCD', 'Hộ chiếu', 'Xuất nhập cảnh', 'Đăng ký xe', 'PCCC', 'An ninh trật tự'],
     'Q. Hoàn Kiếm'),

    ('hn-so-tuphanh',
     'Sở Tư pháp Hà Nội',
     'so-nganh', '28-30 Trần Phú, P. Điện Biên, Q. Ba Đình, Hà Nội',
     21.0355, 105.8394, '024.3734.4453', 'province',
     ['Hộ tịch', 'Công chứng', 'Chứng thực', 'Trợ giúp pháp lý', 'Nuôi con nuôi'],
     'Q. Ba Đình'),

    ('hn-so-tnmt',
     'Sở Tài nguyên & Môi trường Hà Nội',
     'so-nganh', '18 Huỳnh Thúc Kháng, P. Láng Hạ, Q. Đống Đa, Hà Nội',
     21.0247, 105.8287, '024.3514.3200', 'province',
     ['Đất đai', 'Giấy CNQSDĐ', 'Môi trường', 'Khoáng sản', 'Tài nguyên nước'],
     'Q. Đống Đa'),

    ('hn-so-khdt',
     'Sở Kế hoạch & Đầu tư Hà Nội',
     'so-nganh', '16 Cát Linh, P. Cát Linh, Q. Đống Đa, Hà Nội',
     21.0285, 105.8404, '024.3734.4625', 'province',
     ['Đăng ký doanh nghiệp', 'Đầu tư nước ngoài', 'Đấu thầu', 'Hợp tác xã'],
     'Q. Đống Đa'),

    ('hn-so-xaydung',
     'Sở Xây dựng Hà Nội',
     'so-nganh', '52 Lê Đại Hành, P. Lê Đại Hành, Q. Hai Bà Trưng, Hà Nội',
     21.0138, 105.8607, '024.3976.4050', 'province',
     ['Cấp phép xây dựng', 'Quy hoạch kiến trúc', 'Nhà ở', 'Bất động sản'],
     'Q. Hai Bà Trưng'),

    ('hn-so-gtvt',
     'Sở Giao thông Vận tải Hà Nội',
     'so-nganh', '8 Phạm Hùng, P. Mỹ Đình 2, Q. Nam Từ Liêm, Hà Nội',
     21.0234, 105.7830, '024.3768.7484', 'province',
     ['Giấy phép lái xe', 'Đăng kiểm phương tiện', 'Vận tải', 'Hạ tầng giao thông'],
     'Q. Nam Từ Liêm'),

    ('hn-so-yte',
     'Sở Y tế Hà Nội',
     'so-nganh', '4 Sơn Tây, P. Điện Biên, Q. Ba Đình, Hà Nội',
     21.0371, 105.8343, '024.3734.5008', 'province',
     ['Cấp phép hành nghề y', 'An toàn thực phẩm', 'Dược phẩm', 'Khám chữa bệnh'],
     'Q. Ba Đình'),

    ('hn-so-gddt',
     'Sở Giáo dục & Đào tạo Hà Nội',
     'so-nganh', '23 Quang Trung, P. Trần Hưng Đạo, Q. Hoàn Kiếm, Hà Nội',
     21.0233, 105.8513, '024.3942.1256', 'province',
     ['Bằng cấp chứng chỉ', 'Tuyển sinh', 'Phổ cập giáo dục', 'Xét công nhận trường chuẩn'],
     'Q. Hoàn Kiếm'),

    ('hn-so-ldtbxh',
     'Sở Lao động TB&XH Hà Nội',
     'so-nganh', 'Số 4 Đinh Lễ, P. Tràng Tiền, Q. Hoàn Kiếm, Hà Nội',
     21.0261, 105.8528, '024.3825.4812', 'province',
     ['Việc làm', 'Bảo hiểm thất nghiệp', 'Trẻ em', 'Người có công', 'An toàn lao động'],
     'Q. Hoàn Kiếm'),

    ('hn-so-taichinh',
     'Sở Tài chính Hà Nội',
     'so-nganh', '60 Nguyễn Thái Học, P. Nguyễn Thái Học, Q. Ba Đình, Hà Nội',
     21.0326, 105.8387, '024.3734.2268', 'province',
     ['Ngân sách nhà nước', 'Đầu tư công', 'Tài sản công', 'Giá cả thị trường'],
     'Q. Ba Đình'),

    ('hn-so-tttt',
     'Sở Thông tin & Truyền thông Hà Nội',
     'so-nganh', '73 Đinh Tiên Hoàng, P. Đinh Tiên Hoàng, Q. Hoàn Kiếm, Hà Nội',
     21.0306, 105.8520, '024.3938.5075', 'province',
     ['Báo chí xuất bản', 'Viễn thông internet', 'An toàn thông tin', 'Chuyển đổi số'],
     'Q. Hoàn Kiếm'),

    ('hn-cuc-thue',
     'Cục Thuế TP. Hà Nội',
     'tax', '14 Hội Vũ, P. Cửa Đông, Q. Hoàn Kiếm, Hà Nội',
     21.0302, 105.8475, '024.3942.8765', 'province',
     ['Kê khai thuế', 'Hoàn thuế GTGT', 'Đăng ký mã số thuế', 'Thuế TNCN', 'Thuế doanh nghiệp'],
     'Q. Hoàn Kiếm'),

    ('hn-bhxh-tp',
     'BHXH Thành phố Hà Nội',
     'bhxh', '28 Phạm Đình Hổ, P. Phạm Đình Hổ, Q. Hai Bà Trưng, Hà Nội',
     21.0191, 105.8590, '024.3978.8200', 'province',
     ['BHXH bắt buộc', 'BHYT', 'Bảo hiểm thất nghiệp', 'Cấp sổ BHXH', 'Giải quyết chế độ'],
     'Q. Hai Bà Trưng'),

    ('hn-khobac-tp',
     'Kho bạc Nhà nước TP. Hà Nội',
     'tax', '11 Trần Phú, P. Điện Biên, Q. Ba Đình, Hà Nội',
     21.0360, 105.8401, '024.3734.5613', 'province',
     ['Kiểm soát chi NSNN', 'Thanh toán ngân sách', 'Kế toán nhà nước', 'Trái phiếu CP'],
     'Q. Ba Đình'),

    ('hn-tthcc-tp',
     'Trung tâm Phục vụ Hành chính Công TP. Hà Nội',
     'trung-tam', '258 Võ Chí Công, P. Xuân La, Q. Tây Hồ, Hà Nội',
     21.0689, 105.8129, '024.3937.8686', 'province',
     ['Một cửa liên thông', 'Tiếp nhận hồ sơ', 'Trả kết quả', 'Dịch vụ công trực tuyến'],
     'Q. Tây Hồ'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN HOÀN KIẾM
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-hoankiem',
     'UBND Quận Hoàn Kiếm',
     'ubnd', '46 Đinh Tiên Hoàng, P. Lý Thái Tổ, Q. Hoàn Kiếm, Hà Nội',
     21.0283, 105.8503, '024.3825.5533', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh', 'ATTP'],
     'Q. Hoàn Kiếm'),

    ('hn-ca-hoankiem',
     'Công an Quận Hoàn Kiếm',
     'police', '2 Đinh Lễ, P. Tràng Tiền, Q. Hoàn Kiếm, Hà Nội',
     21.0262, 105.8530, '024.3942.9001', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'An ninh trật tự'],
     'Q. Hoàn Kiếm'),

    ('hn-dvc-hoankiem',
     'Bộ phận TN&TKQ Quận Hoàn Kiếm',
     'trung-tam', '46 Đinh Tiên Hoàng, P. Lý Thái Tổ, Q. Hoàn Kiếm, Hà Nội',
     21.0281, 105.8500, '024.3825.5534', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả', 'Dịch vụ công trực tuyến'],
     'Q. Hoàn Kiếm'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN BA ĐÌNH
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-badinh',
     'UBND Quận Ba Đình',
     'ubnd', '10 Liễu Giai, P. Cống Vị, Q. Ba Đình, Hà Nội',
     21.0389, 105.8283, '024.3771.7750', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Ba Đình'),

    ('hn-ca-badinh',
     'Công an Quận Ba Đình',
     'police', '12 Lý Nam Đế, P. Lý Nam Đế, Q. Hoàn Kiếm, Hà Nội',
     21.0340, 105.8450, '024.3771.3571', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy', 'PCCC'],
     'Q. Ba Đình'),

    ('hn-dvc-badinh',
     'Bộ phận TN&TKQ Quận Ba Đình',
     'trung-tam', '10 Liễu Giai, P. Cống Vị, Q. Ba Đình, Hà Nội',
     21.0387, 105.8281, '024.3771.7751', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Ba Đình'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN ĐỐNG ĐA
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-dongda',
     'UBND Quận Đống Đa',
     'ubnd', '45 Nguyễn Khuyến, P. Văn Miếu, Q. Đống Đa, Hà Nội',
     21.0263, 105.8433, '024.3851.1706', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Đống Đa'),

    ('hn-ca-dongda',
     'Công an Quận Đống Đa',
     'police', '37 Hào Nam, P. Ô Chợ Dừa, Q. Đống Đa, Hà Nội',
     21.0237, 105.8370, '024.3851.0076', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Đống Đa'),

    ('hn-dvc-dongda',
     'Bộ phận TN&TKQ Quận Đống Đa',
     'trung-tam', '45 Nguyễn Khuyến, P. Văn Miếu, Q. Đống Đa, Hà Nội',
     21.0261, 105.8431, '024.3851.1707', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Đống Đa'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN HAI BÀ TRƯNG
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-haibatrung',
     'UBND Quận Hai Bà Trưng',
     'ubnd', '86 Lê Đại Hành, P. Lê Đại Hành, Q. Hai Bà Trưng, Hà Nội',
     21.0138, 105.8605, '024.3976.8080', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Hai Bà Trưng'),

    ('hn-ca-haibatrung',
     'Công an Quận Hai Bà Trưng',
     'police', '16 Quỳnh Lôi, P. Quỳnh Lôi, Q. Hai Bà Trưng, Hà Nội',
     21.0063, 105.8558, '024.3976.8111', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Hai Bà Trưng'),

    ('hn-dvc-haibatrung',
     'Bộ phận TN&TKQ Quận Hai Bà Trưng',
     'trung-tam', '86 Lê Đại Hành, P. Lê Đại Hành, Q. Hai Bà Trưng, Hà Nội',
     21.0136, 105.8603, '024.3976.8082', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Hai Bà Trưng'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN HOÀNG MAI
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-hoangmai',
     'UBND Quận Hoàng Mai',
     'ubnd', '129 Minh Khai, P. Minh Khai, Q. Hoàng Mai, Hà Nội',
     20.9940, 105.8595, '024.3641.5805', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Hoàng Mai'),

    ('hn-ca-hoangmai',
     'Công an Quận Hoàng Mai',
     'police', '131 Minh Khai, P. Minh Khai, Q. Hoàng Mai, Hà Nội',
     20.9938, 105.8597, '024.3641.5113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy', 'PCCC'],
     'Q. Hoàng Mai'),

    ('hn-dvc-hoangmai',
     'Bộ phận TN&TKQ Quận Hoàng Mai',
     'trung-tam', '129 Minh Khai, P. Minh Khai, Q. Hoàng Mai, Hà Nội',
     20.9941, 105.8593, '024.3641.5806', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Hoàng Mai'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN LONG BIÊN
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-longbien',
     'UBND Quận Long Biên',
     'ubnd', '48 Tư Đình, P. Long Biên, Q. Long Biên, Hà Nội',
     21.0450, 105.8960, '024.3827.7299', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Long Biên'),

    ('hn-ca-longbien',
     'Công an Quận Long Biên',
     'police', '50 Tư Đình, P. Long Biên, Q. Long Biên, Hà Nội',
     21.0452, 105.8963, '024.3827.7113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Long Biên'),

    ('hn-dvc-longbien',
     'Bộ phận TN&TKQ Quận Long Biên',
     'trung-tam', '48 Tư Đình, P. Long Biên, Q. Long Biên, Hà Nội',
     21.0449, 105.8958, '024.3827.7300', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Long Biên'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN TÂY HỒ
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-tayho',
     'UBND Quận Tây Hồ',
     'ubnd', 'Số 1 Đặng Thai Mai, P. Quảng An, Q. Tây Hồ, Hà Nội',
     21.0680, 105.8270, '024.3718.4888', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Du lịch', 'Kinh doanh'],
     'Q. Tây Hồ'),

    ('hn-ca-tayho',
     'Công an Quận Tây Hồ',
     'police', '262 Thụy Khuê, P. Thụy Khuê, Q. Tây Hồ, Hà Nội',
     21.0559, 105.8213, '024.3718.4113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'An ninh trật tự'],
     'Q. Tây Hồ'),

    ('hn-dvc-tayho',
     'Bộ phận TN&TKQ Quận Tây Hồ',
     'trung-tam', 'Số 1 Đặng Thai Mai, P. Quảng An, Q. Tây Hồ, Hà Nội',
     21.0678, 105.8268, '024.3718.4889', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Tây Hồ'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN CẦU GIẤY
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-caugiay',
     'UBND Quận Cầu Giấy',
     'ubnd', '146 Xuân Thủy, P. Dịch Vọng Hậu, Q. Cầu Giấy, Hà Nội',
     21.0374, 105.7900, '024.3756.5168', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Cầu Giấy'),

    ('hn-ca-caugiay',
     'Công an Quận Cầu Giấy',
     'police', '183 Trần Duy Hưng, P. Trung Hòa, Q. Cầu Giấy, Hà Nội',
     21.0199, 105.7958, '024.3556.7113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Cầu Giấy'),

    ('hn-dvc-caugiay',
     'Bộ phận TN&TKQ Quận Cầu Giấy',
     'trung-tam', '146 Xuân Thủy, P. Dịch Vọng Hậu, Q. Cầu Giấy, Hà Nội',
     21.0372, 105.7898, '024.3756.5169', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Cầu Giấy'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN THANH XUÂN
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-thanhxuan',
     'UBND Quận Thanh Xuân',
     'ubnd', '214 Trường Chinh, P. Khương Mai, Q. Thanh Xuân, Hà Nội',
     20.9970, 105.8250, '024.3558.5559', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Thanh Xuân'),

    ('hn-ca-thanhxuan',
     'Công an Quận Thanh Xuân',
     'police', '4 Khuất Duy Tiến, P. Nhân Chính, Q. Thanh Xuân, Hà Nội',
     21.0046, 105.8052, '024.3558.5113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Thanh Xuân'),

    ('hn-dvc-thanhxuan',
     'Bộ phận TN&TKQ Quận Thanh Xuân',
     'trung-tam', '214 Trường Chinh, P. Khương Mai, Q. Thanh Xuân, Hà Nội',
     20.9968, 105.8248, '024.3558.5560', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Thanh Xuân'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN HÀ ĐÔNG
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-hadong',
     'UBND Quận Hà Đông',
     'ubnd', '11 Lê Trọng Tấn, P. Hà Cầu, Q. Hà Đông, Hà Nội',
     20.9734, 105.7760, '024.3382.3288', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Hà Đông'),

    ('hn-ca-hadong',
     'Công an Quận Hà Đông',
     'police', '3 Quang Trung, P. Quang Trung, Q. Hà Đông, Hà Nội',
     20.9760, 105.7754, '024.3382.3113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy', 'PCCC'],
     'Q. Hà Đông'),

    ('hn-dvc-hadong',
     'Bộ phận TN&TKQ Quận Hà Đông',
     'trung-tam', '11 Lê Trọng Tấn, P. Hà Cầu, Q. Hà Đông, Hà Nội',
     20.9732, 105.7758, '024.3382.3289', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Hà Đông'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN NAM TỪ LIÊM
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-namtuлием',
     'UBND Quận Nam Từ Liêm',
     'ubnd', 'Đường Đỗ Xuân Hợp, P. Trung Văn, Q. Nam Từ Liêm, Hà Nội',
     21.0020, 105.7700, '024.6282.2288', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Nam Từ Liêm'),

    ('hn-ca-namtuliem',
     'Công an Quận Nam Từ Liêm',
     'police', 'Đường Đỗ Xuân Hợp, P. Trung Văn, Q. Nam Từ Liêm, Hà Nội',
     21.0018, 105.7698, '024.6282.2113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'Q. Nam Từ Liêm'),

    ('hn-dvc-namtuliem',
     'Bộ phận TN&TKQ Quận Nam Từ Liêm',
     'trung-tam', 'Đường Đỗ Xuân Hợp, P. Trung Văn, Q. Nam Từ Liêm, Hà Nội',
     21.0019, 105.7699, '024.6282.2289', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Nam Từ Liêm'),

    # ══════════════════════════════════════════════════════════════════════════
    # QUẬN BẮC TỪ LIÊM
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-bactuliem',
     'UBND Quận Bắc Từ Liêm',
     'ubnd', '34 Phạm Văn Đồng, P. Cổ Nhuế 2, Q. Bắc Từ Liêm, Hà Nội',
     21.0510, 105.7770, '024.3836.5588', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
     'Q. Bắc Từ Liêm'),

    ('hn-ca-bactuliem',
     'Công an Quận Bắc Từ Liêm',
     'police', '32 Phạm Văn Đồng, P. Cổ Nhuế 2, Q. Bắc Từ Liêm, Hà Nội',
     21.0508, 105.7768, '024.3836.5113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy', 'PCCC'],
     'Q. Bắc Từ Liêm'),

    ('hn-dvc-bactuliem',
     'Bộ phận TN&TKQ Quận Bắc Từ Liêm',
     'trung-tam', '34 Phạm Văn Đồng, P. Cổ Nhuế 2, Q. Bắc Từ Liêm, Hà Nội',
     21.0509, 105.7769, '024.3836.5589', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'Q. Bắc Từ Liêm'),

    # ══════════════════════════════════════════════════════════════════════════
    # THỊ XÃ SƠN TÂY
    # ══════════════════════════════════════════════════════════════════════════
    ('hn-ubnd-sontay',
     'UBND Thị xã Sơn Tây',
     'ubnd', '5 Phố Lê Lợi, P. Lê Lợi, TX. Sơn Tây, Hà Nội',
     21.1417, 105.5048, '024.3383.2325', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh', 'Du lịch lịch sử'],
     'TX. Sơn Tây'),

    ('hn-ca-sontay',
     'Công an TX. Sơn Tây',
     'police', '38 Phùng Khắc Khoan, P. Quang Trung, TX. Sơn Tây, Hà Nội',
     21.1404, 105.5060, '024.3383.2113', 'district',
     ['CCCD', 'Tạm trú tạm vắng', 'Đăng ký xe máy'],
     'TX. Sơn Tây'),

    ('hn-dvc-sontay',
     'Bộ phận TN&TKQ TX. Sơn Tây',
     'trung-tam', '5 Phố Lê Lợi, P. Lê Lợi, TX. Sơn Tây, Hà Nội',
     21.1415, 105.5046, '024.3383.2326', 'district',
     ['Tiếp nhận hồ sơ', 'Trả kết quả'],
     'TX. Sơn Tây'),

    # ══════════════════════════════════════════════════════════════════════════
    # 17 HUYỆN NGOẠI THÀNH — mỗi huyện: UBND + Công an + Trung tâm Y tế
    # ══════════════════════════════════════════════════════════════════════════

    # Ba Vì
    ('hn-ubnd-bavi',
     'UBND Huyện Ba Vì',
     'ubnd', 'TT. Tây Đằng, H. Ba Vì, Hà Nội',
     21.1867, 105.3944, '024.3387.6501', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Nông nghiệp'], 'H. Ba Vì'),
    ('hn-ca-bavi',
     'Công an Huyện Ba Vì',
     'police', 'TT. Tây Đằng, H. Ba Vì, Hà Nội',
     21.1870, 105.3950, '024.3387.6113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Ba Vì'),
    ('hn-ttyte-bavi',
     'Trung tâm Y tế Huyện Ba Vì',
     'health', 'TT. Tây Đằng, H. Ba Vì, Hà Nội',
     21.1862, 105.3938, '024.3387.6115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng', 'Y tế dự phòng'], 'H. Ba Vì'),

    # Chương Mỹ
    ('hn-ubnd-chuongmy',
     'UBND Huyện Chương Mỹ',
     'ubnd', 'TT. Chúc Sơn, H. Chương Mỹ, Hà Nội',
     20.8744, 105.7231, '024.3386.6501', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Nông nghiệp'], 'H. Chương Mỹ'),
    ('hn-ca-chuongmy',
     'Công an Huyện Chương Mỹ',
     'police', 'TT. Chúc Sơn, H. Chương Mỹ, Hà Nội',
     20.8747, 105.7234, '024.3386.6113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Chương Mỹ'),
    ('hn-ttyte-chuongmy',
     'Trung tâm Y tế Huyện Chương Mỹ',
     'health', 'TT. Chúc Sơn, H. Chương Mỹ, Hà Nội',
     20.8740, 105.7228, '024.3386.6115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Chương Mỹ'),

    # Đan Phượng
    ('hn-ubnd-danphuong',
     'UBND Huyện Đan Phượng',
     'ubnd', 'TT. Phùng, H. Đan Phượng, Hà Nội',
     21.1037, 105.6740, '024.3388.0501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp'], 'H. Đan Phượng'),
    ('hn-ca-danphuong',
     'Công an Huyện Đan Phượng',
     'police', 'TT. Phùng, H. Đan Phượng, Hà Nội',
     21.1040, 105.6743, '024.3388.0113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Đan Phượng'),
    ('hn-ttyte-danphuong',
     'Trung tâm Y tế Huyện Đan Phượng',
     'health', 'TT. Phùng, H. Đan Phượng, Hà Nội',
     21.1034, 105.6737, '024.3388.0115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Đan Phượng'),

    # Đông Anh
    ('hn-ubnd-donganh',
     'UBND Huyện Đông Anh',
     'ubnd', 'TT. Đông Anh, H. Đông Anh, Hà Nội',
     21.1500, 105.8450, '024.3882.1501', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Công nghiệp'], 'H. Đông Anh'),
    ('hn-ca-donganh',
     'Công an Huyện Đông Anh',
     'police', 'TT. Đông Anh, H. Đông Anh, Hà Nội',
     21.1503, 105.8454, '024.3882.1113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Đông Anh'),
    ('hn-ttyte-donganh',
     'Trung tâm Y tế Huyện Đông Anh',
     'health', 'TT. Đông Anh, H. Đông Anh, Hà Nội',
     21.1497, 105.8446, '024.3882.1115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng', 'Y tế dự phòng'], 'H. Đông Anh'),

    # Gia Lâm
    ('hn-ubnd-gialam',
     'UBND Huyện Gia Lâm',
     'ubnd', 'TT. Trâu Quỳ, H. Gia Lâm, Hà Nội',
     21.0168, 105.9417, '024.3827.9501', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Công nghiệp'], 'H. Gia Lâm'),
    ('hn-ca-gialam',
     'Công an Huyện Gia Lâm',
     'police', 'TT. Trâu Quỳ, H. Gia Lâm, Hà Nội',
     21.0171, 105.9420, '024.3827.9113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Gia Lâm'),
    ('hn-ttyte-gialam',
     'Trung tâm Y tế Huyện Gia Lâm',
     'health', 'TT. Trâu Quỳ, H. Gia Lâm, Hà Nội',
     21.0165, 105.9414, '024.3827.9115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Gia Lâm'),

    # Hoài Đức
    ('hn-ubnd-hoaiduc',
     'UBND Huyện Hoài Đức',
     'ubnd', 'TT. Trạm Trôi, H. Hoài Đức, Hà Nội',
     21.0285, 105.7173, '024.3363.5501', 'district',
     ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Nông nghiệp'], 'H. Hoài Đức'),
    ('hn-ca-hoaiduc',
     'Công an Huyện Hoài Đức',
     'police', 'TT. Trạm Trôi, H. Hoài Đức, Hà Nội',
     21.0288, 105.7176, '024.3363.5113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Hoài Đức'),
    ('hn-ttyte-hoaiduc',
     'Trung tâm Y tế Huyện Hoài Đức',
     'health', 'TT. Trạm Trôi, H. Hoài Đức, Hà Nội',
     21.0282, 105.7170, '024.3363.5115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Hoài Đức'),

    # Mê Linh
    ('hn-ubnd-melinh',
     'UBND Huyện Mê Linh',
     'ubnd', 'TT. Chi Đông, H. Mê Linh, Hà Nội',
     21.1857, 105.7470, '024.3386.0501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Công nghiệp'], 'H. Mê Linh'),
    ('hn-ca-melinh',
     'Công an Huyện Mê Linh',
     'police', 'TT. Chi Đông, H. Mê Linh, Hà Nội',
     21.1860, 105.7473, '024.3386.0113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Mê Linh'),
    ('hn-ttyte-melinh',
     'Trung tâm Y tế Huyện Mê Linh',
     'health', 'TT. Chi Đông, H. Mê Linh, Hà Nội',
     21.1854, 105.7467, '024.3386.0115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Mê Linh'),

    # Mỹ Đức
    ('hn-ubnd-myduc',
     'UBND Huyện Mỹ Đức',
     'ubnd', 'TT. Đại Nghĩa, H. Mỹ Đức, Hà Nội',
     20.7135, 105.7170, '024.3387.1501', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Du lịch Hương Sơn'], 'H. Mỹ Đức'),
    ('hn-ca-myduc',
     'Công an Huyện Mỹ Đức',
     'police', 'TT. Đại Nghĩa, H. Mỹ Đức, Hà Nội',
     20.7138, 105.7173, '024.3387.1113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Mỹ Đức'),
    ('hn-ttyte-myduc',
     'Trung tâm Y tế Huyện Mỹ Đức',
     'health', 'TT. Đại Nghĩa, H. Mỹ Đức, Hà Nội',
     20.7132, 105.7167, '024.3387.1115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Mỹ Đức'),

    # Phú Xuyên
    ('hn-ubnd-phuxuyen',
     'UBND Huyện Phú Xuyên',
     'ubnd', 'TT. Phú Minh, H. Phú Xuyên, Hà Nội',
     20.7419, 105.9021, '024.3386.3501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp'], 'H. Phú Xuyên'),
    ('hn-ca-phuxuyen',
     'Công an Huyện Phú Xuyên',
     'police', 'TT. Phú Minh, H. Phú Xuyên, Hà Nội',
     20.7422, 105.9024, '024.3386.3113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Phú Xuyên'),
    ('hn-ttyte-phuxuyen',
     'Trung tâm Y tế Huyện Phú Xuyên',
     'health', 'TT. Phú Minh, H. Phú Xuyên, Hà Nội',
     20.7416, 105.9018, '024.3386.3115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Phú Xuyên'),

    # Phúc Thọ
    ('hn-ubnd-phuctho',
     'UBND Huyện Phúc Thọ',
     'ubnd', 'TT. Phúc Thọ, H. Phúc Thọ, Hà Nội',
     21.1023, 105.5697, '024.3388.6501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp'], 'H. Phúc Thọ'),
    ('hn-ca-phuctho',
     'Công an Huyện Phúc Thọ',
     'police', 'TT. Phúc Thọ, H. Phúc Thọ, Hà Nội',
     21.1026, 105.5700, '024.3388.6113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Phúc Thọ'),
    ('hn-ttyte-phuctho',
     'Trung tâm Y tế Huyện Phúc Thọ',
     'health', 'TT. Phúc Thọ, H. Phúc Thọ, Hà Nội',
     21.1020, 105.5694, '024.3388.6115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Phúc Thọ'),

    # Quốc Oai
    ('hn-ubnd-quocoai',
     'UBND Huyện Quốc Oai',
     'ubnd', 'TT. Quốc Oai, H. Quốc Oai, Hà Nội',
     20.9912, 105.6453, '024.3367.7501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Lâm nghiệp'], 'H. Quốc Oai'),
    ('hn-ca-quocoai',
     'Công an Huyện Quốc Oai',
     'police', 'TT. Quốc Oai, H. Quốc Oai, Hà Nội',
     20.9915, 105.6456, '024.3367.7113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Quốc Oai'),
    ('hn-ttyte-quocoai',
     'Trung tâm Y tế Huyện Quốc Oai',
     'health', 'TT. Quốc Oai, H. Quốc Oai, Hà Nội',
     20.9909, 105.6450, '024.3367.7115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Quốc Oai'),

    # Sóc Sơn
    ('hn-ubnd-socson',
     'UBND Huyện Sóc Sơn',
     'ubnd', 'TT. Sóc Sơn, H. Sóc Sơn, Hà Nội',
     21.2483, 105.8567, '024.3884.0501', 'district',
     ['Hộ tịch', 'Đất đai', 'Lâm nghiệp', 'Nông nghiệp'], 'H. Sóc Sơn'),
    ('hn-ca-socson',
     'Công an Huyện Sóc Sơn',
     'police', 'TT. Sóc Sơn, H. Sóc Sơn, Hà Nội',
     21.2486, 105.8570, '024.3884.0113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Sóc Sơn'),
    ('hn-ttyte-socson',
     'Trung tâm Y tế Huyện Sóc Sơn',
     'health', 'TT. Sóc Sơn, H. Sóc Sơn, Hà Nội',
     21.2480, 105.8564, '024.3884.0115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Sóc Sơn'),

    # Thạch Thất
    ('hn-ubnd-thachthat',
     'UBND Huyện Thạch Thất',
     'ubnd', 'TT. Liên Quan, H. Thạch Thất, Hà Nội',
     21.0003, 105.6217, '024.3368.4501', 'district',
     ['Hộ tịch', 'Đất đai', 'Làng nghề', 'Công nghiệp'], 'H. Thạch Thất'),
    ('hn-ca-thachthat',
     'Công an Huyện Thạch Thất',
     'police', 'TT. Liên Quan, H. Thạch Thất, Hà Nội',
     21.0006, 105.6220, '024.3368.4113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Thạch Thất'),
    ('hn-ttyte-thachthat',
     'Trung tâm Y tế Huyện Thạch Thất',
     'health', 'TT. Liên Quan, H. Thạch Thất, Hà Nội',
     21.0000, 105.6214, '024.3368.4115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Thạch Thất'),

    # Thanh Oai
    ('hn-ubnd-thanhoai',
     'UBND Huyện Thanh Oai',
     'ubnd', 'TT. Kim Bài, H. Thanh Oai, Hà Nội',
     20.8781, 105.8043, '024.3385.5501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Làng nghề'], 'H. Thanh Oai'),
    ('hn-ca-thanhoai',
     'Công an Huyện Thanh Oai',
     'police', 'TT. Kim Bài, H. Thanh Oai, Hà Nội',
     20.8784, 105.8046, '024.3385.5113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Thanh Oai'),
    ('hn-ttyte-thanhoai',
     'Trung tâm Y tế Huyện Thanh Oai',
     'health', 'TT. Kim Bài, H. Thanh Oai, Hà Nội',
     20.8778, 105.8040, '024.3385.5115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Thanh Oai'),

    # Thanh Trì
    ('hn-ubnd-thanhtri',
     'UBND Huyện Thanh Trì',
     'ubnd', 'TT. Văn Điển, H. Thanh Trì, Hà Nội',
     20.9578, 105.8450, '024.3861.0501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Công nghiệp'], 'H. Thanh Trì'),
    ('hn-ca-thanhtri',
     'Công an Huyện Thanh Trì',
     'police', 'TT. Văn Điển, H. Thanh Trì, Hà Nội',
     20.9581, 105.8453, '024.3861.0113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Thanh Trì'),
    ('hn-ttyte-thanhtri',
     'Trung tâm Y tế Huyện Thanh Trì',
     'health', 'TT. Văn Điển, H. Thanh Trì, Hà Nội',
     20.9575, 105.8447, '024.3861.0115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng', 'Y tế dự phòng'], 'H. Thanh Trì'),

    # Thường Tín
    ('hn-ubnd-thuongtin',
     'UBND Huyện Thường Tín',
     'ubnd', 'TT. Thường Tín, H. Thường Tín, Hà Nội',
     20.8667, 105.8667, '024.3386.0501', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Làng nghề'], 'H. Thường Tín'),
    ('hn-ca-thuongtin',
     'Công an Huyện Thường Tín',
     'police', 'TT. Thường Tín, H. Thường Tín, Hà Nội',
     20.8670, 105.8670, '024.3386.0113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Thường Tín'),
    ('hn-ttyte-thuongtin',
     'Trung tâm Y tế Huyện Thường Tín',
     'health', 'TT. Thường Tín, H. Thường Tín, Hà Nội',
     20.8664, 105.8664, '024.3386.0115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Thường Tín'),

    # Ứng Hòa
    ('hn-ubnd-unghoa',
     'UBND Huyện Ứng Hòa',
     'ubnd', 'TT. Vân Đình, H. Ứng Hòa, Hà Nội',
     20.7083, 105.8183, '024.3387.6801', 'district',
     ['Hộ tịch', 'Đất đai', 'Nông nghiệp', 'Nuôi trồng thủy sản'], 'H. Ứng Hòa'),
    ('hn-ca-unghoa',
     'Công an Huyện Ứng Hòa',
     'police', 'TT. Vân Đình, H. Ứng Hòa, Hà Nội',
     20.7086, 105.8186, '024.3387.6113', 'district',
     ['CCCD', 'Đăng ký xe', 'Tạm trú'], 'H. Ứng Hòa'),
    ('hn-ttyte-unghoa',
     'Trung tâm Y tế Huyện Ứng Hòa',
     'health', 'TT. Vân Đình, H. Ứng Hòa, Hà Nội',
     20.7080, 105.8180, '024.3387.6115', 'district',
     ['Khám chữa bệnh', 'Tiêm chủng'], 'H. Ứng Hòa'),
]


# ─────────────────────────────────────────────────────────────────────────────
def build_service_record(row: tuple) -> dict:
    (sid, name, cat_id, address, lat, lng,
     phone, level, services, district) = row
    return {
        'id':           sid,
        'name':         name,
        'description':  name,
        'categoryId':   cat_id,
        'locationId':   None,
        'address':      address,
        'latitude':     lat,
        'longitude':    lng,
        'phone':        phone,
        'email':        '',
        'website':      '',
        'workingHours': WH.copy(),
        'services':     services,
        'level':        level,
        'rating':       0,
        'status':       'normal',
        'distance':     None,
        'province':     'Hà Nội',
        'district':     district,
        'ward':         '',
        'createdAt':    datetime.now().isoformat(),
        'updatedAt':    datetime.now().isoformat(),
    }


def seed_json():
    records = [build_service_record(r) for r in AGENCIES_RAW]
    DATA_DIR.mkdir(exist_ok=True)
    JSON_OUT.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'[JSON] Đã ghi {len(records)} cơ quan → {JSON_OUT}')
    return records


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
        # 1. ds_theloai — UPSERT (không DROP để giữ data Thanh Hóa)
        for cat in CATEGORIES:
            cur.execute('''
                INSERT INTO public.ds_theloai (id, name, code)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            ''', (cat['id'], cat['name'], cat['code']))
        print(f'[DB] Upserted {len(CATEGORIES)} danh mục → ds_theloai')

        # 2. ds_dichvucong — UPSERT từng cơ quan
        rows_dv = []
        for row in AGENCIES_RAW:
            (sid, name, cat_id, address, lat, lng,
             phone, level, services, district) = row
            rows_dv.append((
                sid, name, name, cat_id, address,
                lat, lng, phone, '', '', level, 'normal', 0,
                ', '.join(services), 'Hà Nội', district, '',
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
              province    = EXCLUDED.province,
              district    = EXCLUDED.district,
              updated_at  = now()
        ''', rows_dv)
        print(f'[DB] Upserted {len(rows_dv)} cơ quan → ds_dichvucong')

        # 3. agencies — UPSERT (bảng FK cho queue/appointments)
        rows_ag = []
        for row in AGENCIES_RAW:
            (sid, name, cat_id, address, lat, lng,
             phone, level, services, district) = row
            rows_ag.append((sid, name, address, district, 'Hà Nội', lat, lng, level, phone))

        execute_values(cur, '''
            INSERT INTO public.agencies
              (id, name, address, district, province, latitude, longitude, level, phone)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
              name       = EXCLUDED.name,
              address    = EXCLUDED.address,
              district   = EXCLUDED.district,
              province   = EXCLUDED.province,
              latitude   = EXCLUDED.latitude,
              longitude  = EXCLUDED.longitude,
              level      = EXCLUDED.level,
              phone      = EXCLUDED.phone,
              updated_at = now()
        ''', rows_ag)
        print(f'[DB] Upserted {len(rows_ag)} cơ quan → agencies')

        conn.commit()
        print('[DB] COMMIT OK ✓')

    except Exception as e:
        conn.rollback()
        print(f'[DB] Lỗi seed: {e}')
        import traceback; traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    print('=' * 60)
    print('  Seed dữ liệu cơ quan hành chính TP. Hà Nội')
    print('=' * 60)
    seed_json()
    seed_postgres()
    print('=' * 60)
    print(f'  Tổng: {len(AGENCIES_RAW)} cơ quan | {len(CATEGORIES)} danh mục')
    print('=' * 60)
