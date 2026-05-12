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


# =============================================================================
# 9. TƯ PHÁP — CÔNG CHỨNG, CHỨNG THỰC, LÝ LỊCH TƯ PHÁP
# =============================================================================
TU_PHAP = [
    {
        'id': 'tp-001', 'category': 'tu_phap', 'procedure': 'cong_chung', 'level': 'district',
        'source': 'Luật Công chứng 2014; Nghị định 29/2015/NĐ-CP',
        'question': 'Công chứng hợp đồng ở đâu? Khác gì với chứng thực? Phí công chứng là bao nhiêu?',
        'answer': '''Công chứng là việc công chứng viên xác nhận tính xác thực, hợp pháp của hợp đồng, giao dịch.
Chứng thực là xác nhận bản sao đúng với bản gốc, chữ ký đúng là của người yêu cầu — do UBND xã thực hiện.

TẠI THANH HÓA, các Phòng/Văn phòng công chứng:
- Phòng Công chứng số 1: 01 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.076
- Phòng Công chứng số 2: 69 Quang Trung, TP Thanh Hóa. ĐT: 0237.3760.123
- Và hơn 20 Văn phòng công chứng tư nhân trên toàn tỉnh

PHÍ CÔNG CHỨNG (theo Thông tư 257/2016/TT-BTC):
- Hợp đồng chuyển nhượng BĐS ≤ 50 triệu: 50.000 đ; 50–100 triệu: 100.000 đ
- 100–300 triệu: 0,1% giá trị; 300–1 tỷ: 0,08%; trên 1 tỷ: 0,06% (tối đa 70 triệu đ/HĐ)
- Hợp đồng tặng cho, thế chấp, vay vốn: áp dụng biểu phí riêng

Hồ sơ công chứng hợp đồng chuyển nhượng BĐS:
1. CCCD của các bên (bản gốc)
2. Giấy CN QSDĐ/QSHNƠ (bản gốc)
3. Giấy đăng ký kết hôn/chứng nhận độc thân của bên bán
4. Hợp đồng (công chứng viên có thể soạn thảo, hoặc các bên mang mẫu có sẵn)''',
    },
    {
        'id': 'tp-002', 'category': 'tu_phap', 'procedure': 'ly_lich_tu_phap', 'level': 'province',
        'source': 'Luật Lý lịch tư pháp 2009; Thông tư 13/2011/TT-BTP',
        'question': 'Xin phiếu lý lịch tư pháp (phiếu không có án tích) ở đâu? Mất bao lâu?',
        'answer': '''Cấp Phiếu lý lịch tư pháp tại Sở Tư pháp tỉnh Thanh Hóa hoặc online tại dichvucong.gov.vn.
Địa chỉ: 34 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.573.

Có 2 loại phiếu:
- Phiếu số 1: Cá nhân xin để dùng cho bản thân (ghi đầy đủ thông tin án tích nếu có)
- Phiếu số 2: Cơ quan, tổ chức xin về một cá nhân (chỉ ghi án tích chưa được xóa)

Thời gian: 10 ngày làm việc (trong tỉnh); 15 ngày (ngoài tỉnh/nước ngoài).
Lệ phí: 200.000 đồng/phiếu.

Hồ sơ xin Phiếu số 1:
1. Tờ khai yêu cầu cấp phiếu LLTP (Mẫu 03/2013/TT-BTP)
2. CCCD (bản sao)
3. Ủy quyền công chứng (nếu nhờ người khác nộp hộ)

Dùng phiếu LLTP khi nào: Xin việc vào các cơ quan Nhà nước, đăng ký kinh doanh (ngành nghề có điều kiện), du học, định cư nước ngoài, làm hộ chiếu phổ thông lần đầu (trường hợp cụ thể).

Nộp online: dichvucong.gov.vn → "Cấp phiếu lý lịch tư pháp" → Nhận kết quả bưu điện.''',
    },
    {
        'id': 'tp-003', 'category': 'tu_phap', 'procedure': 'quoc_tich', 'level': 'province',
        'source': 'Luật Quốc tịch Việt Nam 2008 sửa đổi 2014',
        'question': 'Thủ tục xin thôi quốc tịch Việt Nam hoặc xin nhập quốc tịch Việt Nam cần gì?',
        'answer': '''Thủ tục quốc tịch giải quyết tại Sở Tư pháp tỉnh (tiếp nhận hồ sơ) → trình Chủ tịch nước phê duyệt.

1. XIN THÔI QUỐC TỊCH VIỆT NAM:
   Điều kiện: Đã có quốc tịch nước ngoài hoặc được bảo lãnh nhận quốc tịch nước ngoài.
   Hồ sơ:
   - Đơn xin thôi quốc tịch (theo mẫu)
   - Hộ chiếu Việt Nam + CCCD
   - Giấy tờ chứng minh có/sẽ có quốc tịch nước ngoài
   - Phiếu LLTP số 2 (không quá 90 ngày)
   - Bản kê khai các giấy tờ, tài liệu liên quan
   Thời gian: 6–12 tháng (qua Bộ Tư pháp → Chủ tịch nước).

2. XIN NHẬP QUỐC TỊCH VIỆT NAM (người nước ngoài):
   Điều kiện: Cư trú hợp pháp tại VN ≥ 5 năm liên tục; biết tiếng Việt đủ giao tiếp; tự nguyện.
   Hồ sơ: Đơn xin nhập quốc tịch + Hộ chiếu nước ngoài + Giấy phép cư trú + Phiếu LLTP.
   Thời gian: 12–18 tháng.

Lệ phí: Theo quy định (dao động 1.000.000–3.000.000 đồng tùy loại).
Sở Tư pháp Thanh Hóa: stp@thanhhoa.gov.vn.''',
    },
    {
        'id': 'tp-004', 'category': 'tu_phap', 'procedure': 'boi_thuong_nha_nuoc', 'level': 'province',
        'source': 'Luật Trách nhiệm bồi thường của Nhà nước 2017',
        'question': 'Khi bị cơ quan nhà nước gây thiệt hại (oan sai, hành chính sai), tôi có được bồi thường không?',
        'answer': '''Người dân bị thiệt hại do hành vi trái pháp luật của cán bộ, công chức Nhà nước có quyền yêu cầu bồi thường theo Luật TNBTNN 2017.

CÁC TRƯỜNG HỢP ĐƯỢC BỒI THƯỜNG:
- Oan sai trong tố tụng hình sự (bị bắt giam oan, xét xử oan)
- Quyết định hành chính trái pháp luật gây thiệt hại (thu hồi đất sai, xử phạt sai...)
- Hành vi hành chính trái pháp luật (cán bộ gây thiệt hại khi thi hành công vụ)
- Thi hành án dân sự sai

TRÌNH TỰ YÊU CẦU BỒI THƯỜNG:
1. Nộp Đơn yêu cầu bồi thường đến cơ quan có trách nhiệm bồi thường (cơ quan đã ra quyết định sai)
2. Cơ quan đó phải giải quyết trong 45 ngày (phức tạp: 60 ngày), có thể gia hạn 1 lần
3. Nếu không thỏa thuận được: Khởi kiện ra TAND có thẩm quyền
4. Tòa án giải quyết theo thủ tục tố tụng dân sự

THIỆT HẠI ĐƯỢC BỒI THƯỜNG: Thiệt hại về vật chất (tài sản, thu nhập bị mất), tổn thất tinh thần, chi phí phục hồi danh dự.

Hỗ trợ: Sở Tư pháp Thanh Hóa hướng dẫn thủ tục. ĐT: 0237.3852.573.''',
    },
    {
        'id': 'tp-005', 'category': 'tu_phap', 'procedure': 'thua_ke', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Luật Công chứng 2014',
        'question': 'Thủ tục khai nhận thừa kế (di sản đất đai, nhà ở) cần giấy tờ gì?',
        'answer': '''Khai nhận di sản thừa kế (đất, nhà) thực hiện tại Văn phòng/Phòng Công chứng.
Sau đó đăng ký biến động tại Văn phòng Đăng ký đất đai.

THỪA KẾ THEO DI CHÚC:
Hồ sơ công chứng văn bản khai nhận thừa kế:
1. Di chúc hợp pháp (bản gốc, đã được công chứng hoặc có người làm chứng)
2. GCN QSDĐ/QSHNƠ (sổ đỏ/sổ hồng)
3. Giấy chứng tử của người để lại di sản
4. CCCD của người thừa kế
5. Giấy tờ chứng minh quan hệ với người chết (giấy khai sinh)

THỪA KẾ THEO PHÁP LUẬT (không có di chúc):
Thêm vào hồ sơ:
- Giấy tờ chứng minh tất cả người thừa kế (để xác định hàng thừa kế)
- Văn bản từ chối nhận thừa kế (nếu có người từ chối, phải công chứng/chứng thực)
- Thông báo việc thụ lý khai nhận thừa kế trên báo 15 ngày

Lệ phí: 0,15% giá trị di sản thừa kế (tối thiểu 75.000 đ, tối đa 70 triệu đ/hợp đồng).
Thuế TNCN thừa kế: Miễn nếu nhận giữa cha/mẹ-con, vợ chồng, anh chị em ruột.''',
    },
    {
        'id': 'tp-006', 'category': 'tu_phap', 'procedure': 'uy_quyen', 'level': 'ward',
        'source': 'Bộ luật Dân sự 2015; Luật Công chứng 2014',
        'question': 'Làm giấy ủy quyền có cần công chứng không? Thủ tục như thế nào?',
        'answer': '''Hợp đồng ủy quyền liên quan đến bất động sản, xe cộ, tranh tụng... PHẢI công chứng/chứng thực.
Các ủy quyền đơn giản (nhận lương, thay mặt họp...) chỉ cần chứng thực chữ ký tại UBND xã.

CÔNG CHỨNG HỢP ĐỒNG ỦY QUYỀN tại Phòng/Văn phòng Công chứng:
Hồ sơ:
1. CCCD của bên ủy quyền và bên được ủy quyền (bản gốc)
2. Giấy tờ liên quan đến đối tượng ủy quyền (sổ đỏ, giấy đăng ký xe...)
3. Hợp đồng ủy quyền (công chứng viên soạn hoặc mang mẫu)

Lưu ý quan trọng:
- Ủy quyền mua bán đất: Cần có mặt cả hai bên khi công chứng
- Ủy quyền KHÔNG phải là chuyển nhượng — bên được ủy quyền không trở thành chủ sở hữu
- Hợp đồng ủy quyền chấm dứt khi: Hết hạn, bên ủy quyền/được ủy quyền chết, bên ủy quyền hủy bỏ

CHỨNG THỰC CHỮ KÝ tại UBND xã (cho ủy quyền đơn giản):
- Chỉ cần CCCD + văn bản ủy quyền soạn sẵn
- Lệ phí: 50.000 đồng/chữ ký
- Không xác nhận nội dung văn bản, chỉ xác nhận chữ ký đúng của người ủy quyền''',
    },
]

