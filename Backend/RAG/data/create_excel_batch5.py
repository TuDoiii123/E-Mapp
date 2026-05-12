"""
Batch 5 — thêm ~18 bản ghi, đưa tổng ChromaDB lên ~150.
Chạy: python Backend/RAG/data/create_excel_batch5.py
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

# =============================================================================
# 1. DỊCH VỤ TIỆN ÍCH — ĐIỆN, NƯỚC, GAS, INTERNET
# =============================================================================
TIEN_ICH = [
    {
        'id': 'tu-001', 'category': 'tien_ich', 'procedure': 'dang_ky_dien', 'level': 'ward',
        'source': 'Luật Điện lực 2004 sửa đổi; Thông tư 39/2015/TT-BCT',
        'question': 'Đăng ký điện mới cho nhà ở tại Thanh Hóa thủ tục thế nào? Mất bao lâu?',
        'answer': '''Đăng ký cấp điện mới tại Điện lực địa phương (Công ty Điện lực Thanh Hóa).

Điện lực Thanh Hóa: 44 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.157 / Hotline: 19001288.

ĐĂNG KÝ ONLINE (nhanh hơn): Cổng dịch vụ điện trực tuyến: dichvudien.npc.com.vn.

HỒ SƠ CẤP ĐIỆN MỚI NHÀ Ở:
1. Đơn đề nghị cấp điện (lấy tại Điện lực hoặc tải online)
2. CCCD của chủ hộ (bản sao)
3. Giấy tờ nhà đất hợp lệ: GCN QSDĐ hoặc Hợp đồng mua bán/thuê nhà có công chứng
4. Sơ đồ vị trí nhà (phác thảo tay hoặc ảnh chụp Google Maps cũng được)

Thời gian giải quyết: 5–7 ngày làm việc với nhà ở thông thường; 15 ngày với công trình lớn cần đầu tư hạ tầng.

CHI PHÍ ĐĂNG KÝ ĐIỆN:
- Tiền đặt cọc: 100.000–300.000 đồng (tùy công suất đăng ký)
- Phí đấu nối: Miễn phí nếu nhà trong phạm vi ≤ 25m từ đường dây hiện có
- Mua công tơ (đồng hồ điện): Không bắt buộc mua; Điện lực lắp đặt, người dùng thuê

GIÁ ĐIỆN SINH HOẠT 2024 (Quyết định 1249/QĐ-BCT):
- Bậc 1 (0–50 kWh): 1.893 đ/kWh | Bậc 2 (51–100): 1.956 đ | Bậc 3 (101–200): 2.271 đ
- Bậc 4 (201–300): 2.860 đ | Bậc 5 (301–400): 3.197 đ | Bậc 6 (>400): 3.302 đ/kWh

KHIẾU NẠI HÓA ĐƠN ĐIỆN: Gọi 19001288 hoặc đến Chi nhánh Điện lực huyện.''',
    },
    {
        'id': 'tu-002', 'category': 'tien_ich', 'procedure': 'dang_ky_nuoc_do_thi', 'level': 'ward',
        'source': 'Luật Cấp, Thoát nước 2023; Nghị định 80/2014/NĐ-CP',
        'question': 'Đăng ký cấp nước máy sinh hoạt tại TP Thanh Hóa cần gì? Tiền nước tính thế nào?',
        'answer': '''Đăng ký cấp nước máy tại Công ty TNHH MTV Cấp nước Thanh Hóa.
Địa chỉ: 27 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.208. Website: capnuocthanhhoa.vn.

HỒ SƠ ĐĂNG KÝ ĐẤU NỐI NƯỚC MỚI:
1. Đơn đề nghị đấu nối (lấy tại Công ty hoặc tải website)
2. CCCD chủ hộ
3. GCN QSDĐ hoặc giấy tờ nhà hợp lệ
4. Sơ đồ vị trí nhà và điểm đấu nối mong muốn

Thời gian: 7–15 ngày. Phí đấu nối: 500.000–2.000.000 đồng (tùy khoảng cách từ đường ống chính).

GIÁ NƯỚC SINH HOẠT TẠI TP THANH HÓA (Quyết định UBND tỉnh 2023):
- Bậc 1 (0–10 m³/tháng): 7.500 đồng/m³
- Bậc 2 (11–20 m³): 9.000 đồng/m³
- Bậc 3 (21–30 m³): 11.000 đồng/m³
- Bậc 4 (>30 m³): 15.000 đồng/m³
(Chưa bao gồm phí bảo vệ môi trường 10% và VAT 5%)

THANH TOÁN TIỀN NƯỚC:
- Online: App Viettel Money, ZaloPay, VNPay, ngân hàng số
- Tại quầy: Công ty Cấp nước hoặc điểm thu hộ (siêu thị, bưu điện)
- Tự động: Đăng ký trích tài khoản ngân hàng hàng tháng

SỰ CỐ NƯỚC: Gọi đường dây nóng 24/7: 0237.3852.208 (sự cố vỡ ống, mất nước đột ngột).''',
    },
    {
        'id': 'tu-003', 'category': 'tien_ich', 'procedure': 'ho_tro_tien_dien', 'level': 'ward',
        'source': 'Quyết định 28/2014/QĐ-TTg; Thông tư 25/2018/TT-BCT',
        'question': 'Hộ nghèo, hộ chính sách được giảm tiền điện như thế nào? Đăng ký ở đâu?',
        'answer': '''HỖ TRỢ TIỀN ĐIỆN CHO HỘ NGHÈO, HỘ CHÍNH SÁCH (theo Quyết định 28/2014/QĐ-TTg sửa đổi):

ĐỐI TƯỢNG ĐƯỢC HỖ TRỢ:
1. Hộ nghèo theo chuẩn quốc gia
2. Hộ chính sách xã hội (thương binh, liệt sĩ, người có công)
3. Hộ nghèo tại các xã đặc biệt khó khăn vùng dân tộc thiểu số

MỨC HỖ TRỢ:
- 30 kWh/tháng × giá bán lẻ điện bình quân = khoảng 56.790 đồng/tháng (năm 2024)
- Hỗ trợ qua hình thức giảm trừ trực tiếp vào hóa đơn tiền điện hàng tháng

ĐĂNG KÝ NHẬN HỖ TRỢ:
- Không cần đăng ký riêng — Điện lực tự động tra cứu danh sách hộ nghèo từ dữ liệu UBND xã
- Nếu thuộc diện mà chưa được giảm: Đến Chi nhánh Điện lực huyện mang Giấy xác nhận hộ nghèo để yêu cầu bổ sung

HỘ CHÍNH SÁCH DÙNG QUÁ 50 kWh/THÁNG: Phần vượt tính theo giá bình thường.

ĐIỆN MẶT TRỜI MÁI NHÀ:
- Hộ gia đình lắp pin mặt trời mái nhà: Được bán điện thừa lại cho EVN (giá mua lại ~671–920 đồng/kWh tùy thời điểm)
- Đăng ký tại Điện lực địa phương trước khi lắp đặt

Điện lực Thanh Hóa: 19001288 (miễn phí).''',
    },
    {
        'id': 'tu-004', 'category': 'tien_ich', 'procedure': 'internet_truyen_hinh', 'level': 'ward',
        'source': 'Nghị định 06/2016/NĐ-CP; Luật Viễn thông 2023',
        'question': 'Đăng ký internet cáp quang và truyền hình tại Thanh Hóa có những gói nào? Xử lý sự cố thế nào?',
        'answer': '''CÁC NHÀ MẠNG CUNG CẤP INTERNET CÁP QUANG TẠI THANH HÓA:

VIETTEL THANH HÓA:
- Gói Fiber Basic: 180.000 đ/tháng — 60 Mbps
- Gói Fiber Plus: 220.000 đ/tháng — 100 Mbps
- Gói Fiber Max: 320.000 đ/tháng — 200 Mbps
ĐT: 0237.3761.000 | Hotline: 18008098

VNPT THANH HÓA (VinaPhone):
- Gói Internet 60 Mbps: 165.000 đ/tháng
- Gói Internet 100 Mbps: 210.000 đ/tháng
ĐT: 0237.3750.750 | Hotline: 18001260

FPT TELECOM THANH HÓA:
- Gói 60 Mbps: 180.000 đ/tháng | Gói 200 Mbps: 295.000 đ/tháng
ĐT: 0237.3766.666 | Hotline: 19006600

COMBO INTERNET + TRUYỀN HÌNH:
Thường tiết kiệm hơn đăng ký riêng lẻ. Viettel TV, MyTV (VNPT), FPT Play đều có gói kết hợp.

XỬ LÝ SỰ CỐ MẠNG:
1. Khởi động lại router (rút nguồn 30 giây, cắm lại)
2. Kiểm tra đèn trạng thái router (đèn WAN/Internet phải xanh)
3. Nếu không tự khắc phục: Gọi hotline nhà mạng để báo sự cố — kỹ thuật viên đến trong 4–24 giờ
4. Yêu cầu bồi thường nếu mất kết nối > 24 giờ liên tiếp (theo hợp đồng dịch vụ)

PHẢN ÁNH CHẤT LƯỢNG DỊCH VỤ VIỄN THÔNG: Sở TTTT Thanh Hóa: 0237.3852.483.''',
    },
    {
        'id': 'tu-005', 'category': 'tien_ich', 'procedure': 'khai_tu_dich_vu', 'level': 'ward',
        'source': 'Nghị định 52/2024/NĐ-CP',
        'question': 'Chuyển nhà thì cần làm gì với các dịch vụ điện, nước, internet? Có cần hủy đăng ký cũ không?',
        'answer': '''KHI CHUYỂN NHÀ — CHECKLIST CÁC DỊCH VỤ TIỆN ÍCH:

1. ĐIỆN:
   - Chụp ảnh chỉ số công tơ ngày chuyển ra (bằng chứng thanh toán)
   - Báo Điện lực để chốt hóa đơn cuối cùng (có thể qua app/website EVN)
   - Nhà mới: Xin đăng ký cấp điện mới HOẶC đề nghị chuyển tên chủ hợp đồng
   - Thời gian chuyển tên hợp đồng điện: 3–5 ngày

2. NƯỚC:
   - Báo Công ty cấp nước để chốt chỉ số nước và thanh toán tiền nước cũ
   - Đặt cọc tại nơi ở mới và đăng ký cấp nước mới

3. INTERNET/TRUYỀN HÌNH CÁP:
   - Liên hệ nhà mạng để: Chuyển dịch vụ sang địa chỉ mới (nếu trong vùng phủ sóng) HOẶC hủy hợp đồng (chú ý phí phạt nếu còn trong thời hạn cam kết)
   - Phí hủy hợp đồng trước hạn: Thường 1–3 tháng tiền dịch vụ còn lại
   - Một số nhà mạng MIỄN phí hủy và di chuyển nếu chuyển địa chỉ trong cùng tỉnh

4. GAS BÌNH (khí đốt):
   - Bình gas không cần thủ tục — mang theo hoặc bán lại cho đại lý

5. ĐĂNG KÝ KINH DOANH (nếu có kinh doanh tại nhà):
   - Thay đổi địa chỉ trên Giấy đăng ký kinh doanh tại Phòng Tài chính-KH UBND huyện mới

THAY ĐỔI ĐỊA CHỈ TRÊN CÁC GIẤY TỜ QUAN TRỌNG: CCCD (nếu thay đổi tỉnh), Sổ BHXH (thông báo cơ quan), tài khoản ngân hàng, giấy phép lái xe (không bắt buộc đổi ngay).''',
    },
    {
        'id': 'tu-006', 'category': 'tien_ich', 'procedure': 'gas_khi_dot', 'level': 'ward',
        'source': 'Nghị định 87/2018/NĐ-CP về kinh doanh khí',
        'question': 'Sử dụng gas bình và gas đường ống an toàn như thế nào? Phát hiện rò rỉ gas thì làm gì?',
        'answer': '''AN TOÀN KHI SỬ DỤNG GAS:

GAS BÌNH (LPG):
Dấu hiệu mua gas đúng chuẩn: Bình có dấu kiểm định, van không rỉ sét, vỏ bình không méo mó.
Đại lý gas uy tín: Petrolimex Gas, PV Gas, Saigon Petro, VT Gas... (có đăng ký kinh doanh).

KHI PHÁT HIỆN MÙI GAS:
1. KHÔNG bật/tắt công tắc điện, không dùng điện thoại tại chỗ
2. KHÔNG bật lửa
3. Tắt van gas tại bình ngay lập tức (xoay theo chiều kim đồng hồ)
4. Mở hết cửa sổ, cửa chính (thông gió)
5. Thoát ra ngoài, gọi 114 (PCCC) hoặc đại lý gas

KIỂM TRA RÒ RỈ GAS: Dùng nước xà phòng bôi lên van, dây dẫn — bong bóng nổi lên = đang rò.

GAS ĐƯỜNG ỐNG (khí thiên nhiên/CNG):
Tại Thanh Hóa: Hiện chưa phổ biến gas đường ống cho hộ gia đình (chủ yếu tại KCN Nghi Sơn).
Tương lai: Dự án cấp khí CNG cho khu dân cư đang được nghiên cứu.

BẢO DƯỠNG THIẾT BỊ GAS:
- Thay dây dẫn gas: Mỗi 2 năm một lần (không dùng dây quá cũ, nứt)
- Bếp gas: Vệ sinh đầu đốt định kỳ để không bị tắc lửa
- Van điều áp: Kiểm tra 6 tháng/lần

Sự cố gas khẩn cấp: 114 (PCCC) hoặc 1800.5656 (đường dây nóng sự cố hóa chất — Bộ Công thương).''',
    },
]

# =============================================================================
# 2. XUẤT NHẬP CẢNH — VISA, THẺ TẠM TRÚ
# =============================================================================
XUAT_NHAP_CANH = [
    {
        'id': 'xnc-001', 'category': 'xuat_nhap_canh', 'procedure': 'xin_visa_nuoc_ngoai', 'level': 'province',
        'source': 'Luật Xuất nhập cảnh 2019; Thông tư 29/2021/TT-BCA',
        'question': 'Người Việt Nam đi du lịch, công tác nước ngoài cần chuẩn bị hồ sơ visa như thế nào?',
        'answer': '''Thủ tục xin visa phụ thuộc vào từng quốc gia. Dưới đây là hướng dẫn chung:

TRƯỚC KHI XIN VISA:
1. Kiểm tra hộ chiếu còn hiệu lực ≥ 6 tháng so với ngày về (nhiều nước yêu cầu)
2. Tra cứu yêu cầu visa của nước đến: Một số nước miễn visa cho hộ chiếu Việt Nam (ASEAN, Nhật Bản ngắn hạn...)

VISA CÁC NƯỚC PHỔ BIẾN:
- Nhật Bản (3–5 năm/lần): Nộp tại Đại sứ quán Nhật hoặc trung tâm dịch vụ JVA Hà Nội. Yêu cầu: Giấy phép lao động/học/đầu tư, sao kê ngân hàng, giấy tờ quan hệ gia đình...
- Hàn Quốc: Trung tâm Thị thực Hàn Quốc tại Hà Nội, TP.HCM
- Schengen (EU): Đại sứ quán nước đến nhiều ngày nhất; hồ sơ phức tạp nhất
- Mỹ (B1/B2): ĐSQ Hoa Kỳ Hà Nội, phỏng vấn bắt buộc
- Trung Quốc: ĐSQ TQ Hà Nội, hồ sơ đơn giản, cấp nhanh

HỒ SƠ THƯỜNG GẶP:
- Hộ chiếu gốc + bản sao trang thông tin
- Ảnh 3,5×4,5 cm nền trắng (yêu cầu khác nhau từng nước)
- CCCD bản sao
- Sao kê tài khoản ngân hàng 3–6 tháng
- Giấy tờ chứng minh mục đích: Vé máy bay, đặt phòng khách sạn, thư mời...
- Phí visa: $20–$200 (tùy quốc gia)

TẠI THANH HÓA: Một số đại lý du lịch và visa uy tín hỗ trợ làm hồ sơ visa, phí dịch vụ 200.000–1.000.000 đồng.''',
    },
    {
        'id': 'xnc-002', 'category': 'xuat_nhap_canh', 'procedure': 'the_tam_tru_nguoi_nn', 'level': 'province',
        'source': 'Luật Nhập cảnh, xuất cảnh, quá cảnh, cư trú của người nước ngoài 2014 sửa đổi 2019',
        'question': 'Người nước ngoài cư trú dài hạn tại Thanh Hóa cần thẻ tạm trú không? Thủ tục ở đâu?',
        'answer': '''Người nước ngoài cư trú tại Việt Nam từ 90 ngày trở lên cần xin Thẻ tạm trú.

CÁC LOẠI THẺ TẠM TRÚ (ký hiệu LD, ĐT, LĐ, HN, TT...):
- LD (Lao động): Có Giấy phép lao động tại VN
- ĐT (Đầu tư): Nhà đầu tư có dự án tại VN
- DN (Doanh nghiệp): Người đại diện pháp luật doanh nghiệp nước ngoài
- HN (Hôn nhân): Vợ/chồng công dân Việt Nam

NỘP HỒ SƠ TẠI: Phòng PA08 (Quản lý Xuất nhập cảnh) - Công an tỉnh Thanh Hóa.
Địa chỉ: 04 Trần Phú, phường Hàm Rồng, TP Thanh Hóa. ĐT: 069.2587.080.

HỒ SƠ XIN THẺ TẠM TRÚ (LD - Lao động):
1. Tờ khai đề nghị cấp thẻ tạm trú (NA6)
2. Hộ chiếu còn hiệu lực ≥ 12 tháng
3. Giấy phép lao động (bản gốc hoặc sao y)
4. Hợp đồng lao động
5. Ảnh 2×3 cm (4 ảnh)

Thời hạn thẻ tạm trú: Theo thời hạn giấy phép lao động (tối đa 2 năm, gia hạn được).
Lệ phí: 145.000 đồng (thẻ 12 tháng) đến 435.000 đồng (thẻ 36 tháng).

ĐĂNG KÝ TẠM TRÚ TẠI NƠI Ở: Trong vòng 24 giờ sau khi đến nơi ở mới, người nước ngoài phải đăng ký tại Công an xã/phường (khách sạn đăng ký hộ, nhà riêng thì tự đăng ký).''',
    },
    {
        'id': 'xnc-003', 'category': 'xuat_nhap_canh', 'procedure': 'visa_dien_tu_viet_nam', 'level': 'province',
        'source': 'Luật Xuất nhập cảnh 2019 sửa đổi 2023; Nghị định 07/2023/NĐ-CP',
        'question': 'Người nước ngoài vào Việt Nam (Thanh Hóa) xin visa điện tử E-visa như thế nào? Miễn visa không?',
        'answer': '''Việt Nam có 3 hình thức nhập cảnh cho người nước ngoài:

1. MIỄN VISA (KHÔNG CẦN XIN):
Hiện (2024) có 45 quốc gia được miễn visa vào Việt Nam, gồm:
- Các nước ASEAN: Philippines, Indonesia, Malaysia, Singapore, Thái Lan (30 ngày)
- Châu Âu: Pháp, Đức, Anh, Ý, Tây Ban Nha, Hà Lan (45 ngày từ 08/2023)
- Nhật Bản, Hàn Quốc (45 ngày), Ấn Độ (45 ngày), Úc, Canada, Mỹ (45 ngày)
Danh sách đầy đủ: xuatnhapcanh.gov.vn

2. EVISA (VISA ĐIỆN TỬ — E-VISA):
- Áp dụng cho 80 quốc gia chưa được miễn visa
- Xin online: evisa.xuatnhapcanh.gov.vn
- Thời hạn: Tối đa 90 ngày (nhập cảnh nhiều lần)
- Lệ phí: 25 USD
- Thời gian cấp: 3 ngày làm việc
- Cổng vào: Được nhập qua tất cả cửa khẩu quốc tế VN, kể cả sân bay Thọ Xuân (Thanh Hóa)

3. VISA ĐẠI SỨ QUÁN:
Dành cho quốc gia chưa có E-Visa; nộp tại Đại sứ quán/Lãnh sự quán VN.

DU KHÁCH NƯỚC NGOÀI ĐẾN THANH HÓA:
- Sân bay Thọ Xuân (THD): Bay thẳng từ Thái Lan, Hàn Quốc theo mùa
- Nhập cảnh đường bộ: Cửa khẩu Lao Bảo (Quảng Trị) gần nhất từ Lào
Trung tâm Xúc tiến Du lịch Thanh Hóa: 0237.3710.888.''',
    },
    {
        'id': 'xnc-004', 'category': 'xuat_nhap_canh', 'procedure': 'gia_han_ho_chieu', 'level': 'province',
        'source': 'Luật Xuất nhập cảnh 2019',
        'question': 'Hộ chiếu sắp hết hạn thì gia hạn hay làm mới? Thủ tục ở đâu tại Thanh Hóa?',
        'answer': '''Hộ chiếu phổ thông Việt Nam KHÔNG GIA HẠN được — phải làm mới khi hết hạn hoặc sắp hết hạn.

LÀM MỚI HỘ CHIẾU khi nào:
- Hộ chiếu hết hạn hoặc còn dưới 6 tháng (nhiều nước không cho nhập cảnh nếu dưới 6 tháng)
- Hộ chiếu hỏng, rách, mất
- Đã dùng hết trang thị thực (đóng thêm trang không được phép)
- Thay đổi thông tin (họ tên, ảnh lỗi thời)

NỘP HỒ SƠ TẠI: Phòng PA08 - Công an tỉnh Thanh Hóa.
Địa chỉ: 04 Trần Phú, phường Hàm Rồng, TP Thanh Hóa. ĐT: 069.2587.080.
Hoặc online tại: dichvucong.gov.vn → "Cấp hộ chiếu" (nhận kết quả qua bưu điện).

HỒ SƠ LÀM HỘ CHIẾU MỚI:
1. Tờ khai đề nghị cấp hộ chiếu (M1 — điền online hoặc tại chỗ)
2. CCCD/Căn cước công dân còn hiệu lực (bản gốc)
3. Hộ chiếu cũ (bản gốc nếu còn — nộp để thu hồi)
4. Ảnh 4×6 cm (hoặc chụp tại chỗ)

LỆ PHÍ: 200.000 đồng (hộ chiếu 10 năm); 100.000 đồng (trẻ dưới 14 tuổi — 5 năm).
PHÍ NHANH (1–3 ngày): Thêm 200.000 đồng.
THỜI GIAN THƯỜNG: 5–8 ngày làm việc; nhận qua bưu điện hoặc đến lấy.

LƯU Ý: Trẻ em dưới 14 tuổi phải có mặt cha/mẹ khi nộp hồ sơ.''',
    },
    {
        'id': 'xnc-005', 'category': 'xuat_nhap_canh', 'procedure': 'dinh_cu_nuoc_ngoai', 'level': 'province',
        'source': 'Luật Quốc tịch 2008; Nghị định 136/2014/NĐ-CP',
        'question': 'Người Việt muốn định cư ở nước ngoài (Mỹ, Canada, Úc, châu Âu) cần làm gì trước khi đi?',
        'answer': '''Trước khi định cư nước ngoài, cần hoàn thành các thủ tục tại Việt Nam:

CÁC VIỆC CẦN LÀM TRƯỚC KHI XUẤT CẢNH DÀI HẠN:

1. HỘ CHIẾU: Làm mới nếu sắp hết hạn (xem thủ tục cấp hộ chiếu)

2. XIN THÔI QUỐC TỊCH (nếu muốn nhập tịch nước đến — không bắt buộc):
   - Điều kiện: Đã có/sắp có quốc tịch nước đến
   - Thủ tục tại Sở Tư pháp tỉnh Thanh Hóa (trình Bộ Tư pháp → Chủ tịch nước)
   - Thời gian: 6–18 tháng

3. XÓA ĐĂNG KÝ THƯỜNG TRÚ (không bắt buộc nhưng nên làm):
   - Tại Công an xã/phường nơi đang đăng ký thường trú
   - Xuất trình hộ chiếu, CCCD, và giấy tờ chứng minh được phép cư trú ở nước ngoài

4. NGHĨA VỤ THUẾ: Kê khai và hoàn thành thuế TNCN cho năm trước khi đi

5. CÔNG NỢ VÀ HỢP ĐỒNG: Tất toán nợ vay ngân hàng, hủy hợp đồng thuê nhà, giải quyết tranh chấp (nếu có)

6. TÀI SẢN: Ủy quyền quản lý/bán tài sản tại Việt Nam cho người thân tin tưởng (hợp đồng ủy quyền công chứng)

7. PHIẾU LÝ LỊCH TƯ PHÁP: Nhiều nước yêu cầu nộp khi xin visa định cư/thường trú (xem thủ tục tại Sở Tư pháp)

Sau khi định cư: Vẫn có thể sở hữu đất đai/nhà ở tại Việt Nam, nhận kiều hối, và về thăm không cần visa (dùng hộ chiếu Việt Nam).''',
    },
    {
        'id': 'xnc-006', 'category': 'xuat_nhap_canh', 'procedure': 'sân_bay_tho_xuan', 'level': 'province',
        'source': 'Cổng thông tin Cảng hàng không Thọ Xuân',
        'question': 'Sân bay Thọ Xuân Thanh Hóa có những đường bay nào? Làm thủ tục tại sân bay ra sao?',
        'answer': '''Cảng hàng không Thọ Xuân (mã IATA: THD) — Sân bay quốc tế phục vụ tỉnh Thanh Hóa.
Địa chỉ: Xã Xuân Thiên, huyện Thọ Xuân, Thanh Hóa (cách TP Thanh Hóa ~45km).
ĐT: 0237.3674.888.

ĐƯỜNG BAY NỘI ĐỊA HIỆN CÓ (2024):
- Thọ Xuân ↔ TP Hồ Chí Minh: Vietnam Airlines, VietJet, Bamboo Airways (3–5 chuyến/ngày)
- Thọ Xuân ↔ Đà Nẵng: Vietnam Airlines (một số thời điểm)
- Thọ Xuân ↔ Phú Quốc: VietJet (mùa hè)

ĐƯỜNG BAY QUỐC TẾ (charter/thuê chuyến):
- Thọ Xuân ↔ Bangkok (Thái Lan): Theo mùa du lịch
- Thọ Xuân ↔ Seoul/Incheon (Hàn Quốc): Thuê chuyến mùa hè

THỦ TỤC LÀM THỦ TỤC BAY (check-in):
- Check-in online: 24–48 giờ trước giờ bay qua app/website hãng bay (tiết kiệm thời gian)
- Check-in tại quầy sân bay: Có mặt ít nhất 90 phút trước giờ bay nội địa; 2–3 giờ với quốc tế
- Giấy tờ: CCCD/Hộ chiếu + Mã đặt chỗ/vé điện tử
- Hành lý ký gửi: Tùy hạng vé (thường 20–23kg với vé phổ thông)

ĐI TỪ TP THANH HÓA ĐẾN SÂN BAY: Xe khách (bến xe Thanh Hóa → Thọ Xuân), taxi (300.000–500.000 đồng), xe đặt riêng.
Giá vé taxi cố định sân bay Thọ Xuân — TP Thanh Hóa: Tham khảo tại quầy thông tin sân bay.''',
    },
]

# =============================================================================
# 3. KINH DOANH BỔ SUNG
# =============================================================================
KINH_DOANH_2 = [
    {
        'id': 'kd2-001', 'category': 'kinh_doanh', 'procedure': 'thuong_mai_dien_tu', 'level': 'province',
        'source': 'Nghị định 85/2021/NĐ-CP; Thông tư 47/2014/TT-BCT',
        'question': 'Bán hàng online, kinh doanh trên sàn thương mại điện tử có phải đăng ký không? Nộp thuế thế nào?',
        'answer': '''Kinh doanh online ngày càng được kiểm soát chặt hơn — cần tuân thủ các quy định sau:

ĐĂNG KÝ WEBSITE/APP TMĐT:
- Có website bán hàng riêng (không qua sàn): Phải đăng ký với Bộ Công thương tại online.gov.vn
- Bán hàng qua mạng xã hội (Facebook, TikTok shop, Zalo): Không cần đăng ký website, nhưng phải khai báo thuế nếu doanh thu > 100 triệu đồng/năm

BÁN HÀNG TRÊN CÁC SÀN (Shopee, Lazada, Tiki, TikTok Shop):
- Đăng ký tài khoản người bán theo yêu cầu từng sàn (CCCD hoặc Giấy phép kinh doanh)
- Sàn có trách nhiệm thu và nộp thuế hộ người bán theo Nghị định 85/2021 (từ 2022)
- Người bán cá nhân: Sàn khấu trừ 1% thuế TNCN trên doanh thu nếu > 100 triệu/năm
- Hộ kinh doanh bán qua sàn: Tự khai thuế hoặc để sàn khai hộ

THUẾ KINH DOANH ONLINE (nếu tự khai):
- Doanh thu ≤ 100 triệu/năm: Miễn thuế
- 100 triệu – 300 triệu: Thuế GTGT 1% + TNCN 0,5% = 1,5% doanh thu
- > 300 triệu: Tỷ lệ % tùy ngành

HÓA ĐƠN KHI BÁN HÀNG ONLINE:
- Từ 01/07/2022: Phải xuất hóa đơn điện tử khi khách yêu cầu
- Bán lẻ cho cá nhân không lấy hóa đơn: Lập bảng kê doanh thu

Cục Quản lý TMĐT và Kinh tế số - Bộ Công thương hỗ trợ: 1800.0218 (miễn phí).''',
    },
    {
        'id': 'kd2-002', 'category': 'kinh_doanh', 'procedure': 'nhuong_quyen_thuong_mai', 'level': 'province',
        'source': 'Luật Thương mại 2005; Nghị định 08/2018/NĐ-CP',
        'question': 'Muốn mua nhượng quyền thương mại (franchise) cần lưu ý những điều gì về pháp lý?',
        'answer': '''Nhượng quyền thương mại (franchise) là hợp đồng cho phép bên nhận quyền kinh doanh theo mô hình của bên nhượng quyền.

ĐIỀU KIỆN PHÁP LÝ:

BÊN NHƯỢNG QUYỀN (bán franchise):
- Phải đăng ký hoạt động nhượng quyền thương mại tại Bộ Công thương (thương hiệu quốc tế) hoặc Sở Công thương tỉnh (thương hiệu địa phương)
- Hệ thống kinh doanh phải hoạt động ít nhất 1 năm trước khi nhượng quyền

BÊN NHẬN QUYỀN (mua franchise):
- Là cá nhân/doanh nghiệp có đủ năng lực pháp lý
- Ký Hợp đồng nhượng quyền thương mại (bắt buộc bằng văn bản)

KIỂM TRA TRƯỚC KHI ĐỒNG Ý MUA FRANCHISE:
1. Xem bản Công bố thông tin nhượng quyền (phải cung cấp trước 15 ngày ký hợp đồng)
2. Kiểm tra thương hiệu đã đăng ký tại NOIP (noip.gov.vn) chưa
3. Xác nhận doanh thu trung bình các điểm hiện có (yêu cầu số liệu kiểm toán)
4. Xem xét kỹ: Phí nhượng quyền, phí royalty hàng tháng, điều khoản chấm dứt hợp đồng, độc quyền khu vực

CÁC FRANCHISE PHỔ BIẾN TẠI THANH HÓA: Highlands Coffee, Trà sữa TocoToco, Bắp xào Cali... (đã có điểm tại TP Thanh Hóa).

Tư vấn pháp lý franchise: Phòng Thương mại và Công nghiệp VN (VCCI) - Chi nhánh Thanh Hóa: 0237.3853.299.''',
    },
    {
        'id': 'kd2-003', 'category': 'kinh_doanh', 'procedure': 'giai_quyet_tranh_chap_tm', 'level': 'province',
        'source': 'Luật Thương mại 2005; Luật Trọng tài thương mại 2010',
        'question': 'Tranh chấp hợp đồng kinh doanh, thương mại giải quyết qua tòa án hay trọng tài? Khác nhau thế nào?',
        'answer': '''Tranh chấp thương mại (hợp đồng mua bán, đầu tư, hợp tác kinh doanh...) có 4 phương thức giải quyết:

1. THƯƠNG LƯỢNG (giải quyết nội bộ):
   - Hai bên tự đàm phán — nhanh nhất, chi phí thấp nhất
   - Không có giá trị thi hành bắt buộc nếu một bên không thực hiện

2. HÒA GIẢI (qua bên thứ 3):
   - Trung tâm Hòa giải thương mại hoặc hòa giải viên được công nhận
   - Chi phí thấp, linh hoạt, bảo mật
   - Kết quả hòa giải thành có thể yêu cầu Tòa án công nhận để có hiệu lực thi hành

3. TRỌNG TÀI THƯƠNG MẠI:
   - Chỉ áp dụng khi HĐ có điều khoản trọng tài hoặc các bên đồng ý sau tranh chấp
   - Tại Thanh Hóa: Trung tâm Trọng tài Quốc tế VN (VIAC) nhận giải quyết
   - Phán quyết trọng tài: CHUNG THẨM (không kháng cáo), có hiệu lực như bản án tòa
   - Nhanh hơn tòa (6–12 tháng), bảo mật hơn

4. KHỞI KIỆN RA TÒA ÁN:
   - TAND cấp huyện (tranh chấp dưới 3 tỷ đồng, phức tạp vừa)
   - TAND tỉnh Thanh Hóa: 06 Đinh Lễ, TP Thanh Hóa (tranh chấp phức tạp, > 3 tỷ đồng)
   - Án phí: 3–5% giá trị tranh chấp (phần thắng được hoàn lại)
   - Thời gian: 6 tháng–2 năm (sơ thẩm + phúc thẩm nếu kháng cáo)

KHUYẾN CÁO: Đưa điều khoản trọng tài vào HĐ ngay từ đầu để tránh tranh chấp tòa án kéo dài.''',
    },
    {
        'id': 'kd2-004', 'category': 'kinh_doanh', 'procedure': 'bao_ve_nguoi_tieu_dung', 'level': 'province',
        'source': 'Luật Bảo vệ quyền lợi người tiêu dùng 2023',
        'question': 'Mua hàng giả, hàng kém chất lượng, bị lừa đảo trong mua bán thì khiếu nại ở đâu?',
        'answer': '''Người tiêu dùng (NTD) được pháp luật bảo vệ theo Luật Bảo vệ quyền lợi NTD 2023.

QUYỀN CỦA NGƯỜI TIÊU DÙNG:
- Được đổi/trả hàng trong 7 ngày nếu hàng lỗi (hàng online: 14 ngày — theo chính sách sàn TMĐT)
- Được hoàn tiền nếu hàng không đúng mô tả
- Được bồi thường thiệt hại khi hàng kém chất lượng gây hại sức khỏe

KHIẾU NẠI ĐẾN ĐÂU:

1. TRỰC TIẾP VỚI DOANH NGHIỆP:
   - Gọi hotline/CS của cửa hàng/sàn TMĐT
   - Yêu cầu đổi trả theo chính sách

2. HỘI BẢO VỆ NGƯỜI TIÊU DÙNG TỈNH THANH HÓA:
   - Địa chỉ: 18 Tống Duy Tân, TP Thanh Hóa. ĐT: 0237.3754.888
   - Tư vấn miễn phí, hỗ trợ hòa giải giữa NTD và DN

3. SỞ CÔNG THƯƠNG THANH HÓA:
   - Chi cục Quản lý thị trường: Xử lý hàng giả, hàng nhái, hàng kém chất lượng
   - ĐT: 0237.3852.247. Đường dây nóng tố cáo hàng giả: 1800.0324 (miễn phí)

4. CỔNG QUỐC GIA:
   - App "VnSafe" — báo cáo hàng giả, vi phạm ATTP
   - trungtamtieudung.vn — tư vấn NTD quốc gia

XỬ PHẠT DOANH NGHIỆP VI PHẠM:
- Bán hàng giả: Phạt 10–70 triệu đồng + tịch thu hàng + đình chỉ kinh doanh
- Vi phạm quyền NTD: 10–50 triệu đồng''',
    },
    {
        'id': 'kd2-005', 'category': 'kinh_doanh', 'procedure': 'uu_dai_doanh_nghiep_dtt', 'level': 'province',
        'source': 'Luật Doanh nghiệp nhỏ và vừa 2017; Nghị quyết HĐND tỉnh Thanh Hóa',
        'question': 'Doanh nghiệp nhỏ và vừa tại Thanh Hóa được hỗ trợ gì từ Nhà nước?',
        'answer': '''Doanh nghiệp nhỏ và vừa (DNNVV) là DN có ≤ 200 lao động hoặc doanh thu ≤ 100 tỷ đồng/năm.

CÁC HỖ TRỢ LIÊN BANG (Luật DNNVV 2017):

1. HỖ TRỢ TÀI CHÍNH:
   - Bảo lãnh tín dụng: Quỹ Bảo lãnh tín dụng DNNVV tỉnh Thanh Hóa bảo lãnh vay ngân hàng khi không đủ tài sản thế chấp (bảo lãnh tối đa 80% khoản vay)
   - Thuế TNDN ưu đãi: DNNVV siêu nhỏ (≤ 10 lao động, DT ≤ 3 tỷ): Thuế suất 15–17%
   - Miễn lệ phí môn bài năm đầu thành lập

2. HỖ TRỢ PHI TÀI CHÍNH:
   - Đào tạo miễn phí: Kỹ năng quản lý, kế toán, marketing, công nghệ số (Sở KH&ĐT và VCCI tổ chức)
   - Tư vấn pháp lý, thuế miễn phí: 3 lần/năm tại Trung tâm Hỗ trợ DNNVV
   - Kết nối thị trường: Tham gia hội chợ, triển lãm trong và ngoài tỉnh (hỗ trợ 50% chi phí gian hàng)
   - Số hóa DNNVV: Hỗ trợ 50% phí phần mềm quản lý, kế toán, bán hàng online (tối đa 1,5 triệu đồng)

3. HỖ TRỢ MẶT BẰNG:
   - Ưu tiên thuê đất trong KCN, cụm CN với giá ưu đãi
   - Vườn ươm DNNVV: Thuê văn phòng giá thấp tại Trung tâm Hỗ trợ DN Thanh Hóa

Đăng ký hỗ trợ: Trung tâm Hỗ trợ DNNVV tỉnh Thanh Hóa, 24 Hải Thượng Lãn Ông. ĐT: 0237.3852.349.''',
    },
    {
        'id': 'kd2-006', 'category': 'kinh_doanh', 'procedure': 'tam_ngung_giai_the_ho_kd', 'level': 'district',
        'source': 'Nghị định 01/2021/NĐ-CP; Luật Doanh nghiệp 2020',
        'question': 'Hộ kinh doanh muốn tạm ngưng hoạt động hoặc đóng cửa thì thủ tục thế nào?',
        'answer': '''TẠM NGƯNG HOẠT ĐỘNG HỘ KINH DOANH:
Nộp Thông báo tạm ngưng tại Phòng Tài chính-KH UBND huyện.
Thời hạn: Mỗi lần tạm ngưng ≤ 1 năm. Trước khi hết hạn phải thông báo tiếp tục hoặc chấm dứt.
Hồ sơ: Thông báo tạm ngưng (Mẫu ĐKK-09) + Giấy chứng nhận đăng ký hộ KD gốc.
Nộp: Trước ngày dự kiến tạm ngưng ít nhất 3 ngày làm việc.

TRONG THỜI GIAN TẠM NGƯNG:
- Không được hoạt động kinh doanh
- Vẫn phải nộp thuế môn bài cho kỳ đang tạm ngưng
- Không được thay đổi nội dung đăng ký kinh doanh

CHẤM DỨT HOẠT ĐỘNG (ĐÓNG CỬA VĨNH VIỄN):
Hồ sơ:
1. Thông báo chấm dứt hoạt động hộ KD (Mẫu ĐKK-10)
2. Giấy CN đăng ký hộ KD gốc (nộp lại để thu hồi)
3. Xác nhận hoàn thành nghĩa vụ thuế của Chi cục Thuế
4. Giải quyết hết nợ với nhà cung cấp, người lao động

Nộp: Phòng TC-KH UBND huyện. Thời gian: 5 ngày làm việc.

SAU KHI ĐÃ ĐÓNG CỬA: Hủy hóa đơn điện tử chưa sử dụng (thông báo với Chi cục Thuế); đóng tài khoản ngân hàng kinh doanh.

LƯU Ý: Hộ KD không hoạt động mà không thông báo vẫn phải nộp thuế môn bài. Nếu trốn thuế: Bị phạt 1–3 lần số thuế trốn.''',
    },
]


def create_batch5_files():
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_tien_ich.xlsx':       TIEN_ICH,
        'faq_xuat_nhap_canh.xlsx': XUAT_NHAP_CANH,
        'faq_kinh_doanh_2.xlsx':   KINH_DOANH_2,
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
    create_batch5_files()
