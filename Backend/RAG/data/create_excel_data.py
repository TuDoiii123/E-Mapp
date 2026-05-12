"""
Tạo các file Excel chứa dữ liệu Q&A thủ tục hành chính tỉnh Thanh Hóa.
Chạy: python Backend/RAG/data/create_excel_data.py
"""
import os
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).parent

# ── Cột chung cho tất cả sheet ────────────────────────────────────────────────
COLS = ['id', 'question', 'answer', 'category', 'procedure', 'source', 'level']

# =============================================================================
# 1. HỘ TỊCH
# =============================================================================
HO_TICH = [
    {
        'id': 'ht-001', 'category': 'ho_tich', 'procedure': 'khai_sinh', 'level': 'ward',
        'source': 'dichvucong.gov.vn; Luật Hộ tịch 2014',
        'question': 'Đăng ký khai sinh cần giấy tờ gì? Làm ở đâu? Mất bao lâu?',
        'answer': '''Đăng ký khai sinh thực hiện tại UBND xã/phường/thị trấn nơi cư trú của cha hoặc mẹ.
Thời gian xử lý: 3 ngày làm việc. Lệ phí: Miễn phí.
Thời hạn đăng ký: Trong vòng 60 ngày kể từ ngày sinh (quá hạn cần có xác nhận của UBND xã).

Hồ sơ gồm:
1. Tờ khai đăng ký khai sinh (Mẫu số 01 - theo Thông tư 04/2020/TT-BTP)
2. Giấy chứng sinh do bệnh viện/cơ sở y tế cấp (bản gốc)
3. CCCD/Căn cước công dân của cha hoặc mẹ (bản gốc để đối chiếu)
4. Giấy đăng ký kết hôn của cha mẹ (nếu đã kết hôn - bản chính)

Trường hợp chưa xác định được cha: chỉ cần Tờ khai + Giấy chứng sinh + CCCD mẹ.
Nộp trực tuyến: dichvucong.gov.vn hoặc dichvucong.thanhhoa.gov.vn.
Liên kết tra cứu: https://dichvucong.thanhhoa.gov.vn''',
    },
    {
        'id': 'ht-002', 'category': 'ho_tich', 'procedure': 'khai_sinh_qua_han', 'level': 'district',
        'source': 'Nghị định 123/2015/NĐ-CP',
        'question': 'Đăng ký khai sinh quá hạn (trễ hạn 60 ngày) thì làm thế nào?',
        'answer': '''Đăng ký khai sinh quá 60 ngày (đăng ký khai sinh quá hạn) thực hiện tại UBND cấp huyện.
Thời gian: 5 ngày làm việc. Lệ phí: Miễn phí.

Hồ sơ gồm:
1. Tờ khai đăng ký khai sinh (Mẫu 01)
2. Giấy chứng sinh hoặc giấy tờ thay thế (biên bản xác nhận của nhân chứng có UBND xã xác nhận)
3. CCCD của cha/mẹ
4. Văn bản cam đoan của cha/mẹ về các thông tin khai sinh
5. Xác nhận của UBND xã về việc chưa đăng ký khai sinh

Đặc biệt: Trẻ từ 14 tuổi trở lên tự mình nộp hồ sơ và ký tờ khai.
Căn cứ pháp lý: Điều 29 Luật Hộ tịch 2014; Điều 21 Nghị định 123/2015/NĐ-CP.''',
    },
    {
        'id': 'ht-003', 'category': 'ho_tich', 'procedure': 'ket_hon', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Luật HN&GĐ 2014',
        'question': 'Đăng ký kết hôn cần giấy tờ gì? Thủ tục ở đâu?',
        'answer': '''Đăng ký kết hôn tại UBND xã/phường nơi cư trú của một trong hai bên.
Thời gian: 5 ngày làm việc. Lệ phí: Miễn phí (từ 01/01/2021).
Độ tuổi: Nam ≥ 20 tuổi, Nữ ≥ 18 tuổi.

Hồ sơ (mỗi bên chuẩn bị):
1. Tờ khai đăng ký kết hôn (Mẫu số 02) — cả hai bên ký
2. CCCD/Căn cước công dân (bản gốc)
3. Giấy xác nhận tình trạng hôn nhân — UBND xã nơi thường trú cấp (không quá 6 tháng)
4. Giấy khai sinh (bản chính hoặc bản sao có công chứng)
5. 2 ảnh 4×6 cm (nền trắng, chụp trong 6 tháng gần nhất)

Trường hợp đã từng kết hôn: cần bản án ly hôn đã có hiệu lực pháp luật.
Người nước ngoài kết hôn với người Việt: hồ sơ nộp tại Sở Tư pháp.''',
    },
    {
        'id': 'ht-004', 'category': 'ho_tich', 'procedure': 'khai_tu', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP',
        'question': 'Đăng ký khai tử ở đâu? Cần giấy gì? Thời hạn là bao nhiêu?',
        'answer': '''Đăng ký khai tử tại UBND xã/phường nơi người chết cư trú hoặc nơi xảy ra cái chết.
Thời gian: 3 ngày làm việc. Lệ phí: Miễn phí.
Thời hạn: Trong vòng 15 ngày kể từ ngày chết (quá hạn nộp tại UBND huyện).

Hồ sơ:
1. Tờ khai đăng ký khai tử (Mẫu số 05)
2. Giấy báo tử do bệnh viện/cơ sở y tế cấp (bản gốc)
3. CCCD/Hộ chiếu của người đi khai tử
4. Giấy tờ tùy thân của người chết (nếu có — thu hồi)

Khi chết không có giấy báo tử: Cần văn bản xác nhận của công an xã hoặc quyết định của tòa án tuyên bố chết.
Sau khi được cấp Giấy chứng tử, gia đình tiến hành xóa tên khỏi CSDL dân cư.''',
    },
    {
        'id': 'ht-005', 'category': 'ho_tich', 'procedure': 'ly_hon', 'level': 'district',
        'source': 'Bộ luật Tố tụng dân sự 2015; Luật HN&GĐ 2014',
        'question': 'Thủ tục ly hôn thuận tình và ly hôn đơn phương khác nhau như thế nào?',
        'answer': '''Có hai hình thức ly hôn:

1. LY HÔN THUẬN TÌNH (hai bên đồng ý):
   - Nộp đơn tại TAND cấp huyện nơi một trong hai bên cư trú
   - Thời gian: 4–6 tháng (hoà giải → xét xử)
   - Lệ phí: 300.000 đồng (án phí hôn nhân gia đình)
   - Hồ sơ: Đơn xin ly hôn, Giấy đăng ký kết hôn, CCCD, Giấy khai sinh con (nếu có)
   - Phán quyết: Quyết định công nhận thuận tình ly hôn

2. LY HÔN ĐƠN PHƯƠNG (một bên yêu cầu):
   - Nộp đơn tại TAND nơi bị đơn cư trú
   - Thời gian: 6–18 tháng (phức tạp hơn, qua nhiều phiên hoà giải)
   - Lệ phí: 300.000 đồng, có thể thêm án phí nếu tranh chấp tài sản
   - Hồ sơ: Tương tự + Đơn khởi kiện ly hôn
   - Khi có con chưa thành niên, tòa quyết định ai nuôi con, mức cấp dưỡng

Sau khi có bản án ly hôn hiệu lực: Ghi chú vào Sổ hộ tịch tại UBND xã nơi đăng ký kết hôn.
Tòa án tỉnh Thanh Hóa: 06 Đinh Lễ, TP Thanh Hóa. Điện thoại: 0237.3852.271.''',
    },
    {
        'id': 'ht-006', 'category': 'ho_tich', 'procedure': 'nuoi_con_nuoi', 'level': 'district',
        'source': 'Luật Nuôi con nuôi 2010; Nghị định 19/2011/NĐ-CP',
        'question': 'Đăng ký nuôi con nuôi trong nước cần làm gì? Hồ sơ gồm những gì?',
        'answer': '''Đăng ký nuôi con nuôi trong nước tại UBND cấp xã nơi con nuôi hoặc cha mẹ nuôi thường trú.
Thời gian: 30 ngày làm việc. Lệ phí: 400.000 đồng.

Điều kiện người nhận nuôi: Có năng lực hành vi dân sự đầy đủ; hơn con nuôi từ 20 tuổi trở lên; có điều kiện sức khỏe, kinh tế, chỗ ở đảm bảo việc nuôi dưỡng.

Hồ sơ:
1. Đơn xin nhận con nuôi (Mẫu TP/CN-2014-ĐXNCN.1)
2. CCCD/Hộ chiếu của người xin nhận con nuôi
3. Phiếu lý lịch tư pháp (không quá 6 tháng)
4. Văn bản xác nhận tình trạng hôn nhân của người xin nhận con nuôi
5. Xác nhận về thu nhập, tài sản đảm bảo nuôi dưỡng
6. Giấy khai sinh của trẻ; Giấy xác nhận tình trạng sức khỏe của trẻ
7. Quyết định của Tòa án (nếu trẻ mồ côi không xác định được cha mẹ)

Sau khi UBND xã xem xét và tổ chức giao nhận con nuôi, cấp Giấy chứng nhận nuôi con nuôi.''',
    },
    {
        'id': 'ht-007', 'category': 'ho_tich', 'procedure': 'cai_chinh_ho_tich', 'level': 'ward',
        'source': 'Luật Hộ tịch 2014; Thông tư 04/2020/TT-BTP',
        'question': 'Thủ tục cải chính hộ tịch (sửa tên, ngày sinh) thực hiện như thế nào?',
        'answer': '''Cải chính hộ tịch để sửa những thông tin đã đăng ký sai trong giấy tờ hộ tịch (sai tên, ngày sinh, giới tính...).

Thẩm quyền:
- UBND xã nơi đã đăng ký: cải chính thông tin khai sinh, kết hôn, khai tử
- UBND huyện: các trường hợp phức tạp hoặc không xác định nơi đăng ký

Thời gian: 3 ngày làm việc (đơn giản) đến 15 ngày (phức tạp). Lệ phí: Miễn phí.

Hồ sơ:
1. Tờ khai thay đổi, cải chính hộ tịch (Mẫu 11)
2. Bản sao Giấy khai sinh/Giấy đăng ký kết hôn (có sai sót cần cải chính)
3. CCCD/Hộ chiếu của người yêu cầu
4. Giấy tờ chứng minh thông tin cần cải chính đúng (Bằng tốt nghiệp, hồ sơ học bạ, giấy tờ y tế...)

Lưu ý: Cải chính tên trong tất cả giấy tờ (CCCD, bằng lái xe, sổ BHXH...) phải thực hiện sau khi có Giấy khai sinh đã cải chính.''',
    },
    {
        'id': 'ht-008', 'category': 'ho_tich', 'procedure': 'ghi_chu_ket_hon_nuoc_ngoai', 'level': 'province',
        'source': 'Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP',
        'question': 'Công dân Việt Nam kết hôn ở nước ngoài cần làm gì khi về nước?',
        'answer': '''Công dân Việt Nam kết hôn ở nước ngoài phải thực hiện thủ tục "Ghi vào sổ hộ tịch việc kết hôn ở nước ngoài" khi về Việt Nam.

Nộp hồ sơ tại: Sở Tư pháp tỉnh Thanh Hóa (34 Đại lộ Lê Lợi, TP Thanh Hóa).
Thời gian: 10–15 ngày làm việc. Lệ phí: 300.000 đồng.

Hồ sơ:
1. Tờ khai ghi vào sổ hộ tịch việc kết hôn ở nước ngoài (Mẫu 09)
2. Bản sao Giấy đăng ký kết hôn do cơ quan có thẩm quyền nước ngoài cấp (có dịch thuật công chứng)
3. CCCD/Hộ chiếu của cả hai bên
4. Giấy khai sinh của cả hai bên

Sau khi ghi vào sổ, việc kết hôn mới được công nhận về mặt pháp lý tại Việt Nam.
Sở Tư pháp Thanh Hóa: 0237.3852.573 — stp@thanhhoa.gov.vn.''',
    },
]