# =============================================================================
# 10. LAO ĐỘNG — HỢP ĐỒNG, THẤT NGHIỆP, XUẤT KHẨU LAO ĐỘNG
# =============================================================================
LAO_DONG = [
    {
        'id': 'ld-001', 'category': 'lao_dong', 'procedure': 'hop_dong_lao_dong', 'level': 'district',
        'source': 'Bộ luật Lao động 2019; Nghị định 145/2020/NĐ-CP',
        'question': 'Hợp đồng lao động có mấy loại? Công ty không ký HĐLĐ thì người lao động làm gì?',
        'answer': '''Bộ luật Lao động 2019 quy định 2 loại hợp đồng lao động:
1. HĐLĐ không xác định thời hạn (không thời hạn)
2. HĐLĐ xác định thời hạn (từ 12–36 tháng; ký tối đa 2 lần, lần 3 phải ký không thời hạn)

CÔNG TY KHÔNG KÝ HĐLĐ: Sau 15 ngày làm việc mà chưa ký hợp đồng → được coi như HĐLĐ không thời hạn.
Phạt công ty: 3.000.000–7.000.000 đồng/người lao động (Nghị định 28/2020/NĐ-CP).

QUYỀN LỢI NGƯỜI LAO ĐỘNG KHI CÔNG TY VI PHẠM:
- Có thể đơn phương chấm dứt HĐLĐ mà không cần báo trước
- Được nhận trợ cấp thôi việc (mỗi năm làm việc = 0,5 tháng lương bình quân)
- Được nhận lương những ngày đã làm
- Tố cáo đến Thanh tra Sở LĐTBXH

Phản ánh vi phạm: Thanh tra Sở LĐTBXH Thanh Hóa, 24 Hải Thượng Lãn Ông, TP Thanh Hóa.
ĐT: 0237.3852.197. Ngoài ra: Liên đoàn Lao động tỉnh Thanh Hóa: 0237.3852.015.''',
    },
    {
        'id': 'ld-002', 'category': 'lao_dong', 'procedure': 'bao_hiem_that_nghiep', 'level': 'district',
        'source': 'Luật Việc làm 2013; Nghị định 28/2015/NĐ-CP',
        'question': 'Nghỉ việc được hưởng trợ cấp thất nghiệp không? Điều kiện và thủ tục như thế nào?',
        'answer': '''Trợ cấp thất nghiệp (TCTN) do Trung tâm Dịch vụ Việc làm tỉnh Thanh Hóa chi trả.
Địa chỉ: 72 Lê Lợi, TP Thanh Hóa. ĐT: 0237.3757.007.

ĐIỀU KIỆN HƯỞNG TCTN:
1. Chấm dứt HĐLĐ (không phải tự ý nghỉ không có lý do chính đáng)
2. Đã đóng BHTN từ đủ 12 tháng trở lên trong 24 tháng trước khi nghỉ (HĐ xác định thời hạn) hoặc 36 tháng (HĐ không thời hạn)
3. Đã nộp hồ sơ trong 3 tháng kể từ ngày chấm dứt HĐLĐ
4. Chưa tìm được việc làm

MỨC HƯỞNG: 60% mức lương bình quân 6 tháng đóng BHTN trước khi nghỉ.
THỜI GIAN: 3 tháng/12 tháng đóng. Tối đa 12 tháng.

HỒ SƠ:
1. Đơn đề nghị hưởng trợ cấp thất nghiệp (Mẫu 03 - Nghị định 28/2015)
2. Bản sao HĐLĐ đã hết hạn hoặc Quyết định chấm dứt HĐLĐ/thôi việc
3. Sổ BHXH (hoặc xác nhận của BHXH về quá trình đóng BHTN)
4. CCCD (bản sao)

Thời hạn nộp: 3 tháng kể từ ngày chấm dứt HĐLĐ — quá hạn mất quyền hưởng.''',
    },
    {
        'id': 'ld-003', 'category': 'lao_dong', 'procedure': 'xuat_khau_lao_dong', 'level': 'province',
        'source': 'Luật Người lao động VN đi làm việc ở nước ngoài 2021',
        'question': 'Đi xuất khẩu lao động Nhật Bản, Hàn Quốc, Đài Loan cần điều kiện gì? Thủ tục ra sao?',
        'answer': '''Xuất khẩu lao động (XKLĐ) tại Sở Lao động - Thương binh và Xã hội Thanh Hóa.
Thanh Hóa là tỉnh có số lượng XKLĐ lớn nhất cả nước (trên 30.000 người/năm).

CÁC THỊ TRƯỜNG PHỔ BIẾN TẠI THANH HÓA:
- Nhật Bản (Thực tập sinh, Kỹ năng đặc định): Thu nhập 25–45 triệu đ/tháng
- Đài Loan (Công xưởng, Giúp việc, Điều dưỡng): 18–30 triệu đ/tháng
- Hàn Quốc (Chương trình EPS/E-9): 35–55 triệu đ/tháng
- Châu Âu (Romania, Hungary, Ba Lan): 30–50 triệu đ/tháng

ĐIỀU KIỆN CHUNG:
- Tuổi: 18–45 (tùy thị trường và nghề)
- Sức khỏe đủ tiêu chuẩn (không mắc bệnh lây truyền, không tiền án tiền sự)
- Tiếng: Nhật (N4), Hàn (EPS-TOPIK), Anh/Đài (tùy ngành)
- Không có hợp đồng lao động tại Việt Nam

THỦ TỤC:
1. Đăng ký tại Sở LĐTBXH hoặc công ty XKLĐ được Bộ LĐTBXH cấp phép
2. Thi tuyển, khám sức khỏe, học ngoại ngữ và giáo dục định hướng
3. Ký hợp đồng đưa đi làm việc ở nước ngoài
4. Làm hộ chiếu, visa → Xuất cảnh

CẢNH GIÁC LỪA ĐẢO: Chỉ làm việc với công ty có giấy phép XKLĐ của Bộ LĐTBXH (tra cứu tại dolab.gov.vn).
Sở LĐTBXH Thanh Hóa: soldtbxh@thanhhoa.gov.vn. ĐT hỗ trợ XKLĐ: 0237.3852.197.''',
    },
    {
        'id': 'ld-004', 'category': 'lao_dong', 'procedure': 'tai_nan_lao_dong', 'level': 'district',
        'source': 'Luật An toàn vệ sinh lao động 2015; Luật BHXH 2014',
        'question': 'Bị tai nạn lao động thì được hưởng quyền lợi gì? Doanh nghiệp có trách nhiệm gì?',
        'answer': '''Khi xảy ra tai nạn lao động (TNLĐ), người lao động được hưởng các chế độ sau:

CHẾ ĐỘ BỒI THƯỜNG, TRỢ CẤP TỪ DOANH NGHIỆP:
- Suy giảm khả năng lao động 5–10%: Trợ cấp ≥ 1,5 tháng lương
- 11–80%: Tăng thêm 0,4 tháng lương mỗi 1% suy giảm
- Từ 81% trở lên hoặc chết: ≥ 30 tháng lương
- Lỗi do NLĐ gây ra: Bồi thường ≥ 40% mức trên
- Doanh nghiệp không gây ra: Vẫn phải trả trợ cấp ≥ 40%

CHẾ ĐỘ BẢO HIỂM XÃ HỘI (nếu đã đóng BHXH):
- Trợ cấp một lần: 5 triệu đ (suy giảm 5%), tăng 500.000 đ/% (đến 30%)
- Trợ cấp hàng tháng: Nếu suy giảm ≥ 31% — mức trợ cấp theo % suy giảm
- Hỗ trợ phương tiện trợ giúp: Xe lăn, chân tay giả, máy trợ thính...
- Trợ cấp phục vụ: Nếu suy giảm ≥ 81%

THỦ TỤC:
1. Khai báo TNLĐ trong 24h với Sở LĐTBXH và Công an địa phương (TNLĐ chết người)
2. Giám định y tế xác định mức % suy giảm (tại Hội đồng Giám định y khoa tỉnh)
3. Nộp hồ sơ hưởng chế độ tại BHXH cấp huyện

Người lao động KHÔNG được đóng BHXH: Vẫn được doanh nghiệp bồi thường theo Luật ATVSLĐ.''',
    },
    {
        'id': 'ld-005', 'category': 'lao_dong', 'procedure': 'nghi_thai_san', 'level': 'district',
        'source': 'Luật BHXH 2014; Nghị định 115/2015/NĐ-CP',
        'question': 'Chế độ thai sản được hưởng những gì? Nghỉ bao nhiêu ngày? Thủ tục nhận tiền?',
        'answer': '''Chế độ thai sản áp dụng cho lao động nữ đang đóng BHXH bắt buộc.

ĐIỀU KIỆN: Đóng BHXH ≥ 6 tháng trong 12 tháng trước khi sinh/nhận nuôi con nuôi.

THỜI GIAN NGHỈ:
- Trước sinh: ≤ 2 tháng (trong tổng 6 tháng)
- Sinh 1 con: 6 tháng (sinh đôi: thêm 1 tháng/con từ con thứ 2)
- Sinh non dưới 32 tuần: 6 tháng + 1 tháng (sinh mổ)
- Chồng nghỉ khi vợ sinh: 5–14 ngày (tùy có sinh mổ/sinh đôi không)

MỨC HƯỞNG: 100% mức bình quân tiền lương đóng BHXH 6 tháng trước khi nghỉ thai sản.
Trợ cấp một lần khi sinh: Tối đa 2.000.000 đ/con (kể từ 01/7/2024 có thể điều chỉnh).

THỦ TỤC NHẬN CHẾ ĐỘ THAI SẢN:
1. Công ty lập hồ sơ nộp BHXH huyện trong 45 ngày kể từ ngày NLĐ trở lại làm việc
   Hoặc NLĐ tự nộp nếu thôi việc trước khi hết thai sản
2. Hồ sơ gồm: Giấy khai sinh con, Giấy ra viện, Tóm tắt hồ sơ bệnh án (sinh mổ/sinh non), Sổ BHXH
3. BHXH giải quyết trong 10 ngày, chuyển tiền vào tài khoản NLĐ qua doanh nghiệp

Nghỉ thai sản không bị trừ phép năm. Hết thai sản có quyền quay lại làm việc trước thời hạn (sau 4 tháng).''',
    },
]

