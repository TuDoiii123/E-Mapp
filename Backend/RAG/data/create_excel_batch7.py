"""
Batch 7 — thêm ~60 bản ghi Q&A chung toàn quốc, đa dạng chủ đề.
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

BHXH_B7 = [
    {
        'id': 'b7-bh-001', 'category': 'bhxh', 'procedure': 'tra_cuu_bhxh', 'level': 'district',
        'source': 'baohiemxahoi.gov.vn; App VssID',
        'question': 'Tra cứu quá trình đóng BHXH của bản thân ở đâu? Kiểm tra sổ BHXH online như thế nào?',
        'answer': '''TRA CỨU QUÁ TRÌNH ĐÓNG BHXH:

1. APP VssID (Chính thức của BHXH Việt Nam):
   - Tải: CH Play / App Store → Tìm "VssID"
   - Đăng nhập bằng Mã số BHXH (ghi trên Sổ BHXH) + Mật khẩu
   - Xem: Quá trình đóng BHXH từng tháng, tổng số tháng, lương đóng BH, sổ BHXH điện tử

2. CỔNG WEB: baohiemxahoi.gov.vn → "Tra cứu thông tin cá nhân" → Nhập mã số BHXH

3. TẠI CƠ QUAN BHXH: Mang CCCD đến BHXH huyện → Cán bộ tra cứu và in sao kê

MÃ SỐ BHXH Ở ĐÂU?
- Ghi trên mặt sau Sổ BHXH (10 chữ số)
- Ghi trên Thẻ BHYT (số 10 chữ số)
- Từ 2021: Mã số BHXH = Mã số định danh cá nhân (số CCCD)

NẾU PHÁT HIỆN THIẾU THÁNG ĐÓNG:
1. Kiểm tra với bộ phận kế toán công ty (có thể công ty chưa nộp hồ sơ)
2. Phản ánh với Chi nhánh BHXH nơi công ty đặt trụ sở
3. Nếu công ty đã giải thể/phá sản: BHXH giải quyết theo quy trình đặc biệt

SỐ TỔ ĐƯỜNG DÂY NÓNG BHXH: 1800.9068 (miễn phí).''',
    },
    {
        'id': 'b7-bh-002', 'category': 'bhxh', 'procedure': 'cap_so_bhxh', 'level': 'district',
        'source': 'Luật BHXH 2014; Quyết định 505/QĐ-BHXH',
        'question': 'Mất sổ BHXH thì phải làm sao? Thủ tục cấp lại sổ BHXH ở đâu?',
        'answer': '''Từ 2021, Sổ BHXH điện tử thay thế sổ giấy — bạn có thể xem trên App VssID mà không cần sổ giấy vật lý.

Tuy nhiên, nếu cần SỔ BHXH VẬT LÝ (giấy) để làm các thủ tục cũ còn yêu cầu:

CẤP LẠI SỔ BHXH tại BHXH cấp huyện nơi đang tham gia BHXH (nơi công ty đặt trụ sở hoặc nơi cư trú nếu BHXH tự nguyện).

HỒ SƠ:
1. Tờ khai cấp lại sổ BHXH (Mẫu TK1-TS — khai tại BHXH huyện)
2. CCCD (bản gốc để đối chiếu)
3. Văn bản xác nhận của đơn vị sử dụng lao động (nếu đang đi làm)

Thời gian: 10 ngày làm việc. Lệ phí: Miễn phí.

XÁC NHẬN SỔ BHXH (thay vì cấp lại):
Nhiều thủ tục hiện nay chấp nhận Bản xác nhận quá trình đóng BHXH (in từ VssID hoặc BHXH cấp) thay vì Sổ BHXH vật lý.

ĐỒNG THỜI: Đề nghị BHXH cấp Sổ BHXH điện tử → lưu trong VssID → Xuất trình khi cần.

Nếu sổ bị hư hỏng: Nộp kèm Sổ cũ bị hỏng để BHXH thu hồi.''',
    },
    {
        'id': 'b7-bh-003', 'category': 'bhyt', 'procedure': 'dang_ky_bhyt_ban_dau', 'level': 'district',
        'source': 'Luật BHYT 2014 sửa đổi; Thông tư 40/2015/TT-BYT',
        'question': 'Đăng ký cơ sở khám chữa bệnh ban đầu BHYT ở đâu? Khi nào được đổi cơ sở đăng ký?',
        'answer': '''Cơ sở KCB ban đầu là nơi bạn đăng ký khám BHYT đầu tiên (tuyến xã hoặc tuyến huyện).

ĐĂNG KÝ BAN ĐẦU:
- Người lao động: Đơn vị sử dụng lao động đăng ký hộ khi mua thẻ BHYT
- BHXH tự nguyện: Tự chọn khi đăng ký tham gia
- Trẻ em dưới 6 tuổi: Tự động đăng ký tại trạm y tế xã nơi cư trú

THAY ĐỔI CƠ SỞ KCB BAN ĐẦU:
Chỉ được thay đổi 1 LẦN/NĂM vào đầu năm (tháng 1) hoặc khi:
- Thay đổi nơi cư trú/làm việc (được thay đổi bất cứ lúc nào)
- Cơ sở KCB ban đầu giải thể hoặc không còn hợp đồng BHYT

THỦ TỤC THAY ĐỔI:
1. Người lao động: Thông báo với bộ phận nhân sự/kế toán công ty → Công ty điều chỉnh
2. Cá nhân (BHXH tự nguyện): Đến BHXH huyện mang CCCD + Thẻ BHYT → Điều chỉnh ngay

CÁC LOẠI CƠ SỞ ĐƯỢC CHỌN:
- Trạm y tế xã/phường (tuyến 1): Miễn phí hoàn toàn, nhưng ít thiết bị
- Phòng khám đa khoa (tuyến huyện): Thanh toán 80% chi phí
- BV huyện/quận (tuyến huyện): Thanh toán 80%
Không được đăng ký thẳng vào BV tỉnh hay trung ương.

Tra cứu danh sách cơ sở KCB BHYT: baohiemxahoi.gov.vn → "Tra cứu cơ sở KCB".''',
    },
    {
        'id': 'b7-bh-004', 'category': 'bhxh', 'procedure': 'tu_tat_nghe_nghiep', 'level': 'district',
        'source': 'Luật An toàn vệ sinh lao động 2015; Luật BHXH 2014',
        'question': 'Bệnh nghề nghiệp (điếc nghề nghiệp, bụi phổi...) được hưởng chế độ gì?',
        'answer': '''Bệnh nghề nghiệp là bệnh phát sinh do điều kiện lao động có hại gây ra cho người lao động.

DANH MỤC BỆNH NGHỀ NGHIỆP ĐƯỢC BỒI THƯỜNG (34 loại theo Thông tư 15/2016/TT-BYT):
- Bụi phổi silic, Bụi phổi than, Bụi phổi amiăng
- Nhiễm độc chì, nhiễm độc benzene, nhiễm độc thủy ngân
- Điếc nghề nghiệp (do tiếng ồn)
- Bệnh rung chuyển nghề nghiệp
- Ung thư nghề nghiệp do amiăng, các hóa chất...

ĐIỀU KIỆN ĐƯỢC HƯỞNG:
1. Được xác định mắc bệnh nghề nghiệp bởi cơ sở y tế có thẩm quyền
2. Suy giảm khả năng lao động từ 5% trở lên

QUY TRÌNH GIÁM ĐỊNH:
1. Đến khám tại Bệnh viện có khoa/phòng bệnh nghề nghiệp hoặc Trung tâm Y tế lao động
2. Hội đồng giám định y khoa xác định: Bệnh nghề nghiệp + % suy giảm lao động
3. Nộp hồ sơ hưởng chế độ tại BHXH

MỨC HỞ TRỌNG:
- Suy giảm 5–30%: Trợ cấp một lần (theo công thức tương tự TNLĐ)
- Suy giảm ≥ 31%: Trợ cấp hàng tháng

NGƯỜI SỬ DỤNG LAO ĐỘNG:
- Phải thanh toán chi phí khám giám định bệnh nghề nghiệp
- Phải bồi thường thêm (ngoài BHXH) nếu vi phạm ATVSLĐ gây ra bệnh

Trung tâm Sức khỏe Nghề nghiệp - Bộ Y tế: 1800.9095.''',
    },
]

DAN_SU_B7 = [
    {
        'id': 'b7-ds-001', 'category': 'dan_su', 'procedure': 'di_chuc', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015',
        'question': 'Lập di chúc hợp lệ cần những điều kiện gì? Có cần công chứng không?',
        'answer': '''Di chúc là sự thể hiện ý chí của cá nhân nhằm chuyển tài sản sau khi chết.

ĐIỀU KIỆN DI CHÚC HỢP LỆ:
1. Người lập di chúc: Từ đủ 18 tuổi, minh mẫn, không bị lừa dối hoặc đe dọa
2. Nội dung: Không vi phạm pháp luật, đạo đức xã hội
3. Hình thức: Đúng quy định pháp luật

CÁC HÌNH THỨC DI CHÚC:
1. DI CHÚC BẰNG VĂN BẢN CÓ CÔNG CHỨNG/CHỨNG THỰC (an toàn nhất):
   - Lập tại Văn phòng Công chứng
   - Phí: Theo biểu phí công chứng (thường 50.000–300.000 đồng)
   - Hiệu lực cao nhất, khó bị tranh chấp nhất

2. DI CHÚC BẰNG VĂN BẢN KHÔNG CÓ CÔNG CHỨNG:
   - Tự viết tay hoặc đánh máy + ký tên + ngày tháng
   - Cần 2 người làm chứng không thuộc diện thừa kế
   - Hợp lệ nhưng có thể bị tranh chấp hơn

3. DI CHÚC MIỆNG (khi nguy kịch, không thể viết):
   - Nói trước ≥ 2 người làm chứng
   - Các chứng nhân ghi lại, ký xác nhận trong 5 ngày
   - Mất hiệu lực sau 3 tháng nếu người lập di chúc còn sống và minh mẫn

NGƯỜI ĐƯỢC HƯỞNG DI SẢN BẮT BUỘC (dù không có trong di chúc):
Con chưa thành niên, cha/mẹ già, vợ/chồng không có khả năng lao động → Hưởng ít nhất 2/3 suất thừa kế theo pháp luật.

BẢO QUẢN DI CHÚC: Gửi tại Văn phòng Công chứng hoặc UBND xã (ghi vào Sổ di chúc); thông báo cho người thừa kế biết nơi lưu giữ.''',
    },
    {
        'id': 'b7-ds-002', 'category': 'dan_su', 'procedure': 'hop_dong_vay_tien', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Luật Các TCTD 2024',
        'question': 'Cho vay tiền cá nhân (cho bạn bè, người thân vay) có cần hợp đồng không? Lãi suất tối đa là bao nhiêu?',
        'answer': '''CHO VAY CÁ NHÂN (không phải tổ chức tín dụng):

CÓ CẦN HỢP ĐỒNG KHÔNG?
Luật không BẮT BUỘC, nhưng KHUYẾN CÁO MẠNH NÊN CÓ để tránh tranh chấp.
Hợp đồng vay tiền có thể: Viết tay + ký tên + điểm chỉ, hoặc công chứng (an toàn hơn).

HỢP ĐỒNG VAY NÊN GHI RÕ:
- Họ tên, CCCD, địa chỉ cả hai bên
- Số tiền vay (bằng số và chữ)
- Ngày vay, ngày trả
- Lãi suất (nếu có tính lãi)
- Tài sản thế chấp (nếu có)
- Hậu quả nếu vi phạm

LÃI SUẤT TỐI ĐA THEO PHÁP LUẬT:
- Giao dịch dân sự giữa cá nhân: Tối đa 20%/năm (Điều 468 BLDS 2015)
- Tính lãi vượt quá 20%/năm: Phần vượt không có hiệu lực pháp lý (người vay chỉ phải trả 20%)
- LÃI SUẤT CHO VAY NẶNG LÃI (từ 100%/năm): Cấu thành tội cho vay lãi nặng, phạt đến 3 năm tù

KHI NGƯỜI VAY KHÔNG TRẢ:
1. Thương lượng, gửi thư nhắc nợ
2. Khởi kiện ra TAND (kèm hợp đồng/giấy tờ bằng chứng)
3. Tòa tuyên + Thi hành án dân sự (nếu người vay không chịu trả)

LƯU Ý: Đòi nợ kiểu "xã hội đen" (đến nhà gây áp lực, đe dọa) → Vi phạm hình sự (tội cưỡng đoạt tài sản).''',
    },
    {
        'id': 'b7-ds-003', 'category': 'dan_su', 'procedure': 'boi_thuong_thiet_hai', 'level': 'district',
        'source': 'Bộ luật Dân sự 2015',
        'question': 'Bị người khác gây thiệt hại (tài sản, sức khỏe) thì đòi bồi thường như thế nào?',
        'answer': '''Quyền yêu cầu bồi thường thiệt hại ngoài hợp đồng được quy định tại Điều 584–605 BLDS 2015.

ĐIỀU KIỆN ĐỂ ĐƯỢC BỒI THƯỜNG:
1. Có hành vi gây thiệt hại (cố ý hoặc vô ý)
2. Có thiệt hại thực tế xảy ra (mất tài sản, thương tích, tinh thần...)
3. Có mối quan hệ nhân quả giữa hành vi và thiệt hại

CÁC KHOẢN BỒI THƯỜNG:
- THIỆT HẠI VỀ TÀI SẢN: Giá trị tài sản bị mất/hỏng + Chi phí sửa chữa + Thu nhập bị mất do không có tài sản sản xuất
- THIỆT HẠI VỀ SỨC KHỎE: Chi phí điều trị + Thu nhập mất trong thời gian điều trị + Tổn thất tinh thần (tối đa 50 tháng lương cơ sở)
- THIỆT HẠI VỀ TÍNH MẠNG: Chi phí cứu chữa trước khi chết + Tiền cấp dưỡng cho người phụ thuộc + Bù đắp tinh thần (tối đa 100 tháng lương cơ sở)

QUY TRÌNH ĐÒI BỒI THƯỜNG:
1. Thu thập bằng chứng: Ảnh chụp, hóa đơn sửa chữa, giấy viện phí, biên bản công an...
2. Gửi thư yêu cầu bồi thường bằng văn bản (lưu bản copy)
3. Thương lượng trực tiếp
4. Hòa giải tại UBND xã (nếu muốn)
5. Khởi kiện ra TAND huyện nếu không thỏa thuận được

THỜI HIỆU KHỞI KIỆN: 3 năm kể từ ngày biết/phải biết quyền lợi bị xâm phạm.''',
    },
]

HANH_CHINH_B7 = [
    {
        'id': 'b7-hc-001', 'category': 'hanh_chinh', 'procedure': 'phi_le_phi', 'level': 'province',
        'source': 'Luật Phí và Lệ phí 2015; Nghị định 120/2016/NĐ-CP',
        'question': 'Phí và lệ phí hành chính khác nhau như thế nào? Những thủ tục nào được miễn phí hoàn toàn?',
        'answer': '''PHÂN BIỆT PHÍ VÀ LỆ PHÍ:

LỆ PHÍ: Thu để bù đắp chi phí thực hiện dịch vụ hành chính Nhà nước. Mức thu do Nhà nước quy định, không vì mục tiêu lợi nhuận.
Ví dụ: Lệ phí cấp CCCD (70.000–135.000 đồng), lệ phí đăng ký doanh nghiệp (50.000 đồng), lệ phí cấp hộ chiếu (200.000 đồng)

PHÍ: Thu khi Nhà nước cung cấp dịch vụ công theo yêu cầu.
Ví dụ: Phí thẩm định hồ sơ xây dựng, phí đăng kiểm xe, phí sử dụng đường bộ

THỦ TỤC ĐƯỢC MIỄN LỆ PHÍ HOÀN TOÀN (không thu tiền):
HỘ TỊCH (theo Nghị quyết 97/2019/QH14 từ 01/01/2021):
- Đăng ký khai sinh, khai tử, kết hôn, nhận cha mẹ con
- Thay đổi, cải chính, bổ sung hộ tịch
- Xác nhận tình trạng hôn nhân

CƯ TRÚ:
- Đăng ký thường trú, tạm trú
- Xóa đăng ký, cấp phiếu thông tin cư trú

CCCD/CĂN CƯỚC:
- Cấp lần đầu (khi chưa có CCCD bao giờ)
- Đổi trong đợt quốc gia (theo thông báo của Bộ CA)

HỘ NGHÈO, HỘ CHÍNH SÁCH:
- Miễn mọi phí, lệ phí hành chính không bắt buộc
- Miễn án phí khi khởi kiện (nếu thuộc diện)

Tra cứu danh sách đầy đủ tại: thutuchanhchinh.gov.vn → Xem chi tiết từng TTHC.''',
    },
    {
        'id': 'b7-hc-002', 'category': 'hanh_chinh', 'procedure': 'uy_quyen_lam_thu_tuc', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Nghị định 23/2015/NĐ-CP',
        'question': 'Có thể ủy quyền cho người khác làm thủ tục hành chính thay không? Cần giấy tờ gì?',
        'answer': '''Hầu hết thủ tục hành chính đều cho phép ủy quyền cho người khác làm thay, trừ một số trường hợp phải có mặt trực tiếp.

CÁC THỦ TỤC CẦN CÓ MẶT TRỰC TIẾP (không được ủy quyền):
- Cấp CCCD/Căn cước (phải lấy vân tay, ảnh)
- Cấp hộ chiếu (lấy ảnh, ký tên)
- Đăng ký kết hôn (phải cả hai bên cùng có mặt ký)
- Phỏng vấn visa
- Thi bằng lái xe

CÁC THỦ TỤC CÓ THỂ ỦY QUYỀN:
- Nộp/nhận hồ sơ hộ tịch (khai sinh, khai tử, thay đổi hộ tịch)
- Làm thủ tục đất đai (nộp hồ sơ sang tên, đăng ký biến động)
- Nộp hồ sơ kinh doanh
- Nhận kết quả giải quyết thủ tục hành chính

GIẤY ỦY QUYỀN CẦN:
- Đơn giản (nhận kết quả, nộp hồ sơ): Giấy ủy quyền viết tay + CCCD photo của người ủy quyền
- Phức tạp (giao dịch BĐS, tài sản lớn): Hợp đồng ủy quyền có công chứng

MẪU GIẤY ỦY QUYỀN ĐƠN GIẢN (viết tay):
"Tôi [Họ tên], CCCD số [...], địa chỉ [...], ủy quyền cho [Họ tên người được ủy quyền], CCCD số [...] thay mặt tôi [nêu cụ thể việc được ủy quyền] tại [nơi làm thủ tục].
Ký xác nhận: [Chữ ký + Ngày tháng]"''',
    },
    {
        'id': 'b7-hc-003', 'category': 'hanh_chinh', 'procedure': 'boi_thuong_hanh_chinh', 'level': 'province',
        'source': 'Luật Trách nhiệm bồi thường Nhà nước 2017',
        'question': 'Bị cơ quan hành chính gây oan sai, thiệt hại có được bồi thường không? Mức bồi thường thế nào?',
        'answer': '''NHÀ NƯỚC BỒI THƯỜNG khi cán bộ, công chức gây thiệt hại trong khi thi hành công vụ TRÁI PHÁP LUẬT.

TRƯỜNG HỢP ĐƯỢC BỒI THƯỜNG:
Hành chính: Quyết định hành chính trái luật, hành vi hành chính trái luật gây thiệt hại.
Ví dụ: Thu hồi đất không đúng quy định; xử phạt hành chính sai; từ chối cấp phép trái luật; cưỡng chế trái pháp luật.

Tố tụng hình sự: Bắt giam oan; truy tố oan; xét xử oan.
Thi hành án: Thi hành án sai.

CÁC KHOẢN BỒI THƯỜNG:
- Thiệt hại vật chất trực tiếp: Thu nhập bị mất, tài sản bị tịch thu/phá hủy sai
- Tổn thất tinh thần: Tối đa 30 ngày lương cơ sở/tháng bị oan (bị giam oan)
- Chi phí khắc phục hậu quả: Thuê luật sư, đi lại làm thủ tục...

QUY TRÌNH YÊU CẦU BỒI THƯỜNG:
1. Có văn bản xác định hành vi trái pháp luật của cơ quan (bản án tòa, quyết định hủy bỏ)
2. Gửi Đơn yêu cầu bồi thường đến cơ quan có trách nhiệm bồi thường (trong 3 năm)
3. Thương lượng bồi thường (tối đa 45 ngày)
4. Không thỏa thuận: Khởi kiện ra Tòa

Trợ giúp pháp lý miễn phí: Trung tâm TGPL Nhà nước tỉnh hoặc Bộ Tư pháp: 1900.6278.''',
    },
    {
        'id': 'b7-hc-004', 'category': 'hanh_chinh', 'procedure': 'tiep_nhan_phan_anh', 'level': 'province',
        'source': 'Nghị định 20/2008/NĐ-CP; Nghị định 09/2019/NĐ-CP',
        'question': 'Phản ánh kiến nghị về quy định hành chính phiền hà, bất hợp lý thì gửi ở đâu?',
        'answer': '''Công dân có quyền phản ánh, kiến nghị về các quy định hành chính gây phiền hà, bất hợp lý.

CÁC KÊNH PHẢN ÁNH KIẾN NGHỊ:

1. CỔNG TIẾP NHẬN PHẢN ÁNH KIẾN NGHỊ QUỐC GIA:
   Website: phananhkiennghigv.gov.vn
   Tiếp nhận: Phản ánh về quy định hành chính, quy định pháp luật cần sửa đổi
   Văn phòng Chính phủ trả lời trong 30 ngày

2. ĐƯỜNG DÂY NÓNG:
   - Văn phòng Chính phủ: 1022 (hỗ trợ DVC, phản ánh thủ tục)
   - Thanh tra Chính phủ: 1800.1166 (phản ánh tham nhũng, tiêu cực)

3. TRỰC TUYẾN:
   - dichvucong.gov.vn → "Phản ánh kiến nghị"
   - App "Hỏi đáp chính sách" của Văn phòng Chính phủ

4. ĐẾN TRỰC TIẾP:
   - Trụ sở tiếp công dân tỉnh (địa chỉ tại UBND tỉnh)
   - Đại biểu Quốc hội tiếp cử tri (định kỳ)
   - Đại biểu HĐND tỉnh/huyện/xã

KẾT QUẢ SAU PHẢN ÁNH:
- Cơ quan nhận có trách nhiệm trả lời trong 30 ngày
- Kiến nghị hợp lý được xem xét sửa đổi quy định
- Nhiều TTHC đã được rút gọn/bãi bỏ sau phản ánh của người dân

Đây là quyền dân chủ trực tiếp — hãy sử dụng để cải thiện môi trường hành chính.''',
    },
]

GIAO_THONG_B7 = [
    {
        'id': 'b7-gt-001', 'category': 'giao_thong', 'procedure': 'phat_nguoi_di_bo', 'level': 'district',
        'source': 'Nghị định 100/2019/NĐ-CP sửa đổi 123/2021/NĐ-CP',
        'question': 'Người đi bộ vi phạm giao thông bị phạt không? Các lỗi phổ biến của người đi bộ?',
        'answer': '''Người đi bộ CŨNG bị xử phạt vi phạm giao thông theo Nghị định 100/2019/NĐ-CP.

CÁC LỖI VI PHẠM CỦA NGƯỜI ĐI BỘ VÀ MỨC PHẠT:

VƯỢT QUA DẢI PHÂN CÁCH, HÀNG RÀO (nơi có biển cấm):
Phạt 60.000–100.000 đồng

KHÔNG ĐI ĐÚNG PHẦN ĐƯỜNG DÀNH CHO NGƯỜI ĐI BỘ:
- Đi xuống lòng đường (nơi có vỉa hè): Phạt 60.000–100.000 đồng
- Qua đường không đúng nơi quy định, không chờ tín hiệu: Phạt 60.000–100.000 đồng

SỬ DỤNG ĐIỆN THOẠI, THIẾT BỊ ÂM THANH KHI QUA ĐƯỜNG:
Phạt 60.000–100.000 đồng

NẰM, NGỒI TRÊN ĐƯỜNG BỘ NƠI CÓ PHƯƠNG TIỆN QUA LẠI:
Phạt 100.000–200.000 đồng

MANG VẬT CỒNG KỀNH CẢN TRỞ GIAO THÔNG:
Phạt 60.000–100.000 đồng

THỰC TẾ: Tại Việt Nam, xử phạt người đi bộ chưa phổ biến nhưng hoàn toàn hợp pháp.
Trong các đợt ra quân trật tự ATGT, CSGT có thể nhắc nhở hoặc xử phạt.

AN TOÀN KHI QUA ĐƯỜNG:
- Đi đúng vạch kẻ đường hoặc cầu đi bộ
- Nhìn cả hai chiều trước khi qua
- Không nhìn điện thoại khi qua đường
- Mặc quần áo sáng màu, phản quang ban đêm''',
    },
    {
        'id': 'b7-gt-002', 'category': 'giao_thong', 'procedure': 'xu_phat_online', 'level': 'province',
        'source': 'Nghị định 100/2019/NĐ-CP; Thông tư 65/2020/TT-BCA',
        'question': 'Bị phạt nguội (camera ghi hình vi phạm) thì xử lý như thế nào? Nộp phạt ở đâu?',
        'answer': '''PHẠT NGUỘI là hình thức xử phạt vi phạm giao thông qua camera giám sát, không cần cảnh sát có mặt tại hiện trường.

KIỂM TRA XEM CÓ BỊ PHẠT NGUỘI KHÔNG:
1. App "Phạt Nguội" — của Bộ Công an (tải CH Play/App Store)
2. App "iTraffic" — tra cứu thông tin xe và vi phạm
3. Website: csgt.vn → "Tra cứu phương tiện vi phạm"
4. Gọi 1088 (đường dây tra cứu vi phạm, tính phí)
5. Đến trực tiếp Phòng CSGT địa phương (mang Giấy đăng ký xe + GPLX)

QUY TRÌNH XỬ LÝ PHẠT NGUỘI:
1. Phòng CSGT gửi thông báo vi phạm qua đường bưu điện (địa chỉ đăng ký xe)
2. Chủ xe/người vi phạm đến Phòng CSGT trong 10 ngày kể từ ngày nhận thông báo
3. Xem xét hình ảnh/video vi phạm
4. Ký biên bản vi phạm → Nộp phạt

NỘNG PHẠT Ở ĐÂU:
- Trực tiếp tại Phòng CSGT hoặc Kho bạc Nhà nước
- Online: VNePay, MoMo, ZaloPay (quét QR trên thông báo phạt)
- App "Phạt Nguội" → Thanh toán online

HẬU QUẢ NẾU KHÔNG NỘP PHẠT:
- Xe bị "khóa" hệ thống — không đăng kiểm được
- Bị truy thu khi làm thủ tục liên quan đến xe
- Bị cưỡng chế thi hành

Thời hiệu xử phạt vi phạm giao thông: 1 năm kể từ ngày vi phạm.''',
    },
    {
        'id': 'b7-gt-003', 'category': 'giao_thong', 'procedure': 'bao_hiem_xe', 'level': 'district',
        'source': 'Luật Kinh doanh bảo hiểm 2022; Nghị định 67/2023/NĐ-CP',
        'question': 'Bảo hiểm trách nhiệm dân sự xe cơ giới bắt buộc là gì? Không mua bị phạt bao nhiêu?',
        'answer': '''BẢO HIỂM TNDS XE CƠ GIỚI BẮT BUỘC (bảo hiểm bắt buộc) là loại bảo hiểm mọi chủ xe phải mua theo Luật.

MỨC PHÍ 2024 (theo Nghị định 67/2023/NĐ-CP):
- Xe máy dưới 50cc: 55.000 đồng/năm
- Xe máy từ 50–175cc: 60.000 đồng/năm
- Xe máy trên 175cc: 100.000 đồng/năm
- Ô tô con (dưới 6 chỗ, không kinh doanh vận tải): 471.200 đồng/năm
- Ô tô từ 6–11 chỗ: 719.200 đồng/năm

QUYỀN LỢI BỒI THƯỜNG:
- Thiệt hại thân thể người bị nạn: Tối đa 150 triệu đồng/người
- Thiệt hại tài sản người bị nạn: Tối đa 150 triệu đồng/vụ
- Chủ xe không phải bồi thường bằng tiền túi (BH trả thay)

KHÔNG PHẢI TRÁCH NHIỆM CỦA BH TNDS:
- Thiệt hại của chính chủ xe (bảo hiểm thân vỏ/xe mới bồi thường)
- Tài sản trong xe bị hỏng
- Tai nạn cố tình gây ra

PHẠT KHI KHÔNG CÓ BẢO HIỂM:
- Xe máy: 100.000–200.000 đồng
- Ô tô: 400.000–600.000 đồng + Tước GPLX 1–3 tháng nếu gây tai nạn

MUA BẢO HIỂM Ở ĐÂU:
- Các công ty bảo hiểm: Bảo Việt, PJICO, PTI, Bảo Minh, PVI... (giá như nhau do Nhà nước quy định)
- Online qua app/website của công ty BH (tiện nhất)
- Đại lý bảo hiểm tại các cây xăng, đại lý xe''',
    },
]

MOI_TRUONG_B7 = [
    {
        'id': 'b7-mt-001', 'category': 'moi_truong', 'procedure': 'tiet_kiem_dien', 'level': 'ward',
        'source': 'Luật Sử dụng năng lượng tiết kiệm và hiệu quả 2010',
        'question': 'Các biện pháp tiết kiệm điện tại nhà hiệu quả nhất? Quy định về sử dụng điện tiết kiệm?',
        'answer': '''Việt Nam có Luật Sử dụng Năng lượng Tiết kiệm và Hiệu quả 2010, khuyến khích và bắt buộc tiết kiệm điện.

10 BIỆN PHÁP TIẾT KIỆM ĐIỆN TẠI NHÀ HIỆU QUẢ NHẤT:

1. ĐIỀU HÒA: Đặt ở 26°C (mỗi độ giảm tiêu thụ 8% điện); tắt khi ngủ đủ ấm; dùng quạt + điều hòa kết hợp
2. ĐÈN: Thay đèn sợi đốt/huỳnh quang cũ bằng đèn LED (tiết kiệm 60–80% điện đèn)
3. TỦ LẠNH: Không mở cửa thường xuyên; không để thực phẩm nóng vào tủ; giữ tủ cách tường 10–15cm
4. NỒI CƠM ĐIỆN: Nấu xong rút điện, không hầm giữ nhiệt (tốn điện gấp đôi)
5. MÁY GIẶT: Giặt đầy máy mới bật; dùng nước lạnh (không nóng) tiết kiệm 90% điện giặt
6. TI VI, THIẾT BỊ: Tắt hẳn (không chế độ standby/chờ) khi không dùng — standby tiêu thụ 10–20% điện/thiết bị
7. BỘ LƯU ĐIỆN (UPS): Tắt khi máy tính không sử dụng
8. BÌNH NÓNG LẠNH: Chỉ bật trước khi tắm 15 phút; không để bật cả ngày
9. ĐIỆN MÁY GIỜ CAO ĐIỂM: Hạn chế dùng thiết bị công suất lớn từ 17:00–20:00
10. SỬA CHỮA RỈDỆN: Kiểm tra hệ thống điện, thay dây cũ để giảm hao tổn

CHƯƠNG TRÌNH TIẾT KIỆM ĐIỆN:
- Mỗi hộ tiết kiệm ≥ 10%/tháng: Được thưởng tiền từ một số công ty điện lực
- Hộ dùng điện tiết kiệm (bậc 1–2): Trả ít hơn hộ dùng nhiều (biểu giá lũy tiến)

CÁC THIẾT BỊ ĐƯỢC DÁN NHÃN NĂNG LƯỢNG:
Khi mua điều hòa, tủ lạnh, máy giặt: Chọn loại 5 sao năng lượng (tiết kiệm nhất).''',
    },
    {
        'id': 'b7-mt-002', 'category': 'moi_truong', 'procedure': 'quyen_thong_tin_mt', 'level': 'province',
        'source': 'Luật Bảo vệ môi trường 2020; Nghị định 08/2022/NĐ-CP',
        'question': 'Người dân có quyền biết thông tin môi trường không? Lấy thông tin ở đâu?',
        'answer': '''Quyền tiếp cận thông tin môi trường là quyền của mọi công dân theo Luật BVMT 2020 và Luật Tiếp cận thông tin 2016.

THÔNG TIN MÔI TRƯỜNG CÔNG DÂN CÓ QUYỀN BIẾT:
- Kết quả quan trắc chất lượng không khí, nước, đất công khai
- Báo cáo hiện trạng môi trường quốc gia, tỉnh (phát hành hàng năm)
- Danh sách cơ sở gây ô nhiễm nghiêm trọng (đang bị xử lý)
- Kết quả thanh tra, kiểm tra môi trường
- Thông tin về sự cố môi trường, tai nạn hóa chất

KÊNH TIẾP CẬN THÔNG TIN:
1. Cổng thông tin Bộ TNMT: monre.gov.vn
2. Tổng cục Môi trường: vea.gov.vn
3. Sở TNMT tỉnh (website chính thức)
4. App "Quan trắc môi trường" — dữ liệu chất lượng không khí thời gian thực
5. Cổng dữ liệu mở quốc gia: data.gov.vn → tìm "môi trường"

QUAN TRẮC CHẤT LƯỢNG KHÔNG KHÍ:
- AQI (Air Quality Index): Tốt (0-50), Trung bình (51-100), Kém (101-150), Xấu (151-200), Nguy hại (>200)
- App: AirVisual, Pam Air, IQAir — theo dõi AQI thành phố của bạn

YÊU CẦU CUNG CẤP THÔNG TIN MÔI TRƯỜNG:
- Gửi Phiếu yêu cầu thông tin đến Sở TNMT
- Cơ quan phải trả lời trong 10 ngày (thông tin đơn giản) hoặc 30 ngày (phức tạp)
- Miễn phí hoặc phí thấp để sao chụp tài liệu

Nếu cơ quan từ chối cung cấp không có lý do chính đáng: Khiếu nại đến Thanh tra Bộ TNMT.''',
    },
]

TU_PHAP_B7 = [
    {
        'id': 'b7-tp-001', 'category': 'tu_phap', 'procedure': 'khoi_kien_dan_su', 'level': 'district',
        'source': 'Bộ luật Tố tụng Dân sự 2015',
        'question': 'Muốn khởi kiện vụ dân sự (tranh chấp hợp đồng, ly hôn, đòi nợ...) thủ tục thế nào?',
        'answer': '''Khởi kiện vụ án dân sự tại Tòa án Nhân dân.

XÁC ĐỊNH TÒA ÁN CÓ THẨM QUYỀN:
- Tranh chấp dân sự thông thường (dưới 200 triệu hoặc nhỏ): TAND cấp huyện nơi bị đơn cư trú
- Tranh chấp hôn nhân gia đình: TAND nơi bị đơn cư trú
- Tranh chấp thương mại lớn: TAND cấp tỉnh
- Tranh chấp đất đai: TAND nơi có BĐS

HỒ SƠ KHỞI KIỆN:
1. Đơn khởi kiện (Mẫu 23-DS, Nghị quyết 01/2017 của HĐTP) — trình bày rõ: Nguyên đơn, Bị đơn, Nội dung tranh chấp, Yêu cầu
2. Chứng cứ kèm theo: Hợp đồng, hóa đơn, email, tin nhắn, ảnh chụp, nhân chứng...
3. CCCD của nguyên đơn
4. Bản sao chứng cứ (photo, sao y công chứng tùy tài liệu)
5. Giấy tờ chứng minh quan hệ pháp lý (GCN QSDĐ, Giấy ĐKKD...)

NỘP HỒ SƠ: Trực tiếp tại Tòa án hoặc qua bưu điện.
Sau khi nộp: Tòa thông báo thụ lý trong 5 ngày.

ÁN PHÍ:
- 3% giá trị tranh chấp (tối thiểu 300.000 đồng)
- Tạm ứng án phí khi nộp đơn; hoàn lại nếu thắng kiện
- Hộ nghèo, đối tượng chính sách: Miễn án phí

THỜI GIAN GIẢI QUYẾT:
- Sơ thẩm: Tối đa 4 tháng (kéo dài tối đa 6 tháng với vụ phức tạp)
- Phúc thẩm: 2 tháng (nếu bị kháng cáo)

Hỗ trợ tư vấn pháp lý: Đoàn Luật sư tỉnh hoặc Trung tâm TGPL (miễn phí cho người nghèo).''',
    },
    {
        'id': 'b7-tp-002', 'category': 'tu_phap', 'procedure': 'chung_thuc_ban_dich', 'level': 'ward',
        'source': 'Nghị định 23/2015/NĐ-CP',
        'question': 'Chứng thực bản dịch tài liệu nước ngoài ở đâu? Khác gì với dịch thuật thông thường?',
        'answer': '''BẢN DỊCH CÓ CHỨNG THỰC vs BẢN DỊCH THƯỜNG:
- Bản dịch thông thường: Người biết ngôn ngữ dịch, không có cơ quan xác nhận
- Bản dịch có chứng thực: Dịch thuật viên ký tên + Phòng/Văn phòng Công chứng hoặc UBND huyện chứng thực chữ ký của dịch thuật viên

DÙNG KHI NÀO:
Hồ sơ nộp cơ quan Nhà nước thường yêu cầu bản dịch có chứng thực: Visa, định cư nước ngoài, học bổng, công nhận bằng nước ngoài, giao dịch BĐS có yếu tố nước ngoài...

THẨM QUYỀN CHỨNG THỰC BẢN DỊCH:
1. PHÒNG/VĂN PHÒNG CÔNG CHỨNG: Chứng thực chữ ký dịch thuật viên (cách phổ biến nhất)
2. PHÒNG TƯ PHÁP - UBND HUYỆN: Chứng thực bản dịch (chỉ với một số ngôn ngữ họ có dịch thuật viên)

QUY TRÌNH:
1. Tìm dịch thuật viên được công nhận (nhiều phòng công chứng có danh sách cộng tác viên)
2. Dịch thuật viên dịch và ký tên vào bản dịch
3. Nộp tại Văn phòng Công chứng để chứng thực chữ ký dịch thuật viên
4. Công chứng đóng dấu + ký → Bản dịch có giá trị pháp lý

PHÍ: Phí dịch thuật (do người dịch quyết định, thường 100.000–300.000 đồng/trang) + Phí chứng thực chữ ký (50.000 đồng/chữ ký).

CẢNH BÁO: Nhiều dịch vụ "dịch thuật công chứng" tư nhân không chính thức — chỉ dùng Phòng/VPCC được Sở Tư pháp cấp phép.''',
    },
    {
        'id': 'b7-tp-003', 'category': 'tu_phap', 'procedure': 'hoa_giai_co_so', 'level': 'ward',
        'source': 'Luật Hòa giải cơ sở 2013',
        'question': 'Hòa giải cơ sở là gì? Khi nào nên dùng? Hiệu lực pháp lý như thế nào?',
        'answer': '''Hòa giải cơ sở là hoạt động hòa giải tranh chấp, mâu thuẫn tại cộng đồng dân cư, do Tổ Hòa giải thực hiện.

TỔ HÒA GIẢI Ở ĐÂU:
Mỗi thôn, khu dân cư, tổ dân phố có 1 Tổ Hòa giải gồm 3–7 thành viên (Tổ trưởng, hòa giải viên được UBND xã công nhận).

NÊN DÙNG HÒA GIẢI CƠ SỞ KHI:
- Tranh chấp nhỏ giữa hàng xóm (ranh giới, ồn ào, cây cối...)
- Mâu thuẫn gia đình (không đến mức ly hôn)
- Tranh chấp tài sản nhỏ (dưới 50 triệu đồng)
- Vi phạm pháp luật lần đầu, hậu quả nhỏ (muốn giải quyết ngoài tòa)
- Muốn hòa giải nhanh, tiết kiệm chi phí, giữ quan hệ hàng xóm

ƯU ĐIỂM:
- Miễn phí hoàn toàn
- Không mang tính đối đầu (bảo vệ quan hệ cộng đồng)
- Kết quả hòa giải thành: Các bên tự nguyện thực hiện
- Không cần luật sư

HIỆU LỰC PHÁP LÝ:
Thỏa thuận hòa giải thành KHÔNG có hiệu lực thi hành bắt buộc như bản án tòa.
Tuy nhiên: Có thể yêu cầu Tòa án công nhận kết quả hòa giải thành (theo Bộ luật TTDS 2015) → Sau đó có hiệu lực thi hành.

NẾU HÒA GIẢI KHÔNG THÀNH: Mới tiến hành khiếu nại hành chính hoặc khởi kiện tòa án.
Biên bản hòa giải không thành là điều kiện để nộp đơn khởi kiện tranh chấp đất đai.''',
    },
]

GIAO_DUC_B7 = [
    {
        'id': 'b7-gd-001', 'category': 'giao_duc', 'procedure': 'tuyen_sinh_mam_non', 'level': 'ward',
        'source': 'Thông tư 52/2020/TT-BGDĐT',
        'question': 'Thủ tục đăng ký cho con vào trường mầm non công lập như thế nào? Ưu tiên cho ai?',
        'answer': '''Tuyển sinh mầm non công lập thực hiện theo Thông tư 52/2020 và hướng dẫn của UBND tỉnh/thành phố.

ĐỘ TUỔI:
- Nhà trẻ: Từ 3 tháng đến 36 tháng tuổi
- Mẫu giáo: Từ 3–6 tuổi
- Mẫu giáo 5 tuổi (lớp lá): Trẻ đủ 5 tuổi tính đến 31/12 năm học

THỜI GIAN TUYỂN SINH:
- Thường vào tháng 5–7 hàng năm (trước năm học mới)
- Một số trường xét duyệt liên tục khi còn chỗ

HỒ SƠ ĐĂNG KÝ:
1. Đơn xin học (trường cấp mẫu)
2. Giấy khai sinh bản gốc
3. Hộ khẩu/giấy xác nhận cư trú (để xác định tuyến)
4. Sổ tiêm chủng (một số trường yêu cầu)
5. Ảnh 3×4 cm

ƯU TIÊN TUYỂN SINH (theo thứ tự):
1. Trẻ trong địa bàn tuyển sinh (phường/xã/thị trấn của trường)
2. Trẻ có anh/chị đang học cùng trường
3. Con cán bộ công chức của phường/xã
4. Các trường hợp khác theo quy định địa phương

NẾU HẾT CHỖ: Trẻ sẽ được xếp vào danh sách chờ hoặc giới thiệu trường khác có chỗ trống.

TRƯỜNG MẦM NON TƯ THỤC: Không giới hạn tuyến, nhận trực tiếp (nhưng học phí cao hơn nhiều).

Thông tin tuyển sinh: Liên hệ trực tiếp trường hoặc Phòng GD&ĐT huyện.''',
    },
    {
        'id': 'b7-gd-002', 'category': 'giao_duc', 'procedure': 'hoc_phi_hoc_truong', 'level': 'district',
        'source': 'Nghị định 81/2021/NĐ-CP; Nghị định 97/2023/NĐ-CP',
        'question': 'Mức học phí trường công lập 2024-2025 quy định như thế nào? Ai quyết định học phí?',
        'answer': '''HỌC PHÍ TRƯỜNG CÔNG LẬP do HĐND tỉnh/thành phố quyết định trong khung do Chính phủ quy định.

KHUNG HỌC PHÍ CÔNG LẬP (Nghị định 97/2023/NĐ-CP, áp dụng 2023-2025):

MẦM NON VÀ PHỔ THÔNG:
- Vùng thành thị: 300.000–540.000 đồng/tháng
- Vùng nông thôn: 100.000–220.000 đồng/tháng
- Vùng đặc biệt khó khăn: 50.000–110.000 đồng/tháng

MIỄN HỌC PHÍ HOÀN TOÀN (trường công lập):
- Mầm non 5 tuổi (từ năm học 2020–2021): MIỄN
- Tiểu học: MIỄN
- THCS tại các xã đặc biệt khó khăn: MIỄN

AI QUYẾT ĐỊNH HỌC PHÍ:
- Chính phủ: Ban hành khung học phí tối thiểu – tối đa
- HĐND tỉnh: Quyết định mức cụ thể trong khung (mỗi tỉnh khác nhau)
- Trường tự chủ tài chính: Có thể thu cao hơn khung (nhưng phải công khai)

HỌC PHÍ TRƯỜNG TỰ CHỦ TOÀN PHẦN (trường công lập chất lượng cao):
Không bị giới hạn bởi khung — thu theo thực tế chi phí. Ví dụ: Trường THPT chất lượng cao Hà Nội: 3–5 triệu/tháng.

NGOÀI HỌC PHÍ:
- Quỹ phụ huynh: Tự nguyện (không được thu ép buộc)
- Tiền ăn bán trú: Theo thỏa thuận với phụ huynh
- Tiền sách giáo khoa: Mua hoặc mượn thư viện trường

Nếu trường thu quá quy định: Phản ánh đến Phòng GD&ĐT hoặc Thanh tra Sở GD&ĐT.''',
    },
]

NGAN_HANG_B7 = [
    {
        'id': 'b7-nb-001', 'category': 'ngan_hang', 'procedure': 'lai_suat_tiet_kiem', 'level': 'province',
        'source': 'Luật Ngân hàng Nhà nước 2010; Thông tư 08/2012/TT-NHNN',
        'question': 'Lãi suất tiết kiệm ngân hàng 2024 là bao nhiêu? Cách tính lãi tiết kiệm như thế nào?',
        'answer': '''Lãi suất tiết kiệm ngân hàng thay đổi liên tục theo chính sách tiền tệ của NHNN. Dưới đây là tham khảo tháng 6/2024:

LÃI SUẤT TIẾT KIỆM THAM KHẢO (2024):
- Không kỳ hạn: 0,1–0,5%/năm (rất thấp)
- Kỳ hạn 1–2 tháng: 2–3%/năm
- Kỳ hạn 3–6 tháng: 3–4%/năm
- Kỳ hạn 6–12 tháng: 4,5–5,5%/năm
- Kỳ hạn 12–24 tháng: 5–6%/năm
- Kỳ hạn trên 24 tháng: 6–7%/năm (ít phổ biến)

NGÂN HÀNG THƯƠNG MẠI NHÀ NƯỚC (Agribank, BIDV, Vietcombank, VietinBank): Thường lãi suất thấp hơn 0,3–0,5% so với ngân hàng tư nhân, nhưng an toàn hơn.

CÁCH TÍNH LÃI TIẾT KIỆM:
Lãi = Gốc × Lãi suất/năm × Số ngày/365

Ví dụ: Gửi 100 triệu, kỳ hạn 6 tháng, lãi suất 4,5%/năm:
Lãi = 100.000.000 × 4,5% × 180/365 = 2.219.178 đồng (nhận khi đáo hạn)

THUẾ VỚI TIỀN LÃI TIẾT KIỆM:
- Miễn thuế TNCN với lãi tiết kiệm cá nhân (theo Luật Thuế TNCN)

TRA CỨU LÃI SUẤT THỰC TẾ:
- Website từng ngân hàng (cập nhật hàng tuần)
- Trang so sánh: laisuat.vn, giaiphaplaisuat.vn

TIẾT KIỆM ONLINE (lãi cao hơn 0,1–0,3%):
Mở qua app ngân hàng — không cần đến quầy, thường có ưu đãi lãi suất cao hơn.''',
    },
    {
        'id': 'b7-nb-002', 'category': 'ngan_hang', 'procedure': 'bao_cao_gian_lan', 'level': 'province',
        'source': 'Luật Phòng chống rửa tiền 2022; Thông tư 09/2023/TT-NHNN',
        'question': 'Tài khoản ngân hàng bị trừ tiền lạ, giao dịch không rõ nguồn gốc thì xử lý thế nào?',
        'answer': '''KHI PHÁT HIỆN GIAO DỊCH LẠ TRONG TÀI KHOẢN:

NGAY LẬP TỨC:
1. GỌI HOTLINE NGÂN HÀNG 24/7 để khóa thẻ/tài khoản:
   - Vietcombank: 1800.5577 | BIDV: 1800.9247
   - Agribank: 1900.558818 | MB Bank: 1900.54 54 26
   - VietinBank: 1800.1547 | Techcombank: 1800.588812
2. Thay đổi mật khẩu Internet Banking, mã PIN ngay
3. Bật xác thực 2 lớp (2FA) nếu chưa có

TRONG 24 GIỜ:
- Đến ngân hàng với CCCD → Yêu cầu cung cấp thông tin giao dịch lạ (nơi nhận, thời gian, số tiền)
- Nộp Đơn yêu cầu tra soát giao dịch / khiếu nại gian lận
- Nếu bị rút tiền: Ngân hàng có trách nhiệm điều tra trong 30–45 ngày

BÁO CƠ QUAN CÔNG AN:
- Cảnh sát phòng chống tội phạm sử dụng công nghệ cao (PC50): Đến Công an tỉnh/thành phố
- Cổng báo tội phạm mạng: canhbao.ncsc.gov.vn

KHẢ NĂNG ĐƯỢC HOÀN TIỀN:
- Nếu lỗi do hệ thống ngân hàng: Ngân hàng hoàn 100%
- Nếu lỗi do chủ tài khoản (bị lừa cung cấp OTP, mật khẩu): Rất khó được hoàn (ngân hàng coi là lỗi người dùng)
- Nếu thẻ bị clone (sao chép chip): Ngân hàng thường hoàn

PHÒNG NGỪA:
- Không chia sẻ OTP, mật khẩu với bất kỳ ai
- Bật thông báo SMS/email cho mọi giao dịch
- Kiểm tra sao kê định kỳ hàng tuần''',
    },
]


def create_batch7_files():
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_g_bhxh.xlsx':        BHXH_B7,
        'faq_g_dan_su.xlsx':      DAN_SU_B7,
        'faq_g_hanh_chinh.xlsx':  HANH_CHINH_B7,
        'faq_g_giao_thong.xlsx':  GIAO_THONG_B7,
        'faq_g_moi_truong.xlsx':  MOI_TRUONG_B7,
        'faq_g_tu_phap.xlsx':     TU_PHAP_B7,
        'faq_g_giao_duc.xlsx':    GIAO_DUC_B7,
        'faq_g_ngan_hang.xlsx':   NGAN_HANG_B7,
    }

    total = 0
    for filename, rows in datasets.items():
        df = pd.DataFrame(rows, columns=COLS)
        path = OUT_DIR / filename
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='FAQ')
            ws = writer.sheets['FAQ']
            for col_cells in ws.columns:
                max_len = max(len(str(c.value or '')) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 80)
        total += len(rows)
        print(f'  + {filename} ({len(rows)} ban ghi)')

    print(f'\nTong {total} ban ghi moi, {len(datasets)} file tai: {OUT_DIR}')


if __name__ == '__main__':
    create_batch7_files()