# =============================================================================
# 2. ĐẤT ĐAI
# =============================================================================
DAT_DAI = [
    {
        'id': 'dd-001', 'category': 'dat_dai', 'procedure': 'cap_gcn_lan_dau', 'level': 'district',
        'source': 'Luật Đất đai 2024; Nghị định 43/2014/NĐ-CP',
        'question': 'Thủ tục cấp Giấy chứng nhận quyền sử dụng đất (sổ đỏ/sổ hồng) lần đầu cần gì?',
        'answer': '''Cấp Giấy chứng nhận quyền sử dụng đất lần đầu (sổ đỏ) tại Văn phòng Đăng ký đất đai cấp huyện hoặc Sở TNMT tỉnh.
Thời gian: 30 ngày làm việc (đất ở); có thể kéo dài nếu phải đo đạc.
Lệ phí: Theo quy định của HĐND tỉnh Thanh Hóa (thường 100.000–500.000 đồng tùy loại đất).

Hồ sơ:
1. Đơn đăng ký, cấp GCN (Mẫu 04a/ĐK)
2. Một trong các giấy tờ về quyền sử dụng đất theo Điều 100 Luật Đất đai (Quyết định giao đất, giấy tờ mua bán trước 15/10/1993, giấy tờ thừa kế đất...)
3. Giấy tờ về nguồn gốc đất (nếu cần xác minh)
4. Sơ đồ/bản đồ thửa đất (do Văn phòng ĐKDD lập hoặc đo đạc)
5. CCCD của người đứng tên

Nộp tại: Chi nhánh Văn phòng Đăng ký đất đai huyện/thị xã nơi có đất.
Sở TNMT Thanh Hóa: 33 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3752.262.''',
    },
    {
        'id': 'dd-002', 'category': 'dat_dai', 'procedure': 'chuyen_nhuong', 'level': 'district',
        'source': 'Luật Đất đai 2024; Nghị định 43/2014/NĐ-CP',
        'question': 'Thủ tục sang tên sổ đỏ (chuyển nhượng quyền sử dụng đất) cần giấy tờ gì?',
        'answer': '''Chuyển nhượng quyền sử dụng đất và đăng ký biến động (sang tên sổ đỏ) tại Văn phòng ĐKDD cấp huyện.
Thời gian: 10 ngày làm việc. Lệ phí trước bạ: 0,5% giá trị đất.

Bước 1: Công chứng hợp đồng chuyển nhượng tại Phòng/Văn phòng công chứng.
Hồ sơ công chứng:
  - Hợp đồng chuyển nhượng QSDĐ (ký cả hai bên có mặt tại văn phòng công chứng)
  - CCCD của bên bán và bên mua
  - GCN QSDĐ (sổ đỏ/sổ hồng gốc) của bên bán
  - Giấy đăng ký kết hôn/chứng nhận độc thân của bên bán (nếu đất thuộc sở hữu chung vợ chồng)

Bước 2: Đăng ký biến động tại Văn phòng ĐKDD:
  - Đơn đăng ký biến động (Mẫu 09/ĐK)
  - Hợp đồng chuyển nhượng đã công chứng
  - GCN QSDĐ gốc
  - CCCD bên mua
  - Tờ khai lệ phí trước bạ (kê khai online tại etax.gdt.gov.vn)
  - Biên lai đã nộp lệ phí trước bạ và thuế TNCN (2% giá chuyển nhượng của bên bán)

Tra cứu thửa đất online: https://bando.thanhhoa.gov.vn.''',
    },
    {
        'id': 'dd-003', 'category': 'dat_dai', 'procedure': 'tach_thua', 'level': 'district',
        'source': 'Luật Đất đai 2024; Nghị định 43/2014/NĐ-CP sửa đổi',
        'question': 'Thủ tục tách thửa đất (chia lô) cần điều kiện và hồ sơ gì?',
        'answer': '''Tách thửa đất tại Văn phòng Đăng ký đất đai cấp huyện nơi có đất.
Thời gian: 15 ngày làm việc. Lệ phí: Phí đo đạc (theo thực tế diện tích) + phí cấp GCN mới.

Điều kiện:
- Diện tích mỗi thửa sau khi tách phải đạt diện tích tối thiểu theo quy định của UBND tỉnh
- Tại Thanh Hóa: Đất ở đô thị tối thiểu 40m², đất ở nông thôn tối thiểu 60m² (theo QĐ của UBND tỉnh)
- Không vi phạm quy hoạch sử dụng đất

Hồ sơ:
1. Đơn xin tách thửa (Mẫu 11/ĐK)
2. GCN QSDĐ gốc
3. CCCD người sử dụng đất
4. Giấy đăng ký kết hôn (nếu đất đứng tên cả hai vợ chồng)

Quy trình: VPĐKDD tiếp nhận → đo đạc địa chính → lập hồ sơ → cấp GCN mới cho từng thửa.''',
    },
    {
        'id': 'dd-004', 'category': 'dat_dai', 'procedure': 'the_chap', 'level': 'district',
        'source': 'Bộ luật Dân sự 2015; Luật Đất đai 2024',
        'question': 'Thế chấp quyền sử dụng đất để vay ngân hàng cần làm gì?',
        'answer': '''Thế chấp QSDĐ tại tổ chức tín dụng (ngân hàng) và đăng ký giao dịch bảo đảm tại Văn phòng ĐKDD.
Thời gian: 3 ngày làm việc để đăng ký thế chấp. Lệ phí: 80.000 đồng/trường hợp.

Bước 1: Công chứng Hợp đồng thế chấp tại Phòng/Văn phòng công chứng:
- Hợp đồng thế chấp QSDĐ (ngân hàng soạn thảo)
- CCCD chủ sử dụng đất + người thế chấp (nếu khác nhau)
- GCN QSDĐ gốc

Bước 2: Đăng ký thế chấp tại Văn phòng ĐKDD:
- Đơn đăng ký thế chấp (Mẫu số 02 - Nghị định 102/2017/NĐ-CP)
- Hợp đồng thế chấp đã công chứng
- GCN QSDĐ gốc

Lưu ý: Khi tất toán khoản vay, phải làm thủ tục giải chấp (xóa đăng ký thế chấp) trước khi bán, tặng cho đất.''',
    },
    {
        'id': 'dd-005', 'category': 'dat_dai', 'procedure': 'cap_lai_gcn', 'level': 'district',
        'source': 'Luật Đất đai 2024; Thông tư 23/2014/TT-BTNMT',
        'question': 'Mất sổ đỏ thì làm thế nào? Thủ tục cấp lại sổ đỏ bị mất như thế nào?',
        'answer': '''Cấp lại GCN QSDĐ do mất, hỏng tại Văn phòng ĐKDD cấp huyện.
Thời gian: 20 ngày làm việc. Lệ phí: 100.000 đồng.

Bước 1: Đăng báo mất GCN trên báo địa phương (Báo Thanh Hóa hoặc báo tỉnh) ít nhất 2 số liên tiếp.

Bước 2: Nộp hồ sơ tại Văn phòng ĐKDD sau 30 ngày đăng báo:
1. Đơn đề nghị cấp lại GCN (Mẫu 10/ĐK)
2. CCCD người sử dụng đất
3. Tờ báo có đăng thông tin mất GCN (2 số)
4. Bản kê khai các giấy tờ tài sản liên quan (nếu có)

Trong thời gian chờ cấp lại, VPĐKDD thông báo trên phương tiện thông tin đại chúng để phòng ngừa gian lận.
Nếu sổ đỏ hư hỏng (rách, nhòe): Chỉ cần đơn đề nghị + GCN hư hỏng + CCCD.''',
    },
    {
        'id': 'dd-006', 'category': 'dat_dai', 'procedure': 'tang_cho_dat', 'level': 'district',
        'source': 'Luật Đất đai 2024; Bộ luật Dân sự 2015',
        'question': 'Thủ tục tặng cho quyền sử dụng đất (tặng đất cho con) cần gì?',
        'answer': '''Tặng cho QSDĐ (cha mẹ tặng đất cho con, anh em tặng nhau...) tại Văn phòng ĐKDD cấp huyện.
Thời gian: 10 ngày làm việc.
Lệ phí trước bạ: Miễn nếu tặng cho giữa cha, mẹ, vợ, chồng, con, anh chị em ruột, ông bà nội ngoại, cháu ruột. Nếu tặng cho người khác: 0,5% giá trị đất.

Bước 1: Công chứng Hợp đồng tặng cho tại Phòng/VPCC:
- Hợp đồng tặng cho QSDĐ (2 bản)
- CCCD cả bên tặng và bên nhận
- GCN QSDĐ gốc
- Giấy đăng ký kết hôn/chứng nhận độc thân bên tặng (nếu có)
- Giấy tờ chứng minh quan hệ gia đình (giấy khai sinh, sổ hộ khẩu cũ...)

Bước 2: Đăng ký biến động tại VPĐKDD:
- Đơn đăng ký biến động (Mẫu 09/ĐK)
- Hợp đồng tặng cho đã công chứng
- GCN QSDĐ gốc
- Tờ khai lệ phí trước bạ (kê khai tại Chi cục Thuế)''',
    },
]

