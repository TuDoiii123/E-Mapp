"""
Batch 6 — Câu hỏi hành chính công CHUNG TOÀN QUỐC (không riêng Thanh Hóa).
Mục tiêu: ~120 bản ghi bao phủ mọi lĩnh vực phổ biến.
Chạy: python Backend/RAG/data/create_excel_batch6_chung.py
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

# =============================================================================
# 1. HỘ TỊCH CHUNG QUỐC GIA
# =============================================================================
HO_TICH_CHUNG = [
    {
        'id': 'g-ht-001', 'category': 'ho_tich', 'procedure': 'khai_sinh', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP',
        'question': 'Trẻ sinh ra ở bệnh viện nhưng cha mẹ không có hộ khẩu tại tỉnh đó thì đăng ký khai sinh ở đâu?',
        'answer': '''Đăng ký khai sinh theo nguyên tắc: Tại UBND xã nơi cư trú (thường trú hoặc tạm trú) của cha HOẶC mẹ.

CÁC TRƯỜNG HỢP:
1. Cha mẹ có thường trú khác tỉnh với nơi sinh: Chọn UBND xã nơi một trong hai thường trú
2. Cha mẹ chỉ có đăng ký tạm trú: Đăng ký khai sinh tại nơi tạm trú hiện tại (được phép)
3. Không có thường trú lẫn tạm trú tại nơi sinh: Có thể đăng ký tại nơi sinh (UBND xã nơi bệnh viện)
4. Trường hợp đặc biệt (sinh trên tàu, máy bay): Đăng ký tại nơi đăng ký tàu/nơi đến đầu tiên

THỜI GIAN ĐỀ NGHỊ ĐĂNG KÝ: 60 ngày kể từ ngày sinh.
Quá 60 ngày: Vẫn được đăng ký nhưng phải giải thích lý do; nếu trễ hơn 6 tháng cần xác nhận của UBND xã.

HỒ SƠ:
1. Giấy chứng sinh (do bệnh viện cấp)
2. CCCD của cha hoặc mẹ
3. Giấy đăng ký kết hôn (nếu có)
4. Tờ khai đăng ký khai sinh (Mẫu 01)

Thông tin trong Giấy khai sinh rất quan trọng — kiểm tra kỹ trước khi ký nhận, vì cải chính sau mất thêm thủ tục.''',
    },
    {
        'id': 'g-ht-002', 'category': 'ho_tich', 'procedure': 'khai_sinh_nuoc_ngoai', 'level': 'province',
        'source': 'Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP',
        'question': 'Con sinh ra ở nước ngoài thì đăng ký khai sinh tại Việt Nam như thế nào?',
        'answer': '''Trẻ em là công dân Việt Nam sinh ra ở nước ngoài cần đăng ký khai sinh để có giấy tờ hộ tịch Việt Nam.

HAI BƯỚC:

BƯỚC 1 — ĐĂNG KÝ KHAI SINH Ở NƯỚC SỞ TẠI:
Tại cơ quan hộ tịch địa phương nước đó (thường là nơi bệnh viện đã báo sinh).
Nhận Giấy khai sinh nước ngoài → Hợp pháp hóa lãnh sự (apostille hoặc legalization) + dịch thuật công chứng.

BƯỚC 2 — GHI VÀO SỔ HỘ TỊCH VIỆT NAM:
Nộp tại Ủy ban nhân dân cấp xã nơi cha/mẹ có hộ khẩu thường trú tại Việt Nam.
HOẶC: Đăng ký tại Cơ quan đại diện ngoại giao VN ở nước ngoài (Đại sứ quán/Lãnh sự quán VN) — nhanh hơn.

HỒ SƠ:
1. Tờ khai đăng ký khai sinh (Mẫu 01)
2. Giấy khai sinh nước ngoài đã hợp pháp hóa lãnh sự và dịch thuật công chứng
3. CCCD/Hộ chiếu của cha và mẹ
4. Giấy đăng ký kết hôn (nếu có)

Sau khi được ghi vào sổ hộ tịch VN: Trẻ có đầy đủ quyền công dân Việt Nam, có thể làm CCCD và hộ chiếu VN.''',
    },
    {
        'id': 'g-ht-003', 'category': 'ho_tich', 'procedure': 'quyen_nuoi_con', 'level': 'district',
        'source': 'Luật Hôn nhân và Gia đình 2014; Bộ luật Dân sự 2015',
        'question': 'Sau ly hôn, con ở với ai? Người không nuôi con có quyền gì? Thay đổi quyền nuôi con như thế nào?',
        'answer': '''NGUYÊN TẮC XÉT AI NUÔI CON KHI LY HÔN:
- Con dưới 36 tháng tuổi: Mẹ nuôi (trừ mẹ không đủ điều kiện)
- Con từ 36 tháng đến dưới 7 tuổi: Tòa án quyết định dựa trên lợi ích tốt nhất của con
- Con từ 7 tuổi trở lên: Tòa hỏi ý kiến con, xem xét nguyện vọng

YẾU TỐ TÒA XEM XÉT:
- Điều kiện kinh tế, nơi ở ổn định
- Thời gian chăm sóc con thực tế
- Điều kiện giáo dục
- Tình trạng sức khỏe, đạo đức

QUYỀN CỦA NGƯỜI KHÔNG TRỰC TIẾP NUÔI CON:
- Thăm nom con theo thỏa thuận hoặc theo quyết định tòa (thường cuối tuần, dịp lễ)
- Người nuôi con KHÔNG được cản trở quyền thăm nom (vi phạm bị xử phạt)
- Không trả cấp dưỡng: Bị cưỡng chế thi hành án dân sự

THAY ĐỔI QUYỀN NUÔI CON (khi hoàn cảnh thay đổi):
- Nộp đơn yêu cầu thay đổi người trực tiếp nuôi con ra TAND nơi đang giải quyết
- Phải chứng minh: Người đang nuôi không đảm bảo điều kiện (bỏ bê con, bạo hành, nghiện ma túy...)
- Thủ tục giống vụ kiện dân sự thông thường (6–12 tháng)

Mức cấp dưỡng tối thiểu: Tòa tự quyết, thường 15–30% thu nhập người không nuôi con.''',
    },
    {
        'id': 'g-ht-004', 'category': 'ho_tich', 'procedure': 'tuyen_bo_mat_tich_chet', 'level': 'district',
        'source': 'Bộ luật Dân sự 2015; Bộ luật Tố tụng Dân sự 2015',
        'question': 'Người thân mất tích lâu năm, làm sao để được tuyên bố mất tích hoặc đã chết về mặt pháp lý?',
        'answer': '''TUYÊN BỐ MẤT TÍCH và TUYÊN BỐ ĐÃ CHẾT là 2 thủ tục tòa án khác nhau.

TUYÊN BỐ MẤT TÍCH:
Điều kiện: Biệt tích ≥ 2 năm liên tục, không có tin tức (sau khi đã thông báo tìm kiếm đầy đủ).
Hiệu quả pháp lý: Tài sản do người quản lý, nhưng hôn nhân chưa chấm dứt, con vẫn còn cha/mẹ.
Thủ tục: Nộp đơn yêu cầu tại TAND nơi cư trú trước đây của người mất tích.

TUYÊN BỐ ĐÃ CHẾT:
Điều kiện (một trong các trường hợp):
- Biệt tích ≥ 3 năm kể từ ngày tuyên bố mất tích
- Biệt tích ≥ 5 năm (không qua tuyên bố mất tích trước)
- Mất tích trong chiến tranh ≥ 5 năm sau khi kết thúc chiến tranh
- Biệt tích do tai nạn, thiên tai ≥ 2 năm (không còn tin tức)

Hiệu quả pháp lý: Quan hệ nhân thân chấm dứt (vợ/chồng được tái hôn); thừa kế tài sản mở; trẻ em được giám hộ.

Nếu sau đó người "đã chết" quay về: Tòa án hủy quyết định tuyên bố chết; tài sản được trả lại (những gì còn); hôn nhân không tự động khôi phục.

HỒ SƠ NỘP TÒA: Đơn yêu cầu + chứng cứ về việc biệt tích (báo mất tích, xác nhận của công an, hàng xóm, gia đình...) + CCCD người yêu cầu.''',
    },
    {
        'id': 'g-ht-005', 'category': 'ho_tich', 'procedure': 'ket_hon_hai_quoc_tich', 'level': 'province',
        'source': 'Luật Hôn nhân và Gia đình 2014; Nghị định 123/2015/NĐ-CP',
        'question': 'Người Việt kết hôn với người nước ngoài tại Việt Nam thủ tục như thế nào?',
        'answer': '''Kết hôn có yếu tố nước ngoài (một bên là người nước ngoài) thuộc thẩm quyền của SỞ TƯ PHÁP tỉnh nơi đăng ký.
Không thực hiện tại UBND xã như kết hôn giữa hai người Việt.

THỜI GIAN GIẢI QUYẾT: 25 ngày làm việc (phức tạp có thể 45 ngày). Lệ phí: 1.500.000 đồng.

HỒ SƠ PHÍA NGƯỜI VIỆT NAM:
1. Tờ khai đăng ký kết hôn (Mẫu TP/HT-2014-TKKH.2)
2. CCCD/Hộ chiếu còn hiệu lực
3. Giấy xác nhận tình trạng hôn nhân (do UBND xã nơi thường trú cấp, trong 6 tháng)

HỒ SƠ PHÍA NGƯỜI NƯỚC NGOÀI:
1. Hộ chiếu còn hiệu lực
2. Giấy xác nhận tình trạng hôn nhân do cơ quan có thẩm quyền nước ngoài cấp (hợp pháp hóa lãnh sự + dịch thuật công chứng)
3. Giấy xác nhận đủ điều kiện kết hôn theo pháp luật nước họ (một số nước)
4. Giấy phép lao động/thẻ tạm trú còn hiệu lực (nếu đang sinh sống tại VN)

Sau khi đăng ký tại VN: Bên người nước ngoài cần đăng ký thêm tại nước họ (nếu pháp luật nước đó yêu cầu).
Lưu ý: Hôn nhân phải tự nguyện, không vi phạm điều kiện kết hôn của cả hai nước.''',
    },
]

# =============================================================================
# 2. ĐẤT ĐAI CHUNG QUỐC GIA
# =============================================================================
DAT_DAI_CHUNG = [
    {
        'id': 'g-dd-001', 'category': 'dat_dai', 'procedure': 'don_gia_dat', 'level': 'province',
        'source': 'Luật Đất đai 2024; Nghị định 71/2024/NĐ-CP',
        'question': 'Bảng giá đất và giá đất cụ thể khác nhau thế nào? Khi nào dùng giá nào?',
        'answer': '''Luật Đất đai 2024 (hiệu lực 01/01/2025) thay đổi căn bản cách định giá đất:

BẢNG GIÁ ĐẤT:
- Do UBND tỉnh ban hành hàng năm (thay vì 5 năm như trước)
- Tiếp cận gần hơn với giá thị trường
- Dùng để: Tính lệ phí trước bạ, phí và lệ phí hành chính, tính tiền sử dụng đất khi cấp GCN lần đầu, khởi điểm đấu giá quyền sử dụng đất

GIÁ ĐẤT CỤ THỂ:
- Do UBND tỉnh quyết định cho từng thửa đất trong từng dự án, trường hợp cụ thể
- Theo nguyên tắc: GIÁ THỊ TRƯỜNG tại thời điểm định giá (khảo sát thực tế, so sánh giao dịch tương đồng)
- Dùng để: Thu tiền sử dụng đất khi giao đất, tính bồi thường khi thu hồi đất, xác định giá khởi điểm đấu giá theo yêu cầu

ĐIỂM MỚI LUẬT ĐẤT ĐAI 2024:
- Bỏ khung giá đất do Chính phủ ban hành (trao quyền cho địa phương)
- UBND tỉnh định giá đất hàng năm (không còn 5 năm/lần)
- Giá đất bồi thường khi thu hồi = giá thị trường (không thấp hơn bảng giá)
- Đất nông nghiệp tiếp giáp đô thị: Được định giá theo mục đích sử dụng thực tế hơn

Để biết bảng giá đất tại địa phương: Tra cứu tại cổng thông tin Sở TNMT tỉnh hoặc UBND huyện.''',
    },
    {
        'id': 'g-dd-002', 'category': 'dat_dai', 'procedure': 'dat_nong_nghiep_len_tho_cu', 'level': 'district',
        'source': 'Luật Đất đai 2024; Nghị định 102/2024/NĐ-CP',
        'question': 'Chuyển đổi đất nông nghiệp sang đất ở thủ tục thế nào? Có dễ không?',
        'answer': '''Chuyển mục đích sử dụng đất nông nghiệp sang đất ở (đất thổ cư) là thủ tục phức tạp và KHÔNG phải lúc nào cũng được chấp thuận.

ĐIỀU KIỆN CƠ BẢN:
1. Đất nằm trong quy hoạch được phép chuyển sang đất ở (kiểm tra quy hoạch sử dụng đất)
2. Không thuộc đất lúa, đất rừng phòng hộ (rất khó chuyển, cần Thủ tướng/Quốc hội chấp thuận)
3. Phù hợp với kế hoạch sử dụng đất hàng năm cấp huyện

QUY TRÌNH CHUYỂN MỤC ĐÍCH:
1. Nộp đơn tại Văn phòng ĐKDD/UBND huyện
2. Cơ quan chức năng thẩm định (Phòng TNMT + Phòng Quy hoạch)
3. UBND cấp có thẩm quyền ra quyết định cho phép (UBND huyện với đất dưới 0,5ha; tỉnh với trên 0,5ha)
4. Nộp tiền sử dụng đất (chênh lệch giữa giá đất nông nghiệp và giá đất ở)
5. Cấp lại GCN với mục đích mới

TIỀN SỬ DỤNG ĐẤT KHI CHUYỂN MỤC ĐÍCH:
= (Giá đất ở - Giá đất nông nghiệp) × Diện tích × Hệ số điều chỉnh
Thường rất lớn tại khu vực đô thị hóa.

THỰC TẾ: Nhiều địa phương TẠM DỪNG xét duyệt chuyển đất nông nghiệp sang đất ở để kiểm soát quy hoạch. Nên tra cứu thông tin tại Phòng TNMT huyện trước khi làm hồ sơ.''',
    },
    {
        'id': 'g-dd-003', 'category': 'dat_dai', 'procedure': 'doi_giaydung_sang_gcn', 'level': 'district',
        'source': 'Luật Đất đai 2024',
        'question': 'Nhà đất có giấy tờ cũ (giấy trắng, sổ đỏ cũ, bìa đỏ) thì có cần làm lại GCN không?',
        'answer': '''Các loại giấy tờ đất cũ vẫn còn HIỆU LỰC PHÁP LÝ và không bắt buộc phải đổi sang GCN mới.

CÁC LOẠI GIẤY TỜ CŨ CÒN GIÁ TRỊ:
- "Sổ đỏ" cũ (GCN theo Nghị định 43, 88): Vẫn có giá trị, giao dịch bình thường
- "Sổ hồng" cũ (GCN nhà ở): Vẫn có giá trị
- "Bìa đỏ" (GCN QSDĐ theo QĐ 201/HĐBT 1989): Vẫn có giá trị
- Giấy phép xây dựng kèm hóa đơn nộp tiền sử dụng đất: Có thể dùng để cấp GCN

CHỈ CẦN CHUYỂN SANG GCN MỚI KHI:
- Thực hiện giao dịch (mua bán, tặng cho, thế chấp): Cần GCN mới đứng tên bên mua/nhận
- GCN cũ không có đủ thông tin (ví dụ: thiếu diện tích nhà, tầng số...)
- Muốn tách thửa, hợp thửa
- GCN cũ bị hỏng, mất

THỦ TỤC ĐỔI/CẤP LẠI GCN:
- Nộp tại Văn phòng ĐKDD cấp huyện nơi có đất
- Hồ sơ: Đơn đề nghị + GCN cũ + CCCD + Giấy tờ liên quan
- Không mất tiền sử dụng đất (chỉ nộp phí, lệ phí)
- Thời gian: 30 ngày

Đất chưa có bất kỳ giấy tờ nào (đất không giấy): Cần làm thủ tục kê khai đăng ký → xem xét cấp GCN lần đầu (phức tạp hơn).''',
    },
    {
        'id': 'g-dd-004', 'category': 'dat_dai', 'procedure': 'dat_o_nuoc_ngoai_mua_tai_vn', 'level': 'province',
        'source': 'Luật Đất đai 2024; Luật Nhà ở 2023',
        'question': 'Người nước ngoài có được mua nhà, đất tại Việt Nam không? Điều kiện và hạn chế gì?',
        'answer': '''Người nước ngoài và Việt kiều được phép sở hữu nhà ở tại Việt Nam theo Luật Nhà ở 2023 (hiệu lực 01/01/2025).

NGƯỜI NƯỚC NGOÀI ĐƯỢC MUA NHÀ KHI:
- Được phép nhập cảnh hợp pháp vào Việt Nam (có visa hoặc miễn visa)
- Không thuộc khu vực quốc phòng, an ninh (danh sách Bộ Quốc phòng quy định)

HẠN CHẾ ĐỐI VỚI NGƯỜI NƯỚC NGOÀI:
- Chỉ được sở hữu nhà tại DỰ ÁN PHÁT TRIỂN NHÀ Ở THƯƠNG MẠI (không được mua đất riêng lẻ)
- KHÔNG được mua nhà trong khu vực cần bảo vệ quốc phòng/an ninh
- Số lượng: Tối đa 30% căn hộ trong một tòa chung cư; tối đa 250 căn trên một đơn vị hành chính cấp phường
- Thời hạn sở hữu: 50 năm (gia hạn được); người kết hôn với công dân VN: sở hữu lâu dài
- Không được cho thuê lại theo hình thức kinh doanh (chỉ cho thuê bình thường)

VIỆT KIỀU (người Việt Nam định cư nước ngoài):
- Được mua nhà ở thương mại giống công dân trong nước (không bị hạn chế số lượng)
- Được sở hữu lâu dài
- Cần xuất trình hộ chiếu + giấy tờ chứng minh gốc Việt Nam (hộ chiếu VN cũ, giấy khai sinh VN...)

Để kiểm tra dự án nào người nước ngoài được mua: Hỏi chủ đầu tư hoặc Sở Xây dựng địa phương.''',
    },
    {
        'id': 'g-dd-005', 'category': 'dat_dai', 'procedure': 'hop_dong_mua_ban_nha', 'level': 'district',
        'source': 'Luật Nhà ở 2023; Luật Kinh doanh BĐS 2023; Bộ luật Dân sự 2015',
        'question': 'Mua nhà đất viết tay (không qua công chứng) có hợp lệ không? Rủi ro gì?',
        'answer': '''Hợp đồng mua bán nhà đất PHẢI công chứng/chứng thực theo quy định — đây là điều kiện bắt buộc về hình thức.

QUY ĐỊNH PHÁP LUẬT:
- Điều 119 Luật Nhà ở 2023: HĐ mua bán, tặng cho, đổi, góp vốn bằng nhà ở PHẢI công chứng/chứng thực
- Điều 167 Luật Đất đai 2024: Hợp đồng chuyển nhượng QSDĐ PHẢI công chứng/chứng thực

HỢP ĐỒNG VIẾT TAY KHÔNG CÔNG CHỨNG:
- VỀ MẶT PHÁP LÝ: Vô hiệu vì vi phạm hình thức bắt buộc (Điều 129 BLDS 2015)
- TUY NHIÊN: Tòa án có thể công nhận nếu: giao dịch đã thực hiện xong (đã giao đất, đã trả đủ tiền) và một bên yêu cầu công nhận (trong vòng 2 năm từ khi phát hiện giao dịch vô hiệu về hình thức)
- Rất rủi ro nếu bên bán không hợp tác đi công chứng sau đó

CÁC RỦI RO KHI KHÔNG CÔNG CHỨNG:
1. Người bán bán lại cho người khác (tranh chấp quyền sở hữu)
2. Người bán chết trước khi công chứng → thừa kế tranh chấp
3. Đất bị kê biên/thế chấp ngân hàng trong khi chờ công chứng
4. Không làm được sổ đỏ đứng tên người mua
5. Khi có tranh chấp, không có bằng chứng rõ ràng về thỏa thuận

KHUYẾN NGHỊ: Luôn ký hợp đồng công chứng; không nên tin vào "giấy tay" dù quen biết.''',
    },
]

# =============================================================================
# 3. CCCD VÀ CƯ TRÚ CHUNG QUỐC GIA
# =============================================================================
CCCD_CHUNG = [
    {
        'id': 'g-cc-001', 'category': 'cccd', 'procedure': 'the_can_cuoc_chip', 'level': 'district',
        'source': 'Luật Căn cước 2023 (hiệu lực 01/7/2024)',
        'question': 'Thẻ Căn cước (mới) khác thẻ CCCD gắn chip cũ như thế nào? Có cần đổi ngay không?',
        'answer': '''Luật Căn cước 2023 (hiệu lực 01/7/2024) thay thế Luật CCCD 2014. Tên gọi đổi từ "CCCD" thành "Căn cước".

SỰ KHÁC BIỆT:

THẺ CĂN CƯỚC MỚI (từ 01/7/2024):
- Tên gọi: "Căn cước" (bỏ chữ "công dân")
- Thêm thông tin: Nơi đăng ký khai sinh, nơi thường trú/tạm trú (có thể không còn mục "Quê quán" riêng)
- Tích hợp nhiều thông tin hơn vào chip: Sinh trắc học (vân tay, mống mắt), thông tin y tế, BHYT, BHXH...
- Cấp cho: Mọi công dân VN từ đủ 6 tuổi trở lên (thay vì 14 tuổi)
- Trẻ 6–13 tuổi: Thẻ căn cước không có chip (chỉ có QR code), cấp miễn phí, không bắt buộc
- Từ 14 tuổi: Thẻ có chip đầy đủ

CÓ CẦN ĐỔI THẺ CCCD CŨ SANG THẺ CĂN CƯỚC MỚI NGAY KHÔNG?
KHÔNG BẮT BUỘC — Thẻ CCCD gắn chip đã cấp VẪN CÒN HIỆU LỰC đến hết hạn ghi trên thẻ.
Chỉ làm mới khi: Thẻ hết hạn, thẻ hỏng/mất, thông tin thay đổi, hoặc muốn tích hợp thêm thông tin mới.

MIỄN PHÍ ĐỔI: Giai đoạn đầu triển khai (2024), việc đổi từ CCCD chip sang Căn cước mới được miễn phí.''',
    },
    {
        'id': 'g-cc-002', 'category': 'cccd', 'procedure': 'xac_minh_thu_tuc', 'level': 'ward',
        'source': 'Nghị định 59/2022/NĐ-CP về định danh điện tử',
        'question': 'Làm thủ tục hành chính mà không mang CCCD vật lý, chỉ có điện thoại VNeID thì có được không?',
        'answer': '''TỪ NĂM 2022, thẻ căn cước điện tử trên app VNeID (mức 2) được chấp nhận thay thế CCCD vật lý tại nhiều nơi.

NƠI ĐƯỢC DÙNG VNEID THAY CCCD:
- Làm thủ tục hành chính tại UBND xã/phường/huyện (đã triển khai 100% từ 2023)
- Check-in máy bay nội địa (VietJet, Vietnam Airlines, Bamboo đã chấp nhận)
- Khách sạn, nhà nghỉ check-in
- Xuất trình cho cảnh sát giao thông khi bị kiểm tra
- Vào bệnh viện đăng ký khám (một số bệnh viện lớn)
- Giao dịch tại một số ngân hàng

CẦN LƯU Ý:
- Phải kích hoạt VNeID MỨC 2 (xác thực sinh trắc học tại Công an xã/phường) — Mức 1 chưa thay được CCCD vật lý
- Điện thoại cần pin, sóng, bộ nhớ — nên có CCCD vật lý dự phòng
- Một số nơi CHƯA CẬP NHẬT thiết bị đọc QR → vẫn yêu cầu thẻ vật lý (thực tế vẫn xảy ra)
- Giao dịch ngân hàng lần đầu, công chứng, xuất nhập cảnh: Vẫn cần CCCD vật lý

CÁCH KÍCH HOẠT VNEID MỨC 2:
Đến Công an phường/xã → Yêu cầu kích hoạt → Cán bộ scan CCCD + chụp ảnh khuôn mặt → Mức 2 kích hoạt ngay.''',
    },
    {
        'id': 'g-cc-003', 'category': 'cu_tru', 'procedure': 'so_ho_khau_dien_tu', 'level': 'ward',
        'source': 'Luật Cư trú 2020; Nghị định 62/2021/NĐ-CP',
        'question': 'Từ năm 2021 bỏ sổ hộ khẩu giấy, vậy khi cần chứng minh hộ khẩu thì dùng gì?',
        'answer': '''Từ 01/01/2023, Sổ hộ khẩu và Sổ tạm trú giấy CHÍNH THỨC KHÔNG CÒN GIÁ TRỊ SỬ DỤNG.
Thay vào đó là thông tin cư trú quản lý trên Cơ sở dữ liệu quốc gia về dân cư (CSDL QGDC).

CÁCH CHỨNG MINH THÔNG TIN CƯ TRÚ:

1. CCCD/Căn cước (có chip): Chip chứa thông tin nơi thường trú — các cơ quan đọc chip là biết
2. VNeID MỨC 2: Hiển thị đầy đủ thông tin cư trú
3. PHIẾU THÔNG TIN CƯ TRÚ: Công an phường/xã cấp khi có yêu cầu (ngay trong ngày, miễn phí)
4. TRA CỨU ONLINE: Dancu.gov.vn hoặc App Dịch vụ công quốc gia → Xác nhận thông tin cư trú

KHI CƠ QUAN YÊU CẦU "SỔ HỘ KHẨU":
Cơ quan Nhà nước KHÔNG ĐƯỢC yêu cầu sổ hộ khẩu giấy kể từ 01/01/2023 — vi phạm nếu yêu cầu.
Người dân có quyền từ chối và báo cáo tại: dvcqg.gov.vn hoặc 1022 (đường dây hỗ trợ DVC).

THAY ĐỔI THÔNG TIN THƯỜNG TRÚ: Đăng ký trực tiếp tại Công an xã/phường hoặc online qua DVC quốc gia. Không cần sổ giấy.

Tra cứu thông tin cư trú của bản thân: Cổng DVC quốc gia dichvucong.gov.vn → "Tra cứu thông tin cư trú".''',
    },
]

# =============================================================================
# 4. LAO ĐỘNG CHUNG QUỐC GIA
# =============================================================================
LAO_DONG_CHUNG = [
    {
        'id': 'g-ld-001', 'category': 'lao_dong', 'procedure': 'sa_thai_trai_phap_luat', 'level': 'district',
        'source': 'Bộ luật Lao động 2019',
        'question': 'Bị sa thải, đơn phương chấm dứt hợp đồng thì công ty phải trả những gì? Khi nào là trái luật?',
        'answer': '''SA THẢI ĐÚNG LUẬT — CÔNG TY PHẢI:
- Báo trước: 45 ngày (HĐLĐ không thời hạn); 30 ngày (HĐLĐ có thời hạn ≥ 12 tháng); 3 ngày (HĐLĐ dưới 12 tháng)
- Trả trợ cấp thôi việc: 0,5 tháng lương/năm làm việc (cho thời gian đóng BHTN)

SA THẢI TRÁI LUẬT — ĐÒI ĐƯỢC:
1. Nhận lại làm việc (nếu muốn) HOẶC nhận bồi thường bằng tiền
2. Bồi thường: 2 tháng lương × số năm làm việc (ít nhất 2 tháng)
3. Lương trong thời gian không được làm việc (tính từ ngày bị đuổi đến ngày tòa xử)
4. Trợ cấp thôi việc

CÁC TRƯỜNG HỢP SA THẢI TRÁI LUẬT PHỔ BIẾN:
- Không có căn cứ pháp lý (lý do chủ quan, không vi phạm kỷ luật)
- Không thực hiện đúng trình tự kỷ luật (phải họp xem xét kỷ luật, có đại diện CĐ)
- Sa thải phụ nữ đang có thai/nuôi con dưới 12 tháng tuổi
- Sa thải NLĐ đang nghỉ ốm theo chỉ định BS (dưới 6 tháng liên tục)
- Sa thải NLĐ đang nghỉ phép năm, ngày nghỉ lễ

THỜI HIỆU KHIẾU NẠI: 1 năm kể từ ngày bị sa thải.
Nộp: Hòa giải viên lao động cấp huyện → TAND nếu không hòa giải được.''',
    },
    {
        'id': 'g-ld-002', 'category': 'lao_dong', 'procedure': 'bao_hiem_xa_hoi_bat_buoc', 'level': 'district',
        'source': 'Luật BHXH 2014 sửa đổi; Nghị định 12/2022/NĐ-CP',
        'question': 'Công ty không đóng BHXH cho người lao động bị xử phạt thế nào? NLĐ phải làm gì?',
        'answer': '''NGHĨA VỤ ĐÓNG BHXH BẮT BUỘC:
- Công ty đóng: 17,5% lương (BHXH 14%, BHYT 3%, BHTN 1% nếu tính nhầm — chính xác: BHXH 14%, BHYT 3%, BHTN 0,5% = 17,5%)
- Người lao động đóng: 10,5% lương (BHXH 8%, BHYT 1,5%, BHTN 1%)
- Tiền lương đóng BH ≥ Lương tối thiểu vùng và không vượt quá 20 lần lương cơ sở

CÔNG TY KHÔNG ĐÓNG/ĐÓNG THIẾU BHXH:
Xử phạt hành chính (Nghị định 12/2022):
- Trốn đóng BHXH từ 1–10 người: Phạt 12–15% số tiền trốn đóng (tối thiểu 5 triệu)
- Từ 1 tỷ đồng trở lên: Có thể truy cứu hình sự (tội trốn đóng BHXH, phạt tù đến 7 năm)
- Ngoài phạt: Bắt buộc đóng đủ + lãi chậm đóng 0,03%/ngày

NGƯỜI LAO ĐỘNG BỊ THIỆT THÒ PHẢI LÀM GÌ:
1. Tự tra cứu quá trình đóng BHXH: App "VssID" hoặc baohiemxahoi.gov.vn
2. Nếu phát hiện thiếu: Phản ánh đến Chi nhánh BHXH huyện nơi công ty đặt trụ sở
3. Tố cáo đến Thanh tra Sở LĐTBXH: Xử phạt và yêu cầu đóng bù
4. Khởi kiện ra TAND yêu cầu bồi thường

Tra cứu BHXH cá nhân: App VssID (Tổng công ty BHXH Việt Nam) — đăng nhập bằng Mã số BHXH ghi trên Sổ BHXH.''',
    },
    {
        'id': 'g-ld-003', 'category': 'lao_dong', 'procedure': 'che_do_huu_tri', 'level': 'province',
        'source': 'Luật BHXH 2014; Nghị định 115/2015/NĐ-CP',
        'question': 'Tuổi nghỉ hưu và điều kiện hưởng lương hưu hiện nay là gì? Mức lương hưu tính thế nào?',
        'answer': '''TUỔI NGHỈ HƯU (tăng dần theo lộ trình đến 2035):

NAM:
- 2024: 61 tuổi | 2025: 61,5 | 2026: 62 tuổi (đạt mức ổn định 62 tuổi)

NỮ:
- 2024: 56 tuổi | 2025: 56,5 | 2026: 57 | ... | 2035: 60 tuổi (đạt mức ổn định)

NGHỈ HƯU SỚM HƠN (thấp hơn 5 tuổi so với tuổi hưu chuẩn):
- Suy giảm sức lao động ≥ 61%
- Làm nghề nặng nhọc, độc hại (theo danh mục BLĐ quy định)
- Vùng kinh tế xã hội đặc biệt khó khăn

ĐIỀU KIỆN HƯỞNG LƯƠNG HƯU:
- Đủ tuổi nghỉ hưu + Đóng BHXH ≥ 20 năm

MỨC LƯƠNG HƯU:
- 45% mức lương bình quân (nam 20 năm đóng; nữ 15 năm đóng)
- Mỗi năm đóng thêm: Cộng thêm 2%/năm (tối đa 75%)
- Mức lương hưu tối thiểu = Lương cơ sở (2.340.000 đ từ 01/7/2024)

VÍ DỤ: Nam đóng 30 năm, lương BQ đóng BH = 8 triệu:
- Tỷ lệ = 45% + (30-20) × 2% = 65%
- Lương hưu = 65% × 8.000.000 = 5.200.000 đồng/tháng

Tra cứu thời gian đóng BHXH: App VssID hoặc baohiemxahoi.gov.vn.''',
    },
    {
        'id': 'g-ld-004', 'category': 'lao_dong', 'procedure': 'lao_dong_tu_do', 'level': 'district',
        'source': 'Luật BHXH 2014; Nghị định 134/2015/NĐ-CP',
        'question': 'Lao động tự do (xe ôm, bán hàng rong, nội trợ) có tham gia BHXH được không? Lợi ích gì?',
        'answer': '''Lao động tự do (không có hợp đồng lao động với công ty) tham gia BHXH TỰ NGUYỆN.

AI ĐƯỢC THAM GIA BHXH TỰ NGUYỆN:
- Mọi công dân Việt Nam từ đủ 15 tuổi trở lên không thuộc diện BHXH bắt buộc
- Gồm: Lao động tự do, nông dân, hộ kinh doanh, nội trợ, sinh viên, người thất nghiệp...

ĐĂNG KÝ Ở ĐÂU:
- BHXH cấp huyện hoặc BHXH cấp xã (một số địa phương)
- Đại lý thu BHXH tự nguyện (Bưu điện, điểm dịch vụ được ủy quyền)
- Online: App VssID → "Tham gia BHXH tự nguyện"

ĐÓNG BAO NHIÊU:
- 22% × mức thu nhập tháng tự chọn (tối thiểu = lương cơ sở; tối đa = 20 lần lương cơ sở)
- Từ 01/7/2024: Tối thiểu = 22% × 2.340.000 = 514.800 đồng/tháng
- Được chọn đóng: Hàng tháng / Hàng quý / 6 tháng / Cả năm / Nhiều năm một lần

QUYỀN LỢI KHI ĐỦ ĐIỀU KIỆN:
- LƯƠNG HƯU hàng tháng (đủ tuổi + đủ 20 năm đóng)
- TRỢ CẤP MỘT LẦN khi nghỉ hưu chưa đủ 20 năm
- BHYT miễn phí 3 tháng sau khi đóng đủ 12 tháng
- Trợ cấp tử tuất cho thân nhân

HỖ TRỢ ĐÓNG BHXH TỰ NGUYỆN: Nhà nước hỗ trợ 10–30% mức đóng tối thiểu cho hộ nghèo, cận nghèo.''',
    },
]

# =============================================================================
# 5. THUẾ CHUNG QUỐC GIA
# =============================================================================
THUE_CHUNG = [
    {
        'id': 'g-th-001', 'category': 'thue', 'procedure': 'giam_tru_gia_canh', 'level': 'district',
        'source': 'Luật Thuế TNCN 2007 sửa đổi; Nghị quyết 954/2020/UBTVQH14',
        'question': 'Giảm trừ gia cảnh trong thuế TNCN là gì? Đăng ký người phụ thuộc như thế nào?',
        'answer': '''Giảm trừ gia cảnh là khoản thu nhập được trừ trước khi tính thuế TNCN.

MỨC GIẢM TRỪ HIỆN HÀNH (từ 01/7/2020):
- Bản thân người nộp thuế: 11.000.000 đồng/tháng (132 triệu/năm)
- Mỗi người phụ thuộc: 4.400.000 đồng/tháng (52,8 triệu/năm)

Ví dụ: Thu nhập 20 triệu/tháng, 1 con nhỏ:
- Thu nhập tính thuế = 20 triệu - 11 triệu (bản thân) - 4,4 triệu (con) = 4,6 triệu
- Thuế TNCN bậc 1 (5%) = 230.000 đồng/tháng

AI ĐƯỢC TÍNH LÀ NGƯỜI PHỤ THUỘC:
- Con chưa đủ 18 tuổi
- Con từ 18 tuổi đang học đại học, CĐ, trung cấp, học nghề
- Vợ/chồng không có thu nhập hoặc thu nhập ≤ 1 triệu/tháng
- Cha mẹ/ông bà (cả hai bên) đủ 60 tuổi (nam), 55 tuổi (nữ) hoặc tàn tật, không có thu nhập
- Anh/chị/em ruột dưới 18 tuổi hoặc tàn tật không có thu nhập

ĐĂNG KÝ NGƯỜI PHỤ THUỘC:
1. Điền Mẫu 02/ĐK-NPT-TNCN
2. Kèm bằng chứng: Giấy khai sinh (con), CCCD + chứng minh không có thu nhập (cha mẹ)...
3. Nộp cho bộ phận kế toán công ty hoặc tự đăng ký trên thuedientu.gdt.gov.vn
Thời hạn: Đăng ký trong vòng 3 tháng đầu năm tính thuế.

Mỗi người phụ thuộc chỉ được đăng ký với 1 người nộp thuế.''',
    },
    {
        'id': 'g-th-002', 'category': 'thue', 'procedure': 'thue_tncn_tien_luong', 'level': 'district',
        'source': 'Luật Thuế TNCN 2007 sửa đổi; Thông tư 111/2013/TT-BTC',
        'question': 'Thuế TNCN từ tiền lương được tính theo biểu thuế lũy tiến như thế nào? Thu nhập bao nhiêu phải đóng thuế?',
        'answer': '''THU NHẬP CHỊU THUẾ TNCN TỪ TIỀN LƯƠNG:
Thu nhập chịu thuế = Tổng lương - Bảo hiểm NLĐ đóng (10,5%) - Giảm trừ bản thân (11 triệu) - Giảm trừ NPT

Nếu Thu nhập chịu thuế ≤ 0: Không phải đóng thuế.

BIỂU THUẾ LŨY TIẾN 7 BẬC (áp dụng cho phần còn lại):
| Bậc | Thu nhập tính thuế (tr.đ/tháng) | Thuế suất |
|-----|----------------------------------|-----------|
| 1   | Đến 5                           | 5%        |
| 2   | Trên 5 đến 10                   | 10%       |
| 3   | Trên 10 đến 18                  | 15%       |
| 4   | Trên 18 đến 32                  | 20%       |
| 5   | Trên 32 đến 52                  | 25%       |
| 6   | Trên 52 đến 80                  | 30%       |
| 7   | Trên 80                         | 35%       |

VÍ DỤ THỰC TẾ (lương 30 triệu, không NPT):
- BHXH-NLĐ: 30tr × 10,5% = 3,15tr
- Thu nhập chịu thuế: 30 - 3,15 - 11 = 15,85 triệu
- Thuế bậc 1: 5 × 5% = 250.000
- Thuế bậc 2: 5 × 10% = 500.000
- Thuế bậc 3: 5,85 × 15% = 877.500
- TỔNG THUẾ: 1.627.500 đồng/tháng

Thu nhập từ đâu để không đóng thuế: Lương ≤ 11 triệu + BH 10,5% = khoảng ≤ 12,3 triệu/tháng (không có NPT).''',
    },
    {
        'id': 'g-th-003', 'category': 'thue', 'procedure': 'mien_thue_tncn', 'level': 'district',
        'source': 'Luật Thuế TNCN 2007; Thông tư 111/2013/TT-BTC',
        'question': 'Những khoản thu nhập nào được miễn thuế TNCN? Tiền thưởng Tết có đóng thuế không?',
        'answer': '''CÁC KHOẢN THU NHẬP MIỄN THUẾ TNCN:

TỪ TIỀN LƯƠNG, TIỀN CÔNG:
- Phụ cấp ăn trưa: Miễn đến 730.000 đồng/tháng (bao gồm đồ ăn hiện vật)
- Phụ cấp điện thoại: Miễn theo mức khoán nếu phục vụ công việc (có văn bản quy định)
- Phụ cấp trang phục: Miễn đến 5 triệu đồng/người/năm (hiện vật hoặc tiền)
- Phụ cấp đi lại: Miễn nếu theo chế độ chung, không vượt mức khoán
- Hỗ trợ nhà ở: Miễn phần không quá 15% tổng thu nhập chịu thuế

TIỀN THƯỞNG TẾT CÓ ĐÓNG THUẾ KHÔNG?
CÓ — Tiền thưởng (thưởng Tết, thưởng hiệu quả) TÍNH VÀO THU NHẬP CHỊU THUẾ trong tháng nhận.
Nếu thưởng lớn (ví dụ nhận 50 triệu tháng 1) → Thuế tháng đó cao bất thường → Nên quyết toán cả năm để bình quân.

HOÀN TOÀN MIỄN THUẾ TNCN:
- Thu nhập từ lãi tiết kiệm ngân hàng (lãi suất)
- Cổ tức, lãi từ trái phiếu Chính phủ
- Kiều hối nhận từ cha mẹ, vợ chồng, con, anh chị em ruột
- Tiền bảo hiểm nhân thọ được chi trả
- Học bổng hợp lệ
- Trợ cấp thôi việc, mất việc làm theo luật
- Thu nhập bán nhà ở duy nhất (chỉ có 1 nhà, sở hữu ≥ 183 ngày)''',
    },
    {
        'id': 'g-th-004', 'category': 'thue', 'procedure': 'thue_chuyen_nhuong_bds', 'level': 'district',
        'source': 'Luật Thuế TNCN; Thông tư 92/2015/TT-BTC',
        'question': 'Bán nhà đất phải đóng thuế gì? Tính bao nhiêu %? Có được miễn không?',
        'answer': '''KHI BÁN NHÀ ĐẤT, người bán phải nộp THUẾ TNCN từ chuyển nhượng BĐS.

THUẾ SUẤT: 2% giá chuyển nhượng (ghi trên hợp đồng công chứng).
Người bán chịu (trừ trường hợp thỏa thuận người mua chịu — nhưng nghĩa vụ pháp lý vẫn thuộc người bán).

VÍ DỤ: Bán nhà giá 3 tỷ đồng → Thuế TNCN = 2% × 3 tỷ = 60 triệu đồng.

TRƯỜNG HỢP ĐƯỢC MIỄN THUẾ TNCN:
1. Bán nhà ở DUY NHẤT (chỉ có 1 nhà) và đã sở hữu ≥ 183 ngày
2. Chuyển nhượng BĐS giữa vợ và chồng
3. Chuyển nhượng giữa cha/mẹ và con (ruột); ông bà và cháu (ruột); anh/chị/em ruột
4. Thừa kế, tặng cho nhà đất giữa các đối tượng trên

CÁCH NỘP THUẾ:
1. Kê khai online tại thuedientu.gdt.gov.vn trước khi ký công chứng hợp đồng
2. Hoặc kê khai tại Chi cục Thuế nơi có BĐS
3. Nộp tiền tại Kho bạc/ngân hàng liên kết
4. Mang biên lai nộp thuế để công chứng hợp đồng và đăng ký biến động đất đai

Lưu ý: Văn phòng công chứng KHÔNG ký hợp đồng nếu chưa có xác nhận kê khai thuế.''',
    },
]

# =============================================================================
# 6. Y TẾ CHUNG QUỐC GIA
# =============================================================================
Y_TE_CHUNG = [
    {
        'id': 'g-yt-001', 'category': 'y_te', 'procedure': 'dang_ky_kham_benh', 'level': 'district',
        'source': 'Luật Khám chữa bệnh 2023',
        'question': 'Đăng ký khám bệnh ở bệnh viện công có cần đặt lịch trước không? Làm sao tránh xếp hàng?',
        'answer': '''Khám bệnh ở bệnh viện công — đặt lịch trước giúp tiết kiệm thời gian đáng kể.

CÁCH ĐẶT LỊCH KHÁM:
1. APP/WEBSITE BỆNH VIỆN: Hầu hết bệnh viện lớn có app riêng (BV Bạch Mai, BV Chợ Rẫy, BV K...)
2. CỔNG ĐẶT LỊCH QUỐC GIA: Suckhoedientu.vn — đặt lịch tại hơn 900 cơ sở y tế toàn quốc
3. ZALO HEALTH: Đặt lịch qua Mini App "Sức khỏe quốc dân"
4. GỌI ĐIỆN: Tổng đài của bệnh viện (thường 8:00–17:00)
5. ĐẾN TRỰC TIẾP lấy số thứ tự (phải đến sớm, 6–7 giờ sáng)

ĐẶT LỊCH QUA BHYT ĐIỆN TỬ:
App "VssID" → "Đặt lịch khám chữa bệnh" → Chọn cơ sở y tế BHYT đăng ký ban đầu
→ Chọn ngày giờ → Xác nhận → Nhận mã xác nhận

ĐI KHÁM CẦN MANG:
- CCCD/VNeID (bắt buộc để đăng ký khám)
- Thẻ BHYT (nếu có, để được hưởng quyền lợi BH)
- Kết quả khám trước đây (nếu tái khám)

PHÍ KHÁM BỆNH:
- Có BHYT đúng tuyến: Chỉ đóng phần đồng chi trả (20% với tuyến tỉnh; 30% với tuyến trung ương)
- Không có BHYT/trái tuyến: Theo khung giá dịch vụ y tế (100.000–500.000 đồng/lần tùy bệnh viện)

ĐỐI TƯỢNG ĐƯỢC KHÁM ƯU TIÊN (không xếp hàng): Người cao tuổi ≥ 80, phụ nữ có thai, trẻ dưới 6 tuổi, người khuyết tật đặc biệt nặng.''',
    },
    {
        'id': 'g-yt-002', 'category': 'y_te', 'procedure': 'tuyen_kham_chua_benh', 'level': 'district',
        'source': 'Luật BHYT 2014 sửa đổi 2023; Thông tư 40/2015/TT-BYT',
        'question': 'Quy định về tuyến khám chữa bệnh BHYT là gì? Khi nào được lên tuyến trên không cần giấy chuyển tuyến?',
        'answer': '''HỆ THỐNG 4 TUYẾN KHÁM CHỮA BỆNH:
- Tuyến 1 (xã, phường): Trạm y tế xã — khám ban đầu, bệnh thông thường
- Tuyến 2 (huyện/quận): Bệnh viện huyện — điều trị hầu hết bệnh thông thường
- Tuyến 3 (tỉnh): Bệnh viện tỉnh/thành phố — điều trị bệnh phức tạp
- Tuyến 4 (Trung ương): Bệnh viện đầu ngành toàn quốc — bệnh đặc biệt khó

ĐƯỢC LÊN TUYẾN TRÊN MÀ KHÔNG CẦN GIẤY CHUYỂN TUYẾN:
1. THÔNG TUYẾN HUYỆN: Từ 2016, bệnh nhân BHYT được khám tại bất kỳ BV huyện nào trong tỉnh mà không cần chuyển tuyến (coi như đúng tuyến — thanh toán đầy đủ)
2. TRƯỜNG HỢP CẤP CỨU: Được khám trực tiếp tại bất kỳ tuyến nào, BHYT vẫn thanh toán
3. BỆNH HIẾM/ĐẶC BIỆT: Một số bệnh (ung thư, HIV, tâm thần...) được khám thẳng tuyến tỉnh/trung ương
4. TRỰC TIẾP BV TỰ NGUYỆN: Được khám nhưng thanh toán theo mức trái tuyến (40–60%)

GIẤY CHUYỂN TUYẾN:
- Có giá trị 30 ngày kể từ ngày ký
- Phải chuyển đúng tuyến ghi trên giấy
- Một số bệnh mãn tính (ĐTĐ, cao huyết áp): Giấy chuyển có thể dùng cho cả đợt điều trị (đến 12 tháng)

Đăng ký cơ sở KCB ban đầu (thay đổi 1 năm 1 lần, tháng 1 hàng năm) tại BHXH nơi cư trú.''',
    },
    {
        'id': 'g-yt-003', 'category': 'y_te', 'procedure': 'thuoc_bhyt', 'level': 'district',
        'source': 'Thông tư 20/2022/TT-BYT; Nghị định 146/2018/NĐ-CP',
        'question': 'BHYT thanh toán thuốc gì? Khi bác sĩ kê thuốc ngoài danh mục BHYT thì phải trả thêm không?',
        'answer': '''BHYT CHỈ THANH TOÁN THUỐC TRONG "DANH MỤC THUỐC BHYT":
Danh mục gồm khoảng 1.000 hoạt chất — tra cứu đầy đủ tại: yte.gov.vn.

NGUYÊN TẮC THANH TOÁN THUỐC BHYT:
- Thuốc trong danh mục + phù hợp phác đồ điều trị: BHYT thanh toán 80–100%
- Thuốc NGOÀI danh mục: Người bệnh tự trả 100%
- Thuốc trong danh mục nhưng dùng không đúng chỉ định: Người bệnh tự trả

KHI BÁC SĨ KÊ THUỐC NGOÀI DANH MỤC BHYT:
- Bác sĩ PHẢI thông báo trước để người bệnh biết sẽ phải tự trả
- Người bệnh CÓ QUYỀN từ chối và yêu cầu thay thế thuốc trong danh mục
- Không bị ép mua thuốc ngoài danh mục

THUỐC KHÔNG ĐƯỢC BHYT THANH TOÁN (dù trong danh mục):
- Thuốc làm đẹp, giảm cân, tăng chiều cao
- Vitamin, khoáng chất dùng phòng bệnh (không phải điều trị)
- Thuốc y học cổ truyền tại một số cơ sở chưa được chỉ định

MUA THUỐC THEO ĐƠN NGOẠI TRÚ CÓ BHYT:
- Đến nhà thuốc bệnh viện (trong danh mục BHYT được thanh toán)
- Nhà thuốc tư: KHÔNG được thanh toán BHYT (trừ chương trình thí điểm một số tỉnh)''',
    },
]

# =============================================================================
# 7. KINH DOANH CHUNG QUỐC GIA
# =============================================================================
KINH_DOANH_CHUNG = [
    {
        'id': 'g-kd-001', 'category': 'kinh_doanh', 'procedure': 'dieu_kien_kinh_doanh', 'level': 'province',
        'source': 'Luật Đầu tư 2020; Luật Doanh nghiệp 2020',
        'question': 'Ngành nghề kinh doanh có điều kiện là gì? Cần thêm giấy phép gì ngoài giấy đăng ký KD?',
        'answer': '''Ngành nghề kinh doanh có điều kiện (ĐKKD) là ngành phải đáp ứng điều kiện cụ thể TRƯỚC hoặc SAU KHI đăng ký kinh doanh.

NGUỒN TRA CỨU DANH MỤC: Phụ lục IV Luật Đầu tư 2020 — hiện có 227 ngành nghề ĐKKD.

MỘT SỐ NGÀNH PHỔ BIẾN VÀ ĐIỀU KIỆN:

DỊCH VỤ ĂN UỐNG:
- Giấy CN cơ sở đủ điều kiện ATTP (Sở Y tế/Phòng Y tế cấp)
- Chứng nhận tập huấn kiến thức ATTP

KINH DOANH RƯỢU/BIA:
- Giấy phép bán lẻ rượu (UBND phường cấp) hoặc bán buôn (Sở Công thương)

DỊCH VỤ KARAOKE, VŨ TRƯỜNG:
- Phòng VHTT cấp phép; phải đạt tiêu chuẩn âm thanh, PCCC, ATTP...

KHO BÃI, VẬN TẢI:
- Giấy phép kinh doanh vận tải (Sở GTVT)

DỊCH VỤ TÀI CHÍNH (cho vay, bảo hiểm, chứng khoán):
- Giấy phép NHNN, BTC cấp — rất khó được cấp, vốn điều lệ tối thiểu cực lớn

CÁ CƯỢC, TRÒ CHƠI ĐIỆN TỬ CÓ THƯỞNG:
- Giấy phép Bộ Tài chính/Bộ Công thương (rất hạn chế)

KIỂM TRA ĐIỀU KIỆN KHI ĐĂNG KÝ:
Cổng thông tin đăng ký doanh nghiệp: dangkykinhdoanh.gov.vn → "Điều kiện kinh doanh"
Hoặc: Phòng ĐKKD Sở KH&ĐT sẽ tư vấn miễn phí khi nộp hồ sơ.''',
    },
    {
        'id': 'g-kd-002', 'category': 'kinh_doanh', 'procedure': 'thay_doi_dkkd', 'level': 'district',
        'source': 'Luật Doanh nghiệp 2020; Nghị định 01/2021/NĐ-CP',
        'question': 'Thay đổi địa chỉ, ngành nghề, vốn điều lệ của doanh nghiệp phải làm thủ tục gì?',
        'answer': '''Thay đổi thông tin đăng ký doanh nghiệp nộp tại Phòng ĐKKD - Sở KH&ĐT (hoặc online tại dangkykinhdoanh.gov.vn).
Thời gian: 3 ngày làm việc. Lệ phí: 50.000 đồng (nộp hồ sơ giấy) hoặc miễn phí (online).

CÁC THAY ĐỔI PHỔ BIẾN:

1. ĐỔI ĐỊA CHỈ TRỤ SỞ:
Hồ sơ: Thông báo thay đổi (Mẫu I-1) + Giấy tờ địa chỉ mới (hợp đồng thuê hoặc GCN QSDĐ).
Lưu ý: Đổi địa chỉ khác quận/huyện → thông báo đến Cục Thuế và BHXH trong vòng 5 ngày.

2. THAY ĐỔI NGÀNH NGHỀ:
Hồ sơ: Thông báo thay đổi + Điều lệ sửa đổi (nếu điều lệ quy định ngành nghề).
Ngành có điều kiện: Phải đáp ứng điều kiện trước hoặc sau khi đăng ký.

3. TĂNG/GIẢM VỐN ĐIỀU LỆ:
Tăng vốn: Thông báo thay đổi + Quyết định của HĐTV/ĐHCĐ về tăng vốn + Danh sách góp vốn mới.
Giảm vốn: Phải đảm bảo đủ điều kiện (không còn nợ quá hạn, vốn sau giảm ≥ mức tối thiểu ngành nghề ĐKKD).

4. ĐỔI TÊN DOANH NGHIỆP:
Tên mới không trùng/gây nhầm lẫn với DN đã đăng ký — kiểm tra tại dangkykinhdoanh.gov.vn.
Sau khi đổi tên: Cập nhật con dấu, hóa đơn, tài khoản ngân hàng, giấy phép...

5. THAY ĐỔI NGƯỜI ĐẠI DIỆN PHÁP LUẬT:
Hồ sơ: Thông báo thay đổi + CCCD người đại diện mới + Quyết định bổ nhiệm.''',
    },
    {
        'id': 'g-kd-003', 'category': 'kinh_doanh', 'procedure': 'hop_dong_dien_tu', 'level': 'province',
        'source': 'Luật Giao dịch điện tử 2023; Nghị định 52/2013/NĐ-CP',
        'question': 'Hợp đồng điện tử có giá trị pháp lý không? Ký online qua email hay app có được không?',
        'answer': '''HỢP ĐỒNG ĐIỆN TỬ CÓ GIÁ TRỊ PHÁP LÝ theo Luật Giao dịch điện tử 2023 (thay thế Luật 2005).

ĐIỀU KIỆN ĐỂ HỢP ĐỒNG ĐIỆN TỬ CÓ HIỆU LỰC:
1. Các bên đồng ý sử dụng hình thức điện tử
2. Thông tin trong hợp đồng có thể truy cập và sử dụng được (không bị thay đổi)
3. Có chữ ký điện tử hợp lệ (đối với hợp đồng cần chữ ký)

CÁC LOẠI GIAO DỊCH ĐIỆN TỬ:
- Nhấn "Đồng ý" / "Accept" trên website: Có giá trị (hợp đồng click-wrap)
- Gửi email xác nhận đơn hàng: Có giá trị hợp đồng mua bán
- Chữ ký scan/ảnh chụp: Có giá trị nhưng rủi ro tranh chấp cao
- Chữ ký số (PKI): Giá trị pháp lý cao nhất, khó tranh chấp

HỢP ĐỒNG KHÔNG ĐƯỢC KÝ BẰNG HÌNH THỨC ĐIỆN TỬ (phải giấy + công chứng):
- Hợp đồng chuyển nhượng BĐS (nhà, đất)
- Di chúc, thừa kế
- Hôn nhân, ly hôn, nhận nuôi con nuôi
- Giấy tờ quan trọng về hộ tịch, hộ khẩu
- Vận đơn, chứng thư bảo hiểm (theo pháp luật chuyên ngành)

TRANH CHẤP HỢP ĐỒNG ĐIỆN TỬ:
Bằng chứng: Lịch sử email, log hệ thống, metadata file, chứng thư chữ ký số — đều được chấp nhận tại tòa án.

Dịch vụ ký hợp đồng điện tử uy tín: MISA eSign, Viettel Sign, FPT.eContract, VNPT eSign.''',
    },
]

# =============================================================================
# 8. XÂY DỰNG CHUNG QUỐC GIA
# =============================================================================
XAY_DUNG_CHUNG = [
    {
        'id': 'g-xd-001', 'category': 'xay_dung', 'procedure': 'muc_do_xay_dung', 'level': 'district',
        'source': 'Luật Xây dựng 2014 sửa đổi 2020; Quy chuẩn QCVN 01:2021/BXD',
        'question': 'Nhà ở riêng lẻ được phép xây tối đa mấy tầng? Mật độ xây dựng tối đa là bao nhiêu?',
        'answer': '''Tầng cao và mật độ xây dựng nhà ở riêng lẻ phụ thuộc vào QUY HOẠCH ĐÔ THỊ của từng khu vực.

NGUYÊN TẮC CHUNG:
Không có quy định thống nhất toàn quốc — mỗi đô thị có QUY CHẾ QUẢN LÝ KIẾN TRÚC riêng, trong đó ghi rõ:
- Số tầng tối đa
- Mật độ xây dựng tối đa (%)
- Hệ số sử dụng đất (floor area ratio - FAR)
- Khoảng lùi tối thiểu so với đường, hàng xóm

CÁC MỨC THÔNG THƯỜNG:
Nhà phố đô thị (phường, thị trấn):
- Tầng cao: Phụ thuộc quy hoạch, thường 4–7 tầng với đường ≥ 6m
- Mật độ XD: 90–100% đất
Nhà ở nông thôn (xã, vùng ngoại ô):
- Tầng cao: Thường ≤ 3 tầng
- Mật độ XD: 40–60%

ĐỂ BIẾT CHÍNH XÁC CHO THỬA ĐẤT CỤ THỂ:
1. Tra cứu quy hoạch online tại cổng Sở Xây dựng tỉnh
2. Hỏi Phòng Quản lý Đô thị hoặc Phòng Kinh tế Hạ tầng UBND huyện
3. Yêu cầu Chứng chỉ Quy hoạch (Lô đất thông tin quy hoạch) — cơ quan cấp trong 3 ngày

LƯU Ý:
- Xây vượt số tầng quy hoạch: Bị phạt + buộc phá dỡ phần vi phạm
- Nhà mặt phố: Thường bị yêu cầu xây đồng bộ về độ cao, kiến trúc với nhà kề bên
- Hành lang phòng cháy, an toàn điện cao thế: Hạn chế chiều cao riêng biệt''',
    },
    {
        'id': 'g-xd-002', 'category': 'xay_dung', 'procedure': 'quy_hoach_1_500', 'level': 'district',
        'source': 'Luật Quy hoạch đô thị 2009; Luật Xây dựng 2014',
        'question': 'Bản đồ quy hoạch 1/500, 1/2000, 1/5000 khác nhau thế nào? Đọc bản đồ quy hoạch như thế nào?',
        'answer': '''CÁC LOẠI QUY HOẠCH ĐÔ THỊ:

QUY HOẠCH VÙNG (tỷ lệ 1/50.000 – 1/500.000):
Phạm vi lớn: Liên vùng, vùng kinh tế. Không chi tiết đến từng thửa đất.

QUY HOẠCH CHUNG (tỷ lệ 1/5.000 – 1/25.000):
Toàn đô thị. Xác định: Các khu chức năng (khu ở, khu công nghiệp, đất giao thông...).

QUY HOẠCH PHÂN KHU (tỷ lệ 1/2.000 – 1/5.000):
Khu vực cụ thể trong đô thị. Xác định: Mật độ XD, tầng cao tối đa, chỉ giới đường đỏ.

QUY HOẠCH CHI TIẾT (tỷ lệ 1/500):
Chi tiết nhất, áp dụng trực tiếp cho từng ô đất cụ thể. Bắt buộc phải có trước khi cấp phép xây dựng.

ĐỌC KÝ HIỆU BẢN ĐỒ QUY HOẠCH:
- ONT: Đất ở nông thôn
- ODT: Đất ở đô thị
- LUC/LUA: Đất lúa nước (màu vàng chanh)
- CLN: Đất cây lâu năm (màu xanh nhạt)
- BHT/GT: Đất giao thông (màu vàng nhạt)
- CX: Đất cây xanh công cộng (màu xanh lá)
- TM: Đất thương mại dịch vụ

ĐƯỜNG MÀU ĐỎ trên bản đồ = ĐƯỜNG ĐỎ (chỉ giới đường — không được xây vào phần này)
ĐƯỜNG MÀU TÍM/XANH = ranh giới khu đất, lô đất

Tra cứu online: Hầu hết tỉnh có portal bản đồ quy hoạch số (ví dụ Hà Nội: qhkt.hanoi.gov.vn; HCM: gis.hochiminhcity.gov.vn).''',
    },
]

# =============================================================================
# 9. AN NINH TRẬT TỰ CHUNG
# =============================================================================
AN_NINH_CHUNG = [
    {
        'id': 'g-an-001', 'category': 'an_ninh', 'procedure': 'tai_nan_giao_thong', 'level': 'district',
        'source': 'Bộ luật Dân sự 2015; Nghị định 100/2019/NĐ-CP',
        'question': 'Xảy ra tai nạn giao thông phải làm gì? Ai chịu bồi thường thiệt hại?',
        'answer': '''KHI XẢY RA TAI NẠN GIAO THÔNG:

NGAY LẬP TỨC:
1. Gọi 113 (Cảnh sát giao thông) và 115 (Cấp cứu) nếu có người bị thương
2. Bật đèn cảnh báo khẩn cấp, đặt tam giác phản quang (cách 50–100m)
3. KHÔNG di chuyển phương tiện trừ khi cản trở giao thông nghiêm trọng
4. Sơ cứu nạn nhân nếu có thể (không di chuyển người bị thương cột sống)
5. Ghi lại hiện trường: Chụp ảnh, quay video, vị trí xe, vết bánh xe, biển số
6. Thu thập thông tin người chứng kiến

KHI CẢNH SÁT ĐẾN:
- Hợp tác khai báo trung thực
- Lập biên bản tai nạn (yêu cầu 1 bản)
- Đo nồng độ cồn (tuân thủ)

BỒI THƯỜNG THIỆT HẠI:
- Bảo hiểm trách nhiệm dân sự xe cơ giới (bắt buộc): Bồi thường người bị hại tối đa 150 triệu đồng/người (thương tích) hoặc 150 triệu đồng (tài sản)
- Phần vượt bảo hiểm: Người gây tai nạn tự bồi thường
- Nếu người gây tai nạn chạy trốn: Quỹ bảo hiểm xe cơ giới bồi thường tạm thời

LỖI DO CẢ HAI BÊN: Bồi thường theo tỷ lệ lỗi (tòa án xác định).
Lỗi hoàn toàn của bên bị hại: Người điều khiển xe không phải bồi thường.''',
    },
    {
        'id': 'g-an-002', 'category': 'an_ninh', 'procedure': 'bao_mat_thong_tin', 'level': 'province',
        'source': 'Luật An toàn thông tin mạng 2015; Luật Bảo vệ bí mật nhà nước 2018',
        'question': 'Thông tin cá nhân bị lộ lọt trên mạng thì phải làm gì? Ai bảo vệ dữ liệu cá nhân?',
        'answer': '''Dữ liệu cá nhân được bảo vệ theo Nghị định 13/2023/NĐ-CP (hiệu lực 01/7/2023).

QUYỀN CỦA NGƯỜI CÓ DỮ LIỆU CÁ NHÂN:
- Biết thông tin về việc xử lý dữ liệu của mình
- Yêu cầu chỉnh sửa, xóa dữ liệu không chính xác
- Phản đối hoặc hạn chế việc xử lý dữ liệu
- Rút lại sự đồng ý đã cấp trước đó
- Khiếu nại, tố cáo hành vi vi phạm

KHI BỊ LỘ LỌT DỮ LIỆU CÁ NHÂN:

1. XÁC ĐỊNH NGUỒN LỘ: App nào, website nào đã rò rỉ
2. THAY ĐỔI MẬT KHẨU NGAY: Mật khẩu email, tài khoản ngân hàng, mạng xã hội
3. BẬT XÁC THỰC 2 LỚP (2FA): Trên mọi tài khoản quan trọng
4. THEO DÕI TÀI KHOẢN NGÂN HÀNG: Phát hiện giao dịch lạ → khóa thẻ ngay
5. BÁO CÁO VI PHẠM:
   - Cục An toàn thông tin (Bộ TTTT): 1800.1166 (miễn phí) hoặc ais.gov.vn
   - Cảnh sát Phòng chống tội phạm sử dụng công nghệ cao (PC50) - Bộ Công an
   - Trung tâm Ứng cứu sự cố mạng VNCERT: 704.0.704@vncert.vn

XỬ PHẠT VI PHẠM BẢO VỆ DỮ LIỆU CÁ NHÂN (Nghị định 13/2023):
- Tổ chức vi phạm: Phạt đến 5% doanh thu hoặc đến 5 tỷ đồng
- Cá nhân: Phạt hành chính 50–80 triệu đồng

SIM RÁC VÀ DATA BỊ MUA BÁN: Tố cáo số điện thoại lừa đảo tại chongluadao.vn hoặc App VnSafe.''',
    },
]

# =============================================================================
# 10. THÔNG TIN CHUNG VỀ CỔNG DVC QUỐC GIA
# =============================================================================
DVC_QUOC_GIA = [
    {
        'id': 'g-dvc-001', 'category': 'dich_vu_cong', 'procedure': 'cong_dvc_quoc_gia', 'level': 'province',
        'source': 'Nghị định 42/2022/NĐ-CP; Quyết định 06/QĐ-TTg',
        'question': 'Cổng Dịch vụ công Quốc gia là gì? Có thể nộp hồ sơ online những thủ tục gì?',
        'answer': '''Cổng Dịch vụ công Quốc gia: https://dichvucong.gov.vn là nền tảng duy nhất tích hợp dịch vụ công của toàn bộ các bộ, ngành, địa phương.

ĐĂNG NHẬP BẰNG: Tài khoản định danh điện tử (VNeID mức 1/2) hoặc tài khoản CCCD/BHXH.

CÁC DỊCH VỤ PHỔ BIẾN CÓ THỂ NỘP ONLINE:
- HỘ TỊCH: Đăng ký khai sinh, kết hôn, khai tử, cải chính hộ tịch
- CƯ TRÚ: Đăng ký thường trú, tạm trú, tách hộ, xác nhận cư trú
- CCCD/CĂN CƯỚC: Cấp mới, cấp lại, đổi thẻ
- HỘ CHIẾU: Cấp hộ chiếu (nhận kết quả qua bưu điện)
- ĐẤT ĐAI: Tra cứu thông tin thửa đất, đăng ký biến động (một số tỉnh)
- THUẾ: Đăng ký MST, kê khai, nộp thuế
- DOANH NGHIỆP: Đăng ký, thay đổi thông tin kinh doanh
- BHXH: Đăng ký, tra cứu, cấp sổ BHXH, thẻ BHYT

MỨC ĐỘ DỊCH VỤ CÔNG TRỰC TUYẾN:
- Mức 1: Cung cấp thông tin
- Mức 2: Tải mẫu đơn
- Mức 3: Nộp hồ sơ online, nhận kết quả trực tiếp
- Mức 4: Toàn trình online (nộp hồ sơ, thanh toán, nhận kết quả điện tử)

THANH TOÁN PHÍ/LỆ PHÍ ONLINE: Qua VNPay, MoMo, thẻ ngân hàng, QR code.

TRA CỨU TIẾN ĐỘ HỒ SƠ: Đăng nhập cổng → "Hồ sơ của tôi" → Xem trạng thái từng bước.
Hotline hỗ trợ: 1022 (miễn phí).''',
    },
    {
        'id': 'g-dvc-002', 'category': 'dich_vu_cong', 'procedure': 'thu_tuc_hanh_chinh', 'level': 'province',
        'source': 'Nghị định 61/2018/NĐ-CP; Nghị định 107/2021/NĐ-CP',
        'question': 'Cơ quan nhà nước không giải quyết hồ sơ đúng hạn thì người dân có quyền gì?',
        'answer': '''Người dân có đầy đủ quyền pháp lý khi cơ quan hành chính giải quyết hồ sơ trễ hẹn.

QUYỀN CỦA NGƯỜI DÂN KHI HỒ SƠ TRỄ HẠN:

1. PHẢN ÁNH QUA ĐƯỜNG DÂY NÓNG:
   - Hotline DVC Quốc gia: 1022 (miễn phí, 24/7) — phản ánh trực tiếp, được xử lý trong 24h
   - Cổng phản ánh của tỉnh/thành phố
   - App "Phản ánh 1022"

2. KHIẾU NẠI HÀNH CHÍNH:
   - Gửi đơn khiếu nại đến người đứng đầu cơ quan đã thụ lý hồ sơ
   - Thời hạn giải quyết khiếu nại: 30 ngày (phức tạp: 45 ngày)

3. TỐ CÁO HÀNH VI NHŨNG NHIỄU:
   - Cán bộ cố tình trì hoãn để gợi ý "bồi dưỡng": Tố cáo với thanh tra cơ quan, Thanh tra Chính phủ

XỬ PHẠT CÁN BỘ TRỄ HẸN (Nghị định 107/2021):
- Giải quyết trễ hạn không có lý do chính đáng: Kiểm điểm, xử lý kỷ luật
- Cố tình gây khó dễ: Hạ bậc lương, cách chức, thậm chí truy cứu hình sự (hành hạ công dân)

TRÁCH NHIỆM GIẢI TRÌNH:
- Cơ quan phải thông báo lý do khi gia hạn hoặc trễ hẹn
- Không được yêu cầu bổ sung hồ sơ quá 1 lần sau khi đã thụ lý
- Không được yêu cầu thêm hồ sơ ngoài thành phần đã công bố

Thời hạn giải quyết và thành phần hồ sơ tra cứu tại: dichvucong.gov.vn (tra cứu TTHC).''',
    },
    {
        'id': 'g-dvc-003', 'category': 'dich_vu_cong', 'procedure': 'so_hoa_ho_so', 'level': 'province',
        'source': 'Nghị định 45/2020/NĐ-CP; Chỉ thị 05/CT-TTg',
        'question': 'Số hóa hồ sơ, giấy tờ là gì? Làm thế nào để không phải nộp bản sao công chứng khi làm thủ tục?',
        'answer': '''Số hóa hồ sơ là chủ trương của Chính phủ để giảm bớt giấy tờ photo, công chứng khi làm thủ tục hành chính.

NGUYÊN TẮC "KẾT QUẢ SỐ":
Từ 2023, kết quả giải quyết TTHC (Giấy khai sinh, GCN QSDĐ, CCCD...) đều được lưu vào cơ sở dữ liệu quốc gia.
→ Lần sau làm thủ tục khác liên quan, cơ quan tra cứu online — KHÔNG cần nộp bản photo/công chứng.

CÁC GIẤY TỜ KHÔNG CẦN NỘP BẢN SAO:
- CCCD/Căn cước: Xuất trình thẻ gốc để đối chiếu (không cần bản sao)
- Giấy khai sinh: Cơ quan tra cứu hệ thống (không cần nộp bản sao)
- Sổ hộ khẩu: Đã bãi bỏ (xem quy định cư trú số hóa)
- GCN QSDĐ: Đã có trên hệ thống đất đai (nhiều tỉnh đã số hóa)

KHI NÀO PHẢI CÔNG CHỨNG/CHỨNG THỰC:
- Giấy tờ nước ngoài (bắt buộc hợp pháp hóa lãnh sự + dịch thuật)
- Hợp đồng chuyển nhượng BĐS, ủy quyền tài sản lớn
- Một số thủ tục đặc biệt theo quy định chuyên ngành

TRỢ GIÚP SỐ HÓA TẠI CHỖ:
Bộ phận một cửa các cơ quan hành chính có bộ phận scan và số hóa hồ sơ miễn phí — người dân mang bản gốc, nhân viên scan và lưu vào hệ thống.

NẾU CƠ QUAN VẪN YÊU CẦU BẰNG GIẤY KHÔNG CẦN THIẾT: Phản ánh tại 1022 hoặc dichvucong.gov.vn.''',
    },
    {
        'id': 'g-dvc-004', 'category': 'dich_vu_cong', 'procedure': 'ho_so_lien_thong', 'level': 'province',
        'source': 'Quyết định 468/QĐ-TTg; Nghị định 61/2018/NĐ-CP',
        'question': 'Thủ tục liên thông là gì? Ví dụ: khi sinh con cần bao nhiêu cơ quan giải quyết?',
        'answer': '''THỦ TỤC LIÊN THÔNG là nhóm TTHC có liên quan được giải quyết cùng lúc, người dân chỉ cần nộp hồ sơ một lần.

VÍ DỤ TIÊU BIỂU — KHI SINH CON:

TRƯỚC ĐÂY (làm từng thủ tục):
1. Đăng ký khai sinh (UBND xã) → 3 ngày
2. Đăng ký thường trú cho bé (Công an phường) → 7 ngày
3. Cấp thẻ BHYT cho bé (BHXH huyện) → 5 ngày
TỔNG: 3 cơ quan, 15 ngày

HIỆN NAY — LIÊN THÔNG 3 THỦ TỤC:
Nộp 1 bộ hồ sơ tại UBND xã/phường → Cơ quan chia sẻ thông tin → Nhận kết quả cả 3 trong 7 ngày.
(Khai sinh + Thường trú cho bé + Thẻ BHYT miễn phí cho bé dưới 6 tuổi)

CÁC NHÓM TTHC LIÊN THÔNG PHỔ BIẾN:
- Sinh con: Khai sinh + Thường trú + BHYT (Liên thông 3 trong 1)
- Khai tử: Đăng ký khai tử + Xóa thường trú + Hưởng chế độ tử tuất BHXH (Liên thông 3 trong 1)
- Thành lập DN: Đăng ký KD + Đăng ký thuế + Khắc dấu + Mở TK ngân hàng (nhiều địa phương)

NỘP HỒ SƠ LIÊN THÔNG TẠI:
- Bộ phận một cửa UBND xã/phường/huyện (nộp tất cả ở đây, họ chuyển tiếp)
- Cổng DVC Quốc gia (online) — chọn TTHC liên thông

Hotline hỗ trợ: 1022 (miễn phí, 24/7).''',
    },
    {
        'id': 'g-dvc-005', 'category': 'dich_vu_cong', 'procedure': 'tra_cuu_thu_tuc', 'level': 'province',
        'source': 'Cơ sở dữ liệu quốc gia về TTHC - thutuchanhchinh.gov.vn',
        'question': 'Làm sao tra cứu thủ tục hành chính bất kỳ? Biết được cần hồ sơ gì, nộp ở đâu, mất bao lâu?',
        'answer': '''Để tra cứu thủ tục hành chính chính xác nhất, dùng các kênh sau:

1. CỔNG DVC QUỐC GIA (dichvucong.gov.vn):
   - Tra cứu → TTHC → Nhập tên thủ tục → Chọn tỉnh/thành phố → Xem chi tiết
   - Hiển thị: Tên TTHC, hồ sơ cần nộp, cơ quan tiếp nhận, thời gian, lệ phí, cơ sở pháp lý

2. CƠ SỞ DỮ LIỆU QUỐC GIA VỀ TTHC (thutuchanhchinh.gov.vn):
   - Hơn 6.000 TTHC từ cấp xã đến trung ương
   - Tìm kiếm theo: Tên thủ tục, cơ quan thực hiện, cấp thực hiện

3. APP "CỔNG DVC QUỐC GIA":
   - Tải trên Android/iOS → Đăng nhập → Tra cứu TTHC → Nộp hồ sơ online

4. TRỰC TIẾP:
   - Gọi Hotline 1022 (miễn phí) → Hỏi cán bộ tư vấn
   - Đến Bộ phận Một cửa UBND xã/huyện → Nhân viên hướng dẫn

THÔNG TIN CUNG CẤP KHI HỎI TƯ VẤN:
- Tên thủ tục muốn làm (nếu không biết: mô tả việc cần làm)
- Địa chỉ của mình (để biết nộp ở cấp nào, địa phương nào)
- Hoàn cảnh cụ thể (ví dụ: khai sinh trễ hạn, đất chưa có sổ...)

CÁC THAY ĐỔI THỦ TỤC QUAN TRỌNG NĂM 2024–2025:
- Luật Đất đai 2024: Nhiều TTHC đất đai thay đổi từ 01/01/2025
- Luật Căn cước 2023: CCCD đổi thành Căn cước từ 01/7/2024
- Luật Nhà ở 2023: Điều kiện mua nhà của người nước ngoài thay đổi từ 01/01/2025''',
    },
]


def create_batch6_files():
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_g_ho_tich.xlsx':     HO_TICH_CHUNG,
        'faq_g_dat_dai.xlsx':     DAT_DAI_CHUNG,
        'faq_g_cccd_cu_tru.xlsx': CCCD_CHUNG,
        'faq_g_lao_dong.xlsx':    LAO_DONG_CHUNG,
        'faq_g_thue.xlsx':        THUE_CHUNG,
        'faq_g_y_te.xlsx':        Y_TE_CHUNG,
        'faq_g_kinh_doanh.xlsx':  KINH_DOANH_CHUNG,
        'faq_g_xay_dung.xlsx':    XAY_DUNG_CHUNG,
        'faq_g_an_ninh.xlsx':     AN_NINH_CHUNG,
        'faq_g_dvc.xlsx':         DVC_QUOC_GIA,
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
    create_batch6_files()