# =============================================================================
# 11. Y TẾ — KHÁM SỨC KHỎE, HÀNH NGHỀ Y, AN TOÀN THỰC PHẨM
# =============================================================================
Y_TE = [
    {
        'id': 'yt-001', 'category': 'y_te', 'procedure': 'kham_suc_khoe', 'level': 'district',
        'source': 'Thông tư 14/2013/TT-BYT; Thông tư 32/2023/TT-BYT',
        'question': 'Xin giấy khám sức khỏe ở đâu? Dùng vào việc gì? Có hiệu lực bao lâu?',
        'answer': '''Giấy chứng nhận sức khỏe do các cơ sở y tế có thẩm quyền cấp (Bệnh viện, Phòng khám đa khoa được Sở Y tế công nhận).

TẠI THANH HÓA:
- Bệnh viện Đa khoa tỉnh Thanh Hóa: 03 Hải Thượng Lãn Ông, TP Thanh Hóa. ĐT: 0237.3852.021
- Bệnh viện Đa khoa huyện/thị (đối với giấy sức khỏe hạng B, C)
- Các phòng khám đa khoa tư nhân được Sở Y tế cấp phép

CÁC HẠNG SỨC KHỎE:
- Hạng I (tốt), II (khá), III (trung bình), IV (kém), V (rất kém — không đủ điều kiện nhiều công việc)

SỬ DỤNG GIẤY KHÁM SỨC KHỎE:
- Làm GPLX: Cần giấy sức khỏe lái xe (mẫu riêng, do cơ sở y tế chuyên khoa cấp)
- Xin việc làm: Nhiều cơ quan yêu cầu
- Đăng ký kết hôn với người nước ngoài
- Đăng ký đi XKLĐ
- Làm hồ sơ học bổng, du học

HIỆU LỰC: 12 tháng (1 năm) kể từ ngày cấp. Một số mục đích yêu cầu trong vòng 6 tháng.

CHI PHÍ: 150.000–350.000 đồng tùy hạng và cơ sở khám (bệnh viện công thường rẻ hơn).''',
    },
    {
        'id': 'yt-002', 'category': 'y_te', 'procedure': 'hanh_nghe_y_tu_nhan', 'level': 'province',
        'source': 'Luật Khám chữa bệnh 2023; Nghị định 96/2023/NĐ-CP',
        'question': 'Mở phòng khám tư nhân cần điều kiện và giấy phép gì? Xin ở đâu?',
        'answer': '''Cấp phép hoạt động cơ sở khám chữa bệnh tư nhân tại Sở Y tế Thanh Hóa.
Địa chỉ: 03 Phạm Bành, TP Thanh Hóa. ĐT: 0237.3852.390.

ĐIỀU KIỆN CÁ NHÂN (người chịu trách nhiệm chuyên môn):
- Có bằng bác sĩ/điều dưỡng/dược sĩ đại học trở lên
- Có chứng chỉ hành nghề khám chữa bệnh còn hiệu lực (cấp tại Sở Y tế)
- Thực hành ≥ 54 tháng (bác sĩ), 36 tháng (các ngành khác)

ĐIỀU KIỆN CƠ SỞ:
- Địa điểm: Riêng biệt, có đủ phòng khám, phòng thủ thuật (nếu có)
- Diện tích tối thiểu: ≥ 10m²/phòng khám (theo loại hình cơ sở)
- Trang thiết bị: Phải có danh mục trang thiết bị tối thiểu theo chuyên khoa
- Phòng cháy chữa cháy: Có xác nhận của Cảnh sát PCCC

QUY TRÌNH CẤP PHÉP:
1. Nộp hồ sơ tại Sở Y tế
2. Thẩm định hồ sơ (30 ngày)
3. Kiểm tra thực tế cơ sở
4. Cấp giấy phép hoạt động (nếu đủ điều kiện)

Thời gian: 60–120 ngày. Giấy phép có giá trị vô thời hạn (định kỳ đánh giá chất lượng).''',
    },
    {
        'id': 'yt-003', 'category': 'y_te', 'procedure': 'vsattp', 'level': 'district',
        'source': 'Luật An toàn thực phẩm 2010; Nghị định 15/2018/NĐ-CP',
        'question': 'Quán ăn, nhà hàng cần giấy phép vệ sinh an toàn thực phẩm không? Xin ở đâu?',
        'answer': '''Giấy chứng nhận cơ sở đủ điều kiện an toàn thực phẩm (ATTP) bắt buộc với hầu hết cơ sở kinh doanh thực phẩm.

CƠ QUAN CẤP PHÉP:
- Nhà hàng, quán ăn, căng-tin: UBND cấp huyện (Phòng Y tế) hoặc Ban Quản lý ATTP tỉnh
- Cơ sở sản xuất, chế biến thực phẩm: Sở Y tế hoặc Sở NNPTNT (tùy loại thực phẩm)
- Hộ kinh doanh nhỏ lẻ, bán rong: Tự đảm bảo điều kiện, chỉ ký cam kết ATTP

ĐIỀU KIỆN:
- Địa điểm: Sạch sẽ, cách xa nguồn ô nhiễm, có nước sạch, xử lý rác thải đúng cách
- Thiết bị: Dụng cụ chế biến, lưu trữ thực phẩm hợp vệ sinh
- Nhân viên: Có giấy chứng nhận tập huấn kiến thức ATTP (4 giờ/năm)
- Nhân viên trực tiếp chế biến: Có giấy khám sức khỏe (hạng III trở lên), không mắc bệnh lây qua thực phẩm

HỒ SƠ:
1. Đơn đề nghị cấp GCN cơ sở đủ điều kiện ATTP
2. Bản thuyết minh về cơ sở vật chất, dụng cụ, trang thiết bị
3. Giấy khám sức khỏe + chứng nhận tập huấn ATTP của chủ cơ sở và nhân viên
4. CCCD của chủ cơ sở

Thời hạn GCN: 3 năm. Phí: 700.000 đồng (sản xuất); 300.000 đồng (kinh doanh dịch vụ ăn uống).''',
    },
    {
        'id': 'yt-004', 'category': 'y_te', 'procedure': 'bao_hiem_y_te_trai_tuyen', 'level': 'district',
        'source': 'Luật BHYT 2014 sửa đổi 2023; Thông tư 40/2015/TT-BYT',
        'question': 'Khám bệnh trái tuyến BHYT được thanh toán bao nhiêu %? Làm sao để thanh toán?',
        'answer': '''Khi khám chữa bệnh KHÔNG đúng tuyến BHYT (đi thẳng bệnh viện mà không có giấy chuyển tuyến):

MỨC THANH TOÁN TRÁI TUYẾN (từ 01/01/2021 theo Luật BHYT sửa đổi):
- Tự đi bệnh viện huyện trái tuyến: 70% chi phí (trước đây: 70%, giữ nguyên)
- Tự đi bệnh viện tỉnh trái tuyến: 60% chi phí (không cần giấy chuyển tuyến)
- Tự đi bệnh viện trung ương trái tuyến: 40% chi phí

ĐÚNG TUYẾN ĐƯỢC THANH TOÁN 80–100%:
- Khám tại Trạm y tế xã đăng ký ban đầu: 100%
- Khám tại bệnh viện tuyến huyện đăng ký ban đầu: 100%
- Có giấy chuyển tuyến hợp lệ: Thanh toán như đúng tuyến

LƯU Ý QUAN TRỌNG (từ 2024):
Quy định "thông tuyến huyện" — người có thẻ BHYT đăng ký tại bất kỳ CSYT tuyến huyện nào trong cùng tỉnh đều được coi là ĐÚNG TUYẾN (thanh toán 80–100%).

THANH TOÁN CHI PHÍ TRỰC TIẾP (khi CSYT chưa ký hợp đồng BHYT):
- Nộp hồ sơ tại cơ quan BHXH nơi cư trú trong 12 tháng kể từ ngày ra viện
- Hồ sơ: Hóa đơn gốc, Phiếu chỉ định XN/thuốc, Tóm tắt bệnh án, Thẻ BHYT photo, CCCD''',
    },
]

