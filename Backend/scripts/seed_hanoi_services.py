"""
Seed dữ liệu cơ quan hành chính toàn bộ Hà Nội vào public_services.json
Bao gồm: 12 quận nội thành + 17 huyện/thị xã ngoại thành
Mỗi đơn vị: UBND, Công an, BHXH, Chi cục thuế, Trung tâm hành chính công
"""
import json
import os
from datetime import datetime

DATA_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'public_services.json'))
NOW = datetime.now().isoformat()

WH = {
    "monday": "7:30-17:00", "tuesday": "7:30-17:00",
    "wednesday": "7:30-17:00", "thursday": "7:30-17:00",
    "friday": "7:30-17:00", "saturday": "7:30-11:30", "sunday": "Closed"
}
WH_247 = {k: "24/7" for k in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}

def svc(id_, name, desc, cat, addr, lat, lng, phone, level, services, rating=0, website='', district='', ward=''):
    return {
        "id": id_, "name": name, "description": desc, "categoryId": cat,
        "locationId": None, "address": addr, "latitude": lat, "longitude": lng,
        "phone": phone, "email": "", "website": website,
        "workingHours": WH,
        "services": services, "level": level, "rating": rating,
        "status": "normal", "distance": None,
        "province": "Hà Nội", "district": district, "ward": ward,
        "createdAt": NOW, "updatedAt": NOW
    }

