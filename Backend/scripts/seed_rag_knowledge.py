"""
Seed dữ liệu kiến thức thủ tục hành chính vào ChromaDB (RAG).
Chatbot sẽ dùng dữ liệu này để trả lời câu hỏi của người dân.

Chạy sau seed_procedures.py:
  python scripts/seed_rag_knowledge.py
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ── Documents kiến thức ──────────────────────────────────────────────────────
# Mỗi document là một đoạn văn mô tả thủ tục hoặc câu hỏi thường gặp (FAQ)
# Viết dạng Q&A để chatbot dễ match với câu hỏi người dùng

KNOWLEDGE_DOCS = [
    # ═══════════════════════════════════════════════════════
    # HỘ TỊCH
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-khai-sinh-1',
        'text': '''Thủ tục đăng ký khai sinh tại Việt Nam.
Câu hỏi: Đăng ký khai sinh cần giấy tờ gì? Làm ở đâu? Mất bao lâu?

Trả lời: Đăng ký khai sinh thực hiện tại UBND cấp xã/phường/thị trấn nơi cư trú của cha hoặc mẹ.
Thời gian xử lý: 3 ngày làm việc.
Lệ phí: Miễn phí (0 đồng).
Thời hạn đăng ký: Trong vòng 60 ngày kể từ ngày sinh.

Giấy tờ cần mang:
1. Tờ khai đăng ký khai sinh (Mẫu TP/HT-2014-TKKS.1) — lấy tại UBND hoặc tải tại dichvucong.gov.vn
2. Giấy chứng sinh (bản gốc do bệnh viện/cơ sở y tế cấp)
3. CCCD/Căn cước công dân của cha hoặc mẹ (bản gốc)
4. Giấy đăng ký kết hôn của cha mẹ (nếu đã kết hôn — bản chính)

Căn cứ pháp lý: Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP.
Nộp trực tuyến: Tại cổng dichvucong.gov.vn hoặc dichvucong.thanhhoa.gov.vn.''',
        'metadata': {'category': 'ho_tich', 'procedure': 'khai_sinh', 'level': 'ward'}
    },
    {
        'id': 'proc-ket-hon-1',
        'text': '''Thủ tục đăng ký kết hôn tại Việt Nam.
Câu hỏi: Đăng ký kết hôn cần những giấy tờ gì? Thủ tục ở đâu?

Trả lời: Đăng ký kết hôn thực hiện tại UBND cấp xã/phường/thị trấn nơi cư trú của một trong hai bên.
Thời gian xử lý: 5 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ.
Lệ phí: Miễn phí từ ngày 01/01/2021 theo Nghị quyết 97/2019/QH14.
Độ tuổi kết hôn: Nam từ đủ 20 tuổi, Nữ từ đủ 18 tuổi.

Giấy tờ cần mang (mỗi người):
1. Tờ khai đăng ký kết hôn (Mẫu TP/HT-2014-TKKH.1) — cả hai bên ký
2. CCCD/Căn cước công dân (bản gốc)
3. Giấy xác nhận tình trạng hôn nhân — do UBND xã nơi thường trú cấp (trong 6 tháng gần nhất)
4. Giấy khai sinh (bản chính hoặc bản sao công chứng)
5. 2 ảnh 4x6 cm (nền trắng, chụp trong 6 tháng)

Lưu ý: Nếu một trong hai bên đã từng kết hôn, phải có bản án ly hôn đã có hiệu lực pháp luật.
Căn cứ: Luật Hộ tịch 2014; Luật HN&GĐ 2014; Nghị định 123/2015/NĐ-CP.''',
        'metadata': {'category': 'ho_tich', 'procedure': 'ket_hon', 'level': 'ward'}
    },
    {
        'id': 'proc-khai-tu-1',
        'text': '''Thủ tục đăng ký khai tử.
Câu hỏi: Đăng ký khai tử ở đâu? Cần giấy tờ gì?

Trả lời: Đăng ký khai tử tại UBND cấp xã/phường nơi người chết cư trú hoặc nơi người chết.
Thời gian: 3 ngày làm việc. Lệ phí: Miễn phí.
Thời hạn: Trong vòng 15 ngày kể từ ngày chết.

Giấy tờ cần:
1. Tờ khai đăng ký khai tử (Mẫu TP/HT-2014-TKKT.1)
2. Giấy báo tử của bệnh viện/cơ sở y tế (bản gốc)
3. CCCD/Căn cước công dân của người yêu cầu đăng ký

Nếu chết không có giấy báo tử: cần văn bản xác nhận của công an hoặc tòa án.
Căn cứ: Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP.''',
        'metadata': {'category': 'ho_tich', 'procedure': 'khai_tu', 'level': 'ward'}
    },

    # ═══════════════════════════════════════════════════════
    # CƯ TRÚ
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-thuong-tru-1',
        'text': '''Thủ tục đăng ký thường trú (nhập hộ khẩu).
Câu hỏi: Đăng ký thường trú cần gì? Nhập hộ khẩu mất bao lâu?

Trả lời: Nộp hồ sơ tại Công an cấp xã/phường nơi muốn đăng ký thường trú.
Thời gian: 7 ngày làm việc. Lệ phí: Miễn phí.

Điều kiện: Có chỗ ở hợp pháp (sở hữu, thuê ≥ 1 năm, được cho ở nhờ).

Giấy tờ cần:
1. Phiếu báo thay đổi hộ khẩu, nhân khẩu (CT01) — điền đầy đủ
2. CCCD/Căn cước công dân (bản gốc)
3. Giấy tờ chứng minh chỗ ở hợp pháp: Sổ đỏ/Sổ hồng, hoặc Hợp đồng thuê nhà công chứng (≥ 12 tháng)
4. Văn bản đồng ý của chủ hộ (nếu vào hộ người khác)
5. Giấy tờ quan hệ nhân thân với chủ hộ: Giấy khai sinh/Giấy đăng ký kết hôn

Từ năm 2021: Sổ hộ khẩu giấy đã bị bãi bỏ, thay bằng Cơ sở dữ liệu quốc gia về dân cư.
Căn cứ: Luật Cư trú 2020; Nghị định 62/2021/NĐ-CP.''',
        'metadata': {'category': 'cu_tru', 'procedure': 'thuong_tru', 'level': 'ward'}
    },
    {
        'id': 'proc-xac-nhan-cu-tru-1',
        'text': '''Xác nhận thông tin cư trú / Giấy xác nhận nơi cư trú.
Câu hỏi: Xin giấy xác nhận cư trú ở đâu? Cần giấy gì để xác nhận hộ khẩu?

Trả lời: Từ năm 2021, sổ hộ khẩu không còn giá trị. Thay vào đó:
- Tra cứu thông tin cư trú trực tuyến tại dichvucong.gov.vn
- Cổng thông tin dân cư: dancu.gov.vn
- Hoặc đến Công an phường/xã/thị trấn để được cấp Phiếu thông tin cư trú

Thời gian: Ngay trong ngày. Lệ phí: Miễn phí.
Chỉ cần CCCD/Căn cước công dân để tra cứu.

Lưu ý: Nhiều thủ tục hành chính hiện đã chia sẻ dữ liệu dân cư, không cần nộp bản sao sổ hộ khẩu nữa.''',
        'metadata': {'category': 'cu_tru', 'procedure': 'xac_nhan_cu_tru', 'level': 'ward'}
    },

    # ═══════════════════════════════════════════════════════
    # CCCD
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-cccd-1',
        'text': '''Cấp, đổi thẻ Căn cước công dân (CCCD) gắn chip.
Câu hỏi: Làm CCCD mới ở đâu? Cần giấy tờ gì? Mất bao nhiêu tiền?

Trả lời: Nộp hồ sơ tại Công an cấp huyện/quận hoặc điểm thu nhận lưu động của Công an tỉnh.
Tại Thanh Hóa: Phòng Cảnh sát QLHC về TTXH - Công an tỉnh hoặc Công an các huyện/thị.

Lệ phí:
- Cấp lần đầu: Miễn phí
- Đổi CCCD gắn chip: Miễn phí (trong đợt triển khai quốc gia)
- Cấp lại do mất: 70.000 đồng
- Cấp đổi do hư hỏng: 50.000 đồng

Thời gian: 7-15 ngày làm việc (cấp nhanh trong ngày: thu thêm phí theo quy định).

Giấy tờ cần:
1. Tờ khai căn cước công dân (CC01) — điền đầy đủ tại quầy
2. CCCD/CMND cũ (bản gốc, để thu hồi khi cấp mới)
3. Không cần mang ảnh (hệ thống chụp trực tiếp tại quầy)

Ai phải đổi sang CCCD gắn chip:
- Tất cả công dân Việt Nam từ đủ 14 tuổi trở lên
- CMND còn hạn vẫn có giá trị đến 31/12/2024

Căn cứ: Luật CCCD 2014; Luật Căn cước 2023; Nghị định 05/2021/NĐ-CP.''',
        'metadata': {'category': 'cccd', 'procedure': 'cccd', 'level': 'district'}
    },

    # ═══════════════════════════════════════════════════════
    # GIẤY PHÉP LÁI XE
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-gplx-1',
        'text': '''Cấp, đổi giấy phép lái xe (GPLX).
Câu hỏi: Đổi bằng lái xe cần giấy tờ gì? Làm bằng lái ở đâu tại Thanh Hóa?

Trả lời: Tại Sở Giao thông Vận tải Thanh Hóa (hoặc qua Trung tâm Đào tạo, sát hạch lái xe).
Địa chỉ: 09 Đại lộ Hùng Vương, TP Thanh Hóa.

Các hạng bằng lái phổ biến:
- B1: Xe không kinh doanh ≤ 9 chỗ, xe tải ≤ 3.5 tấn
- B2: Xe kinh doanh ≤ 9 chỗ, xe tải ≤ 3.5 tấn
- C: Xe tải > 3.5 tấn (không kéo moóc)

Lệ phí: 135.000 đồng/lần (theo Thông tư 296/2016/TT-BTC).
Thời gian: 15 ngày làm việc.

Giấy tờ đổi GPLX hết hạn:
1. Đơn đề nghị cấp/đổi GPLX (mẫu theo Thông tư 12/2017)
2. CCCD/Căn cước công dân (bản gốc + 1 bản sao)
3. GPLX cũ (bản gốc để thu hồi)
4. Giấy khám sức khỏe lái xe (còn hạn 6 tháng, do cơ sở y tế được phép cấp)
5. 2 ảnh 3×4 cm (nền trắng, chụp trong 6 tháng)

Thời hạn GPLX: B1: 10 năm; B2, C: 5 năm; D, E, F: 5 năm.
Căn cứ: Thông tư 12/2017/TT-BGTVT; Thông tư 05/2024/TT-BGTVT.''',
        'metadata': {'category': 'giao_thong', 'procedure': 'gplx', 'level': 'province'}
    },

    # ═══════════════════════════════════════════════════════
    # ĐẤT ĐAI
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-dat-dai-1',
        'text': '''Thủ tục sang tên, chuyển nhượng quyền sử dụng đất (Sổ đỏ/Sổ hồng).
Câu hỏi: Sang tên sổ đỏ cần giấy tờ gì? Mất bao lâu? Chi phí?

Trả lời: Nộp hồ sơ tại Văn phòng Đăng ký đất đai (thuộc Sở TNMT Thanh Hóa) hoặc UBND cấp huyện.
Thời gian: 15 ngày làm việc.

Chi phí phải nộp:
- Thuế TNCN (bên bán): 2% giá chuyển nhượng
- Lệ phí trước bạ (bên mua): 0,5% giá trị đất
- Phí công chứng: 0,1% giá trị tài sản (tối thiểu 50.000đ, tối đa 70 triệu đồng)
- Lệ phí cấp GCN: 100.000 đồng/lần

Giấy tờ cần (đã có hợp đồng công chứng):
1. Đơn đăng ký biến động đất đai (Mẫu 09/ĐK)
2. CCCD của hai bên (bản sao có chứng thực)
3. Sổ đỏ/Sổ hồng gốc (để đăng ký sang tên)
4. Hợp đồng chuyển nhượng có công chứng (bản chính)
5. Tờ khai lệ phí trước bạ (Mẫu 01/LPTB)
6. Biên lai nộp thuế TNCN hoặc giấy xác nhận miễn thuế

Lưu ý: Bước đầu tiên là ký hợp đồng mua bán tại Văn phòng Công chứng, sau đó mới nộp hồ sơ sang tên.
Căn cứ: Luật Đất đai 2024 (có hiệu lực từ 01/8/2024); Nghị định 43/2014/NĐ-CP.''',
        'metadata': {'category': 'dat_dai', 'procedure': 'chuyen_nhuong_qsdd', 'level': 'district'}
    },
    {
        'id': 'proc-dat-dai-2',
        'text': '''Cấp Giấy chứng nhận quyền sử dụng đất lần đầu (Sổ đỏ).
Câu hỏi: Làm sổ đỏ lần đầu cần gì? Đất chưa có sổ đỏ làm thế nào?

Trả lời: Nộp hồ sơ tại Văn phòng Đăng ký đất đai cấp huyện hoặc UBND xã (đối với đất nông thôn).
Thời gian: 30 ngày làm việc (nông thôn: 40 ngày).
Lệ phí: 100.000 đồng + thuế sử dụng đất phi nông nghiệp (nếu áp dụng).

Giấy tờ cần:
1. Đơn đăng ký cấp GCN (Mẫu 04a/ĐK)
2. CCCD + 1 bản sao
3. Giấy tờ chứng minh nguồn gốc sử dụng đất: biên lai thuế đất cũ, hợp đồng mua bán từ trước 2004 có xác nhận của UBND, quyết định giao đất...
4. Trích lục bản đồ địa chính (do Văn phòng ĐKDD cấp)

Trường hợp đất không có giấy tờ: phải làm thủ tục xét duyệt, có thể mất 3-6 tháng.''',
        'metadata': {'category': 'dat_dai', 'procedure': 'cap_gcn_dat', 'level': 'district'}
    },

    # ═══════════════════════════════════════════════════════
    # XÂY DỰNG
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-xay-dung-1',
        'text': '''Cấp phép xây dựng nhà ở riêng lẻ tại đô thị.
Câu hỏi: Xin phép xây nhà cần giấy gì? Xây nhà không có phép bị phạt bao nhiêu?

Trả lời: Nộp tại UBND cấp huyện (Phòng Quản lý Đô thị hoặc Phòng Kinh tế - Hạ tầng).
Tại TP Thanh Hóa: Phòng Quản lý Đô thị - UBND TP Thanh Hóa.
Thời gian: 15 ngày làm việc.
Lệ phí: Theo quy định HĐND tỉnh (100.000 - 500.000 đồng tùy công trình).

Nhà ở không cần phép xây dựng (theo Luật Xây dựng 2020):
- Công trình ở nông thôn, miền núi không thuộc đô thị
- Công trình sửa chữa không thay đổi kết cấu, kiến trúc

Giấy tờ cần:
1. Đơn đề nghị cấp phép xây dựng (Mẫu số 01, phụ lục II NĐ15)
2. CCCD (bản gốc + 1 bản sao)
3. Sổ đỏ/Sổ hồng bản sao công chứng
4. Hồ sơ thiết kế 2 bộ: mặt bằng, mặt đứng, mặt cắt, sơ đồ vị trí
5. Sơ đồ tổng mặt bằng

Phạt vi phạm xây dựng không phép: 60-80 triệu đồng + buộc tháo dỡ phần vi phạm.
Căn cứ: Luật Xây dựng 2014 sửa đổi 2020; Nghị định 15/2021/NĐ-CP.''',
        'metadata': {'category': 'xay_dung', 'procedure': 'cap_phep_xay_dung', 'level': 'district'}
    },

    # ═══════════════════════════════════════════════════════
    # KINH DOANH
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-kinh-doanh-1',
        'text': '''Đăng ký thành lập hộ kinh doanh cá thể.
Câu hỏi: Mở hộ kinh doanh cần gì? Đăng ký kinh doanh cá thể ở đâu?

Trả lời: Nộp tại Phòng Tài chính - Kế hoạch UBND cấp huyện nơi đặt địa điểm kinh doanh.
Thời gian: 3 ngày làm việc. Lệ phí: 100.000 đồng.

Ai được đăng ký hộ kinh doanh:
- Cá nhân là công dân Việt Nam từ đủ 18 tuổi, có năng lực hành vi dân sự đầy đủ
- Một hộ kinh doanh chỉ được đăng ký 1 địa điểm kinh doanh
- Số lao động thường xuyên < 10 người

Giấy tờ cần:
1. Giấy đề nghị đăng ký hộ kinh doanh (Phụ lục III-1, NĐ01/2021)
2. CCCD của chủ hộ kinh doanh (bản gốc + 1 bản sao)
3. Giấy tờ chứng minh địa điểm: hợp đồng thuê (công chứng) hoặc sổ đỏ/sổ hồng bản sao công chứng

Sau khi được cấp Giấy chứng nhận đăng ký hộ kinh doanh, phải:
- Đăng ký thuế tại Chi cục Thuế trong 10 ngày
- Treo biển hiệu theo quy định

Căn cứ: Nghị định 01/2021/NĐ-CP; Luật Doanh nghiệp 2020.''',
        'metadata': {'category': 'kinh_doanh', 'procedure': 'ho_kinh_doanh', 'level': 'district'}
    },
    {
        'id': 'proc-kinh-doanh-2',
        'text': '''Đăng ký thành lập công ty TNHH, công ty cổ phần.
Câu hỏi: Thành lập công ty TNHH cần gì? Đăng ký doanh nghiệp online được không?

Trả lời: Đăng ký tại Sở Kế hoạch và Đầu tư tỉnh Thanh Hóa, hoặc đăng ký trực tuyến tại dangkykinhdoanh.gov.vn.
Thời gian: 3 ngày làm việc.
Lệ phí: Miễn phí khi đăng ký online; 50.000đ khi nộp hồ sơ giấy.

Giấy tờ cần (Công ty TNHH 1 thành viên):
1. Giấy đề nghị đăng ký doanh nghiệp (Phụ lục I-1, NĐ01/2021)
2. Điều lệ công ty (đại diện pháp luật ký từng trang)
3. CCCD của chủ sở hữu (bản sao — không cần công chứng)
4. CCCD của người đại diện theo pháp luật (bản sao)

Vốn điều lệ: Không có quy định tối thiểu, tự khai theo thực tế.
Ngành nghề có điều kiện (kinh doanh tài chính, ngân hàng, y tế...): cần thêm giấy phép chuyên ngành.

Sau đăng ký phải làm:
- Khắc dấu doanh nghiệp và đăng tải mẫu dấu
- Mở tài khoản ngân hàng
- Đăng ký thuế, kê khai và nộp thuế định kỳ

Căn cứ: Luật Doanh nghiệp 2020; Nghị định 01/2021/NĐ-CP.''',
        'metadata': {'category': 'kinh_doanh', 'procedure': 'thanh_lap_cong_ty', 'level': 'province'}
    },

    # ═══════════════════════════════════════════════════════
    # BẢO HIỂM XÃ HỘI
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-bhxh-1',
        'text': '''Bảo hiểm xã hội, bảo hiểm y tế tại Thanh Hóa.
Câu hỏi: Đăng ký BHXH ở đâu? BHYT tự nguyện mua như thế nào?

Trả lời: BHXH tỉnh Thanh Hóa địa chỉ: 103 Đại lộ Lê Lợi, TP Thanh Hóa. ĐT: 0237.3852.268.
Có thể giao dịch trực tuyến tại baohiemxahoi.gov.vn.

BHXH bắt buộc (người lao động có hợp đồng lao động ≥ 1 tháng):
- Doanh nghiệp đăng ký qua cổng dvcbhxh.vss.gov.vn
- Người lao động không cần tự đăng ký (do doanh nghiệp làm thay)

BHYT tự nguyện (người không thuộc đối tượng bắt buộc):
- Mức đóng: 4,5% lương cơ sở (khoảng 900.000đ/năm năm 2024)
- Đăng ký tại BHXH huyện hoặc qua ứng dụng VssID

Hưởng BHXH một lần: Điều kiện: đủ 20 năm đóng và nam đủ 60 tuổi, nữ đủ 55 tuổi (hoặc điều kiện bệnh tật đặc biệt).
Hồ sơ: Đơn đề nghị (Mẫu 14-HSB), Sổ BHXH gốc, CCCD.

Căn cứ: Luật BHXH 2014; Luật BHYT 2008 sửa đổi 2014.''',
        'metadata': {'category': 'bao_hiem', 'procedure': 'bhxh', 'level': 'district'}
    },

    # ═══════════════════════════════════════════════════════
    # TƯ PHÁP
    # ═══════════════════════════════════════════════════════
    {
        'id': 'proc-lltp-1',
        'text': '''Cấp Phiếu lý lịch tư pháp số 1 (còn gọi là lý lịch tư pháp, xác nhận không có tiền án).
Câu hỏi: Xin lý lịch tư pháp ở đâu? Cần giấy gì để xin phiếu lý lịch tư pháp?

Trả lời: Tại Sở Tư pháp tỉnh Thanh Hóa (địa chỉ: 34 Đại lộ Lê Lợi, TP Thanh Hóa).
Hoặc nộp trực tuyến tại: dichvucong.gov.vn.
Thời gian: 10 ngày làm việc. Lệ phí: 200.000 đồng.

Phiếu lý lịch tư pháp số 1: Cấp cho cá nhân (để nộp cho cơ quan tuyển dụng, du học, xin việc...)
Phiếu lý lịch tư pháp số 2: Cấp theo yêu cầu của cơ quan nhà nước có thẩm quyền.

Giấy tờ cần:
1. Tờ khai yêu cầu (Mẫu số 03/2013/TT-BTP) — lấy tại Sở Tư pháp hoặc tải online
2. CCCD/Căn cước công dân (bản gốc để đối chiếu + 1 bản sao)
3. Lệ phí 200.000 đồng

Thời hạn hiệu lực phiếu LLTP: Không có quy định thời hạn cụ thể, nhưng thường được chấp nhận trong 3-6 tháng kể từ ngày cấp.
Căn cứ: Luật Lý lịch tư pháp 2009; Nghị định 111/2010/NĐ-CP.''',
        'metadata': {'category': 'tu_phap', 'procedure': 'lltp', 'level': 'province'}
    },

    # ═══════════════════════════════════════════════════════
    # THÔNG TIN TỔNG QUÁT
    # ═══════════════════════════════════════════════════════
    {
        'id': 'info-thanhhoa-portal-1',
        'text': '''Cổng thông tin dịch vụ công tỉnh Thanh Hóa.
Câu hỏi: Trang web dịch vụ công Thanh Hóa là gì? Nộp hồ sơ online ở đâu?

Trả lời: Cổng dịch vụ công tỉnh Thanh Hóa: dichvucong.thanhhoa.gov.vn
Cổng dịch vụ công Quốc gia: dichvucong.gov.vn
Tra cứu thủ tục: thutuchanhchinh.gov.vn

Trung tâm Phục vụ Hành chính công tỉnh Thanh Hóa:
- Địa chỉ: 25A Đại lộ Lê Lợi, phường Ba Đình, TP Thanh Hóa
- Điện thoại: 0237.3753.888
- Giờ làm việc: Thứ 2-6: 7:00-17:30; Thứ 7: 7:30-12:00

Tiếp nhận hồ sơ của 19 Sở, ngành và UBND TP Thanh Hóa tại 1 đầu mối.
Người dân có thể nộp hồ sơ trực tuyến hoặc đến trực tiếp.

Đường dây hỗ trợ: 1022 (miễn phí, 24/7)
Ứng dụng di động: VNeID (xác thực định danh); VssID (BHXH); VNPT SmartCA (chữ ký số).''',
        'metadata': {'category': 'thong_tin', 'procedure': 'portal', 'level': 'province'}
    },
    {
        'id': 'info-thanhhoa-agencies-1',
        'text': '''Danh sách các cơ quan hành chính tỉnh Thanh Hóa và số điện thoại liên hệ.

UBND tỉnh Thanh Hóa: 0237.3852.428 | ubnd@thanhhoa.gov.vn
Công an tỉnh (CCCD/cư trú): 069.2587.018
Sở Tư pháp (công chứng, lý lịch tư pháp): 0237.3852.573
Sở TNMT (đất đai, môi trường): 0237.3752.262
Sở Xây dựng (phép xây dựng): 0237.3852.601
Sở GTVT (giấy phép lái xe): 0237.3850.397
Sở KH&ĐT (doanh nghiệp): 0237.3852.349
Cục Thuế tỉnh: 0237.3850.068
BHXH tỉnh: 0237.3852.268
Sở Y tế: 0237.3852.390
Sở GD&ĐT: 0237.3852.487
Sở LĐ-TB&XH: 0237.3852.197
Trung tâm HCC tỉnh: 0237.3753.888

Đường dây nóng phản ánh: 0237.3650.000
Hỗ trợ DVC trực tuyến: 1022''',
        'metadata': {'category': 'thong_tin', 'procedure': 'lien_he', 'level': 'province'}
    },
    {
        'id': 'info-thanhhoa-fee-1',
        'text': '''Bảng phí và lệ phí các thủ tục hành chính phổ biến tại Thanh Hóa.

MIỄN PHÍ (0 đồng):
- Đăng ký khai sinh, khai tử, kết hôn
- Cấp CCCD lần đầu (trong đợt triển khai quốc gia)
- Đăng ký thường trú, tạm trú
- Đăng ký doanh nghiệp trực tuyến
- Cấp sổ BHXH

CÓ PHÍ:
- Đổi CCCD do mất: 70.000đ | do hỏng: 50.000đ
- Giấy phép lái xe: 135.000đ/lần
- Lý lịch tư pháp số 1: 200.000đ
- Đăng ký hộ kinh doanh: 100.000đ
- Công chứng hợp đồng: 0,1% giá trị tài sản (tối thiểu 50.000đ)
- Lệ phí trước bạ nhà, đất: 0,5% giá trị
- Thuế TNCN chuyển nhượng đất: 2% giá chuyển nhượng
- Giấy phép xây dựng: 100.000-500.000đ tùy công trình
- Khám sức khỏe (GPLX): 80.000-120.000đ

Miễn giảm phí cho: Hộ nghèo, cận nghèo, người có công, thương binh bệnh binh, đồng bào dân tộc thiểu số ở vùng đặc biệt khó khăn.''',
        'metadata': {'category': 'thong_tin', 'procedure': 'phi_le_phi', 'level': 'province'}
    },
    {
        'id': 'info-thanhhoa-time-1',
        'text': '''Thời gian xử lý các thủ tục hành chính phổ biến và lưu ý quan trọng.

NHANH (1-3 ngày làm việc):
- Khai sinh, khai tử: 3 ngày
- Đăng ký hộ kinh doanh: 3 ngày
- Đăng ký công ty: 3 ngày
- Xác nhận cư trú: 1 ngày

TRUNG BÌNH (5-15 ngày làm việc):
- Đăng ký kết hôn: 5 ngày
- Đăng ký thường trú: 7 ngày
- Cấp/đổi CCCD: 7-15 ngày
- Đổi GPLX: 10-15 ngày
- Lý lịch tư pháp: 10 ngày
- Cấp phép xây dựng: 15 ngày
- Chuyển nhượng đất: 15 ngày

DÀI (≥ 30 ngày):
- Cấp sổ đỏ lần đầu: 30-40 ngày
- Công nhận văn bằng nước ngoài: 30 ngày

LƯU Ý QUAN TRỌNG:
- Nộp hồ sơ vào thứ 3-4 để tránh đông đầu tuần và cuối tuần
- Nên tra cứu yêu cầu hồ sơ trước tại dichvucong.thanhhoa.gov.vn
- Có thể đặt lịch hẹn trước tại Trung tâm HCC để không phải chờ đợi
- Mang theo CCCD bản gốc cho tất cả thủ tục''',
        'metadata': {'category': 'thong_tin', 'procedure': 'thoi_gian', 'level': 'province'}
    },
]


def seed_rag(collection_name: str = 'faqs_collection'):
    """Nạp kiến thức thủ tục vào ChromaDB."""
    import chromadb
    from pathlib import Path

    rag_dir = Path(__file__).parent.parent / 'RAG'
    chroma_path = rag_dir / 'chroma_db' / 'chroma_db_faqs'
    chroma_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(chroma_path))

    # Lấy hoặc tạo collection
    try:
        collection = client.get_collection(collection_name)
        print(f'  Đã có collection "{collection_name}" ({collection.count()} documents)')
    except Exception:
        collection = client.create_collection(
            name=collection_name,
            metadata={'hnsw:space': 'cosine'}
        )
        print(f'  Tạo collection mới: "{collection_name}"')

    # Xóa documents cũ của chúng ta (có prefix 'proc-' hoặc 'info-')
    try:
        ids_to_delete = [d['id'] for d in KNOWLEDGE_DOCS]
        existing = collection.get(ids=ids_to_delete)
        if existing['ids']:
            collection.delete(ids=existing['ids'])
            print(f'  Đã xóa {len(existing["ids"])} documents cũ')
    except Exception:
        pass

    # Thêm documents mới
    ids       = [d['id'] for d in KNOWLEDGE_DOCS]
    documents = [d['text'] for d in KNOWLEDGE_DOCS]
    metadatas = [d['metadata'] for d in KNOWLEDGE_DOCS]

    # Thêm theo batch 10 documents
    batch_size = 10
    added = 0
    for i in range(0, len(ids), batch_size):
        batch_ids   = ids[i:i + batch_size]
        batch_docs  = documents[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        try:
            collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
            added += len(batch_ids)
            print(f'  + Batch {i//batch_size + 1}: {len(batch_ids)} documents')
        except Exception as e:
            print(f'  ! Batch {i//batch_size + 1} lỗi: {e}')

    print(f'  → Tổng {added}/{len(KNOWLEDGE_DOCS)} documents đã seed vào ChromaDB.')
    print(f'  → Collection hiện có: {collection.count()} documents.')
    return added


def seed_thanhhoa_collection():
    """Cũng seed vào collection thanhhoa (nếu tồn tại)."""
    import chromadb
    from pathlib import Path

    rag_dir = Path(__file__).parent.parent / 'RAG'
    chroma_path = rag_dir / 'chroma_db' / 'thanhhoa'

    if not chroma_path.exists():
        print('  Collection thanhhoa chưa tồn tại — bỏ qua.')
        return

    client = chromadb.PersistentClient(path=str(chroma_path))
    try:
        collections = client.list_collections()
        if not collections:
            print('  Không có collection nào trong thanhhoa — bỏ qua.')
            return
        col_name = collections[0].name
        collection = client.get_collection(col_name)
        print(f'  Seed vào collection thanhhoa/{col_name}...')
        ids       = [d['id'] for d in KNOWLEDGE_DOCS]
        documents = [d['text'] for d in KNOWLEDGE_DOCS]
        metadatas = [d['metadata'] for d in KNOWLEDGE_DOCS]
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f'  → Đã upsert {len(ids)} documents vào thanhhoa/{col_name}.')
    except Exception as e:
        print(f'  ! Lỗi seed thanhhoa: {e}')


if __name__ == '__main__':
    print('\n' + '='*60)
    print('  SEED RAG KNOWLEDGE — Thủ tục hành chính Thanh Hóa')
    print('='*60 + '\n')

    print('1. Seed vào ChromaDB (faqs_collection)...')
    seed_rag()

    print('\n2. Seed vào ChromaDB (thanhhoa collection)...')
    seed_thanhhoa_collection()

    print('\n✓ Hoàn thành seed RAG knowledge!')
    print(f'  Tổng {len(KNOWLEDGE_DOCS)} documents kiến thức đã được nạp.')
    print('\nChatbot giờ có thể trả lời các câu hỏi về:')
    for doc in KNOWLEDGE_DOCS:
        proc = doc["metadata"].get("procedure", "")
        print(f'  - {proc}: {doc["text"][:60].strip()}...')