# =============================================================================
# 12. GIÁO DỤC — CHUYỂN TRƯỜNG, MIỄN GIẢM HỌC PHÍ
# =============================================================================
GIAO_DUC = [
    {
        'id': 'gd-001', 'category': 'giao_duc', 'procedure': 'chuyen_truong', 'level': 'district',
        'source': 'Thông tư 28/2020/TT-BGDĐT; Thông tư 51/2012/TT-BGDĐT',
        'question': 'Thủ tục chuyển trường cho con (tiểu học, THCS, THPT) cần gì? Có được chuyển bất cứ lúc nào không?',
        'answer': '''Chuyển trường trong cùng tỉnh/thành phố và chuyển trường liên tỉnh đều được thực hiện trong năm học.

CHUYỂN TRƯỜNG TRONG TỈNH THANH HÓA:
Hồ sơ nộp tại trường mới muốn chuyển đến:
1. Đơn xin chuyển trường (phụ huynh/học sinh viết)
2. Học bạ bản chính (trường cũ cấp)
3. Giấy giới thiệu chuyển trường (trường cũ cấp)
4. Giấy khai sinh (bản sao)
5. Hộ khẩu/Giấy xác nhận cư trú tại địa bàn trường mới (nếu chuyển do thay đổi nơi ở)

Thời gian giải quyết: 7–15 ngày. Lệ phí: Miễn phí.

CHUYỂN TRƯỜNG LIÊN TỈNH (Vào Thanh Hóa hoặc ra khỏi Thanh Hóa):
Thêm vào hồ sơ:
- Xác nhận của Phòng/Sở GD&ĐT tỉnh cũ đồng ý cho chuyển

Điều kiện chuyển trường:
- Phải có lý do hợp lý (chuyển nơi cư trú, cha mẹ chuyển công tác...)
- Trường mới phải còn chỉ tiêu tuyển sinh
- THPT: Điểm học tập đáp ứng yêu cầu đầu vào của trường

Sở GD&ĐT Thanh Hóa: 03 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.487.''',
    },
    {
        'id': 'gd-002', 'category': 'giao_duc', 'procedure': 'mien_giam_hoc_phi', 'level': 'ward',
        'source': 'Nghị định 81/2021/NĐ-CP; Nghị định 97/2023/NĐ-CP',
        'question': 'Học sinh diện nào được miễn giảm học phí? Thủ tục xin miễn giảm học phí như thế nào?',
        'answer': '''Các đối tượng được MIỄN học phí:
1. Học sinh mầm non 5 tuổi, tiểu học (từ năm học 2020–2021 trở đi — trường công lập)
2. Học sinh THCS ở xã, thôn đặc biệt khó khăn (vùng ĐBKK theo QĐ của Chính phủ)
3. Con cán bộ, công nhân viên, học sinh, sinh viên bị nhiễm chất độc hóa học
4. Học sinh khuyết tật nặng, đặc biệt nặng
5. Trẻ em mồ côi cả cha lẫn mẹ không nơi nương tựa
6. Học sinh hộ nghèo, cận nghèo (tùy cấp học và địa phương)

Các đối tượng được GIẢM 70% học phí:
- Học sinh, sinh viên hộ có thu nhập bình quân bằng 150% hộ nghèo
- Học sinh là người dân tộc thiểu số ở vùng có điều kiện kinh tế xã hội khó khăn

THỦ TỤC XIN MIỄN GIẢM:
1. Đơn xin miễn giảm học phí (nhà trường có mẫu)
2. Bản sao Giấy xác nhận hộ nghèo/cận nghèo (do UBND xã cấp, còn hiệu lực)
3. Bản sao các giấy tờ chứng minh diện miễn giảm (Thẻ người tàn tật, xác nhận mồ côi...)

Nộp đầu năm học tại nhà trường → Trường tổng hợp → Phòng GD&ĐT phê duyệt.
Thời gian giải quyết: 30 ngày.''',
    },
    {
        'id': 'gd-003', 'category': 'giao_duc', 'procedure': 'cong_nhan_bang_nuoc_ngoai', 'level': 'province',
        'source': 'Thông tư 13/2021/TT-BGDĐT',
        'question': 'Bằng đại học nước ngoài có cần công nhận ở Việt Nam không? Thủ tục như thế nào?',
        'answer': '''Công nhận bằng do cơ sở giáo dục nước ngoài cấp (còn gọi là "hợp pháp hóa bằng" hay "nostrification") tại Sở GD&ĐT tỉnh Thanh Hóa.

Cần công nhận khi:
- Đăng ký thi tuyển vào cơ quan Nhà nước
- Thăng chức, bổ nhiệm trong hệ thống Nhà nước
- Đăng ký học tiếp bậc học cao hơn tại Việt Nam
- Một số doanh nghiệp yêu cầu

Hồ sơ:
1. Đơn đề nghị công nhận văn bằng (Mẫu 03, Thông tư 13/2021)
2. Bản sao bằng tốt nghiệp + Bảng điểm (có hợp pháp hóa lãnh sự và dịch thuật công chứng)
3. CCCD (bản sao)
4. Minh chứng về chương trình đào tạo của cơ sở giáo dục nước ngoài

Thời gian: 30 ngày làm việc. Lệ phí: 600.000 đồng.

Lưu ý: Cơ sở giáo dục nước ngoài phải được kiểm định và công nhận hợp pháp tại nước đó. Bằng do trường "lởm" (diploma mills) cấp không được công nhận.

Sở GD&ĐT Thanh Hóa: 03 Đào Duy Từ, TP Thanh Hóa. ĐT: 0237.3852.487.''',
    },
    {
        'id': 'gd-004', 'category': 'giao_duc', 'procedure': 'hoc_bong_ho_ngheo', 'level': 'ward',
        'source': 'Nghị định 86/2015/NĐ-CP; Thông tư 09/2016/TT-BGDĐT',
        'question': 'Con hộ nghèo học đại học được hỗ trợ tiền không? Học bổng chính sách như thế nào?',
        'answer': '''Học sinh, sinh viên hộ nghèo, cận nghèo được hưởng chính sách hỗ trợ chi phí học tập:

TRỢ CẤP XÃ HỘI (theo Nghị định 86/2015):
- Hộ nghèo: 3.600.000 đồng/năm (300.000 đ/tháng × 12 tháng học)
- Hộ cận nghèo: 50% mức trên = 1.800.000 đồng/năm
- Điều kiện: Đang học tại cơ sở GD nghề nghiệp và GDĐH công lập

VAY VỐN HỌC TẬP (Ngân hàng Chính sách Xã hội):
- Mức vay: Đến 4.000.000 đồng/tháng (tùy năm)
- Lãi suất: 6,6%/năm (ưu đãi, thấp hơn lãi suất thị trường)
- Trả sau khi ra trường (ân hạn 12 tháng, trả trong 10 năm)
- Điều kiện: Hộ nghèo, cận nghèo, gia đình KT khó khăn

THỦ TỤC VAY VỐN:
1. Xác nhận sinh viên đang học tại trường (do Phòng Công tác sinh viên cấp)
2. Hộ khẩu gia đình + Giấy xác nhận hộ nghèo/cận nghèo
3. Nộp tại Phòng Giao dịch NHCSXH cấp huyện nơi gia đình cư trú

NHCSXH Thanh Hóa: 119 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3851.248.''',
    },
]