# =============================================================================
# 3. CCCD, HỘ CHIẾU, CƯ TRÚ
# =============================================================================
CCCD_HO_CHIEU = [
    {
        'id': 'cc-001', 'category': 'cccd', 'procedure': 'cap_cccd', 'level': 'district',
        'source': 'Luật Căn cước 2023; Thông tư 17/2024/TT-BCA',
        'question': 'Làm thẻ căn cước (CCCD) mới ở đâu? Cần gì? Lệ phí bao nhiêu?',
        'answer': '''Cấp, đổi, cấp lại thẻ Căn cước tại Công an cấp xã (từ 01/07/2024 theo Luật Căn cước 2023) hoặc Phòng Cảnh sát QLHC về TTXH - Công an cấp huyện/tỉnh.

Tại Thanh Hóa: Công an các phường/xã/thị trấn hoặc Phòng PA06 - Công an tỉnh Thanh Hóa (4 Trần Phú, Hàm Rồng, TP Thanh Hóa), ĐT: 069.2587.018.

Lệ phí:
- Cấp lần đầu (từ đủ 14 tuổi): Miễn phí
- Đổi thẻ Căn cước (CCCD gắn chip → Căn cước): Miễn phí đến hết năm 2024
- Cấp lại do mất: 70.000 đồng
- Cấp đổi do hư hỏng: 50.000 đồng

Hồ sơ:
1. Tờ khai căn cước (CC02) — điền tại nơi nộp hồ sơ
2. Giấy khai sinh (nếu chưa có CCCD bao giờ)
3. Thẻ CCCD/CMND cũ (nếu đổi/cấp lại)

Thời gian trả: 7 ngày làm việc (trong tỉnh), 20 ngày (ngoài tỉnh).
Nhận tại nơi đăng ký hoặc đề nghị gửi bưu điện (phí ship do người dân chi trả).''',
    },
    {
        'id': 'cc-002', 'category': 'cccd', 'procedure': 'cap_ho_chieu', 'level': 'province',
        'source': 'Luật Xuất nhập cảnh 2019; Nghị định 136/2007/NĐ-CP',
        'question': 'Làm hộ chiếu (passport) phổ thông ở đâu? Hồ sơ gồm gì? Bao lâu có?',
        'answer': '''Cấp hộ chiếu phổ thông tại Phòng Quản lý xuất nhập cảnh - Công an tỉnh Thanh Hóa hoặc cổng dichvucong.gov.vn (online).

Địa chỉ: Phòng PA08 - Công an tỉnh Thanh Hóa, 4 Trần Phú, TP Thanh Hóa. ĐT: 069.2587.080.

Lệ phí:
- Hộ chiếu thông thường (10 năm): 200.000 đồng
- Hộ chiếu thông thường (5 năm, cho trẻ dưới 14 tuổi): 100.000 đồng
- Thêm phí dịch vụ nếu nộp qua cổng online: 20.000 đồng

Hồ sơ:
1. Tờ khai đề nghị cấp hộ chiếu (M1 — điền online hoặc tại nơi nộp)
2. CCCD/Căn cước công dân còn hiệu lực (bản gốc)
3. Bản sao Giấy khai sinh (nếu là trẻ dưới 14 tuổi)
4. Ảnh 4×6 cm, phông trắng (không cần nộp nếu lấy ảnh tại chỗ)

Thời gian:
- Thường (5–8 ngày làm việc): Nhận tại bưu điện hoặc đến lấy
- Nhanh (1–3 ngày): Phụ phí 200.000 đồng

Trẻ dưới 14 tuổi: Phải có mặt cha/mẹ khi nộp hồ sơ.''',
    },
    {
        'id': 'cc-003', 'category': 'cu_tru', 'procedure': 'dang_ky_thuong_tru', 'level': 'ward',
        'source': 'Luật Cư trú 2020; Nghị định 62/2021/NĐ-CP',
        'question': 'Đăng ký thường trú (nhập hộ khẩu) ở đâu? Cần điều kiện và giấy tờ gì?',
        'answer': '''Đăng ký thường trú (nhập hộ khẩu) tại Công an cấp xã/phường nơi muốn đăng ký.
Thời gian: 7 ngày làm việc. Lệ phí: Miễn phí.

Điều kiện: Có chỗ ở hợp pháp tại địa bàn đăng ký. Chỗ ở hợp pháp gồm:
- Nhà ở sở hữu (có sổ đỏ/sổ hồng)
- Thuê nhà ≥ 12 tháng có hợp đồng công chứng
- Được cho ở nhờ/mượn (có văn bản đồng ý của chủ hộ)

Hồ sơ:
1. Phiếu báo thay đổi hộ khẩu, nhân khẩu (CT01) — khai đầy đủ
2. CCCD (bản gốc)
3. Giấy tờ chứng minh chỗ ở hợp pháp: Sổ đỏ/Sổ hồng, Hợp đồng thuê nhà công chứng (12 tháng trở lên), hoặc văn bản đồng ý của chủ hộ
4. Giấy tờ quan hệ nhân thân với chủ hộ: Giấy khai sinh, Giấy đăng ký kết hôn
5. Văn bản đồng ý của chủ hộ (khi đăng ký vào hộ người khác)

Lưu ý: Từ 2021 không dùng Sổ hộ khẩu giấy. Thay bằng dữ liệu điện tử trên CSDL quốc gia về dân cư.''',
    },
    {
        'id': 'cc-004', 'category': 'cu_tru', 'procedure': 'dang_ky_tam_tru', 'level': 'ward',
        'source': 'Luật Cư trú 2020',
        'question': 'Đăng ký tạm trú khi thuê nhà ở tỉnh khác cần làm gì? Có bắt buộc không?',
        'answer': '''Đăng ký tạm trú bắt buộc khi lưu trú trên 30 ngày liên tục tại nơi không phải nơi thường trú.
Nộp hồ sơ tại: Công an xã/phường nơi tạm trú.
Thời gian: Ngay trong ngày. Lệ phí: Miễn phí.
Thời hạn tạm trú: 2 năm, có thể gia hạn tiếp.

Hồ sơ:
1. Phiếu báo thay đổi hộ khẩu, nhân khẩu (CT01)
2. CCCD (bản gốc)
3. Giấy tờ chứng minh chỗ ở tạm trú: Hợp đồng thuê nhà, hoặc văn bản đồng ý của chủ nhà/chủ hộ

Xử phạt nếu không đăng ký: Phạt tiền 500.000–1.000.000 đồng theo Nghị định 144/2021/NĐ-CP.

Người Nước ngoài lưu trú: Khách sạn/nhà trọ khai báo tạm trú hộ. Nếu ở nhà riêng/gia đình: tự khai báo tại Công an xã trong 12 giờ.''',
    },
]

