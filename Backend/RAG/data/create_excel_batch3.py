"""
Batch 3 — thêm ~82 bản ghi mới, đưa tổng ChromaDB lên ~150.
Chạy: python Backend/RAG/data/create_excel_batch3.py
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

# =============================================================================
# 1. NGÂN HÀNG & TÍN DỤNG
# =============================================================================
NGAN_HANG = [
    {
        'id': 'nb-001', 'category': 'ngan_hang', 'procedure': 'vay_mua_nha', 'level': 'province',
        'source': 'Luật Các TCTD 2024; Thông tư 39/2016/TT-NHNN',
        'question': 'Vay ngân hàng mua nhà cần điều kiện gì? Thủ tục và hồ sơ gồm những gì?',
        'answer': '''Vay mua nhà (vay thế chấp BĐS) tại các ngân hàng thương mại.
Tại Thanh Hóa: Agribank, BIDV, Vietcombank, VietinBank, MB, VPBank, Techcombank đều có sản phẩm vay mua nhà.

ĐIỀU KIỆN VAY:
- Tuổi: 18–65 tuổi (một số ngân hàng đến 70 tuổi khi kết thúc khoản vay)
- Thu nhập: Chứng minh thu nhập ổn định (lương, kinh doanh); thông thường trả nợ hàng tháng ≤ 50% thu nhập
- Tài sản bảo đảm: BĐS mua hoặc BĐS khác có GCN đủ điều kiện thế chấp
- Lịch sử tín dụng: Không có nợ xấu tại hệ thống CIC

MỨC VAY & LÃI SUẤT (tham khảo 2024):
- Mức vay: 70–85% giá trị BĐS (tùy ngân hàng và định giá)
- Thời hạn: Tối đa 25–30 năm
- Lãi suất: 6–9%/năm (cố định 1–3 năm đầu), thả nổi theo thị trường sau đó

HỒ SƠ VAY:
1. CCCD/Hộ chiếu của người vay (và đồng vay nếu có)
2. Giấy đăng ký kết hôn/chứng nhận độc thân
3. Chứng minh thu nhập: Hợp đồng lao động + Sao kê lương 3–6 tháng; hoặc sao kê tài khoản kinh doanh
4. Hợp đồng mua bán nhà/đất (hoặc đặt cọc)
5. GCN QSDĐ của tài sản thế chấp
6. Bảo hiểm nhân thọ (một số ngân hàng yêu cầu)

Thời gian phê duyệt: 5–15 ngày làm việc.''',
    },
    {
        'id': 'nb-002', 'category': 'ngan_hang', 'procedure': 'mo_tai_khoan', 'level': 'ward',
        'source': 'Thông tư 23/2014/TT-NHNN',
        'question': 'Mở tài khoản ngân hàng cần gì? Có mở online được không?',
        'answer': '''Mở tài khoản thanh toán cá nhân tại ngân hàng rất đơn giản.

MỞ TRỰC TIẾP TẠI PHÒNG GIAO DỊCH:
Hồ sơ: Chỉ cần CCCD/Căn cước công dân còn hiệu lực (bản gốc).
Thời gian: 15–30 phút. Lệ phí: Miễn phí (nhiều ngân hàng).

MỞ TÀI KHOẢN ONLINE (eKYC):
- Tải app ngân hàng → Chọn "Mở tài khoản" → Chụp CCCD 2 mặt → Selfie xác thực khuôn mặt
- Hoàn tất trong 5–10 phút, không cần đến phòng giao dịch
- Áp dụng: Vietcombank (VCB Digibank), BIDV (SmartBanking), MB (App MBBank), Techcombank (TCB Mobile)...

LƯU Ý:
- Tài khoản eKYC ban đầu có giới hạn giao dịch (thường 100 triệu đ/ngày); nâng hạn bằng cách xác thực tại quầy
- Cần số điện thoại Việt Nam để nhận OTP
- Trẻ dưới 15 tuổi: Cha/mẹ đứng tên mở hộ

CÁC NGÂN HÀNG TẠI THANH HÓA:
Agribank Thanh Hóa: 05 Đại lộ Lê Lợi. BIDV Thanh Hóa: 02 Đại lộ Lê Lợi.
Vietcombank Thanh Hóa: 07 Đại lộ Lê Lợi. VietinBank: 103 Đại lộ Lê Lợi.''',
    },
    {
        'id': 'nb-003', 'category': 'ngan_hang', 'procedure': 'vay_von_san_xuat', 'level': 'district',
        'source': 'Nghị định 55/2015/NĐ-CP; Luật Các TCTD 2024',
        'question': 'Nông dân, hộ kinh doanh vay vốn sản xuất ở đâu? Được vay bao nhiêu? Thủ tục thế nào?',
        'answer': '''Nông dân và hộ kinh doanh nhỏ lẻ có thể vay vốn tại:

1. AGRIBANK (Ngân hàng NN&PTNT):
   - Cho vay nông nghiệp nông thôn theo Nghị định 55/2015
   - Vay không cần thế chấp: Đến 100 triệu đồng (cá nhân); 300 triệu đồng (hộ kinh doanh)
   - Lãi suất ưu đãi: 5–7%/năm (thấp hơn lãi suất thông thường)
   - Chỉ cần: CCCD + Giấy xác nhận hộ nông dân của UBND xã
   Agribank Thanh Hóa: 05 Đại lộ Lê Lợi. ĐT: 0237.3852.046.

2. NGÂN HÀNG CHÍNH SÁCH XÃ HỘI (NHCSXH):
   - Đối tượng: Hộ nghèo, cận nghèo, hộ mới thoát nghèo, hộ sản xuất vùng khó khăn
   - Vay qua Tổ tiết kiệm và vay vốn tại thôn/xóm (không cần thế chấp)
   - Mức vay: 50–200 triệu đồng. Lãi suất: 6,6%/năm
   NHCSXH Thanh Hóa: 119 Đại lộ Lê Lợi. ĐT: 0237.3851.248.

3. QUỸ HỖ TRỢ PHÁT TRIỂN HỢP TÁC XÃ TỈNH THANH HÓA:
   - Dành riêng cho HTX nông nghiệp, lâm nghiệp, thủy sản
   - Lãi suất bằng 50% lãi suất cho vay thông thường

THỦ TỤC CHUNG: Đơn vay + CCCD + Giấy xác nhận mục đích sử dụng vốn.''',
    },
    {
        'id': 'nb-004', 'category': 'ngan_hang', 'procedure': 'chuyen_tien_quoc_te', 'level': 'province',
        'source': 'Pháp lệnh ngoại hối 2013; Thông tư 20/2022/TT-NHNN',
        'question': 'Nhận tiền từ nước ngoài gửi về (kiều hối) thủ tục như thế nào? Có phải đóng thuế không?',
        'answer': '''Nhận kiều hối (tiền từ người thân ở nước ngoài gửi về) tại Việt Nam.

KÊNH NHẬN KIỀU HỐI:
1. Ngân hàng thương mại (Western Union, MoneyGram qua ngân hàng đại lý)
2. Công ty chuyển tiền được cấp phép: Viettel Money, MoMo, Remitly, Wise...
3. Bưu điện (qua Vietnam Post)

THỦ TỤC NHẬN:
- Người nhận: Chỉ cần CCCD + Mã giao dịch (MTCN) do người gửi cung cấp
- Nhận tiền mặt hoặc vào tài khoản ngân hàng
- Không giới hạn số lần nhận, không cần khai báo với cơ quan Nhà nước

THUẾ KIỀU HỐI:
- KHÔNG phải đóng thuế Thu nhập cá nhân đối với kiều hối từ cha, mẹ, vợ, chồng, con, anh chị em ruột
- Người khác gửi: Miễn thuế nếu số tiền nhận không vượt ngưỡng miễn trừ gia cảnh hàng năm
- Thực tế: Hầu hết kiều hối cá nhân đều không phải đóng thuế

PHÍ NHẬN KIỀU HỐI: Thường miễn phí (phí do người gửi ở nước ngoài chịu).
Tỷ giá: Ngân hàng Nhà nước quy định biên độ, ngân hàng thương mại mua theo tỷ giá thị trường.

Tại Thanh Hóa 2024: Kiều hối đạt khoảng 800 triệu USD/năm, chủ yếu từ Nhật Bản, Hàn Quốc, Đài Loan.''',
    },
    {
        'id': 'nb-005', 'category': 'ngan_hang', 'procedure': 'xu_ly_no_xau', 'level': 'province',
        'source': 'Nghị quyết 42/2017/QH14; Luật Các TCTD 2024',
        'question': 'Bị nợ xấu ngân hàng thì làm gì? Xóa nợ xấu CIC được không?',
        'answer': '''Nợ xấu là nợ nhóm 3, 4, 5 trên hệ thống CIC (Trung tâm Thông tin Tín dụng quốc gia).

CÁC MỨC NỢ XẤU:
- Nhóm 1: Đủ tiêu chuẩn (không quá hạn)
- Nhóm 2: Cần chú ý (quá hạn 10–90 ngày)
- Nhóm 3: Dưới tiêu chuẩn (91–180 ngày) — BẮT ĐẦU ẢNH HƯỞNG VAY MỚI
- Nhóm 4: Nghi ngờ (181–360 ngày)
- Nhóm 5: Có khả năng mất vốn (>360 ngày)

XỬ LÝ NỢ XẤU:
1. THANH TOÁN ĐỦ NỢ: Sau khi trả hết, nợ xấu tự động được cập nhật trên CIC (thường 5–7 ngày làm việc)
2. THƯƠNG LƯỢNG CƠ CẤU NỢ: Làm việc trực tiếp với ngân hàng để giãn nợ, giảm lãi phạt
3. MUA BÁN NỢ: Ngân hàng có thể bán nợ cho VAMC (Công ty Quản lý tài sản)

THỜI GIAN LƯU NỢ XẤU TRÊN CIC: 5 năm kể từ khi tất toán khoản nợ xấu.
→ Trong 5 năm đó vẫn khó vay mới, nhưng một số ngân hàng/công ty tài chính vẫn xét.

KHÔNG THỂ XÓA NỢ XẤU CIC bằng cách: Đóng tiền cho dịch vụ môi giới (đây là lừa đảo).
Chỉ cách duy nhất: Thanh toán đủ nợ + chờ 5 năm.

Kiểm tra nợ xấu CIC miễn phí: App "CONG CIC" hoặc website cic.org.vn.''',
    },
    {
        'id': 'nb-006', 'category': 'ngan_hang', 'procedure': 'bao_hiem_tien_gui', 'level': 'province',
        'source': 'Luật Bảo hiểm tiền gửi 2012',
        'question': 'Gửi tiết kiệm ngân hàng có an toàn không? Nếu ngân hàng phá sản thì tiền có mất không?',
        'answer': '''Tiền gửi tại ngân hàng được bảo hiểm bởi Bảo hiểm Tiền gửi Việt Nam (DIV).

MỨC BẢO HIỂM: Từ 01/01/2024, mức chi trả tối đa là 125 triệu đồng/người/ngân hàng.
(Tăng từ 75 triệu → 125 triệu đồng theo QĐ 2345/QĐ-TTg ngày 28/12/2023)

ĐỐI TƯỢNG ĐƯỢC BẢO HIỂM:
- Tiền gửi bằng VND của cá nhân tại tổ chức tham gia BHTG
- Bao gồm: Tiết kiệm, tiền gửi không kỳ hạn, có kỳ hạn

KHÔNG ĐƯỢC BẢO HIỂM:
- Tiền gửi ngoại tệ
- Tiền gửi của cổ đông lớn, thành viên HĐQT, Ban điều hành ngân hàng
- Tiền gửi để đảm bảo thực hiện nghĩa vụ của người gửi

KHI NGÂN HÀNG PHÁ SẢN:
1. DIV chi trả trong vòng 60 ngày kể từ khi có quyết định phá sản
2. Số tiền trên 125 triệu: Được giải quyết theo thứ tự ưu tiên thanh lý tài sản

KHUYẾN CÁO AN TOÀN:
- Chia nhỏ tiền gửi ra nhiều ngân hàng (mỗi ngân hàng ≤ 125 triệu để được bảo hiểm toàn bộ)
- Ưu tiên ngân hàng quốc doanh (Agribank, BIDV, Vietcombank, VietinBank) — rủi ro thấp hơn
- Không tin lãi suất "siêu cao" từ ngân hàng nhỏ/chưa kiểm chứng''',
    },
    {
        'id': 'nb-007', 'category': 'ngan_hang', 'procedure': 'the_tin_dung', 'level': 'ward',
        'source': 'Thông tư 39/2016/TT-NHNN',
        'question': 'Làm thẻ tín dụng cần điều kiện gì? Hạn mức bao nhiêu? Cách dùng để không bị phí?',
        'answer': '''Thẻ tín dụng (credit card) cho phép chi tiêu trước, trả tiền sau trong kỳ sao kê (thường 45–55 ngày miễn lãi).

ĐIỀU KIỆN MỞ THẺ:
- Thu nhập: Tối thiểu 3–5 triệu đồng/tháng (tùy ngân hàng và loại thẻ)
- Chứng minh thu nhập: Sao kê lương hoặc sao kê tài khoản 3 tháng gần nhất
- Không có nợ xấu CIC
- Tuổi: 18–65 tuổi

HẠN MỨC THẺ: Thường 2–5 lần thu nhập tháng (ví dụ lương 10 triệu → hạn mức 20–50 triệu đ)

PHÍ CẦN LƯU Ý:
- Phí thường niên: 150.000–500.000 đồng/năm (nhiều ngân hàng miễn nếu chi tiêu đủ ngưỡng)
- Lãi suất chậm trả: 25–45%/năm — rất cao, cần trả đúng hạn
- Phí rút tiền mặt: 3–4% (không nên rút tiền mặt bằng thẻ tín dụng)
- Phí giao dịch ngoại tệ: 1.5–3%

CÁCH DÙNG THÔNG MINH:
1. Luôn trả toàn bộ dư nợ trước ngày đến hạn (không chỉ trả tối thiểu)
2. Không rút tiền mặt từ thẻ tín dụng
3. Dùng thẻ tín dụng có hoàn tiền (cashback) hoặc tích điểm để có lợi
4. Đặt thông báo SMS khi có giao dịch để phát hiện gian lận sớm''',
    },
    {
        'id': 'nb-008', 'category': 'ngan_hang', 'procedure': 'thanh_toan_dien_tu', 'level': 'ward',
        'source': 'Nghị định 52/2024/NĐ-CP về thanh toán không dùng tiền mặt',
        'question': 'Các ứng dụng thanh toán điện tử nào phổ biến tại Việt Nam? Cách đăng ký và dùng an toàn?',
        'answer': '''Thanh toán điện tử không dùng tiền mặt ngày càng phổ biến, đặc biệt sau Nghị định 52/2024/NĐ-CP.

CÁC VÍ ĐIỆN TỬ PHỔ BIẾN:
- MoMo: Hơn 31 triệu người dùng — nạp tiền điện thoại, thanh toán hóa đơn, đặt vé, mua bảo hiểm
- ZaloPay: Tích hợp Zalo, dễ chuyển tiền trong nhóm bạn bè
- VNPay: Mạnh về thanh toán QR tại siêu thị, nhà hàng
- Viettel Money: Phủ sóng nông thôn, có thể rút tiền mặt tại điểm giao dịch Viettel

THANH TOÁN QUA NGÂN HÀNG SỐ: App của ngân hàng (VCB Digibank, BIDV SmartBanking, MB App...)

ĐĂNG KÝ: Tải app → Nhập số điện thoại → Xác thực OTP → Liên kết tài khoản ngân hàng → KYC (chụp CCCD + selfie)

AN TOÀN KHI DÙNG:
- Không bao giờ chia sẻ mã OTP với bất kỳ ai (kể cả người tự xưng là nhân viên ngân hàng)
- Đặt mã PIN/Face ID cho app thanh toán
- Không dùng wifi công cộng khi giao dịch tiền
- Bật thông báo giao dịch để phát hiện gian lận ngay lập tức
- Nếu nghi ngờ bị hack: Khóa ngay tài khoản qua app hoặc gọi hotline ngân hàng''',
    },
]

# =============================================================================
# 2. HỘ TỊCH BỔ SUNG (batch 2)
# =============================================================================
HO_TICH_2 = [
    {
        'id': 'ht2-001', 'category': 'ho_tich', 'procedure': 'giam_ho', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Luật Hộ tịch 2014',
        'question': 'Đăng ký giám hộ cho người thân (người già mất năng lực, trẻ mồ côi) cần làm gì?',
        'answer': '''Giám hộ là việc cá nhân/tổ chức thực hiện việc chăm sóc, bảo vệ quyền lợi cho người chưa thành niên không có cha mẹ hoặc người mất/hạn chế năng lực hành vi dân sự.

ĐĂNG KÝ GIÁM HỘ tại UBND xã/phường nơi cư trú của người được giám hộ.
Thời gian: 3 ngày làm việc. Lệ phí: Miễn phí.

CÁC TRƯỜNG HỢP CẦN ĐĂNG KÝ GIÁM HỘ:
1. Trẻ dưới 15 tuổi không có cha mẹ hoặc cha mẹ bị hạn chế quyền cha mẹ
2. Người từ 15–18 tuổi không có cha mẹ mà tài sản của họ cần được bảo vệ
3. Người mất năng lực hành vi dân sự (có quyết định của Tòa án)
4. Người có khó khăn trong nhận thức, làm chủ hành vi (có quyết định của Tòa án)

HỒ SƠ:
1. Tờ khai đăng ký giám hộ (Mẫu số 12)
2. CCCD của người giám hộ
3. Giấy tờ chứng minh điều kiện cần giám hộ:
   - Giấy chứng tử của cha/mẹ (nếu mồ côi)
   - Quyết định của Tòa án tuyên bố mất năng lực hành vi dân sự
4. Văn bản thỏa thuận cử người giám hộ (nếu có nhiều người cùng đủ điều kiện)
5. Giấy khai sinh của người được giám hộ

Người giám hộ đương nhiên (ưu tiên): Anh/chị/em ruột → Ông/bà nội ngoại → Bác/chú/cậu/cô/dì ruột.''',
    },
    {
        'id': 'ht2-002', 'category': 'ho_tich', 'procedure': 'xac_nhan_tinh_trang_hon_nhan', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Thông tư 04/2020/TT-BTP',
        'question': 'Xin giấy xác nhận tình trạng hôn nhân (độc thân) ở đâu? Cần gì? Hiệu lực bao lâu?',
        'answer': '''Giấy xác nhận tình trạng hôn nhân (xác nhận độc thân/chưa kết hôn) do UBND cấp xã/phường nơi đăng ký thường trú cấp.
Thời gian: Ngay trong ngày hoặc 3 ngày làm việc. Lệ phí: Miễn phí.
Hiệu lực: 6 tháng kể từ ngày cấp.

DÙNG KHI NÀO:
- Đăng ký kết hôn lần đầu
- Kết hôn với người nước ngoài
- Làm hồ sơ vay vốn, thừa kế
- Xin visa định cư nước ngoài (F2A, CR1...)
- Nộp hồ sơ xin việc một số cơ quan

HỒ SƠ:
1. Tờ khai xác nhận tình trạng hôn nhân (Mẫu số 17)
2. CCCD (bản gốc để đối chiếu)
3. Xuất trình sổ hộ khẩu cũ hoặc giấy xác nhận cư trú (nếu chưa cập nhật trong CSDL dân cư)

LƯU Ý: Nếu trước đây đã đăng ký kết hôn rồi ly hôn → cần nộp thêm Bản án ly hôn có hiệu lực pháp luật để UBND xã xác nhận đã ly hôn (không phải đang có vợ/chồng).

Người đang ở nước ngoài: Có thể ủy quyền cho người thân tại Việt Nam làm hộ (cần ủy quyền có công chứng).''',
    },
    {
        'id': 'ht2-003', 'category': 'ho_tich', 'procedure': 'dang_ky_lai_ho_tich', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Thông tư 04/2020/TT-BTP',
        'question': 'Mất giấy khai sinh, bằng chứng sinh thì phải làm lại như thế nào?',
        'answer': '''Đăng ký lại khai sinh (khi Sổ hộ tịch bị mất, hư hỏng, hoặc không còn lưu trữ) tại UBND xã nơi đã đăng ký khai sinh trước đây HOẶC nơi cư trú hiện tại.
Thời gian: 5 ngày làm việc. Lệ phí: Miễn phí.

HỒ SƠ:
1. Tờ khai đăng ký lại khai sinh (Mẫu 06)
2. Bản sao Giấy khai sinh đã cấp trước đây (nếu còn)
3. Các giấy tờ có thông tin về nhân thân: CCCD, Hộ chiếu, Bằng tốt nghiệp, Học bạ, Sổ BHXH, Hồ sơ lưu trữ tại cơ quan (bất kỳ giấy tờ nào có đủ thông tin: họ tên, ngày sinh, quê quán, cha mẹ)
4. CCCD của người yêu cầu đăng ký lại

TRƯỜNG HỢP KHÔNG CÒN GIẤY TỜ GÌ:
- Người từ đủ 14 tuổi tự khai + 2 người làm chứng biết rõ về việc sinh + UBND xã xác nhận
- Đối chiếu với hồ sơ lưu tại trường học, cơ quan, quân đội...

Sau khi đăng ký lại: Cần cập nhật thông tin vào CCCD, hộ chiếu và các giấy tờ khác.''',
    },
    {
        'id': 'ht2-004', 'category': 'ho_tich', 'procedure': 'nhan_cha_me_con', 'level': 'ward',
        'source': 'Luật Hôn nhân và Gia đình 2014; Luật Hộ tịch 2014',
        'question': 'Thủ tục nhận cha, mẹ, con ngoài giá thú (con ngoài hôn nhân) như thế nào?',
        'answer': '''Nhận cha, mẹ, con (ngoài giá thú) tại UBND xã/phường nơi cư trú của người nhận hoặc người được nhận.
Thời gian: 3 ngày làm việc. Lệ phí: Miễn phí.

TRƯỜNG HỢP ÁP DỤNG:
- Cha muốn nhận con sinh ra ngoài hôn nhân
- Con muốn nhận cha/mẹ không được đăng ký trên khai sinh
- Bổ sung thông tin cha/mẹ vào Giấy khai sinh

ĐIỀU KIỆN:
- Người nhận và người được nhận phải đồng ý (trừ trường hợp người được nhận là trẻ chưa đủ 9 tuổi)
- Không có tranh chấp về việc nhận (nếu tranh chấp → ra Tòa án)

HỒ SƠ:
1. Tờ khai nhận cha/mẹ/con (Mẫu 16)
2. CCCD của người nhận và người được nhận (nếu đã có)
3. Giấy khai sinh của người được nhận (bản gốc)
4. Các giấy tờ chứng minh quan hệ cha con: Kết quả xét nghiệm ADN (nếu có), ảnh chụp chung, thư từ...

Sau khi UBND xã đăng ký nhận cha/mẹ/con: Cập nhật lại Giấy khai sinh của người được nhận (bổ sung tên cha/mẹ).''',
    },
    {
        'id': 'ht2-005', 'category': 'ho_tich', 'procedure': 'doi_ten', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Luật Hộ tịch 2014',
        'question': 'Đổi tên trong giấy khai sinh, CCCD được không? Thủ tục đổi tên như thế nào?',
        'answer': '''Thay đổi họ tên trong giấy tờ hộ tịch (đổi tên) thực hiện theo thủ tục THAY ĐỔI HỘ TỊCH tại UBND xã/phường.
Thời gian: 3 ngày (đơn giản) – 15 ngày (phức tạp). Lệ phí: Miễn phí.

ĐƯỢC ĐỔI TÊN KHI:
1. Tên xấu, khó đọc, dễ gây hiểu lầm về giới tính
2. Tên gây ảnh hưởng xấu đến đời sống, sinh hoạt
3. Thay đổi họ theo họ cha/mẹ khi xác định lại cha/mẹ
4. Đổi họ theo họ chồng/vợ hoặc trở lại họ trước khi kết hôn

KHÔNG ĐƯỢC ĐỔI TÊN ĐỂ TRỐN TRÁNH PHÁP LUẬT.

HỒ SƠ:
1. Tờ khai thay đổi hộ tịch (Mẫu 11)
2. CCCD/Hộ chiếu bản gốc
3. Giấy khai sinh bản gốc
4. Văn bản chứng minh lý do đổi tên (ý kiến tư vấn phong thủy, quyết định của tòa án xác định cha mẹ...)

SAU KHI ĐƯỢC CẤP GIẤY KHAI SINH MỚI (tên mới):
1. Làm CCCD/Căn cước mới (tại Công an)
2. Đổi hộ chiếu (tại PA08 - Công an tỉnh)
3. Cập nhật Sổ BHXH (tại BHXH huyện)
4. Cập nhật tài khoản ngân hàng, bằng lái xe...
Lưu ý: Các văn bằng chứng chỉ vẫn giữ tên cũ — cần xin giấy xác nhận tên mới = tên cũ từ UBND xã.''',
    },
]

# =============================================================================
# 3. ĐẤT ĐAI BỔ SUNG (batch 2)
# =============================================================================
DAT_DAI_2 = [
    {
        'id': 'dd2-001', 'category': 'dat_dai', 'procedure': 'quy_hoach_dat', 'level': 'province',
        'source': 'Luật Đất đai 2024; Luật Quy hoạch đô thị 2009',
        'question': 'Làm sao biết mảnh đất của mình có bị quy hoạch không? Đất quy hoạch có bán được không?',
        'answer': '''Kiểm tra quy hoạch đất đai tại các kênh sau:

1. TRA CỨU ONLINE:
   - Cổng thông tin đất đai Thanh Hóa: https://bando.thanhhoa.gov.vn (bản đồ quy hoạch số)
   - Cổng thông tin quốc gia: https://quyhoach.xaydung.gov.vn
   - App "Bản đồ Quy hoạch" của Bộ Xây dựng

2. TRA CỨU TRỰC TIẾP:
   - Văn phòng ĐKDD cấp huyện nơi có đất
   - UBND xã (Cán bộ địa chính sẽ tra giúp)
   - Phòng Quản lý đô thị/Kinh tế hạ tầng UBND huyện

THÔNG TIN CẦN BIẾT TỪ BẢN ĐỒ QUY HOẠCH:
- Ký hiệu ô đất (ONT = đất ở; CLN = đất cây lâu năm; BHT = giao thông; CV = cây xanh...)
- Chỉ tiêu quy hoạch: Mật độ xây dựng, tầng cao tối đa, hệ số sử dụng đất

ĐẤT QUY HOẠCH CÓ BÁN ĐƯỢC KHÔNG?
- Đất trong quy hoạch treo (chưa thu hồi): Vẫn được mua bán, nhưng hạn chế cải tạo xây dựng
- Đất đã có quyết định thu hồi: KHÔNG được bán (giao dịch vô hiệu)
- Đất nằm trong hành lang bảo vệ đê, lộ giới đường: Hạn chế xây dựng, vẫn mua bán được''',
    },
    {
        'id': 'dd2-002', 'category': 'dat_dai', 'procedure': 'den_bu_gpmb', 'level': 'province',
        'source': 'Luật Đất đai 2024; Nghị định 88/2024/NĐ-CP',
        'question': 'Bị thu hồi đất để làm dự án, được đền bù bao nhiêu? Không đồng ý thì làm gì?',
        'answer': '''Khi Nhà nước thu hồi đất, người sử dụng đất được bồi thường, hỗ trợ và tái định cư theo quy định Luật Đất đai 2024.

MỨC BỒI THƯỜNG:
- Đất ở: Theo giá đất cụ thể do UBND tỉnh quyết định (không thấp hơn giá thị trường)
- Tài sản trên đất (nhà, cây cối, hoa màu): Theo giá xây dựng mới/giá thị trường
- Đất nông nghiệp: Theo bảng giá đất UBND tỉnh × hệ số điều chỉnh (K)

HỖ TRỢ THÊM (ngoài bồi thường):
- Hỗ trợ di chuyển: 4–7 triệu đồng/hộ (tùy địa phương)
- Hỗ trợ ổn định đời sống: 6–12 tháng tiền sinh hoạt
- Hỗ trợ chuyển đổi nghề: Nếu mất đất nông nghiệp đang sản xuất

KHI KHÔNG ĐỒNG Ý VỚI MỨC ĐỀN BÙ:
1. Khiếu nại đến Chủ tịch UBND huyện (trong 30 ngày từ khi nhận Quyết định bồi thường)
2. Nếu không thỏa mãn: Khiếu nại tiếp lên Chủ tịch UBND tỉnh
3. Hoặc: Khởi kiện ra Tòa án Hành chính (TAND tỉnh)
4. Không tự ý cản trở thi công sau khi hết thời gian khiếu nại → bị cưỡng chế

Hội đồng bồi thường tại Thanh Hóa: Sở TNMT phối hợp với UBND huyện thực hiện.
ĐT hỗ trợ: 0237.3752.262 (Sở TNMT Thanh Hóa).''',
    },
    {
        'id': 'dd2-003', 'category': 'dat_dai', 'procedure': 'tranh_chap_dat', 'level': 'district',
        'source': 'Luật Đất đai 2024; Luật Hòa giải cơ sở 2013',
        'question': 'Tranh chấp đất với hàng xóm phải giải quyết ở đâu? Quy trình thế nào?',
        'answer': '''Tranh chấp đất đai (ranh giới, quyền sử dụng, thừa kế đất...) được giải quyết theo trình tự:

BƯỚC 1 — HÒA GIẢI CƠ SỞ (bắt buộc):
- Nộp đơn yêu cầu hòa giải tại UBND xã nơi có đất tranh chấp
- Thời gian: 45 ngày (có thể gia hạn 1 lần)
- Tổ hòa giải + đại diện UBND tổ chức hòa giải các bên
- Nếu HÒA GIẢI THÀNH: Lập biên bản, các bên thực hiện
- Nếu KHÔNG THÀNH CÔNG: Mới được khiếu nại hoặc khởi kiện

BƯỚC 2 — KHIẾU NẠI HÀNH CHÍNH hoặc KHỞI KIỆN DÂN SỰ:

Đối với đất có GCN (tranh chấp ai là chủ):
→ Khởi kiện ra TAND cấp huyện (giải quyết theo thủ tục dân sự)

Đối với tranh chấp ai có quyền quản lý, sử dụng đất:
→ Nộp đơn đến UBND cấp huyện hoặc UBND tỉnh (tùy loại đất)
→ Không đồng ý kết quả: Khiếu nại tiếp hoặc kiện hành chính ra Tòa

HỒ SƠ KHỞI KIỆN DÂN SỰ:
1. Đơn khởi kiện (Mẫu 23-DS)
2. GCN QSDĐ hoặc giấy tờ chứng minh quyền sử dụng
3. Biên bản hòa giải không thành tại UBND xã
4. Sơ đồ, bản đồ tranh chấp
5. Chứng cứ khác (giấy tờ mua bán, thừa kế, nhân chứng...)

TAND huyện Đông Sơn giải quyết đất đai TP Thanh Hóa: 35 Lý Nam Đế, TP Thanh Hóa.''',
    },
    {
        'id': 'dd2-004', 'category': 'dat_dai', 'procedure': 'cho_thue_dat', 'level': 'district',
        'source': 'Luật Đất đai 2024; Bộ luật Dân sự 2015',
        'question': 'Cho thuê nhà đất cần hợp đồng công chứng không? Thủ tục đăng ký cho thuê ra sao?',
        'answer': '''Hợp đồng cho thuê nhà đất cá nhân với nhau.

CÓ BẮT BUỘC CÔNG CHỨNG KHÔNG?
- Luật pháp KHÔNG BẮT BUỘC công chứng hợp đồng thuê nhà ở/đất giữa cá nhân
- Nhưng KHUYẾN NGHỊ nên công chứng để bảo vệ quyền lợi cả hai bên
- Hợp đồng không công chứng vẫn có hiệu lực pháp lý nếu đúng quy định (tự nguyện, không trái pháp luật)

THUÊ NHÀ DÀI HẠN (≥ 6 tháng) NÊN CÓ HỢP ĐỒNG VIẾT:
Nội dung tối thiểu:
1. Thông tin các bên (tên, CCCD, địa chỉ)
2. Thông tin tài sản cho thuê (địa chỉ, diện tích, tình trạng)
3. Thời hạn thuê, mức giá thuê, phương thức thanh toán
4. Tiền đặt cọc (thường 1–3 tháng tiền thuê)
5. Quyền và nghĩa vụ hai bên (sửa chữa, điện nước, khách ở...)
6. Điều kiện chấm dứt hợp đồng và bồi thường

THUẾ KHI CHO THUÊ NHÀ:
- Thu nhập từ cho thuê tài sản ≥ 100 triệu đồng/năm: Nộp thuế TNCN 5% + thuế Môn bài 1 triệu đ/năm
- Dưới 100 triệu/năm: Miễn thuế
- Kê khai tại Chi cục Thuế nơi có tài sản cho thuê''',
    },
    {
        'id': 'dd2-005', 'category': 'dat_dai', 'procedure': 'dang_ky_nha_o_xa_hoi', 'level': 'province',
        'source': 'Luật Nhà ở 2023; Nghị định 100/2024/NĐ-CP',
        'question': 'Mua nhà ở xã hội, nhà ở thu nhập thấp tại Thanh Hóa cần điều kiện gì?',
        'answer': '''Nhà ở xã hội (NOXH) dành cho người thu nhập thấp, công nhân, cán bộ công chức.

ĐIỀU KIỆN MUA NOXH (Luật Nhà ở 2023):
1. Chưa có nhà ở tại tỉnh Thanh Hóa HOẶC có nhà nhưng dưới 10m²/người
2. Thu nhập: Không thuộc diện chịu thuế TNCN (thu nhập bình quân ≤ 11 triệu đ/tháng năm 2024)
3. Đã đăng ký thường trú/tạm trú từ đủ 1 năm tại tỉnh có dự án NOXH

ƯU ĐÃI:
- Giá bán thấp hơn thị trường 20–40%
- Vay vốn ưu đãi lãi suất 4,8%/năm từ Ngân hàng Chính sách Xã hội (cho CB-CC-LLVT)
- Gói vay 120.000 tỷ đồng lãi suất 7–8%/năm (ngân hàng thương mại)

CÁC DỰ ÁN NOXH TẠI THANH HÓA (2024):
- Khu nhà ở xã hội Đông Sơn (Phường Đông Sơn, TP Thanh Hóa): ~500 căn hộ
- Khu NOXH phường Đông Hải, TP Thanh Hóa: Đang xây dựng
- Khu công nghiệp Hoàng Long, Nghi Sơn: Nhà ở công nhân

ĐĂNG KÝ MUA:
- Nộp hồ sơ tại chủ đầu tư dự án khi có thông báo mở bán
- UBND tỉnh xét duyệt danh sách đủ điều kiện (bốc thăm nếu vượt chỉ tiêu)
- Liên hệ: Sở Xây dựng Thanh Hóa: 0237.3852.601.''',
    },
]

# =============================================================================
# 4. LAO ĐỘNG BỔ SUNG (batch 2)
# =============================================================================
LAO_DONG_2 = [
    {
        'id': 'ld2-001', 'category': 'lao_dong', 'procedure': 'luong_toi_thieu', 'level': 'district',
        'source': 'Nghị định 74/2024/NĐ-CP (hiệu lực 01/7/2024)',
        'question': 'Lương tối thiểu vùng 2024 tại Thanh Hóa là bao nhiêu? Làm thêm giờ được tính thế nào?',
        'answer': '''LƯƠNG TỐI THIỂU VÙNG 2024 (từ 01/7/2024, theo Nghị định 74/2024/NĐ-CP):
- Vùng I (TP Thanh Hóa, TX Bỉm Sơn, TX Sầm Sơn): 4.960.000 đồng/tháng
- Vùng II (các huyện còn lại tỉnh Thanh Hóa): 4.410.000 đồng/tháng
- Vùng III (huyện miền núi): 3.860.000 đồng/tháng
- Vùng IV (xã vùng cao, đặc biệt khó khăn): 3.450.000 đồng/tháng

LƯƠNG LÀM THÊM GIỜ (Điều 98 BLLĐ 2019):
- Ngày thường: Ít nhất 150% lương giờ bình thường
- Ngày nghỉ hàng tuần: Ít nhất 200%
- Ngày lễ, Tết: Ít nhất 300% (chưa kể tiền lương ngày lễ nếu đã hưởng)
- Giới hạn làm thêm: ≤ 40 giờ/tháng và ≤ 200 giờ/năm (ngành đặc thù: 300 giờ/năm)

LÀM ĐÊM (22:00–06:00):
- Thêm ít nhất 30% lương giờ bình thường
- Làm thêm giờ + ban đêm: Thêm ít nhất 20% phụ cấp làm đêm

NẾU CÔNG TY KHÔNG TRẢ ĐÚNG: Khiếu nại đến Thanh tra Sở LĐTBXH Thanh Hóa.
ĐT: 0237.3852.197.''',
    },
    {
        'id': 'ld2-002', 'category': 'lao_dong', 'procedure': 'nghi_phep_nam', 'level': 'district',
        'source': 'Bộ luật Lao động 2019',
        'question': 'Người lao động được nghỉ phép mấy ngày/năm? Có được thanh toán tiền phép không?',
        'answer': '''NGÀY NGHỈ PHÉP NĂM (Điều 113 BLLĐ 2019):
- Làm đủ 12 tháng: Tối thiểu 12 ngày/năm (có lương)
- Làm chưa đủ 12 tháng: Số ngày tỷ lệ theo số tháng làm việc
- Thâm niên cứ 5 năm: Cộng thêm 1 ngày phép
- Lao động chưa thành niên, người khuyết tật, làm nặng nhọc độc hại: 14 ngày/năm
- Làm việc nguy hiểm đặc biệt: 16 ngày/năm

NGHỈ LỄ, TẾT (Điều 112 — được nghỉ hưởng nguyên lương):
- Tết Dương lịch: 1 ngày
- Tết Âm lịch: 5 ngày (riêng 2025: 9 ngày do nghị quyết đặc biệt)
- Giỗ Tổ Hùng Vương (10/3 âm lịch): 1 ngày
- Ngày Giải phóng (30/4): 1 ngày
- Ngày Quốc tế Lao động (1/5): 1 ngày
- Quốc khánh (2/9): 2 ngày
Tổng: ít nhất 11 ngày lễ/năm

THANH TOÁN TIỀN PHÉP:
- Người lao động được trả tiền những ngày phép chưa nghỉ khi CHẤM DỨT hợp đồng
- Không được quy đổi phép thành tiền nếu HĐ còn hiệu lực (trừ thỏa thuận)
- Tự ý không nghỉ phép trong năm: Tiền phép không mang sang năm sau (trừ thỏa thuận)''',
    },
    {
        'id': 'ld2-003', 'category': 'lao_dong', 'procedure': 'tranh_chap_lao_dong', 'level': 'district',
        'source': 'Bộ luật Lao động 2019; Bộ luật Tố tụng dân sự 2015',
        'question': 'Bị công ty sa thải oan, không trả lương, xử lý kỷ luật sai thì khiếu nại ở đâu?',
        'answer': '''Tranh chấp lao động cá nhân (giữa NLĐ và NSDLĐ) giải quyết theo trình tự:

BƯỚC 1 — HÒA GIẢI (trong 5 ngày):
Nộp đơn đến Hòa giải viên lao động tại Phòng LĐTBXH cấp huyện.
Nếu hòa giải thành: Biên bản có giá trị thi hành.
Không hòa giải được/quá hạn: Chuyển bước 2.

BƯỚC 2 — KHỞI KIỆN RA TAND CẤP HUYỆN:
Các trường hợp không cần qua hòa giải (kiện thẳng):
- Bị sa thải trái pháp luật
- Tranh chấp về bồi thường thiệt hại
- Tranh chấp giữa giúp việc gia đình với chủ nhà

Thời hiệu khởi kiện: 1 năm kể từ ngày phát hiện hành vi vi phạm.
Án phí: 300.000 đồng (NLĐ khởi kiện có thể được miễn nếu hộ nghèo).

ĐỒNG THỜI: Tố cáo vi phạm đến Thanh tra Sở LĐTBXH:
- Không ký HĐLĐ, không đóng BHXH, không trả lương, quấy rối...
- Thanh tra vào kiểm tra và xử phạt doanh nghiệp (5–200 triệu đồng/vi phạm)

Tư vấn miễn phí: Liên đoàn Lao động tỉnh Thanh Hóa: 0237.3852.015.
Trợ giúp pháp lý: Trung tâm TGPL Thanh Hóa: 0237.3851.666.''',
    },
    {
        'id': 'ld2-004', 'category': 'lao_dong', 'procedure': 'nghi_om', 'level': 'district',
        'source': 'Luật BHXH 2014; Nghị định 115/2015/NĐ-CP',
        'question': 'Chế độ ốm đau BHXH: Nghỉ ốm mấy ngày được hưởng? Mức hưởng bao nhiêu?',
        'answer': '''Chế độ ốm đau áp dụng cho lao động đang đóng BHXH bắt buộc.

SỐ NGÀY NGHỈ ỐM TỐI ĐA TRONG NĂM (tùy điều kiện làm việc):
- Điều kiện bình thường: 30 ngày (đóng BHXH dưới 15 năm); 40 ngày (15–30 năm); 60 ngày (trên 30 năm)
- Làm nặng nhọc, độc hại: 40 ngày (dưới 15 năm); 50 ngày (15–30 năm); 70 ngày (trên 30 năm)

MỨC HƯỞNG:
- 75% mức lương đóng BHXH của tháng liền trước khi nghỉ
- Ví dụ: Lương đóng BHXH 8 triệu → hưởng 6 triệu/tháng khi nghỉ ốm

NGHỈ ỐM DÀI NGÀY (bệnh cần điều trị dài ngày theo danh mục BYT):
- Tối đa 180 ngày/năm
- Sau 180 ngày vẫn còn ốm: Hưởng tiếp 65% lương (nếu đóng ≥ 30 năm) hoặc 55% (đóng dưới 30 năm)

HỒ SƠ HƯỞNG CHẾ ĐỘ:
1. Giấy ra viện HOẶC Giấy chứng nhận nghỉ ốm (do bác sĩ cấp, không quá 30 ngày/lần)
2. Đơn vị sử dụng lao động lập danh sách đề nghị BHXH thanh toán (hàng quý)
3. Tiền được chuyển trả qua lương hàng tháng

3 NGÀY NGHỈ ỐM ĐẦU: Do doanh nghiệp trả 100% (theo thỏa thuận HĐLĐ hoặc Thỏa ước LĐ tập thể).''',
    },
    {
        'id': 'ld2-005', 'category': 'lao_dong', 'procedure': 'lao_dong_nuoc_ngoai', 'level': 'province',
        'source': 'Luật Người nước ngoài LĐ tại VN (Bộ luật LĐ 2019)',
        'question': 'Người nước ngoài làm việc tại Thanh Hóa cần giấy phép lao động không? Thủ tục cấp ở đâu?',
        'answer': '''Người nước ngoài làm việc tại Việt Nam cần Giấy phép lao động (GPLĐ) do Sở LĐTBXH cấp.
Địa chỉ: Sở LĐTBXH Thanh Hóa, 24 Hải Thượng Lãn Ông, TP Thanh Hóa. ĐT: 0237.3852.197.

ĐƯỢC MIỄN GPLĐ:
- Chủ sở hữu/thành viên góp vốn công ty có giá trị vốn ≥ 3 tỷ VNĐ
- Di chuyển nội bộ trong doanh nghiệp đa quốc gia (dưới 90 ngày/năm)
- Vào để chào bán, đàm phán hợp đồng (dưới 30 ngày, không quá 3 lần/năm)
- Chuyên gia, nhà quản lý người nước ngoài làm việc ngắn hạn dưới 30 ngày/năm

CẦN GPLĐ (thời hạn tối đa 2 năm, gia hạn được):
Hồ sơ xin cấp GPLĐ:
1. Văn bản đề nghị của doanh nghiệp
2. Sơ yếu lý lịch (lý lịch cá nhân)
3. Văn bằng, chứng chỉ chứng minh trình độ chuyên môn
4. Lý lịch tư pháp nước ngoài (hợp pháp hóa lãnh sự + dịch thuật công chứng)
5. Giấy khám sức khỏe (do cơ sở y tế Việt Nam cấp)
6. Ảnh 4×6 cm; Hộ chiếu bản sao

Thời gian: 10 ngày làm việc. Lệ phí: 400.000 đồng/lần cấp.''',
    },
]

# =============================================================================
# 5. THUE BỔ SUNG (batch 2)
# =============================================================================
THUE_2 = [
    {
        'id': 'th2-001', 'category': 'thue', 'procedure': 'hoa_don_dien_tu', 'level': 'district',
        'source': 'Luật Quản lý thuế 2019; Nghị định 123/2020/NĐ-CP; Thông tư 78/2021/TT-BTC',
        'question': 'Hộ kinh doanh, doanh nghiệp bắt buộc dùng hóa đơn điện tử chưa? Đăng ký thế nào?',
        'answer': '''Từ 01/7/2022, TẤT CẢ doanh nghiệp và hộ kinh doanh BẮT BUỘC sử dụng hóa đơn điện tử (HĐĐT).
Không dùng HĐĐT: Phạt 2–10 triệu đồng.

2 LOẠI HÓA ĐƠN ĐIỆN TỬ:
1. HĐĐT CÓ MÃ CỦA CQT (cơ quan thuế): Doanh nghiệp gửi dữ liệu lên cổng CQT, cổng xác nhận và cấp mã, sau đó gửi cho khách hàng
2. HĐĐT KHÔNG CÓ MÃ: Doanh nghiệp lớn (doanh thu >50 tỷ/năm) được phép phát hành không qua cổng CQT nhưng phải gửi dữ liệu lên cổng sau

ĐĂNG KÝ SỬ DỤNG HĐĐT:
1. Đăng ký qua cổng thuế: https://hoadondientu.gdt.gov.vn → Đăng ký tờ khai 06/ĐKTĐ-HĐĐT
2. Hoặc đăng ký qua phần mềm HĐĐT của bên thứ 3 (MISA, FAST, VIETTEL, VNPT E-Invoice...)
3. Cục/Chi cục Thuế xét duyệt trong 1 ngày làm việc
4. Sau khi được duyệt → Phát hành hóa đơn trên phần mềm

PHÍ PHẦN MỀM HĐĐT: Tùy nhà cung cấp, thường 200.000–1.000.000 đồng/năm.
Hộ kinh doanh có doanh thu nhỏ: Được sử dụng HĐĐT miễn phí tại cổng https://hoadondientu.gdt.gov.vn

Hỗ trợ đăng ký HĐĐT: Cục Thuế Thanh Hóa: 0237.3850.068.''',
    },
    {
        'id': 'th2-002', 'category': 'thue', 'procedure': 'thue_tndn', 'level': 'province',
        'source': 'Luật Thuế TNDN 2008 sửa đổi; Nghị định 218/2013/NĐ-CP',
        'question': 'Doanh nghiệp nộp thuế Thu nhập doanh nghiệp (TNDN) như thế nào? Tỷ lệ bao nhiêu?',
        'answer': '''Thuế Thu nhập doanh nghiệp (TNDN) = Thu nhập tính thuế × Thuế suất.
Thu nhập tính thuế = Doanh thu - Chi phí được trừ - Thu nhập miễn thuế.

THUẾ SUẤT TNDN:
- Thông thường: 20% (áp dụng cho đại đa số doanh nghiệp)
- Doanh nghiệp nhỏ và siêu nhỏ (doanh thu ≤ 3 tỷ/năm): 15–17% (tùy quy mô)
- Khai thác khoáng sản: 40–50%
- Hoạt động xổ số, casino: 32%
- Dự án đầu tư tại vùng khuyến khích (KKT Nghi Sơn): 10% (15 năm)

KÊ KHAI VÀ NỘP THUẾ TNDN:
- Tạm nộp theo quý: Nộp chậm nhất ngày 30 của tháng tiếp theo mỗi quý
- Quyết toán năm: Nộp tờ khai và nộp thuế trước ngày 31/3 năm sau
- Kê khai online tại: https://thuedientu.gdt.gov.vn

CHI PHÍ ĐƯỢC TRỪ (hợp lệ):
- Chi phí nhân công (lương, BHXH)
- Nguyên vật liệu, hàng hóa
- Khấu hao tài sản cố định
- Lãi vay (trong giới hạn 30% EBITDA)
- Phải có hóa đơn hợp lệ kèm theo

CHI PHÍ KHÔNG ĐƯỢC TRỪ: Phạt vi phạm hành chính, chi hoa hồng không có hợp đồng...''',
    },
    {
        'id': 'th2-003', 'category': 'thue', 'procedure': 'thue_gtgt', 'level': 'district',
        'source': 'Luật Thuế GTGT 2008 sửa đổi; Nghị định 209/2013/NĐ-CP',
        'question': 'Thuế VAT (GTGT) bao nhiêu %? Hàng hóa nào miễn thuế VAT?',
        'answer': '''Thuế Giá trị gia tăng (GTGT/VAT) là thuế đánh vào giá trị tăng thêm của hàng hóa, dịch vụ.

CÁC MỨC THUẾ SUẤT VAT HIỆN HÀNH:
- 0%: Hàng hóa xuất khẩu, vận tải quốc tế, dịch vụ xuất khẩu
- 5%: Nước sạch, phân bón, thuốc bảo vệ thực vật, máy móc nông nghiệp, thức ăn chăn nuôi, sách giáo khoa, đồ chơi trẻ em, dịch vụ khám chữa bệnh, giáo dục
- 10% (tiêu chuẩn): Hầu hết hàng hóa dịch vụ còn lại

Lưu ý: Từ 01/7/2025 thuế suất VAT tổng quát là 10% (đã hết giảm xuống 8%).

KHÔNG CHỊU THUẾ VAT (miễn thuế):
- Sản phẩm nông nghiệp chưa chế biến (lúa, ngô, rau, quả tươi...)
- Dịch vụ tín dụng, kinh doanh chứng khoán, bảo hiểm nhân thọ
- Nhà ở xã hội do Nhà nước đầu tư bán cho người thu nhập thấp
- Dạy học, dạy nghề
- Báo chí, xuất bản sách

KHAI VÀ NỘP VAT:
- Doanh nghiệp lớn (phương pháp khấu trừ): Kê khai hàng tháng hoặc quý
- Hộ kinh doanh (phương pháp khoán): Nộp theo thông báo của cơ quan thuế''',
    },
    {
        'id': 'th2-004', 'category': 'thue', 'procedure': 'khoan_thue_ho_kinh_doanh', 'level': 'district',
        'source': 'Thông tư 40/2021/TT-BTC',
        'question': 'Hộ kinh doanh cá thể nộp thuế gì? Mức thuế khoán bao nhiêu?',
        'answer': '''Hộ kinh doanh cá thể nộp 3 loại thuế: Thuế môn bài + Thuế GTGT + Thuế TNCN (theo phương pháp khoán).

THUẾ MÔN BÀI (hàng năm):
- Doanh thu > 500 triệu đồng/năm: 1.000.000 đồng/năm
- Doanh thu 300–500 triệu đồng/năm: 500.000 đồng/năm
- Doanh thu ≤ 300 triệu đồng/năm: 300.000 đồng/năm
- Doanh thu ≤ 100 triệu đồng/năm: MIỄN thuế môn bài

THUẾ KHOÁN (GTGT + TNCN):
Cơ quan thuế ấn định mức thuế khoán hàng năm dựa trên:
- Ngành nghề kinh doanh
- Địa điểm kinh doanh
- Quy mô doanh thu thực tế ước tính

Ví dụ (tham khảo): Quán ăn nhỏ tại TP Thanh Hóa, doanh thu ~300 triệu/năm:
- Thuế GTGT ~3% × 300 triệu = 9 triệu đồng/năm
- Thuế TNCN ~1,5% × 300 triệu = 4,5 triệu đồng/năm
- Tổng khoảng 13,5 triệu + 300.000 môn bài

DOANH THU ≤ 100 TRIỆU/NĂM: MIỄN cả thuế GTGT và TNCN.

Nộp tờ khai tại Chi cục Thuế cấp huyện nơi kinh doanh.
Tra cứu mức thuế khoán tại: Chi cục Thuế hoặc cổng thuedientu.gdt.gov.vn.''',
    },
]

# =============================================================================
# 6. GIAO THÔNG BỔ SUNG (batch 2)
# =============================================================================
GIAO_THONG_2 = [
    {
        'id': 'gt2-001', 'category': 'giao_thong', 'procedure': 'phat_vi_pham_giao_thong', 'level': 'province',
        'source': 'Nghị định 100/2019/NĐ-CP; Nghị định 123/2021/NĐ-CP',
        'question': 'Mức phạt vi phạm giao thông 2024 khi uống rượu bia lái xe là bao nhiêu?',
        'answer': '''Xử phạt vi phạm nồng độ cồn theo Nghị định 100/2019 (hiệu lực từ 01/01/2020):

ĐỐI VỚI XE MÁY:
- Mức 1 (0 < nồng độ cồn ≤ 50mg/100ml máu hoặc ≤ 0,25mg/1L khí thở):
  Phạt 2–3 triệu đồng + Tước GPLX 10–12 tháng
- Mức 2 (50–80mg/100ml máu hoặc 0,25–0,4mg/1L khí thở):
  Phạt 4–5 triệu đồng + Tước GPLX 16–18 tháng
- Mức 3 (> 80mg/100ml máu hoặc > 0,4mg/1L khí thở):
  Phạt 6–8 triệu đồng + Tước GPLX 22–24 tháng

ĐỐI VỚI Ô TÔ:
- Mức 1: Phạt 6–8 triệu + Tước GPLX 10–12 tháng
- Mức 2: Phạt 16–18 triệu + Tước GPLX 16–18 tháng
- Mức 3: Phạt 30–40 triệu + Tước GPLX 22–24 tháng

KHÔNG HỢP TÁC (không chịu kiểm tra nồng độ cồn):
→ Bị phạt như Mức 3 (mức cao nhất)

CÁC VI PHẠM PHỔ BIẾN KHÁC (2024):
- Vượt đèn đỏ (xe máy): 1–2 triệu đồng
- Không đội mũ bảo hiểm: 300.000–400.000 đồng
- Sử dụng điện thoại khi lái xe (ô tô): 3–5 triệu + Tước GPLX 1–3 tháng
- Chạy quá tốc độ > 35km/h (ô tô): 10–12 triệu + Tước GPLX 2–4 tháng''',
    },
    {
        'id': 'gt2-002', 'category': 'giao_thong', 'procedure': 'bien_so_xe', 'level': 'district',
        'source': 'Nghị định 10/2020/NĐ-CP; Thông tư 58/2020/TT-BCA',
        'question': 'Biển số xe Thanh Hóa là bao nhiêu? Mua xe cũ có giữ lại biển số không?',
        'answer': '''Biển số xe Thanh Hóa: 36-xx xxxx (ô tô) hoặc 36-x1 xxxx (xe máy).

KÝ HIỆU ĐẦU BIỂN SỐ THEO HUYỆN/THỊ:
- 36-A: TP Thanh Hóa
- 36-B: TX Sầm Sơn, Hoằng Hóa, Thiệu Hóa
- 36-C: TX Bỉm Sơn, Hà Trung, Nga Sơn
- 36-E: Thạch Thành, Vĩnh Lộc
- 36-F: Yên Định, Cẩm Thủy
- 36-K: Quan Sơn, Mường Lát, Quan Hóa, Bá Thước
- 36-L: Thọ Xuân, Ngọc Lặc
- 36-M: TX Nghi Sơn (cũ: Tĩnh Gia)
- 36-N: Hậu Lộc, Quảng Xương
- 36-P: Đông Sơn, Triệu Sơn, Nông Cống

MUA XE CŨ — BIỂN SỐ:
- Xe ô tô: Biển số THEO XE (không theo chủ), người mua giữ lại biển số cũ
- Xe máy: Biển số THEO CHỦ, khi chuyển nhượng phải bốc biển mới theo địa chỉ thường trú người mua
- Trường hợp người mua cùng tỉnh: Vẫn phải đổi biển nếu khác huyện (với xe máy)

ĐẤU GIÁ BIỂN SỐ Ô TÔ ĐẸP:
Từ 01/9/2023, Bộ CA tổ chức đấu giá biển số đẹp online tại: https://daugiabienso.mca.gov.vn
Giá trúng thầu: Từ vài chục triệu đến hàng tỷ đồng.''',
    },
    {
        'id': 'gt2-003', 'category': 'giao_thong', 'procedure': 'xe_dien', 'level': 'district',
        'source': 'Nghị định 10/2020/NĐ-CP; Thông tư 12/2021/TT-BGTVT',
        'question': 'Xe máy điện, xe đạp điện có cần đăng ký biển số, bảo hiểm, bằng lái không?',
        'answer': '''Quy định về xe điện 2024:

XE ĐẠP ĐIỆN (vận tốc tối đa ≤ 25km/h, công suất ≤ 250W):
- KHÔNG cần đăng ký biển số
- KHÔNG cần bằng lái xe
- KHÔNG cần bảo hiểm trách nhiệm dân sự bắt buộc
- Người điều khiển phải đội mũ bảo hiểm (xe đạp điện được coi là xe thô sơ có động cơ)

XE MÁY ĐIỆN (vận tốc > 25km/h hoặc công suất > 250W):
- PHẢI đăng ký biển số (như xe máy thông thường)
- PHẢI có bảo hiểm trách nhiệm dân sự bắt buộc
- Người từ 16 tuổi trở lên mới được lái
- Bằng lái: Không cần (xe máy điện < 50cc) HOẶC cần bằng A1 (xe máy điện ≥ 50cc)

Ô TÔ ĐIỆN: Đăng ký, bảo hiểm, bằng lái như ô tô xăng bình thường.

MIỄN LỆ PHÍ TRƯỚC BẠ:
Đến hết 2025, ô tô điện được miễn 100% lệ phí trước bạ (theo Nghị định 41/2023/NĐ-CP).
Xe máy điện: Lệ phí trước bạ 1% (thay vì 2% như xe máy xăng).

Đăng ký xe máy điện: Nộp tại Công an cấp huyện nơi thường trú, hồ sơ tương tự xe máy thông thường.''',
    },
]

# =============================================================================
# 7. XÂY DỰNG BỔ SUNG (batch 2)
# =============================================================================
XAY_DUNG_2 = [
    {
        'id': 'xd2-001', 'category': 'xay_dung', 'procedure': 'chung_cu', 'level': 'province',
        'source': 'Luật Nhà ở 2023; Luật Kinh doanh BĐS 2023',
        'question': 'Mua căn hộ chung cư cần lưu ý gì? Pháp lý như thế nào? Sổ hồng chung cư cấp bao lâu?',
        'answer': '''MUA CHUNG CƯ TẠI THANH HÓA — ĐIỂM CẦN LƯU Ý:

PHÁP LÝ DỰ ÁN (kiểm tra trước khi đặt cọc):
1. Giấy phép xây dựng còn hiệu lực
2. Quyết định giao đất/cho thuê đất của UBND tỉnh
3. Thông báo đủ điều kiện bán nhà hình thành trong tương lai (từ Sở Xây dựng)
4. Hợp đồng bảo lãnh của ngân hàng (bắt buộc theo Luật KD BĐS 2014; Luật mới 2023 vẫn duy trì)
5. GCN QSDĐ hoặc quyết định giao đất cho chủ đầu tư

HỢP ĐỒNG MUA BÁN:
- Ký với chủ đầu tư (không qua sàn giao dịch trực tiếp)
- Điều khoản quan trọng: Giá bán, tiến độ thanh toán, ngày bàn giao, phạt chậm bàn giao, phí quản lý

CẤP SỔ HỒNG CHUNG CƯ:
- Pháp lý: Chủ đầu tư hoàn thành nghĩa vụ thuế + Bộ phận quản lý vận hành được thành lập
- Thời gian: 50 ngày theo pháp luật, thực tế 6 tháng – 2 năm tùy dự án
- Nếu chủ đầu tư chậm cấp sổ: Có thể khởi kiện ra tòa hoặc phản ánh Sở Xây dựng

CHUNG CƯ TẠI THANH HÓA (một số dự án tiêu biểu 2024):
- FLC Thanh Hóa (Sầm Sơn): Phức hợp cao cấp
- Eurowindow Twin Parks (TP Thanh Hóa): Dự án đang triển khai
- Khu đô thị Đông Bắc ga (TP Thanh Hóa)
Liên hệ tư vấn: Sở Xây dựng Thanh Hóa: 0237.3852.601.''',
    },
    {
        'id': 'xd2-002', 'category': 'xay_dung', 'procedure': 'giai_phong_mat_bang', 'level': 'province',
        'source': 'Luật Đất đai 2024; Nghị định 88/2024/NĐ-CP',
        'question': 'Khi làm đường, làm dự án mà đất nhà tôi nằm trong hành lang, phải xử lý thế nào?',
        'answer': '''Khi công trình công cộng (đường, kênh mương, dự án Nhà nước) đi qua đất tư nhân:

NẾU ĐẤT NẰM TRONG PHẠM VI THU HỒI:
- Nhà nước ra Quyết định thu hồi đất
- Người dân được bồi thường + hỗ trợ + tái định cư (xem mục "Thu hồi đất đền bù")
- Thời gian từ thông báo → thực hiện thu hồi: Tối thiểu 90 ngày (đất nông nghiệp), 180 ngày (đất ở)

NẾU ĐẤT NẰM TRONG HÀNH LANG BẢO VỆ (không thu hồi nhưng hạn chế):
Hành lang đường bộ:
- Quốc lộ: Tùy loại đường (Cấp I: 17m; Cấp II: 13m; Cấp III: 9m tính từ tim đường)
- Tỉnh lộ: 7–9m từ tim đường
Hành lang đê điều: 5–25m (tùy loại đê)
Hành lang điện cao thế: 7–45m (tùy cấp điện áp)

QUYỀN LỢI TRONG HÀNH LANG:
- Được đền bù hoa màu, công trình phụ bị ảnh hưởng
- Không được xây dựng mới, cải tạo lớn trong phạm vi hành lang
- Có thể yêu cầu bồi thường thiệt hại do hạn chế sử dụng

PHẢN ĐỐI QUYẾT ĐỊNH THU HỒI: Khiếu nại theo thủ tục hành chính (xem mục Khiếu nại).''',
    },
    {
        'id': 'xd2-003', 'category': 'xay_dung', 'procedure': 'sua_chua_nha', 'level': 'ward',
        'source': 'Luật Xây dựng 2014 sửa đổi 2020; Nghị định 15/2021/NĐ-CP',
        'question': 'Sửa nhà, cơi nới, đổ mái thêm tầng có cần xin phép xây dựng không?',
        'answer': '''TRƯỜNG HỢP PHẢI XIN PHÉP XÂY DỰNG TRƯỚC KHI SỬA:
- Xây thêm tầng (nâng tầng)
- Mở rộng diện tích sàn xây dựng
- Thay đổi kết cấu chịu lực (dầm, cột, sàn, móng)
- Cơi nới vượt ra ngoài chỉ giới xây dựng cho phép
- Thay đổi kiến trúc mặt ngoài nhà mặt phố trong khu vực bảo vệ cảnh quan

KHÔNG CẦN XIN PHÉP (sửa chữa nhỏ):
- Sơn sửa, lát lại nền, thay cửa
- Sửa chữa mái (không thay đổi kết cấu)
- Lắp điều hòa, đường ống trong nhà
- Sửa chữa không ảnh hưởng kết cấu chịu lực, không thay đổi kiến trúc ngoài

LÀM MÀ KHÔNG XIN PHÉP (khi cần phép):
- Bị phạt: 50–200 triệu đồng (Nghị định 16/2022/NĐ-CP)
- Phải dỡ bỏ phần vi phạm
- Không được hợp thức hóa trong một số trường hợp

CÁCH XIN PHÉP SỬA CHỮA:
Hồ sơ tương tự xin phép xây dựng mới, nộp tại UBND cấp huyện.
Lưu ý: Một số phường tại TP Thanh Hóa yêu cầu thêm ý kiến của Ban quản lý khu phố.''',
    },
]

# =============================================================================
# 8. NGƯỜI CAO TUỔI, NGƯỜI KHUYẾT TẬT
# =============================================================================
NCT_NKT = [
    {
        'id': 'nkt-001', 'category': 'xa_hoi', 'procedure': 'tro_cap_nguoi_khuyet_tat', 'level': 'ward',
        'source': 'Luật Người khuyết tật 2010; Nghị định 20/2021/NĐ-CP',
        'question': 'Người khuyết tật được hưởng trợ cấp xã hội không? Mức bao nhiêu? Thủ tục ở đâu?',
        'answer': '''Người khuyết tật thuộc diện bảo trợ xã hội được hưởng trợ cấp hàng tháng.

ĐIỀU KIỆN HƯỞNG TRỢ CẤP:
- Người khuyết tật đặc biệt nặng (mức 1): Không tự phục vụ bản thân
- Người khuyết tật nặng (mức 2): Khó khăn trong sinh hoạt hàng ngày

(Mức độ khuyết tật do Hội đồng xác định mức độ khuyết tật cấp xã xác định)

MỨC TRỢ CẤP (từ 01/7/2021 theo NĐ 20/2021):
Mức chuẩn trợ giúp xã hội: 360.000 đồng/tháng (hệ số 1)

- NKT đặc biệt nặng không tự phục vụ, sống một mình: 1.080.000 đ/tháng (hệ số 3)
- NKT đặc biệt nặng: 720.000 đồng/tháng (hệ số 2)
- NKT nặng: 540.000 đồng/tháng (hệ số 1,5)
- Trẻ em dưới 6 tuổi bị khuyết tật: 540.000 đồng/tháng

NGOÀI TRỢ CẤP TIỀN MẶT:
- Cấp thẻ BHYT miễn phí
- Miễn/giảm học phí (nếu đang đi học)
- Ưu tiên tiếp cận giao thông công cộng

HỒ SƠ (nộp tại UBND xã/phường):
1. Đơn đề nghị trợ cấp xã hội (Mẫu số 01)
2. Biên bản họp Hội đồng xác định mức độ khuyết tật
3. Giấy xác nhận khuyết tật (UBND xã cấp sau khi họp hội đồng)
4. CCCD (bản sao)
5. Sổ hộ khẩu hoặc giấy xác nhận cư trú

Thời gian: 30 ngày. Phòng LĐTBXH huyện phê duyệt.''',
    },
    {
        'id': 'nkt-002', 'category': 'xa_hoi', 'procedure': 'che_do_nguoi_cao_tuoi', 'level': 'ward',
        'source': 'Luật Người cao tuổi 2009; Nghị định 20/2021/NĐ-CP',
        'question': 'Người già trên 80 tuổi có được nhận trợ cấp xã hội không? Điều kiện như thế nào?',
        'answer': '''Người cao tuổi (từ đủ 60 tuổi trở lên) được hưởng nhiều chính sách ưu đãi.

TRỢ CẤP XÃ HỘI HÀNG THÁNG (bắt buộc, ai đủ điều kiện đều được hưởng):
- Người từ đủ 80 tuổi KHÔNG có lương hưu/BHXH: 360.000 đồng/tháng (hệ số 1)
- Người từ đủ 80 tuổi thuộc hộ nghèo: 540.000 đồng/tháng
- Người từ đủ 60 tuổi thuộc hộ nghèo không có người nuôi dưỡng: 360.000 đồng/tháng

THỦ TỤC NHẬN TRỢ CẤP:
1. Nộp đơn tại UBND xã/phường
2. CCCD + Sổ hộ khẩu + Giấy xác nhận hộ nghèo (nếu có)
3. Phòng LĐTBXH huyện xét duyệt trong 30 ngày
4. Nhận tiền hàng tháng tại UBND xã/phường hoặc qua tài khoản

QUYỀN LỢI KHÁC CỦA NGƯỜI CAO TUỔI:
- Thẻ BHYT: Từ đủ 80 tuổi → cấp thẻ BHYT miễn phí (Nhà nước đóng)
- Khám sức khỏe định kỳ: Ít nhất 1 lần/năm (miễn phí tại trạm y tế xã)
- Ưu tiên khám chữa bệnh: Không xếp hàng (ưu tiên số thứ tự)
- Miễn phí vé xe buýt (theo quy định tỉnh/thành phố)
- Được tặng quà trong dịp lễ Tết (địa phương tổ chức)

Liên hệ: Phòng LĐTBXH UBND huyện nơi cư trú.''',
    },
    {
        'id': 'nkt-003', 'category': 'xa_hoi', 'procedure': 'ho_ngheo_can_ngheo', 'level': 'ward',
        'source': 'Nghị định 07/2021/NĐ-CP; Quyết định 05/2022/QĐ-TTg',
        'question': 'Tiêu chí hộ nghèo 2022-2025 là gì? Đăng ký hộ nghèo ở đâu để được hưởng chính sách?',
        'answer': '''CHUẨN HỘ NGHÈO GIAI ĐOẠN 2022–2025 (Quyết định 07/2021/QĐ-TTg):

TIÊU CHÍ THU NHẬP:
- Khu vực nông thôn: Thu nhập bình quân ≤ 1,5 triệu đồng/người/tháng
- Khu vực thành thị: Thu nhập bình quân ≤ 2,0 triệu đồng/người/tháng

TIÊU CHÍ THIẾU HỤT DỊCH VỤ XÃ HỘI CƠ BẢN (thiếu ≥ 3 chỉ số):
Việc làm, giáo dục, y tế, nhà ở, nước sạch, vệ sinh, thông tin.

HỘ CẬN NGHÈO: Thu nhập từ 1,5–2,0 triệu đ/người/tháng (nông thôn) hoặc 2,0–2,6 triệu (thành thị).

RÀ SOÁT HỘ NGHÈO HÀNG NĂM: Vào cuối năm (tháng 10–12), UBND xã tổ chức điều tra rà soát.
Hộ muốn được xét → Đăng ký với Ban điều tra của UBND xã.

CHÍNH SÁCH HỖ TRỢ HỘ NGHÈO:
- Thẻ BHYT miễn phí
- Miễn/giảm học phí con em
- Vay vốn ưu đãi NHCSXH: 50–200 triệu đồng, lãi suất 6,6%/năm
- Hỗ trợ nhà ở (Chương trình 167): Xây mới/sửa chữa nhà dột nát
- Điện, nước giá ưu đãi
- Miễn lệ phí hành chính

Liên hệ: Ban LĐTBXH xã/phường → Phòng LĐTBXH huyện.''',
    },
]

# =============================================================================
# 9. PHÒNG CHÁY CHỮA CHÁY
# =============================================================================
PCCC = [
    {
        'id': 'pc-001', 'category': 'pccc', 'procedure': 'pccc_nha_o', 'level': 'ward',
        'source': 'Luật Phòng cháy và Chữa cháy 2001 sửa đổi 2013; Nghị định 136/2020/NĐ-CP',
        'question': 'Nhà ở, quán kinh doanh cần trang bị PCCC gì? Bị kiểm tra thì cần giấy tờ gì?',
        'answer': '''PHÒNG CHÁY CHỮA CHÁY NHÀ Ở (nhà riêng lẻ ≤ 7 tầng):
Không thuộc diện thẩm duyệt PCCC, nhưng chủ nhà CÓ TRÁCH NHIỆM tự đảm bảo.

TRANG BỊ TỐI THIỂU CHO NHÀ Ở:
- Bình chữa cháy xách tay (CO2 hoặc bột ABC): 1 bình/tầng (tối thiểu)
- Bình xịt CO2 loại nhỏ trong bếp
- Đèn pin sạc điện hoặc đèn khẩn cấp
- Thang dây thoát hiểm (nhà 3 tầng trở lên)
- Không để hàng hóa cản lối thoát hiểm

KINH DOANH NHỎ (tạp hóa, salon, quán ăn):
- Bình chữa cháy: 1 bình/50m² sàn (tối thiểu 1 bình/cơ sở)
- Hướng dẫn sơ đồ thoát hiểm dán ở nơi dễ thấy
- Không tích trữ hàng hóa dễ cháy gần nguồn lửa

NHÀ CAO TẦNG (≥ 5 tầng) VÀ CƠ SỞ SẢN XUẤT:
- Phải thẩm duyệt PCCC trước khi xây dựng (Phòng Cảnh sát PCCC Công an tỉnh)
- Phải có hệ thống báo cháy, chữa cháy tự động, đèn exit, thang thoát hiểm

KHI BỊ KIỂM TRA PCCC:
- Xuất trình: Bình chữa cháy còn hạn sử dụng, sổ theo dõi bảo dưỡng thiết bị
- Vi phạm nhỏ: Nhắc nhở, hạn khắc phục. Vi phạm nghiêm trọng: Phạt 5–50 triệu đồng, tạm đình chỉ hoạt động.

Phòng Cảnh sát PCCC Công an tỉnh Thanh Hóa: 04 Trần Phú, TP Thanh Hóa. Hotline PCCC: 114.''',
    },
    {
        'id': 'pc-002', 'category': 'pccc', 'procedure': 'cap_phep_pccc', 'level': 'province',
        'source': 'Nghị định 136/2020/NĐ-CP; Thông tư 149/2020/TT-BCA',
        'question': 'Cơ sở kinh doanh, nhà xưởng cần giấy phép PCCC không? Xin ở đâu? Thủ tục thế nào?',
        'answer': '''Cơ sở thuộc Phụ lục V, Nghị định 136/2020 PHẢI có Giấy chứng nhận thẩm duyệt/nghiệm thu PCCC.

CÁC LOẠI CƠ SỞ BẮT BUỘC THẨM DUYỆT PCCC:
- Nhà cao từ 5 tầng trở lên có chức năng ở hoặc kinh doanh hỗn hợp
- Cơ sở sản xuất/kho tàng có khối lượng chất cháy ≥ 1.000kg hoặc diện tích ≥ 500m²
- Chợ, trung tâm thương mại, siêu thị
- Khách sạn, nhà nghỉ từ 5 tầng trở lên hoặc từ 50 phòng trở lên
- Bệnh viện, trường học, rạp chiếu phim, nhà hát, sân vận động
- Cây xăng, kho chứa xăng dầu, khí đốt

TRÌNH TỰ THẨM DUYỆT THIẾT KẾ PCCC:
1. Nộp hồ sơ thiết kế PCCC đến Phòng Cảnh sát PCCC (khi chuẩn bị xây dựng)
2. Được thẩm duyệt trong 15–30 ngày (tùy quy mô)
3. Xây dựng theo thiết kế được duyệt
4. Sau hoàn công: Nghiệm thu PCCC → Cấp Giấy CN PCCC
5. Định kỳ kiểm tra PCCC: 1 lần/năm

Nộp hồ sơ tại: Phòng Cảnh sát PCCC - Công an tỉnh Thanh Hóa.
Địa chỉ: 04 Trần Phú, phường Hàm Rồng, TP Thanh Hóa. ĐT: 069.2587.114.''',
    },
]

# =============================================================================
# 10. VIỄN THÔNG VÀ CÔNG NGHỆ SỐ
# =============================================================================
VIEN_THONG = [
    {
        'id': 'vt-001', 'category': 'vien_thong', 'procedure': 'dang_ky_sim', 'level': 'ward',
        'source': 'Nghị định 49/2017/NĐ-CP; Thông tư 04/2024/TT-BTTTT',
        'question': 'Đăng ký SIM điện thoại cần gì? Một người được đăng ký mấy SIM? SIM rác bị xử lý thế nào?',
        'answer': '''Từ 01/03/2024, tất cả SIM PHẢI đăng ký thông tin thuê bao chính chủ bằng CCCD/Căn cước.

ĐĂNG KÝ MUA SIM MỚI:
- Xuất trình CCCD/Căn cước công dân tại cửa hàng viễn thông
- Nhà mạng scan CCCD + chụp ảnh khuôn mặt đối chiếu
- Hoàn tất trong 5 phút

SỐ LƯỢNG SIM TỐI ĐA:
- 1 người được đăng ký tối đa 4 SIM/nhà mạng
- Đã có 4 SIM của mạng A → không thể mua thêm SIM mạng A đứng tên mình

NẾU ĐANG CÓ SIM CHƯA ĐĂNG KÝ ĐÚNG CHÍNH CHỦ:
- Đến cửa hàng nhà mạng mang CCCD để chuẩn hóa thông tin
- Hạn chót đã qua (31/12/2023) → SIM chưa chuẩn hóa bị khóa một chiều (chỉ nhận cuộc gọi, không gọi đi được)
- Tiếp tục không chuẩn hóa → SIM bị cắt dịch vụ hoàn toàn

SIM RÁC (đăng ký nhiều SIM để lừa đảo):
- Phạt người sở hữu >4 SIM/nhà mạng: 40–60 triệu đồng
- Phạt nhà mạng bán SIM không đúng quy định: 80–100 triệu đồng/lần

Đường dây hỗ trợ viễn thông Thanh Hóa:
- Viettel: 18008098 | Vinaphone: 18001091 | Mobifone: 18001090''',
    },
    {
        'id': 'vt-002', 'category': 'vien_thong', 'procedure': 'vneid_dinh_danh_so', 'level': 'province',
        'source': 'Quyết định 06/QĐ-TTg; Nghị định 59/2022/NĐ-CP',
        'question': 'App VNeID là gì? Cài đặt như thế nào? Dùng thay CCCD vật lý được không?',
        'answer': '''VNeID là ứng dụng định danh điện tử của Bộ Công an Việt Nam, thay thế việc mang CCCD vật lý.

TẢI VÀ CÀI ĐẶT:
- Android: Google Play → Tìm "VNeID" → Cài đặt
- iOS: App Store → Tìm "VNeID" → Cài đặt
- Nhà phát triển: Trung tâm Dữ liệu quốc gia về dân cư (C06 - Bộ Công an)

ĐĂNG KÝ TÀI KHOẢN VNeID:
Mức 1 (tự đăng ký qua app):
1. Mở app → Chọn "Đăng ký tài khoản"
2. Nhập số CCCD + ngày sinh + số điện thoại đăng ký SIM chính chủ
3. Xác thực OTP → Tạo mã PIN 6 số
→ Dùng được: Tra cứu thông tin cá nhân, nộp hồ sơ DVC trực tuyến

Mức 2 (đến Công an xã để xác thực khuôn mặt):
→ Dùng thay CCCD vật lý khi: Xuất trình cho cảnh sát giao thông, check-in khách sạn, đi máy bay nội địa, làm thủ tục hành chính

TÍNH NĂNG CHÍNH:
- Hiển thị CCCD điện tử (thay thẻ vật lý khi xuất trình)
- Đăng nhập Cổng DVC Quốc gia bằng VNeID
- Theo dõi lịch sử giao dịch hành chính
- Thông báo khi có người tra cứu thông tin của mình

Hỗ trợ kích hoạt VNeID: Công an xã/phường. ĐT hỗ trợ: 1900.0368.''',
    },
    {
        'id': 'vt-003', 'category': 'vien_thong', 'procedure': 'chu_ky_so', 'level': 'province',
        'source': 'Luật Giao dịch điện tử 2023; Nghị định 130/2018/NĐ-CP',
        'question': 'Chữ ký số là gì? Cần chữ ký số để làm gì? Đăng ký ở đâu tại Thanh Hóa?',
        'answer': '''Chữ ký số (digital signature) là chữ ký điện tử được tạo bằng khóa bí mật, dùng để ký văn bản điện tử có giá trị pháp lý.

DÙNG CHỮ KÝ SỐ KHI NÀO:
- Ký hợp đồng điện tử (thương mại, lao động, dịch vụ)
- Kê khai thuế điện tử (bắt buộc với doanh nghiệp)
- Nộp hồ sơ BHXH điện tử
- Ký công văn, văn bản hành chính điện tử (cơ quan Nhà nước)
- Ký hóa đơn điện tử
- Giao dịch ngân hàng điện tử

2 LOẠI CHỮ KÝ SỐ:
1. USB Token (thiết bị vật lý cắm USB): Phổ biến nhất, an toàn cao
2. Chữ ký số trên điện thoại (SIM PKI hoặc App): Tiện lợi hơn

ĐĂNG KÝ CHỮ KÝ SỐ TẠI THANH HÓA:
Các đơn vị cung cấp được Bộ TTTT cấp phép:
- VIETTEL-CA: 0237.3761.000 (Viettel Thanh Hóa)
- VNPT-CA: 1800.1260 (Vinaphone Thanh Hóa)
- BKAV-CA: 024.3771.0066
- FPT-CA: 1800.6600

Phí: 800.000–2.000.000 đồng/2 năm (tùy loại và nhà cung cấp).
Thời gian cấp: 1–3 ngày làm việc.

CHỮ KÝ SỐ CÁ NHÂN (không cần doanh nghiệp): Cũng có thể đăng ký, dùng để ký hợp đồng cá nhân.''',
    },
]


def create_batch3_files():
    import os
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_ngan_hang.xlsx':     NGAN_HANG,
        'faq_ho_tich_2.xlsx':     HO_TICH_2,
        'faq_dat_dai_2.xlsx':     DAT_DAI_2,
        'faq_lao_dong_2.xlsx':    LAO_DONG_2,
        'faq_thue_2.xlsx':        THUE_2,
        'faq_giao_thong_2.xlsx':  GIAO_THONG_2,
        'faq_xay_dung_2.xlsx':    XAY_DUNG_2,
        'faq_xa_hoi.xlsx':        NCT_NKT,
        'faq_pccc.xlsx':          PCCC,
        'faq_vien_thong.xlsx':    VIEN_THONG,
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

    print(f'\nTong {total} ban ghi moi, {len(datasets)} file Excel tai: {OUT_DIR}')


if __name__ == '__main__':
    create_batch3_files()
