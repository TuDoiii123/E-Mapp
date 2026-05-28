"""Fix 5 procedure có steps sai / thiếu dấu."""
import sys
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

FIXES = {
    'cap-doi-cccd': {
        'steps': (
            "Bước 1: Công dân mang CCCD / CMND cũ (bản gốc) đến cơ quan quản lý căn cước của "
            "Công an cấp tỉnh / huyện / xã được uỷ quyền, hoặc đăng ký qua ứng dụng VNeID "
            "(mức độ 4 - trực tuyến hoàn toàn).\n"
            "Bước 2: Cán bộ thu nhận thông tin sinh trắc học: ảnh chân dung, vân tay hai bàn tay, "
            "chữ ký điện tử; cập nhật thông tin cá nhân nếu có thay đổi (họ tên, địa chỉ...).\n"
            "Bước 3: Cán bộ in phiếu tiếp nhận hồ sơ, hẹn ngày trả kết quả. Thời hạn: 7 ngày "
            "làm việc kể từ ngày tiếp nhận (20 ngày với miền núi, hải đảo).\n"
            "Bước 4: Công dân nhận thẻ Căn cước mới tại nơi đã nộp hồ sơ hoặc qua dịch vụ bưu "
            "chính; nộp lại thẻ cũ / CMND theo yêu cầu của cán bộ."
        ),
        'conditions': (
            "Công dân Việt Nam từ đủ 14 tuổi; trẻ dưới 6 tuổi cha/mẹ hoặc người giám hộ làm thủ tục thay.\n"
            "Cấp mới: chưa có CCCD. Đổi: thẻ hết hạn, hỏng, thay đổi thông tin cá nhân hoặc địa chỉ.\n"
            "Không đang bị cấm cư trú, quản chế hoặc có lệnh truy nã của cơ quan có thẩm quyền."
        ),
    },
    'dang-ky-thuong-tru': {
        'steps': (
            "Bước 1: Người có nhu cầu chuẩn bị hồ sơ gồm Tờ khai đăng ký cư trú (Mẫu CT01 theo "
            "Thông tư 56/2021/TT-BCA), CCCD / Căn cước còn hiệu lực, giấy tờ chứng minh chỗ ở "
            "hợp lệ (hợp đồng thuê nhà, giấy tờ sở hữu, xác nhận của chủ hộ...).\n"
            "Bước 2: Nộp hồ sơ qua ứng dụng VNeID (ưu tiên) hoặc trực tiếp tại Công an cấp xã "
            "có thẩm quyền; cũng có thể nộp tại Cổng DVC quốc gia / tỉnh Thanh Hóa.\n"
            "Bước 3: Cán bộ Công an xác minh thông tin, cập nhật vào Cơ sở dữ liệu dân cư quốc "
            "gia. Thời hạn giải quyết: 7 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ.\n"
            "Bước 4: Công dân nhận kết quả qua VNeID (thông báo điện tử) hoặc tại trụ sở Công an "
            "cấp xã; thông tin thường trú được cập nhật trực tiếp vào CCCD / Căn cước."
        ),
        'conditions': (
            "Có chỗ ở hợp lệ tại địa chỉ đăng ký: sở hữu, thuê, mượn, ở nhờ có xác nhận chủ hộ.\n"
            "Không thuộc trường hợp bị cấm đăng ký thường trú theo Điều 24 Luật Cư trú 2020.\n"
            "Người chưa thành niên đăng ký theo cha, mẹ hoặc người giám hộ theo quy định pháp luật."
        ),
    },
    'dang-ky-ket-hon': {
        'steps': (
            "Bước 1: Hai bên nam nữ chuẩn bị hồ sơ gồm Tờ khai đăng ký kết hôn (Mẫu HTT-2014-01.1), "
            "CCCD / Căn cước công dân của cả hai bên còn hiệu lực, Xác nhận tình trạng hôn nhân "
            "do UBND cấp xã cấp trong vòng 6 tháng.\n"
            "Bước 2: Nộp hồ sơ trực tiếp tại Bộ phận một cửa UBND cấp xã có thẩm quyền hoặc nộp "
            "trực tuyến qua Cổng DVC quốc gia / tỉnh Thanh Hóa.\n"
            "Bước 3: Cán bộ tư pháp kiểm tra tính hợp lệ của hồ sơ, yêu cầu bổ sung nếu thiếu. "
            "Thời hạn giải quyết: trong ngày làm việc (trường hợp yếu tố nước ngoài: 5 ngày làm việc).\n"
            "Bước 4: Cán bộ tư pháp tổ chức lễ đăng ký kết hôn, yêu cầu hai bên xác nhận vào Sổ "
            "đăng ký kết hôn; cấp Giấy chứng nhận đăng ký kết hôn cho mỗi bên 01 bản."
        ),
        'conditions': (
            "Nam từ đủ 20 tuổi trở lên, nữ từ đủ 18 tuổi trở lên.\n"
            "Việc kết hôn do nam và nữ tự nguyện quyết định, không bị ép buộc hoặc lừa dối.\n"
            "Các bên không bị mất năng lực hành vi dân sự.\n"
            "Hai bên không thuộc trường hợp cấm kết hôn theo Luật Hôn nhân và Gia đình 2014."
        ),
    },
    'dang-ky-khai-sinh': {
        'steps': (
            "Bước 1: Cha hoặc mẹ (hoặc người có trách nhiệm) chuẩn bị hồ sơ gồm Giấy chứng sinh "
            "do cơ sở y tế cấp, CCCD của cha/mẹ, Giấy đăng ký kết hôn của cha mẹ (nếu có).\n"
            "Bước 2: Nộp hồ sơ tại Bộ phận một cửa UBND cấp xã nơi cư trú của mẹ (hoặc cha nếu "
            "mẹ không có nơi cư trú ở Việt Nam); hoặc nộp trực tuyến qua Cổng DVC.\n"
            "Bước 3: Cán bộ tư pháp kiểm tra hồ sơ, nếu hợp lệ ghi vào Sổ đăng ký khai sinh. "
            "Thời hạn: trong ngày làm việc hoặc chậm nhất ngày làm việc tiếp theo.\n"
            "Bước 4: Người yêu cầu nhận Trích lục khai sinh (01 bản chính thức) tại bộ phận một cửa."
        ),
        'conditions': (
            "Đăng ký khai sinh thực hiện trong vòng 60 ngày kể từ ngày sinh.\n"
            "Trẻ sinh sống trong thời gian đủ 24 giờ mới làm thủ tục đăng ký.\n"
            "Trường hợp đăng ký quá hạn cần giải trình lý do và có xác nhận của UBND cấp xã."
        ),
    },
    'cap-phieu-lltp': {
        'steps': (
            "Bước 1: Người có yêu cầu chuẩn bị hồ sơ gồm Tờ khai yêu cầu cấp Phiếu lý lịch tư "
            "pháp (theo mẫu), bản sao CCCD / Căn cước còn hiệu lực. Xác định loại phiếu: Số 1 "
            "(cá nhân tự yêu cầu) hoặc Số 2 (cơ quan, tổ chức yêu cầu).\n"
            "Bước 2: Nộp hồ sơ trực tiếp tại Bộ phận một cửa Sở Tư pháp tỉnh Thanh Hóa (34 Đại "
            "lộ Lê Lợi) hoặc nộp trực tuyến qua Cổng DVC quốc gia / tỉnh; có thể nộp qua bưu chính.\n"
            "Bước 3: Sở Tư pháp kiểm tra, tra cứu cơ sở dữ liệu lý lịch tư pháp, xác nhận kết "
            "quả. Thời hạn: 10 ngày làm việc (20 ngày nếu cần xác minh từ nước ngoài).\n"
            "Bước 4: Người yêu cầu nhận Phiếu LLTP tại nơi nộp hồ sơ, qua bưu chính hoặc nhận "
            "Phiếu LLTP điện tử qua ứng dụng VNeID (nếu đã đăng ký)."
        ),
        'conditions': (
            "Cá nhân có quyền yêu cầu cấp Phiếu LLTP số 1 để sử dụng theo nhu cầu cá nhân.\n"
            "Cơ quan, tổ chức yêu cầu cấp Phiếu số 2 phải có văn bản đề nghị kèm theo uỷ quyền.\n"
            "Trường hợp uỷ quyền: cần Giấy uỷ quyền có công chứng và CCCD người được uỷ quyền."
        ),
    },
}

with app.app_context():
    updated = 0
    for proc_id, data in FIXES.items():
        result = db.session.execute(text("""
            UPDATE public.procedures
            SET steps      = :steps,
                conditions = :conds
            WHERE id = :pid
        """), {'steps': data['steps'], 'conds': data['conditions'], 'pid': proc_id})
        updated += result.rowcount
        status = "OK" if result.rowcount else "NOT FOUND"
        print(f"  {status}  {proc_id}")
    db.session.commit()
    print(f"\nXong: {updated} thu tuc da duoc sua.")