# =============================================================================
# 4. GIAO THÔNG (GPLX, ĐĂNG KÝ XE)
# =============================================================================
GIAO_THONG = [
    {
        'id': 'gt-001', 'category': 'giao_thong', 'procedure': 'cap_gplx', 'level': 'province',
        'source': 'Thông tư 12/2017/TT-BGTVT; Nghị định 100/2019/NĐ-CP',
        'question': 'Thi bằng lái xe ô tô (hạng B1, B2) ở đâu? Quy trình và chi phí như thế nào?',
        'answer': '''Thi và cấp Giấy phép lái xe ô tô hạng B1, B2 tại Trường đào tạo lái xe được cấp phép.
Tại Thanh Hóa có nhiều trường: Trường Trung cấp GTVT Thanh Hóa, Trung tâm đào tạo lái xe Hùng Vương, ...

Hạng bằng lái xe ô tô:
- B1 (hạng 1): Xe ô tô không hành nghề lái xe (dưới 9 chỗ, xe tải ≤ 3,5 tấn). Không được cấp B2.
- B2 (hạng 2): Được lái tất cả xe hạng B1 và dùng để chở thuê/hành nghề.

Chi phí tham khảo (2024):
- Học phí B2: 7.000.000–10.000.000 đồng (40 giờ lý thuyết + 500 km thực hành trở lên)
- Lệ phí cấp bằng: 135.000 đồng (khi thi đỗ, cơ sở đào tạo nộp hộ)

Điều kiện: Đủ 18 tuổi (B1, B2), sức khỏe đủ điều kiện lái xe.

Quy trình: Đăng ký học → Học lý thuyết + lái xe cơ bản → Sát hạch (lý thuyết + thực hành Sa hình + Đường trường) → Nhận bằng sau 3–7 ngày.

Sở GTVT Thanh Hóa quản lý: 09 Đại lộ Hùng Vương, TP Thanh Hóa. ĐT: 0237.3850.397.''',
    },
    {
        'id': 'gt-002', 'category': 'giao_thong', 'procedure': 'doi_gplx', 'level': 'province',
        'source': 'Thông tư 12/2017/TT-BGTVT sửa đổi',
        'question': 'Đổi giấy phép lái xe (GPLX) khi hết hạn hoặc bị hỏng ở đâu?',
        'answer': '''Đổi Giấy phép lái xe tại Sở Giao thông Vận tải tỉnh Thanh Hóa hoặc online tại dichvucong.gov.vn.
Địa chỉ: 09 Đại lộ Hùng Vương, TP Thanh Hóa. Hotline: 0237.3850.397.

Thời hạn GPLX: Hạng A1, A2, A3, A4: Không thời hạn. Hạng B1: 10 năm. Hạng B2: 5 năm. Hạng C: 5 năm. Hạng D, E, F: 5 năm.

Lệ phí đổi GPLX: 135.000 đồng (xe máy) hoặc 200.000 đồng (ô tô).

Hồ sơ đổi GPLX hết hạn:
1. Đơn đề nghị đổi GPLX (Mẫu 3, TT12/2017)
2. GPLX cũ (bản gốc - thu hồi)
3. CCCD (bản gốc để đối chiếu)
4. Giấy khám sức khỏe lái xe (không quá 6 tháng - do cơ sở khám sức khỏe được Bộ Y tế công nhận cấp)
5. Ảnh 3×4 cm (nền trắng, chụp trong 6 tháng)

Hồ sơ đổi GPLX hỏng/mất: Tương tự + thêm Đơn khai báo mất (nếu mất) có xác nhận của Công an xã.
Thời gian: 3–5 ngày làm việc.''',
    },
    {
        'id': 'gt-003', 'category': 'giao_thong', 'procedure': 'dang_ky_xe', 'level': 'district',
        'source': 'Nghị định 10/2020/NĐ-CP; Thông tư 58/2020/TT-BCA',
        'question': 'Đăng ký xe máy mới mua ở đâu? Cần giấy tờ gì? Lệ phí bao nhiêu?',
        'answer': '''Đăng ký xe máy mua mới tại Công an cấp quận/huyện nơi chủ xe cư trú thường xuyên.
Tại TP Thanh Hóa: Công an TP Thanh Hóa, 04 Đại lộ Hùng Vương.

Lệ phí đăng ký xe máy:
- TP Thanh Hóa (đô thị loại I): 500.000 đồng/lần đầu
- Huyện, thị xã khác: 200.000 đồng
- Lệ phí biển số: Bốc biển thường 500.000 đồng; bốc biển đẹp: đấu giá

Hồ sơ:
1. Tờ khai đăng ký xe (1 bản)
2. Hóa đơn mua xe (bản gốc) và Phiếu xuất kho (nếu mua qua đại lý)
3. Giấy chứng nhận chất lượng an toàn kỹ thuật và bảo vệ môi trường (xuất xưởng)
4. CCCD của chủ xe
5. Tờ khai thuế lệ phí trước bạ (điền online tại etax.gdt.gov.vn, nộp trước ở Kho bạc/ngân hàng)
   - Lệ phí trước bạ xe máy: 2% giá tính lệ phí trước bạ do Bộ Tài chính quy định
6. Biên lai nộp lệ phí trước bạ

Thời gian: Ngay trong ngày (nếu hồ sơ đầy đủ). Nhận biển số và Giấy đăng ký xe.''',
    },
    {
        'id': 'gt-004', 'category': 'giao_thong', 'procedure': 'dang_kiem_xe', 'level': 'district',
        'source': 'Luật Giao thông đường bộ 2008; Thông tư 16/2021/TT-BGTVT',
        'question': 'Đăng kiểm ô tô ở đâu tại Thanh Hóa? Bao lâu đăng kiểm một lần?',
        'answer': '''Đăng kiểm phương tiện ô tô tại Trung tâm Đăng kiểm xe cơ giới (thuộc Cục Đăng kiểm Việt Nam).
Tại Thanh Hóa:
- Trung tâm Đăng kiểm 36-01D: Đường Trường Thi, TP Thanh Hóa
- Trung tâm Đăng kiểm 36-02D: Khu công nghiệp Lễ Môn, TP Thanh Hóa
- Và các trạm đăng kiểm tại Bỉm Sơn, Nghi Sơn...

Chu kỳ đăng kiểm ô tô:
- Xe ô tô con dưới 9 chỗ mới: 2 năm/lần đầu, sau đó 1 năm/lần (≤ 5 tuổi: 2 năm, 6–7 tuổi: 18 tháng, ≥ 8 tuổi: 12 tháng)
- Xe kinh doanh vận tải (taxi, xe khách): 6 tháng/lần
- Xe tải: 6 tháng hoặc 1 năm tùy tải trọng và tuổi xe

Lệ phí đăng kiểm: Khoảng 340.000–560.000 đồng tùy loại xe.

Hồ sơ mang theo:
1. Giấy đăng ký xe (bản gốc)
2. Giấy đăng kiểm còn hạn trước (nếu có)
3. Bảo hiểm trách nhiệm dân sự còn hiệu lực
4. CCCD chủ xe (đối chiếu)

Đặt lịch đăng kiểm online: dangkiem.gov.vn (ưu tiên đặt online, tránh xếp hàng).''',
    },
]

