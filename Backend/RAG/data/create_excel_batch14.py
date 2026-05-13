"""Batch 14 — điền đủ 500: tài chính cá nhân, y tế tâm thần, khởi nghiệp, văn bằng chứng chỉ."""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent

def w(filename, rows):
    df = pd.DataFrame(rows, columns=['id','category','procedure','level','source','question','answer'])
    with pd.ExcelWriter(OUT / filename, engine='openpyxl') as xw:
        df.to_excel(xw, sheet_name='FAQ', index=False)
    print(f'+ {filename} ({len(df)} rows)')

def main():
    w('faq_g_tai_chinh_ca_nhan.xlsx', [
        ('tcn001','Tài chính cá nhân','Tiết kiệm','Quốc gia','NHNN',
         'Tiền gửi tiết kiệm tại ngân hàng được bảo hiểm bao nhiêu?',
         'Theo Luật Bảo hiểm tiền gửi và Nghị định hiện hành, số tiền bảo hiểm tiền gửi tối đa là 125 triệu đồng/người/ngân hàng. Nếu ngân hàng phá sản, Bảo hiểm tiền gửi Việt Nam (DIV) chi trả tối đa 125 triệu/người bất kể số dư thực tế. Để an toàn: chia tiền gửi qua nhiều ngân hàng nếu số dư vượt 125 triệu. Bảo hiểm áp dụng cho: tiền gửi tiết kiệm, tiền gửi thanh toán, chứng chỉ tiền gửi; không áp dụng cho: tiền gửi của ngân hàng khác, tiền gửi bảo đảm thực hiện nghĩa vụ.'),
        ('tcn002','Tài chính cá nhân','Vay tiêu dùng','Quốc gia','NHNN',
         'Vay tín chấp (tín dụng tiêu dùng) cần điều kiện gì và lãi suất thế nào?',
         'Vay tín chấp cá nhân tại ngân hàng/công ty tài chính: Điều kiện: có nguồn thu nhập ổn định (lương, kinh doanh), lịch sử tín dụng tốt (CIC), tuổi từ 22–60, chứng minh thu nhập (bảng lương, hợp đồng lao động, sao kê tài khoản). Lãi suất: ngân hàng: 10–20%/năm; công ty tài chính (FE Credit, Home Credit, Mcredit): 25–45%/năm. Hạn mức: thường đến 8–10 lần thu nhập tháng. Cảnh báo: không vay qua app không rõ nguồn gốc — có thể là tín dụng đen hoặc lừa đảo.'),
        ('tcn003','Tài chính cá nhân','Tín dụng đen','Quốc gia','NHNN',
         'Nhận biết và tố cáo tín dụng đen như thế nào?',
         'Dấu hiệu tín dụng đen: (1) Cho vay không cần giấy tờ, giải ngân ngay; (2) Lãi suất "hấp dẫn" nhưng có phí ẩn đẩy lãi thực lên hàng trăm %/năm; (3) Đòi nợ bằng cách đe dọa, quấy rối (gọi điện liên tục, đến nhà); (4) Yêu cầu giữ CCCD, sổ đỏ làm tin. Tố cáo tín dụng đen: Công an huyện/tỉnh hoặc Cục CSHS Bộ Công an; đường dây nóng 113; Ngân hàng Nhà nước chi nhánh tỉnh/TP. Nếu bị đòi nợ kiểu xã hội đen: gọi 113 ngay.'),
        ('tcn004','Tài chính cá nhân','Lập kế hoạch tài chính','Quốc gia','Bộ Tài chính',
         'Quy tắc 50/30/20 trong quản lý tài chính cá nhân là gì?',
         'Quy tắc 50/30/20 là phương pháp phân bổ thu nhập: 50% cho nhu cầu thiết yếu (nhà ở, ăn uống, đi lại, hóa đơn điện nước); 30% cho mong muốn (giải trí, mua sắm không thiết yếu, du lịch); 20% để tiết kiệm và đầu tư (quỹ khẩn cấp, hưu trí, đầu tư). Mục tiêu: xây dựng quỹ khẩn cấp 3–6 tháng chi phí sinh hoạt, sau đó đầu tư dài hạn. Có thể điều chỉnh tỷ lệ tùy thu nhập — thu nhập thấp ưu tiên cắt giảm "muốn" trước.'),
        ('tcn005','Tài chính cá nhân','Hưu trí','Quốc gia','BHXH VN',
         'Lương hưu được tính như thế nào và tối thiểu bao nhiêu năm đóng BHXH?',
         'Điều kiện hưởng lương hưu: nam từ 61 tuổi, nữ từ 56 tuổi (theo lộ trình tăng dần đến 62 và 60 tuổi); đóng BHXH tối thiểu 20 năm. Tỷ lệ hưởng: mỗi năm đóng đủ được 2,25% (nữ) hoặc 2% (nam) mức bình quân lương đóng BHXH, tối đa 75%. Mức lương hưu tối thiểu: không thấp hơn mức lương tối thiểu vùng. Nếu đóng đủ 15–20 năm và chưa đủ tuổi: nhận lương hưu muộn hơn hoặc nhận BHXH 1 lần. Tra cứu thông tin BHXH tại baohiemxahoi.gov.vn.'),
        ('tcn006','Tài chính cá nhân','Vay mua nhà','Quốc gia','NHNN',
         'Vay ngân hàng mua nhà — những điều cần biết trước khi ký hợp đồng?',
         'Trước khi ký hợp đồng vay mua nhà: (1) So sánh lãi suất: ưu đãi cố định (thường 6–9%/năm) bao nhiêu tháng, sau đó lãi suất thả nổi là bao nhiêu; (2) Tính khả năng trả nợ: tiền trả hàng tháng không nên quá 30–40% thu nhập; (3) Đọc kỹ điều kiện phạt trả nợ trước hạn (thường 1–3% số dư khi trả trước trong 3–5 năm đầu); (4) Chi phí phát sinh: phí định giá, phí thẩm định, phí bảo hiểm nhân thọ liên kết vay, phí công chứng; (5) Xem mục "điều chỉnh lãi suất" — ngân hàng điều chỉnh theo kỳ nào (3, 6, hay 12 tháng/lần).'),
    ])

    w('faq_g_suc_khoe_tam_than.xlsx', [
        ('sktt001','Y tế','Sức khỏe tâm thần','Quốc gia','Bộ Y tế',
         'Trầm cảm có phải bệnh thực sự không và điều trị ở đâu?',
         'Có, trầm cảm là bệnh tâm thần thực sự, được WHO công nhận và có phác đồ điều trị hiệu quả. Triệu chứng: buồn bã kéo dài >2 tuần, mất hứng thú mọi thứ, mệt mỏi, khó tập trung, rối loạn ngủ, có thể có ý nghĩ tự làm hại bản thân. Điều trị tại: khoa Tâm thần bệnh viện đa khoa tỉnh/TP; Bệnh viện Tâm thần trung ương (Hà Nội, TP.HCM); phòng khám tâm lý tư. Phương pháp: tâm lý trị liệu (CBT), thuốc chống trầm cảm, hoặc kết hợp. BHYT thanh toán điều trị trầm cảm tại bệnh viện công. Đường dây hỗ trợ tâm lý: 1800 599 920.'),
        ('sktt002','Y tế','Sức khỏe tâm thần','Quốc gia','Bộ Y tế',
         'Ai được hưởng chế độ khám chữa bệnh BHYT cho bệnh tâm thần?',
         'Người bệnh tâm thần có thẻ BHYT được: (1) Khám và điều trị tại cơ sở y tế đúng tuyến; (2) BHYT thanh toán theo quy định — thường 80–100% chi phí tùy mức đóng; (3) Điều trị nội trú bệnh viện tâm thần: BHYT thanh toán; (4) Thuốc tâm thần trong danh mục BHYT được thanh toán. Người bệnh tâm thần phân liệt, rối loạn lưỡng cực nặng được điều trị dài hạn theo chương trình mục tiêu y tế quốc gia, miễn phí thuốc tại trạm y tế xã/phường (thuốc do Nhà nước cấp).'),
        ('sktt003','Y tế','Sức khỏe tâm thần','Quốc gia','Bộ Y tế',
         'Người thân bị bệnh tâm thần nặng, không chịu điều trị — làm thế nào?',
         'Khi người thân bị rối loạn tâm thần nặng và không hợp tác điều trị: (1) Liên hệ bác sĩ tâm thần để tư vấn cách thuyết phục; (2) Liên hệ UBND phường/xã: theo Luật Khám bệnh chữa bệnh và Pháp lệnh Phòng chống bệnh tâm thần, chính quyền địa phương có thể hỗ trợ đưa người bệnh đi điều trị bắt buộc nếu họ nguy hiểm cho bản thân hoặc người khác; (3) Yêu cầu cơ sở y tế tâm thần tư vấn tại nhà. Không tự ý dùng vũ lực — nguy hiểm và trái pháp luật. Kiên nhẫn và tìm hỗ trợ từ chuyên gia là quan trọng nhất.'),
        ('sktt004','Y tế','Sức khỏe tâm thần','Quốc gia','Bộ Y tế',
         'Căng thẳng công việc (stress) có cần đi gặp chuyên gia tâm lý không?',
         'Nên gặp chuyên gia tâm lý khi stress ảnh hưởng đến cuộc sống: mất ngủ kéo dài, không thể tập trung làm việc, các mối quan hệ bị ảnh hưởng, có biểu hiện lo âu hoặc trầm cảm. Chuyên gia tâm lý (psychologist) khác bác sĩ tâm thần (psychiatrist): chuyên gia tâm lý không kê thuốc, tập trung tâm lý trị liệu; bác sĩ tâm thần có thể kê thuốc. Phòng khám tâm lý tư: chi phí 300.000–1.500.000 đồng/buổi. Một số tỉnh có đường dây hỗ trợ tâm lý miễn phí hoặc qua app như Youmed, Doctor Anywhere.'),
        ('sktt005','Y tế','Phòng chống tự tử','Quốc gia','Bộ Y tế',
         'Ai có thể gọi khi có ý nghĩ tự tử hoặc cần hỗ trợ tâm lý khẩn cấp?',
         'Đường dây hỗ trợ tâm lý và phòng chống tự tử tại Việt Nam: (1) Đường dây sức khỏe tâm thần quốc gia: 1800 599 920 (miễn phí, 24/7); (2) Đường dây hỗ trợ trẻ em: 111 (miễn phí, 24/7); (3) Đường dây hỗ trợ phụ nữ và trẻ em: 1800 599 920 (miễn phí); (4) Nếu nguy hiểm ngay: gọi 115 (cấp cứu) hoặc đến phòng cấp cứu bệnh viện gần nhất. Nếu thấy người khác có nguy cơ: không để họ một mình, lắng nghe, đưa đến cơ sở y tế. Nói về tự tử KHÔNG làm tăng nguy cơ — hỏi thẳng là cách giúp đỡ đúng đắn.'),
        ('sktt006','Y tế','Sức khỏe tâm thần trẻ em','Quốc gia','Bộ Y tế',
         'Trẻ em có biểu hiện tự kỷ cần được đánh giá và can thiệp như thế nào?',
         'Dấu hiệu tự kỷ sớm ở trẻ: không giao tiếp mắt, không phản hồi khi gọi tên, không chỉ tay vào vật muốn, chậm nói, lặp đi lặp lại hành vi. Bước 1: Đưa trẻ đến khoa Nhi thần kinh hoặc Tâm thần trẻ em bệnh viện để đánh giá bằng thang đo chuẩn (CARS, MCHAT). Bước 2: Nếu xác định tự kỷ: tham gia chương trình can thiệp sớm (trị liệu ngôn ngữ, ABA, hoạt động trị liệu). Can thiệp sớm trước 5 tuổi cho kết quả tốt nhất. BHYT thanh toán một phần chi phí can thiệp tại cơ sở y tế công. Một số tỉnh có trường/lớp chuyên biệt miễn phí cho trẻ tự kỷ.'),
    ])

    w('faq_g_khoi_nghiep.xlsx', [
        ('kn001','Khởi nghiệp','Startup','Quốc gia','Bộ KH&ĐT',
         'Khởi nghiệp đổi mới sáng tạo (startup) được Nhà nước hỗ trợ những gì?',
         'Hỗ trợ khởi nghiệp sáng tạo theo Quyết định 844/QĐ-TTg và Luật Hỗ trợ DNNVV: (1) Hỗ trợ tư vấn, đào tạo miễn phí qua mạng lưới hỗ trợ khởi nghiệp quốc gia; (2) Hỗ trợ thuê mặt bằng tại vườn ươm/hub khởi nghiệp; (3) Tiếp cận vốn đầu tư mạo hiểm qua Quỹ Đầu tư khởi nghiệp sáng tạo quốc gia; (4) Ưu đãi thuế cho doanh nghiệp công nghệ cao; (5) Bảo hộ quyền sở hữu trí tuệ miễn/giảm phí; (6) Kết nối với thị trường quốc tế qua các chương trình của Bộ KH&ĐT. Đăng ký tham gia hệ sinh thái khởi nghiệp: startup.gov.vn.'),
        ('kn002','Khởi nghiệp','Gọi vốn đầu tư','Quốc gia','Bộ KH&ĐT',
         'Startup Việt Nam có thể gọi vốn từ nhà đầu tư nước ngoài như thế nào?',
         'Startup Việt Nam gọi vốn nước ngoài thường qua: (1) Thiết lập cấu trúc VIE (Variable Interest Entity) hoặc lập công ty mẹ ở Singapore/Cayman để dễ nhận đầu tư quốc tế; (2) Gọi vốn trực tiếp vào công ty Việt Nam — nhà đầu tư nước ngoài phải đăng ký qua Cục Đầu tư nước ngoài; (3) Tham gia các chương trình tăng tốc quốc tế (Y Combinator, 500 Startups...). Các quỹ đầu tư mạo hiểm hoạt động tại Việt Nam: Do Ventures, Mekong Capital, Monk Hill, Vietnam Investments, Monk Hill Ventures.'),
        ('kn003','Khởi nghiệp','Mô hình kinh doanh','Quốc gia','Bộ KH&ĐT',
         'Phân biệt startup, SME (doanh nghiệp vừa nhỏ), và doanh nghiệp thông thường?',
         'Startup: doanh nghiệp mới, tập trung đổi mới sáng tạo công nghệ, mô hình kinh doanh có thể nhân rộng (scalable), mục tiêu tăng trưởng nhanh, thường cần vốn đầu tư mạo hiểm. SME: doanh nghiệp vừa và nhỏ (theo Luật Hỗ trợ DNNVV: vốn ≤100 tỷ hoặc lao động ≤200 người với siêu nhỏ/nhỏ; ≤300 tỷ/300 người với vừa) — kinh doanh ổn định, không nhất thiết đổi mới công nghệ. Doanh nghiệp thông thường: quy mô bất kỳ. SME được nhiều ưu đãi về thuế, đào tạo, tư vấn theo chính sách hỗ trợ của Nhà nước.'),
        ('kn004','Khởi nghiệp','Bảo vệ ý tưởng','Quốc gia','Cục SHTT',
         'Làm thế nào để bảo vệ ý tưởng kinh doanh và sản phẩm công nghệ?',
         'Bảo vệ ý tưởng kinh doanh: (1) Ký Thỏa thuận bảo mật thông tin (NDA) với đối tác, nhân viên; (2) Đăng ký sáng chế/giải pháp hữu ích tại Cục SHTT nếu có công nghệ độc đáo; (3) Đăng ký nhãn hiệu thương mại sớm; (4) Đăng ký bản quyền phần mềm/code (tự động có nhưng đăng ký để có bằng chứng); (5) Quản lý bí mật thương mại — hạn chế người biết thông tin nhạy cảm. Lưu ý: ý tưởng đơn thuần không được bảo hộ — chỉ có ý tưởng được thể hiện dưới dạng cụ thể (code, phương pháp, sản phẩm) mới bảo hộ được.'),
        ('kn005','Khởi nghiệp','Thất bại startup','Quốc gia','Bộ KH&ĐT',
         'Startup thất bại, nợ ngân hàng và nhà đầu tư phải xử lý thế nào?',
         'Xử lý nợ khi startup thất bại: (1) Nợ ngân hàng: thương lượng gia hạn, cơ cấu lại nợ; nếu không thể trả: ngân hàng xử lý tài sản bảo đảm; chủ công ty TNHH không chịu trách nhiệm vô hạn bằng tài sản cá nhân (trừ khi có bảo lãnh cá nhân); (2) Nợ nhà đầu tư (equity): không phải trả nếu nhà đầu tư đầu tư vốn cổ phần, không phải vay; (3) Nộp đơn xin phá sản nếu không thể tiếp tục. Bài học: tách biệt tài chính cá nhân và doanh nghiệp ngay từ đầu; không đặt tài sản cá nhân (nhà, đất) làm bảo lãnh vay nếu không chắc chắn.'),
        ('kn006','Khởi nghiệp','Thương mại hóa','Quốc gia','Bộ KH&ĐT',
         'Cách thức chuyển giao công nghệ và thương mại hóa kết quả nghiên cứu khoa học?',
         'Thương mại hóa kết quả nghiên cứu: (1) Đăng ký bảo hộ SHTT (sáng chế, giải pháp hữu ích) trước khi công bố; (2) Chuyển giao công nghệ: ký Hợp đồng chuyển giao công nghệ theo Luật Chuyển giao công nghệ 2017 — đăng ký với Bộ KH&CN nếu trị giá trên 100 triệu đồng; (3) Góp vốn bằng tài sản trí tuệ vào doanh nghiệp spinoff; (4) Nhận hỗ trợ từ Quỹ Phát triển KH&CN quốc gia (NAFOSTED) hoặc quỹ tỉnh. Trường/viện nghiên cứu công: nghiên cứu viên có thể được phân chia lợi nhuận từ thương mại hóa kết quả nghiên cứu theo quy chế riêng.'),
    ])

    w('faq_g_van_bang.xlsx', [
        ('vb001','Giáo dục','Bằng cấp chứng chỉ','Quốc gia','Bộ GD&ĐT',
         'Bằng tốt nghiệp đại học bị mất cần làm thủ tục gì?',
         'Bằng tốt nghiệp bị mất: theo quy định, bằng tốt nghiệp ĐH chỉ cấp 1 lần và không cấp lại bản gốc khi mất. Thay thế: (1) Xin "Giấy xác nhận tốt nghiệp" tại trường — có giá trị tương đương bằng gốc trong hầu hết trường hợp; (2) Hoặc xin bảng điểm có xác nhận tốt nghiệp của trường. Với bằng ĐH nước ngoài bị mất: liên hệ trường phát bằng để xin bản sao được chứng thực, sau đó hợp pháp hóa lãnh sự tại Bộ Ngoại giao Việt Nam. Bằng THPT mất: liên hệ Sở GD&ĐT nơi cấp bằng xin xác nhận.'),
        ('vb002','Giáo dục','Công nhận bằng nước ngoài','Quốc gia','Bộ GD&ĐT',
         'Bằng đại học nước ngoài được Việt Nam công nhận như thế nào?',
         'Công nhận bằng đại học nước ngoài tại Việt Nam: (1) Hợp pháp hóa lãnh sự: xin xác nhận từ cơ quan chức năng nước phát bằng, sau đó hợp pháp hóa tại Đại sứ quán/Bộ Ngoại giao Việt Nam; (2) Dịch và công chứng sang tiếng Việt; (3) Nộp hồ sơ công nhận tại Cục Quản lý chất lượng (Bộ GD&ĐT) theo Thông tư 13/2021/TT-BGDĐT; (4) Thời gian: 15–30 ngày làm việc; (5) Phí: 200.000–400.000 đồng. Một số nước có thỏa thuận song phương: công nhận tự động. Kiểm tra danh sách tại cơ sở dữ liệu Bộ GD&ĐT.'),
        ('vb003','Giáo dục','Chứng chỉ nghề','Quốc gia','Bộ LĐTBXH',
         'Các chứng chỉ kỹ năng nghề quốc gia có giá trị như thế nào?',
         'Chứng chỉ kỹ năng nghề quốc gia do Tổng cục Giáo dục nghề nghiệp cấp sau khi thi đánh giá kỹ năng. Các bậc: Bậc 1–5 (thợ bậc thấp đến cao), Bậc 6–7 (kỹ sư/chuyên gia). Giá trị: tương đương bằng cấp trong ngành, được Nhà nước công nhận để thi tuyển vào khu vực công, nâng bậc lương, thăng tiến; được một số nước ASEAN công nhận theo thỏa thuận MRA. Đăng ký thi: tại Trung tâm đánh giá kỹ năng nghề được cấp phép (tra tại kynangnghe.gov.vn).'),
        ('vb004','Giáo dục','Chứng chỉ tiếng Anh','Quốc gia','Bộ GD&ĐT',
         'Các chứng chỉ tiếng Anh nào được Việt Nam công nhận cho mục đích tuyển dụng, học thuật?',
         'Chứng chỉ tiếng Anh được công nhận tại Việt Nam: (1) IELTS: phổ biến nhất, chấp nhận rộng rãi tại trường ĐH, visa du học, xin việc; (2) TOEFL iBT: dùng nhiều cho du học Mỹ; (3) TOEIC: phổ biến trong tuyển dụng doanh nghiệp (thường yêu cầu 500–700 TOEIC); (4) Cambridge B2 First, C1 Advanced: học thuật; (5) VSTEP (Việt Nam Standard Testing Program): chứng chỉ tiếng Anh quốc gia do Bộ GD&ĐT ban hành, tương đương CEFR. Khi tuyển dụng: mỗi doanh nghiệp tự quy định yêu cầu chứng chỉ; khu vực công thường chấp nhận IELTS/TOEIC/VSTEP.'),
        ('vb005','Giáo dục','Bằng giả','Quốc gia','Bộ GD&ĐT',
         'Phát hiện sử dụng bằng giả trong tuyển dụng xử lý như thế nào?',
         'Sử dụng bằng giả trong tuyển dụng bị xử lý: (1) Hành chính: phạt 10–30 triệu đồng; (2) Hình sự: theo Điều 341 BLHS, làm giả tài liệu cơ quan Nhà nước (bao gồm bằng tốt nghiệp) bị phạt tù 6 tháng – 7 năm; (3) Hủy hợp đồng lao động vì gian lận; (4) Phải hoàn trả lương, thưởng đã nhận. Người phát hiện nhân viên dùng bằng giả: báo Cơ quan điều tra hoặc Sở GD&ĐT cơ quan phát bằng để xác minh. Tra cứu tính xác thực bằng tốt nghiệp ĐH: dichvucong.gov.vn hoặc cổng xác minh của từng trường.'),
        ('vb006','Giáo dục','Học tập suốt đời','Quốc gia','Bộ GD&ĐT',
         'Học tập suốt đời và trung tâm học tập cộng đồng có những chương trình gì?',
         'Trung tâm học tập cộng đồng (TTHTCĐ) tại xã/phường/thị trấn cung cấp: (1) Xóa mù chữ và giáo dục tiếp tục cho người lớn; (2) Dạy nghề ngắn hạn (nông nghiệp, thủ công mỹ nghệ, vi tính...); (3) Giáo dục pháp luật, sức khỏe, kỹ năng sống; (4) Các lớp học tiếng Anh, tin học miễn phí hoặc học phí thấp. Học tập suốt đời (lifelong learning) được khuyến khích qua các nền tảng trực tuyến: Coursera, edX, Kyna, Udemy (có thể có hỗ trợ phí cho người thuộc diện chính sách). Chứng chỉ học nghề ngắn hạn do trung tâm dạy nghề hoặc TTHTCĐ cấp được Nhà nước công nhận.'),
    ])

    print('\nBatch 14 hoan thanh.')

if __name__ == '__main__':
    main()