# =============================================================================
# 13. MÔI TRƯỜNG — ĐÁNH GIÁ TÁC ĐỘNG, GIẤY PHÉP MÔI TRƯỜNG
# =============================================================================
MOI_TRUONG = [
    {
        'id': 'mt-001', 'category': 'moi_truong', 'procedure': 'giay_phep_moi_truong', 'level': 'province',
        'source': 'Luật Bảo vệ môi trường 2020; Nghị định 08/2022/NĐ-CP',
        'question': 'Doanh nghiệp cần giấy phép môi trường không? Đăng ký ở đâu? Thủ tục thế nào?',
        'answer': '''Từ 01/01/2022, Giấy phép môi trường (GPMT) thay thế nhiều loại giấy phép cũ (xả thải, khai thác nước, xử lý chất thải nguy hại...).

ĐỐI TƯỢNG BẮT BUỘC CÓ GPMT:
- Dự án nhóm I (có tác động môi trường lớn): Do Bộ TNMT cấp
- Dự án nhóm II (tác động vừa): Do Sở TNMT cấp
- Dự án nhóm III (tác động nhỏ): Do UBND cấp huyện cấp
- Cơ sở sản xuất có lượng nước thải ≥ 10m³/ngày, phát sinh chất thải nguy hại...

Cơ sở SẢN XUẤT NHỎ (dưới ngưỡng GPMT): Đăng ký môi trường tại UBND cấp xã.

NỘP HỒ SƠ TẠI SỞ TNMT THANH HÓA (với dự án nhóm II):
1. Đơn đề nghị cấp GPMT
2. Báo cáo đề xuất cấp GPMT (do đơn vị tư vấn lập)
3. Kết quả quan trắc môi trường xung quanh
4. Sơ đồ vị trí dự án và các công trình xử lý chất thải

Thời gian: 45 ngày làm việc (nhóm II). Thời hạn GPMT: 10 năm (gia hạn mỗi 5 năm).
Sở TNMT: 33 Đại lộ Lê Lợi. ĐT: 0237.3752.262.''',
    },
    {
        'id': 'mt-002', 'category': 'moi_truong', 'procedure': 'xu_ly_o_nhiem', 'level': 'province',
        'source': 'Luật Bảo vệ môi trường 2020',
        'question': 'Phát hiện doanh nghiệp gây ô nhiễm môi trường (xả thải, khói bụi) thì tố cáo ở đâu?',
        'answer': '''Người dân phát hiện ô nhiễm môi trường có thể phản ánh, tố cáo qua nhiều kênh:

1. ĐƯỜNG DÂY NÓNG:
   - Tổng cục Môi trường - Bộ TNMT: 1800.5656 (miễn phí, 24/7)
   - Sở TNMT Thanh Hóa: 0237.3752.262
   - Chi cục Bảo vệ môi trường Thanh Hóa: (thuộc Sở TNMT)

2. CỔNG PHẢN ÁNH KIẾN NGHỊ:
   - Quốc gia: phananhkiennghimoitruong.gov.vn
   - Thanh Hóa: pakn.thanhhoa.gov.vn
   - App "Môi trường Việt Nam" (Tổng cục Môi trường)

3. NỘP ĐƠN TỐ CÁO:
   - Thanh tra Sở TNMT Thanh Hóa (kèm bằng chứng: ảnh, video, kết quả quan trắc tự làm nếu có)
   - Phòng TN&MT UBND huyện
   - UBND xã (với vi phạm nhỏ)

SAU KHI TIẾP NHẬN:
- Cơ quan có thẩm quyền phải kiểm tra trong 30 ngày (trường hợp phức tạp 60 ngày)
- Nếu vi phạm: Xử phạt hành chính (5–1.000 triệu đồng), đình chỉ hoạt động, yêu cầu khắc phục
- Trường hợp nghiêm trọng (gây ô nhiễm diện rộng): Có thể truy cứu hình sự (Điều 235 BLHS 2015)

Bằng chứng hữu ích: Ảnh/video có dấu thời gian, mô tả màu, mùi nước thải, vị trí chính xác.''',
    },
    {
        'id': 'mt-003', 'category': 'moi_truong', 'procedure': 'xu_ly_rac_thai', 'level': 'ward',
        'source': 'Luật Bảo vệ môi trường 2020; Nghị định 45/2022/NĐ-CP',
        'question': 'Quy định về phân loại rác thải tại nguồn từ năm 2025 là gì? Xử phạt thế nào?',
        'answer': '''Từ 01/01/2025, người dân và doanh nghiệp BẮT BUỘC phân loại rác thải tại nguồn theo Luật BVMT 2020.

3 LOẠI RÁC CẦN PHÂN LOẠI:
1. Chất thải rắn có thể tái sử dụng, tái chế: Giấy, nhựa, kim loại, thủy tinh, quần áo cũ... (bỏ túi xanh/trắng)
2. Chất thải thực phẩm (rác hữu cơ): Thức ăn thừa, rau củ hỏng, vỏ trái cây... (bỏ túi nâu)
3. Chất thải rắn sinh hoạt khác: Rác không tái chế, không phân hủy được (bỏ túi đen)

CHẤT THẢI NGUY HẠI GIA ĐÌNH (bình đèn huỳnh quang, pin, thuốc quá hạn, sơn cũ):
→ Mang đến điểm thu gom nguy hại riêng (Sở TNMT quy định điểm thu trên địa bàn)

XỬ PHẠT VI PHẠM (Nghị định 45/2022):
- Không phân loại rác theo quy định: Cảnh cáo hoặc phạt 500.000–1.000.000 đồng
- Xả rác không đúng nơi quy định: Phạt 100.000–7.000.000 đồng (tùy khối lượng)
- Đốt rác ngoài trời không đúng nơi quy định: Phạt 1.000.000–5.000.000 đồng

TẠI THANH HÓA: Lộ trình thực hiện theo kế hoạch của UBND tỉnh. Liên hệ UBND xã/phường để biết điểm thu gom và lịch thu rác tại địa phương.''',
    },
]