# =============================================================================
# 5. KINH DOANH, DOANH NGHIỆP
# =============================================================================
KINH_DOANH = [
    {
        'id': 'kd-001', 'category': 'kinh_doanh', 'procedure': 'dang_ky_ho_kinh_doanh', 'level': 'district',
        'source': 'Nghị định 01/2021/NĐ-CP; Luật Doanh nghiệp 2020',
        'question': 'Thủ tục đăng ký kinh doanh hộ cá thể (hộ kinh doanh) cần gì? Nộp ở đâu?',
        'answer': '''Đăng ký thành lập hộ kinh doanh tại Phòng Tài chính - Kế hoạch UBND cấp huyện.
Thời gian: 3 ngày làm việc. Lệ phí: 100.000 đồng.

Điều kiện:
- Chủ hộ kinh doanh là cá nhân từ đủ 18 tuổi, có năng lực pháp luật dân sự đầy đủ
- Không được kinh doanh nhiều hộ kinh doanh
- Không phải là chủ doanh nghiệp đang hoạt động

Hồ sơ:
1. Giấy đề nghị đăng ký hộ kinh doanh (Phụ lục III-1, NĐ 01/2021)
2. CCCD của chủ hộ kinh doanh (bản sao)
3. Bản sao hợp lệ biên bản họp thành lập (nếu có từ 2 cá nhân trở lên)
4. Giấy tờ chứng minh địa điểm kinh doanh hợp pháp (Hợp đồng thuê mặt bằng công chứng, hoặc giấy tờ sở hữu nhà)

Sau khi đăng ký thành công: Nhận Giấy chứng nhận đăng ký hộ kinh doanh → Đăng ký mã số thuế tại Chi cục Thuế → Mua hóa đơn hoặc sử dụng hóa đơn điện tử.

Phòng TC-KH UBND TP Thanh Hóa: 16 Lê Hoàn, TP Thanh Hóa. ĐT: 0237.3852.666.''',
    },
    {
        'id': 'kd-002', 'category': 'kinh_doanh', 'procedure': 'dang_ky_doanh_nghiep', 'level': 'province',
        'source': 'Luật Doanh nghiệp 2020; Nghị định 01/2021/NĐ-CP',
        'question': 'Thủ tục thành lập công ty TNHH/cổ phần cần gì? Nộp ở đâu?',
        'answer': '''Đăng ký thành lập doanh nghiệp tại Sở Kế hoạch và Đầu tư tỉnh Thanh Hóa (Phòng Đăng ký kinh doanh) hoặc qua Cổng đăng ký doanh nghiệp quốc gia: dangkykinhdoanh.gov.vn.
Thời gian: 3 ngày làm việc. Lệ phí: 50.000 đồng (nộp hồ sơ giấy) hoặc miễn phí (đăng ký online).

Hồ sơ Công ty TNHH một thành viên:
1. Giấy đề nghị đăng ký doanh nghiệp (Phụ lục I-1, NĐ01/2021)
2. Điều lệ công ty (NĐPL ký từng trang)
3. Bản sao CCCD/Hộ chiếu của người đại diện pháp luật
4. Giấy tờ ủy quyền cho người nộp hồ sơ (nếu không phải chủ sở hữu/NĐPL)

Hồ sơ Công ty TNHH hai thành viên trở lên:
- Thêm: Danh sách thành viên góp vốn + bản sao CCCD từng thành viên

Sau khi được cấp Giấy chứng nhận đăng ký doanh nghiệp:
1. Khắc con dấu và thông báo mẫu dấu (online)
2. Đăng ký tài khoản ngân hàng doanh nghiệp
3. Khai thuế ban đầu tại Cục/Chi cục Thuế
4. Đăng ký sử dụng hóa đơn điện tử

Sở KHĐT Thanh Hóa: 24 Hải Thượng Lãn Ông. ĐT: 0237.3852.349.''',
    },
    {
        'id': 'kd-003', 'category': 'kinh_doanh', 'procedure': 'giai_the_dn', 'level': 'province',
        'source': 'Luật Doanh nghiệp 2020; Nghị định 01/2021/NĐ-CP',
        'question': 'Thủ tục giải thể/đóng cửa doanh nghiệp như thế nào?',
        'answer': '''Giải thể doanh nghiệp tự nguyện thực hiện qua Cổng đăng ký doanh nghiệp quốc gia.

Điều kiện được giải thể:
- Đã thanh toán hết các khoản nợ, nghĩa vụ tài sản
- Không trong quá trình giải quyết tranh chấp tại tòa án/trọng tài
- Đã hoàn thành nghĩa vụ thuế (có xác nhận của cơ quan thuế)

Quy trình:
1. Hội đồng thành viên/Đại hội cổ đông ra quyết định giải thể
2. Thông báo quyết định giải thể tới tất cả chủ nợ, người có quyền lợi/nghĩa vụ liên quan
3. Thanh lý tài sản, trả nợ
4. Nộp hồ sơ giải thể tại Phòng ĐKKD - Sở KHĐT:
   - Thông báo giải thể DN
   - Quyết định giải thể
   - Biên bản thanh lý hợp đồng
   - Xác nhận hoàn thành nghĩa vụ thuế của cơ quan thuế
   - Xác nhận đã nộp lại con dấu (nếu có)
5. Sở KHĐT đăng thông tin giải thể lên Cổng thông tin quốc gia — Doanh nghiệp chấm dứt tồn tại.

Thời gian: 5 ngày làm việc (sau khi có đủ hồ sơ hợp lệ).''',
    },
]

