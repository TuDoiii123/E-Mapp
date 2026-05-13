"""Batch 11 — thi hành án, du lịch, điện lực, nước sạch, vận tải."""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent

def w(filename, rows):
    df = pd.DataFrame(rows, columns=['id','category','procedure','level','source','question','answer'])
    with pd.ExcelWriter(OUT / filename, engine='openpyxl') as xw:
        df.to_excel(xw, sheet_name='FAQ', index=False)
    print(f'+ {filename} ({len(df)} rows)')

def main():
    w('faq_g_thi_hanh_an.xlsx', [
        ('tha001','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Bản án dân sự đã có hiệu lực nhưng bên thua không thi hành — phải làm gì?',
         'Nộp đơn yêu cầu thi hành án tại Chi cục Thi hành án dân sự cấp huyện hoặc Cục Thi hành án dân sự cấp tỉnh (tùy bản án của Tòa cấp nào). Hồ sơ: bản sao bản án có hiệu lực + đơn yêu cầu thi hành án. Thời hạn nộp đơn: 5 năm kể từ ngày bản án có hiệu lực. Cơ quan thi hành án sẽ ra quyết định, áp dụng biện pháp cưỡng chế (kê biên tài sản, phong tỏa tài khoản...) nếu bên phải thi hành không tự nguyện.'),
        ('tha002','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Phong tỏa tài khoản ngân hàng trong thi hành án diễn ra như thế nào?',
         'Trong quá trình thi hành án dân sự, chấp hành viên có thể ra quyết định phong tỏa tài khoản ngân hàng của người phải thi hành án. Ngân hàng nhận được văn bản phải thực hiện ngay. Số tiền bị phong tỏa không được rút, chuyển khoản; sau khi xác minh đủ điều kiện, chấp hành viên ra lệnh trích chuyển tiền từ tài khoản để thi hành án. Người phải thi hành án có thể phản đối quyết định phong tỏa nếu không đúng quy định.'),
        ('tha003','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Kê biên và bán đấu giá tài sản trong thi hành án như thế nào?',
         'Quy trình kê biên tài sản: (1) Chấp hành viên ra quyết định kê biên và lập biên bản kê biên tài sản tại hiện trường; (2) Thuê tổ chức thẩm định giá xác định giá trị tài sản; (3) Thông báo bán đấu giá; (4) Tổ chức đấu giá tại Trung tâm dịch vụ đấu giá tài sản; (5) Tiền bán đấu giá được phân chia: chi phí thi hành án → nợ ưu tiên → nợ theo bản án. Phần còn lại (nếu có) trả lại người phải thi hành án.'),
        ('tha004','Thi hành án','Thi hành án hình sự','Quốc gia','Bộ Công an',
         'Người chấp hành xong hình phạt tù có bị hạn chế quyền gì không?',
         'Sau khi chấp hành xong hình phạt tù: (1) Được cấp Giấy chứng nhận chấp hành xong hình phạt tù; (2) Được tự do và khôi phục các quyền công dân cơ bản; (3) Một số tội có thể bị cấm đảm nhiệm chức vụ, kinh doanh ngành nghề nhất định theo bản án; (4) Có thể bị quản chế 1–5 năm sau khi ra tù (với một số tội nghiêm trọng); (5) Chưa được xóa án tích ngay — phải đợi thời gian nhất định (1–5 năm tùy mức phạt) rồi làm thủ tục xóa án tích. Án tích ảnh hưởng đến việc làm, xin thẻ xanh/visa.'),
        ('tha005','Thi hành án','Xóa án tích','Quốc gia','Tòa án nhân dân',
         'Thủ tục xóa án tích sau khi chấp hành xong hình phạt là gì?',
         'Điều kiện xóa án tích: chấp hành xong hình phạt chính (tù, cải tạo không giam giữ), hình phạt bổ sung, và các quyết định khác kèm theo; hết thời gian thử thách (với án treo). Thời gian chờ xóa án tích sau khi chấp hành xong: phạt tiền, cải tạo không giam giữ: 1 năm; tù đến 5 năm: 2 năm; tù 5–15 năm: 3 năm; tù trên 15 năm: 5 năm; tù chung thân, tử hình đã ân giảm: 7 năm. Hồ sơ xin xóa án tích nộp tại TAND nơi tòa xét xử hoặc nơi thi hành án.'),
        ('tha006','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Chi phí thi hành án dân sự người được thi hành án phải chịu không?',
         'Phí thi hành án dân sự: thu theo tỷ lệ số tiền/tài sản thực tế được thi hành, từ 3–5% giá trị được nhận (tùy giá trị). Miễn phí thi hành án: người được hưởng tiền cấp dưỡng, tiền bồi thường thiệt hại về tính mạng sức khỏe; người thuộc diện hộ nghèo, đặc biệt khó khăn. Phí thi hành án do người phải thi hành án chịu, trừ trường hợp không có tài sản để thi hành thì người được thi hành án tạm ứng (sẽ hoàn lại khi thu được tiền).'),
        ('tha007','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Người phải thi hành án đang ở nơi khác hoặc trốn tránh thì xử lý thế nào?',
         'Khi người phải thi hành án đi vắng hoặc trốn tránh: (1) Chấp hành viên tiến hành xác minh tài sản, điều kiện thi hành án; (2) Nếu có tài sản: tiến hành cưỡng chế mà không cần sự có mặt của đương sự (chỉ cần thông báo trước theo quy định); (3) Nếu không có tài sản: ra quyết định hoãn thi hành án; (4) Trốn tránh có thể bị xử phạt hành chính 3–5 triệu đồng; cản trở thi hành án có thể bị truy cứu hình sự. Phối hợp công an theo dõi di chuyển nếu cần.'),
        ('tha008','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Quyết định thi hành án có thể bị hoãn hoặc đình chỉ không?',
         'Hoãn thi hành án trong các trường hợp: người phải thi hành án ốm đau nặng có xác nhận y tế; thiên tai, hỏa hoạn ảnh hưởng trực tiếp; người được thi hành án đồng ý hoãn (có thể thỏa thuận kế hoạch trả dần). Đình chỉ thi hành án: người được thi hành án yêu cầu đình chỉ; người phải hoặc được thi hành án chết và nghĩa vụ không thể chuyển giao; tài sản không còn, cơ quan không còn tồn tại. Yêu cầu hoãn/đình chỉ nộp đến Chi cục Thi hành án.'),
        ('tha009','Thi hành án','Khiếu nại thi hành án','Quốc gia','Bộ Tư pháp',
         'Không đồng ý với quyết định thi hành án có thể khiếu nại không?',
         'Có, đương sự có quyền khiếu nại các quyết định, hành vi của chấp hành viên và cơ quan thi hành án. Thủ tục: (1) Khiếu nại lần 1: gửi đến Thủ trưởng Chi cục hoặc Cục Thi hành án dân sự (phải khiếu nại trong vòng 15 ngày từ khi biết quyết định); (2) Nếu không đồng ý với giải quyết lần 1: khiếu nại lần 2 đến cơ quan cấp trên trong vòng 10 ngày; (3) Nếu vẫn không đồng ý: khởi kiện ra Tòa hành chính. Quyết định bị khiếu nại vẫn tiếp tục thực hiện trừ trường hợp bị tạm đình chỉ.'),
        ('tha010','Thi hành án','Thi hành án dân sự','Quốc gia','Bộ Tư pháp',
         'Bản án nước ngoài có được thi hành tại Việt Nam không?',
         'Bản án, quyết định dân sự của Tòa án nước ngoài được công nhận và thi hành tại Việt Nam nếu: (1) Giữa Việt Nam và nước đó có Hiệp định tương trợ tư pháp, hoặc (2) Theo nguyên tắc có đi có lại. Thủ tục: nộp đơn yêu cầu công nhận tại TAND cấp tỉnh → TAND xem xét → nếu chấp nhận, bản án được thi hành theo quy định Việt Nam. Bản án hình sự nước ngoài: công dân Việt Nam bị phạt ở nước ngoài có thể được chuyển giao về chấp hành án tại Việt Nam theo hiệp định song phương.'),
    ])

    w('faq_g_du_lich.xlsx', [
        ('dl001','Du lịch','Quyền du khách','Quốc gia','Bộ VHTTDL',
         'Quyền và nghĩa vụ của khách du lịch theo pháp luật Việt Nam?',
         'Theo Luật Du lịch 2017, khách du lịch có quyền: được cung cấp thông tin đầy đủ về dịch vụ; được an toàn tính mạng, sức khỏe, tài sản; khiếu nại và được bồi thường nếu dịch vụ không đúng cam kết. Nghĩa vụ: thực hiện quy định tại điểm du lịch, giữ gìn môi trường, không mang theo vũ khí, không xâm phạm tài sản di tích. Khi bị thiệt hại bởi công ty du lịch: khiếu nại trực tiếp hoặc đến Sở Du lịch/Sở VHTTDL tỉnh, thành phố.'),
        ('dl002','Du lịch','Tour du lịch','Quốc gia','Bộ VHTTDL',
         'Hợp đồng tour du lịch cần có những nội dung gì để bảo vệ quyền lợi?',
         'Hợp đồng lữ hành bắt buộc phải có: tên, địa chỉ doanh nghiệp lữ hành; lịch trình chi tiết; dịch vụ bao gồm (vé, khách sạn hạng mấy, bữa ăn, hướng dẫn viên); giá tour và phương thức thanh toán; điều kiện hoàn/hủy tour; quyền và nghĩa vụ mỗi bên; bảo hiểm du lịch. Kiểm tra mã số kinh doanh lữ hành của công ty tại cổng thông tin Bộ VHTTDL (vietnamtourism.gov.vn). Không ký hợp đồng với công ty không có giấy phép.'),
        ('dl003','Du lịch','Hướng dẫn viên','Quốc gia','Bộ VHTTDL',
         'Hướng dẫn viên du lịch cần những chứng chỉ gì để hành nghề hợp pháp?',
         'Hướng dẫn viên du lịch hành nghề hợp pháp cần: (1) Thẻ hướng dẫn viên du lịch do Sở Du lịch cấp; (2) Tốt nghiệp ít nhất trung cấp chuyên ngành du lịch hoặc ngoại ngữ; (3) Chứng chỉ nghiệp vụ hướng dẫn du lịch; (4) Biết ngoại ngữ (với HDV quốc tế). Có 3 loại thẻ: HDV nội địa (hướng dẫn trong nước bằng tiếng Việt), HDV quốc tế (hướng dẫn bằng ngoại ngữ), HDV tại điểm (chỉ hoạt động trong khuôn viên điểm tham quan). Kiểm tra thẻ HDV tại vietnamtourism.gov.vn.'),
        ('dl004','Du lịch','Bảo hiểm du lịch','Quốc gia','Bộ Tài chính',
         'Bảo hiểm du lịch gồm những quyền lợi gì và có bắt buộc không?',
         'Bảo hiểm du lịch thường bao gồm: (1) Tai nạn thân thể (thương tích, tử vong); (2) Chi phí y tế khẩn cấp khi đi du lịch; (3) Chậm/hủy chuyến bay; (4) Mất/trễ hành lý; (5) Hỗ trợ pháp lý khẩn cấp; (6) Hồi hương y tế. Với tour du lịch trong nước: không bắt buộc nhưng được khuyến khích. Với tour nước ngoài đến Schengen: bắt buộc mua bảo hiểm tối thiểu 30.000 EUR cho visa Schengen. Phí bảo hiểm du lịch: 50.000–300.000 đồng/chuyến tùy gói.'),
        ('dl005','Du lịch','Phàn nàn dịch vụ','Quốc gia','Bộ VHTTDL',
         'Tour du lịch không đúng cam kết — khiếu nại ở đâu và được bồi thường không?',
         'Khi tour du lịch không đúng cam kết (dịch vụ kém, thiếu bữa ăn, khách sạn sai hạng...): (1) Ghi nhận và chụp ảnh bằng chứng ngay tại chỗ; (2) Khiếu nại với hướng dẫn viên và liên hệ công ty du lịch yêu cầu xử lý; (3) Nếu không giải quyết thỏa đáng: tố cáo tại Sở Du lịch tỉnh/thành phố nơi công ty đăng ký; (4) Yêu cầu bồi thường qua hòa giải hoặc khởi kiện ra Tòa dân sự. Giữ lại hợp đồng, hóa đơn và bằng chứng về dịch vụ không đúng cam kết.'),
        ('dl006','Du lịch','Visa du lịch','Quốc gia','Bộ Công an',
         'Người nước ngoài vào Việt Nam du lịch tự túc cần chuẩn bị gì?',
         'Để du lịch tự túc tại Việt Nam: (1) Kiểm tra xem quốc tịch có được miễn visa không (khoảng 45 quốc gia); (2) Nếu cần visa: xin E-visa tại evisa.xuatnhapcanh.gov.vn (phí 25 USD, 90 ngày, nhiều lần); (3) Hộ chiếu còn hiệu lực ít nhất 6 tháng; (4) Bảo hiểm du lịch (không bắt buộc nhưng nên có); (5) Đặt khách sạn/nhà nghỉ trước; (6) Khai báo hải quan nếu mang theo tiền/vàng lớn. Giao thông: taxi, Grab, xe máy thuê phổ biến; cần bằng lái quốc tế (IDP) nếu lái xe tự thuê.'),
        ('dl007','Du lịch','Khu di tích','Quốc gia','Bộ VHTTDL',
         'Tham quan di tích lịch sử có cần mua vé không và giá vé thế nào?',
         'Hầu hết di tích lịch sử, bảo tàng quốc gia và danh lam thắng cảnh có thu phí tham quan. Giá vé thay đổi tùy địa điểm: Vịnh Hạ Long khoảng 240.000–290.000 đồng/người; Hội An phố cổ 120.000 đồng; Hoàng thành Thăng Long 30.000 đồng; Bảo tàng lịch sử quốc gia 40.000 đồng. Trẻ em dưới 6 tuổi thường miễn vé; người cao tuổi, người khuyết tật, học sinh sinh viên có thể được giảm giá. Mua vé trực tiếp hoặc qua app/website của khu di tích.'),
        ('dl008','Du lịch','An toàn du lịch','Quốc gia','Bộ VHTTDL',
         'Những điểm du lịch nguy hiểm cần lưu ý an toàn tại Việt Nam?',
         'An toàn khi du lịch: (1) Bãi biển có cờ đỏ/vàng: không xuống biển khi sóng lớn; (2) Trekking rừng/núi: đi theo nhóm, thuê hướng dẫn viên địa phương, thông báo lịch trình; (3) Vùng núi mùa mưa lũ: nguy cơ sạt lở, không vượt suối khi nước lớn; (4) Xe máy: đội mũ bảo hiểm, không uống rượu bia lái xe, giao thông tại các thành phố phức tạp; (5) Đồ ăn đường phố: chọn nơi đông khách, tươi sạch. Cứu nạn: 113 (công an), 114 (cứu hỏa), 115 (cấp cứu), 1800 599 909 (hỗ trợ du lịch miễn phí).'),
        ('dl009','Du lịch','Kinh doanh du lịch','Quốc gia','Bộ VHTTDL',
         'Điều kiện để mở công ty du lịch lữ hành quốc tế?',
         'Điều kiện kinh doanh lữ hành quốc tế: (1) Doanh nghiệp phải có ít nhất 1 người quản lý có nghiệp vụ điều hành du lịch quốc tế; (2) Ký quỹ tại ngân hàng: 500 triệu đồng (lữ hành quốc tế phục vụ khách outbound/inbound), 250 triệu đồng (lữ hành quốc tế phục vụ khách Việt ra nước ngoài); (3) Giấy phép kinh doanh lữ hành quốc tế do Tổng cục Du lịch cấp. Lữ hành nội địa: ký quỹ 100 triệu, giấy phép do Sở Du lịch tỉnh/TP cấp.'),
        ('dl010','Du lịch','Homestay','Quốc gia','Bộ VHTTDL',
         'Homestay có cần đăng ký kinh doanh lưu trú không?',
         'Theo Luật Du lịch 2017 và Nghị định 168/2017/NĐ-CP, cơ sở lưu trú du lịch (gồm homestay) phải: (1) Đăng ký kinh doanh dịch vụ lưu trú (nếu kinh doanh thường xuyên); (2) Thông báo về điều kiện an toàn và phòng cháy chữa cháy; (3) Thực hiện khai báo tạm trú khách tại công an. Cho thuê phòng dưới 2 phòng/căn với quy mô nhỏ gia đình tự phục vụ thì không phải xin giấy phép kinh doanh lưu trú, nhưng vẫn phải nộp thuế theo quy định hộ kinh doanh.'),
    ])

    w('faq_g_dien_luc.xlsx', [
        ('el001','Điện lực','Hóa đơn điện','Quốc gia','Bộ Công Thương',
         'Giá điện sinh hoạt theo bậc thang hiện nay như thế nào?',
         'Giá điện sinh hoạt bậc thang (theo quy định EVN, có thể điều chỉnh): Bậc 1 (0–50 kWh): ~1.893 đồng/kWh; Bậc 2 (51–100 kWh): ~1.956 đồng/kWh; Bậc 3 (101–200 kWh): ~2.271 đồng/kWh; Bậc 4 (201–300 kWh): ~2.860 đồng/kWh; Bậc 5 (301–400 kWh): ~3.197 đồng/kWh; Bậc 6 (>400 kWh): ~3.302 đồng/kWh (chưa VAT). Hóa đơn điện = số kWh × giá tương ứng từng bậc + VAT 8%. Kiểm tra giá điện mới nhất tại evn.com.vn.'),
        ('el002','Điện lực','Hóa đơn điện','Quốc gia','EVN',
         'Tiền điện tháng này tăng đột biến — nguyên nhân và cách kiểm tra?',
         'Nguyên nhân tiền điện tăng đột biến: (1) Thời tiết nóng — dùng điều hòa nhiều hơn; (2) Kỳ ghi điện dài hơn thông thường (31 ngày thay vì 28 ngày); (3) Thiết bị điện hỏng gây rò rỉ điện; (4) Biểu giá bậc thang — khi vượt ngưỡng 300 kWh, đơn giá tăng vọt. Cách kiểm tra: (1) Chụp ảnh đồng hồ điện, so với kỳ trước; (2) Đăng nhập App EVN hoặc chamsodientu.evn.com.vn tra chỉ số; (3) Liên hệ điện lực địa phương yêu cầu kiểm tra đồng hồ nếu nghi ngờ sai số.'),
        ('el003','Điện lực','Đăng ký điện','Quốc gia','EVN',
         'Thủ tục đăng ký lắp đặt điện mới cho nhà ở như thế nào?',
         'Thủ tục đăng ký điện mới: (1) Nộp đơn đề nghị cấp điện tại Chi nhánh điện lực địa phương hoặc qua web/app EVN; (2) Hồ sơ: đơn theo mẫu, giấy tờ nhà đất (GCNQSDĐ hoặc hợp đồng thuê/mua), CCCD chủ hộ; (3) Nhân viên điện lực khảo sát hiện trường; (4) Ký hợp đồng mua bán điện; (5) Lắp đặt công tơ và đấu nối (thường 5–7 ngày làm việc sau khi ký hợp đồng). Chi phí: phí đấu nối tùy theo khoảng cách và công suất yêu cầu.'),
        ('el004','Điện lực','Cúp điện','Quốc gia','EVN',
         'Mất điện đột ngột không báo trước — quyền lợi khách hàng và liên hệ ở đâu?',
         'Khi mất điện đột ngột không báo trước: (1) Liên hệ hotline EVN 19001006 hoặc app EVN Customer Care; (2) Tra thông báo cúp điện tại app/website điện lực địa phương; (3) Nếu mất điện do sự cố, EVN có trách nhiệm khôi phục trong thời gian quy định. Quyền lợi: nếu EVN cúp điện có kế hoạch không thông báo trước đúng quy định, khách hàng được giảm trừ tiền điện theo quy định. Nếu mất điện gây thiệt hại thiết bị do lỗi của điện lực, yêu cầu bồi thường qua Chi nhánh điện lực.'),
        ('el005','Điện lực','Điện mặt trời','Quốc gia','Bộ Công Thương',
         'Lắp điện mặt trời áp mái cần thủ tục gì và có được bán điện ngược lại không?',
         'Thủ tục lắp điện mặt trời mái nhà: (1) Liên hệ điện lực địa phương đăng ký; (2) Ký hợp đồng mua bán điện với EVN; (3) Lắp đặt hệ thống (qua đơn vị thi công được cấp phép); (4) Điện lực lắp công tơ 2 chiều và nghiệm thu. Bán điện dư ngược lên lưới: hiện được phép và EVN mua lại theo giá quy định của Bộ Công Thương (giá FIT, thay đổi theo từng thời kỳ). Công suất hệ thống mái nhà thường 3–10 kWp tùy diện tích mái.'),
        ('el006','Điện lực','Tiết kiệm điện','Quốc gia','Bộ Công Thương',
         'Các thiết bị tiêu thụ điện nhiều nhất trong gia đình và cách tiết kiệm?',
         'Thiết bị tiêu thụ điện nhiều nhất: (1) Điều hòa nhiệt độ (40–50% hóa đơn điện mùa hè) — đặt 26–27°C, dùng chế độ auto, vệ sinh lọc định kỳ; (2) Bình nước nóng — dùng loại năng lượng mặt trời hoặc bơm nhiệt; (3) Tủ lạnh — chọn loại inverter tiết kiệm điện, không để thức ăn nóng vào tủ; (4) Máy giặt — giặt đầy máy mới giặt, không sấy quần áo; (5) Đèn — thay đèn LED. Thiết bị chờ (standby) cũng tiêu tốn điện — rút phích cắm khi không dùng.'),
        ('el007','Điện lực','Điện 3 pha','Quốc gia','EVN',
         'Điện 3 pha dùng cho mục đích gì và khác điện 1 pha thế nào?',
         'Điện 1 pha (220V/50Hz): dùng cho sinh hoạt thông thường, các thiết bị gia dụng. Điện 3 pha (380V/50Hz): dùng cho cơ sở sản xuất, máy bơm công suất lớn, thang máy, hệ thống HVAC công nghiệp. Ưu điểm điện 3 pha: tải lớn hơn, ổn định hơn, hiệu suất động cơ cao hơn. Để đăng ký điện 3 pha: nộp đơn tại điện lực, cung cấp sơ đồ thiết bị sử dụng và công suất yêu cầu; Chi phí đấu nối và hệ thống đo đếm cao hơn điện 1 pha.'),
        ('el008','Điện lực','Nợ tiền điện','Quốc gia','EVN',
         'Chậm thanh toán tiền điện có bị cắt điện không và có phạt không?',
         'Nếu chậm thanh toán tiền điện: (1) Sau 15 ngày kể từ ngày ghi trên hóa đơn không thanh toán: điện lực thông báo và có thể tạm ngừng cấp điện; (2) Khi nối lại điện sau khi bị cắt: phải thanh toán toàn bộ số tiền nợ + phí truy thu. Không có phạt lãi suất chậm nộp như tiền thuế, nhưng cắt điện gây bất tiện và phải trả phí nối lại. Đăng ký thanh toán tự động qua ngân hàng hoặc ví điện tử để tránh bị cắt điện do quên nộp.'),
        ('el009','Điện lực','An toàn điện','Quốc gia','Bộ Công Thương',
         'Những sự cố điện nguy hiểm thường gặp trong gia đình và cách phòng tránh?',
         'Sự cố điện nguy hiểm thường gặp: (1) Chập điện do dây dẫn cũ, quá tải hoặc chuột cắn — kiểm tra hệ thống điện 5–10 năm/lần, lắp aptomat (cầu dao tự động); (2) Điện giật do ổ cắm ẩm, thiết bị hỏng — lắp ổ cắm chống giật, không cắm điện tay ướt; (3) Hỏa hoạn do điện — không dùng dây điện đã bị nứt, không để thiết bị điện gần vật dễ cháy, lắp thiết bị bảo vệ chống rò điện (ELCB/RCD). Khi xảy ra sự cố: ngắt nguồn điện, gọi 114 (cứu hỏa).'),
        ('el010','Điện lực','Khiếu nại tiền điện','Quốc gia','EVN',
         'Nghi ngờ đồng hồ điện sai số, có thể yêu cầu kiểm tra không?',
         'Có, khách hàng có quyền yêu cầu kiểm tra định kỳ công tơ điện: (1) Liên hệ Chi nhánh điện lực địa phương yêu cầu kiểm tra đồng hồ; (2) Nếu công tơ sai từ 2% trở lên: EVN thu hồi công tơ, hoàn trả tiền thừa hoặc truy thu tiền thiếu tối đa 12 tháng; (3) Phí kiểm tra công tơ: miễn phí nếu sai số vượt mức cho phép; nếu công tơ đúng, khách hàng chịu phí kiểm tra (khoảng 200.000–500.000 đồng). Chu kỳ kiểm định công tơ theo quy định: 5 năm/lần (loại điện 1 pha thông thường).'),
    ])

    w('faq_g_van_tai.xlsx', [
        ('vt001','Vận tải','Vận tải hành khách','Quốc gia','Bộ GTVT',
         'Quy định về giá cước taxi và cách phòng tránh taxi "chặt chém"?',
         'Taxi phải niêm yết giá cước trên xe hoặc màn hình đồng hồ tính tiền. Dấu hiệu taxi không uy tín: không bật đồng hồ, đồng hồ chạy nhanh bất thường, không có logo hãng rõ ràng, từ chối in hóa đơn. Cách phòng tránh: sử dụng taxi công nghệ (Grab, Be, Gojek) — giá hiển thị trước khi đặt; chỉ đi taxi có hãng uy tín (Mai Linh, Vinasun, G7...); thỏa thuận giá trước nếu taxi không có đồng hồ. Khiếu nại taxi chặt chém: liên hệ hãng taxi hoặc Sở GTVT tỉnh/TP.'),
        ('vt002','Vận tải','Xe khách liên tỉnh','Quốc gia','Bộ GTVT',
         'Mua vé xe khách liên tỉnh online an toàn ở đâu?',
         'Mua vé xe khách liên tỉnh online qua: (1) Vexere.com — nền tảng lớn nhất, tổng hợp nhiều hãng xe; (2) Baoxevietnam.vn; (3) App hoặc website của từng hãng xe (Phương Trang/FUTA, Hoàng Long, Thành Bưởi...); (4) Vé xe tại bến xe (Mien Dong, Mien Tay, My Dinh...) — đặt trực tiếp quầy. Lưu ý: chỉ mua qua kênh chính thức, không trả tiền cho "cò xe". Kiểm tra biển số xe, giờ khởi hành với nhân viên bến xe trước khi lên xe.'),
        ('vt003','Vận tải','Vận chuyển hàng hóa','Quốc gia','Bộ GTVT',
         'Gửi hàng hóa bằng xe khách liên tỉnh có quy định gì cần biết?',
         'Quy định gửi hàng qua xe khách: (1) Hàng cồng kềnh hoặc quá 30kg thường phải mua vé hàng riêng; (2) Không được gửi: chất dễ cháy, nổ, độc hại, động vật sống không có giấy phép, hàng cấm; (3) Bưu kiện phải đóng gói chắc chắn, dán nhãn rõ người gửi/nhận; (4) Yêu cầu biên nhận gửi hàng; (5) Trường hợp hàng bị hỏng/mất: khiếu nại với hãng xe trong vòng 7 ngày. Nên chụp ảnh hàng hóa trước khi gửi làm bằng chứng.'),
        ('vt004','Vận tải','Hàng không','Quốc gia','Cục HKVN',
         'Quy định về hành lý xách tay và ký gửi khi đi máy bay nội địa?',
         'Quy định hành lý hàng không nội địa Việt Nam (thông thường): Hành lý xách tay: tối đa 7–10kg, kích thước không quá 56×36×23cm; mỗi hành khách 1 kiện. Hành lý ký gửi: phụ thuộc hạng vé và hãng bay. Vietjet/Bamboo hạng phổ thông cơ bản: thường không bao gồm hành lý ký gửi — phải mua thêm; VNA phổ thông: thường 23kg. Chất lỏng xách tay: tối đa 100ml/chai, đặt trong túi nhựa trong suốt 1 lít. Vật phẩm cấm mang: pin lithium rời, bật lửa, dao kéo trong hành lý xách tay.'),
        ('vt005','Vận tải','Đường sắt','Quốc gia','Bộ GTVT',
         'Mua vé tàu hỏa online ở đâu và có được hoàn vé không?',
         'Mua vé tàu online: (1) Dtalemand.vn/vi/vé-tàu hoặc website Vietnam Railways (dsvn.vn); (2) App VR TICHET của Đường sắt Việt Nam; (3) Qua các ứng dụng như Vexere.com, Bestprice. Hoàn vé tàu: được phép hoàn vé trước giờ tàu chạy, phí hoàn theo quy định (0–30% giá vé tùy thời gian). Nếu hoàn trước 24h: phí 30%; nếu muộn hơn: phí cao hơn hoặc không được hoàn. Đổi tàu/ngày: phí 10.000–30.000 đồng tùy loại vé. Thực hiện hoàn/đổi tại nhà ga hoặc qua website.'),
        ('vt006','Vận tải','Vận chuyển container','Quốc gia','Bộ GTVT',
         'Doanh nghiệp xuất khẩu cần biết gì về vận chuyển hàng hóa quốc tế?',
         'Vận chuyển hàng hóa xuất khẩu: (1) Đường biển (phổ biến nhất, chi phí thấp, thời gian dài): thuê container 20ft hoặc 40ft, đặt chỗ qua freight forwarder; (2) Đường hàng không (nhanh, giá cao): phù hợp hàng giá trị cao, thời hạn gấp; (3) Đường bộ (sang Trung Quốc, Lào, Campuchia): chi phí trung bình. Các loại giấy tờ: hợp đồng ngoại thương, Commercial Invoice, Packing List, Bill of Lading, C/O (giấy chứng nhận xuất xứ), phytosanitary certificate (hàng nông sản). Thuê công ty Freight Forwarder uy tín để xử lý thủ tục hải quan.'),
        ('vt007','Vận tải','Bằng lái xe quốc tế','Quốc gia','Bộ GTVT',
         'Bằng lái xe quốc tế (IDP) làm ở đâu và có giá trị bao lâu?',
         'Bằng lái xe quốc tế (International Driving Permit) theo Công ước Vienna 1968: (1) Làm tại Cục Đường bộ Việt Nam hoặc Sở GTVT tỉnh/TP; (2) Hồ sơ: bằng lái xe trong nước, CCCD, ảnh 4x6, đơn đề nghị; (3) Phí: 135.000 đồng; (4) Thời gian: 3–5 ngày làm việc; (5) Hiệu lực: 3 năm kể từ ngày cấp (không quá hạn bằng lái gốc). Lưu ý: IDP phải đi kèm bằng lái gốc trong nước; không phải tất cả quốc gia đều chấp nhận — kiểm tra trước với nước đến.'),
        ('vt008','Vận tải','Phí cao tốc','Quốc gia','Bộ GTVT',
         'Thanh toán phí đường cao tốc bằng ETC như thế nào?',
         'ETC (Electronic Toll Collection) thu phí không dừng trên đường cao tốc: (1) Dán đầu đọc thẻ OBU lên kính xe; (2) Nạp tiền vào tài khoản ETC liên kết với thẻ ngân hàng; (3) Khi qua trạm thu phí: xe đi thẳng vào làn ETC, tự động trừ tiền. Đăng ký ETC: tại trạm thu phí, đại lý ủy quyền, hoặc qua app của ngân hàng (VCB, Vietcombank, BIDV, MB...). Phí dán đầu đọc: 100.000–350.000 đồng. Từ 8/2022, làn ETC là bắt buộc trên các tuyến cao tốc có thu phí.'),
        ('vt009','Vận tải','Vận chuyển nguy hiểm','Quốc gia','Bộ GTVT',
         'Quy định về vận chuyển hàng nguy hiểm (xăng dầu, hóa chất) trên đường bộ?',
         'Vận chuyển hàng nguy hiểm đường bộ theo Nghị định 42/2020/NĐ-CP: (1) Phương tiện phải có giấy phép vận chuyển hàng nguy hiểm do Sở GTVT cấp; (2) Lái xe và người áp tải phải được đào tạo và có chứng chỉ; (3) Xe phải dán biểu trưng nguy hiểm theo quy định UN; (4) Chở đúng tuyến đường, khung giờ cho phép; (5) Có đủ thiết bị phòng cháy chữa cháy và xử lý sự cố trên xe. Vi phạm bị phạt nặng và tước giấy phép vận tải.'),
        ('vt010','Vận tải','Bảo hiểm xe ô tô','Quốc gia','Bộ Tài chính',
         'Bảo hiểm vật chất xe ô tô tự nguyện bảo vệ những gì và mua ở đâu?',
         'Bảo hiểm vật chất xe ô tô (bảo hiểm thân vỏ) bảo vệ: hư hại do tai nạn giao thông, va chạm, lật đổ; trộm cắp toàn bộ xe hoặc bộ phận; thiên tai (lũ lụt, mưa đá, cháy); vỡ kính. Thường trừ: hao mòn tự nhiên, lỗi kỹ thuật, lái xe không bằng, say rượu. Phí bảo hiểm: khoảng 1–2% giá trị xe/năm. Mua tại: công ty bảo hiểm phi nhân thọ (PVI, Bảo Việt, PJICO, PTI...), đại lý bảo hiểm, hoặc online qua app. Lưu số hotline bảo hiểm trên xe để gọi ngay khi xảy ra tai nạn.'),
    ])

    print('\nBatch 11 hoan thanh.')

if __name__ == '__main__':
    main()