# =============================================================================
# 14. ĐẦU TƯ — CẤP PHÉP, KKT NGHI SƠN, ƯU ĐÃI
# =============================================================================
DAU_TU = [
    {
        'id': 'dt-001', 'category': 'dau_tu', 'procedure': 'cap_phep_dau_tu', 'level': 'province',
        'source': 'Luật Đầu tư 2020; Nghị định 31/2021/NĐ-CP',
        'question': 'Doanh nghiệp nước ngoài muốn đầu tư vào Thanh Hóa thì thủ tục như thế nào?',
        'answer': '''Nhà đầu tư nước ngoài muốn đầu tư tại Thanh Hóa nộp hồ sơ tại Sở Kế hoạch và Đầu tư tỉnh hoặc Ban Quản lý Khu kinh tế Nghi Sơn và các Khu công nghiệp (đối với dự án trong KKT/KCN).

CÁC LOẠI DỰ ÁN:
1. Dự án không phải xin chấp thuận chủ trương (dưới 500 tỷ VNĐ, không thuộc lĩnh vực nhạy cảm): Cấp Giấy chứng nhận đăng ký đầu tư trực tiếp
2. Dự án cần chấp thuận chủ trương đầu tư của UBND tỉnh: Trình qua Sở KH&ĐT
3. Dự án cần Thủ tướng/Quốc hội chấp thuận: Quy mô > 5.000 tỷ đồng

THỦ TỤC CẤP GIẤY CHỨNG NHẬN ĐĂNG KÝ ĐẦU TƯ:
1. Đề xuất dự án đầu tư (thuyết minh)
2. Hồ sơ pháp lý nhà đầu tư (Điều lệ công ty, xác nhận tài chính, CCCD/Hộ chiếu)
3. Văn bản chứng minh quyền sử dụng địa điểm (hợp đồng thuê đất/nhà xưởng)
4. Báo cáo ĐTM hoặc cam kết BVMT (nếu có yêu cầu)

Thời gian cấp phép: 15 ngày (không thuộc diện chấp thuận chủ trương).

ƯU ĐÃI ĐẦU TƯ TẠI THANH HÓA:
- Thuế TNDN: 10% (15 năm); miễn 4 năm, giảm 50% trong 9 năm tiếp
- Miễn tiền thuê đất: 3–15 năm (tùy địa bàn và ngành nghề)
- Hỗ trợ GPMB, xây dựng hạ tầng ngoài hàng rào cho dự án lớn

Sở KH&ĐT Thanh Hóa: 24 Hải Thượng Lãn Ông. ĐT: 0237.3852.349. Email: skhdt@thanhhoa.gov.vn.''',
    },
    {
        'id': 'dt-002', 'category': 'dau_tu', 'procedure': 'kkt_nghi_son', 'level': 'province',
        'source': 'Quyết định 513/QĐ-TTg; Nghị định 36/2021/NĐ-CP về KKT Nghi Sơn',
        'question': 'Khu kinh tế Nghi Sơn có ưu đãi đầu tư gì đặc biệt? Nộp hồ sơ ở đâu?',
        'answer': '''Khu kinh tế Nghi Sơn (KKT Nghi Sơn) là KKT ven biển trọng điểm quốc gia tại tỉnh Thanh Hóa, diện tích 106.000 ha.

NỘP HỒ SƠ: Ban Quản lý Khu kinh tế Nghi Sơn và các KCN tỉnh Thanh Hóa.
Địa chỉ: Phường Hải Hòa, TX Nghi Sơn, Thanh Hóa. ĐT: 0237.3693.555.
Website: bqlkktns.thanhhoa.gov.vn.

ƯU ĐÃI ĐẶC BIỆT KKT NGHI SƠN:
1. THUẾ TNDN: 10% suốt thời gian dự án (hoặc 10% trong 15 năm cho dự án khác)
   - Miễn 4 năm kể từ khi có thu nhập chịu thuế
   - Giảm 50% trong 9 năm tiếp theo
2. THUẾ NHẬP KHẨU: Miễn thuế NK hàng hóa tạo TS cố định; nguyên liệu SX trong 5 năm
3. TIỀN THUÊ ĐẤT: Miễn 15 năm (địa bàn ưu tiên); giảm 50% trong các năm còn lại
4. THUẾ VAT: Hoàn VAT đầu vào cho hàng hóa sản xuất xuất khẩu

LĨNH VỰC ƯU TIÊN:
- Công nghiệp nặng, lọc hóa dầu (Lọc dầu Nghi Sơn đã vận hành)
- Cảng biển, logistics
- Năng lượng (nhiệt điện, LNG)
- Chế biến thủy sản, nông sản xuất khẩu
- Du lịch, dịch vụ

HIỆN TRẠNG (2024): KKT Nghi Sơn đã thu hút hơn 100 dự án, tổng vốn đăng ký > 12 tỷ USD.''',
    },
]

