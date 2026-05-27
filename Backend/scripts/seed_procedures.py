"""
Seed dữ liệu thực từ Cổng Dịch vụ công Quốc gia (dichvucong.gov.vn)
và Cổng thông tin tỉnh Thanh Hóa.

Nguồn:
  - https://dichvucong.gov.vn
  - https://dichvucong.thanhhoa.gov.vn
  - Cơ sở dữ liệu quốc gia về TTHC (thutuchanhchinh.gov.vn)

Chạy: python scripts/seed_procedures.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(override=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. DỮ LIỆU CƠ QUAN HÀNH CHÍNH — Tỉnh Thanh Hóa
# ══════════════════════════════════════════════════════════════════════════════

AGENCIES = [
    # ── Cấp tỉnh ─────────────────────────────────────────────────────────────
    {
        'id': 'ubnd-thanhhoa',
        'name': 'UBND tỉnh Thanh Hóa',
        'description': 'Ủy ban nhân dân tỉnh Thanh Hóa — cơ quan hành chính nhà nước cao nhất tỉnh',
        'categoryId': 'civil',
        'address': '45 Đại lộ Lê Lợi, phường Điện Biên, TP Thanh Hóa',
        'latitude': 19.8069, 'longitude': 105.7852,
        'phone': '0237.3852.428', 'email': 'ubnd@thanhhoa.gov.vn',
        'website': 'https://thanhhoa.gov.vn', 'level': 'province',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp', 'Xây dựng', 'Kinh doanh', 'Môi trường'],
        'rating': 4.4, 'status': 'available',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'tthcc-thanhhoa',
        'name': 'Trung tâm Phục vụ Hành chính công tỉnh Thanh Hóa',
        'description': 'Giải quyết thủ tục hành chính theo cơ chế một cửa tập trung. Tiếp nhận hồ sơ của 19 Sở, ngành.',
        'categoryId': 'civil',
        'address': '25A Đại lộ Lê Lợi, phường Ba Đình, TP Thanh Hóa',
        'latitude': 19.8078, 'longitude': 105.7858,
        'phone': '0237.3753.888', 'email': 'trungtam@thanhhoa.gov.vn',
        'website': 'https://dichvucong.thanhhoa.gov.vn', 'level': 'province',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp', 'Xây dựng', 'Kinh doanh', 'Thuế', 'Lao động', 'Y tế', 'Giao thông'],
        'rating': 4.6, 'status': 'available',
        'workingHours': {'monday': '7:00-17:30', 'tuesday': '7:00-17:30', 'wednesday': '7:00-17:30',
                         'thursday': '7:00-17:30', 'friday': '7:00-17:30', 'saturday': '7:30-12:00', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'congan-thanhhoa',
        'name': 'Công an tỉnh Thanh Hóa',
        'description': 'Cấp CCCD, hộ chiếu, đăng ký xe, cư trú. Phòng Cảnh sát QLHC về TTXH.',
        'categoryId': 'civil',
        'address': '4 Trần Phú, phường Hàm Rồng, TP Thanh Hóa',
        'latitude': 19.8150, 'longitude': 105.7900,
        'phone': '069.2587.018', 'email': 'pa06@congan.thanhhoa.gov.vn',
        'level': 'province',
        'services': ['CCCD', 'Hộ chiếu', 'Cư trú', 'Đăng ký xe'],
        'rating': 4.3, 'status': 'normal',
        'workingHours': {'monday': '7:30-11:30,13:30-17:00', 'tuesday': '7:30-11:30,13:30-17:00',
                         'wednesday': '7:30-11:30,13:30-17:00', 'thursday': '7:30-11:30,13:30-17:00',
                         'friday': '7:30-11:30,13:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-tnmt',
        'name': 'Sở Tài nguyên và Môi trường Thanh Hóa',
        'description': 'Quản lý đất đai, tài nguyên khoáng sản, môi trường, biển và hải đảo tỉnh Thanh Hóa',
        'categoryId': 'land',
        'address': '33 Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8102, 'longitude': 105.7831,
        'phone': '0237.3752.262', 'email': 'stnmt@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Đất đai', 'Môi trường', 'Khoáng sản', 'Biển'],
        'rating': 4.2, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-tu-phap',
        'name': 'Sở Tư pháp Thanh Hóa',
        'description': 'Công chứng, chứng thực, hộ tịch, quốc tịch, lý lịch tư pháp, bồi thường nhà nước',
        'categoryId': 'justice',
        'address': '34 Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8095, 'longitude': 105.7840,
        'phone': '0237.3852.573', 'email': 'stp@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Tư pháp', 'Hộ tịch', 'Công chứng', 'Lý lịch tư pháp'],
        'rating': 4.5, 'status': 'available',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-gtvt',
        'name': 'Sở Giao thông Vận tải Thanh Hóa',
        'description': 'Cấp đổi giấy phép lái xe, đăng kiểm phương tiện, cấp phép vận tải',
        'categoryId': 'civil',
        'address': '09 Đại lộ Hùng Vương, TP Thanh Hóa',
        'latitude': 19.8040, 'longitude': 105.7880,
        'phone': '0237.3850.397', 'email': 'sgtvt@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Giấy phép lái xe', 'Đăng kiểm xe', 'Vận tải', 'Đường bộ'],
        'rating': 4.1, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-xay-dung',
        'name': 'Sở Xây dựng Thanh Hóa',
        'description': 'Cấp phép xây dựng, quy hoạch đô thị, kinh doanh bất động sản, nhà ở',
        'categoryId': 'construction',
        'address': '22 Đào Duy Từ, TP Thanh Hóa',
        'latitude': 19.8110, 'longitude': 105.7760,
        'phone': '0237.3852.601', 'email': 'sxd@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Xây dựng', 'Quy hoạch', 'Bất động sản', 'Nhà ở'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-khdt',
        'name': 'Sở Kế hoạch và Đầu tư Thanh Hóa',
        'description': 'Đăng ký doanh nghiệp, cấp phép đầu tư, quản lý đấu thầu, thống kê',
        'categoryId': 'business',
        'address': '24 Hải Thượng Lãn Ông, TP Thanh Hóa',
        'latitude': 19.8060, 'longitude': 105.7810,
        'phone': '0237.3852.349', 'email': 'skhdt@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Đăng ký doanh nghiệp', 'Đầu tư', 'Đấu thầu'],
        'rating': 4.2, 'status': 'available',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'cuc-thue-thanhhoa',
        'name': 'Cục Thuế tỉnh Thanh Hóa',
        'description': 'Đăng ký mã số thuế, khai thuế, hoàn thuế, cấp hóa đơn điện tử',
        'categoryId': 'tax',
        'address': '27A Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8082, 'longitude': 105.7845,
        'phone': '0237.3850.068', 'email': 'th@thanhhoa.gdt.gov.vn',
        'website': 'https://thanhhoa.gdt.gov.vn', 'level': 'province',
        'services': ['Thuế', 'Mã số thuế', 'Hóa đơn điện tử', 'Hoàn thuế'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': 'Đóng cửa', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'bhxh-thanhhoa',
        'name': 'Bảo hiểm xã hội tỉnh Thanh Hóa',
        'description': 'BHXH, BHYT, BHTN, hưu trí, tử tuất, ốm đau, thai sản',
        'categoryId': 'labor',
        'address': '103 Đại lộ Lê Lợi, TP Thanh Hóa',
        'latitude': 19.8045, 'longitude': 105.7900,
        'phone': '0237.3852.268', 'email': 'bhxhthanhhoa@vss.gov.vn',
        'website': 'https://bhxthanhhoa.gov.vn', 'level': 'province',
        'services': ['BHXH', 'BHYT', 'Hưu trí', 'Thai sản', 'Ốm đau'],
        'rating': 4.1, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-y-te',
        'name': 'Sở Y tế Thanh Hóa',
        'description': 'Khám sức khỏe, chứng nhận sức khỏe, cấp phép hành nghề y dược, giám định y tế',
        'categoryId': 'health',
        'address': '03 Phạm Bành, TP Thanh Hóa',
        'latitude': 19.8120, 'longitude': 105.7770,
        'phone': '0237.3852.390', 'email': 'soyte@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Y tế', 'Khám sức khỏe', 'Hành nghề y', 'Dược'],
        'rating': 4.3, 'status': 'available',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-gd-dt',
        'name': 'Sở Giáo dục và Đào tạo Thanh Hóa',
        'description': 'Công nhận văn bằng, chứng chỉ, tiếp nhận học sinh, chuyển trường',
        'categoryId': 'education',
        'address': '03 Đào Duy Từ, TP Thanh Hóa',
        'latitude': 19.8125, 'longitude': 105.7750,
        'phone': '0237.3852.487', 'email': 'sgddt@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Giáo dục', 'Văn bằng', 'Chứng chỉ'],
        'rating': 4.2, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': 'Đóng cửa', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'so-ldtbxh',
        'name': 'Sở Lao động - Thương binh và Xã hội Thanh Hóa',
        'description': 'Việc làm, xuất khẩu lao động, ưu đãi người có công, trẻ em, xã hội',
        'categoryId': 'labor',
        'address': '24 Hải Thượng Lãn Ông, TP Thanh Hóa',
        'latitude': 19.8055, 'longitude': 105.7820,
        'phone': '0237.3852.197', 'email': 'soldtbxh@thanhhoa.gov.vn',
        'level': 'province',
        'services': ['Lao động', 'Việc làm', 'Xuất khẩu lao động', 'Người có công'],
        'rating': 4.2, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': 'Đóng cửa', 'sunday': 'Đóng cửa'},
    },
    # ── Cấp huyện / thị xã / thành phố ──────────────────────────────────────
    {
        'id': 'ubnd-tp-thanhhoa',
        'name': 'UBND thành phố Thanh Hóa',
        'description': 'Ủy ban nhân dân thành phố Thanh Hóa — đầu mối giải quyết TTHC cấp thành phố',
        'categoryId': 'civil',
        'address': '16 Lê Hoàn, phường Lam Sơn, TP Thanh Hóa',
        'latitude': 19.8088, 'longitude': 105.7767,
        'phone': '0237.3852.666', 'email': 'ubnd@tpthanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Tư pháp', 'Xây dựng', 'Kinh doanh'],
        'rating': 4.3, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-bimson',
        'name': 'UBND thị xã Bỉm Sơn',
        'description': 'Ủy ban nhân dân thị xã Bỉm Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Đường Lê Lợi, phường Ba Đình, TX Bỉm Sơn',
        'latitude': 20.0876, 'longitude': 105.8579,
        'phone': '0237.3676.001', 'email': 'ubnd@bimson.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Kinh doanh'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-samson',
        'name': 'UBND thị xã Sầm Sơn',
        'description': 'Ủy ban nhân dân thị xã Sầm Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Đường Trường Sơn, phường Trung Sơn, TX Sầm Sơn',
        'latitude': 19.7319, 'longitude': 105.9032,
        'phone': '0237.3866.286', 'email': 'ubnd@samson.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Kinh doanh', 'Du lịch'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-nghison',
        'name': 'UBND thị xã Nghi Sơn',
        'description': 'Ủy ban nhân dân thị xã Nghi Sơn (trước là huyện Tĩnh Gia), tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Khu kinh tế Nghi Sơn, TX Nghi Sơn',
        'latitude': 19.3808, 'longitude': 105.7856,
        'phone': '0237.3693.234', 'email': 'ubnd@nghison.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Kinh doanh', 'Môi trường'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-hoanghoа',
        'name': 'UBND huyện Hoằng Hóa',
        'description': 'Ủy ban nhân dân huyện Hoằng Hóa, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Bút Sơn, huyện Hoằng Hóa',
        'latitude': 19.9003, 'longitude': 105.8564,
        'phone': '0237.3842.001', 'email': 'ubnd@hoanghoa.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 3.9, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-dongson',
        'name': 'UBND huyện Đông Sơn',
        'description': 'Ủy ban nhân dân huyện Đông Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Rừng Thông, huyện Đông Sơn',
        'latitude': 19.7833, 'longitude': 105.7167,
        'phone': '0237.3840.246', 'email': 'ubnd@dongson.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 3.9, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-quangxuong',
        'name': 'UBND huyện Quảng Xương',
        'description': 'Ủy ban nhân dân huyện Quảng Xương, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Quảng Xương, huyện Quảng Xương',
        'latitude': 19.6756, 'longitude': 105.8303,
        'phone': '0237.3871.001', 'email': 'ubnd@quangxuong.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 4.1, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-trieuson',
        'name': 'UBND huyện Triệu Sơn',
        'description': 'Ủy ban nhân dân huyện Triệu Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Triệu Sơn, huyện Triệu Sơn',
        'latitude': 19.9167, 'longitude': 105.5500,
        'phone': '0237.3662.234', 'email': 'ubnd@trieuson.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 3.9, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-thoxuan',
        'name': 'UBND huyện Thọ Xuân',
        'description': 'Ủy ban nhân dân huyện Thọ Xuân, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Thọ Xuân, huyện Thọ Xuân',
        'latitude': 19.9897, 'longitude': 105.4756,
        'phone': '0237.3674.246', 'email': 'ubnd@thoxuan.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng', 'Nông nghiệp'],
        'rating': 4.0, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-yendinh',
        'name': 'UBND huyện Yên Định',
        'description': 'Ủy ban nhân dân huyện Yên Định, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Yên Lâm, huyện Yên Định',
        'latitude': 20.1167, 'longitude': 105.6167,
        'phone': '0237.3670.234', 'email': 'ubnd@yendinh.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Xây dựng'],
        'rating': 3.8, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-vinhloc',
        'name': 'UBND huyện Vĩnh Lộc',
        'description': 'Ủy ban nhân dân huyện Vĩnh Lộc, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Vĩnh Lộc, huyện Vĩnh Lộc',
        'latitude': 20.1833, 'longitude': 105.4667,
        'phone': '0237.3673.234', 'email': 'ubnd@vinhloc.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Du lịch'],
        'rating': 3.9, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-hauloc',
        'name': 'UBND huyện Hậu Lộc',
        'description': 'Ủy ban nhân dân huyện Hậu Lộc, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Hậu Lộc, huyện Hậu Lộc',
        'latitude': 20.0083, 'longitude': 105.9194,
        'phone': '0237.3849.234', 'email': 'ubnd@hauloc.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Thủy sản'],
        'rating': 3.9, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-ngason',
        'name': 'UBND huyện Nga Sơn',
        'description': 'Ủy ban nhân dân huyện Nga Sơn, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Nga Sơn, huyện Nga Sơn',
        'latitude': 20.0833, 'longitude': 106.0333,
        'phone': '0237.3834.234', 'email': 'ubnd@ngason.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Nông nghiệp'],
        'rating': 3.8, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
    {
        'id': 'ubnd-nongcong',
        'name': 'UBND huyện Nông Cống',
        'description': 'Ủy ban nhân dân huyện Nông Cống, tỉnh Thanh Hóa',
        'categoryId': 'civil',
        'address': 'Thị trấn Nông Cống, huyện Nông Cống',
        'latitude': 19.6333, 'longitude': 105.6500,
        'phone': '0237.3882.234', 'email': 'ubnd@nongcong.thanhhoa.gov.vn',
        'level': 'district',
        'services': ['Hộ tịch', 'Đất đai', 'Nông nghiệp'],
        'rating': 3.8, 'status': 'normal',
        'workingHours': {'monday': '7:30-17:00', 'tuesday': '7:30-17:00', 'wednesday': '7:30-17:00',
                         'thursday': '7:30-17:00', 'friday': '7:30-17:00', 'saturday': '7:30-11:30', 'sunday': 'Đóng cửa'},
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# 2. THỦ TỤC HÀNH CHÍNH — Service Requirements
# Nguồn: Cơ sở dữ liệu quốc gia về TTHC (thutuchanhchinh.gov.vn)
# ══════════════════════════════════════════════════════════════════════════════

PROCEDURES = {
    # ── Hộ tịch ──────────────────────────────────────────────────────────────
    'khai_sinh': {
        'name': 'Đăng ký khai sinh',
        'code': '2.000728',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': [
            'Luật Hộ tịch số 60/2014/QH13 ngày 20/11/2014',
            'Nghị định số 123/2015/NĐ-CP ngày 15/11/2015',
            'Thông tư số 04/2020/TT-BTP ngày 28/05/2020',
        ],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký khai sinh (Mẫu TP/HT-2014-TKKS.1)', 'Điền đầy đủ, ký tên người yêu cầu; lấy tại UBND hoặc tải tại dichvucong.gov.vn', True, 'original', 0, 'mau-to-khai-dang-ky-khai-sinh.doc'),
            ('Giấy chứng sinh', 'Bản gốc do cơ sở y tế có thẩm quyền cấp. Nếu sinh tại nhà: giấy xác nhận của người làm chứng', True, 'original', 1),
            ('CCCD/Căn cước công dân của cha hoặc mẹ', 'Bản gốc còn hiệu lực để đối chiếu', True, 'original', 2),
            ('Giấy đăng ký kết hôn của cha mẹ', 'Bản chính (nếu cha mẹ đã đăng ký kết hôn)', False, 'original', 3),
            ('Giấy xác nhận của cha, mẹ (nếu chưa đăng ký kết hôn)', 'Có xác nhận của UBND nơi cư trú', False, 'original', 4),
        ],
    },
    'ket_hon': {
        'name': 'Đăng ký kết hôn',
        'code': '2.000366',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí (từ 01/01/2021)',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': [
            'Luật Hộ tịch số 60/2014/QH13',
            'Luật Hôn nhân và Gia đình số 52/2014/QH13',
            'Nghị định số 123/2015/NĐ-CP ngày 15/11/2015',
        ],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký kết hôn (Mẫu TP/HT-2014-TKKH.1)', 'Hai bên nam nữ điền đầy đủ và ký tên; lấy tại UBND hoặc tải online', True, 'original', 0, 'mau-to-khai-dang-ky-ket-hon.docx'),
            ('CCCD/Căn cước công dân của hai bên nam, nữ', 'Bản gốc còn hiệu lực. Nếu người nước ngoài: hộ chiếu còn hiệu lực', True, 'original', 1),
            ('Giấy xác nhận tình trạng hôn nhân', 'Do UBND cấp xã nơi cư trú cấp trong vòng 06 tháng; cả hai bên đều cần cung cấp', True, 'original', 2, 'mau-to-khai-xac-nhan-tinh-trang-hon-nhan.docx'),
            ('Giấy khai sinh', 'Bản chính hoặc bản sao có chứng thực; dùng để xác định tuổi kết hôn', True, 'certified_copy', 3),
            ('Ảnh 4×6 cm (2 ảnh/người)', 'Ảnh nền trắng, chụp trong vòng 06 tháng', True, 'original', 4),
            ('Giấy khám sức khỏe (nếu cần)', 'Một số trường hợp đặc biệt theo yêu cầu', False, 'original', 5),
        ],
    },
    'khai_tu': {
        'name': 'Đăng ký khai tử',
        'code': '2.000458',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': [
            'Luật Hộ tịch số 60/2014/QH13',
            'Nghị định số 123/2015/NĐ-CP ngày 15/11/2015',
        ],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký khai tử (Mẫu TP/HT-2014-TKKT.1)', 'Người yêu cầu điền đầy đủ và ký tên', True, 'original', 0, 'mau-to-khai-dang-ky-khai-tu.docx'),
            ('Giấy báo tử', 'Do bệnh viện/cơ sở y tế cấp; hoặc Biên bản xác nhận của cơ quan có thẩm quyền nếu chết không rõ nguyên nhân', True, 'original', 1),
            ('CCCD/Căn cước công dân của người yêu cầu', 'Bản gốc còn hiệu lực', True, 'original', 2),
            ('Sổ hộ khẩu/Giấy tờ cư trú của người chết', 'Để xác nhận nơi cư trú', False, 'original', 3),
        ],
    },
    'nhap_quoc_tich': {
        'name': 'Thôi quốc tịch Việt Nam',
        'code': '1.004883',
        'category': 'justice',
        'fee': 2500000,
        'fee_note': '2.500.000 đồng (theo Thông tư 174/2016/TT-BTC)',
        'processing_days': 90,
        'processing_note': '90 ngày làm việc',
        'legal_basis': ['Luật Quốc tịch Việt Nam 2008; sửa đổi 2014'],
        'implementing_level': 'province',
        'agency': 'Sở Tư pháp',
        'requirements': [
            ('Đơn xin thôi quốc tịch Việt Nam', 'Mẫu theo quy định', True, 'original', 0),
            ('Bản sao Hộ chiếu', 'Có chứng thực', True, 'certified_copy', 1),
            ('Giấy tờ về quốc tịch nước ngoài', 'Chứng minh sẽ được nhập quốc tịch nước ngoài', True, 'certified_copy', 2),
            ('Phiếu lý lịch tư pháp số 1', 'Do Sở Tư pháp cấp', True, 'original', 3),
        ],
    },
    # ── Cư trú ────────────────────────────────────────────────────────────────
    'dang_ky_thuong_tru': {
        'name': 'Đăng ký thường trú',
        'code': '2.000600',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 7,
        'processing_note': '07 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Cư trú 2020 (Luật số 68/2020/QH14)',
            'Nghị định số 62/2021/NĐ-CP ngày 29/6/2021',
        ],
        'implementing_level': 'ward',
        'agency': 'Công an cấp xã, phường (nơi đăng ký thường trú)',
        'requirements': [
            ('Phiếu báo thay đổi hộ khẩu, nhân khẩu (CT01)', 'Điền đầy đủ theo mẫu; lấy tại Công an hoặc tải trên Cổng DVC', True, 'original', 0, 'mau-CT01-to-khai-cu-tru.doc'),
            ('CCCD/Căn cước công dân của người yêu cầu', 'Bản gốc còn hiệu lực', True, 'original', 1),
            ('Giấy tờ chứng minh chỗ ở hợp pháp', 'Một trong các loại: Sổ đỏ/Sổ hồng, hợp đồng mua bán nhà, hợp đồng thuê nhà công chứng (thời hạn ≥ 1 năm), giấy cho phép của chủ hộ...', True, 'certified_copy', 2),
            ('Văn bản đồng ý của chủ hộ (nếu đăng ký vào hộ người khác)', 'Ký trực tiếp trước cán bộ hoặc có công chứng', False, 'original', 3),
            ('Giấy tờ xác nhận quan hệ nhân thân với chủ hộ', 'Giấy khai sinh, giấy đăng ký kết hôn… (nếu đăng ký vào hộ gia đình)', False, 'copy', 4),
            ('Tờ khai đăng ký thường trú (Mẫu HK01)', 'Điền đầy đủ thông tin, ký tên (dùng cho cả đăng ký mới và chuyển đổi từ tạm trú)', False, 'original', 5, 'mau-to-khai-dang-ky-thuong-tru.docx'),
        ],
    },
    'xac_nhan_cu_tru': {
        'name': 'Cấp thông báo số định danh cá nhân và thông tin trong Cơ sở dữ liệu về cư trú',
        'code': '2.000660',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 1,
        'processing_note': 'Ngay trong ngày làm việc',
        'legal_basis': ['Luật Cư trú 2020', 'Nghị định 62/2021/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'Công an cấp xã, phường hoặc thực hiện trực tuyến tại cổng DVC',
        'requirements': [
            ('CCCD/Căn cước công dân', 'Bản gốc', True, 'original', 0),
            ('Đơn đề nghị (nếu cấp giấy xác nhận cư trú)', 'Theo mẫu', False, 'original', 1),
        ],
    },
    # ── CCCD ─────────────────────────────────────────────────────────────────
    'cap_cccd': {
        'name': 'Cấp thẻ Căn cước công dân (lần đầu)',
        'code': '2.001944',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí khi cấp lần đầu',
        'processing_days': 15,
        'processing_note': '07-15 ngày làm việc. Cấp nhanh trong 8h nếu cần (thêm phí)',
        'legal_basis': [
            'Luật Căn cước công dân 2014 (Luật số 59/2014/QH13)',
            'Nghị định số 05/2021/NĐ-CP ngày 25/01/2021',
            'Thông tư số 17/2021/TT-BCA ngày 05/02/2021',
        ],
        'implementing_level': 'district',
        'agency': 'Công an cấp huyện / Công an cấp xã (khi được ủy quyền)',
        'requirements': [
            ('Tờ khai căn cước công dân (CC01)', 'Điền đầy đủ, ký tên. Người dưới 14 tuổi: cha/mẹ/người giám hộ ký thay', True, 'original', 0, 'mau-CC01-to-khai-CCCD.doc'),
            ('CMND cũ / CCCD cũ (nếu có)', 'Bản gốc để thu hồi', False, 'original', 1, 'mau-to-khai-cap-CMND.docx'),
            ('Giấy tờ chứng minh thông tin cá nhân', 'Giấy khai sinh, hộ chiếu, sổ hộ khẩu... nếu thông tin chưa có trong CSDL quốc gia', False, 'copy', 2),
        ],
    },
    'doi_cccd': {
        'name': 'Cấp đổi thẻ Căn cước công dân',
        'code': '2.001945',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí cấp đổi theo lộ trình nhà nước. Phí đổi có chip: 30.000 đồng',
        'processing_days': 15,
        'processing_note': '07-15 ngày làm việc',
        'legal_basis': [
            'Luật Căn cước công dân 2014',
            'Nghị định số 05/2021/NĐ-CP',
        ],
        'implementing_level': 'district',
        'agency': 'Công an cấp huyện hoặc làm tại xe lưu động của Công an tỉnh',
        'requirements': [
            ('Tờ khai căn cước công dân (CC01)', 'Điền đầy đủ thông tin', True, 'original', 0, 'mau-CC01-to-khai-CCCD.doc'),
            ('CCCD cũ / CMND cũ', 'Bản gốc để thu hồi khi cấp mới', True, 'original', 1),
        ],
    },
    # ── Giấy phép lái xe ─────────────────────────────────────────────────────
    'cap_gplx_b1': {
        'name': 'Cấp giấy phép lái xe hạng B1 (lần đầu)',
        'code': '2.001095',
        'category': 'civil',
        'fee': 135000,
        'fee_note': '135.000 đồng (theo Thông tư 296/2016/TT-BTC)',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc sau khi hoàn thành thi sát hạch',
        'legal_basis': [
            'Luật Giao thông đường bộ 2008 (Luật số 23/2008/QH12)',
            'Thông tư số 12/2017/TT-BGTVT ngày 15/04/2017',
            'Thông tư 05/2024/TT-BGTVT (sửa đổi)',
        ],
        'implementing_level': 'province',
        'agency': 'Sở Giao thông Vận tải (qua Trung tâm Đào tạo, sát hạch lái xe)',
        'requirements': [
            ('Đơn đề nghị cấp giấy phép lái xe (mẫu 3, phụ lục 29)', 'Điền đầy đủ, ký tên', True, 'original', 0),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'original', 1),
            ('Giấy khám sức khỏe lái xe', 'Do cơ sở y tế được Bộ Y tế cho phép cấp; có giá trị trong 06 tháng; hạng B1 theo mẫu 01/GPLX', True, 'original', 2, 'mau-giay-kham-suc-khoe-lai-xe.doc'),
            ('Ảnh 3×4 cm (02 ảnh)', 'Ảnh nền trắng, chụp trong vòng 06 tháng', True, 'original', 3),
            ('Giấy chứng nhận đào tạo lái xe', 'Do cơ sở đào tạo được cấp phép cấp', True, 'original', 4),
        ],
    },
    'doi_gplx': {
        'name': 'Cấp đổi giấy phép lái xe do hết hạn',
        'code': '2.001096',
        'category': 'civil',
        'fee': 135000,
        'fee_note': '135.000 đồng',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc',
        'legal_basis': [
            'Thông tư số 12/2017/TT-BGTVT',
            'Thông tư 05/2024/TT-BGTVT',
        ],
        'implementing_level': 'province',
        'agency': 'Sở Giao thông Vận tải',
        'requirements': [
            ('Đơn đề nghị cấp lại/cấp đổi GPLX (mẫu 3, phụ lục 29)', 'Điền đầy đủ', True, 'original', 0),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'original', 1),
            ('Giấy phép lái xe cũ', 'Bản gốc để thu hồi', True, 'original', 2),
            ('Giấy khám sức khỏe lái xe', 'Trong hạn 06 tháng', True, 'original', 3, 'mau-giay-kham-suc-khoe-lai-xe.doc'),
            ('Ảnh 3×4 cm (02 ảnh)', 'Chụp trong 06 tháng, nền trắng', True, 'original', 4),
        ],
    },
    # ── Đất đai ───────────────────────────────────────────────────────────────
    'chuyen_nhuong_qsdd': {
        'name': 'Đăng ký, cấp Giấy chứng nhận quyền sử dụng đất do chuyển nhượng',
        'code': '1.002204',
        'category': 'land',
        'fee': 0,
        'fee_note': 'Lệ phí trước bạ: 0,5% giá trị QSDĐ; Phí công chứng theo Thông tư 257/2016/TT-BTC; Phí cấp GCN: 100.000đ/lần',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Đất đai 2024 (Luật số 31/2024/QH15)',
            'Nghị định số 43/2014/NĐ-CP (sửa đổi bởi NĐ 148/2020)',
            'Nghị định 10/2023/NĐ-CP',
            'Thông tư 09/2021/TT-BTNMT',
        ],
        'implementing_level': 'district',
        'agency': 'Văn phòng Đăng ký đất đai (thuộc Sở TNMT); UBND cấp huyện',
        'requirements': [
            ('Đơn đăng ký biến động đất đai (Mẫu 09/ĐK)', 'Điền đầy đủ theo mẫu của Bộ TNMT', True, 'original', 0, 'mau-don-dang-ky-bien-dong-dat-dai.doc'),
            ('CCCD/Căn cước công dân hai bên', 'Bản gốc + 01 bản sao mỗi người', True, 'certified_copy', 1),
            ('Giấy chứng nhận QSDĐ (Sổ đỏ/Sổ hồng)', 'Bản gốc để đăng ký sang tên', True, 'original', 2),
            ('Hợp đồng chuyển nhượng QSDĐ', 'Bản chính có công chứng/chứng thực (tại Văn phòng công chứng)', True, 'certified_copy', 3),
            ('Tờ khai lệ phí trước bạ (Mẫu 01/LPTB)', 'Theo mẫu của cơ quan thuế', True, 'original', 4, 'mau-to-khai-le-phi-truoc-ba.docx'),
            ('Biên lai nộp thuế thu nhập cá nhân / Giấy xác nhận miễn thuế', 'Từ cơ quan thuế', True, 'original', 5),
            ('Chứng từ thực hiện nghĩa vụ tài chính (nếu có)', 'Biên lai nộp tiền sử dụng đất, lệ phí trước bạ', False, 'copy', 6),
        ],
    },
    'cap_gcn_dat': {
        'name': 'Đăng ký đất đai lần đầu (cấp Giấy chứng nhận QSDĐ)',
        'code': '1.004006',
        'category': 'land',
        'fee': 100000,
        'fee_note': 'Lệ phí cấp GCN: 100.000đ (hộ gia đình); Thuế sử dụng đất phi nông nghiệp tùy diện tích',
        'processing_days': 30,
        'processing_note': '30 ngày làm việc (khu vực nông thôn: 40 ngày)',
        'legal_basis': [
            'Luật Đất đai 2024',
            'Nghị định 43/2014/NĐ-CP và các văn bản sửa đổi',
        ],
        'implementing_level': 'district',
        'agency': 'Văn phòng Đăng ký đất đai; UBND cấp huyện',
        'requirements': [
            ('Đơn đăng ký, cấp Giấy chứng nhận (Mẫu 04a/ĐK)', 'Điền đầy đủ theo mẫu', True, 'original', 0, 'mau-don-cap-gcnqsdd-so-do.docx'),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'certified_copy', 1),
            ('Một trong các giấy tờ về quyền sử dụng đất', 'Sổ hộ khẩu cũ, quyết định giao đất, biên lai thuế đất, giấy tờ mua bán đất từ trước 2004 có xác nhận...', True, 'copy', 2),
            ('Trích lục bản đồ địa chính thửa đất', 'Do Văn phòng ĐKDD cấp', True, 'original', 3),
            ('Tờ khai thuế sử dụng đất phi nông nghiệp (nếu áp dụng)', 'Theo mẫu cơ quan thuế', False, 'original', 4),
        ],
    },
    # ── Xây dựng ──────────────────────────────────────────────────────────────
    'cap_phep_xay_dung': {
        'name': 'Cấp giấy phép xây dựng nhà ở riêng lẻ tại đô thị',
        'code': '1.001086',
        'category': 'construction',
        'fee': 0,
        'fee_note': 'Lệ phí cấp phép xây dựng theo quy định HĐND tỉnh (khoảng 100.000-500.000đ tùy công trình)',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'legal_basis': [
            'Luật Xây dựng 2014 (sửa đổi 2020)',
            'Nghị định số 15/2021/NĐ-CP ngày 03/3/2021',
            'Thông tư 09/2021/TT-BXD',
        ],
        'implementing_level': 'district',
        'agency': 'UBND cấp huyện (Phòng Quản lý Đô thị / Phòng Kinh tế - Hạ tầng)',
        'requirements': [
            ('Đơn đề nghị cấp giấy phép xây dựng (Mẫu số 01, phụ lục II NĐ15)', 'Điền đầy đủ thông tin, ký tên chủ đầu tư', True, 'original', 0, 'mau-don-xin-cap-phep-xay-dung.docx'),
            ('CCCD/Căn cước công dân chủ đầu tư', 'Bản gốc + 01 bản sao', True, 'certified_copy', 1),
            ('Giấy tờ chứng minh quyền sử dụng đất', 'Sổ đỏ/Sổ hồng (bản sao công chứng) hoặc hợp đồng thuê đất', True, 'certified_copy', 2),
            ('Hồ sơ thiết kế xây dựng (02 bộ)', 'Gồm: bản vẽ mặt bằng, mặt đứng, mặt cắt, sơ đồ vị trí; được lập bởi đơn vị tư vấn có tư cách pháp nhân', True, 'original', 3),
            ('Bản vẽ sơ đồ tổng mặt bằng', 'Thể hiện vị trí công trình so với các công trình lân cận', True, 'original', 4),
            ('Văn bản phê duyệt thiết kế của cơ quan có thẩm quyền (nếu cần)', 'Đối với công trình ảnh hưởng PCCC, môi trường', False, 'copy', 5),
        ],
    },
    # ── Kinh doanh ────────────────────────────────────────────────────────────
    'dang_ky_ho_kinh_doanh': {
        'name': 'Đăng ký thành lập hộ kinh doanh',
        'code': '2.000214',
        'category': 'business',
        'fee': 100000,
        'fee_note': '100.000 đồng/lần (theo Thông tư 215/2016/TT-BTC)',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Doanh nghiệp 2020 (Luật số 59/2020/QH14)',
            'Nghị định số 01/2021/NĐ-CP ngày 04/01/2021',
            'Thông tư 01/2021/TT-BKHĐT',
        ],
        'implementing_level': 'district',
        'agency': 'Phòng Tài chính - Kế hoạch UBND cấp huyện',
        'requirements': [
            ('Giấy đề nghị đăng ký hộ kinh doanh (Phụ lục III-1, NĐ01/2021)', 'Điền đầy đủ, chủ hộ kinh doanh ký tên; lấy tại Phòng TC-KH hoặc tải online', True, 'original', 0, 'mau-giay-de-nghi-dang-ky-ho-kinh-doanh.docx'),
            ('CCCD/Căn cước công dân chủ hộ kinh doanh', 'Bản gốc + 01 bản sao', True, 'certified_copy', 1),
            ('Danh sách thành viên hộ kinh doanh (nếu có từ 02 thành viên trở lên)', 'Theo mẫu', False, 'original', 2),
            ('Giấy tờ chứng minh địa điểm kinh doanh hợp pháp', 'Hợp đồng thuê mặt bằng (công chứng) hoặc giấy tờ nhà sở hữu', True, 'certified_copy', 3),
        ],
    },
    'dang_ky_cong_ty_tnhh': {
        'name': 'Đăng ký thành lập Công ty TNHH một thành viên',
        'code': '1.000956',
        'category': 'business',
        'fee': 50000,
        'fee_note': '50.000 đồng nếu nộp hồ sơ giấy; miễn phí nếu đăng ký trực tuyến qua Cổng đăng ký quốc gia',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Doanh nghiệp 2020',
            'Nghị định số 01/2021/NĐ-CP',
            'Thông tư 01/2021/TT-BKHĐT',
        ],
        'implementing_level': 'province',
        'agency': 'Sở Kế hoạch và Đầu tư (Phòng Đăng ký kinh doanh)',
        'requirements': [
            ('Giấy đề nghị đăng ký doanh nghiệp (Phụ lục I-1, NĐ01/2021)', 'Người đại diện pháp luật ký tên', True, 'original', 0, 'mau-giay-de-nghi-dang-ky-doanh-nghiep.docx'),
            ('Điều lệ công ty', 'Người đại diện pháp luật ký từng trang', True, 'original', 1),
            ('CCCD/Căn cước công dân chủ sở hữu', 'Bản sao không cần công chứng', True, 'copy', 2),
            ('Giấy tờ pháp lý cá nhân người đại diện pháp luật', 'CCCD hoặc hộ chiếu còn hiệu lực, bản sao', True, 'copy', 3),
            ('Văn bản ủy quyền (nếu người nộp không phải chủ sở hữu/đại diện)', 'Có công chứng/chứng thực', False, 'certified_copy', 4),
        ],
    },
    # ── Bảo hiểm xã hội ──────────────────────────────────────────────────────
    'cap_so_bhxh': {
        'name': 'Cấp sổ bảo hiểm xã hội',
        'code': '1.003403',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 10,
        'processing_note': '10 ngày kể từ khi nhận đủ hồ sơ (qua đơn vị sử dụng lao động)',
        'legal_basis': [
            'Luật BHXH số 58/2014/QH13',
            'Quyết định số 505/QĐ-BHXH ngày 27/3/2020',
        ],
        'implementing_level': 'district',
        'agency': 'BHXH cấp huyện (qua đơn vị sử dụng lao động hoặc tự nộp)',
        'requirements': [
            ('Tờ khai tham gia, điều chỉnh thông tin BHXH, BHYT (Mẫu TK1-TS)', 'Điền đầy đủ, ký tên', True, 'original', 0, 'mau-to-khai-tham-gia-bhxh-bhyt.doc'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Giấy khai sinh (nếu chưa có CCCD)', 'Bản sao có chứng thực', False, 'certified_copy', 2),
        ],
    },
    'huong_bhxh_mot_lan': {
        'name': 'Giải quyết hưởng bảo hiểm xã hội một lần',
        'code': '1.003459',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'legal_basis': [
            'Luật BHXH 2014',
            'Nghị định 115/2015/NĐ-CP',
            'Thông tư 59/2015/TT-BLĐTBXH',
        ],
        'implementing_level': 'district',
        'agency': 'BHXH cấp huyện',
        'requirements': [
            ('Đơn đề nghị hưởng BHXH một lần (Mẫu 14-HSB)', 'Người lao động ký', True, 'original', 0),
            ('Sổ bảo hiểm xã hội', 'Bản gốc', True, 'original', 1),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 2),
            ('Tài khoản ngân hàng cá nhân', 'Số tài khoản đứng tên người yêu cầu', True, 'original', 3),
        ],
    },
    # ── Giáo dục ─────────────────────────────────────────────────────────────
    'cong_nhan_bang': {
        'name': 'Công nhận văn bằng, chứng chỉ do cơ sở giáo dục nước ngoài cấp',
        'code': '1.003898',
        'category': 'education',
        'fee': 600000,
        'fee_note': '600.000 đồng (theo Thông tư 185/2016/TT-BTC)',
        'processing_days': 30,
        'processing_note': '30 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Giáo dục 2019',
            'Thông tư 13/2021/TT-BGDĐT ngày 15/4/2021',
        ],
        'implementing_level': 'province',
        'agency': 'Sở Giáo dục và Đào tạo',
        'requirements': [
            ('Đơn đề nghị công nhận văn bằng', 'Theo mẫu quy định', True, 'original', 0),
            ('Bản sao văn bằng gốc', 'Có hợp pháp hóa lãnh sự (Apostille) và bản dịch công chứng tiếng Việt', True, 'certified_copy', 1),
            ('Bảng điểm học tập', 'Bản sao có hợp pháp hóa lãnh sự và dịch công chứng', True, 'certified_copy', 2),
            ('CCCD/Căn cước công dân hoặc hộ chiếu', 'Bản sao', True, 'copy', 3),
        ],
    },
    # ── Y tế ──────────────────────────────────────────────────────────────────
    'cap_giay_kham_suc_khoe': {
        'name': 'Khám và cấp giấy chứng nhận sức khỏe',
        'code': 'y_te_001',
        'category': 'health',
        'fee': 80000,
        'fee_note': '80.000 - 120.000 đồng tùy cơ sở khám (theo BYT quy định)',
        'processing_days': 1,
        'processing_note': 'Trong ngày làm việc, trả kết quả sau 2-4 giờ',
        'legal_basis': [
            'Thông tư 14/2013/TT-BYT ngày 06/5/2013',
            'Thông tư 32/2023/TT-BYT',
        ],
        'implementing_level': 'province',
        'agency': 'Cơ sở y tế được Bộ Y tế cho phép (bệnh viện, phòng khám đa khoa)',
        'requirements': [
            ('CCCD/Căn cước công dân', 'Bản gốc để xác minh', True, 'original', 0),
            ('Ảnh 3×4 cm (02 ảnh)', 'Chụp trong 06 tháng, nền trắng', True, 'original', 1),
            ('Lệ phí khám', 'Theo quy định của cơ sở khám', True, 'original', 2),
        ],
    },
    # ── Tư pháp ───────────────────────────────────────────────────────────────
    'cap_phieu_lltp': {
        'name': 'Cấp Phiếu lý lịch tư pháp số 1',
        'code': '2.000413',
        'category': 'justice',
        'fee': 200000,
        'fee_note': '200.000 đồng (theo Nghị định 113/2013/NĐ-CP)',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc; 15 ngày nếu có xác minh thêm',
        'legal_basis': [
            'Luật Lý lịch tư pháp 2009 (Luật số 28/2009/QH12)',
            'Nghị định số 111/2010/NĐ-CP',
        ],
        'implementing_level': 'province',
        'agency': 'Sở Tư pháp (cá nhân có hộ khẩu / cư trú tại Thanh Hóa)',
        'requirements': [
            ('Tờ khai yêu cầu cấp Phiếu LLTP (Mẫu số 03/2013/TT-BTP)', 'Người yêu cầu ký tên; lấy tại Sở Tư pháp hoặc tải online', True, 'original', 0, 'mau-phieu-ly-lich-tu-phap-so1.docx'),
            ('CCCD/Căn cước công dân', 'Bản gốc để đối chiếu + 01 bản sao', True, 'certified_copy', 1),
            ('Lệ phí (200.000đ)', 'Nộp tại quầy tiếp nhận hoặc chuyển khoản', True, 'original', 2),
            ('Giấy ủy quyền (nếu ủy quyền cho người khác nộp/nhận)', 'Có công chứng hoặc chứng thực', False, 'certified_copy', 3),
        ],
    },
    'cong_chung_hop_dong': {
        'name': 'Công chứng hợp đồng mua bán, chuyển nhượng bất động sản',
        'code': 'tp_cc_001',
        'category': 'justice',
        'fee': 0,
        'fee_note': 'Phí công chứng theo biểu phí Thông tư 257/2016/TT-BTC: 0,1% giá trị TS (tối thiểu 50.000đ, tối đa 70 triệu đồng)',
        'processing_days': 2,
        'processing_note': 'Trong ngày hoặc 01-02 ngày làm việc (tùy phức tạp của hồ sơ)',
        'legal_basis': [
            'Luật Công chứng 2014 (Luật số 53/2014/QH13)',
            'Nghị định 29/2015/NĐ-CP',
            'Thông tư 257/2016/TT-BTC',
        ],
        'implementing_level': 'district',
        'agency': 'Phòng công chứng số 1, 2, 3 Thanh Hóa / Văn phòng công chứng tư',
        'requirements': [
            ('CCCD/Căn cước công dân hai bên (bên bán và bên mua)', 'Bản gốc + 01 bản sao mỗi người', True, 'certified_copy', 0),
            ('Giấy chứng nhận QSDĐ/Quyền sở hữu nhà (Sổ đỏ/Sổ hồng)', 'Bản gốc', True, 'original', 1),
            ('Giấy đăng ký kết hôn (nếu đã kết hôn)', 'Bản sao để xác định sở hữu chung/riêng', False, 'copy', 2),
            ('Giấy khai sinh (nếu cần xác định tuổi)', 'Bản sao', False, 'copy', 3),
        ],
    },
    # ── Thuế ─────────────────────────────────────────────────────────────────
    'dang_ky_ma_so_thue': {
        'name': 'Đăng ký thuế lần đầu đối với cá nhân',
        'code': '1.001169',
        'category': 'tax',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ',
        'legal_basis': [
            'Luật Quản lý thuế 2019 (Luật số 38/2019/QH14)',
            'Thông tư 105/2020/TT-BTC ngày 3/12/2020',
        ],
        'implementing_level': 'district',
        'agency': 'Chi cục Thuế khu vực / Cục Thuế tỉnh',
        'requirements': [
            ('Tờ khai đăng ký thuế (Mẫu 05-ĐK-TCT)', 'Điền đầy đủ thông tin cá nhân', True, 'original', 0),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PHẦN MỞ RỘNG — 38 thủ tục bổ sung (khớp với file Word mẫu)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Hộ tịch bổ sung ──────────────────────────────────────────────────────
    'dang_ky_lai_khai_sinh': {
        'name': 'Đăng ký lại khai sinh',
        'code': '2.000730',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc',
        'legal_basis': ['Luật Hộ tịch 2014', 'Nghị định 123/2015/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký lại khai sinh', 'Điền đầy đủ theo mẫu; lấy tại UBND hoặc tải online', True, 'original', 0, 'mau-to-khai-dang-ky-lai-khai-sinh.docx'),
            ('CCCD/Căn cước công dân của người yêu cầu', 'Bản gốc còn hiệu lực', True, 'original', 1),
            ('Giấy tờ chứng minh về nội dung khai sinh', 'Sổ hộ khẩu, học bạ, hồ sơ khám bệnh... có thể hiện năm sinh, họ tên', True, 'copy', 2),
        ],
    },
    'nhan_cha_me_con': {
        'name': 'Đăng ký nhận cha, mẹ, con',
        'code': '2.000637',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc',
        'legal_basis': ['Luật Hộ tịch 2014', 'Luật HN&GĐ 2014'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký nhận cha, mẹ, con', 'Điền đầy đủ, ký tên các bên', True, 'original', 0, 'mau-to-khai-nhan-cha-me-con.doc'),
            ('CCCD/Căn cước công dân các bên', 'Bản gốc còn hiệu lực', True, 'original', 1),
            ('Giấy khai sinh của người con', 'Bản chính', True, 'original', 2),
            ('Văn bản cam kết nhận cha/mẹ/con (nếu cần)', 'Có xác nhận', False, 'original', 3),
        ],
    },
    'cai_chinh_ho_tich': {
        'name': 'Thay đổi, cải chính, bổ sung hộ tịch',
        'code': '2.000739',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc',
        'legal_basis': ['Luật Hộ tịch 2014', 'Nghị định 123/2015/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai thay đổi, cải chính, bổ sung thông tin hộ tịch', 'Điền đầy đủ nội dung thay đổi', True, 'original', 0, 'mau-to-khai-thay-doi-cai-chinh-ho-tich.doc'),
            ('CCCD/Căn cước công dân', 'Bản gốc', True, 'original', 1),
            ('Giấy tờ hộ tịch có sai sót cần cải chính', 'Bản gốc để đối chiếu', True, 'original', 2),
            ('Giấy tờ chứng minh nội dung đề nghị thay đổi', 'Học bạ, sổ hộ khẩu, hồ sơ y tế...', True, 'copy', 3),
        ],
    },
    'cap_ban_sao_ho_tich': {
        'name': 'Cấp bản sao trích lục hộ tịch',
        'code': '2.000955',
        'category': 'civil',
        'fee': 8000,
        'fee_note': '8.000 đồng/bản sao (theo Thông tư 85/2019/TT-BTC)',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc; ngay trong ngày nếu hồ sơ đã lưu tại nơi tiếp nhận',
        'legal_basis': ['Luật Hộ tịch 2014', 'Nghị định 123/2015/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn nơi đăng ký hộ tịch',
        'requirements': [
            ('Tờ khai đề nghị cấp bản sao trích lục hộ tịch', 'Điền thông tin người yêu cầu và loại hộ tịch cần cấp', True, 'original', 0, 'mau-to-khai-cap-ban-sao-trich-luc-ho-tich.docx'),
            ('CCCD/Căn cước công dân', 'Bản gốc để đối chiếu', True, 'original', 1),
        ],
    },
    'dang_ky_giam_ho': {
        'name': 'Đăng ký giám hộ',
        'code': '2.000645',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc',
        'legal_basis': ['Luật Hộ tịch 2014', 'Bộ luật Dân sự 2015'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đăng ký giám hộ', 'Điền đầy đủ thông tin người giám hộ và người được giám hộ', True, 'original', 0, 'mau-to-khai-dang-ky-giam-ho.docx'),
            ('CCCD/Căn cước công dân người giám hộ', 'Bản gốc còn hiệu lực', True, 'original', 1),
            ('Giấy tờ chứng minh tư cách giám hộ', 'Giấy khai sinh, quyết định tòa án... (nếu có)', False, 'copy', 2),
        ],
    },

    # ── Cư trú & Căn cước bổ sung ─────────────────────────────────────────────
    'dang_ky_xe_co_gioi': {
        'name': 'Đăng ký xe mô tô, xe gắn máy',
        'code': '2.000401',
        'category': 'civil',
        'fee': 150000,
        'fee_note': '150.000 đồng lệ phí đăng ký xe (xe mô tô); xe ô tô cao hơn theo quy định',
        'processing_days': 2,
        'processing_note': '02 ngày làm việc kể từ khi đủ hồ sơ',
        'legal_basis': ['Thông tư 24/2023/TT-BCA', 'Nghị định 71/2012/NĐ-CP'],
        'implementing_level': 'district',
        'agency': 'Công an cấp huyện (Đội CSGT - TT)',
        'requirements': [
            ('Giấy khai đăng ký xe (Mẫu số 01)', 'Điền đầy đủ thông tin xe và chủ xe', True, 'original', 0, 'mau-khai-dang-ky-xe-co-gioi.docx'),
            ('CCCD/Căn cước công dân chủ xe', 'Bản gốc + 01 bản sao', True, 'certified_copy', 1),
            ('Hóa đơn mua bán xe / Tờ khai nhập khẩu', 'Bản gốc (xe nhập khẩu: tờ khai hải quan)', True, 'original', 2),
            ('Chứng từ nộp thuế trước bạ', 'Biên lai nộp lệ phí trước bạ từ Chi cục thuế', True, 'original', 3),
            ('Giấy tờ chuyển quyền sở hữu (nếu mua lại)', 'Giấy bán xe có công chứng', False, 'certified_copy', 4),
        ],
    },

    # ── Hôn nhân bổ sung ──────────────────────────────────────────────────────
    'ly_hon_thuan_tinh': {
        'name': 'Yêu cầu công nhận thuận tình ly hôn',
        'code': 'tp_lyh_001',
        'category': 'justice',
        'fee': 300000,
        'fee_note': '300.000 đồng án phí sơ thẩm (theo Nghị quyết 326/2016/UBTVQH14)',
        'processing_days': 15,
        'processing_note': '15 ngày sau khi thụ lý; Tòa án có thể hòa giải thêm',
        'legal_basis': ['Luật HN&GĐ 2014', 'Bộ luật TTDS 2015'],
        'implementing_level': 'district',
        'agency': 'Tòa án nhân dân cấp huyện nơi bị đơn cư trú',
        'requirements': [
            ('Đơn yêu cầu công nhận thuận tình ly hôn', 'Hai vợ chồng cùng ký; ghi rõ thỏa thuận về tài sản, con cái', True, 'original', 0, 'mau-don-thuan-tinh-ly-hon.docx'),
            ('CCCD/Căn cước công dân hai bên', 'Bản sao', True, 'copy', 1),
            ('Giấy đăng ký kết hôn', 'Bản chính', True, 'original', 2),
            ('Giấy khai sinh con chung (nếu có)', 'Bản sao để xác định quyền nuôi con', False, 'copy', 3),
            ('Giấy tờ về tài sản chung (nếu có tranh chấp)', 'Sổ đỏ, hợp đồng mua bán...', False, 'copy', 4),
        ],
    },

    # ── Tư pháp bổ sung ──────────────────────────────────────────────────────
    'cap_lltp_so2': {
        'name': 'Cấp Phiếu lý lịch tư pháp số 2',
        'code': '2.000414',
        'category': 'justice',
        'fee': 200000,
        'fee_note': '200.000 đồng',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc',
        'legal_basis': ['Luật Lý lịch tư pháp 2009', 'Nghị định 111/2010/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Sở Tư pháp (cơ quan, tổ chức yêu cầu)',
        'requirements': [
            ('Phiếu lý lịch tư pháp số 2', 'Theo mẫu; do cơ quan, tổ chức yêu cầu điền và nộp', True, 'original', 0, 'mau-phieu-ly-lich-tu-phap-so2.doc'),
            ('Văn bản ủy quyền của tổ chức', 'Nếu ủy quyền cho cá nhân nộp/nhận', False, 'certified_copy', 1),
            ('CCCD/Căn cước của đối tượng tra cứu', 'Bản sao', True, 'copy', 2),
        ],
    },
    'cap_ho_chieu': {
        'name': 'Cấp hộ chiếu phổ thông trong nước',
        'code': '2.001871',
        'category': 'justice',
        'fee': 200000,
        'fee_note': '200.000 đồng (Thông tư 219/2016/TT-BTC)',
        'processing_days': 8,
        'processing_note': '08 ngày làm việc; cấp nhanh 02 ngày (thêm phí)',
        'legal_basis': ['Luật Xuất cảnh, Nhập cảnh 2019', 'Nghị định 136/2007/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Phòng Quản lý Xuất nhập cảnh — Công an tỉnh Thanh Hóa',
        'requirements': [
            ('Tờ khai đề nghị cấp hộ chiếu phổ thông', 'Điền đầy đủ, ký tên; khai trực tuyến trên cổng dichvucong.gov.vn hoặc nộp giấy', True, 'original', 0, 'mau-to-khai-cap-ho-chieu.docx'),
            ('CCCD/Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
            ('Ảnh 4×6 cm (02 ảnh)', 'Nền trắng, không đeo kính, chụp trong 06 tháng', True, 'original', 2),
            ('Hộ chiếu cũ (nếu đổi/cấp lại)', 'Bản gốc để thu hồi', False, 'original', 3),
        ],
    },

    # ── Đất đai bổ sung ──────────────────────────────────────────────────────
    'cap_doi_gcnqsdd': {
        'name': 'Cấp đổi Giấy chứng nhận quyền sử dụng đất',
        'code': '1.004002',
        'category': 'land',
        'fee': 50000,
        'fee_note': 'Lệ phí đo đạc và cấp đổi theo quy định HĐND tỉnh',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc',
        'legal_basis': ['Luật Đất đai 2024', 'Nghị định 43/2014/NĐ-CP và các văn bản sửa đổi'],
        'implementing_level': 'district',
        'agency': 'Văn phòng Đăng ký đất đai; UBND cấp huyện',
        'requirements': [
            ('Đơn đề nghị cấp đổi Giấy chứng nhận QSDĐ (Mẫu 18)', 'Điền đầy đủ lý do đề nghị cấp đổi', True, 'original', 0, 'mau-don-cap-doi-gcnqsdd-so-do.docx'),
            ('Giấy chứng nhận QSDĐ cũ', 'Bản gốc để thu hồi', True, 'original', 1),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'certified_copy', 2),
        ],
    },
    'tach_thua_dat': {
        'name': 'Tách thửa, hợp thửa đất',
        'code': '1.004003',
        'category': 'land',
        'fee': 50000,
        'fee_note': 'Phí đo đạc địa chính theo quy định',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'legal_basis': ['Luật Đất đai 2024', 'Thông tư 09/2021/TT-BTNMT'],
        'implementing_level': 'district',
        'agency': 'Văn phòng Đăng ký đất đai thuộc Sở TNMT',
        'requirements': [
            ('Đơn xin tách thửa / hợp thửa đất', 'Ghi rõ diện tích tách/hợp, lý do', True, 'original', 0, 'mau-don-tach-thua-hop-thua-dat.docx'),
            ('Giấy chứng nhận QSDĐ gốc', 'Bản gốc', True, 'original', 1),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'certified_copy', 2),
            ('Sơ đồ thửa đất (do đơn vị đo đạc cấp phép lập)', 'Thể hiện ranh giới các thửa sau tách/hợp', True, 'original', 3),
        ],
    },
    'giao_dat_cho_thue': {
        'name': 'Giao đất, cho thuê đất, cho phép chuyển mục đích sử dụng đất',
        'code': '1.004008',
        'category': 'land',
        'fee': 0,
        'fee_note': 'Tiền sử dụng đất / tiền thuê đất theo quyết định của UBND tỉnh',
        'processing_days': 20,
        'processing_note': '20 ngày làm việc (nông thôn 30 ngày)',
        'legal_basis': ['Luật Đất đai 2024', 'Nghị định 43/2014/NĐ-CP'],
        'implementing_level': 'district',
        'agency': 'UBND cấp huyện; Sở TNMT (đất cấp tỉnh)',
        'requirements': [
            ('Đơn xin giao đất / cho thuê đất / chuyển mục đích SDĐ (Mẫu 01)', 'Điền đầy đủ mục đích sử dụng mới', True, 'original', 0, 'mau-don-giao-dat-cho-thue-dat-chuyen-muc-dich.doc'),
            ('CCCD/Căn cước công dân hoặc Giấy phép kinh doanh', 'Bản sao', True, 'copy', 1),
            ('Hồ sơ dự án / phương án sử dụng đất', 'Nếu xin giao đất cho dự án đầu tư', False, 'original', 2),
            ('Giấy chứng nhận QSDĐ hiện trạng (nếu chuyển mục đích)', 'Bản gốc', False, 'original', 3),
        ],
    },

    # ── Thuế bổ sung ──────────────────────────────────────────────────────────
    'khai_thue_tndn': {
        'name': 'Khai thuế thu nhập doanh nghiệp',
        'code': 'tax_tndn_001',
        'category': 'tax',
        'fee': 0,
        'fee_note': 'Miễn phí khai báo; thuế TNDN 20% lợi nhuận tính thuế',
        'processing_days': 0,
        'processing_note': 'Nộp tờ khai theo kỳ (tháng/quý/năm); không có thời gian chờ duyệt',
        'legal_basis': ['Luật Thuế TNDN 2008 (sửa đổi 2014)', 'Thông tư 80/2021/TT-BTC'],
        'implementing_level': 'district',
        'agency': 'Chi cục Thuế khu vực / Cục Thuế tỉnh',
        'requirements': [
            ('Tờ khai thuế thu nhập doanh nghiệp (Mẫu 04/TNDN)', 'Điền đủ doanh thu, chi phí, lợi nhuận kỳ khai thuế', True, 'original', 0, 'mau-to-khai-thue-thu-nhap-doanh-nghiep.doc'),
            ('Báo cáo tài chính (cuối năm)', 'Bảng cân đối kế toán, kết quả hoạt động kinh doanh', False, 'copy', 1),
        ],
    },
    'khai_thue_mon_bai': {
        'name': 'Khai lệ phí môn bài',
        'code': 'tax_mb_001',
        'category': 'tax',
        'fee': 0,
        'fee_note': 'Lệ phí môn bài: 300.000 - 3.000.000đ/năm tùy vốn điều lệ',
        'processing_days': 0,
        'processing_note': 'Nộp tờ khai khi thành lập, trước ngày 31/01 năm tiếp theo',
        'legal_basis': ['Nghị định 139/2016/NĐ-CP', 'Thông tư 302/2016/TT-BTC'],
        'implementing_level': 'district',
        'agency': 'Chi cục Thuế khu vực',
        'requirements': [
            ('Tờ khai lệ phí môn bài', 'Điền thông tin đơn vị và mức vốn', True, 'original', 0, 'mau-to-khai-thue-mon-bai.doc'),
            ('Giấy chứng nhận đăng ký doanh nghiệp / hộ kinh doanh', 'Bản sao', True, 'copy', 1),
        ],
    },
    'hoan_thue': {
        'name': 'Đề nghị hoàn trả khoản thu NSNN (hoàn thuế)',
        'code': 'tax_ht_001',
        'category': 'tax',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 40,
        'processing_note': '06 ngày làm việc (hoàn trước-kiểm sau); 40 ngày (kiểm trước-hoàn sau)',
        'legal_basis': ['Luật Quản lý thuế 2019', 'Thông tư 80/2021/TT-BTC'],
        'implementing_level': 'district',
        'agency': 'Cục Thuế tỉnh / Chi cục Thuế',
        'requirements': [
            ('Giấy đề nghị hoàn trả khoản thu NSNN (Mẫu 01/NHT)', 'Ghi rõ số tiền đề nghị hoàn, lý do, tài khoản nhận', True, 'original', 0, 'mau-giay-de-nghi-hoan-thue.doc'),
            ('Hồ sơ chứng minh được hoàn thuế', 'Hóa đơn, hợp đồng, tờ khai thuế liên quan', True, 'copy', 1),
            ('CCCD/Căn cước công dân hoặc Giấy phép kinh doanh', 'Bản sao', True, 'copy', 2),
        ],
    },

    # ── Y tế bổ sung ──────────────────────────────────────────────────────────
    'cap_gcn_suc_khoe': {
        'name': 'Cấp giấy chứng nhận sức khỏe',
        'code': 'yt_skh_001',
        'category': 'health',
        'fee': 80000,
        'fee_note': '80.000 - 150.000 đồng tùy cơ sở y tế và loại giấy',
        'processing_days': 1,
        'processing_note': 'Trong ngày làm việc',
        'legal_basis': ['Thông tư 14/2013/TT-BYT', 'Thông tư 32/2023/TT-BYT'],
        'implementing_level': 'district',
        'agency': 'Cơ sở khám, chữa bệnh được cấp phép',
        'requirements': [
            ('Đơn xin cấp giấy chứng nhận sức khỏe', 'Theo mẫu của cơ sở y tế; ghi rõ mục đích', True, 'original', 0, 'mau-don-cap-giay-chung-nhan-suc-khoe.doc'),
            ('CCCD/Căn cước công dân', 'Bản gốc để xác minh', True, 'original', 1),
            ('Ảnh 3×4 cm (02 ảnh)', 'Chụp trong 06 tháng, nền trắng', True, 'original', 2),
        ],
    },
    'yeu_cau_xet_nghiem': {
        'name': 'Đề nghị kiểm nghiệm / xét nghiệm mẫu sản phẩm',
        'code': 'yt_xn_001',
        'category': 'health',
        'fee': 0,
        'fee_note': 'Phí kiểm nghiệm theo quy định (tùy loại xét nghiệm)',
        'processing_days': 7,
        'processing_note': '07-15 ngày tùy loại kiểm nghiệm',
        'legal_basis': ['Luật Dược 2016', 'Luật ATTP 2010'],
        'implementing_level': 'province',
        'agency': 'Viện Kiểm nghiệm thuốc / Trung tâm kiểm nghiệm tỉnh',
        'requirements': [
            ('Phiếu yêu cầu kiểm nghiệm / xét nghiệm', 'Điền đầy đủ thông tin mẫu, chỉ tiêu cần kiểm', True, 'original', 0, 'mau-phieu-yeu-cau-xet-nghiem.doc'),
            ('Mẫu sản phẩm cần kiểm nghiệm', 'Đóng gói theo quy định, dán nhãn đầy đủ', True, 'original', 1),
            ('Tài liệu kỹ thuật của sản phẩm', 'Tiêu chuẩn áp dụng, phương pháp thử', False, 'copy', 2),
        ],
    },

    # ── BHXH & Lao động bổ sung ───────────────────────────────────────────────
    'tro_cap_tnld': {
        'name': 'Giải quyết hưởng chế độ tai nạn lao động, bệnh nghề nghiệp',
        'code': '1.003451',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày kể từ ngày nhận đủ hồ sơ hợp lệ',
        'legal_basis': ['Luật ATVSLĐ 2015', 'Luật BHXH 2014', 'Thông tư 28/2021/TT-BLĐTBXH'],
        'implementing_level': 'district',
        'agency': 'BHXH cấp huyện (qua đơn vị sử dụng lao động)',
        'requirements': [
            ('Đơn đề nghị hưởng chế độ TNLĐ/BNN (Mẫu 05A-HSB)', 'Người lao động ký, đơn vị xác nhận', True, 'original', 0, 'mau-05A-HSB-tro-cap-tai-nan-lao-dong.docx'),
            ('Hồ sơ hưởng chế độ TNLĐ/BNN (Mẫu 05-HSB)', 'Tổng hợp các giấy tờ liên quan', True, 'original', 1, 'mau-05-HSB-ho-so-tai-nan-lao-dong.doc'),
            ('Biên bản điều tra tai nạn lao động', 'Do đoàn điều tra lập', True, 'original', 2),
            ('Giấy ra viện / kết luận điều trị', 'Của cơ sở y tế điều trị', True, 'original', 3),
            ('Sổ bảo hiểm xã hội', 'Bản gốc', True, 'original', 4),
        ],
    },
    'cap_the_bhyt': {
        'name': 'Cấp lại, đổi thẻ bảo hiểm y tế',
        'code': '1.003421',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc',
        'legal_basis': ['Luật BHYT 2008 (sửa đổi 2014)', 'Quyết định 505/QĐ-BHXH'],
        'implementing_level': 'district',
        'agency': 'BHXH cấp huyện',
        'requirements': [
            ('Tờ khai đề nghị cấp thẻ BHYT', 'Điền thông tin cá nhân và lý do cấp lại', True, 'original', 0, 'mau-to-khai-cap-the-bao-hiem-y-te.docx'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Thẻ BHYT cũ (nếu còn)', 'Để thu hồi', False, 'original', 2),
        ],
    },
    'bao_tro_xa_hoi': {
        'name': 'Hưởng trợ cấp xã hội hàng tháng tại cộng đồng',
        'code': '1.001543',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'legal_basis': ['Nghị định 20/2021/NĐ-CP ngày 15/3/2021', 'Thông tư 02/2021/TT-BLĐTBXH'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã (tiếp nhận); UBND cấp huyện (phê duyệt)',
        'requirements': [
            ('Tờ khai đề nghị trợ cấp xã hội (Phụ lục NĐ 20)', 'Điền đầy đủ thông tin đối tượng hưởng trợ cấp', True, 'original', 0, 'mau-to-khai-bao-tro-xa-hoi-nd20.docx'),
            ('Hồ sơ xác nhận đối tượng thuộc diện hưởng', 'Giấy xác nhận khuyết tật, xác nhận hộ nghèo... tùy đối tượng', True, 'copy', 1),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 2),
        ],
    },
    'tro_cap_that_nghiep': {
        'name': 'Hưởng trợ cấp thất nghiệp',
        'code': '1.003428',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 20,
        'processing_note': '20 ngày làm việc kể từ ngày tiếp nhận hồ sơ',
        'legal_basis': ['Luật Việc làm 2013', 'Nghị định 28/2015/NĐ-CP', 'Thông tư 28/2015/TT-BLĐTBXH'],
        'implementing_level': 'province',
        'agency': 'Trung tâm Dịch vụ Việc làm tỉnh Thanh Hóa',
        'requirements': [
            ('Đơn đề nghị hưởng trợ cấp thất nghiệp (Mẫu số 03)', 'Điền đầy đủ; nộp trong vòng 03 tháng sau khi nghỉ việc', True, 'original', 0, 'mau-don-tro-cap-that-nghiep.docx'),
            ('CCCD/Căn cước công dân', 'Bản gốc + 01 bản sao', True, 'certified_copy', 1),
            ('Sổ bảo hiểm xã hội', 'Bản gốc có xác nhận của cơ quan BHXH', True, 'original', 2),
            ('Quyết định thôi việc / hợp đồng lao động hết hạn', 'Bản sao hoặc bản gốc', True, 'copy', 3),
        ],
    },
    'tro_cap_xa_hoi': {
        'name': 'Giải quyết trợ cấp xã hội đột xuất',
        'code': '1.001547',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 10,
        'processing_note': '10 ngày kể từ khi UBND nhận đủ hồ sơ',
        'legal_basis': ['Nghị định 20/2021/NĐ-CP', 'Quyết định 22/2013/QĐ-TTg'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã, phường, thị trấn',
        'requirements': [
            ('Tờ khai đề nghị trợ cấp xã hội đột xuất', 'Ghi rõ hoàn cảnh, mức đề nghị hỗ trợ', True, 'original', 0, 'mau-to-khai-tro-cap-xa-hoi.docx'),
            ('Biên bản xác nhận thiệt hại (hỏa hoạn, thiên tai...)', 'Do UBND cấp xã lập', False, 'original', 1),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 2),
        ],
    },
    'ky_ket_hop_dong_ld': {
        'name': 'Đề nghị ký kết hợp đồng lao động',
        'code': 'ld_hdld_001',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc kể từ ngày tiếp nhận',
        'legal_basis': ['Bộ luật Lao động 2019', 'Nghị định 145/2020/NĐ-CP'],
        'implementing_level': 'district',
        'agency': 'Đơn vị sử dụng lao động (công lập)',
        'requirements': [
            ('Đơn đề nghị ký kết hợp đồng lao động', 'Ghi rõ vị trí, thời hạn đề nghị ký hợp đồng', True, 'original', 0, 'mau-de-nghi-ky-ket-hop-dong-lao-dong.docx'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Văn bằng, chứng chỉ chuyên môn', 'Bản sao công chứng', True, 'certified_copy', 2),
            ('Phiếu lý lịch tư pháp số 1', 'Trong hạn 06 tháng', True, 'original', 3),
            ('Giấy khám sức khỏe', 'Trong hạn 12 tháng', True, 'original', 4),
        ],
    },

    # ── Giáo dục bổ sung ──────────────────────────────────────────────────────
    'xin_hoc_bong': {
        'name': 'Xét duyệt học bổng khuyến khích học tập',
        'code': 'gd_hb_001',
        'category': 'education',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày kể từ khi cơ sở giáo dục tiếp nhận hồ sơ',
        'legal_basis': ['Luật Giáo dục 2019', 'Thông tư 16/2018/TT-BGDĐT'],
        'implementing_level': 'district',
        'agency': 'Cơ sở giáo dục đào tạo (trường, đại học)',
        'requirements': [
            ('Đơn xin học bổng', 'Ghi rõ loại học bổng và thành tích học tập', True, 'original', 0, 'mau-don-xin-hoc-bong.docx'),
            ('Bảng điểm học kỳ / năm học gần nhất', 'Bản sao có xác nhận của nhà trường', True, 'copy', 1),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 2),
            ('Giấy tờ chứng minh hoàn cảnh khó khăn (nếu học bổng xã hội)', 'Hộ nghèo, cận nghèo, giấy xác nhận của địa phương', False, 'copy', 3),
        ],
    },
    'xin_viec_tuyen_dung': {
        'name': 'Đăng ký dự tuyển viên chức, công chức',
        'code': 'gd_xv_001',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Lệ phí dự tuyển theo quy định từng đơn vị (thường 500.000-700.000đ)',
        'processing_days': 30,
        'processing_note': '30 ngày xét duyệt hồ sơ; thi viết/phỏng vấn theo lịch riêng',
        'legal_basis': ['Luật Viên chức 2010 (sửa đổi 2019)', 'Nghị định 115/2020/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Đơn vị tuyển dụng / Sở Nội vụ',
        'requirements': [
            ('Đơn đăng ký dự tuyển (xin việc)', 'Ghi rõ vị trí và đơn vị đăng ký', True, 'original', 0, 'mau-don-xin-viec-du-tuyen.doc'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Văn bằng, chứng chỉ theo yêu cầu vị trí', 'Bản sao công chứng', True, 'certified_copy', 2),
            ('Giấy khám sức khỏe', 'Do cơ sở y tế được phép cấp', True, 'original', 3),
            ('Phiếu lý lịch tư pháp số 1', 'Trong hạn 06 tháng', True, 'original', 4),
            ('Sơ yếu lý lịch tự thuật', 'Có xác nhận của UBND cấp xã nơi cư trú', True, 'original', 5),
        ],
    },
    'chuyen_truong': {
        'name': 'Chuyển trường đối với học sinh phổ thông',
        'code': '2.000875',
        'category': 'education',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc kể từ khi nhận đủ hồ sơ',
        'legal_basis': ['Luật Giáo dục 2019', 'Thông tư 28/2020/TT-BGDĐT'],
        'implementing_level': 'district',
        'agency': 'Phòng GD&ĐT (THCS); Sở GD&ĐT (THPT)',
        'requirements': [
            ('Đơn xin chuyển trường', 'Phụ huynh/người giám hộ ký; ghi rõ lý do chuyển', True, 'original', 0, 'mau-don-xin-chuyen-truong-thcs.doc'),
            ('Học bạ (bản sao có chứng thực)', 'Xác nhận của trường cũ', True, 'certified_copy', 1),
            ('Giấy giới thiệu của trường cũ', 'Xác nhận hoàn thành năm học, không nợ học phí', True, 'original', 2),
            ('CCCD/Căn cước của phụ huynh', 'Bản sao', True, 'copy', 3),
        ],
    },
    'thoi_hoc': {
        'name': 'Thủ tục xin thôi học',
        'code': 'gd_thh_001',
        'category': 'education',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc',
        'legal_basis': ['Luật Giáo dục 2019', 'Quy chế học sinh, sinh viên của từng trường'],
        'implementing_level': 'district',
        'agency': 'Phòng Công tác sinh viên / Ban Giám hiệu',
        'requirements': [
            ('Đơn xin thôi học', 'Sinh viên/học sinh ký; phụ huynh ký (nếu chưa thành niên)', True, 'original', 0, 'mau-don-xin-thoi-hoc.docx'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Thẻ sinh viên / học sinh', 'Để thu hồi', False, 'original', 2),
        ],
    },
    'xet_tot_nghiep': {
        'name': 'Xét công nhận tốt nghiệp',
        'code': 'gd_tn_001',
        'category': 'education',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày xét tốt nghiệp theo đợt; có thể lâu hơn tùy trường',
        'legal_basis': ['Luật Giáo dục 2019', 'Quy chế đào tạo của từng cơ sở GD'],
        'implementing_level': 'province',
        'agency': 'Hội đồng xét công nhận tốt nghiệp của cơ sở giáo dục',
        'requirements': [
            ('Đơn xin xét công nhận tốt nghiệp', 'Ghi rõ khóa học, ngành học, điểm toàn khóa', True, 'original', 0, 'mau-don-xin-xet-tot-nghiep.docx'),
            ('Bảng điểm toàn khóa', 'In từ hệ thống nhà trường hoặc bản sao có xác nhận', True, 'copy', 1),
            ('Đề tài/khóa luận tốt nghiệp (nếu có)', 'File PDF + bản cứng nộp phòng đào tạo', False, 'original', 2),
        ],
    },
    'phuc_khao_thi': {
        'name': 'Đề nghị chấm phúc khảo bài thi',
        'code': 'gd_pk_001',
        'category': 'education',
        'fee': 30000,
        'fee_note': '30.000 đồng/môn thi (theo quy định từng trường)',
        'processing_days': 15,
        'processing_note': '15 ngày kể từ khi thông báo kết quả thi',
        'legal_basis': ['Quy chế thi cử của Bộ GD&ĐT; Quy định của cơ sở giáo dục'],
        'implementing_level': 'district',
        'agency': 'Ban Khảo thí / Phòng Đào tạo',
        'requirements': [
            ('Đơn xin chấm phúc khảo bài thi', 'Ghi rõ môn thi, mã đề, số phách, điểm muốn phúc khảo', True, 'original', 0, 'mau-don-xin-phuc-khao-bai-thi.doc'),
            ('Biên lai nộp lệ phí phúc khảo', 'Nộp tại phòng tài chính hoặc chuyển khoản', True, 'original', 1),
            ('Đơn xin chấm phúc khảo bài thi tuyển sinh y tế (Mẫu SYT)', 'Dành riêng cho kỳ thi tuyển sinh các trường y tế; ghi rõ môn thi, số báo danh', False, 'original', 2, 'mau-don-xin-phuc-khao-bai-thi-syt.doc'),
        ],
    },
    'mien_giam_hoc_phi': {
        'name': 'Đề nghị miễn, giảm học phí',
        'code': '2.000870',
        'category': 'education',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 20,
        'processing_note': '20 ngày làm việc kể từ khi tiếp nhận hồ sơ',
        'legal_basis': ['Nghị định 81/2021/NĐ-CP ngày 27/8/2021', 'Luật Giáo dục 2019'],
        'implementing_level': 'district',
        'agency': 'Cơ sở giáo dục (trường học)',
        'requirements': [
            ('Đơn đề nghị miễn, giảm học phí', 'Ghi rõ đối tượng, diện miễn/giảm đề nghị', True, 'original', 0, 'mau-don-mien-giam-hoc-phi.docx'),
            ('Giấy tờ chứng minh đối tượng miễn/giảm', 'Hộ nghèo, xác nhận thương binh, liệt sĩ, người có công...', True, 'copy', 1),
            ('CCCD/Căn cước công dân học sinh/sinh viên', 'Bản sao', True, 'copy', 2),
        ],
    },

    # ── Lao động & Xã hội bổ sung ─────────────────────────────────────────────
    'ho_tro_nha_o': {
        'name': 'Hỗ trợ về nhà ở đối với người có công với cách mạng',
        'code': '1.001649',
        'category': 'labor',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày kể từ khi UBND huyện duyệt danh sách',
        'legal_basis': ['Quyết định 22/2013/QĐ-TTg', 'Quyết định 15/2020/QĐ-TTg'],
        'implementing_level': 'ward',
        'agency': 'UBND cấp xã (đề xuất); Sở LĐ-TB&XH (thẩm định)',
        'requirements': [
            ('Đơn đề nghị hỗ trợ nhà ở (Mẫu 04 / QĐ 15/2020/QĐ-TTg)', 'Ghi rõ tình trạng nhà ở hiện tại và mức đề nghị hỗ trợ', True, 'original', 0, 'mau-don-ho-tro-nha-o.doc'),
            ('Giấy xác nhận người có công với cách mạng', 'Do Sở LĐ-TB&XH hoặc cơ quan có thẩm quyền cấp', True, 'original', 1, 'mau-giay-xac-nhan-nguoi-co-cong.doc'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 2),
            ('Giấy tờ về nhà ở hiện tại', 'Sổ đỏ/sổ hồng, hoặc xác nhận không có nhà của UBND xã', True, 'copy', 3),
        ],
    },

    # ── Doanh nghiệp bổ sung ──────────────────────────────────────────────────
    'thay_doi_dkdn': {
        'name': 'Thông báo thay đổi nội dung đăng ký doanh nghiệp',
        'code': '1.001015',
        'category': 'business',
        'fee': 50000,
        'fee_note': '50.000 đồng nộp hồ sơ giấy; miễn phí nộp trực tuyến',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc',
        'legal_basis': ['Luật Doanh nghiệp 2020', 'Nghị định 01/2021/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Sở Kế hoạch và Đầu tư (Phòng Đăng ký kinh doanh)',
        'requirements': [
            ('Thông báo thay đổi nội dung đăng ký doanh nghiệp (Phụ lục II-1)', 'Mô tả rõ nội dung thay đổi (tên, địa chỉ, người đại diện...)', True, 'original', 0, 'mau-thong-bao-thay-doi-noi-dung-dkdn.docx'),
            ('Giấy chứng nhận ĐKDN', 'Bản gốc để thu hồi và cấp lại', True, 'original', 1),
            ('CCCD/Căn cước của người đại diện', 'Bản sao', True, 'copy', 2),
            ('Quyết định của chủ sở hữu / HĐQT về việc thay đổi', 'Nếu thay đổi vốn, cơ cấu tổ chức', False, 'original', 3),
        ],
    },
    'giai_the_doanh_nghiep': {
        'name': 'Đề nghị giải thể doanh nghiệp',
        'code': '1.001030',
        'category': 'business',
        'fee': 50000,
        'fee_note': '50.000 đồng',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc để đăng ký; quá trình giải thể thực tế 180 ngày',
        'legal_basis': ['Luật Doanh nghiệp 2020', 'Nghị định 01/2021/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Sở Kế hoạch và Đầu tư',
        'requirements': [
            ('Thông báo giải thể doanh nghiệp (Phụ lục II-18)', 'Ghi rõ lý do giải thể, thời điểm dự kiến', True, 'original', 0, 'mau-giai-the-doanh-nghiep.docx'),
            ('Quyết định giải thể của chủ sở hữu / HĐQT', 'Bản gốc có ký tên, đóng dấu', True, 'original', 1),
            ('Giấy chứng nhận ĐKDN', 'Bản gốc để thu hồi', True, 'original', 2),
            ('Xác nhận hoàn thành nghĩa vụ thuế', 'Từ Cục Thuế', True, 'original', 3),
            ('Xác nhận hoàn thành nghĩa vụ BHXH', 'Từ BHXH', True, 'original', 4),
        ],
    },
    'dieu_chinh_dau_tu': {
        'name': 'Điều chỉnh dự án đầu tư',
        'code': '1.004200',
        'category': 'business',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': ['Luật Đầu tư 2020 (Luật số 61/2020/QH14)', 'Nghị định 31/2021/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Sở Kế hoạch và Đầu tư; Ban Quản lý KKT Nghi Sơn',
        'requirements': [
            ('Văn bản đề nghị điều chỉnh dự án đầu tư (Mẫu A-I-11)', 'Ghi rõ nội dung điều chỉnh, lý do', True, 'original', 0, 'mau-de-nghi-dieu-chinh-du-an-dau-tu.docx'),
            ('Giấy chứng nhận đăng ký đầu tư / IRC', 'Bản gốc', True, 'original', 1),
            ('Tài liệu giải trình nội dung điều chỉnh', 'Báo cáo tiến độ, phương án điều chỉnh', True, 'original', 2),
            ('CCCD/Căn cước hoặc hộ chiếu người đại diện', 'Bản sao', True, 'copy', 3),
        ],
    },

    # ── Thuế TNCN ─────────────────────────────────────────────────────────────
    'khai_thue_tncn': {
        'name': 'Khai thuế thu nhập cá nhân',
        'code': 'tax_tncn_001',
        'category': 'tax',
        'fee': 0,
        'fee_note': 'Miễn phí khai báo; thuế TNCN theo biểu lũy tiến hoặc 10%/20% tùy loại thu nhập',
        'processing_days': 0,
        'processing_note': 'Khai theo kỳ tính thuế (tháng/quý); quyết toán năm trước 31/3',
        'legal_basis': ['Luật Thuế TNCN 2007 (sửa đổi 2012, 2014)', 'Thông tư 80/2021/TT-BTC'],
        'implementing_level': 'district',
        'agency': 'Chi cục Thuế khu vực / Cổng dịch vụ thuế điện tử',
        'requirements': [
            ('Tờ khai thuế thu nhập cá nhân (Mẫu 02/QTT-TNCN)', 'Điền đầy đủ thu nhập, khấu trừ; nộp trực tuyến hoặc giấy', True, 'original', 0, 'mau-to-khai-thue-thu-nhap-ca-nhan.docx'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Chứng từ khấu trừ thuế / bảng lương', 'Do đơn vị chi trả thu nhập cấp', False, 'copy', 2),
        ],
    },

    # ── Hải quan ──────────────────────────────────────────────────────────────
    'khai_hai_quan': {
        'name': 'Khai bổ sung tờ khai hải quan',
        'code': 'hq_001',
        'category': 'business',
        'fee': 0,
        'fee_note': 'Miễn phí khai bổ sung (phạt vi phạm tùy mức độ sai sót)',
        'processing_days': 5,
        'processing_note': '05 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': ['Luật Hải quan 2014', 'Nghị định 08/2015/NĐ-CP', 'Thông tư 38/2015/TT-BTC'],
        'implementing_level': 'province',
        'agency': 'Chi cục Hải quan tỉnh Thanh Hóa',
        'requirements': [
            ('Tờ khai hải quan bổ sung', 'Ghi rõ nội dung cần bổ sung/sửa đổi so với tờ khai gốc', True, 'original', 0, 'mau-to-khai-hai-quan-bo-sung.docx'),
            ('Tờ khai hải quan gốc', 'Bản sao để đối chiếu', True, 'copy', 1),
            ('Hóa đơn / Chứng từ chứng minh thông tin bổ sung', 'Invoice, packing list, bill of lading...', True, 'copy', 2),
        ],
    },

    # ── Ủy quyền ──────────────────────────────────────────────────────────────
    'uy_quyen': {
        'name': 'Lập giấy ủy quyền',
        'code': 'tp_uq_001',
        'category': 'justice',
        'fee': 50000,
        'fee_note': 'Phí công chứng ủy quyền: 50.000 đồng (theo Thông tư 257/2016/TT-BTC)',
        'processing_days': 1,
        'processing_note': 'Trong ngày làm việc',
        'legal_basis': ['Bộ luật Dân sự 2015', 'Luật Công chứng 2014'],
        'implementing_level': 'district',
        'agency': 'Phòng công chứng / Văn phòng công chứng tư',
        'requirements': [
            ('Giấy ủy quyền (có công chứng)', 'Ghi rõ phạm vi ủy quyền, thời hạn, người được ủy quyền', True, 'original', 0, 'mau-giay-uy-quyen.docx'),
            ('CCCD/Căn cước công dân bên ủy quyền', 'Bản gốc để đối chiếu + bản sao', True, 'certified_copy', 1),
            ('CCCD/Căn cước công dân bên được ủy quyền', 'Bản sao', True, 'copy', 2),
        ],
    },

    # ── Đăng ký DN Phụ lục I-2 (Công ty TNHH 2+ thành viên) ─────────────────
    'dang_ky_cong_ty_tnhh_nhieu_tv': {
        'name': 'Đăng ký thành lập Công ty TNHH hai thành viên trở lên',
        'code': '1.000955',
        'category': 'business',
        'fee': 50000,
        'fee_note': '50.000 đồng nộp giấy; miễn phí đăng ký trực tuyến',
        'processing_days': 3,
        'processing_note': '03 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ',
        'legal_basis': ['Luật Doanh nghiệp 2020', 'Nghị định 01/2021/NĐ-CP', 'Thông tư 01/2021/TT-BKHĐT'],
        'implementing_level': 'province',
        'agency': 'Sở Kế hoạch và Đầu tư (Phòng Đăng ký kinh doanh)',
        'requirements': [
            ('Giấy đề nghị đăng ký doanh nghiệp (Phụ lục I-2, NĐ01/2021)', 'Người đại diện pháp luật ký tên', True, 'original', 0, 'mau-dang-ky-doanh-nghiep-phu-luc-i2.docx'),
            ('Điều lệ công ty', 'Người đại diện pháp luật và các thành viên ký từng trang', True, 'original', 1),
            ('Danh sách thành viên góp vốn', 'Ghi rõ họ tên, CCCD, phần vốn góp từng thành viên', True, 'original', 2),
            ('CCCD/Căn cước công dân các thành viên và người đại diện', 'Bản sao không cần công chứng', True, 'copy', 3),
        ],
    },

    # ── Xử phạt & Môi trường bổ sung ─────────────────────────────────────────
    'khieu_nai_hanh_chinh': {
        'name': 'Giải quyết khiếu nại hành chính lần đầu',
        'code': 'kn_001',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Miễn phí',
        'processing_days': 30,
        'processing_note': '30 ngày làm việc (vụ việc phức tạp tối đa 45 ngày)',
        'legal_basis': ['Luật Khiếu nại 2011 (Luật số 02/2011/QH13)', 'Nghị định 124/2020/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'Thủ trưởng cơ quan hành chính đã ban hành quyết định bị khiếu nại',
        'requirements': [
            ('Đơn khiếu nại', 'Ghi rõ quyết định/hành vi bị khiếu nại, lý do, yêu cầu', True, 'original', 0, 'mau-don-khieu-nai-hanh-chinh.docx'),
            ('CCCD/Căn cước công dân', 'Bản sao', True, 'copy', 1),
            ('Bản sao quyết định/văn bản bị khiếu nại', 'Có xác nhận', True, 'copy', 2),
            ('Tài liệu, chứng cứ liên quan', 'Hợp đồng, biên lai, ảnh chụp...', False, 'copy', 3),
        ],
    },
    'xu_ly_vi_pham_hc': {
        'name': 'Lập biên bản vi phạm hành chính',
        'code': 'xp_001',
        'category': 'civil',
        'fee': 0,
        'fee_note': 'Không thu phí lập biên bản; xử phạt theo quyết định riêng',
        'processing_days': 1,
        'processing_note': 'Lập ngay tại chỗ khi phát hiện vi phạm',
        'legal_basis': ['Luật Xử lý VPHC 2012 (sửa đổi 2020)', 'Nghị định 118/2021/NĐ-CP'],
        'implementing_level': 'ward',
        'agency': 'Người có thẩm quyền xử phạt (cảnh sát, thanh tra, kiểm lâm...)',
        'requirements': [
            ('Biên bản vi phạm hành chính', 'Lập theo mẫu NĐ 118/2021; có chữ ký người vi phạm và người lập', True, 'original', 0, 'mau-bien-ban-vi-pham-hanh-chinh.docx'),
            ('CCCD/Căn cước của người vi phạm', 'Bản gốc để đối chiếu', True, 'original', 1),
        ],
    },
    'cap_phep_moi_truong': {
        'name': 'Cấp giấy phép môi trường',
        'code': '1.004231',
        'category': 'environment',
        'fee': 0,
        'fee_note': 'Miễn phí theo Luật BVMT 2020',
        'processing_days': 45,
        'processing_note': '45 ngày làm việc kể từ ngày tiếp nhận đủ hồ sơ hợp lệ',
        'legal_basis': ['Luật Bảo vệ môi trường 2020 (Luật số 72/2020/QH14)', 'Nghị định 08/2022/NĐ-CP'],
        'implementing_level': 'province',
        'agency': 'Sở Tài nguyên và Môi trường Thanh Hóa',
        'requirements': [
            ('Đơn đề nghị cấp giấy phép môi trường (Mẫu 05)', 'Điền đầy đủ thông tin dự án/cơ sở', True, 'original', 0, 'mau-don-cap-giay-phep-moi-truong.docx'),
            ('Báo cáo đánh giá tác động môi trường (ĐTM) đã được phê duyệt', 'Hoặc Kế hoạch bảo vệ môi trường', True, 'original', 1),
            ('Giấy chứng nhận ĐKDN / Quyết định đầu tư', 'Bản sao', True, 'copy', 2),
            ('Kế hoạch quản lý chất thải, nước thải', 'Theo yêu cầu kỹ thuật', True, 'original', 3),
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# 3. HÀM SEED
# ══════════════════════════════════════════════════════════════════════════════

def seed_agencies():
    """Seed thêm cơ quan vào file-based PublicService storage."""
    from models.public_service import PublicService
    from models.service_category import ServiceCategory

    all_cats = ServiceCategory.find_all()
    code_map = {c['code']: c['id'] for c in all_cats}

    existing = PublicService.find_all()
    existing_ids   = {x.get('id') for x in existing if x.get('id')}
    existing_names = {x.get('name') for x in existing}

    added = 0
    for a in AGENCIES:
        if a['id'] in existing_ids or a['name'] in existing_names:
            print(f"  - Đã tồn tại: {a['name']}")
            continue
        cat_id = code_map.get(a.get('categoryId'))
        payload = {**a, 'categoryId': cat_id or a.get('categoryId')}
        PublicService.create(payload)
        print(f"  + Thêm mới:   {a['name']}")
        added += 1

    print(f'  → Tổng thêm {added}/{len(AGENCIES)} cơ quan.')


def seed_service_requirements():
    """Seed thủ tục hành chính (service_requirements) vào PostgreSQL."""
    from models.db import db
    from sqlalchemy import text
    import uuid

    upserted = 0
    for svc_id, proc in PROCEDURES.items():
        # Xóa requirements cũ nếu có để seed lại đúng
        try:
            db.session.execute(
                text('DELETE FROM public.service_requirements WHERE service_id = :sid'),
                {'sid': svc_id}
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

        for i, req_tuple in enumerate(proc['requirements']):
            doc_name, doc_desc, is_req, doc_type, order_idx = req_tuple[:5]
            tmpl_file = req_tuple[5] if len(req_tuple) > 5 else None
            try:
                db.session.execute(text('''
                    INSERT INTO public.service_requirements
                        (id, service_id, doc_name, doc_description, is_required, doc_type, order_index, template_file)
                    VALUES (:id, :sid, :name, :desc, :req, :dtype, :order, :tmpl)
                    ON CONFLICT (id) DO UPDATE SET
                        doc_name        = EXCLUDED.doc_name,
                        doc_description = EXCLUDED.doc_description,
                        is_required     = EXCLUDED.is_required,
                        doc_type        = EXCLUDED.doc_type,
                        order_index     = EXCLUDED.order_index,
                        template_file   = EXCLUDED.template_file
                '''), {
                    'id':    f'{svc_id}-req-{i:03d}',
                    'sid':   svc_id,
                    'name':  doc_name,
                    'desc':  doc_desc,
                    'req':   is_req,
                    'dtype': doc_type,
                    'order': order_idx,
                    'tmpl':  tmpl_file,
                })
                upserted += 1
            except Exception as e:
                print(f'  ! Lỗi khi seed {svc_id} req {i}: {e}')
                db.session.rollback()

        try:
            db.session.commit()
            print(f"  + {proc['name']} ({svc_id}): {len(proc['requirements'])} giấy tờ")
        except Exception as e:
            print(f'  ! Commit lỗi {svc_id}: {e}')
            db.session.rollback()

    print(f'  → Tổng {upserted} giấy tờ của {len(PROCEDURES)} thủ tục.')


def seed_procedure_metadata():
    """Lưu metadata thủ tục (phí, thời gian, căn cứ pháp lý) vào DB riêng."""
    from models.db import db
    from sqlalchemy import text
    import json

    # Tạo bảng procedures nếu chưa có
    try:
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS public.procedures (
                id              VARCHAR(80)  PRIMARY KEY,
                name            VARCHAR(255) NOT NULL,
                code            VARCHAR(50),
                category        VARCHAR(80)  NOT NULL DEFAULT '',
                fee             INTEGER      NOT NULL DEFAULT 0,
                fee_note        TEXT         NOT NULL DEFAULT '',
                processing_days INTEGER      NOT NULL DEFAULT 0,
                processing_note TEXT         NOT NULL DEFAULT '',
                legal_basis     JSONB        NOT NULL DEFAULT '[]',
                implementing_level VARCHAR(30) NOT NULL DEFAULT 'ward',
                agency          TEXT         NOT NULL DEFAULT '',
                is_online       BOOLEAN      NOT NULL DEFAULT TRUE,
                is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_proc_category
                ON public.procedures(category, is_active);
            CREATE INDEX IF NOT EXISTS idx_proc_level
                ON public.procedures(implementing_level, is_active);
        '''))
        db.session.commit()
    except Exception as e:
        print(f'  ! Tạo bảng procedures lỗi: {e}')
        db.session.rollback()

    upserted = 0
    for svc_id, proc in PROCEDURES.items():
        try:
            db.session.execute(text('''
                INSERT INTO public.procedures
                    (id, name, code, category, fee, fee_note, processing_days,
                     processing_note, legal_basis, implementing_level, agency)
                VALUES (:id, :name, :code, :cat, :fee, :fee_note, :days,
                        :days_note, :legal::jsonb, :level, :agency)
                ON CONFLICT (id) DO UPDATE SET
                    name            = EXCLUDED.name,
                    code            = EXCLUDED.code,
                    fee             = EXCLUDED.fee,
                    fee_note        = EXCLUDED.fee_note,
                    processing_days = EXCLUDED.processing_days,
                    processing_note = EXCLUDED.processing_note,
                    legal_basis     = EXCLUDED.legal_basis,
                    implementing_level = EXCLUDED.implementing_level,
                    agency          = EXCLUDED.agency,
                    updated_at      = now()
            '''), {
                'id':       svc_id,
                'name':     proc['name'],
                'code':     proc.get('code', ''),
                'cat':      proc.get('category', ''),
                'fee':      proc.get('fee', 0),
                'fee_note': proc.get('fee_note', ''),
                'days':     proc.get('processing_days', 0),
                'days_note':proc.get('processing_note', ''),
                'legal':    json.dumps(proc.get('legal_basis', []), ensure_ascii=False),
                'level':    proc.get('implementing_level', 'ward'),
                'agency':   proc.get('agency', ''),
            })
            upserted += 1
        except Exception as e:
            print(f'  ! {svc_id}: {e}')
            db.session.rollback()

    try:
        db.session.commit()
        print(f'  → Seed {upserted} thủ tục vào bảng procedures.')
    except Exception as e:
        print(f'  ! Commit metadata lỗi: {e}')
        db.session.rollback()


def main():
    print('\n' + '='*60)
    print('  SEED DỮ LIỆU E-MAPP — Tỉnh Thanh Hóa')
    print('  Nguồn: dichvucong.gov.vn | thutuchanhchinh.gov.vn')
    print('='*60 + '\n')

    # Khởi tạo Flask app context
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from flask import Flask
    from models.db import init_db

    app = Flask(__name__)
    db = init_db(app)

    with app.app_context():
        print('1. Seed cơ quan hành chính...')
        seed_agencies()

        print('\n2. Seed thủ tục hành chính (giấy tờ yêu cầu)...')
        seed_service_requirements()

        print('\n3. Seed metadata thủ tục (phí, thời gian, căn cứ pháp lý)...')
        seed_procedure_metadata()

    print('\n✓ Hoàn thành seed dữ liệu!')
    print('\nĐể tải dữ liệu vào RAG chatbot, chạy tiếp:')
    print('  python scripts/seed_rag_knowledge.py')


if __name__ == '__main__':
    main()