# =============================================================================
# 6. BẢO HIỂM XÃ HỘI, Y TẾ
# =============================================================================
BHXH = [
    {
        'id': 'bh-001', 'category': 'bhxh', 'procedure': 'tham_gia_bhxh_tu_nguyen', 'level': 'district',
        'source': 'Luật BHXH 2014; Nghị định 134/2015/NĐ-CP',
        'question': 'Tham gia bảo hiểm xã hội tự nguyện (để hưởng lương hưu) cần làm gì?',
        'answer': '''BHXH tự nguyện dành cho lao động tự do, hộ kinh doanh, nông dân... không có HĐLĐ.
Đăng ký tại BHXH cấp huyện hoặc đại lý thu BHXH tự nguyện (bưu điện, điểm dịch vụ).

Mức đóng BHXH tự nguyện năm 2024:
- Tối thiểu: 22% × mức lương cơ sở (từ 01/7/2024: lương cơ sở 2.340.000 đồng) = 514.800 đồng/tháng
- Tối đa: 22% × 20 lần lương cơ sở = 10.296.000 đồng/tháng
- Người dân chọn mức đóng và phương thức đóng (hàng tháng/quý/6 tháng/năm)

Hỗ trợ từ Nhà nước (theo Nghị định 134/2015):
- Hộ nghèo: được hỗ trợ 30% mức đóng tối thiểu
- Hộ cận nghèo: 25%
- Các đối tượng khác: 10%

Hồ sơ:
1. Tờ khai đăng ký tham gia BHXH tự nguyện (TK1-TS)
2. CCCD/Căn cước công dân

Điều kiện hưởng lương hưu: Đủ tuổi nghỉ hưu (Nam 62, Nữ 60 tuổi trong năm 2028 trở đi) VÀ đóng BHXH đủ 20 năm.
BHXH Thanh Hóa: 103 Đại lộ Lê Lợi. ĐT: 0237.3852.268.''',
    },
    {
        'id': 'bh-002', 'category': 'bhxh', 'procedure': 'huong_bhxh_mot_lan', 'level': 'district',
        'source': 'Luật BHXH 2014; Nghị quyết 93/2015/QH13',
        'question': 'Rút BHXH một lần được không? Điều kiện và thủ tục như thế nào?',
        'answer': '''Hưởng BHXH một lần được thực hiện tại BHXH cấp huyện nơi cư trú.

Điều kiện được rút BHXH 1 lần:
- Đủ tuổi nghỉ hưu mà chưa đủ 20 năm đóng BHXH
- Ra nước ngoài định cư
- Mắc bệnh hiểm nghèo (ung thư, bại liệt, phong, tâm thần nặng...)
- Không còn đóng BHXH và không tiếp tục đóng (sau 01 năm nghỉ việc)

Mức hưởng: 1,5 tháng lương bình quân/năm đóng (cho những năm đóng BHXH trước 2014); 2 tháng/năm (từ 2014 trở đi).

Hồ sơ:
1. Đơn đề nghị hưởng BHXH một lần (Mẫu 14-HSB)
2. Sổ BHXH (bản gốc)
3. CCCD (bản sao)
4. Tài khoản ngân hàng cá nhân (số tài khoản đứng tên người yêu cầu)
5. Quyết định chấm dứt HĐLĐ hoặc xác nhận của đơn vị

Lưu ý quan trọng: Rút BHXH một lần sẽ mất đi quyền hưởng lương hưu hàng tháng sau này. Nên cân nhắc kỹ.
Thời gian giải quyết: 10 ngày làm việc.''',
    },
    {
        'id': 'bh-003', 'category': 'bhyt', 'procedure': 'cap_the_bhyt_ho_gia_dinh', 'level': 'ward',
        'source': 'Luật BHYT 2014 sửa đổi 2023; Nghị định 146/2018/NĐ-CP',
        'question': 'Mua thẻ bảo hiểm y tế hộ gia đình ở đâu? Mức đóng bao nhiêu?',
        'answer': '''Mua thẻ BHYT hộ gia đình tại: Cơ quan BHXH quận/huyện, Bưu điện, hoặc Đại lý thu BHYT được ủy quyền.

Mức đóng BHYT hộ gia đình (từ 01/7/2023 - cơ sở lương 1.800.000 đồng):
- Người thứ 1: 4,5% × 1.800.000 = 81.000 đồng/tháng = 972.000 đồng/năm
- Người thứ 2 giảm 30%: 56.700 đồng/tháng
- Người thứ 3 giảm 40%: 48.600 đồng/tháng
- Người thứ 4 trở đi giảm 50%: 40.500 đồng/tháng

(Lưu ý: Từ 01/7/2024 lương cơ sở tăng lên 2.340.000 đồng, mức đóng sẽ tăng tương ứng 30%)

Hồ sơ:
1. Tờ khai tham gia BHYT (TK1-TS)
2. CCCD/Căn cước của từng thành viên
3. Giấy khai sinh của trẻ em chưa có CCCD

Quyền lợi hưởng: 80% chi phí khám chữa bệnh đúng tuyến; 40% nếu trái tuyến tỉnh; 70% nếu trái tuyến huyện.
Người nghèo, trẻ em dưới 6 tuổi, người có công: Nhà nước đóng thay.''',
    },
]

