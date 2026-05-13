"""Batch 8 — Q&A chung toàn quốc: bảo hiểm, quyền tiêu dùng, SHTT, chuyển đổi số, nhà ở, công an, phúc lợi."""
import sys
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent

def w(filename, rows):
    df = pd.DataFrame(rows, columns=['id','category','procedure','level','source','question','answer'])
    path = OUT / filename
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='FAQ', index=False)
    print(f'+ {filename} ({len(df)} rows)')

def main():
    # 1. Bảo hiểm
    w('faq_g_bao_hiem.xlsx', [
        ('bh001','Bảo hiểm','Bảo hiểm nhân thọ','Quốc gia','Bộ Tài chính',
         'Bảo hiểm nhân thọ là gì?',
         'Bảo hiểm nhân thọ là loại bảo hiểm mà công ty bảo hiểm cam kết chi trả một khoản tiền nhất định khi người được bảo hiểm tử vong, sống đến hạn hợp đồng, hoặc xảy ra các sự kiện được thỏa thuận. Hợp đồng thường có kỳ hạn từ 5–30 năm, phí đóng định kỳ theo tháng/năm.'),
        ('bh002','Bảo hiểm','Bảo hiểm nhân thọ','Quốc gia','Bộ Tài chính',
         'Quyền lợi khi hủy hợp đồng bảo hiểm nhân thọ trước hạn là gì?',
         'Khi hủy hợp đồng bảo hiểm nhân thọ trước hạn, bạn được nhận "giá trị hoàn lại" — số tiền tích lũy trong hợp đồng sau khi trừ chi phí. Thông thường trong 2 năm đầu, giá trị hoàn lại rất thấp hoặc bằng 0. Từ năm thứ 3 trở đi mới có giá trị đáng kể. Cần xem kỹ bảng giá trị hoàn lại trong hợp đồng trước khi quyết định hủy.'),
        ('bh003','Bảo hiểm','Bảo hiểm phi nhân thọ','Quốc gia','Bộ Tài chính',
         'Bảo hiểm xe máy bắt buộc có phạm vi bồi thường như thế nào?',
         'Bảo hiểm trách nhiệm dân sự xe máy bắt buộc bồi thường thiệt hại cho bên thứ ba (người bị tai nạn do xe gây ra): tử vong tối đa 150 triệu đồng/người, thương tật tối đa 50 triệu đồng/người, tài sản tối đa 15 triệu đồng/vụ. Không bồi thường cho chủ xe hoặc lái xe gây tai nạn.'),
        ('bh004','Bảo hiểm','Bảo hiểm phi nhân thọ','Quốc gia','Bộ Tài chính',
         'Phí bảo hiểm xe máy bắt buộc hàng năm là bao nhiêu?',
         'Theo quy định hiện hành, phí bảo hiểm trách nhiệm dân sự bắt buộc xe máy là 66.000 đồng/năm (đã bao gồm VAT). Đây là mức tối thiểu bắt buộc; có thể mua thêm bảo hiểm tự nguyện với phạm vi bồi thường cao hơn.'),
        ('bh005','Bảo hiểm','Bảo hiểm phi nhân thọ','Quốc gia','Bộ Tài chính',
         'Làm thế nào để yêu cầu bồi thường bảo hiểm tai nạn xe máy?',
         'Thủ tục yêu cầu bồi thường: (1) Thông báo ngay cho công ty bảo hiểm (hotline in trên thẻ/giấy chứng nhận); (2) Cung cấp: biên bản tai nạn của công an, giấy chứng nhận thương tích/tử vong, giấy đăng ký xe, giấy phép lái xe; (3) Điền đơn yêu cầu bồi thường; (4) Công ty giải quyết trong vòng 15 ngày kể từ khi nhận đủ hồ sơ.'),
        ('bh006','Bảo hiểm','Bảo hiểm sức khỏe','Quốc gia','Bộ Tài chính',
         'Bảo hiểm sức khỏe tư nhân khác bảo hiểm y tế nhà nước như thế nào?',
         'BHYT nhà nước: bắt buộc, phí thấp, thanh toán theo % chi phí điều trị tại cơ sở được chỉ định, có trần bồi thường theo quy định. Bảo hiểm sức khỏe tư nhân: tự nguyện, phí cao hơn, thường bồi thường chi phí thực tế (viện phí, phẫu thuật, thuốc), có thể khám bất kỳ bệnh viện nào, một số gói chi trả cả nha khoa, thị lực. Hai loại có thể bổ sung cho nhau.'),
        ('bh007','Bảo hiểm','Bảo hiểm nhân thọ','Quốc gia','Cục Quản lý Bảo hiểm',
         'Làm sao biết công ty bảo hiểm có được cấp phép hợp pháp không?',
         'Kiểm tra danh sách công ty bảo hiểm được cấp phép tại website của Cục Quản lý, giám sát bảo hiểm (iacvn.gov.vn) thuộc Bộ Tài chính. Hiện có khoảng 18 công ty bảo hiểm nhân thọ và 30+ công ty bảo hiểm phi nhân thọ được cấp phép hoạt động tại Việt Nam.'),
        ('bh008','Bảo hiểm','Khiếu nại bảo hiểm','Quốc gia','Cục Quản lý Bảo hiểm',
         'Khiếu nại khi công ty bảo hiểm từ chối bồi thường oan?',
         'Bước 1: Gửi khiếu nại bằng văn bản đến bộ phận giải quyết khiếu nại của công ty bảo hiểm. Bước 2: Nếu không đồng ý, khiếu nại lên Cục Quản lý giám sát bảo hiểm (Bộ Tài chính). Bước 3: Khởi kiện ra Tòa án nhân dân. Lưu giữ đầy đủ hợp đồng, biên lai đóng phí và văn bản từ chối của công ty làm bằng chứng.'),
    ])

    # 2. Quyền người tiêu dùng
    w('faq_g_quyen_tieu_dung.xlsx', [
        ('qtd001','Quyền người tiêu dùng','Bảo vệ quyền lợi','Quốc gia','Bộ Công Thương',
         'Quyền cơ bản của người tiêu dùng theo pháp luật Việt Nam là gì?',
         'Theo Luật Bảo vệ quyền lợi người tiêu dùng, 8 quyền cơ bản gồm: (1) An toàn tính mạng, sức khỏe, tài sản; (2) Được cung cấp thông tin đầy đủ, chính xác; (3) Lựa chọn hàng hóa/dịch vụ; (4) Góp ý về hàng hóa; (5) Khiếu nại, tố cáo; (6) Bồi thường thiệt hại; (7) Được tư vấn hỗ trợ; (8) Hợp đồng công bằng, minh bạch.'),
        ('qtd002','Quyền người tiêu dùng','Mua hàng online','Quốc gia','Bộ Công Thương',
         'Khi mua hàng online nhận được hàng giả, hàng kém chất lượng phải làm gì?',
         'Thực hiện theo thứ tự: (1) Liên hệ người bán/sàn thương mại điện tử yêu cầu đổi trả hoặc hoàn tiền trong thời gian bảo hành/đổi trả; (2) Tố cáo sàn TMĐT lên Bộ Công Thương qua Cổng thông tin quản lý hoạt động TMĐT (online.gov.vn); (3) Tố cáo lên Cục Quản lý thị trường; (4) Khởi kiện ra Tòa nếu thiệt hại lớn. Giữ lại ảnh chụp, hóa đơn, video khi mở hàng làm bằng chứng.'),
        ('qtd003','Quyền người tiêu dùng','Hoàn trả hàng','Quốc gia','Bộ Công Thương',
         'Khi mua hàng trực tuyến, người tiêu dùng có quyền đổi trả trong bao nhiêu ngày?',
         'Theo quy định, người tiêu dùng có quyền đơn phương chấm dứt hợp đồng mua bán từ xa trong vòng 14 ngày làm việc kể từ khi nhận hàng, không cần lý do (trừ các mặt hàng đặc biệt như đồ tươi sống, sản phẩm kỹ thuật số đã tải xuống). Chi phí hoàn trả do hai bên thỏa thuận, nếu không thỏa thuận thì người tiêu dùng chịu.'),
        ('qtd004','Quyền người tiêu dùng','Khiếu nại','Quốc gia','Hội Bảo vệ NTD',
         'Liên hệ đâu để được hỗ trợ giải quyết tranh chấp về quyền lợi người tiêu dùng?',
         'Các kênh hỗ trợ: (1) Tổng đài 1800 6838 (miễn phí) của Cục Cạnh tranh và Bảo vệ người tiêu dùng (VCCA); (2) Hội Bảo vệ quyền lợi người tiêu dùng tỉnh/thành phố; (3) Nộp đơn trực tuyến tại dichvucong.gov.vn; (4) Yêu cầu hòa giải qua VCCA. Hòa giải thường nhanh và hiệu quả hơn khởi kiện.'),
        ('qtd005','Quyền người tiêu dùng','Hàng giả','Quốc gia','Cục Quản lý thị trường',
         'Tố cáo hàng giả, hàng nhái ở đâu?',
         'Tố cáo hàng giả, hàng nhái qua: (1) Tổng đài 1800 599 961 (miễn phí) của Tổng cục Quản lý thị trường; (2) App hoặc website qltt.gov.vn; (3) Trực tiếp đến Chi cục Quản lý thị trường tại địa phương; (4) Phản ánh qua Zalo OA "Quản lý thị trường". Khi tố cáo cần cung cấp tên/địa chỉ người bán, ảnh chụp hàng hóa, hóa đơn mua hàng.'),
        ('qtd006','Quyền người tiêu dùng','Dịch vụ viễn thông','Quốc gia','Bộ TT&TT',
         'Nhà mạng trừ tiền điện thoại không rõ lý do phải làm gì?',
         'Bước 1: Liên hệ tổng đài nhà mạng (Viettel: 198, Vinaphone: 1800 1091, Mobifone: 9090) yêu cầu giải thích và hoàn tiền. Bước 2: Nếu không giải quyết, phản ánh lên Cục Viễn thông (VNPT) qua dichvucong.gov.vn hoặc Bộ Thông tin & Truyền thông. Bước 3: Tố cáo tới Cục Quản lý thị trường. Giữ tin nhắn trừ tiền và lịch sử giao dịch làm bằng chứng.'),
    ])

    # 3. Sở hữu trí tuệ
    w('faq_g_so_huu_tri_tue.xlsx', [
        ('shtt001','Sở hữu trí tuệ','Bản quyền','Quốc gia','Bộ VHTTDL',
         'Bản quyền tác giả được bảo hộ tự động hay phải đăng ký?',
         'Theo Luật Sở hữu trí tuệ Việt Nam, quyền tác giả phát sinh tự động ngay khi tác phẩm được sáng tạo và thể hiện dưới hình thức vật chất nhất định — không cần đăng ký. Tuy nhiên, đăng ký tại Cục Bản quyền tác giả (Bộ VHTTDL) sẽ tạo ra bằng chứng pháp lý vững chắc khi xảy ra tranh chấp. Phí đăng ký từ 100.000–500.000 đồng tùy loại tác phẩm.'),
        ('shtt002','Sở hữu trí tuệ','Bản quyền','Quốc gia','Bộ VHTTDL',
         'Bảo hộ quyền tác giả kéo dài bao lâu?',
         'Quyền nhân thân (đặt tên, công nhận là tác giả, bảo vệ toàn vẹn tác phẩm) được bảo hộ vĩnh viễn. Quyền tài sản (sao chép, phân phối, truyền đạt tác phẩm) được bảo hộ trong 75 năm kể từ khi tác giả qua đời (hoặc 75 năm từ ngày công bố nếu là tác phẩm điện ảnh, nhiếp ảnh, mỹ thuật ứng dụng, tác phẩm khuyết danh).'),
        ('shtt003','Sở hữu trí tuệ','Nhãn hiệu','Quốc gia','Cục SHTT',
         'Đăng ký nhãn hiệu ở đâu và thời gian bao lâu?',
         'Nộp đơn đăng ký nhãn hiệu tại Cục Sở hữu trí tuệ (Bộ KH&CN), địa chỉ: 384–386 Nguyễn Trãi, Thanh Xuân, Hà Nội; hoặc nộp trực tuyến tại ipvietnam.gov.vn. Quy trình: thẩm định hình thức (1–2 tháng) → thẩm định nội dung (9–12 tháng) → cấp văn bằng. Tổng thời gian khoảng 12–18 tháng. Phí nộp đơn từ 180.000 đồng/nhóm hàng hóa.'),
        ('shtt004','Sở hữu trí tuệ','Nhãn hiệu','Quốc gia','Cục SHTT',
         'Bằng độc quyền nhãn hiệu có hiệu lực bao lâu?',
         'Bằng độc quyền nhãn hiệu có hiệu lực 10 năm kể từ ngày nộp đơn, có thể gia hạn nhiều lần, mỗi lần 10 năm. Phí gia hạn phải nộp trong vòng 6 tháng trước khi hết hạn (hoặc thêm 6 tháng gia hạn muộn với phí phụ).'),
        ('shtt005','Sở hữu trí tuệ','Sáng chế','Quốc gia','Cục SHTT',
         'Điều kiện để được cấp bằng độc quyền sáng chế là gì?',
         'Sáng chế được bảo hộ khi đáp ứng 3 điều kiện: (1) Tính mới — chưa bị bộc lộ công khai trước ngày nộp đơn; (2) Trình độ sáng tạo — không hiển nhiên đối với người có trình độ thông thường trong lĩnh vực đó; (3) Khả năng áp dụng công nghiệp — có thể sản xuất/sử dụng trong thực tế. Bằng sáng chế có hiệu lực 20 năm từ ngày nộp đơn.'),
        ('shtt006','Sở hữu trí tuệ','Vi phạm bản quyền','Quốc gia','Cục SHTT',
         'Xử lý thế nào khi bị vi phạm bản quyền online?',
         'Biện pháp xử lý vi phạm bản quyền trực tuyến: (1) Yêu cầu nền tảng (YouTube, Facebook, TikTok) gỡ nội dung vi phạm qua công cụ DMCA Takedown; (2) Gửi thư yêu cầu chấm dứt vi phạm (cease and desist) đến người vi phạm; (3) Tố cáo đến Thanh tra Bộ VHTTDL hoặc Cục SHTT; (4) Khởi kiện dân sự ra Tòa án để đòi bồi thường thiệt hại.'),
    ])

    # 4. Chuyển đổi số / DVC trực tuyến
    w('faq_g_chuyen_doi_so.xlsx', [
        ('cds001','Chuyển đổi số','Dịch vụ công trực tuyến','Quốc gia','Bộ TT&TT',
         'Cổng dịch vụ công quốc gia là gì và cách đăng ký tài khoản?',
         'Cổng Dịch vụ công quốc gia (dichvucong.gov.vn) là nền tảng tích hợp dịch vụ hành chính công trực tuyến toàn quốc. Để đăng ký: truy cập dichvucong.gov.vn → Đăng ký → Điền thông tin CCCD/CMND → Xác thực qua SMS OTP hoặc VNeID. Sau đó có thể nộp hồ sơ, theo dõi tiến độ, nhận kết quả trực tuyến với hàng nghìn dịch vụ công.'),
        ('cds002','Chuyển đổi số','Dịch vụ công trực tuyến','Quốc gia','Bộ TT&TT',
         'Hồ sơ điện tử nộp qua cổng DVC có giá trị pháp lý như bản giấy không?',
         'Có. Theo Nghị định 45/2020/NĐ-CP, hồ sơ điện tử được nộp hợp lệ qua Cổng DVC quốc gia hoặc cổng DVC tỉnh/thành có đầy đủ giá trị pháp lý như hồ sơ giấy. Kết quả giải quyết thủ tục hành chính cũng có thể được trả dưới dạng bản điện tử có chữ ký số của cơ quan nhà nước — có giá trị tương đương bản giấy.'),
        ('cds003','Chuyển đổi số','VNeID','Quốc gia','Bộ Công an',
         'Ứng dụng VNeID dùng để làm gì và cách đăng ký?',
         'VNeID là ứng dụng định danh điện tử quốc gia do Bộ Công an phát triển, cho phép: lưu CCCD điện tử thay thế thẻ vật lý, nộp hồ sơ trực tuyến, thanh toán phí, tra cứu thông tin cá nhân, đăng nhập DVC không cần mật khẩu. Đăng ký: tải app VNeID → nhập số CCCD → chụp ảnh khuôn mặt → chờ xác thực từ Công an (Level 1 tự đăng ký; Level 2 cần đến công an phường xác thực sinh trắc học).'),
        ('cds004','Chuyển đổi số','Chữ ký số','Quốc gia','Bộ TT&TT',
         'Chữ ký số cá nhân dùng để làm gì và mua ở đâu?',
         'Chữ ký số cá nhân dùng để ký văn bản điện tử có giá trị pháp lý (hợp đồng điện tử, khai thuế, nộp hồ sơ DVC mức độ 4). Mua tại các tổ chức cung cấp dịch vụ chứng thực chữ ký số được Bộ TT&TT cấp phép như: VGCA, Newtel, VNPT-CA, Viettel-CA, FPT-CA. Phí khoảng 700.000–1.500.000 đồng/2 năm. Hiện cũng có thể dùng chữ ký số miễn phí qua VNeID Level 2.'),
        ('cds005','Chuyển đổi số','Thanh toán không dùng tiền mặt','Quốc gia','NHNN',
         'Các phương thức thanh toán không dùng tiền mặt phổ biến hiện nay là gì?',
         'Các phương thức TTKDTM phổ biến: (1) Chuyển khoản ngân hàng (internet banking, mobile banking); (2) QR Code (VietQR chuẩn liên ngân hàng); (3) Ví điện tử (MoMo, ZaloPay, VNPay, ShopeePay); (4) Thẻ ngân hàng (Visa, Mastercard, nội địa); (5) Mobile Money (Viettel Money, Vinaphone Money). Phí chuyển khoản thường miễn phí hoặc rất thấp hiện nay.'),
        ('cds006','Chuyển đổi số','An toàn thông tin','Quốc gia','Bộ TT&TT',
         'Bị lừa đảo trực tuyến (scam online) cần báo ở đâu?',
         'Khi bị lừa đảo trực tuyến: (1) Báo ngay cho ngân hàng để phong tỏa tài khoản nếu bị mất tiền; (2) Trình báo công an nơi cư trú hoặc công an huyện/quận; (3) Phản ánh qua Cổng thông tin 156.gov.vn (Bộ TT&TT) chuyên về lừa đảo mạng; (4) Tố cáo tại Cục An ninh mạng và phòng chống tội phạm sử dụng công nghệ cao (Bộ Công an). Giữ toàn bộ bằng chứng: ảnh chụp màn hình, số tài khoản nhận tiền, tin nhắn liên lạc.'),
        ('cds007','Chuyển đổi số','Dữ liệu cá nhân','Quốc gia','Bộ TT&TT',
         'Quyền của cá nhân đối với dữ liệu cá nhân theo pháp luật Việt Nam?',
         'Theo Nghị định 13/2023/NĐ-CP, cá nhân có các quyền: (1) Biết dữ liệu của mình đang được xử lý; (2) Đồng ý hoặc không đồng ý cho xử lý; (3) Xem, chỉnh sửa dữ liệu không chính xác; (4) Xóa dữ liệu (quyền được quên); (5) Hạn chế xử lý; (6) Phản đối xử lý trong trường hợp nhất định; (7) Khiếu nại khi vi phạm. Tổ chức thu thập dữ liệu phải có sự đồng ý rõ ràng và thông báo mục đích sử dụng.'),
    ])

    # 5. Nhà ở, chung cư
    w('faq_g_nha_o.xlsx', [
        ('nho001','Nhà ở','Mua bán nhà đất','Quốc gia','Bộ Xây dựng',
         'Hợp đồng mua bán nhà ở có bắt buộc công chứng không?',
         'Có. Theo Luật Nhà ở 2014 và Luật Kinh doanh bất động sản 2023, hợp đồng mua bán, tặng cho, đổi nhà ở giữa cá nhân phải được công chứng hoặc chứng thực. Nếu mua nhà của doanh nghiệp kinh doanh BĐS thì không bắt buộc công chứng nhưng vẫn nên thực hiện để đảm bảo an toàn pháp lý.'),
        ('nho002','Nhà ở','Chung cư','Quốc gia','Bộ Xây dựng',
         'Ban quản trị chung cư được thành lập như thế nào?',
         'Ban quản trị nhà chung cư được thành lập tại hội nghị nhà chung cư lần đầu (tổ chức khi tòa nhà đạt ít nhất 50% số căn đã bàn giao và cư dân đã về ở). Hội nghị bầu Ban quản trị gồm 3–15 thành viên (tùy số căn hộ). Ban quản trị có nhiệm kỳ 3 năm, đại diện cho cư dân trong quan hệ với Ban quản lý/chủ đầu tư, quản lý quỹ bảo trì.'),
        ('nho003','Nhà ở','Chung cư','Quốc gia','Bộ Xây dựng',
         'Phí bảo trì chung cư 2% là gì và ai được giữ?',
         'Khi mua căn hộ chung cư, người mua phải đóng 2% giá trị hợp đồng mua bán vào quỹ bảo trì. Quỹ này dùng để bảo trì các phần sở hữu chung của tòa nhà. Chủ đầu tư tạm giữ đến khi Ban quản trị được thành lập, sau đó phải bàn giao toàn bộ quỹ trong vòng 7 ngày làm việc. Nếu chủ đầu tư không bàn giao, Ban quản trị có thể khiếu nại đến Sở Xây dựng để cưỡng chế bàn giao.'),
        ('nho004','Nhà ở','Thuê nhà','Quốc gia','Bộ Xây dựng',
         'Hợp đồng thuê nhà có cần công chứng không? Thời hạn tối thiểu để phải đăng ký là bao nhiêu?',
         'Hợp đồng thuê nhà dưới 6 tháng không bắt buộc công chứng và không cần đăng ký. Hợp đồng thuê nhà từ 6 tháng trở lên cần đăng ký với UBND phường/xã nơi có nhà thuê. Công chứng không bắt buộc nhưng được khuyến khích để bảo vệ quyền lợi cả hai bên. Người thuê nhà có quyền được biết trước ít nhất 3 tháng nếu chủ nhà muốn lấy lại nhà trước hạn.'),
        ('nho005','Nhà ở','Mua bán nhà đất','Quốc gia','Bộ Xây dựng',
         'Người nước ngoài có được mua nhà ở tại Việt Nam không?',
         'Có, theo Luật Nhà ở 2023 (hiệu lực từ 1/1/2025), người nước ngoài được phép sở hữu nhà ở tại Việt Nam khi: (1) Được phép nhập cảnh vào Việt Nam; (2) Nhà ở là căn hộ chung cư hoặc nhà ở riêng lẻ trong dự án BĐS; (3) Không phải khu vực an ninh quốc phòng. Thời hạn sở hữu là 50 năm, có thể gia hạn thêm 50 năm. Số lượng nhà người nước ngoài được mua không quá 30% tòa nhà hoặc 250 căn/phường.'),
        ('nho006','Nhà ở','Tranh chấp nhà đất','Quốc gia','Bộ Xây dựng',
         'Tranh chấp về ranh giới đất với hàng xóm giải quyết thế nào?',
         'Quy trình giải quyết: (1) Thương lượng trực tiếp với hàng xóm; (2) Hòa giải tại UBND phường/xã — bắt buộc trước khi khởi kiện; (3) Nếu hòa giải không thành, khởi kiện tại Tòa án nhân dân cấp huyện nơi có đất. Khi tranh chấp, cần chuẩn bị: Giấy chứng nhận QSDĐ, bản đồ địa chính, hồ sơ mua bán/thừa kế trước đây. Có thể yêu cầu cơ quan đo đạc địa chính tiến hành đo đạc làm cơ sở phân định.'),
    ])

    # 6. Thủ tục công an
    w('faq_g_cong_an.xlsx', [
        ('ca001','Công an','Báo mất giấy tờ','Quốc gia','Bộ Công an',
         'Mất CCCD cần làm gì ngay lập tức?',
         'Khi mất CCCD: (1) Trình báo ngay đến công an xã/phường/thị trấn nơi cư trú để được cấp giấy xác nhận mất CCCD; (2) Thông báo cho ngân hàng để đề phòng bị lạm dụng; (3) Nộp hồ sơ làm lại CCCD tại công an cấp huyện hoặc qua cổng DVC trực tuyến; hồ sơ gồm: đơn khai báo mất + ảnh 4x6. Phí cấp lại: 70.000 đồng. Thời gian làm lại: 7 ngày làm việc (cấp huyện) hoặc 20 ngày (qua bưu điện).'),
        ('ca002','Công an','Báo mất giấy tờ','Quốc gia','Bộ Công an',
         'Mất Sổ hộ khẩu (hoặc giấy tờ cư trú) cần làm gì?',
         'Từ 1/7/2021, Sổ hộ khẩu giấy đã chính thức bị bãi bỏ — thông tin hộ khẩu được lưu trên Cơ sở dữ liệu quốc gia về dân cư. Bạn không cần lo lắng về "mất sổ hộ khẩu" nữa. Thay vào đó, khi cần chứng minh cư trú, bạn xuất trình CCCD (có chip) hoặc in "Giấy xác nhận thông tin cư trú" miễn phí từ VNeID hoặc tại công an phường/xã.'),
        ('ca003','Công an','Xin lý lịch tư pháp','Quốc gia','Bộ Tư pháp',
         'Lý lịch tư pháp (phiếu số 1) xin ở đâu và mất bao lâu?',
         'Xin lý lịch tư pháp (phiếu số 1 — dành cho cá nhân) tại: Sở Tư pháp nơi thường trú hoặc tạm trú; hoặc nộp trực tuyến qua dichvucong.gov.vn. Hồ sơ: Đơn theo mẫu + bản sao CCCD/CMND. Phí: 200.000 đồng. Thời gian: 5 ngày làm việc (thường trú) hoặc 10 ngày (qua bưu điện). Kết quả có thể nhận bản điện tử hoặc bản giấy.'),
        ('ca004','Công an','Phòng cháy chữa cháy','Quốc gia','Cảnh sát PCCC',
         'Hộ gia đình cần trang bị phòng cháy chữa cháy tối thiểu những gì?',
         'Theo Thông tư 148/2020/TT-BCA, hộ gia đình phải có: (1) Bình chữa cháy xách tay (bột hoặc CO2); (2) Dụng cụ thoát hiểm (thang dây hoặc búa phá cửa). Nên bổ sung: đầu báo khói, đèn pin khẩn cấp, mặt nạ chống khói. Bình chữa cháy cần kiểm tra áp suất định kỳ và nạp lại/thay mới theo hướng dẫn của nhà sản xuất.'),
        ('ca005','Công an','Tố giác tội phạm','Quốc gia','Bộ Công an',
         'Tố giác tội phạm bằng cách nào và có được bảo vệ không?',
         'Tố giác tội phạm qua: (1) Gọi 113 (Cảnh sát khẩn cấp); (2) Đến trực tiếp cơ quan điều tra (công an phường/huyện/tỉnh); (3) Gửi đơn qua bưu điện; (4) Tố giác qua Cổng tiếp nhận tố giác của Bộ Công an. Người tố giác được pháp luật bảo vệ theo Luật Tố cáo 2018 — cơ quan tiếp nhận có trách nhiệm giữ bí mật danh tính. Nếu có dấu hiệu bị đe dọa trả thù, yêu cầu cơ quan công an áp dụng biện pháp bảo vệ.'),
        ('ca006','Công an','Công chứng và xác nhận','Quốc gia','Bộ Tư pháp',
         'Giấy tờ nào cần xác nhận của công an phường, giấy tờ nào cần UBND phường?',
         'Công an phường xác nhận: lý lịch bản thân (nơi thường trú cũ), xác nhận mất giấy tờ, xác nhận nhân thân phục vụ tuyển dụng công an/quân đội. UBND phường xác nhận: xác nhận thông tin hộ khẩu, xác nhận tình trạng hôn nhân, xác nhận thu nhập, xác nhận đơn xin phép xây dựng, chứng thực bản sao, chứng thực chữ ký. Hiện nhiều loại xác nhận đã được tích hợp vào hệ thống điện tử, có thể làm trực tuyến.'),
    ])

    # 7. Phúc lợi xã hội
    w('faq_g_phuc_loi.xlsx', [
        ('pl001','Phúc lợi xã hội','Trợ cấp người khuyết tật','Quốc gia','Bộ LĐTBXH',
         'Người khuyết tật được hưởng những quyền lợi gì từ nhà nước?',
         'Người khuyết tật được hưởng: (1) Trợ cấp xã hội hàng tháng (từ 360.000–900.000 đồng/tháng tùy mức độ khuyết tật và hoàn cảnh); (2) Cấp thẻ BHYT miễn phí; (3) Miễn/giảm học phí; (4) Vay vốn ưu đãi học nghề và tạo việc làm; (5) Ưu tiên tiếp cận giao thông, công trình công cộng; (6) Hỗ trợ dụng cụ chỉnh hình. Mức trợ cấp và điều kiện cụ thể theo Nghị định 20/2021/NĐ-CP.'),
        ('pl002','Phúc lợi xã hội','Trợ cấp người khuyết tật','Quốc gia','Bộ LĐTBXH',
         'Thủ tục xin xác nhận khuyết tật để hưởng trợ cấp?',
         'Thủ tục: (1) Đến UBND xã/phường nơi cư trú nộp đơn đề nghị xác định mức độ khuyết tật; (2) Hội đồng xác định mức độ khuyết tật (gồm y tế, giáo dục, xã hội) thực hiện xác định; (3) Nhận Giấy xác nhận khuyết tật; (4) Nộp hồ sơ đề nghị trợ cấp xã hội tại UBND xã/phường. Thời gian xử lý: 20 ngày làm việc. Không mất phí.'),
        ('pl003','Phúc lợi xã hội','Trẻ em','Quốc gia','Bộ LĐTBXH',
         'Trẻ em mồ côi được hỗ trợ những gì?',
         'Trẻ em mồ côi (mất cả cha lẫn mẹ, hoặc mồ côi cha/mẹ mà người còn lại không còn khả năng nuôi dưỡng) được: (1) Trợ cấp xã hội hàng tháng theo nhóm tuổi (dưới 4 tuổi: 900.000 đồng; 4–16 tuổi: 540.000 đồng); (2) Cấp thẻ BHYT miễn phí; (3) Miễn học phí; (4) Ưu tiên được nhận vào cơ sở bảo trợ xã hội. Gia đình nhận nuôi trẻ mồ côi cũng được hỗ trợ kinh phí chăm sóc.'),
        ('pl004','Phúc lợi xã hội','Người cao tuổi','Quốc gia','Bộ LĐTBXH',
         'Người cao tuổi từ 80 tuổi trở lên được nhận trợ cấp không?',
         'Người từ đủ 80 tuổi trở lên không có lương hưu, trợ cấp BHXH, trợ cấp người có công hoặc trợ cấp xã hội khác được hưởng trợ cấp xã hội hàng tháng tối thiểu 360.000 đồng/tháng. Người từ 80 tuổi không có người phụng dưỡng sẽ được xem xét cấp thêm hỗ trợ. Hồ sơ nộp tại UBND xã/phường nơi cư trú.'),
        ('pl005','Phúc lợi xã hội','Hộ nghèo','Quốc gia','Bộ LĐTBXH',
         'Chuẩn nghèo đa chiều giai đoạn 2022–2025 là bao nhiêu?',
         'Theo Nghị định 07/2021/NĐ-CP, chuẩn nghèo đa chiều 2022–2025: Khu vực nông thôn: thu nhập dưới 1.500.000 đồng/người/tháng; Khu vực thành thị: thu nhập dưới 2.000.000 đồng/người/tháng. Ngoài ra còn đánh giá thiếu hụt theo 6 chiều dịch vụ xã hội cơ bản (việc làm, y tế, giáo dục, nhà ở, nước sạch, thông tin). Đủ điều kiện về thu nhập VÀ thiếu hụt từ 3 chiều trở lên mới được xếp là hộ nghèo.'),
        ('pl006','Phúc lợi xã hội','Hộ nghèo','Quốc gia','Bộ LĐTBXH',
         'Hộ nghèo được miễn/giảm những loại phí, lệ phí gì?',
         'Hộ nghèo được: (1) Miễn 100% BHYT (nhà nước đóng thay); (2) Miễn học phí cho con em từ mầm non đến THCS; (3) Miễn phí đăng ký cư trú, hộ khẩu, CCCD; (4) Giảm tiền điện theo chương trình hỗ trợ (khoảng 50.000–100.000 đồng/tháng); (5) Được vay vốn ưu đãi từ Ngân hàng Chính sách xã hội lãi suất thấp; (6) Ưu tiên các chương trình nhà ở xã hội. Điều kiện cụ thể tra tại UBND xã/phường.'),
    ])

    print('\nBatch 8 hoan thanh.')

if __name__ == '__main__':
    main()