# =============================================================================
# 15. KHIẾU NẠI TỐ CÁO — QUYỀN CỦA CÔNG DÂN
# =============================================================================
KHIEU_NAI = [
    {
        'id': 'kn-001', 'category': 'khieu_nai', 'procedure': 'khieu_nai_hanh_chinh', 'level': 'province',
        'source': 'Luật Khiếu nại 2011; Nghị định 124/2020/NĐ-CP',
        'question': 'Khi bị cơ quan hành chính ra quyết định sai (thu hồi đất không đúng, xử phạt oan), tôi phải làm gì?',
        'answer': '''Công dân có quyền khiếu nại quyết định hành chính, hành vi hành chính của cơ quan/cán bộ Nhà nước.

QUY TRÌNH KHIẾU NẠI:

BƯỚC 1 — KHIẾU NẠI LẦN ĐẦU (đến cơ quan đã ra quyết định):
- Nộp Đơn khiếu nại đến người có thẩm quyền ra quyết định (thủ trưởng cơ quan)
- Thời hiệu: 90 ngày kể từ ngày nhận quyết định/biết được hành vi vi phạm
- Thời hạn giải quyết: 30 ngày (phức tạp: 45 ngày); vùng xa: +10 ngày
- Kết quả: Quyết định giải quyết khiếu nại lần đầu

BƯỚC 2 — KHIẾU NẠI LẦN HAI (nếu không đồng ý kết quả lần đầu):
- Nộp đơn đến thủ trưởng cấp trên trực tiếp hoặc Chánh Thanh tra
- Thời hiệu: 30 ngày kể từ khi nhận QĐ giải quyết lần đầu
- Thời hạn: 45–60 ngày
- Hoặc: Khởi kiện ra Tòa án Hành chính (thay vì khiếu nại lần 2)

ĐƠN KHIẾU NẠI GỒM:
1. Họ tên, địa chỉ người khiếu nại
2. Nội dung quyết định/hành vi bị khiếu nại
3. Lý do khiếu nại và yêu cầu cụ thể
4. Tài liệu, bằng chứng kèm theo

Thanh tra tỉnh Thanh Hóa: 28 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.029.
Hỗ trợ tư vấn pháp lý miễn phí: Trung tâm Trợ giúp pháp lý Nhà nước tỉnh Thanh Hóa. ĐT: 0237.3851.666.''',
    },
    {
        'id': 'kn-002', 'category': 'khieu_nai', 'procedure': 'to_cao', 'level': 'province',
        'source': 'Luật Tố cáo 2018; Nghị định 31/2019/NĐ-CP',
        'question': 'Tố cáo cán bộ tham nhũng, tiêu cực thì tố cáo ở đâu? Có bị lộ danh tính không?',
        'answer': '''Công dân có quyền tố cáo hành vi vi phạm pháp luật của cán bộ, công chức (tham nhũng, lạm quyền, nhận hối lộ...).

CÁC KÊNH TỐ CÁO:

1. TỐ CÁO TRỰC TIẾP:
   - Đến Thanh tra tỉnh Thanh Hóa: 28 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.029
   - Đến cơ quan quản lý trực tiếp của cán bộ bị tố cáo
   - Tiếp công dân thường xuyên: Thứ 2 và Thứ 5 hàng tuần tại Trụ sở tiếp công dân tỉnh

2. TỐ CÁO BẰNG VĂN BẢN:
   - Gửi đơn tố cáo (ký tên, ghi rõ họ tên, địa chỉ) đến cơ quan có thẩm quyền
   - Tố cáo nặc danh: Nếu có chứng cứ cụ thể, cơ quan vẫn xem xét giải quyết

3. TỐ CÁO THAM NHŨNG:
   - Ủy ban Kiểm tra Tỉnh ủy Thanh Hóa: 01 Đào Duy Từ, TP Thanh Hóa
   - Ban Nội chính Tỉnh ủy
   - Đường dây nóng phòng chống tham nhũng: 1800.1098 (Thanh tra Chính phủ)
   - Online: thanhtra.gov.vn

BẢO VỆ NGƯỜI TỐ CÁO:
- Cơ quan tiếp nhận có trách nhiệm giữ bí mật thông tin người tố cáo
- Cố tình tiết lộ: Xử lý kỷ luật hoặc truy cứu trách nhiệm hình sự
- Người tố cáo bị trả thù: Có quyền yêu cầu bảo vệ, tố cáo hành vi trả thù

Thời hạn giải quyết: 30–60 ngày (phức tạp: 90 ngày).''',
    },
    {
        'id': 'kn-003', 'category': 'khieu_nai', 'procedure': 'tiep_cong_dan', 'level': 'province',
        'source': 'Luật Tiếp công dân 2013; Nghị định 64/2014/NĐ-CP',
        'question': 'Muốn gặp lãnh đạo tỉnh Thanh Hóa để phản ánh, khiếu nại thì đến đâu? Lịch tiếp như thế nào?',
        'answer': '''Trụ sở Tiếp công dân tỉnh Thanh Hóa:
Địa chỉ: 02 Đào Duy Từ, phường Điện Biên, TP Thanh Hóa.
ĐT: 0237.3851.666.
Giờ làm việc: Thứ 2–6 (trừ ngày lễ): 7:30–11:30 và 13:30–17:00.

LỊCH TIẾP CÔNG DÂN CỦA LÃNH ĐẠO:
- Chủ tịch UBND tỉnh: Ngày 20 hàng tháng (hoặc ngày làm việc liền kề)
- Phó Chủ tịch: Mỗi tuần 1 ngày (theo phân công luân phiên)
- Trưởng Ban Tiếp công dân: Tiếp thường xuyên hàng ngày

ĐỂ ĐƯỢC TIẾP CÔNG DÂN:
1. Đăng ký trước tại Ban Tiếp công dân tỉnh (mang CCCD)
2. Trình bày nội dung cần gặp (đơn/tài liệu liên quan nếu có)
3. Được sắp xếp lịch tiếp theo thứ tự đăng ký

LƯU Ý:
- Đã có quyết định giải quyết khiếu nại lần 2 có hiệu lực: Không tiếp theo thủ tục khiếu nại (chuyển sang tòa án)
- Khiếu nại đông người (trên 5 người): Cử 1–2 đại diện vào tiếp
- Giữ trật tự, không gây rối tại trụ sở tiếp công dân (vi phạm bị xử phạt hành chính)

Trụ sở Tiếp công dân UBND TP Thanh Hóa: 16 Lê Hoàn. ĐT: 0237.3852.666.''',
    },
    {
        'id': 'kn-004', 'category': 'khieu_nai', 'procedure': 'tro_giup_phap_ly', 'level': 'province',
        'source': 'Luật Trợ giúp pháp lý 2017',
        'question': 'Tôi nghèo không có tiền thuê luật sư, có được nhà nước hỗ trợ luật sư miễn phí không?',
        'answer': '''Trung tâm Trợ giúp pháp lý Nhà nước tỉnh Thanh Hóa cung cấp dịch vụ pháp lý MIỄN PHÍ cho người thuộc diện trợ giúp.

Địa chỉ: 77 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3851.666.
Email: tgpl.stp@thanhhoa.gov.vn.

ĐỐI TƯỢNG ĐƯỢC TRỢ GIÚP PHÁP LÝ MIỄN PHÍ:
1. Người có công với cách mạng
2. Người thuộc hộ nghèo
3. Trẻ em (dưới 18 tuổi)
4. Người dân tộc thiểu số cư trú ở vùng có điều kiện KT-XH đặc biệt khó khăn
5. Người bị buộc tội từ đủ 16 đến dưới 18 tuổi; người bị buộc tội thuộc hộ cận nghèo
6. Người thuộc hộ cận nghèo
7. Nạn nhân bạo lực gia đình
8. Nạn nhân của tội phạm mua bán người
9. Người cao tuổi, người khuyết tật có hoàn cảnh khó khăn

PHẠM VI TRỢ GIÚP:
- Tư vấn pháp luật (trực tiếp, online, qua điện thoại)
- Soạn thảo đơn từ, văn bản pháp lý
- Tham gia tố tụng (đại diện/bào chữa tại tòa án)
- Hòa giải (trong tranh chấp dân sự)

Ngoài ra: Các Hội Luật gia và Đoàn Luật sư tỉnh Thanh Hóa cũng có các buổi tư vấn pháp lý miễn phí định kỳ.''',
    },
]