HANOI_DATA = [
    # ══════════════════════════════════════════════
    # CẤP THÀNH PHỐ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-tp", "UBND Thành phố Hà Nội", "Ủy ban nhân dân Thành phố Hà Nội",
        "ubnd", "12 Lê Lai, Điện Biên, Ba Đình, Hà Nội", 21.0339, 105.8410,
        "024.3825.3906", "province",
        ["Hành chính tổng hợp","Tiếp công dân","Giải quyết khiếu nại","Chỉ đạo điều hành"], 4.1,
        "https://hanoi.gov.vn", "TP. Hà Nội"),

    svc("hn-conganthanh-pho", "Công an Thành phố Hà Nội", "Công an TP Hà Nội – cơ quan đầu mối an ninh trật tự",
        "police", "87 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội", 21.0240, 105.8490,
        "024.3942.4466", "province",
        ["CCCD/Căn cước","Đăng ký xe","Xuất nhập cảnh","Phòng cháy chữa cháy","Tạm trú tạm vắng"], 3.9,
        "", "TP. Hà Nội"),

    svc("hn-bhxh-tp", "BHXH Thành phố Hà Nội", "Bảo hiểm xã hội TP Hà Nội",
        "bhxh", "75 Nguyễn Chí Thanh, Đống Đa, Hà Nội", 21.0222, 105.8336,
        "024.3834.3537", "province",
        ["BHXH","BHYT","BHTN","Sổ BHXH","Giải quyết chế độ"], 3.8,
        "https://bhxhhanoi.gov.vn", "TP. Hà Nội"),

    svc("hn-cuc-thue-tp", "Cục Thuế Thành phố Hà Nội", "Cơ quan thuế cấp thành phố",
        "tax", "127 Trần Duy Hưng, Trung Hoà, Cầu Giấy, Hà Nội", 21.0085, 105.7979,
        "024.7303.7399", "province",
        ["Đăng ký mã số thuế","Kê khai thuế","Hoá đơn điện tử","Hoàn thuế"], 3.7,
        "", "TP. Hà Nội", "Cầu Giấy"),

    svc("hn-ttphcc-tp", "Trung tâm Phục vụ Hành chính công Hà Nội",
        "Một cửa dịch vụ công tập trung toàn thành phố",
        "trung-tam", "258 Phố Huế, Hai Bà Trưng, Hà Nội", 21.0120, 105.8486,
        "024.3622.8266", "province",
        ["Tiếp nhận hồ sơ một cửa","Giải quyết thủ tục hành chính","Trả kết quả"], 4.3,
        "", "TP. Hà Nội", "Hai Bà Trưng"),

    svc("hn-so-tuphanh", "Sở Tư pháp Hà Nội", "Cơ quan quản lý công tác tư pháp",
        "so-nganh", "18 Trần Phú, Ba Đình, Hà Nội", 21.0330, 105.8398,
        "024.3734.5388", "province",
        ["Hộ tịch","Công chứng","Chứng thực","Lý lịch tư pháp","Trợ giúp pháp lý"], 4.0,
        "", "TP. Hà Nội", "Ba Đình"),

    svc("hn-so-tnmt", "Sở Tài nguyên & Môi trường Hà Nội", "Quản lý đất đai, tài nguyên, môi trường",
        "so-nganh", "18 Huỳnh Thúc Kháng, Đống Đa, Hà Nội", 21.0246, 105.8286,
        "024.3834.6666", "province",
        ["Cấp sổ đỏ","Biến động đất đai","Đăng ký giao dịch bảo đảm","Môi trường"], 3.6,
        "", "TP. Hà Nội", "Đống Đa"),

    svc("hn-so-xd", "Sở Xây dựng Hà Nội", "Cấp phép xây dựng, quy hoạch đô thị",
        "so-nganh", "52 Lê Đại Hành, Hai Bà Trưng, Hà Nội", 21.0148, 105.8525,
        "024.3976.4601", "province",
        ["Cấp phép xây dựng","Quy hoạch","Nhà ở","Thẩm định thiết kế"], 3.5,
        "", "TP. Hà Nội", "Hai Bà Trưng"),

    svc("hn-so-khdt", "Sở Kế hoạch & Đầu tư Hà Nội", "Đăng ký doanh nghiệp, đầu tư",
        "so-nganh", "16 Cát Linh, Đống Đa, Hà Nội", 21.0282, 105.8394,
        "024.3734.2553", "province",
        ["Đăng ký doanh nghiệp","Đăng ký hộ kinh doanh","Đầu tư nước ngoài"], 3.9,
        "", "TP. Hà Nội", "Đống Đa"),

    svc("hn-so-gt", "Sở Giao thông Vận tải Hà Nội", "Quản lý giao thông, GPLX",
        "so-nganh", "8 Phạm Hùng, Bắc Từ Liêm, Hà Nội", 21.0536, 105.7803,
        "024.3768.8858", "province",
        ["Cấp GPLX","Đăng kiểm xe","Vận tải hành khách","Đường bộ"], 3.5,
        "", "TP. Hà Nội", "Bắc Từ Liêm"),

    # ══════════════════════════════════════════════
    # QUẬN BA ĐÌNH
    # ══════════════════════════════════════════════
    svc("hn-ubnd-badinh", "UBND Quận Ba Đình", "Ủy ban nhân dân Quận Ba Đình",
        "ubnd", "Số 6 Lê Hồng Phong, Điện Biên, Ba Đình, Hà Nội", 21.0358, 105.8382,
        "024.3734.4699", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Doanh nghiệp"], 4.0,
        "", "Ba Đình"),

    svc("hn-caquan-badinh", "Công an Quận Ba Đình", "Công an Quận Ba Đình",
        "police", "47 Nguyễn Thái Học, Ba Đình, Hà Nội", 21.0343, 105.8406,
        "024.3734.5510", "district",
        ["CCCD","Đăng ký tạm trú","Cấp phép"], 3.8, "", "Ba Đình"),

    svc("hn-bhxh-badinh", "BHXH Quận Ba Đình", "Bảo hiểm xã hội Quận Ba Đình",
        "bhxh", "127 Đội Cấn, Ba Đình, Hà Nội", 21.0366, 105.8314,
        "024.3767.3390", "district",
        ["BHXH","BHYT","Sổ BHXH","Chế độ thai sản"], 3.7, "", "Ba Đình"),

    # ══════════════════════════════════════════════
    # QUẬN HOÀN KIẾM
    # ══════════════════════════════════════════════
    svc("hn-ubnd-hoankiem", "UBND Quận Hoàn Kiếm", "Ủy ban nhân dân Quận Hoàn Kiếm",
        "ubnd", "49 Đinh Tiên Hoàng, Hoàn Kiếm, Hà Nội", 21.0285, 105.8542,
        "024.3928.6869", "district",
        ["Hộ tịch","Cư trú","Đất đai","Kinh doanh"], 4.1, "", "Hoàn Kiếm"),

    svc("hn-caquan-hoankiem", "Công an Quận Hoàn Kiếm", "Công an Quận Hoàn Kiếm",
        "police", "2A Lý Thường Kiệt, Hoàn Kiếm, Hà Nội", 21.0283, 105.8484,
        "024.3942.4188", "district",
        ["CCCD","Đăng ký xe","Tạm trú"], 3.9, "", "Hoàn Kiếm"),

    svc("hn-ttyt-hoankiem", "Trung tâm Y tế Quận Hoàn Kiếm", "Dịch vụ y tế cấp quận",
        "health", "72 Hàng Bạc, Hoàn Kiếm, Hà Nội", 21.0319, 105.8517,
        "024.3928.5655", "district",
        ["Khám chữa bệnh","Tiêm chủng","Kiểm tra sức khỏe","Chứng nhận sức khỏe"], 3.8,
        "", "Hoàn Kiếm"),

    # ══════════════════════════════════════════════
    # QUẬN HAI BÀ TRƯNG
    # ══════════════════════════════════════════════
    svc("hn-ubnd-hbt", "UBND Quận Hai Bà Trưng", "Ủy ban nhân dân Quận Hai Bà Trưng",
        "ubnd", "5 Phan Chu Trinh, Phạm Đình Hổ, Hai Bà Trưng, Hà Nội", 21.0124, 105.8479,
        "024.3976.6879", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 3.9, "", "Hai Bà Trưng"),

    svc("hn-caquan-hbt", "Công an Quận Hai Bà Trưng", "Công an Quận Hai Bà Trưng",
        "police", "97 Hàn Thuyên, Hai Bà Trưng, Hà Nội", 21.0156, 105.8519,
        "024.3976.4562", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.7, "", "Hai Bà Trưng"),

    svc("hn-bhxh-hbt", "BHXH Quận Hai Bà Trưng", "Bảo hiểm xã hội Quận Hai Bà Trưng",
        "bhxh", "37 Trần Đại Nghĩa, Hai Bà Trưng, Hà Nội", 21.0084, 105.8438,
        "024.3636.4449", "district",
        ["BHXH","BHYT","Chế độ ốm đau","Hưu trí"], 3.6, "", "Hai Bà Trưng"),

    # ══════════════════════════════════════════════
    # QUẬN ĐỐNG ĐA
    # ══════════════════════════════════════════════
    svc("hn-ubnd-dongda", "UBND Quận Đống Đa", "Ủy ban nhân dân Quận Đống Đa",
        "ubnd", "108 Tôn Đức Thắng, Quốc Tử Giám, Đống Đa, Hà Nội", 21.0263, 105.8380,
        "024.3845.5064", "district",
        ["Hộ tịch","Cư trú","Đất đai","Kinh doanh","Xây dựng"], 3.9, "", "Đống Đa"),

    svc("hn-caquan-dongda", "Công an Quận Đống Đa", "Công an Quận Đống Đa",
        "police", "38 Cát Linh, Đống Đa, Hà Nội", 21.0278, 105.8405,
        "024.3845.6767", "district",
        ["CCCD","Đăng ký xe","Tạm trú","PCCC"], 3.7, "", "Đống Đa"),

    svc("hn-bvbachmai", "Bệnh viện Bạch Mai", "Bệnh viện đa khoa tuyến Trung ương",
        "health", "78 Giải Phóng, Phương Mai, Đống Đa, Hà Nội", 21.0045, 105.8445,
        "024.3869.3731", "province",
        ["Khám bệnh","Cấp cứu","Nội trú","Xét nghiệm","Chẩn đoán hình ảnh"], 4.3,
        "https://bachmai.gov.vn", "Đống Đa"),

    # ══════════════════════════════════════════════
    # QUẬN TÂY HỒ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-tayho", "UBND Quận Tây Hồ", "Ủy ban nhân dân Quận Tây Hồ",
        "ubnd", "Tòa nhà UBND, Xuân La, Tây Hồ, Hà Nội", 21.0710, 105.8221,
        "024.3718.2777", "district",
        ["Hộ tịch","Cư trú","Đất đai","Giải quyết khiếu nại"], 4.0, "", "Tây Hồ"),

    svc("hn-caquan-tayho", "Công an Quận Tây Hồ", "Công an Quận Tây Hồ",
        "police", "Xuân La, Tây Hồ, Hà Nội", 21.0695, 105.8235,
        "024.3718.3118", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.8, "", "Tây Hồ"),

    svc("hn-bhxh-tayho", "BHXH Quận Tây Hồ", "Bảo hiểm xã hội Quận Tây Hồ",
        "bhxh", "Xuân La, Tây Hồ, Hà Nội", 21.0688, 105.8228,
        "024.3718.9024", "district",
        ["BHXH","BHYT","Sổ BHXH"], 3.6, "", "Tây Hồ"),

    # ══════════════════════════════════════════════
    # QUẬN CẦU GIẤY
    # ══════════════════════════════════════════════
    svc("hn-ubnd-caugiay", "UBND Quận Cầu Giấy", "Ủy ban nhân dân Quận Cầu Giấy",
        "ubnd", "3 Trần Thái Tông, Dịch Vọng Hậu, Cầu Giấy, Hà Nội", 21.0352, 105.7977,
        "024.3768.2232", "district",
        ["Hộ tịch","Cư trú","Đất đai","Doanh nghiệp","Xây dựng"], 4.1, "", "Cầu Giấy"),

    svc("hn-caquan-caugiay", "Công an Quận Cầu Giấy", "Công an Quận Cầu Giấy",
        "police", "20 Trần Thái Tông, Cầu Giấy, Hà Nội", 21.0365, 105.7971,
        "024.3768.2199", "district",
        ["CCCD","Tạm trú","Đăng ký xe","PCCC"], 3.9, "", "Cầu Giấy"),

    svc("hn-ccthue-caugiay", "Chi cục Thuế Quận Cầu Giấy", "Cơ quan thuế cấp quận",
        "tax", "85 Duy Tân, Cầu Giấy, Hà Nội", 21.0320, 105.7899,
        "024.3768.6680", "district",
        ["Đăng ký MST","Kê khai thuế","Hoá đơn","Quyết toán thuế"], 3.7, "", "Cầu Giấy"),

    svc("hn-bhxh-caugiay", "BHXH Quận Cầu Giấy", "Bảo hiểm xã hội Quận Cầu Giấy",
        "bhxh", "Dịch Vọng, Cầu Giấy, Hà Nội", 21.0348, 105.7961,
        "024.3768.2888", "district",
        ["BHXH","BHYT","Sổ bảo hiểm"], 3.8, "", "Cầu Giấy"),

    # ══════════════════════════════════════════════
    # QUẬN THANH XUÂN
    # ══════════════════════════════════════════════
    svc("hn-ubnd-thanhxuan", "UBND Quận Thanh Xuân", "Ủy ban nhân dân Quận Thanh Xuân",
        "ubnd", "6 Lương Thế Vinh, Nhân Chính, Thanh Xuân, Hà Nội", 20.9919, 105.8119,
        "024.3854.7560", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 3.9, "", "Thanh Xuân"),

    svc("hn-caquan-thanhxuan", "Công an Quận Thanh Xuân", "Công an Quận Thanh Xuân",
        "police", "Nguyễn Quý Đức, Thanh Xuân, Hà Nội", 20.9901, 105.8101,
        "024.3854.6789", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.7, "", "Thanh Xuân"),

    svc("hn-bhxh-thanhxuan", "BHXH Quận Thanh Xuân", "Bảo hiểm xã hội Quận Thanh Xuân",
        "bhxh", "Vương Thừa Vũ, Thanh Xuân, Hà Nội", 20.9878, 105.8148,
        "024.3854.8989", "district",
        ["BHXH","BHYT","Chế độ thai sản"], 3.6, "", "Thanh Xuân"),

    # ══════════════════════════════════════════════
    # QUẬN HOÀNG MAI
    # ══════════════════════════════════════════════
    svc("hn-ubnd-hoangmai", "UBND Quận Hoàng Mai", "Ủy ban nhân dân Quận Hoàng Mai",
        "ubnd", "505 Giải Phóng, Giáp Bát, Hoàng Mai, Hà Nội", 20.9756, 105.8523,
        "024.3641.5799", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Doanh nghiệp"], 3.8, "", "Hoàng Mai"),

    svc("hn-caquan-hoangmai", "Công an Quận Hoàng Mai", "Công an Quận Hoàng Mai",
        "police", "63 Tân Mai, Hoàng Mai, Hà Nội", 20.9779, 105.8504,
        "024.3641.5510", "district",
        ["CCCD","Đăng ký xe","Tạm trú"], 3.7, "", "Hoàng Mai"),

    svc("hn-bhxh-hoangmai", "BHXH Quận Hoàng Mai", "Bảo hiểm xã hội Quận Hoàng Mai",
        "bhxh", "Lĩnh Nam, Hoàng Mai, Hà Nội", 20.9745, 105.8565,
        "024.3641.7777", "district",
        ["BHXH","BHYT","Sổ bảo hiểm"], 3.5, "", "Hoàng Mai"),

    svc("hn-bvdhynhn", "Bệnh viện Đại học Y Hà Nội", "Bệnh viện thực hành đại học uy tín",
        "health", "1 Tôn Thất Tùng, Đống Đa, Hà Nội", 20.9980, 105.8455,
        "024.3574.7788", "province",
        ["Khám bệnh","Nội trú","Cấp cứu","Chuyên khoa sâu"], 4.4,
        "https://bvdhyhanoi.vn", "Đống Đa"),

    # ══════════════════════════════════════════════
    # QUẬN LONG BIÊN
    # ══════════════════════════════════════════════
    svc("hn-ubnd-longbien", "UBND Quận Long Biên", "Ủy ban nhân dân Quận Long Biên",
        "ubnd", "Đường Nguyễn Văn Cừ, Gia Thụy, Long Biên, Hà Nội", 21.0466, 105.8898,
        "024.3827.4011", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 4.0, "", "Long Biên"),

    svc("hn-caquan-longbien", "Công an Quận Long Biên", "Công an Quận Long Biên",
        "police", "Ngọc Lâm, Long Biên, Hà Nội", 21.0481, 105.8886,
        "024.3827.6655", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.8, "", "Long Biên"),

    svc("hn-bhxh-longbien", "BHXH Quận Long Biên", "Bảo hiểm xã hội Quận Long Biên",
        "bhxh", "Đức Giang, Long Biên, Hà Nội", 21.0444, 105.8876,
        "024.3827.8810", "district",
        ["BHXH","BHYT","Sổ bảo hiểm","Chế độ hưu trí"], 3.6, "", "Long Biên"),

    # ══════════════════════════════════════════════
    # QUẬN BẮC TỪ LIÊM
    # ══════════════════════════════════════════════
    svc("hn-ubnd-bactuliem", "UBND Quận Bắc Từ Liêm", "Ủy ban nhân dân Quận Bắc Từ Liêm",
        "ubnd", "Cổ Nhuế 2, Bắc Từ Liêm, Hà Nội", 21.0622, 105.7827,
        "024.6255.0166", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Doanh nghiệp"], 3.9, "", "Bắc Từ Liêm"),

    svc("hn-caquan-bactuliem", "Công an Quận Bắc Từ Liêm", "Công an Quận Bắc Từ Liêm",
        "police", "Phú Diễn, Bắc Từ Liêm, Hà Nội", 21.0605, 105.7813,
        "024.6255.1199", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.7, "", "Bắc Từ Liêm"),

    # ══════════════════════════════════════════════
    # QUẬN NAM TỪ LIÊM
    # ══════════════════════════════════════════════
    svc("hn-ubnd-namtuliem", "UBND Quận Nam Từ Liêm", "Ủy ban nhân dân Quận Nam Từ Liêm",
        "ubnd", "Đường Lê Quang Đạo, Mỹ Đình, Nam Từ Liêm, Hà Nội", 21.0128, 105.7706,
        "024.3768.9978", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 4.0, "", "Nam Từ Liêm"),

    svc("hn-caquan-namtuliem", "Công an Quận Nam Từ Liêm", "Công an Quận Nam Từ Liêm",
        "police", "Mỹ Đình, Nam Từ Liêm, Hà Nội", 21.0110, 105.7715,
        "024.3768.9779", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.8, "", "Nam Từ Liêm"),

    svc("hn-bhxh-namtuliem", "BHXH Quận Nam Từ Liêm", "Bảo hiểm xã hội Quận Nam Từ Liêm",
        "bhxh", "Mỹ Đình 2, Nam Từ Liêm, Hà Nội", 21.0095, 105.7742,
        "024.3768.7777", "district",
        ["BHXH","BHYT","Sổ BHXH"], 3.6, "", "Nam Từ Liêm"),

    # ══════════════════════════════════════════════
    # QUẬN HÀ ĐÔNG
    # ══════════════════════════════════════════════
    svc("hn-ubnd-hadong", "UBND Quận Hà Đông", "Ủy ban nhân dân Quận Hà Đông",
        "ubnd", "22 Trần Phú, Hà Đông, Hà Nội", 20.9629, 105.7798,
        "024.3382.4033", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Doanh nghiệp"], 4.0, "", "Hà Đông"),

    svc("hn-caquan-hadong", "Công an Quận Hà Đông", "Công an Quận Hà Đông",
        "police", "Phùng Hưng, Hà Đông, Hà Nội", 20.9648, 105.7812,
        "024.3382.2288", "district",
        ["CCCD","Đăng ký xe","Tạm trú","PCCC"], 3.8, "", "Hà Đông"),

    svc("hn-bhxh-hadong", "BHXH Quận Hà Đông", "Bảo hiểm xã hội Quận Hà Đông",
        "bhxh", "Quang Trung, Hà Đông, Hà Nội", 20.9612, 105.7785,
        "024.3382.1515", "district",
        ["BHXH","BHYT","Hưu trí","Chế độ ốm đau"], 3.7, "", "Hà Đông"),

    svc("hn-ccthue-hadong", "Chi cục Thuế Quận Hà Đông", "Cơ quan thuế cấp quận",
        "tax", "Yên Nghĩa, Hà Đông, Hà Nội", 20.9580, 105.7759,
        "024.3382.5566", "district",
        ["Đăng ký MST","Kê khai thuế","Quyết toán"], 3.5, "", "Hà Đông"),

    # ══════════════════════════════════════════════
    # HUYỆN ĐÔNG ANH
    # ══════════════════════════════════════════════
    svc("hn-ubnd-donganh", "UBND Huyện Đông Anh", "Ủy ban nhân dân Huyện Đông Anh",
        "ubnd", "Thị trấn Đông Anh, Huyện Đông Anh, Hà Nội", 21.1524, 105.8460,
        "024.3882.3688", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Đăng ký kinh doanh"], 3.8, "", "Đông Anh"),

    svc("hn-caquan-donganh", "Công an Huyện Đông Anh", "Công an Huyện Đông Anh",
        "police", "Thị trấn Đông Anh, Hà Nội", 21.1510, 105.8472,
        "024.3882.3510", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.6, "", "Đông Anh"),

    svc("hn-bhxh-donganh", "BHXH Huyện Đông Anh", "Bảo hiểm xã hội Huyện Đông Anh",
        "bhxh", "Thị trấn Đông Anh, Hà Nội", 21.1498, 105.8455,
        "024.3882.4499", "district",
        ["BHXH","BHYT","Sổ bảo hiểm"], 3.5, "", "Đông Anh"),

    # ══════════════════════════════════════════════
    # HUYỆN GIA LÂM
    # ══════════════════════════════════════════════
    svc("hn-ubnd-gialaam", "UBND Huyện Gia Lâm", "Ủy ban nhân dân Huyện Gia Lâm",
        "ubnd", "Thị trấn Trâu Quỳ, Gia Lâm, Hà Nội", 21.0158, 105.9400,
        "024.3827.7088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 3.8, "", "Gia Lâm"),

    svc("hn-caquan-gialaam", "Công an Huyện Gia Lâm", "Công an Huyện Gia Lâm",
        "police", "Thị trấn Trâu Quỳ, Gia Lâm, Hà Nội", 21.0170, 105.9388,
        "024.3827.5510", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.6, "", "Gia Lâm"),

    svc("hn-bhxh-gialaam", "BHXH Huyện Gia Lâm", "Bảo hiểm xã hội Huyện Gia Lâm",
        "bhxh", "Trâu Quỳ, Gia Lâm, Hà Nội", 21.0145, 105.9415,
        "024.3827.9777", "district",
        ["BHXH","BHYT","Hưu trí"], 3.5, "", "Gia Lâm"),

    # ══════════════════════════════════════════════
    # HUYỆN THANH TRÌ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-thanhtri", "UBND Huyện Thanh Trì", "Ủy ban nhân dân Huyện Thanh Trì",
        "ubnd", "Thị trấn Văn Điển, Thanh Trì, Hà Nội", 20.9316, 105.8436,
        "024.3641.1988", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.7, "", "Thanh Trì"),

    svc("hn-caquan-thanhtri", "Công an Huyện Thanh Trì", "Công an Huyện Thanh Trì",
        "police", "Văn Điển, Thanh Trì, Hà Nội", 20.9328, 105.8448,
        "024.3641.2299", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.5, "", "Thanh Trì"),

    # ══════════════════════════════════════════════
    # HUYỆN HOÀI ĐỨC
    # ══════════════════════════════════════════════
    svc("hn-ubnd-hoaiduc", "UBND Huyện Hoài Đức", "Ủy ban nhân dân Huyện Hoài Đức",
        "ubnd", "Thị trấn Trạm Trôi, Hoài Đức, Hà Nội", 21.0030, 105.7430,
        "024.3386.5088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng"], 3.8, "", "Hoài Đức"),

    svc("hn-caquan-hoaiduc", "Công an Huyện Hoài Đức", "Công an Huyện Hoài Đức",
        "police", "Trạm Trôi, Hoài Đức, Hà Nội", 21.0044, 105.7418,
        "024.3386.4488", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.5, "", "Hoài Đức"),

    svc("hn-bhxh-hoaiduc", "BHXH Huyện Hoài Đức", "Bảo hiểm xã hội Huyện Hoài Đức",
        "bhxh", "Hoài Đức, Hà Nội", 21.0018, 105.7424,
        "024.3386.8822", "district",
        ["BHXH","BHYT","Sổ BHXH"], 3.4, "", "Hoài Đức"),

    # ══════════════════════════════════════════════
    # HUYỆN ĐAN PHƯỢNG
    # ══════════════════════════════════════════════
    svc("hn-ubnd-danphuong", "UBND Huyện Đan Phượng", "Ủy ban nhân dân Huyện Đan Phượng",
        "ubnd", "Thị trấn Phùng, Đan Phượng, Hà Nội", 21.0870, 105.6752,
        "024.3386.2688", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.7, "", "Đan Phượng"),

    svc("hn-caquan-danphuong", "Công an Huyện Đan Phượng", "Công an Huyện Đan Phượng",
        "police", "Thị trấn Phùng, Đan Phượng, Hà Nội", 21.0882, 105.6740,
        "024.3386.2133", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.4, "", "Đan Phượng"),

    # ══════════════════════════════════════════════
    # HUYỆN PHÚC THỌ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-phuctho", "UBND Huyện Phúc Thọ", "Ủy ban nhân dân Huyện Phúc Thọ",
        "ubnd", "Thị trấn Phúc Thọ, Hà Nội", 21.0989, 105.5740,
        "024.3388.0088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.6, "", "Phúc Thọ"),

    svc("hn-caquan-phuctho", "Công an Huyện Phúc Thọ", "Công an Huyện Phúc Thọ",
        "police", "Thị trấn Phúc Thọ, Hà Nội", 21.1001, 105.5728,
        "024.3388.1144", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.3, "", "Phúc Thọ"),

    # ══════════════════════════════════════════════
    # HUYỆN THẠCH THẤT
    # ══════════════════════════════════════════════
    svc("hn-ubnd-thachthat", "UBND Huyện Thạch Thất", "Ủy ban nhân dân Huyện Thạch Thất",
        "ubnd", "Thị trấn Liên Quan, Thạch Thất, Hà Nội", 21.0284, 105.6512,
        "024.3386.4088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp","Làng nghề"], 3.7, "", "Thạch Thất"),

    svc("hn-caquan-thachthat", "Công an Huyện Thạch Thất", "Công an Huyện Thạch Thất",
        "police", "Liên Quan, Thạch Thất, Hà Nội", 21.0296, 105.6500,
        "024.3386.5633", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.4, "", "Thạch Thất"),

    # ══════════════════════════════════════════════
    # HUYỆN QUỐC OAI
    # ══════════════════════════════════════════════
    svc("hn-ubnd-quocoai", "UBND Huyện Quốc Oai", "Ủy ban nhân dân Huyện Quốc Oai",
        "ubnd", "Thị trấn Quốc Oai, Hà Nội", 20.9622, 105.6572,
        "024.3389.1088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.6, "", "Quốc Oai"),

    svc("hn-caquan-quocoai", "Công an Huyện Quốc Oai", "Công an Huyện Quốc Oai",
        "police", "Thị trấn Quốc Oai, Hà Nội", 20.9635, 105.6560,
        "024.3389.0033", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.3, "", "Quốc Oai"),

    # ══════════════════════════════════════════════
    # HUYỆN CHƯƠNG MỸ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-chuongmy", "UBND Huyện Chương Mỹ", "Ủy ban nhân dân Huyện Chương Mỹ",
        "ubnd", "Thị trấn Chúc Sơn, Chương Mỹ, Hà Nội", 20.9161, 105.7168,
        "024.3389.8188", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp","Làng nghề"], 3.6, "", "Chương Mỹ"),

    svc("hn-caquan-chuongmy", "Công an Huyện Chương Mỹ", "Công an Huyện Chương Mỹ",
        "police", "Chúc Sơn, Chương Mỹ, Hà Nội", 20.9148, 105.7180,
        "024.3389.7733", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.3, "", "Chương Mỹ"),

    # ══════════════════════════════════════════════
    # HUYỆN THƯỜNG TÍN
    # ══════════════════════════════════════════════
    svc("hn-ubnd-thuongtin", "UBND Huyện Thường Tín", "Ủy ban nhân dân Huyện Thường Tín",
        "ubnd", "Thị trấn Thường Tín, Hà Nội", 20.8788, 105.8673,
        "024.3386.8588", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.6, "", "Thường Tín"),

    svc("hn-caquan-thuongtin", "Công an Huyện Thường Tín", "Công an Huyện Thường Tín",
        "police", "Thị trấn Thường Tín, Hà Nội", 20.8801, 105.8661,
        "024.3386.8122", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.4, "", "Thường Tín"),

    # ══════════════════════════════════════════════
    # HUYỆN PHÚ XUYÊN
    # ══════════════════════════════════════════════
    svc("hn-ubnd-phuxuyen", "UBND Huyện Phú Xuyên", "Ủy ban nhân dân Huyện Phú Xuyên",
        "ubnd", "Thị trấn Phú Minh, Phú Xuyên, Hà Nội", 20.7678, 105.9146,
        "024.3387.5088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.5, "", "Phú Xuyên"),

    svc("hn-caquan-phuxuyen", "Công an Huyện Phú Xuyên", "Công an Huyện Phú Xuyên",
        "police", "Phú Minh, Phú Xuyên, Hà Nội", 20.7691, 105.9133,
        "024.3387.4411", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.2, "", "Phú Xuyên"),

    # ══════════════════════════════════════════════
    # HUYỆN ỨNG HÒA
    # ══════════════════════════════════════════════
    svc("hn-ubnd-unghoa", "UBND Huyện Ứng Hòa", "Ủy ban nhân dân Huyện Ứng Hòa",
        "ubnd", "Thị trấn Vân Đình, Ứng Hòa, Hà Nội", 20.7584, 105.8275,
        "024.3387.0088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp"], 3.5, "", "Ứng Hòa"),

    svc("hn-caquan-unghoa", "Công an Huyện Ứng Hòa", "Công an Huyện Ứng Hòa",
        "police", "Vân Đình, Ứng Hòa, Hà Nội", 20.7597, 105.8263,
        "024.3387.1122", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.2, "", "Ứng Hòa"),

    # ══════════════════════════════════════════════
    # HUYỆN MỸ ĐỨC
    # ══════════════════════════════════════════════
    svc("hn-ubnd-myduc", "UBND Huyện Mỹ Đức", "Ủy ban nhân dân Huyện Mỹ Đức",
        "ubnd", "Thị trấn Đại Nghĩa, Mỹ Đức, Hà Nội", 20.6612, 105.7218,
        "024.3386.2089", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp","Du lịch Hương Sơn"], 3.6, "", "Mỹ Đức"),

    svc("hn-caquan-myduc", "Công an Huyện Mỹ Đức", "Công an Huyện Mỹ Đức",
        "police", "Đại Nghĩa, Mỹ Đức, Hà Nội", 20.6625, 105.7205,
        "024.3386.2211", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.1, "", "Mỹ Đức"),

    # ══════════════════════════════════════════════
    # HUYỆN SÓC SƠN
    # ══════════════════════════════════════════════
    svc("hn-ubnd-socson", "UBND Huyện Sóc Sơn", "Ủy ban nhân dân Huyện Sóc Sơn",
        "ubnd", "Thị trấn Sóc Sơn, Hà Nội", 21.2533, 105.8679,
        "024.3884.1888", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp","Lâm nghiệp"], 3.7, "", "Sóc Sơn"),

    svc("hn-caquan-socson", "Công an Huyện Sóc Sơn", "Công an Huyện Sóc Sơn",
        "police", "Thị trấn Sóc Sơn, Hà Nội", 21.2545, 105.8667,
        "024.3884.2299", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.5, "", "Sóc Sơn"),

    svc("hn-bhxh-socson", "BHXH Huyện Sóc Sơn", "Bảo hiểm xã hội Huyện Sóc Sơn",
        "bhxh", "Sóc Sơn, Hà Nội", 21.2520, 105.8690,
        "024.3884.3377", "district",
        ["BHXH","BHYT","Sổ BHXH"], 3.4, "", "Sóc Sơn"),

    # ══════════════════════════════════════════════
    # HUYỆN MÊ LINH
    # ══════════════════════════════════════════════
    svc("hn-ubnd-melinh", "UBND Huyện Mê Linh", "Ủy ban nhân dân Huyện Mê Linh",
        "ubnd", "Thị trấn Chi Đông, Mê Linh, Hà Nội", 21.1784, 105.7698,
        "024.3888.5088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông nghiệp","Hoa màu"], 3.7, "", "Mê Linh"),

    svc("hn-caquan-melinh", "Công an Huyện Mê Linh", "Công an Huyện Mê Linh",
        "police", "Chi Đông, Mê Linh, Hà Nội", 21.1796, 105.7685,
        "024.3888.4411", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.4, "", "Mê Linh"),

    # ══════════════════════════════════════════════
    # THỊ XÃ SƠN TÂY
    # ══════════════════════════════════════════════
    svc("hn-ubnd-sontay", "UBND Thị xã Sơn Tây", "Ủy ban nhân dân Thị xã Sơn Tây",
        "ubnd", "Lê Lợi, Quang Trung, Sơn Tây, Hà Nội", 21.1349, 105.5055,
        "024.3388.2288", "district",
        ["Hộ tịch","Cư trú","Đất đai","Xây dựng","Doanh nghiệp"], 3.8, "", "Sơn Tây"),

    svc("hn-caquan-sontay", "Công an Thị xã Sơn Tây", "Công an Thị xã Sơn Tây",
        "police", "Quang Trung, Sơn Tây, Hà Nội", 21.1362, 105.5041,
        "024.3388.2399", "district",
        ["CCCD","Tạm trú","Đăng ký xe","PCCC"], 3.6, "", "Sơn Tây"),

    svc("hn-bhxh-sontay", "BHXH Thị xã Sơn Tây", "Bảo hiểm xã hội Thị xã Sơn Tây",
        "bhxh", "Sơn Tây, Hà Nội", 21.1336, 105.5068,
        "024.3388.3344", "district",
        ["BHXH","BHYT","Hưu trí","Sổ BHXH"], 3.5, "", "Sơn Tây"),

    # ══════════════════════════════════════════════
    # HUYỆN BA VÌ
    # ══════════════════════════════════════════════
    svc("hn-ubnd-bavi", "UBND Huyện Ba Vì", "Ủy ban nhân dân Huyện Ba Vì",
        "ubnd", "Thị trấn Tây Đằng, Ba Vì, Hà Nội", 21.1285, 105.3885,
        "024.3387.3088", "district",
        ["Hộ tịch","Cư trú","Đất đai","Nông-Lâm nghiệp","Du lịch"], 3.6, "", "Ba Vì"),

    svc("hn-caquan-bavi", "Công an Huyện Ba Vì", "Công an Huyện Ba Vì",
        "police", "Tây Đằng, Ba Vì, Hà Nội", 21.1298, 105.3872,
        "024.3387.4411", "district",
        ["CCCD","Tạm trú","Đăng ký xe"], 3.3, "", "Ba Vì"),

    # ══════════════════════════════════════════════
    # BỆNH VIỆN & Y TẾ
    # ══════════════════════════════════════════════
    svc("hn-bvhukytong", "Bệnh viện Hữu nghị Việt Đức", "Bệnh viện ngoại khoa hàng đầu",
        "health", "40 Tràng Thi, Hoàn Kiếm, Hà Nội", 21.0302, 105.8437,
        "024.3825.3531", "province",
        ["Ngoại khoa","Cấp cứu","Ghép tạng","Chấn thương"], 4.5,
        "https://vietduchospital.edu.vn", "Hoàn Kiếm"),

    svc("hn-bvsantraphuong", "Bệnh viện Sản Trung ương", "Bệnh viện sản phụ khoa hàng đầu",
        "health", "43 Tràng Thi, Hoàn Kiếm, Hà Nội", 21.0288, 105.8430,
        "024.3825.9011", "province",
        ["Sản khoa","Phụ khoa","Nhi sơ sinh","Thai sản"], 4.3,
        "", "Hoàn Kiếm"),

    svc("hn-bvnhikhamtrung", "Bệnh viện Nhi Trung ương", "Bệnh viện nhi hàng đầu Việt Nam",
        "health", "18/879 La Thành, Đống Đa, Hà Nội", 21.0228, 105.8267,
        "024.6273.8532", "province",
        ["Nhi khoa","Cấp cứu nhi","Ngoại nhi","Nội khoa trẻ em"], 4.4,
        "https://nhp.org.vn", "Đống Đa"),

    svc("hn-bvthanhxuan", "Bệnh viện Thanh Xuân", "Bệnh viện đa khoa Quận Thanh Xuân",
        "health", "Khuất Duy Tiến, Thanh Xuân, Hà Nội", 20.9938, 105.8124,
        "024.3563.7333", "district",
        ["Khám bệnh","Nội trú","Xét nghiệm","Cấp cứu"], 3.8, "", "Thanh Xuân"),

    svc("hn-ttyt-hadong", "Trung tâm Y tế Quận Hà Đông", "Dịch vụ y tế cấp quận Hà Đông",
        "health", "Quang Trung, Hà Đông, Hà Nội", 20.9601, 105.7791,
        "024.3382.3800", "district",
        ["Khám bệnh","Tiêm chủng","Kiểm tra sức khỏe"], 3.7, "", "Hà Đông"),

    svc("hn-ttyt-caugiay", "Trung tâm Y tế Quận Cầu Giấy", "Dịch vụ y tế cấp quận Cầu Giấy",
        "health", "Nghĩa Tân, Cầu Giấy, Hà Nội", 21.0408, 105.7868,
        "024.3768.2905", "district",
        ["Khám bệnh","Tiêm chủng","Xét nghiệm cơ bản"], 3.8, "", "Cầu Giấy"),

    svc("hn-ttyt-longbien", "Trung tâm Y tế Quận Long Biên", "Dịch vụ y tế cấp quận Long Biên",
        "health", "Bồ Đề, Long Biên, Hà Nội", 21.0501, 105.8801,
        "024.3827.3700", "district",
        ["Khám bệnh","Tiêm chủng","Cấp chứng nhận sức khỏe"], 3.7, "", "Long Biên"),
]

def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {s['id'] for s in existing}
    new_svcs = [s for s in HANOI_DATA if s['id'] not in existing_ids]
    updated   = [s for s in HANOI_DATA if s['id'] in existing_ids]

    # Update existing (replace với data mới hơn)
    existing_map = {s['id']: i for i, s in enumerate(existing)}
    for s in updated:
        existing[existing_map[s['id']]] = s

    # Append new
    combined = existing + new_svcs

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"OK! Them {len(new_svcs)} co quan moi, cap nhat {len(updated)} co quan Ha Noi")
    print(f"   Tong cong: {len(combined)} co quan")
    by_dist = {}
    for s in HANOI_DATA:
        d = s.get('district','?')
        by_dist[d] = by_dist.get(d,0) + 1
    print("\n   Phan bo theo quan/huyen:")
    for d,c in sorted(by_dist.items()):
        print(f"   {d}: {c}")

if __name__ == '__main__':
    main()
