"""
Batch 4 — thêm ~42 bản ghi, đưa tổng ChromaDB lên ~150.
Chạy: python Backend/RAG/data/create_excel_batch4.py
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

# =============================================================================
# 1. Y TẾ BỔ SUNG
# =============================================================================
Y_TE_2 = [
    {
        'id': 'yt2-001', 'category': 'y_te', 'procedure': 'tiem_chung', 'level': 'ward',
        'source': 'Nghị định 104/2016/NĐ-CP; Thông tư 38/2017/TT-BYT',
        'question': 'Lịch tiêm chủng mở rộng miễn phí cho trẻ em gồm những vắc-xin gì? Tiêm ở đâu?',
        'answer': '''Chương trình Tiêm chủng mở rộng (TCMR) cung cấp vắc-xin MIỄN PHÍ cho trẻ em tại trạm y tế xã/phường.
Tại Thanh Hóa: Trạm y tế 635 xã/phường/thị trấn đều thực hiện TCMR.

LỊCH TIÊM VẮC-XIN MIỄN PHÍ:
- Sơ sinh: BCG (lao), Viêm gan B mũi 1
- 2 tháng: DPT-VGB-Hib (bạch hầu-ho gà-uốn ván-viêm gan B-Hib) + OPV (bại liệt uống)
- 3 tháng: DPT-VGB-Hib mũi 2 + OPV mũi 2
- 4 tháng: DPT-VGB-Hib mũi 3 + OPV mũi 3 + IPV (bại liệt tiêm)
- 9 tháng: Sởi mũi 1
- 18 tháng: DPT mũi 4 + Sởi-Rubella (MR)
- 12 tháng: Viêm não Nhật Bản B mũi 1
- 13 tháng: Viêm não Nhật Bản B mũi 2
- 24 tháng: Viêm não Nhật Bản B mũi 3

VẮC-XIN DỊCH VỤ (trả phí, tại phòng khám tư/bệnh viện):
- Rota (tiêu chảy cấp), Phế cầu (viêm phổi), Thủy đậu, Cúm, HPV (ung thư cổ tử cung cho nữ 9–14 tuổi), Viêm màng não mô cầu...

SÁCH TIÊM CHỦNG: Trạm y tế cấp sổ tiêm chủng cho trẻ từ khi sinh — giữ cẩn thận.
Đăng ký tiêm: Gọi trạm y tế xã hoặc đăng ký qua App Sổ Sức khỏe Điện tử.
Hotline TCMR Thanh Hóa: Trung tâm Kiểm soát bệnh tật tỉnh (CDC): 0237.3852.021.''',
    },
    {
        'id': 'yt2-002', 'category': 'y_te', 'procedure': 'cap_cuu_khan_cap', 'level': 'province',
        'source': 'Luật Khám chữa bệnh 2023',
        'question': 'Gọi cấp cứu 115 như thế nào? Bệnh viện nào có cấp cứu 24/7 tại Thanh Hóa?',
        'answer': '''CẤP CỨU 115 — Trung tâm Cấp cứu 115 Thanh Hóa:
Điện thoại: 115 (miễn phí, hoạt động 24/7)
Địa chỉ trạm: Bệnh viện Đa khoa tỉnh Thanh Hóa, 03 Hải Thượng Lãn Ông, TP Thanh Hóa.

KHI GỌI 115 CẦN NÓI RÕ:
1. Địa chỉ chính xác (số nhà, đường, phường/xã, huyện)
2. Tình trạng người bệnh (bất tỉnh, khó thở, tai nạn, ngộ độc...)
3. Số điện thoại liên lạc của bạn
4. Giữ đường dây, làm theo hướng dẫn của nhân viên điều phối

BỆNH VIỆN CẤP CỨU 24/7 TẠI THANH HÓA:
- BV Đa khoa tỉnh Thanh Hóa: 03 Hải Thượng Lãn Ông. ĐT: 0237.3852.021 (cấp cứu tuyến tỉnh)
- BV Đa khoa TP Thanh Hóa: 02 Hoàng Diệu. ĐT: 0237.3852.341
- BV Đa khoa khu vực Nghi Sơn: TX Nghi Sơn. ĐT: 0237.3693.299
- BV Đa khoa huyện Thọ Xuân, Hoằng Hóa, Hậu Lộc, Nông Cống... (cấp cứu cơ bản)

CẤP CỨU TIM MẠCH (STEMI): BV Đa khoa tỉnh có phòng thông tim can thiệp 24/7.
CẤP CỨU ĐỘT QUỴ: Kích hoạt báo động đột quỵ tại BV Đa khoa tỉnh — can thiệp trong 4,5 giờ.

SƠ CỨU TẠI CHỖ:
- Ngừng tim: CPR (ép tim 30 lần + thổi ngạt 2 lần, lặp lại đến khi xe cấp cứu đến)
- Đuối nước: Lật nghiêng, thông đường thở, CPR nếu cần
- Gãy xương: Bất động chi, KHÔNG nắn chỉnh, chờ cấp cứu''',
    },
    {
        'id': 'yt2-003', 'category': 'y_te', 'procedure': 'kham_benh_tu_xa', 'level': 'province',
        'source': 'Nghị định 111/2021/NĐ-CP; Thông tư 41/2023/TT-BYT',
        'question': 'Khám bệnh từ xa (telemedicine) tại Thanh Hóa có chưa? Sử dụng như thế nào?',
        'answer': '''Khám chữa bệnh từ xa (Telemedicine) đã được triển khai tại Thanh Hóa theo Đề án Khám chữa bệnh từ xa của Bộ Y tế.

CÁC NỀN TẢNG KHÁM BỆNH TỪ XA PHỔ BIẾN TẠI VIỆT NAM:
1. Telehealth (Bộ Y tế): https://telehealth.gov.vn — Kết nối bệnh viện tỉnh với tuyến huyện, xã
2. Medlink, Doctor Anywhere, JioHealth — App khám từ xa tư nhân
3. BV Đa khoa tỉnh Thanh Hóa kết nối với BV tuyến trung ương qua hệ thống Telehealth

KHÁM TỪ XA ĐƯỢC DÙNG KHI:
- Hội chẩn ca bệnh khó giữa BV huyện và BV tỉnh/trung ương
- Tư vấn sức khỏe ban đầu, không cần đến cơ sở y tế
- Theo dõi bệnh mãn tính sau khi điều trị (đái tháo đường, tim mạch, tăng huyết áp)

BHYT CÓ THANH TOÁN KHÁM TỪ XA KHÔNG?
- Khám từ xa hội chẩn giữa các cơ sở y tế: BHYT thanh toán
- Tư vấn trực tiếp qua app tư nhân: Chưa được BHYT thanh toán (người dùng tự trả)

APP SỨC KHỎE ĐIỆN TỬ QUỐC GIA:
- "Sổ Sức khỏe Điện tử" (do Bộ Y tế phát hành): Lưu lịch sử khám bệnh, kết quả xét nghiệm, lịch tiêm chủng
- Link: https://suckhoedientu.vn hoặc tải App trên CH Play/App Store''',
    },
    {
        'id': 'yt2-004', 'category': 'y_te', 'procedure': 'giay_chung_nhan_tat', 'level': 'province',
        'source': 'Luật Người khuyết tật 2010; Thông tư 01/2019/TT-BLĐTBXH',
        'question': 'Thủ tục xác định mức độ khuyết tật để được cấp giấy chứng nhận khuyết tật như thế nào?',
        'answer': '''Xác định mức độ khuyết tật và cấp Giấy xác nhận khuyết tật tại UBND xã/phường nơi cư trú.
Thời gian: 30 ngày. Lệ phí: Miễn phí.

QUY TRÌNH:
1. Người khuyết tật (hoặc người đại diện) nộp đơn đề nghị xác định mức độ khuyết tật tại UBND xã
2. UBND xã thành lập Hội đồng xác định mức độ khuyết tật (gồm: Chủ tịch UBND xã, cán bộ LĐTBXH, y tế xã, giáo dục xã và đại diện các tổ chức xã hội)
3. Hội đồng họp đánh giá trực tiếp (người khuyết tật phải có mặt, trừ trường hợp không đi lại được)
4. Lập biên bản kết luận mức độ khuyết tật
5. UBND xã cấp Giấy xác nhận khuyết tật

4 MỨC ĐỘ KHUYẾT TẬT:
- Khuyết tật đặc biệt nặng (mức 1): Không tự thực hiện sinh hoạt cá nhân hàng ngày
- Khuyết tật nặng (mức 2): Có khó khăn đặc biệt trong sinh hoạt, học tập, lao động
- Khuyết tật nhẹ (mức 3): Có khó khăn trong sinh hoạt, học tập, lao động
- (Không phải khuyết tật): Không đủ tiêu chí

HỒ SƠ:
1. Đơn đề nghị xác định mức độ khuyết tật (Mẫu số 01)
2. Hồ sơ y tế liên quan (nếu có): Giấy xuất viện, phim X-quang, kết quả chẩn đoán
3. CCCD

Sau khi có Giấy xác nhận: Nộp lên Phòng LĐTBXH huyện để xét trợ cấp xã hội.''',
    },
]

# =============================================================================
# 2. GIÁO DỤC BỔ SUNG
# =============================================================================
GIAO_DUC_2 = [
    {
        'id': 'gd2-001', 'category': 'giao_duc', 'procedure': 'hoc_nghe', 'level': 'province',
        'source': 'Luật Giáo dục nghề nghiệp 2014; Nghị định 15/2019/NĐ-CP',
        'question': 'Học nghề (trung cấp, cao đẳng nghề) tại Thanh Hóa ở đâu? Được hỗ trợ học phí không?',
        'answer': '''CÁC CƠ SỞ GIÁO DỤC NGHỀ NGHIỆP TẠI THANH HÓA:

CẤP CAO ĐẲNG:
- Trường CĐ Nghề Thanh Hóa: Đường Đinh Chương Dương, TP Thanh Hóa. ĐT: 0237.3752.689
- Trường CĐ Y tế Thanh Hóa: 177 Tống Duy Tân, TP Thanh Hóa
- Trường CĐ Nông Lâm Thanh Hóa: Đường Bà Triệu, TP Thanh Hóa
- Trường CĐ Văn hóa Nghệ thuật: Đường Tô Hiến Thành, TP Thanh Hóa

CẤP TRUNG CẤP & SƠ CẤP:
- 18 Trung tâm Giáo dục nghề nghiệp cấp huyện trên toàn tỉnh

CHÍNH SÁCH HỌC PHÍ:
- Học nghề trình độ sơ cấp: 4.000.000 đồng/khóa (kéo dài 3–6 tháng)
- Lao động nông thôn học nghề theo Đề án 1956: MIỄN HỌC PHÍ
- Hộ nghèo, người khuyết tật, người dân tộc thiểu số: Miễn học phí + hỗ trợ chi phí học tập

HỖ TRỢ CHI PHÍ HỌC NGHỀ (nếu thuộc đối tượng ưu tiên):
- Hỗ trợ tiền ăn: 30.000 đồng/ngày thực học
- Hỗ trợ tiền đi lại: 200.000 đồng/tháng (nếu xa trên 15km)
- Hỗ trợ chỗ ở: Miễn ký túc xá (nếu trường có)

Thủ tục: Đăng ký tại cơ sở GDNN → Nộp hồ sơ nhập học (CCCD + Bằng TN THCS/THPT + Ảnh) → Xét tuyển.
Sở LĐTBXH Thanh Hóa (phụ trách GDNN): 0237.3852.197.''',
    },
    {
        'id': 'gd2-002', 'category': 'giao_duc', 'procedure': 'bo_tuc_van_hoa', 'level': 'district',
        'source': 'Thông tư 22/2021/TT-BGDĐT',
        'question': 'Người lớn chưa tốt nghiệp THPT muốn học bổ túc, lấy bằng THPT thì làm thế nào?',
        'answer': '''Người chưa có bằng THPT có thể học chương trình Giáo dục thường xuyên (GDTX) cấp THPT và thi lấy bằng.

CÁC TRUNG TÂM GDTX TẠI THANH HÓA:
- Trung tâm GDTX tỉnh: 02 Lê Lợi, TP Thanh Hóa. ĐT: 0237.3752.258
- 27 Trung tâm GDTX cấp huyện (mỗi huyện 1 trung tâm)

ĐIỀU KIỆN NHẬP HỌC:
- Không giới hạn tuổi
- Đã tốt nghiệp THCS (hoặc tương đương)

CHƯƠNG TRÌNH HỌC:
- 3 năm (lớp 10, 11, 12) — có thể học ban ngày hoặc ban tối
- Học phí: 150.000–250.000 đồng/tháng (theo quy định tỉnh; hộ nghèo miễn phí)

THI TỐT NGHIỆP THPT (thi chung với học sinh trường thường):
- Thi cùng kỳ thi tốt nghiệp THPT quốc gia hàng năm (thường tháng 6–7)
- Đăng ký thi tại trường THPT mà Sở GD&ĐT phân công
- Bằng THPT GDTX có giá trị tương đương bằng THPT thông thường

ĐỐI VỚI NGƯỜI ĐÃ ĐI LÀM:
- Có thể học buổi tối (18:00–21:00) và cuối tuần tại Trung tâm GDTX huyện
- Không cần nghỉ việc

Sở GD&ĐT Thanh Hóa quản lý hệ thống GDTX: 0237.3852.487.''',
    },
    {
        'id': 'gd2-003', 'category': 'giao_duc', 'procedure': 'xet_tuyen_dai_hoc', 'level': 'province',
        'source': 'Thông tư 08/2022/TT-BGDĐT; Quy chế tuyển sinh 2024',
        'question': 'Xét tuyển đại học tại Việt Nam hiện nay có những phương thức nào? Đăng ký như thế nào?',
        'answer': '''Từ 2022, tuyển sinh đại học thực hiện qua Hệ thống tuyển sinh chung: https://thisinh.thitotnghiepthpt.edu.vn

CÁC PHƯƠNG THỨC XÉT TUYỂN PHỔ BIẾN 2024:

1. XÉT ĐIỂM THI TỐT NGHIỆP THPT (phổ biến nhất):
   - Đăng ký và nộp nguyện vọng sau khi có điểm thi (tháng 7)
   - Tối đa không giới hạn nguyện vọng, sắp xếp theo thứ tự ưu tiên

2. XÉT HỌC BẠ THPT:
   - Nhiều trường xét từ học kỳ 1 lớp 10 đến HK1 lớp 12
   - Đăng ký trực tiếp với trường (tháng 3–5 hàng năm)

3. XÉT ĐIỂM THI ĐÁNH GIÁ NĂNG LỰC:
   - ĐH Quốc gia HN (ĐGNL), ĐH Quốc gia TP.HCM, ĐH Bách khoa HN tổ chức thi riêng
   - Thi nhiều lần, lấy điểm cao nhất

4. TUYỂN THẲNG/ƯU TIÊN:
   - Thí sinh giỏi, học sinh giỏi quốc gia, quốc tế
   - Theo quy định của từng trường

LỊCH CHUNG 2024:
- Tháng 3–4: Đăng ký xét học bạ
- Tháng 6: Thi tốt nghiệp THPT
- Tháng 7: Công bố điểm thi, đăng ký nguyện vọng (trực tuyến)
- Tháng 8: Công bố kết quả trúng tuyển, xác nhận nhập học

Học sinh Thanh Hóa năm 2023 có tỷ lệ đỗ đại học công lập đạt khoảng 65% (trên mức trung bình cả nước).''',
    },
    {
        'id': 'gd2-004', 'category': 'giao_duc', 'procedure': 'tre_em_khuyet_tat_hoc', 'level': 'ward',
        'source': 'Luật Người khuyết tật 2010; Thông tư 03/2018/TT-BGDĐT',
        'question': 'Trẻ khuyết tật có được học hòa nhập ở trường thường không? Nhà trường có hỗ trợ gì?',
        'answer': '''Trẻ em khuyết tật có quyền học hòa nhập tại trường phổ thông gần nhà theo quy định Luật Người khuyết tật 2010.

QUYỀN CỦA TRẺ KHUYẾT TẬT TRONG GIÁO DỤC:
- Được nhận vào học tại bất kỳ trường phổ thông nào mà không được từ chối vì lý do khuyết tật
- Được miễn giảm học phí (khuyết tật nặng: miễn 100%)
- Được hỗ trợ phương tiện học tập đặc biệt (sách chữ Braille, máy tính có phần mềm đặc biệt...)
- Được có giáo viên hỗ trợ học hòa nhập (trường có học sinh khuyết tật đặc biệt nặng)
- Được xét tốt nghiệp theo hình thức đặc biệt nếu không thể tham gia kỳ thi thông thường

THỦ TỤC ĐĂNG KÝ HỌC HÒA NHẬP:
1. Phụ huynh liên hệ trực tiếp Ban giám hiệu trường muốn đăng ký
2. Nộp Giấy xác nhận khuyết tật (do UBND xã cấp)
3. Nhà trường lập kế hoạch giáo dục cá nhân (IEP) cho học sinh
4. Phối hợp với Trung tâm hỗ trợ phát triển GDHN người khuyết tật (nếu có)

TRƯỜNG CHUYÊN BIỆT TẠI THANH HÓA:
- Trường Phổ thông dành cho trẻ khuyết tật Thanh Hóa: 73 Ngô Thì Nhậm, TP Thanh Hóa. ĐT: 0237.3752.168
- Trung tâm Hỗ trợ phát triển GDHN NKT tỉnh: 03 Phạm Bành, TP Thanh Hóa

Sở GD&ĐT hỗ trợ giáo dục hòa nhập: 0237.3852.487.''',
    },
]

# =============================================================================
# 3. NÔNG NGHIỆP BỔ SUNG
# =============================================================================
NONG_NGHIEP_2 = [
    {
        'id': 'nn2-001', 'category': 'nong_nghiep', 'procedure': 'thu_y', 'level': 'district',
        'source': 'Luật Thú y 2015; Nghị định 35/2016/NĐ-CP',
        'question': 'Chăn nuôi gia súc, gia cầm thì tiêm phòng dịch bệnh gì? Có miễn phí không?',
        'answer': '''Tiêm phòng bắt buộc cho gia súc, gia cầm theo lịch của Cục Thú y và Sở NN&PTNT Thanh Hóa.

TIÊM PHÒNG BẮT BUỘC (MIỄN PHÍ VACCINE theo chương trình Nhà nước):
- LỢN: Lở mồm long móng (LMLM), Dịch tả lợn cổ điển, Tụ huyết trùng
- TRÂU BÒ: Lở mồm long móng, Tụ huyết trùng, Viêm da nổi cục (nếu có nguy cơ)
- GÀ VỊT: Cúm gia cầm H5N1 (vùng nguy cơ cao), Newcastle, Dịch tả vịt

LỊCH TIÊM PHÒNG:
- Vụ Xuân-Hè: Tháng 3–4
- Vụ Thu-Đông: Tháng 9–10
- Ngoài lịch: Khi có dịch bệnh xảy ra → tiêm khẩn cấp theo lệnh của UBND huyện

KHI PHÁT HIỆN GIA SÚC, GIA CẦM CÓ DẤU HIỆU BỆNH:
1. Báo ngay cho Trạm Thú y huyện hoặc UBND xã
2. Cách ly con vật bệnh, không bán/giết mổ/vận chuyển ra khỏi địa bàn
3. Trạm thú y đến lấy mẫu xét nghiệm và xử lý
4. Được hỗ trợ bồi thường nếu phải tiêu hủy (gia cầm 75% giá thị trường; lợn 80%)

Chi cục Chăn nuôi và Thú y Thanh Hóa: 20 Hải Thượng Lãn Ông, TP Thanh Hóa.
ĐT: 0237.3857.007. Đường dây nóng dịch bệnh: 0237.3751.619.''',
    },
    {
        'id': 'nn2-002', 'category': 'nong_nghiep', 'procedure': 'bao_ve_thuc_vat', 'level': 'district',
        'source': 'Luật Bảo vệ và Kiểm dịch thực vật 2013; Thông tư 21/2015/TT-BNNPTNT',
        'question': 'Mua thuốc bảo vệ thực vật cần điều kiện gì? Sử dụng đúng cách để không bị phạt?',
        'answer': '''Thuốc bảo vệ thực vật (BVTV) được kiểm soát chặt để bảo vệ môi trường và sức khỏe.

MUA THUỐC BVTV:
- Chỉ mua tại cửa hàng có Chứng chỉ hành nghề buôn bán thuốc BVTV
- Thuốc phải có trong Danh mục thuốc BVTV được phép sử dụng tại Việt Nam (kiểm tra tại: cục BVTV.gov.vn)
- KHÔNG mua thuốc không nhãn mác, thuốc nhập lậu

SỬ DỤNG ĐÚNG NGUYÊN TẮC "4 ĐÚNG":
1. Đúng thuốc: Chọn thuốc phù hợp với từng loại sâu bệnh, cây trồng
2. Đúng liều lượng: Pha theo hướng dẫn trên nhãn, không tùy tiện tăng nồng độ
3. Đúng lúc: Phun khi sâu bệnh ở tuổi nhỏ, thời tiết thuận lợi (không mưa, không gió mạnh)
4. Đúng cách: Mặc bảo hộ lao động (khẩu trang, kính, găng tay, áo dài)

THỜI GIAN CÁCH LY TRƯỚC THU HOẠCH:
- Ghi rõ trên nhãn thuốc — TUÂN THỦ TUYỆT ĐỐI
- Ví dụ: Rau ăn lá thường 3–7 ngày; quả 7–14 ngày; lúa 14–21 ngày

VI PHẠM SỬ DỤNG THUỐC BVTV:
- Sử dụng thuốc cấm, thuốc ngoài danh mục: Phạt 5–20 triệu đồng + tịch thu thuốc
- Không đảm bảo thời gian cách ly: Phạt 500.000–2.000.000 đồng

Chi cục Trồng trọt và BVTV Thanh Hóa: 20 Hải Thượng Lãn Ông, TP Thanh Hóa. ĐT: 0237.3851.379.''',
    },
    {
        'id': 'nn2-003', 'category': 'nong_nghiep', 'procedure': 'bao_hiem_nong_nghiep', 'level': 'district',
        'source': 'Nghị định 58/2018/NĐ-CP; Thông tư 57/2018/TT-BTC',
        'question': 'Bảo hiểm nông nghiệp (cây lúa, vật nuôi) tại Thanh Hóa có không? Mua ở đâu?',
        'answer': '''Bảo hiểm nông nghiệp giúp bù đắp thiệt hại khi thiên tai, dịch bệnh xảy ra với cây trồng/vật nuôi.

CÁC SẢN PHẨM BẢO HIỂM NÔNG NGHIỆP TẠI THANH HÓA:
1. BẢO HIỂM CÂY LÚA:
   - Rủi ro được bảo hiểm: Bão, lũ, hạn hán, rét đậm, dịch bệnh (đạo ôn, bạc lá...)
   - Mức phí: 1–2,5% giá trị bảo hiểm/vụ
   - Hỗ trợ phí BH từ Nhà nước: Hộ nghèo được hỗ trợ 90%; hộ cận nghèo 80%; hộ khác 60%

2. BẢO HIỂM VẬT NUÔI (trâu, bò, lợn, gia cầm):
   - Bảo hiểm dịch bệnh và tai nạn
   - Phí: 1,5–5%/năm (tùy loại vật nuôi và rủi ro)

3. BẢO HIỂM CÂY TRỒNG KHÁC (cây ăn quả, cao su, cà phê):
   - Đang triển khai thí điểm tại Thanh Hóa

MUA BẢO HIỂM NÔNG NGHIỆP:
- Qua Công ty Bảo hiểm Agribank (ABIC): 0237.3857.123
- Bảo Việt Thanh Hóa: 0237.3760.886
- Bảo Minh Thanh Hóa: 0237.3754.567
- Đăng ký qua UBND xã (chương trình hỗ trợ hộ nghèo)

KHI XẢY RA THIỆT HẠI: Báo ngay cho công ty bảo hiểm trong 72 giờ + UBND xã để lập biên bản.''',
    },
]

# =============================================================================
# 4. MÔI TRƯỜNG BỔ SUNG
# =============================================================================
MOI_TRUONG_2 = [
    {
        'id': 'mt2-001', 'category': 'moi_truong', 'procedure': 'nuoc_sach_nong_thon', 'level': 'district',
        'source': 'Chương trình MTQG nước sạch vệ sinh môi trường nông thôn',
        'question': 'Người dân nông thôn Thanh Hóa tiếp cận nước sạch như thế nào? Được hỗ trợ không?',
        'answer': '''Chương trình Nước sạch và Vệ sinh môi trường nông thôn do Bộ NN&PTNT và địa phương triển khai.

HIỆN TRẠNG TẠI THANH HÓA (2024):
- Tỷ lệ dân số nông thôn được dùng nước sạch đạt chuẩn: ~88%
- Còn khoảng 12% (chủ yếu vùng núi cao, vùng sâu) chưa có nước sạch

CÁC NGUỒN NƯỚC SẠCH NÔNG THÔN:
1. Công trình cấp nước tập trung: Nhà máy nước xã, bể chứa nước tập trung
2. Giếng khoan hợp vệ sinh: Hộ gia đình tự làm theo hướng dẫn kỹ thuật
3. Nước mưa trữ bể (vùng khan hiếm nước)

HỖ TRỢ XÂY DỰNG CÔNG TRÌNH NƯỚC SẠCH:
- Hộ nghèo, cận nghèo vùng đặc biệt khó khăn: Hỗ trợ 100% chi phí xây giếng hoặc lắp đường ống
- Hộ gia đình khác: Vay vốn ưu đãi NHCSXH, lãi suất 6,6%/năm
- Hộ muốn đấu nối vào mạng cấp nước xã: Đóng phí đấu nối (100.000–500.000 đồng)

TIỀN NƯỚC HÀNG THÁNG:
- Giá nước nông thôn: 4.000–7.000 đồng/m³ (tùy địa phương)
- Hộ nghèo: Giảm 50% giá nước

Phản ánh thiếu nước: UBND xã → Phòng NN&PTNT huyện → Sở NN&PTNT Thanh Hóa: 0237.3852.491.''',
    },
    {
        'id': 'mt2-002', 'category': 'moi_truong', 'procedure': 'bien_doi_khi_hau', 'level': 'province',
        'source': 'Luật Bảo vệ môi trường 2020; Kế hoạch UBND tỉnh Thanh Hóa về BĐKH',
        'question': 'Thanh Hóa có bị ảnh hưởng bởi biến đổi khí hậu không? Các biện pháp ứng phó là gì?',
        'answer': '''Thanh Hóa là tỉnh dễ bị tổn thương bởi biến đổi khí hậu (BĐKH) do có 102km bờ biển và địa hình đa dạng.

TÁC ĐỘNG BĐKH TẠI THANH HÓA:
- Bão lũ: Tần suất và cường độ tăng (trung bình 2–3 cơn bão/năm ảnh hưởng trực tiếp)
- Hạn hán: Khu vực Nghi Sơn, phía Nam và miền núi thường xuyên hạn
- Nước biển dâng: Dự báo dâng 30–50cm vào 2050 → ảnh hưởng vùng ven biển Sầm Sơn, Nghi Sơn, Hậu Lộc
- Xâm nhập mặn: Sông Mã, sông Yên bị xâm mặn sâu hơn vào mùa khô
- Sạt lở đất: Vùng núi Quan Hóa, Mường Lát thường xuyên sạt lở sau mưa lớn

BIỆN PHÁP ỨNG PHÓ CỦA TỈNH:
- Kè bờ biển: Đầu tư kè chống sạt lở bờ biển Sầm Sơn, Hậu Lộc
- Trồng rừng phòng hộ ven biển: Rừng ngập mặn Nga Sơn, Hậu Lộc
- Hệ thống thoát lũ: Cải tạo kênh tiêu thoát lũ sông Mã, sông Chu
- Năng lượng tái tạo: Điện mặt trời, điện gió tại Nghi Sơn

NGƯỜI DÂN CÓ THỂ LÀM GÌ:
- Trồng cây, bảo vệ rừng
- Phân loại rác, giảm rác thải nhựa
- Sử dụng năng lượng tiết kiệm (điện, xăng dầu)
- Tham gia chương trình trồng 1 tỷ cây xanh của tỉnh

Báo cáo sự cố môi trường: Sở TNMT: 0237.3752.262 hoặc 1800.1166 (miễn phí).''',
    },
]

# =============================================================================
# 5. VĂN HÓA, THỂ THAO, DU LỊCH
# =============================================================================
VAN_HOA = [
    {
        'id': 'vh-001', 'category': 'van_hoa', 'procedure': 'to_chuc_su_kien', 'level': 'district',
        'source': 'Nghị định 54/2019/NĐ-CP; Nghị định 38/2021/NĐ-CP',
        'question': 'Tổ chức sự kiện, lễ hội, biểu diễn nghệ thuật cần xin phép ở đâu? Hồ sơ gồm gì?',
        'answer': '''Tổ chức biểu diễn nghệ thuật, thi người đẹp, lễ hội... cần xin phép cơ quan văn hóa.

PHÂN CẤP THẨM QUYỀN CẤP PHÉP:
- Sở Văn hóa, Thể thao và Du lịch Thanh Hóa: Cấp phép sự kiện quy mô toàn tỉnh, sự kiện quốc tế
- Phòng Văn hóa và Thông tin UBND huyện: Sự kiện quy mô cấp huyện
- UBND xã/phường: Lễ hội dân gian cấp xã, hoạt động văn hóa cộng đồng nhỏ

HỒ SƠ CẤP PHÉP BIỂU DIỄN NGHỆ THUẬT:
1. Đơn đề nghị cấp phép biểu diễn
2. Chương trình, nội dung chi tiết tiết mục
3. Danh sách nghệ sĩ tham gia + giấy tờ pháp lý (CCCD, Thẻ hội viên Hội Nghệ sĩ...)
4. Giấy tờ pháp nhân của đơn vị tổ chức (Giấy phép hoạt động biểu diễn nghệ thuật)
5. Phương án đảm bảo an ninh trật tự và PCCC

THỜI GIAN CẤP PHÉP: 7 ngày làm việc (10 ngày với sự kiện quốc tế).
LỆ PHÍ: 500.000–2.000.000 đồng (tùy quy mô).

LƯU Ý ĐẶC BIỆT:
- Ca sĩ nước ngoài biểu diễn: Do Cục Nghệ thuật biểu diễn - Bộ VHTTDL cấp phép
- Lễ hội có nghi thức tôn giáo: Cần xin phép thêm Ban Tôn giáo tỉnh
Sở VHTTDL Thanh Hóa: 14 Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.535.''',
    },
    {
        'id': 'vh-002', 'category': 'du_lich', 'procedure': 'huong_dan_vien_du_lich', 'level': 'province',
        'source': 'Luật Du lịch 2017; Thông tư 06/2017/TT-BVHTTDL',
        'question': 'Nghề hướng dẫn viên du lịch cần bằng cấp gì? Xin thẻ hướng dẫn viên ở đâu?',
        'answer': '''Hướng dẫn viên du lịch phải có Thẻ hướng dẫn viên do Sở Du lịch/Sở VHTTDL cấp.

3 LOẠI THẺ HƯỚNG DẪN VIÊN:
1. Thẻ HDV nội địa: Dẫn khách trong nước đi tour nội địa
2. Thẻ HDV quốc tế: Dẫn khách nước ngoài hoặc khách Việt đi tour nước ngoài
3. Thẻ HDV tại điểm: Chỉ được giới thiệu tại một địa điểm cụ thể (bảo tàng, di tích...)

ĐIỀU KIỆN CẤP THẺ HDV NỘI ĐỊA:
- Tốt nghiệp trung cấp du lịch trở lên HOẶC tốt nghiệp trung cấp khác + chứng chỉ bồi dưỡng nghiệp vụ HDV nội địa (80 giờ)
- Biết ít nhất 1 ngoại ngữ (với HDV quốc tế: thành thạo ngoại ngữ + Chứng chỉ ngoại ngữ B2 trở lên)
- Không có tiền án tiền sự

HỒ SƠ XIN CẤP THẺ:
1. Đơn đề nghị (Mẫu 17, Thông tư 06/2017)
2. Bản sao bằng tốt nghiệp + chứng chỉ nghiệp vụ
3. CCCD + Phiếu LLTP
4. Giấy xác nhận sức khỏe
5. 2 ảnh 3×4 cm

Nộp tại: Sở VHTTDL Thanh Hóa, 14 Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.535.
Thời gian: 15 ngày làm việc. Lệ phí: 200.000 đồng. Thẻ có hiệu lực 5 năm.''',
    },
    {
        'id': 'vh-003', 'category': 'du_lich', 'procedure': 'diem_du_lich_thanh_hoa', 'level': 'province',
        'source': 'Sở VHTTDL Thanh Hóa; Cổng thông tin du lịch Thanh Hóa',
        'question': 'Các điểm du lịch nổi tiếng tại Thanh Hóa? Thủ tục tham quan di tích lịch sử ra sao?',
        'answer': '''THANH HÓA là tỉnh có tiềm năng du lịch phong phú với nhiều loại hình:

DU LỊCH BIỂN:
- Sầm Sơn (TX Sầm Sơn): Bãi biển dài 9km, sầm uất nhất miền Bắc mùa hè
- Biển Hải Tiến (Hoằng Hóa): Biển còn nguyên sơ, yên tĩnh
- Biển Hải Hòa (Nghi Sơn): Bãi biển đẹp gần Khu Kinh tế
- Vùng biển Nga Sơn: Kết hợp tham quan làng chiếu cói

DI TÍCH LỊCH SỬ & VĂN HÓA:
- Thành Nhà Hồ (Vĩnh Lộc): Di sản UNESCO, xây năm 1397. Phí tham quan: 40.000 đồng/người
- Lam Kinh (Thọ Xuân): Lăng tẩm triều Hậu Lê, Lễ hội Lam Kinh (ngày 21–22/8 âm lịch). Phí: 40.000 đ
- Đền Bà Triệu (Hậu Lộc): Thờ Bà Triệu Thị Trinh. Miễn phí tham quan
- Đền thờ Lê Hoàn (Thọ Xuân): Thờ vua Lê Đại Hành
- Hang Con Moong (Thạch Thành): Di chỉ khảo cổ người tiền sử

DU LỊCH SINH THÁI:
- Vườn Quốc gia Bến En (Như Thanh): Hồ Bến En, rừng nhiệt đới nguyên sinh
- Khu bảo tồn Pù Luông (Bá Thước): Ruộng bậc thang, bản làng dân tộc Thái
- Thác Mây, Thác 7 tầng (Quan Hóa)

Trung tâm Xúc tiến Du lịch Thanh Hóa: 14 Lê Lợi, TP Thanh Hóa. ĐT: 0237.3710.888.
Website: dulichthanhoa.com.vn.''',
    },
]

# =============================================================================
# 6. TÔN GIÁO, TÍN NGƯỠNG
# =============================================================================
TON_GIAO = [
    {
        'id': 'tg-001', 'category': 'ton_giao', 'procedure': 'dang_ky_hoat_dong_ton_giao', 'level': 'province',
        'source': 'Luật Tín ngưỡng, Tôn giáo 2016; Nghị định 162/2017/NĐ-CP',
        'question': 'Tổ chức tôn giáo muốn hoạt động tại Thanh Hóa phải đăng ký ở đâu? Thủ tục thế nào?',
        'answer': '''Hoạt động tôn giáo tại Việt Nam được pháp luật bảo hộ, nhưng phải đăng ký và tuân theo quy định.

CÁC TÔN GIÁO ĐƯỢC NHÀ NƯỚC CÔNG NHẬN TẠI THANH HÓA:
Phật giáo, Công giáo, Tin Lành, Cao Đài, Hòa Hảo, Hồi giáo, Tôn giáo Baha'i.
Tại Thanh Hóa: Phật giáo và Công giáo là 2 tôn giáo lớn nhất.

ĐĂNG KÝ SINH HOẠT TÔN GIÁO TẬP TRUNG (nhóm tư gia):
- Nhóm sinh hoạt tôn giáo chưa có tổ chức: Đăng ký tại UBND cấp xã
- Thời gian: 20 ngày. Thời hạn đăng ký: 1 năm (gia hạn được)
- Hồ sơ: Văn bản đăng ký + Danh sách thành viên + CCCD người đại diện

ĐĂNG KÝ HOẠT ĐỘNG TÔN GIÁO HỌC NĂM (hội nghị, đại hội, lớp bồi dưỡng):
- Tổ chức tôn giáo đăng ký tại cơ quan quản lý Nhà nước về tôn giáo: Ban Tôn giáo tỉnh (thuộc Sở Nội vụ)
- Thời gian: 30 ngày trước khi tổ chức

XÂY DỰNG, CẢI TẠO CƠ SỞ TÔN GIÁO (chùa, nhà thờ):
- Đề nghị gửi Sở Nội vụ tỉnh + UBND tỉnh
- Phải có phép xây dựng của Sở Xây dựng

Ban Tôn giáo Thanh Hóa (thuộc Sở Nội vụ): 22 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.451.''',
    },
    {
        'id': 'tg-002', 'category': 'tin_nguong', 'procedure': 'le_hoi_truyen_thong', 'level': 'district',
        'source': 'Nghị định 110/2018/NĐ-CP về quản lý và tổ chức lễ hội',
        'question': 'Tổ chức lễ hội truyền thống, giỗ họ, lễ hội đình làng cần xin phép không? Thủ tục ra sao?',
        'answer': '''Lễ hội truyền thống được khuyến khích phục hồi và phát huy, nhưng cần đăng ký với cơ quan Nhà nước.

PHÂN LOẠI LỄ HỘI:
1. Lễ hội dân gian (lễ hội làng, lễ hội đình, giỗ họ): Do cộng đồng tổ chức
2. Lễ hội lịch sử - cách mạng: Do Nhà nước hoặc cơ quan Nhà nước chủ trì
3. Lễ hội văn hóa, du lịch, thể thao: Kết hợp giữa Nhà nước và doanh nghiệp

ĐĂNG KÝ TỔ CHỨC LỄ HỘI TRUYỀN THỐNG:
- Lễ hội cấp xã: Báo cáo UBND xã trước 10 ngày
- Lễ hội cấp huyện: Đề nghị UBND huyện phê duyệt trước 20 ngày
- Lễ hội cấp tỉnh/liên tỉnh: UBND tỉnh phê duyệt, Sở VHTTDL chủ trì

HỒ SƠ:
1. Đơn đề nghị (ghi rõ: tên lễ hội, địa điểm, thời gian, quy mô, nguồn kinh phí)
2. Kịch bản chương trình lễ hội
3. Phương án đảm bảo ANTT, PCCC, vệ sinh môi trường

NHỮNG ĐIỀU KHÔNG ĐƯỢC LÀM TRONG LỄ HỘI:
- Tổ chức cờ bạc dưới mọi hình thức
- Lợi dụng lễ hội để tuyên truyền mê tín dị đoan
- Thu tiền vé vào khu vực lễ hội (không được thu quá mức quy định)
- Đốt vàng mã quá mức gây lãng phí, ô nhiễm

Sở VHTTDL Thanh Hóa hướng dẫn thực hiện: 0237.3852.535.''',
    },
]

# =============================================================================
# 7. KHOA HỌC CÔNG NGHỆ, ĐỔI MỚI SÁNG TẠO
# =============================================================================
KHOA_HOC = [
    {
        'id': 'kh-001', 'category': 'khoa_hoc', 'procedure': 'dang_ky_sang_che', 'level': 'province',
        'source': 'Luật Sở hữu trí tuệ 2005 sửa đổi 2022; Nghị định 65/2023/NĐ-CP',
        'question': 'Đăng ký bằng sáng chế, nhãn hiệu hàng hóa ở đâu? Thủ tục và chi phí như thế nào?',
        'answer': '''Đăng ký sở hữu trí tuệ (bằng sáng chế, nhãn hiệu, kiểu dáng...) tại Cục Sở hữu trí tuệ - Bộ KHCN (Hà Nội) hoặc các Văn phòng đại diện.

ĐĂNG KÝ NHÃN HIỆU (thương hiệu):
Hồ sơ:
1. Tờ khai đăng ký nhãn hiệu (Mẫu 04-NH)
2. Mẫu nhãn hiệu (8 tờ, kích thước 80×80mm)
3. Danh mục hàng hóa/dịch vụ theo phân loại Nice (43 nhóm)
4. Giấy ủy quyền (nếu nộp qua tổ chức đại diện)
5. Lệ phí nộp đơn: 150.000 đồng/nhóm + 300.000 đồng/nhãn hiệu

Thời gian: 12–18 tháng (thẩm định hình thức 1 tháng + công bố 2 tháng + thẩm định nội dung 9–12 tháng).
Hiệu lực: 10 năm, gia hạn vô thời hạn (mỗi 10 năm).

ĐĂNG KÝ BẰNG SÁNG CHẾ (phát minh kỹ thuật):
- Yêu cầu: Tính mới, trình độ sáng tạo, có khả năng áp dụng công nghiệp
- Lệ phí: 150.000 đồng (nộp đơn) + phí thẩm định
- Thời gian: 3–5 năm
- Hiệu lực: 20 năm (không gia hạn)

TẠI THANH HÓA:
- Sở Khoa học và Công nghệ Thanh Hóa hỗ trợ tư vấn đăng ký SHTT: 33 Ngô Thì Nhậm, TP Thanh Hóa. ĐT: 0237.3852.474
- Có chương trình hỗ trợ 50% phí đăng ký nhãn hiệu cho DN nhỏ và vừa, HTX, hộ kinh doanh''',
    },
    {
        'id': 'kh-002', 'category': 'khoa_hoc', 'procedure': 'ho_tro_startup', 'level': 'province',
        'source': 'Quyết định 844/QĐ-TTg; Nghị quyết 02/NQ-TU Thanh Hóa',
        'question': 'Startup, khởi nghiệp tại Thanh Hóa được hỗ trợ gì? Nộp hồ sơ ở đâu?',
        'answer': '''Tỉnh Thanh Hóa có nhiều chính sách hỗ trợ khởi nghiệp đổi mới sáng tạo.

CÁC CHÍNH SÁCH HỖ TRỢ STARTUP TẠI THANH HÓA:

1. HỖ TRỢ TÀI CHÍNH:
   - Quỹ Hỗ trợ Khởi nghiệp tỉnh: Hỗ trợ 30–50% chi phí đăng ký thành lập DN, đăng ký SHTT
   - Quỹ Phát triển KHCN tỉnh: Cho vay lãi suất 0% để thực hiện dự án KHCN (tối đa 500 triệu đ)
   - Ngân hàng Chính sách: Cho vay ưu đãi cho hộ kinh doanh mới thành lập (tối đa 200 triệu đ, lãi 6,6%/năm)

2. HỖ TRỢ PHI TÀI CHÍNH:
   - Miễn phí tư vấn đăng ký kinh doanh tại Sở KH&ĐT
   - Hỗ trợ kết nối thị trường, giới thiệu sản phẩm tại các hội chợ, triển lãm
   - Đào tạo kỹ năng kinh doanh miễn phí (Trung tâm Hỗ trợ DN nhỏ và vừa)

3. HỖ TRỢ HẠ TẦNG:
   - Vườn ươm Doanh nghiệp Thanh Hóa (Sở KH&ĐT): Thuê văn phòng giá ưu đãi 6 tháng–2 năm
   - Không gian làm việc chung (coworking space) tại TP Thanh Hóa

ĐĂNG KÝ HỖ TRỢ:
- Sở Khoa học và Công nghệ: 33 Ngô Thì Nhậm. ĐT: 0237.3852.474. Email: sokhcn@thanhhoa.gov.vn
- Sở KH&ĐT (Trung tâm Hỗ trợ DNNVV): 24 Hải Thượng Lãn Ông. ĐT: 0237.3852.349''',
    },
]

# =============================================================================
# 8. AN NINH TRẬT TỰ
# =============================================================================
AN_NINH = [
    {
        'id': 'an-001', 'category': 'an_ninh', 'procedure': 'to_giac_toi_pham', 'level': 'province',
        'source': 'Bộ luật Tố tụng Hình sự 2015; Luật Tố cáo 2018',
        'question': 'Phát hiện hành vi phạm tội (trộm cắp, ma túy, lừa đảo) thì tố giác ở đâu? Thế nào là an toàn?',
        'answer': '''TỐ GIÁC TỘI PHẠM là quyền và nghĩa vụ của mọi công dân. Được pháp luật bảo vệ.

KÊNH TỐ GIÁC:

1. GỌI ĐIỆN KHẨN CẤP:
   - Công an: 113 (trực 24/7, toàn quốc)
   - Công an tỉnh Thanh Hóa: 069.2587.000
   - Đường dây nóng chống ma túy: 1800.1234 (miễn phí)
   - Đường dây nóng chống mua bán người: 1800.1567 (miễn phí)

2. ĐẾN TỐ GIÁC TRỰC TIẾP:
   - Công an xã/phường nơi gần nhất
   - Cơ quan điều tra Công an tỉnh Thanh Hóa: 04 Trần Phú, TP Thanh Hóa

3. TỐ GIÁC BẰNG VĂN BẢN/ONLINE:
   - App "VNeID" → Mục "Phản ánh vi phạm"
   - Cổng thông tin Công an Thanh Hóa: conganthanhhoa.gov.vn
   - Email: congan@thanhhoa.gov.vn

BẢO VỆ NGƯỜI TỐ GIÁC:
- Cơ quan điều tra có trách nhiệm giữ bí mật thông tin người tố giác
- Nếu bị đe dọa vì tố giác: Báo ngay Công an để được bảo vệ (Chương trình bảo vệ người tố cáo)

LƯU Ý: Tố giác sai sự thật có thể bị xử phạt hành chính hoặc truy cứu hình sự.
Ưu tiên: KHÔNG tự mình đối đầu với tội phạm — gọi cảnh sát và quan sát từ xa.''',
    },
    {
        'id': 'an-002', 'category': 'an_ninh', 'procedure': 'phong_chong_lua_dao', 'level': 'province',
        'source': 'Cục An toàn thông tin - Bộ TTTT; Công an tỉnh Thanh Hóa',
        'question': 'Các hình thức lừa đảo phổ biến nhất hiện nay là gì? Làm sao để không bị lừa?',
        'answer': '''CÁC HÌNH THỨC LỪA ĐẢO PHỔ BIẾN TẠI THANH HÓA (2024):

1. GIẢ MẠO CÔNG AN, VIỆN KIỂM SÁT:
   - Gọi điện thông báo "liên quan vụ án", yêu cầu chuyển tiền để "xác minh"
   - THỰC TẾ: Cơ quan điều tra KHÔNG bao giờ yêu cầu chuyển tiền qua điện thoại

2. LỪA ĐẢO ĐẦU TƯ TIỀN ẢO, CHỨNG KHOÁN:
   - Mời tham gia nhóm đầu tư lợi nhuận "khủng" (100–300%/tháng)
   - Ban đầu cho rút tiền, sau đó khóa tài khoản
   - DẤU HIỆU: Lợi nhuận quá cao, không có giấy phép, thúc ép đầu tư nhanh

3. LỪA ĐẢO TUYỂN DỤNG ONLINE:
   - Tuyển cộng tác viên làm việc tại nhà (like, share, đặt đơn hàng ảo)
   - Yêu cầu nộp tiền "đặt cọc" hoặc "mua hàng mẫu"

4. LỪA ĐẢO XUẤT KHẨU LAO ĐỘNG:
   - Đặt cọc tiền "phí môi giới" cao (30–50 triệu đồng), sau đó biến mất
   - KIỂM TRA: Công ty XKLĐ phải có giấy phép của Bộ LĐTBXH (tra cứu tại dolab.gov.vn)

5. CHIẾM ĐOẠT TÀI KHOẢN (sim swap, phishing):
   - Gửi link giả mạo ngân hàng, yêu cầu nhập mật khẩu OTP

NẾU BỊ LỪA: Giữ nguyên bằng chứng → Báo Công an ngay → Liên hệ ngân hàng phong tỏa tài khoản.
Đường dây tố cáo lừa đảo: 113 hoặc cổng thông tin Công an tỉnh.''',
    },
    {
        'id': 'an-003', 'category': 'an_ninh', 'procedure': 'bao_luc_gia_dinh', 'level': 'ward',
        'source': 'Luật Phòng, chống bạo lực gia đình 2022',
        'question': 'Bị bạo lực gia đình thì gọi ai? Có được bảo vệ an toàn không?',
        'answer': '''Bạo lực gia đình (BLGĐ) là hành vi vi phạm pháp luật, bị xử lý theo Luật BLGĐ 2022.

LIÊN HỆ KHI BỊ BLGĐ:

KHẨN CẤP:
- Gọi 113 (Cảnh sát) nếu nguy hiểm tính mạng
- Đến Trạm y tế xã/phường gần nhất cấp cứu và xin xác nhận thương tích (bằng chứng)

HỖ TRỢ:
- Đường dây nóng hỗ trợ BLGĐ quốc gia: 1800.5999 (miễn phí, 24/7)
- Trung tâm Tư vấn và Dịch vụ truyền thông - Hội LHPN tỉnh Thanh Hóa: 0237.3752.041
- UBND xã/phường: Có cán bộ hỗ trợ xử lý BLGĐ

CÁC BIỆN PHÁP BẢO VỆ:
1. Cấm tiếp xúc tạm thời (CTC): Người có hành vi BLGĐ bị cấm đến gần, liên lạc với nạn nhân
   - Do UBND xã quyết định (thời hạn ≤ 3 ngày) hoặc Tòa án quyết định (3–4 tháng)
2. Địa chỉ tin cậy cộng đồng: Hàng xóm đăng ký là địa chỉ tin cậy để nạn nhân chạy đến khi nguy hiểm
3. Cơ sở hỗ trợ nạn nhân BLGĐ: Nơi ở tạm thời an toàn

XỬ LÝ NGƯỜI CÓ HÀNH VI BLGĐ:
- Nhắc nhở, xử phạt hành chính: 5.000.000–30.000.000 đồng
- Nghiêm trọng: Truy cứu hình sự (tội cố ý gây thương tích, tội hành hạ người khác...)

Hội LHPN tỉnh Thanh Hóa: 01 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.033.''',
    },
]


def create_batch4_files():
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_y_te_2.xlsx':        Y_TE_2,
        'faq_giao_duc_2.xlsx':    GIAO_DUC_2,
        'faq_nong_nghiep_2.xlsx': NONG_NGHIEP_2,
        'faq_moi_truong_2.xlsx':  MOI_TRUONG_2,
        'faq_van_hoa.xlsx':       VAN_HOA,
        'faq_ton_giao.xlsx':      TON_GIAO,
        'faq_khoa_hoc.xlsx':      KHOA_HOC,
        'faq_an_ninh.xlsx':       AN_NINH,
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
    create_batch4_files()