# =============================================================================
# 7. THUẾ
# =============================================================================
THUE = [
    {
        'id': 'th-001', 'category': 'thue', 'procedure': 'dang_ky_mst_ca_nhan', 'level': 'district',
        'source': 'Luật Quản lý thuế 2019; Thông tư 105/2020/TT-BTC',
        'question': 'Đăng ký mã số thuế cá nhân ở đâu? Cần giấy gì? Dùng để làm gì?',
        'answer': '''Mã số thuế (MST) cá nhân dùng để kê khai, nộp thuế thu nhập cá nhân, lệ phí trước bạ, thuế chuyển nhượng bất động sản...

Đăng ký MST cá nhân tại: Chi cục Thuế cấp huyện nơi cư trú hoặc online tại thuedientu.gdt.gov.vn.
Thời gian: 3 ngày làm việc. Lệ phí: Miễn phí.

Hồ sơ:
1. Tờ khai đăng ký thuế (Mẫu 05-ĐK-TCT)
2. CCCD (bản sao)
3. Giấy tờ chứng minh thu nhập (nếu có — không bắt buộc khi đăng ký lần đầu)

Lưu ý: Từ 2022, Tổng cục Thuế đã cấp MST tự động cho mọi công dân Việt Nam dựa trên số CCCD. Bạn có thể kiểm tra MST của mình tại: https://tracuunnt.gdt.gov.vn.

MST doanh nghiệp: Tự động cấp khi đăng ký kinh doanh (trùng với Mã số doanh nghiệp trên Giấy chứng nhận ĐKKD).
Cục Thuế Thanh Hóa: 27A Đại lộ Lê Lợi. ĐT: 0237.3850.068.''',
    },
    {
        'id': 'th-002', 'category': 'thue', 'procedure': 'quyet_toan_thue_tncn', 'level': 'province',
        'source': 'Luật Thuế TNCN 2007 sửa đổi; Thông tư 80/2021/TT-BTC',
        'question': 'Quyết toán thuế thu nhập cá nhân (hoàn thuế) làm như thế nào?',
        'answer': '''Quyết toán thuế TNCN để được hoàn thuế nếu đã nộp thừa trong năm (thường gặp với người làm nhiều nơi).

Thời hạn quyết toán: Trước ngày 30/4 năm sau (cá nhân tự quyết toán). Công ty quyết toán hộ: trước 31/3.

Thực hiện online tại: thuedientu.gdt.gov.vn (ĐĂNG NHẬP bằng MST cá nhân + mật khẩu).

Điều kiện được tự quyết toán:
- Có thu nhập từ 2 nơi trở lên trong năm
- Có giảm trừ gia cảnh cho người phụ thuộc chưa được cập nhật
- Có thu nhập vãng lai không do nơi làm tính thuế

Hồ sơ (nộp online):
1. Tờ khai quyết toán thuế TNCN (Mẫu 02/QTT-TNCN)
2. Phụ lục bảng kê thu nhập từ tiền lương (Mẫu 02-1/BK-QTT-TNCN)
3. Chứng từ khấu trừ thuế do nơi làm cấp
4. Hóa đơn giảm trừ (bảo hiểm nhân thọ, quỹ hưu trí tự nguyện...)

Hoàn thuế: Nếu được hoàn, cơ quan thuế chuyển vào tài khoản ngân hàng trong 6–15 ngày.''',
    },
    {
        'id': 'th-003', 'category': 'thue', 'procedure': 'thue_truoc_ba', 'level': 'district',
        'source': 'Luật Lệ phí trước bạ 2019; Nghị định 10/2022/NĐ-CP',
        'question': 'Lệ phí trước bạ khi mua nhà đất là bao nhiêu? Nộp ở đâu?',
        'answer': '''Lệ phí trước bạ khi đăng ký quyền sở hữu/sử dụng tài sản:

Lệ phí trước bạ NHÀ ĐẤT:
- Đất: 0,5% × Giá đất (theo Bảng giá đất của UBND tỉnh Thanh Hóa)
- Nhà: 0,5% × Giá trị nhà (theo đơn giá xây dựng của tỉnh)
- Miễn lệ phí: Nhà đất tặng cho giữa cha/mẹ/vợ/chồng/con/anh chị em ruột/ông bà nội ngoại/cháu ruột

Lệ phí trước bạ XE CƠ GIỚI:
- Xe ô tô con mới lần đầu: 10–12% (TP Thanh Hóa) hoặc 5–7% (huyện, tùy loại xe)
- Xe máy: 2% giá tính lệ phí trước bạ
- Xe máy điện: 1%

Kê khai và nộp lệ phí trước bạ:
1. Kê khai online tại etax.gdt.gov.vn (chọn "Lệ phí trước bạ")
2. In tờ khai → nộp tiền tại Kho bạc Nhà nước hoặc ngân hàng liên kết
3. Mang biên lai nộp tiền kèm hồ sơ đến Văn phòng ĐKDD hoặc Công an (đăng ký xe)

Chi cục Thuế cấp huyện hỗ trợ kê khai trực tiếp nếu không thực hiện được online.''',
    },
]

# =============================================================================
# 8. XÂY DỰNG
# =============================================================================
XAY_DUNG = [
    {
        'id': 'xd-001', 'category': 'xay_dung', 'procedure': 'cap_phep_xay_dung_nha_o', 'level': 'district',
        'source': 'Luật Xây dựng 2014 sửa đổi 2020; Nghị định 15/2021/NĐ-CP',
        'question': 'Thủ tục xin giấy phép xây dựng nhà ở riêng lẻ cần gì? Thời gian bao lâu?',
        'answer': '''Cấp phép xây dựng nhà ở riêng lẻ tại UBND cấp huyện (Phòng Quản lý đô thị/Kinh tế hạ tầng).
Thời gian: 15 ngày làm việc. Lệ phí: Khoảng 100.000–300.000 đồng (theo quy định tỉnh).

Trường hợp miễn phép xây dựng: Sửa chữa, cải tạo không thay đổi kết cấu chịu lực, không thay đổi kiến trúc mặt ngoài; công trình xây dựng ở nông thôn (làng, xã, thị trấn) theo quy định.

Hồ sơ:
1. Đơn đề nghị cấp GPXD (Mẫu số 01, Phụ lục II NĐ 15/2021)
2. GCN QSDĐ (bản sao công chứng) hoặc giấy tờ hợp lệ về đất
3. Bản vẽ thiết kế kỹ thuật (2 bộ):
   - Mặt bằng, mặt đứng, mặt cắt tỷ lệ 1:50 hoặc 1:100
   - Sơ đồ vị trí khu đất tỷ lệ 1:500 hoặc 1:2000
   - Bản vẽ móng, kết cấu (nếu ≥ 3 tầng hoặc chiều cao ≥ 12m)
4. Giấy ủy quyền (nếu người nộp không phải chủ đầu tư)

Sau khi có GPXD: Phải khởi công trong 12 tháng và hoàn công trong thời hạn ghi trong giấy phép.
Sở Xây dựng Thanh Hóa: 22 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.601.''',
    },
    {
        'id': 'xd-002', 'category': 'xay_dung', 'procedure': 'hoan_cong', 'level': 'district',
        'source': 'Luật Xây dựng 2014 sửa đổi 2020',
        'question': 'Thủ tục hoàn công nhà ở (nghiệm thu công trình) sau khi xây xong cần làm gì?',
        'answer': '''Thủ tục hoàn công nhà ở sau khi xây dựng hoàn thành để được ghi nhận vào hồ sơ đất đai.
Nộp tại: UBND cấp huyện (Phòng QL Đô thị/Kinh tế hạ tầng) hoặc Văn phòng ĐKDD.
Thời gian: 15–30 ngày. Lệ phí: Phí thẩm định theo quy định.

Điều kiện:
- Xây dựng đúng giấy phép được cấp (về vị trí, diện tích, số tầng, chiều cao)
- Đã có đủ hệ thống phòng cháy, thoát nước (đối với nhà ≥ 5 tầng)

Hồ sơ:
1. Đơn đề nghị kiểm tra công nhận hoàn thành công trình
2. Giấy phép xây dựng đã được cấp (bản gốc)
3. Bản vẽ hoàn công (as-built drawing) — đối chiếu với bản vẽ thiết kế
4. Biên bản nghiệm thu hoàn thành từng giai đoạn (móng, kết cấu thô, hoàn thiện)
5. GCN QSDĐ (bản sao công chứng)
6. Biên bản kiểm tra PCCC (đối với nhà ≥ 5 tầng hoặc diện tích sàn ≥ 300m²)

Sau khi hoàn công: Diện tích nhà được cập nhật vào Giấy chứng nhận QSDĐ và quyền sở hữu nhà.''',
    },
]