# =============================================================================
# 16. NÔNG NGHIỆP — GIỐNG, CHĂN NUÔI, THỦY SẢN
# =============================================================================
NONG_NGHIEP = [
    {
        'id': 'nn-001', 'category': 'nong_nghiep', 'procedure': 'cap_giay_chung_nhan_vietgap', 'level': 'province',
        'source': 'Quyết định 1516/QĐ-BNN-TT; Thông tư 48/2012/TT-BNNPTNT',
        'question': 'Thủ tục cấp giấy chứng nhận VietGAP cho trang trại, vùng trồng trọt cần gì?',
        'answer': '''Chứng nhận VietGAP (Thực hành Nông nghiệp tốt Việt Nam) cho rau quả, lúa, chè, cà phê...
Nộp tại: Sở Nông nghiệp và Phát triển nông thôn tỉnh Thanh Hóa hoặc Tổ chức chứng nhận được Bộ NN&PTNT chỉ định.

Địa chỉ Sở NN&PTNT Thanh Hóa: 20 Hải Thượng Lãn Ông, TP Thanh Hóa. ĐT: 0237.3852.491.

QUY TRÌNH CHỨNG NHẬN VIETGAP:
1. Đăng ký đánh giá với tổ chức chứng nhận
2. Đánh giá ban đầu (kiểm tra hồ sơ + kiểm tra thực địa)
3. Cấp chứng nhận nếu đạt (hiệu lực 2 năm, đánh giá giám sát hàng năm)
4. Gia hạn sau 2 năm (đánh giá lại)

HỒ SƠ:
1. Đơn đăng ký chứng nhận VietGAP
2. Bản đồ, sơ đồ vùng sản xuất
3. Hồ sơ về giống, phân bón, thuốc BVTV đã sử dụng
4. Nhật ký sản xuất (ghi chép toàn bộ quy trình canh tác)
5. Kết quả xét nghiệm mẫu sản phẩm (dư lượng thuốc BVTV, kim loại nặng)
6. Hồ sơ đất đai (GCN QSDĐ hoặc hợp đồng thuê đất)

Lợi ích: Được gắn nhãn VietGAP, bán vào siêu thị, xuất khẩu dễ hơn, giá bán cao hơn 10–30%.''',
    },
    {
        'id': 'nn-002', 'category': 'nong_nghiep', 'procedure': 'ho_tro_nong_nghiep', 'level': 'province',
        'source': 'Nghị định 52/2018/NĐ-CP; Nghị quyết HĐND tỉnh Thanh Hóa',
        'question': 'Nông dân Thanh Hóa được hỗ trợ gì khi mua máy móc nông nghiệp, trồng trọt, chăn nuôi?',
        'answer': '''Tỉnh Thanh Hóa có nhiều chính sách hỗ trợ nông dân, hợp tác xã nông nghiệp:

1. HỖ TRỢ MUA MÁY MÓC NÔNG NGHIỆP (theo Nghị định 52/2018):
   - Máy làm đất, máy cấy, máy gặt đập liên hợp: Hỗ trợ 100% lãi suất vay ngân hàng trong 2 năm
   - Hộ nông dân, HTX mua trực tiếp: Được vay vốn ưu đãi qua NHNN và NHCSXH

2. HỖ TRỢ TRỒNG TRỌT (theo NQ HĐND tỉnh):
   - Chuyển đổi đất lúa sang rau màu, cây ăn quả: 1–3 triệu đồng/ha
   - Xây dựng nhà lưới, nhà màng sản xuất rau an toàn: 30–50% chi phí (tối đa 200 triệu đ/ha)
   - Giống lúa chất lượng cao, giống rau mới: Hỗ trợ 50% tiền giống

3. HỖ TRỢ CHĂN NUÔI:
   - Tiêm phòng dịch bệnh (LMLM, dịch tả lợn...): Miễn phí vaccine
   - Xây dựng chuồng trại đảm bảo vệ sinh: Hỗ trợ 30% (tối đa 50 triệu đ/hộ)
   - Thiệt hại do dịch bệnh (khi có công bố dịch): Hỗ trợ theo giá thị trường

Liên hệ: Phòng Nông nghiệp UBND huyện hoặc Sở NN&PTNT Thanh Hóa để được tư vấn cụ thể.
Sở NN&PTNT: soldtbxh@thanhhoa.gov.vn. ĐT: 0237.3852.491.''',
    },
    {
        'id': 'nn-003', 'category': 'nong_nghiep', 'procedure': 'nuoi_trong_thuy_san', 'level': 'district',
        'source': 'Luật Thủy sản 2017; Nghị định 26/2019/NĐ-CP',
        'question': 'Muốn nuôi trồng thủy sản (tôm, cá) quy mô lớn cần giấy phép gì? Thủ tục ở đâu?',
        'answer': '''Nuôi trồng thủy sản thương phẩm cần đăng ký tại cơ quan quản lý thủy sản địa phương.

TẠI THANH HÓA: Nộp hồ sơ tại Chi cục Thủy sản (thuộc Sở NN&PTNT) hoặc Phòng Nông nghiệp UBND huyện.
Chi cục Thủy sản Thanh Hóa: 20 Hải Thượng Lãn Ông, TP Thanh Hóa.

ĐIỀU KIỆN NUÔI TRỒNG THỦY SẢN (cơ sở nuôi trên biển, nuôi thương phẩm lớn):
- Có GCN QSDĐ hoặc hợp đồng thuê mặt nước từ UBND tỉnh/huyện
- Cơ sở hạ tầng đảm bảo (ao nuôi, hệ thống cấp thoát nước, xử lý nước thải)
- Không nằm trong vùng cấm, hạn chế nuôi trồng thủy sản

HỒ SƠ ĐỀ NGHỊ GIAO MẶT NƯỚC BIỂN ĐỂ NUÔI TRỒNG:
1. Đơn đề nghị giao mặt nước biển
2. Dự án nuôi trồng thủy sản (thuyết minh quy trình, công nghệ)
3. Giấy tờ pháp nhân (CCCD/Giấy đăng ký DN)
4. Bản đồ vị trí khu vực đề nghị giao

HỖ TRỢ NUÔI TRỒNG THỦY SẢN TẠI THANH HÓA:
- Vay vốn ưu đãi qua Quỹ Hỗ trợ phát triển HTX tỉnh
- Hỗ trợ phí kiểm dịch giống thủy sản nhập tỉnh
- Tập huấn kỹ thuật nuôi trồng miễn phí (do Sở NN&PTNT tổ chức)

Thanh Hóa có bờ biển 102km, mạnh về nuôi tôm thẻ chân trắng, cua, hàu, cá lồng bè.''',
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
        # Batch 2
        'faq_tu_phap.xlsx':       TU_PHAP,
        'faq_lao_dong.xlsx':      LAO_DONG,
        'faq_y_te.xlsx':          Y_TE,
        'faq_giao_duc.xlsx':      GIAO_DUC,
        'faq_moi_truong.xlsx':    MOI_TRUONG,
        'faq_dau_tu.xlsx':        DAU_TU,
        'faq_khieu_nai.xlsx':     KHIEU_NAI,
        'faq_nong_nghiep.xlsx':   NONG_NGHIEP,
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
