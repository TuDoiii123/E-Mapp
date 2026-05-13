"""Batch 13 — dược phẩm, TMĐT, hàng không/đường sắt, phòng chống thiên tai, quyền trẻ em."""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent

def w(filename, rows):
    df = pd.DataFrame(rows, columns=['id','category','procedure','level','source','question','answer'])
    with pd.ExcelWriter(OUT / filename, engine='openpyxl') as xw:
        df.to_excel(xw, sheet_name='FAQ', index=False)
    print(f'+ {filename} ({len(df)} rows)')

def main():
    w('faq_g_duoc_pham.xlsx', [
        ('dp001','Dược phẩm','Mua thuốc','Quốc gia','Bộ Y tế',
         'Thuốc kê đơn và thuốc không kê đơn khác nhau thế nào?',
         'Thuốc kê đơn (Prescription Only Medicine - POM): chỉ được bán khi có đơn thuốc của bác sĩ, ghi chữ "Thuốc bán theo đơn" trên bao bì; thường có tác dụng mạnh, nguy cơ tác dụng phụ cao. Thuốc không kê đơn (OTC - Over The Counter): được bán tự do tại nhà thuốc, không cần đơn; thường là thuốc giảm đau, hạ sốt, thuốc ho, vitamin. Bán thuốc kê đơn không có đơn là vi phạm pháp luật. Kiểm tra danh sách thuốc kê đơn tại website Cục Quản lý Dược (drugbank.vn).'),
        ('dp002','Dược phẩm','An toàn thuốc','Quốc gia','Bộ Y tế',
         'Làm sao nhận biết thuốc giả, thuốc kém chất lượng?',
         'Dấu hiệu thuốc giả/kém chất lượng: (1) Bao bì nhàu nát, mờ, lỗi chính tả, màu sắc không đồng đều; (2) Số đăng ký không có trên website Cục Quản lý Dược (drugbank.vn); (3) Bao bì không có số lô, ngày sản xuất, hạn dùng rõ ràng; (4) Mùi/màu sắc bất thường so với thuốc chính hãng; (5) Giá thấp bất thường. Mua thuốc tại nhà thuốc có GPP (logo nhà thuốc đạt chuẩn). Báo cáo thuốc giả: Cục Quản lý Dược 024 38234781 hoặc drugbank.vn.'),
        ('dp003','Dược phẩm','Nhập khẩu thuốc','Quốc gia','Bộ Y tế',
         'Cá nhân có được mang thuốc nước ngoài vào Việt Nam không?',
         'Cá nhân được mang thuốc vào Việt Nam để sử dụng cá nhân với điều kiện: (1) Có đơn thuốc của bác sĩ (bản gốc hoặc sao có công chứng); (2) Số lượng không quá 3 tháng điều trị; (3) Không phải chất ma túy/tiền chất. Nếu không có đơn thuốc: chỉ được mang tối đa 1 hộp/loại thuốc OTC. Mang thuốc nhập khẩu kinh doanh không có phép: vi phạm pháp luật và bị xử phạt. Các loại thực phẩm chức năng không yêu cầu giấy phép đặc biệt nhưng phải khai báo hải quan nếu số lượng lớn.'),
        ('dp004','Dược phẩm','Tác dụng phụ','Quốc gia','Bộ Y tế',
         'Khi dùng thuốc gặp tác dụng phụ nghiêm trọng phải làm gì?',
         'Khi gặp tác dụng phụ nghiêm trọng (phản ứng dị ứng nặng, khó thở, tụt huyết áp, ngất...): (1) GỌI NGAY 115 hoặc đến cấp cứu gần nhất; (2) Dừng thuốc ngay; (3) Mang theo vỏ hộp/đơn thuốc để bác sĩ cấp cứu biết loại thuốc. Sau khi ổn định: báo cáo phản ứng có hại của thuốc (ADR) lên Trung tâm Quốc gia về thông tin thuốc và theo dõi ADR (canhgiacduoc.org.vn) để cảnh báo cộng đồng. Bác sĩ, dược sĩ, người dùng đều có thể báo cáo ADR.'),
        ('dp005','Dược phẩm','Nhà thuốc GPP','Quốc gia','Bộ Y tế',
         'Nhà thuốc đạt tiêu chuẩn GPP là gì và khác nhà thuốc thường thế nào?',
         'GPP (Good Pharmacy Practice) là tiêu chuẩn thực hành tốt nhà thuốc do Bộ Y tế ban hành. Nhà thuốc GPP đảm bảo: (1) Dược sĩ có bằng cấp và kinh nghiệm trực tiếp hướng dẫn sử dụng thuốc; (2) Bảo quản thuốc đúng điều kiện (nhiệt độ, độ ẩm); (3) Không bán thuốc kê đơn không có đơn; (4) Có hệ thống quản lý thuốc; (5) Được cơ quan y tế kiểm tra định kỳ. Nhận biết: logo GPP tại cửa nhà thuốc. Báo cáo nhà thuốc vi phạm (bán thuốc kê đơn không đơn): Sở Y tế tỉnh/TP.'),
        ('dp006','Dược phẩm','Thực phẩm chức năng','Quốc gia','Bộ Y tế',
         'Thực phẩm chức năng và thuốc khác nhau thế nào? Tin quảng cáo TPCN không?',
         'Khác biệt quan trọng: Thuốc phải qua thử nghiệm lâm sàng, có bằng chứng khoa học về hiệu quả; được dùng để điều trị bệnh. Thực phẩm chức năng (TPCN) chỉ cần đăng ký công bố thành phần; KHÔNG được quảng cáo là "chữa bệnh". Theo quy định, TPCN không thay thế thuốc và không chữa khỏi bệnh. Dấu hiệu quảng cáo TPCN vi phạm: khẳng định "chữa khỏi X bệnh", "100% an toàn", "chỉ 1 liệu trình là hết". Tố cáo quảng cáo TPCN sai phép: Cục An toàn thực phẩm (Bộ Y tế) và Cục Quản lý Bảo vệ người tiêu dùng.'),
        ('dp007','Dược phẩm','Bảo quản thuốc','Quốc gia','Bộ Y tế',
         'Bảo quản thuốc tại nhà đúng cách như thế nào?',
         'Nguyên tắc bảo quản thuốc tại nhà: (1) Đọc và làm theo hướng dẫn trên nhãn (nhiệt độ phòng/mát/lạnh); (2) Không để thuốc trong nhà tắm hoặc gần bếp (ẩm, nóng); (3) Để xa tầm tay trẻ em; (4) Giữ thuốc trong bao bì gốc, không trộn lẫn; (5) Không dùng thuốc hết hạn — hủy đúng cách (không đổ xuống cống/vứt rác thường). Hủy thuốc hết hạn: trả về nhà thuốc (một số nhà thuốc GPP có dịch vụ thu hồi), hoặc hòa trong túi nilon kín rồi vứt vào rác sinh hoạt. Thuốc lỏng: không đổ xuống bồn rửa.'),
        ('dp008','Dược phẩm','Ma túy y tế','Quốc gia','Bộ Y tế',
         'Morphine và thuốc giảm đau nhóm opioid có được kê đơn hợp pháp không?',
         'Có, morphine và opioid được sử dụng hợp pháp trong y tế để giảm đau cho bệnh nhân ung thư giai đoạn cuối, đau mạn tính nặng, gây mê phẫu thuật. Tuy nhiên, thuộc danh mục kiểm soát đặc biệt: (1) Chỉ được kê bởi bác sĩ có giấy phép kê đơn gây nghiện; (2) Chỉ được cấp phát tại cơ sở y tế được phép; (3) Bệnh nhân phải có đơn gốc và được kiểm tra định kỳ; (4) Cơ sở y tế phải báo cáo sử dụng thuốc gây nghiện theo quy định. Sử dụng opioid phi y tế là vi phạm pháp luật nghiêm trọng.'),
        ('dp009','Dược phẩm','Kháng sinh','Quốc gia','Bộ Y tế',
         'Tại sao không nên tự mua kháng sinh và nguy cơ kháng kháng sinh là gì?',
         'Tự mua kháng sinh không có đơn nguy hiểm vì: (1) Kháng sinh không có tác dụng với bệnh do virus (cảm, cúm); (2) Sử dụng sai loại, sai liều → không diệt được vi khuẩn, gây nhờn thuốc; (3) Tác dụng phụ (tiêu chảy, dị ứng, tổn thương gan thận) khi dùng sai. Kháng kháng sinh là mối đe dọa toàn cầu: vi khuẩn biến đổi không còn bị tiêu diệt bởi kháng sinh — người bệnh tử vong vì nhiễm khuẩn thông thường mà không có thuốc điều trị. Theo quy định, kháng sinh là thuốc kê đơn — phải có đơn bác sĩ mới được bán.'),
        ('dp010','Dược phẩm','Vắc-xin','Quốc gia','Bộ Y tế',
         'Lịch tiêm chủng mở rộng miễn phí cho trẻ em gồm những vắc-xin gì?',
         'Chương trình Tiêm chủng mở rộng (TCMR) miễn phí cho trẻ em Việt Nam gồm: Sơ sinh: BCG (lao), Viêm gan B liều sơ sinh. 2–3 tháng: bạch hầu-ho gà-uốn ván (DPT), bại liệt (OPV/IPV), Hib, Viêm gan B. 9 tháng: Sởi, Viêm não Nhật Bản mũi 1. 18 tháng: DPT nhắc lại, Sởi-Rubella. Ngoài ra, phụ nữ mang thai được tiêm uốn ván miễn phí. Đưa trẻ đến trạm y tế xã/phường để tiêm đúng lịch. Nếu tiêm muộn, tiêm bù theo hướng dẫn của cán bộ y tế.'),
    ])

    w('faq_g_tmdt.xlsx', [
        ('tmdt001','Thương mại điện tử','Sàn TMĐT','Quốc gia','Bộ Công Thương',
         'Kinh doanh trên Shopee, Lazada, TikTok Shop có cần đăng ký không?',
         'Theo Nghị định 85/2021/NĐ-CP về TMĐT: (1) Cá nhân bán hàng trên sàn TMĐT phải đăng ký tài khoản thật (CCCD), khai báo thông tin và nộp thuế; (2) Hộ kinh doanh và doanh nghiệp bán hàng phải đăng ký với sàn TMĐT và khai báo doanh thu với cơ quan thuế; (3) Các sàn TMĐT có nghĩa vụ thu thập thông tin người bán và cung cấp cho cơ quan thuế. Từ 2022, các sàn lớn (Shopee, Lazada, TikTok Shop) trực tiếp khấu trừ và nộp thuế thay cho người bán theo quy định.'),
        ('tmdt002','Thương mại điện tử','Website bán hàng','Quốc gia','Bộ Công Thương',
         'Mở website bán hàng cá nhân cần đăng ký gì?',
         'Mở website bán hàng cá nhân/doanh nghiệp: (1) Đăng ký tên miền (.vn hoặc quốc tế); (2) Thông báo website thương mại điện tử tại Cổng thông tin quản lý TMĐT (online.gov.vn) — bắt buộc với website bán hàng có doanh thu; (3) Đăng ký kinh doanh nếu hoạt động thường xuyên, có lợi nhuận; (4) Khai báo thuế. Miễn đăng ký: cá nhân bán hàng dưới 100 triệu đồng/năm và bán qua sàn TMĐT (đã được sàn xử lý). Vi phạm không thông báo: phạt 10–20 triệu đồng.'),
        ('tmdt003','Thương mại điện tử','Giao hàng','Quốc gia','Bộ Công Thương',
         'Người mua hàng online có quyền từ chối nhận hàng và hoàn tiền không?',
         'Quyền từ chối nhận hàng của người mua: (1) Hàng không đúng mô tả (sai màu, kích cỡ, model): có quyền từ chối và yêu cầu hoàn tiền; (2) Hàng bị hỏng khi giao: từ chối và chụp ảnh bằng chứng; (3) Giao hàng quá trễ so với cam kết: có quyền hủy đơn; (4) Trong thời gian hoàn trả theo chính sách của sàn (thường 7–15 ngày): đổi trả dễ dàng. Khi từ chối nhận hàng đúng lý do: shipper ghi nhận và hàng trả về người bán, sàn hoàn tiền tự động. Giữ lại video unboxing khi nhận hàng để làm bằng chứng nếu hàng hỏng/sai.'),
        ('tmdt004','Thương mại điện tử','Thanh toán an toàn','Quốc gia','Bộ Công Thương',
         'Phương thức thanh toán nào an toàn nhất khi mua hàng online?',
         'An toàn từ cao xuống thấp: (1) Thanh toán qua sàn TMĐT (tiền giữ ở escrow, chỉ trả cho người bán sau khi người mua xác nhận nhận hàng) — AN TOÀN NHẤT; (2) Thẻ tín dụng qua cổng thanh toán uy tín (VNPay, OnePay) — bảo vệ bởi chính sách hoàn tiền chargeback; (3) Ví điện tử (MoMo, ZaloPay) — có cơ chế bảo vệ người mua; (4) COD (thanh toán khi nhận hàng) — an toàn với người mua nhưng cần kiểm tra hàng trước khi trả tiền; (5) Chuyển khoản trực tiếp — RỦI RO NHẤT, không có bảo vệ nếu bị lừa.'),
        ('tmdt005','Thương mại điện tử','Review sản phẩm','Quốc gia','Bộ Công Thương',
         'Có được xóa đánh giá (review) tiêu cực trên sàn TMĐT không?',
         'Người bán KHÔNG được xóa đánh giá tiêu cực của người mua thực sự — điều này vi phạm quy định của sàn và Luật Bảo vệ người tiêu dùng. Người bán CÓ THỂ: (1) Phản hồi công khai giải thích; (2) Báo cáo review vi phạm (ngôn ngữ thù địch, không liên quan đến sản phẩm) để sàn xem xét xóa; (3) Liên hệ khách hàng giải quyết — nếu khách hàng đồng ý, tự họ có thể sửa/xóa review. Doanh nghiệp nhờ người viết review ảo (review bomb/fake) vi phạm Luật Cạnh tranh và có thể bị phạt.'),
        ('tmdt006','Thương mại điện tử','Dropshipping','Quốc gia','Bộ Công Thương',
         'Dropshipping (bán hàng không cần kho) có hợp pháp tại Việt Nam không?',
         'Dropshipping hợp pháp tại Việt Nam khi: (1) Người bán đăng ký kinh doanh (hộ kinh doanh hoặc công ty) và khai báo thuế; (2) Sản phẩm được bán không thuộc hàng cấm, hàng giả, hàng không rõ nguồn gốc; (3) Thông tin sản phẩm trung thực, không gây hiểu lầm; (4) Có hóa đơn/chứng từ chứng minh nguồn gốc hàng hóa. Rủi ro: người bán dropship chịu trách nhiệm với người mua về chất lượng và thời gian giao hàng, ngay cả khi không kiểm soát trực tiếp kho hàng của nhà cung cấp.'),
        ('tmdt007','Thương mại điện tử','Bảo vệ thông tin','Quốc gia','Bộ Công Thương',
         'Thông tin cá nhân bị lộ từ sàn TMĐT — quyền lợi người tiêu dùng?',
         'Khi thông tin cá nhân bị lộ từ sàn TMĐT: (1) Yêu cầu sàn TMĐT giải thích nguyên nhân và biện pháp khắc phục; (2) Theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân: sàn TMĐT phải thông báo sự cố bảo mật trong vòng 72 giờ; (3) Khiếu nại tới Bộ Công Thương (Cục Thương mại điện tử) hoặc Bộ TT&TT (Cục An toàn thông tin); (4) Nếu thiệt hại thực tế: khởi kiện dân sự yêu cầu bồi thường. Ngay khi biết bị lộ thông tin: đổi mật khẩu tất cả tài khoản dùng email đó, bật xác thực 2 yếu tố.'),
        ('tmdt008','Thương mại điện tử','Hàng nhập khẩu online','Quốc gia','Bộ Tài chính',
         'Mua hàng từ website nước ngoài về Việt Nam phải đóng thuế nhập khẩu không?',
         'Hàng mua online từ nước ngoài gửi về Việt Nam: (1) Trị giá từng gói hàng ≤ 1 triệu đồng: miễn thuế; (2) Trên 1 triệu đồng: phải đóng thuế nhập khẩu (0–30% tùy loại) + VAT 10% + phí hải quan. Trong thực tế, nhiều gói hàng nhỏ qua bưu điện được thông quan nhanh và ít bị kiểm tra. Tuy nhiên, từ 2023 có xu hướng thắt chặt kiểm soát hàng xách tay và hàng nhập khẩu online để bảo hộ thương mại nội địa và thu thuế đúng quy định.'),
        ('tmdt009','Thương mại điện tử','Khuyến mãi online','Quốc gia','Bộ Công Thương',
         'Chương trình khuyến mãi "giá gốc" rồi giảm 90% có hợp pháp không?',
         'Khuyến mãi gian lận (ghi giá cao ảo rồi giảm để tạo cảm giác lời) là hành vi vi phạm Luật Bảo vệ người tiêu dùng và Luật Cạnh tranh. Theo Nghị định 98/2020/NĐ-CP: (1) Giá gốc phải là giá thực tế đã bán trước đó ít nhất 30 ngày; (2) Không được thổi phồng giá để khuyến mãi giả; (3) Khuyến mãi trên 50% cần thông báo với Sở Công Thương. Vi phạm phạt 10–70 triệu đồng. Người tiêu dùng nên so sánh giá qua nhiều kênh (CafeF, CongGia.vn) trước khi mua hàng khuyến mãi.'),
        ('tmdt010','Thương mại điện tử','Livestream bán hàng','Quốc gia','Bộ Công Thương',
         'Bán hàng qua livestream trên TikTok, Facebook có phải tuân thủ quy định gì?',
         'Bán hàng qua livestream phải tuân thủ: (1) Đăng ký kinh doanh và khai báo thuế như bán hàng online thông thường; (2) Thông tin sản phẩm phải trung thực, không gây hiểu lầm; (3) Không bán sản phẩm cấm, hàng giả, không rõ nguồn gốc; (4) Không quảng cáo thuốc, TPCN theo hình thức gây hiểu lầm; (5) Không cản trở người mua thực hiện quyền đổi trả. Riêng với TikTok Shop: nền tảng yêu cầu xác minh danh tính và đăng ký kinh doanh để mở tính năng livestream bán hàng. Vi phạm bị xử phạt và khóa tài khoản.'),
    ])

    w('faq_g_thien_tai.xlsx', [
        ('tn001','Phòng chống thiên tai','Lũ lụt','Quốc gia','Bộ NN&PTNT',
         'Người dân cần chuẩn bị gì trước mùa lũ lụt?',
         'Chuẩn bị trước mùa lũ: (1) Dự trữ lương thực, nước uống đủ ít nhất 3–7 ngày (gạo, mì gói, nước đóng chai); (2) Dự phòng thuốc men, đặc biệt thuốc điều trị bệnh mãn tính; (3) Sạc đầy pin điện thoại, radio pin để nghe thông tin; (4) Chuẩn bị phao, áo phao cứu sinh; (5) Cất giữ giấy tờ quan trọng ở nơi khô ráo, cao hoặc cho vào túi zip; (6) Biết vị trí điểm sơ tán gần nhất; (7) Theo dõi cảnh báo lũ qua bản tin thời tiết, app cảnh báo thiên tai. Khi có lệnh sơ tán: tuân theo ngay, không chần chừ.'),
        ('tn002','Phòng chống thiên tai','Bão','Quốc gia','Bộ NN&PTNT',
         'Biện pháp an toàn khi có bão đổ bộ là gì?',
         'Trước khi bão đổ bộ: gia cố nhà cửa (chằng chống mái tôn, cắt tỉa cành cây to gần nhà), dự trữ lương thực và nước. Khi bão đổ bộ: (1) Ở trong nhà kiên cố, tránh xa cửa kính; (2) Cắt nguồn điện nếu có nguy cơ ngập; (3) Không ra đường khi bão đang đổ bộ; (4) Nếu ở vùng ven biển/vùng thấp: sơ tán theo lệnh của chính quyền; (5) Theo dõi thông tin qua đài phát thanh (điện có thể mất). Sau bão: cẩn thận dây điện đứt, cây đổ, nhà sập không ổn định. Gọi 112 khi có người bị nạn.'),
        ('tn003','Phòng chống thiên tai','Sạt lở đất','Quốc gia','Bộ NN&PTNT',
         'Dấu hiệu nhận biết nguy cơ sạt lở đất để phòng tránh?',
         'Dấu hiệu cảnh báo sạt lở đất: (1) Mưa to kéo dài (đặc biệt trên 200mm/ngày ở vùng núi); (2) Xuất hiện vết nứt trên mặt đất, tường nhà, đường; (3) Cây nghiêng, nghiêng đột ngột; (4) Tiếng nổ, tiếng ầm từ trong lòng đất hoặc sườn núi; (5) Nước suối đột ngột đục hơn bình thường; (6) Mực nước suối tăng nhanh. Khi thấy dấu hiệu: sơ tán ngay khỏi khu vực có nguy cơ, thông báo cho hàng xóm và chính quyền. Không ở lại nhà ven taluy, ven sông suối khi mưa lớn.'),
        ('tn004','Phòng chống thiên tai','Hỗ trợ thiên tai','Quốc gia','Bộ NN&PTNT',
         'Người dân bị thiệt hại do thiên tai được hỗ trợ những gì?',
         'Hỗ trợ thiệt hại do thiên tai theo Nghị định 20/2021/NĐ-CP và các quy định địa phương: (1) Hỗ trợ lương thực: gạo từ 15–45 kg/người/tháng; (2) Hỗ trợ nhà ở bị hư hại/sập: từ 30–130 triệu đồng tùy mức độ; (3) Hỗ trợ đời sống: 500.000–1 triệu đồng/người/tháng trong thời gian khắc phục; (4) Hỗ trợ sản xuất: giống cây trồng, vật nuôi, thức ăn thủy sản; (5) Miễn giảm thuế, nợ vay. Đăng ký với UBND xã trong vòng 15 ngày sau thiên tai. UBND huyện/tỉnh xem xét và cấp hỗ trợ.'),
        ('tn005','Phòng chống thiên tai','Hạn hán','Quốc gia','Bộ NN&PTNT',
         'Vùng hạn hán, thiếu nước sinh hoạt người dân được hỗ trợ thế nào?',
         'Hỗ trợ khi hạn hán, thiếu nước: (1) Nhà nước cung cấp nước sinh hoạt bằng xe bồn hoặc bơm từ nguồn nước tập trung; (2) Hỗ trợ khoan giếng cộng đồng; (3) Hỗ trợ giống cây trồng chịu hạn; (4) Miễn thủy lợi phí; (5) Khoanh nợ, giãn nợ vay sản xuất. Người dân thiếu nước nên thông báo ngay với UBND xã. Ban Chỉ huy PCTT&TKCN cấp huyện điều phối hỗ trợ. Ngoài ra, Mặt trận Tổ quốc và các tổ chức từ thiện cũng hỗ trợ trực tiếp trong thảm họa.'),
        ('tn006','Phòng chống thiên tai','Cứu nạn','Quốc gia','Bộ Quốc phòng',
         'Số điện thoại khẩn cấp khi gặp thiên tai và cần được cứu nạn?',
         'Số điện thoại khẩn cấp: 112 (khẩn cấp tổng hợp — miễn phí, 24/7); 113 (Cảnh sát); 114 (Cứu hỏa); 115 (Cấp cứu y tế); 1800 599 914 (Ủy ban Quốc gia Ứng phó sự cố thiên tai, miễn phí); đường dây TKCN hàng hải: 0511 3820 777. Khi gọi: nêu rõ vị trí (địa chỉ hoặc tọa độ GPS), tình trạng và số người cần cứu. Cài app "Thiên tai Việt Nam" của Tổng cục PCTT để nhận cảnh báo sớm theo địa điểm thực tế.'),
        ('tn007','Phòng chống thiên tai','Sét','Quốc gia','Bộ NN&PTNT',
         'Biện pháp an toàn khi có sét đánh và đang ở ngoài trời?',
         'An toàn khi có sét: Ngoài trời: (1) Vào trong nhà hoặc ô tô ngay; (2) Tránh xa cây cao, cột điện, vật kim loại; (3) Không đứng trên đỉnh đồi, cánh đồng trống; (4) Nếu không có nơi trú ẩn: ngồi thấp, chụm chân, không nằm, không nâng cao vật dẫn điện. Trong nhà: (1) Tránh xa cửa sổ, tường ngoài; (2) Không dùng điện thoại có dây, không tắm; (3) Rút phích cắm thiết bị điện. Lắp cột thu lôi cho nhà cao, chuồng trại gia súc ở vùng nhiều sét.'),
        ('tn008','Phòng chống thiên tai','Cháy rừng','Quốc gia','Bộ NN&PTNT',
         'Mùa khô nóng cần chú ý gì để phòng cháy rừng?',
         'Phòng cháy rừng mùa khô: (1) Không đốt lửa trong rừng hoặc gần rừng; (2) Không đốt rẫy khi không có phép và trong thời gian cao điểm cháy; (3) Không vứt mẩu thuốc lá, chai thủy tinh (có thể tập trung ánh sáng gây cháy); (4) Khi đi rừng mang theo nước; (5) Tắt máy xe trước khi dừng gần khu vực khô hanh. Khi phát hiện khói bốc lên bất thường: gọi ngay 114 hoặc Kiểm lâm địa phương. Mỗi người dân là "tai mắt" phòng cháy rừng — báo cáo sớm là yếu tố quyết định trong công tác chữa cháy.'),
        ('tn009','Phòng chống thiên tai','Ngập lụt đô thị','Quốc gia','Bộ Xây dựng',
         'Ngập úng đô thị — khiếu nại ở đâu và ai chịu trách nhiệm?',
         'Ngập úng đô thị: trách nhiệm thuộc Công ty Thoát nước và xử lý nước thải đô thị (đơn vị quản lý hạ tầng thoát nước), và UBND quận/huyện quản lý địa bàn. Phản ánh ngập úng: (1) Gọi đường dây nóng Công ty Thoát nước địa phương; (2) App phản ánh đô thị của tỉnh/thành phố (như iHanoi, TPHCM Report); (3) Phản ánh tới UBND phường/quận. Nếu ngập gây thiệt hại tài sản nghiêm trọng do lỗi hệ thống hạ tầng: có thể khiếu nại và yêu cầu bồi thường. Chụp ảnh bằng chứng thiệt hại và thời điểm xảy ra.'),
        ('tn010','Phòng chống thiên tai','Quyên góp từ thiện','Quốc gia','Bộ Tài chính',
         'Cá nhân, tổ chức quyên góp từ thiện để hỗ trợ thiên tai phải tuân thủ quy định gì?',
         'Theo Nghị định 93/2021/NĐ-CP về vận động, tiếp nhận, phân phối và sử dụng nguồn đóng góp: (1) Cá nhân/tổ chức muốn vận động quyên góp phải đăng ký với UBND cấp tỉnh/Bộ LĐ&TB&XH; (2) Tiền quyên góp phải gửi vào tài khoản mở riêng tại ngân hàng, ghi chép rõ thu chi; (3) Phải phân phối trong vòng 70 ngày (trong nước); (4) Báo cáo công khai trên phương tiện truyền thông sau khi thực hiện. Cá nhân nghệ sĩ, người nổi tiếng quyên góp cũng phải tuân thủ quy định này. Vi phạm: phạt đến 100 triệu đồng.'),
    ])

    w('faq_g_tre_em.xlsx', [
        ('te001','Trẻ em','Quyền trẻ em','Quốc gia','Bộ LĐTBXH',
         'Các quyền cơ bản của trẻ em theo Luật Trẻ em Việt Nam 2016?',
         'Luật Trẻ em 2016 quy định 25 quyền, nhóm thành 4 nhóm: (1) Quyền sống còn: được khai sinh, được chăm sóc sức khỏe, không bị bỏ rơi; (2) Quyền được bảo vệ: không bị bạo lực, xâm hại, bóc lột, mua bán; (3) Quyền phát triển: được học hành, vui chơi, tiếp cận thông tin; (4) Quyền tham gia: được bày tỏ ý kiến về các vấn đề liên quan. Mọi trẻ em đều có quyền bình đẳng, không phân biệt dân tộc, giới tính, hoàn cảnh gia đình.'),
        ('te002','Trẻ em','Bảo vệ trẻ em','Quốc gia','Bộ LĐTBXH',
         'Khi phát hiện trẻ em bị bạo hành hoặc xâm hại phải làm gì?',
         'Khi phát hiện hoặc nghi ngờ trẻ em bị bạo hành, xâm hại: (1) Gọi ngay Tổng đài bảo vệ trẻ em 111 (miễn phí, 24/7); (2) Báo Công an phường/xã; (3) Liên hệ UBND phường/xã (cán bộ phụ trách bảo vệ trẻ em); (4) Có thể báo ẩn danh — thông tin người tố cáo được bảo mật. Không nên chờ đợi hay xử lý nội bộ trong gia đình đối với các trường hợp nghiêm trọng. Trẻ em là nạn nhân xâm hại tình dục đặc biệt cần được bảo vệ khẩn cấp.'),
        ('te003','Trẻ em','Lao động trẻ em','Quốc gia','Bộ LĐTBXH',
         'Trẻ em dưới 18 tuổi có được đi làm thêm không?',
         'Quy định về lao động người chưa thành niên: (1) Dưới 13 tuổi: cấm sử dụng lao động trong mọi trường hợp; (2) 13–15 tuổi: chỉ được làm các công việc nhẹ trong danh mục Bộ LĐTBXH cho phép, cần sự đồng ý của cha mẹ; (3) 15–18 tuổi: được làm việc nhưng không làm công việc nặng nhọc, độc hại; thời gian làm không quá 8 giờ/ngày, không làm đêm. Thuê lao động dưới 13 tuổi: phạt hình sự. Tố cáo: Thanh tra Bộ LĐTBXH hoặc Tổng đài 111.'),
        ('te004','Trẻ em','Bảo vệ trực tuyến','Quốc gia','Bộ TT&TT',
         'Bảo vệ trẻ em khỏi nội dung độc hại trên internet như thế nào?',
         'Bảo vệ trẻ em trên internet: (1) Sử dụng phần mềm kiểm soát nội dung (Google Family Link, Norton Family, Net Nanny); (2) Bật chế độ Safe Search trên Google, YouTube Kids thay vì YouTube thường; (3) Giới hạn thời gian sử dụng thiết bị; (4) Đặt thiết bị ở nơi chung, không để trẻ dùng một mình; (5) Giáo dục trẻ về an toàn mạng, không chia sẻ thông tin cá nhân. Báo cáo nội dung độc hại nhắm vào trẻ em: Cục Trẻ em (Bộ LĐTBXH) và Cục An toàn thông tin (Bộ TT&TT) qua nettruong.vn.'),
        ('te005','Trẻ em','Khai sinh','Quốc gia','Bộ Tư pháp',
         'Khai sinh cho trẻ em không xác định được cha là ai làm như thế nào?',
         'Khai sinh cho trẻ không xác định cha: (1) Đăng ký khai sinh tại UBND xã/phường nơi mẹ cư trú với thông tin của mẹ; (2) Phần họ tên cha để trống hoặc ghi là "chưa xác định"; (3) Trẻ mang họ của mẹ; (4) Sau này nếu xác định được cha, làm thủ tục nhận cha — có thể tự nguyện hoặc theo bản án của Tòa. Trẻ không xác định được cả cha lẫn mẹ (trẻ bị bỏ rơi): UBND xã/phường nơi phát hiện lập hồ sơ, đặt tên, khai sinh và giao cho cơ sở bảo trợ xã hội hoặc gia đình nhận nuôi.'),
        ('te006','Trẻ em','Giám hộ','Quốc gia','Bộ Tư pháp',
         'Ai là giám hộ đương nhiên của trẻ em khi cha mẹ mất hoặc bị mất năng lực?',
         'Giám hộ đương nhiên của người chưa thành niên (Điều 52 BLDS 2015): (1) Anh, chị ruột đã thành niên đủ điều kiện; (2) Nếu không có: ông nội, bà nội hoặc ông ngoại, bà ngoại đủ điều kiện; (3) Nếu không có: bác, chú, cậu, cô, dì đủ điều kiện. Nếu không có người thân thích phù hợp: Tòa án chỉ định người giám hộ khác hoặc đề nghị Ủy ban bảo vệ trẻ em (UBND xã đảm nhận). Giám hộ được đăng ký tại UBND xã/phường nơi cư trú của trẻ.'),
        ('te007','Trẻ em','Trường học','Quốc gia','Bộ GD&ĐT',
         'Trẻ em bị bạo lực học đường phải làm gì?',
         'Khi trẻ em bị bạo lực học đường: (1) Báo ngay với giáo viên chủ nhiệm hoặc Ban Giám hiệu trường; (2) Gặp gỡ phụ huynh của học sinh vi phạm theo mời của nhà trường; (3) Nếu nhà trường không xử lý: khiếu nại với Phòng GD&ĐT quận/huyện; (4) Nếu gây thương tích: trình báo công an. Bố mẹ cần lắng nghe con, không phán xét, khuyến khích con kể chuyện. Bảo vệ tâm lý: trường phải có giáo viên/tư vấn tâm lý học đường. Gọi Tổng đài 111 nếu bạo lực nghiêm trọng.'),
        ('te008','Trẻ em','Phòng chống xâm hại','Quốc gia','Bộ LĐTBXH',
         'Dạy trẻ em cách tự bảo vệ bản thân khỏi xâm hại tình dục?',
         'Dạy trẻ kỹ năng tự bảo vệ: (1) Quy tắc 5 ngón tay/vòng tròn an toàn: chỉ người thân tin tưởng trong "vòng tròn an toàn" mới được đụng vào người; (2) Dạy trẻ biết nói KHÔNG với những đụng chạm không thoải mái; (3) Dạy trẻ kể lại với người lớn tin tưởng nếu bị đụng chạm không phù hợp; (4) Nhấn mạnh: không bao giờ là lỗi của trẻ nếu bị xâm hại; (5) Không có bí mật nào về cơ thể cần giấu với cha mẹ. Sử dụng sách, video giáo dục phù hợp độ tuổi. Tổng đài 111 hỗ trợ tư vấn cho cả cha mẹ và trẻ em.'),
        ('te009','Trẻ em','Quyền vui chơi','Quốc gia','Bộ LĐTBXH',
         'Nhà trường có được bắt học sinh học thêm bắt buộc không?',
         'Theo quy định Bộ GD&ĐT: (1) Nhà trường KHÔNG được tổ chức dạy thêm bắt buộc cho học sinh; (2) Không được gợi ý, ép buộc học sinh học thêm dưới bất kỳ hình thức nào (gợi ý điểm số, đe dọa...); (3) Không được dạy trước chương trình để bán dịch vụ dạy thêm; (4) Giáo viên không được tổ chức dạy thêm cho học sinh của mình đang dạy trên lớp. Vi phạm: giáo viên bị xử lý kỷ luật, trường bị đình chỉ dạy thêm. Tố cáo: Phòng GD&ĐT quận/huyện hoặc Sở GD&ĐT tỉnh.'),
        ('te010','Trẻ em','Chế độ chính sách','Quốc gia','Bộ LĐTBXH',
         'Trẻ em sinh ra trong gia đình hộ nghèo được hưởng ưu đãi gì?',
         'Trẻ em trong hộ nghèo được hưởng: (1) Miễn 100% học phí từ mầm non đến hết THCS; (2) Thẻ BHYT miễn phí (Nhà nước đóng thay); (3) Hỗ trợ tiền ăn trưa trẻ mầm non (290.000 đồng/tháng); (4) Miễn phí học bơi (một số địa phương); (5) Được ưu tiên nhận học bổng và hỗ trợ sách vở; (6) Trẻ khuyết tật trong hộ nghèo được hưởng trợ cấp bổ sung. Hộ nghèo cần đăng ký với UBND xã/phường để được cấp các giấy tờ xác nhận và hưởng các chính sách ưu đãi này.'),
    ])

    print('\nBatch 13 hoan thanh.')

if __name__ == '__main__':
    main()