# =============================================================================
# HỎI ĐÁP CHUNG VỀ CÁC DỊCH VỤ THANH HÓA
# =============================================================================
CHUNG = [
    {
        'id': 'ch-001', 'category': 'chung', 'procedure': 'cong_dan_so', 'level': 'province',
        'source': 'dichvucong.thanhhoa.gov.vn',
        'question': 'Cổng dịch vụ công trực tuyến tỉnh Thanh Hóa ở đâu? Có thể nộp hồ sơ online không?',
        'answer': '''Cổng Dịch vụ công trực tuyến tỉnh Thanh Hóa: https://dichvucong.thanhhoa.gov.vn
Cổng Dịch vụ công Quốc gia: https://dichvucong.gov.vn

Trung tâm Phục vụ Hành chính công tỉnh Thanh Hóa:
- Địa chỉ: 25A Đại lộ Lê Lợi, phường Ba Đình, TP Thanh Hóa
- Điện thoại: 0237.3753.888
- Giờ làm việc: Thứ 2–6: 7:00–17:30; Thứ 7: 7:30–12:00

Hiện có thể nộp hồ sơ 100% trực tuyến mức độ 4 (nộp, theo dõi, nhận kết quả online) cho hơn 1.800 thủ tục tại Thanh Hóa.

Hỗ trợ người dân: Trung tâm Phục vụ Hành chính công có bộ phận hỗ trợ số hóa, giúp scan và nộp hồ sơ trực tuyến tại chỗ (miễn phí).

App di động: Tải "Dịch vụ công Thanh Hóa" trên App Store/CH Play để tra cứu, theo dõi hồ sơ.''',
    },
    {
        'id': 'ch-002', 'category': 'chung', 'procedure': 'tra_cuu_ho_so', 'level': 'province',
        'source': 'dichvucong.thanhhoa.gov.vn',
        'question': 'Làm sao tra cứu tiến độ hồ sơ đã nộp? Biết hồ sơ đang ở bước nào?',
        'answer': '''Tra cứu tiến độ hồ sơ tại:
1. Cổng DVC Thanh Hóa: https://dichvucong.thanhhoa.gov.vn → Mục "Tra cứu hồ sơ" → Nhập Số biên nhận
2. Cổng DVC Quốc gia: https://dichvucong.gov.vn → "Tra cứu hồ sơ"
3. Gọi điện: Bộ phận một cửa nơi nộp hồ sơ
4. App "Dịch vụ công Thanh Hóa"

Thông báo tự động: Hệ thống gửi SMS/email khi hồ sơ được tiếp nhận, đang xử lý, hoặc có kết quả.

Nếu hồ sơ quá hạn giải quyết: Phản ánh qua:
- Đường dây nóng Trung tâm PVHCC: 0237.3753.888
- Cổng phản ánh kiến nghị Thanh Hóa: https://pakn.thanhhoa.gov.vn
- Ứng dụng 1022 Thanh Hóa (phản ánh, kiến nghị của người dân)''',
    },
    {
        'id': 'ch-003', 'category': 'chung', 'procedure': 'co_quan_thanh_hoa', 'level': 'province',
        'source': 'Cổng thông tin tỉnh Thanh Hóa',
        'question': 'Danh sách số điện thoại các cơ quan hành chính quan trọng tại Thanh Hóa?',
        'answer': '''Các cơ quan hành chính tỉnh Thanh Hóa:

SỞ, BAN, NGÀNH TỈNH:
- UBND tỉnh Thanh Hóa: 0237.3852.428 — ubnd@thanhhoa.gov.vn
- Trung tâm PVHCC: 0237.3753.888 — 25A Đại lộ Lê Lợi, phường Ba Đình
- Sở Tư pháp: 0237.3852.573 — stp@thanhhoa.gov.vn
- Sở TNMT: 0237.3752.262 — stnmt@thanhhoa.gov.vn
- Sở GTVT: 0237.3850.397 — sgtvt@thanhhoa.gov.vn
- Sở Xây dựng: 0237.3852.601 — sxd@thanhhoa.gov.vn
- Sở KHĐT: 0237.3852.349 — skhdt@thanhhoa.gov.vn
- Cục Thuế: 0237.3850.068 — thanhhoa.gdt.gov.vn
- BHXH tỉnh: 0237.3852.268 — bhxhthanhhoa@vss.gov.vn
- Công an tỉnh (PA06 - CCCD): 069.2587.018
- Công an tỉnh (PA08 - Hộ chiếu): 069.2587.080

ĐƯỜNG DÂY NÓNG:
- Cải cách hành chính: 0237.3851.888
- Tiếp nhận phản ánh kiến nghị: 1800.1166 (miễn phí)
- Phòng cháy chữa cháy: 114
- Cấp cứu: 115 | Công an: 113 | Cảnh sát biển: 1800.599.907''',
    },
    {
        'id': 'ch-004', 'category': 'chung', 'procedure': 'phi_dich_vu', 'level': 'province',
        'source': 'Luật Phí và Lệ phí 2015; Nghị quyết HĐND tỉnh Thanh Hóa',
        'question': 'Những thủ tục hành chính nào được miễn phí tại tỉnh Thanh Hóa?',
        'answer': '''Tại Thanh Hóa, các thủ tục sau đây MIỄN PHÍ (lệ phí = 0 đồng):

HỘ TỊCH (miễn phí hoàn toàn từ 01/01/2021):
- Đăng ký khai sinh, khai tử, kết hôn, nhận con nuôi, thay đổi hộ tịch
- Xác nhận tình trạng hôn nhân, cải chính hộ tịch

CƯ TRÚ:
- Đăng ký thường trú, tạm trú, xóa đăng ký thường trú
- Cấp phiếu thông tin cư trú

CCCD / CĂN CƯỚC:
- Cấp thẻ căn cước lần đầu
- Đổi thẻ CCCD sang thẻ Căn cước (trong năm 2024)

Y TẾ:
- Khám bệnh cho trẻ em dưới 6 tuổi (đã có BHYT miễn phí)
- Khám chữa bệnh cho người nghèo, cận nghèo (Nhà nước trả qua BHYT)

ĐẤT ĐAI (miễn lệ phí trước bạ):
- Tặng cho giữa cha mẹ - con, vợ chồng, anh chị em ruột, ông bà - cháu ruột

GIÁO DỤC:
- Đăng ký nhập học mầm non, tiểu học trường công lập
- Cấp bản sao văn bằng chứng chỉ từ sổ gốc

Các thủ tục khác: Xem tại cổng dichvucong.thanhhoa.gov.vn mục "Tìm kiếm TTHC" → xem chi tiết lệ phí.''',
    },
]


def create_all_excel_files():
    os.makedirs(OUT_DIR, exist_ok=True)

    datasets = {
        'faq_ho_tich.xlsx':       HO_TICH,
        'faq_dat_dai.xlsx':       DAT_DAI,
        'faq_cccd_cu_tru.xlsx':   CCCD_HO_CHIEU,
        'faq_giao_thong.xlsx':    GIAO_THONG,
        'faq_kinh_doanh.xlsx':    KINH_DOANH,
        'faq_bhxh_bhyt.xlsx':     BHXH,
        'faq_thue.xlsx':          THUE,
        'faq_xay_dung.xlsx':      XAY_DUNG,
        'faq_chung.xlsx':         CHUNG,
    }

    for filename, rows in datasets.items():
        df = pd.DataFrame(rows, columns=COLS)
        path = OUT_DIR / filename
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='FAQ')
            ws = writer.sheets['FAQ']
            # Điều chỉnh độ rộng cột
            for col_cells in ws.columns:
                max_len = max(len(str(c.value or '')) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 80)
        print(f'  + {filename} ({len(rows)} ban ghi)')

    print(f'\nDa tao {len(datasets)} file Excel tai: {OUT_DIR}')


if __name__ == '__main__':
    create_all_excel_files()
