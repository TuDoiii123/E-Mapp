"""
seed_new_procedures.py
Thêm 21 thủ tục mới vào procedures + service_requirements.
ON CONFLICT DO NOTHING — chạy lại an toàn.
"""
import sys, uuid
sys.path.insert(0, '.')
from server import app
from models.db import db
from sqlalchemy import text

# ─────────────────────────────────────────────────────────────────────────────
# PROCEDURES DATA
# fields: id, name, code, category, fee, fee_note, processing_days,
#         processing_note, implementing_level, agency, steps, conditions
# ─────────────────────────────────────────────────────────────────────────────
PROCEDURES = [
  # ── CIVIL / Hộ tịch ───────────────────────────────────────────────────────
  dict(
    id='dang-ky-lai-khai-sinh',
    name='Đăng ký lại khai sinh',
    code='TTHC-DLKS', category='civil', fee=0, fee_note='Miễn lệ phí',
    processing_days=5, processing_note='5 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='ward', agency='UBND cấp xã/phường nơi đã đăng ký khai sinh lần đầu',
    steps="""\
Bước 1: Cha, mẹ hoặc người có yêu cầu chuẩn bị hồ sơ gồm Tờ khai đăng ký lại khai sinh (Mẫu HTT-2014-01.3), CCCD của người yêu cầu, các giấy tờ liên quan đến khai sinh trước đây (sổ hộ khẩu cũ, giấy tờ học tập, bảo hiểm...).
Bước 2: Nộp hồ sơ tại UBND cấp xã nơi đã đăng ký khai sinh trước đây hoặc nơi có hồ sơ, sổ sách liên quan; hoặc nộp trực tuyến qua Cổng DVC.
Bước 3: Cán bộ tư pháp kiểm tra hồ sơ, tra cứu hồ sơ gốc; xác minh thông tin nếu cần. Thời hạn giải quyết: 5 ngày làm việc.
Bước 4: Nhận Trích lục khai sinh (bản đăng ký lại) tại bộ phận một cửa UBND cấp xã.""",
    conditions="""\
Áp dụng khi bản gốc Giấy khai sinh bị mất, hư hỏng hoặc Sổ đăng ký khai sinh đã bị thất lạc.
Người yêu cầu phải cung cấp ít nhất 2 trong số các giấy tờ chứng minh thông tin khai sinh trước đây (sổ hộ khẩu, học bạ, bảo hiểm, giấy tờ quân sự...).
Trường hợp không có giấy tờ chứng minh, cần xác nhận của nhân chứng có giá trị pháp lý.""",
  ),
  dict(
    id='dang-ky-nhan-con',
    name='Nhận cha, mẹ, con',
    code='TTHC-NCC', category='civil', fee=0, fee_note='Miễn lệ phí',
    processing_days=3, processing_note='3 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='ward', agency='UBND cấp xã/phường nơi cư trú của người nhận hoặc người được nhận',
    steps="""\
Bước 1: Người yêu cầu chuẩn bị hồ sơ gồm Tờ khai đăng ký nhận cha/mẹ/con (Mẫu HTT-2014-05), CCCD của người nhận và người được nhận (hoặc người đại diện nếu là trẻ em), các giấy tờ chứng minh quan hệ huyết thống (kết quả ADN nếu có tranh chấp).
Bước 2: Nộp hồ sơ trực tiếp tại UBND cấp xã nơi cư trú của người nhận hoặc người được nhận; hoặc nộp trực tuyến qua Cổng DVC.
Bước 3: Cán bộ tư pháp kiểm tra hồ sơ, xác minh thông tin; niêm yết công khai 3 ngày (nếu không có tranh chấp). Thời hạn: 3 ngày làm việc.
Bước 4: Người yêu cầu nhận Trích lục đăng ký nhận cha/mẹ/con; cập nhật vào Sổ hộ khẩu/CCCD theo quy định.""",
    conditions="""\
Người nhận cha/mẹ/con phải còn sống tại thời điểm đăng ký.
Không có tranh chấp về quan hệ cha, mẹ, con; nếu có tranh chấp cần bản án/quyết định của Tòa án.
Đối với trẻ em chưa thành niên, cần có sự đồng ý của người đang nuôi dưỡng trẻ.""",
  ),
  dict(
    id='thay-doi-canh-chinh-ho-tich',
    name='Thay đổi, cải chính hộ tịch',
    code='TTHC-CCHT', category='civil', fee=0, fee_note='Miễn lệ phí',
    processing_days=3, processing_note='3 ngày làm việc; trường hợp phức tạp không quá 8 ngày',
    level='ward', agency='UBND cấp xã/phường nơi đã đăng ký hộ tịch cần cải chính',
    steps="""\
Bước 1: Người yêu cầu chuẩn bị hồ sơ gồm Tờ khai thay đổi/cải chính hộ tịch (Mẫu HTT-2014-07), CCCD còn hiệu lực, Trích lục hộ tịch cần cải chính (khai sinh, kết hôn...) và các giấy tờ chứng minh nội dung cần thay đổi/cải chính.
Bước 2: Nộp hồ sơ tại UBND cấp xã nơi đã đăng ký hộ tịch hoặc nơi có Sổ hộ tịch cần cải chính; hoặc nộp trực tuyến.
Bước 3: Cán bộ tư pháp kiểm tra tính hợp lệ, xác minh tài liệu gốc trong Sổ hộ tịch; ký duyệt. Thời hạn: 3 ngày làm việc.
Bước 4: Người yêu cầu nhận Trích lục hộ tịch đã được cải chính; cập nhật thông tin vào CCCD nếu có thay đổi họ, tên, ngày sinh.""",
    conditions="""\
Chỉ được cải chính thông tin đã ghi sai do lỗi của cán bộ hoặc do giấy tờ gốc có sai sót.
Không được thay đổi quốc tịch, dân tộc theo thủ tục hộ tịch thông thường; phải theo thủ tục riêng.
Phải có giấy tờ gốc chứng minh nội dung đúng (giấy tờ học tập, y tế, quân đội, bảo hiểm...).""",
  ),
  dict(
    id='cap-ban-sao-trich-luc-ho-tich',
    name='Cấp bản sao trích lục hộ tịch',
    code='TTHC-BSTL', category='civil', fee=8000, fee_note='8.000 đ/bản sao',
    processing_days=1, processing_note='Trong ngày làm việc hoặc ngày làm việc tiếp theo',
    level='ward', agency='UBND cấp xã/phường nơi lưu trữ Sổ hộ tịch gốc',
    steps="""\
Bước 1: Người yêu cầu chuẩn bị Tờ khai yêu cầu cấp bản sao trích lục hộ tịch (Mẫu HTT-2014-09.1), CCCD còn hiệu lực, nêu rõ loại trích lục cần cấp (khai sinh, kết hôn, khai tử).
Bước 2: Nộp tại bộ phận một cửa UBND cấp xã nơi đã đăng ký hộ tịch, hoặc nộp trực tuyến qua Cổng DVC quốc gia.
Bước 3: Cán bộ tra cứu Sổ hộ tịch gốc hoặc Cơ sở dữ liệu hộ tịch điện tử; in Trích lục và ký xác nhận. Thời hạn: trong ngày làm việc.
Bước 4: Nhận bản sao Trích lục hộ tịch có chữ ký, đóng dấu của UBND cấp xã.""",
    conditions="""\
Người yêu cầu là đương sự hoặc người có quyền, lợi ích liên quan đến sự kiện hộ tịch.
Trường hợp ủy quyền phải có Giấy ủy quyền có công chứng và CCCD người được ủy quyền.
Phải nộp lệ phí theo quy định hiện hành (8.000 đ/bản sao).""",
  ),
  dict(
    id='dang-ky-tam-tru',
    name='Đăng ký tạm trú',
    code='TTHC-DKTT', category='civil', fee=0, fee_note='Miễn lệ phí',
    processing_days=3, processing_note='3 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='ward', agency='Công an cấp xã/phường nơi người đến tạm trú',
    steps="""\
Bước 1: Người đến tạm trú chuẩn bị Tờ khai đăng ký tạm trú (Mẫu CT02 theo Thông tư 56/2021/TT-BCA), CCCD/Căn cước còn hiệu lực, giấy tờ chứng minh chỗ ở hợp lệ (hợp đồng thuê nhà, xác nhận chủ nhà/chủ hộ).
Bước 2: Nộp hồ sơ qua ứng dụng VNeID hoặc trực tiếp tại Công an cấp xã nơi đến tạm trú; có thể nộp qua Cổng DVC.
Bước 3: Cán bộ Công an kiểm tra, xác minh; cập nhật thông tin tạm trú vào Cơ sở dữ liệu quốc gia về dân cư. Thời hạn: 3 ngày làm việc.
Bước 4: Người tạm trú nhận thông báo kết quả qua VNeID hoặc tại Công an cấp xã; sổ tạm trú được cập nhật điện tử.""",
    conditions="""\
Người không có chỗ ở thường trú hoặc đến ở tại địa chỉ khác với nơi thường trú từ 30 ngày trở lên.
Có chỗ ở hợp lệ: thuê, mượn, ở nhờ có xác nhận của chủ nhà.
Tạm trú có thời hạn tối đa 2 năm, có thể gia hạn khi hết hạn.""",
  ),
  dict(
    id='tach-ho-khau',
    name='Tách hộ / Điều chỉnh thông tin cư trú',
    code='TTHC-THHK', category='civil', fee=0, fee_note='Miễn lệ phí',
    processing_days=7, processing_note='7 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='ward', agency='Công an cấp xã/phường nơi có hộ khẩu cần tách',
    steps="""\
Bước 1: Người yêu cầu tách hộ chuẩn bị Tờ khai điều chỉnh thông tin cư trú (Mẫu CT01), CCCD còn hiệu lực, giấy tờ chứng minh chỗ ở mới hợp lệ (sở hữu, thuê, mượn).
Bước 2: Nộp hồ sơ qua ứng dụng VNeID hoặc tại Công an cấp xã có thẩm quyền; hoặc qua Cổng DVC quốc gia/tỉnh.
Bước 3: Cán bộ Công an xác minh thông tin, kiểm tra điều kiện tách hộ; cập nhật Cơ sở dữ liệu dân cư. Thời hạn: 7 ngày làm việc.
Bước 4: Nhận thông báo kết quả qua VNeID; thông tin hộ gia đình mới được cập nhật và phản ánh trên CCCD/Căn cước.""",
    conditions="""\
Người yêu cầu tách hộ phải từ đủ 18 tuổi và có năng lực hành vi dân sự đầy đủ.
Có chỗ ở hợp lệ tại địa chỉ tách ra (sở hữu, thuê, mượn hợp pháp).
Việc tách hộ không được làm ảnh hưởng đến quyền lợi của các thành viên còn lại trong hộ.""",
  ),
  dict(
    id='cap-tai-khoan-dinh-danh',
    name='Cấp tài khoản định danh điện tử (VNeID)',
    code='TTHC-DINH-DANH', category='civil', fee=0, fee_note='Miễn phí',
    processing_days=1, processing_note='Cấp ngay trong ngày làm việc hoặc qua ứng dụng VNeID',
    level='province', agency='Công an cấp tỉnh/huyện/xã hoặc qua ứng dụng VNeID',
    steps="""\
Bước 1: Công dân tải ứng dụng VNeID từ App Store / Google Play; chọn "Đăng ký tài khoản định danh điện tử" và nhập số CCCD/Căn cước còn hiệu lực.
Bước 2: Xác thực sinh trắc học trực tiếp trong ứng dụng (nhận diện khuôn mặt, ảnh CCCD) hoặc đến Công an cấp xã để xác thực thủ công nếu không tự thực hiện được.
Bước 3: Hệ thống kiểm tra khớp thông tin với Cơ sở dữ liệu quốc gia về dân cư; phê duyệt tài khoản mức 1 (xác thực cơ bản) hoặc mức 2 (xác thực sinh trắc).
Bước 4: Công dân nhận tài khoản VNeID; có thể sử dụng để nộp hồ sơ trực tuyến, xem giấy tờ số, xác thực danh tính trực tuyến.""",
    conditions="""\
Công dân Việt Nam từ đủ 14 tuổi có CCCD/Căn cước còn hiệu lực.
Thiết bị di động có kết nối internet và camera chụp ảnh rõ nét.
Tài khoản mức 2 yêu cầu xác thực khuôn mặt khớp với dữ liệu sinh trắc đã thu thập khi làm CCCD.""",
  ),
  # ── LAND / Đất đai ────────────────────────────────────────────────────────
  dict(
    id='chuyen-nhuong-quyen-su-dung-dat',
    name='Đăng ký chuyển nhượng quyền sử dụng đất',
    code='TTHC-CNQSD', category='land', fee=500000, fee_note='Lệ phí cấp GCN: từ 100.000 – 500.000 đ; thuế TNCN, thuế trước bạ theo giá trị giao dịch',
    processing_days=10, processing_note='10 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
    level='district', agency='Văn phòng Đăng ký đất đai cấp huyện / Chi nhánh VPĐKĐĐ',
    steps="""\
Bước 1: Hai bên (bên bán và bên mua) ký Hợp đồng chuyển nhượng QSDĐ có công chứng tại Văn phòng công chứng; chuẩn bị GCN QSDĐ bản gốc, CCCD hai bên, tờ khai thuế TNCN, thuế trước bạ.
Bước 2: Nộp hồ sơ tại Văn phòng Đăng ký đất đai cấp huyện hoặc Bộ phận một cửa UBND huyện; hoặc nộp trực tuyến qua Cổng DVC.
Bước 3: VPĐKĐĐ kiểm tra hồ sơ, thông báo nghĩa vụ tài chính (thuế TNCN 2%, thuế trước bạ 0,5%); bên mua nộp thuế tại Chi cục Thuế. Thời hạn: 10 ngày làm việc.
Bước 4: Nhận GCN QSDĐ đã sang tên (Sổ đỏ/Sổ hồng mới) tại VPĐKĐĐ hoặc qua bưu chính.""",
    conditions="""\
GCN QSDĐ bản gốc còn hiệu lực; đất không có tranh chấp, không trong diện thu hồi.
Hợp đồng chuyển nhượng phải được công chứng/chứng thực theo quy định (trừ giữa vợ chồng, cha mẹ con, anh chị em ruột).
Đã hoàn thành nghĩa vụ tài chính: thuế TNCN (bên bán) và lệ phí trước bạ (bên mua).
Không thuộc trường hợp đất đang bị kê biên để đảm bảo thi hành án.""",
  ),
  dict(
    id='tach-thua-dat',
    name='Tách thửa / Hợp thửa đất',
    code='TTHC-TATD', category='land', fee=200000, fee_note='Phí đo đạc, lệ phí cấp GCN: theo quy định địa phương',
    processing_days=15, processing_note='15 ngày làm việc; trường hợp phức tạp không quá 30 ngày',
    level='district', agency='Văn phòng Đăng ký đất đai cấp huyện',
    steps="""\
Bước 1: Người sử dụng đất chuẩn bị Đơn đề nghị tách thửa/hợp thửa (Mẫu 11/ĐĐ theo TT 24/2014/TT-BTNMT), GCN QSDĐ bản gốc, CCCD còn hiệu lực, bản vẽ vị trí thửa đất dự kiến tách/hợp.
Bước 2: Nộp hồ sơ tại VPĐKĐĐ cấp huyện hoặc Bộ phận một cửa UBND huyện; hoặc trực tuyến qua Cổng DVC tỉnh Thanh Hóa.
Bước 3: VPĐKĐĐ kiểm tra điều kiện, tổ chức đo đạc bản đồ địa chính (hoặc yêu cầu đo vẽ tư nhân); lập hồ sơ kỹ thuật thửa đất mới. Thời hạn: 15 ngày.
Bước 4: Người sử dụng đất nhận GCN QSDĐ mới cho từng thửa sau tách; nộp lệ phí theo quy định.""",
    conditions="""\
Diện tích mỗi thửa sau tách không nhỏ hơn diện tích tối thiểu được phép tách theo quy định địa phương.
Thửa đất không có tranh chấp, không bị kê biên, không trong diện quy hoạch thu hồi.
Việc tách/hợp thửa phải phù hợp quy hoạch sử dụng đất, quy hoạch xây dựng đã được phê duyệt.""",
  ),
  dict(
    id='dang-ky-bien-dong-dat-dai',
    name='Đăng ký biến động đất đai',
    code='TTHC-BDDĐ', category='land', fee=100000, fee_note='Phí đăng ký biến động: từ 50.000 – 100.000 đ',
    processing_days=10, processing_note='10 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='district', agency='Văn phòng Đăng ký đất đai cấp huyện',
    steps="""\
Bước 1: Người sử dụng đất chuẩn bị hồ sơ tùy loại biến động: thừa kế (bản án/di chúc), tặng cho (hợp đồng công chứng), thế chấp/giải chấp (hợp đồng ngân hàng), thay đổi thông tin (CCCD mới). Kèm GCN QSDĐ bản gốc.
Bước 2: Nộp hồ sơ tại VPĐKĐĐ cấp huyện hoặc nộp trực tuyến qua Cổng DVC tỉnh; nhận phiếu tiếp nhận.
Bước 3: VPĐKĐĐ kiểm tra hồ sơ, xác nhận biến động vào GCN QSDĐ gốc hoặc cấp GCN mới tùy từng trường hợp. Thời hạn: 10 ngày làm việc.
Bước 4: Người sử dụng đất nhận GCN QSDĐ đã cập nhật biến động; nộp lệ phí theo quy định.""",
    conditions="""\
GCN QSDĐ bản gốc còn hiệu lực; đất không có tranh chấp.
Phải đăng ký biến động trong vòng 30 ngày kể từ khi phát sinh biến động.
Hợp đồng/văn bản làm căn cứ biến động phải có công chứng/chứng thực hợp lệ (trừ trường hợp thừa kế theo pháp luật).""",
  ),
  # ── CONSTRUCTION / Xây dựng ───────────────────────────────────────────────
  dict(
    id='hoan-cong-cong-trinh',
    name='Thông báo hoàn thành công trình xây dựng đưa vào sử dụng',
    code='TTHC-HCCG', category='construction', fee=0, fee_note='Miễn phí',
    processing_days=7, processing_note='Cơ quan có thẩm quyền kiểm tra trong 7 ngày làm việc',
    level='district', agency='UBND cấp huyện / Sở Xây dựng (tùy cấp công trình)',
    steps="""\
Bước 1: Chủ đầu tư hoàn thành thi công, lập hồ sơ hoàn công gồm: Thông báo hoàn thành công trình, Bản vẽ hoàn công (as-built), Biên bản nghiệm thu từng phần, Hợp đồng thi công, Giấy phép xây dựng gốc.
Bước 2: Nộp hồ sơ tại Bộ phận một cửa UBND cấp huyện (nhà ở riêng lẻ) hoặc Sở Xây dựng (công trình cấp tỉnh); có thể nộp trực tuyến qua Cổng DVC.
Bước 3: Cơ quan có thẩm quyền kiểm tra thực địa (nếu cần), xem xét hồ sơ. Thời hạn: 7 ngày làm việc kể từ ngày nhận thông báo.
Bước 4: Công trình không bị phát hiện vi phạm được đưa vào sử dụng; chủ đầu tư tiến hành đăng ký nhà ở/tài sản gắn liền với đất (nếu có).""",
    conditions="""\
Đã xây dựng đúng theo Giấy phép xây dựng được cấp; không vi phạm quy hoạch, thiết kế.
Hoàn thành đầy đủ hệ thống PCCC được nghiệm thu (nếu bắt buộc).
Không áp dụng cho công trình đã xây dựng trái phép; phải giải quyết vi phạm trước.""",
  ),
  # ── BUSINESS / Kinh doanh ─────────────────────────────────────────────────
  dict(
    id='thay-doi-noi-dung-dkdn',
    name='Thay đổi nội dung đăng ký doanh nghiệp',
    code='TTHC-TDDN', category='business', fee=50000, fee_note='Lệ phí đăng ký thay đổi: 50.000 đ',
    processing_days=3, processing_note='3 ngày làm việc kể từ ngày nhận hồ sơ hợp lệ',
    level='province', agency='Phòng Đăng ký kinh doanh — Sở Kế hoạch và Đầu tư tỉnh Thanh Hóa',
    steps="""\
Bước 1: Doanh nghiệp chuẩn bị hồ sơ: Thông báo thay đổi nội dung đăng ký doanh nghiệp (theo loại thay đổi: tên, địa chỉ, vốn, người đại diện...), Quyết định/Biên bản họp HĐTV/ĐHCĐ (nếu có), CCCD người đại diện pháp luật mới (nếu thay đổi).
Bước 2: Nộp hồ sơ qua Hệ thống thông tin quốc gia về đăng ký doanh nghiệp (dangkykinhdoanh.gov.vn) hoặc trực tiếp tại Phòng ĐKKD — Sở KH&ĐT tỉnh Thanh Hóa.
Bước 3: Phòng ĐKKD kiểm tra hồ sơ; cấp Giấy chứng nhận ĐKDN mới hoặc thông báo bổ sung nếu thiếu. Thời hạn: 3 ngày làm việc.
Bước 4: Doanh nghiệp nhận GCN ĐKDN đã cập nhật thay đổi; công bố thông tin thay đổi trên Cổng thông tin quốc gia trong vòng 30 ngày.""",
    conditions="""\
Doanh nghiệp đang hoạt động hợp lệ (không bị đình chỉ, giải thể, phá sản).
Người ký hồ sơ là người đại diện theo pháp luật của doanh nghiệp hoặc người được ủy quyền hợp lệ.
Thay đổi tên: tên mới không trùng, không gây nhầm lẫn với doanh nghiệp đã đăng ký.""",
  ),
  dict(
    id='giai-the-doanh-nghiep',
    name='Đăng ký giải thể doanh nghiệp',
    code='TTHC-GTDN', category='business', fee=0, fee_note='Miễn lệ phí đăng ký giải thể',
    processing_days=5, processing_note='5 ngày làm việc sau khi đủ điều kiện giải thể',
    level='province', agency='Phòng Đăng ký kinh doanh — Sở Kế hoạch và Đầu tư tỉnh Thanh Hóa',
    steps="""\
Bước 1: HĐTV/ĐHCĐ/chủ sở hữu thông qua Quyết định giải thể; thành lập Hội đồng thanh lý tài sản (nếu có). Công bố thông tin giải thể trên Cổng thông tin quốc gia về ĐKDN.
Bước 2: Hoàn thành nghĩa vụ tài chính: nộp đủ thuế, thanh toán nợ lao động, nợ BHXH, các khoản nợ khác. Lấy xác nhận hoàn thành nghĩa vụ từ Cơ quan thuế và BHXH.
Bước 3: Nộp hồ sơ giải thể tại Phòng ĐKKD Sở KH&ĐT hoặc qua dangkykinhdoanh.gov.vn. Hồ sơ gồm: Thông báo giải thể, QĐ giải thể, GCN ĐKDN gốc, xác nhận hoàn thành nghĩa vụ thuế/BHXH.
Bước 4: Phòng ĐKKD cập nhật tình trạng giải thể trên Cổng thông tin quốc gia trong 5 ngày làm việc; doanh nghiệp chấm dứt tư cách pháp nhân.""",
    conditions="""\
Đã thanh toán hết nợ và các nghĩa vụ tài sản; không đang trong quá trình giải quyết tranh chấp tại Tòa án.
Đã nộp đủ thuế, hoàn thành nghĩa vụ BHXH; có xác nhận của cơ quan thuế và BHXH.
Không đang trong tình trạng bị khởi kiện hoặc phong tỏa tài sản theo quyết định của Tòa án.""",
  ),
  dict(
    id='tam-ngung-kinh-doanh',
    name='Tạm ngừng / tiếp tục hoạt động kinh doanh',
    code='TTHC-TNKD', category='business', fee=0, fee_note='Miễn lệ phí',
    processing_days=3, processing_note='3 ngày làm việc kể từ ngày nhận hồ sơ hợp lệ',
    level='province', agency='Phòng Đăng ký kinh doanh — Sở Kế hoạch và Đầu tư tỉnh Thanh Hóa',
    steps="""\
Bước 1: Doanh nghiệp/hộ kinh doanh chuẩn bị Thông báo tạm ngừng hoặc tiếp tục kinh doanh (theo mẫu), nêu rõ thời gian tạm ngừng (tối đa 1 năm/lần).
Bước 2: Nộp hồ sơ qua dangkykinhdoanh.gov.vn (doanh nghiệp) hoặc tại Phòng Tài chính-Kế hoạch UBND huyện (hộ kinh doanh); hoặc qua Cổng DVC.
Bước 3: Cơ quan đăng ký kiểm tra hồ sơ; ghi nhận thông tin tạm ngừng vào hệ thống đăng ký. Thời hạn: 3 ngày làm việc.
Bước 4: Trong thời gian tạm ngừng, doanh nghiệp/hộ kinh doanh nộp báo cáo thuế theo quy định (dạng quyết toán 0 đồng) và không phát sinh giao dịch kinh doanh.""",
    conditions="""\
Nộp thông báo tạm ngừng trước ít nhất 3 ngày làm việc trước ngày tạm ngừng dự kiến.
Mỗi lần tạm ngừng không quá 1 năm; có thể gia hạn nhưng tổng không quá 2 năm liên tiếp.
Đã nộp đầy đủ báo cáo thuế, không có nợ thuế quá hạn tại thời điểm nộp thông báo.""",
  ),
  # ── JUSTICE / Tư pháp ────────────────────────────────────────────────────
  dict(
    id='chung-thuc-ban-sao',
    name='Chứng thực bản sao từ bản chính',
    code='TTHC-CTBS', category='justice', fee=2000, fee_note='2.000 đ/trang; tối đa 200.000 đ/bản sao',
    processing_days=1, processing_note='Trong ngày làm việc hoặc trả ngay trong buổi làm việc',
    level='ward', agency='UBND cấp xã/phường/thị trấn hoặc Phòng Tư pháp cấp huyện',
    steps="""\
Bước 1: Người yêu cầu mang bản chính giấy tờ cần chứng thực (CCCD, bằng cấp, GCN QSDĐ, hộ chiếu...) và các bản sao đã chụp đến cơ quan chứng thực.
Bước 2: Cán bộ tiếp nhận đối chiếu bản sao với bản chính; nếu đúng sẽ đóng dấu xác nhận "Chứng thực bản sao từ bản chính" lên từng trang bản sao.
Bước 3: Người yêu cầu nộp lệ phí: 2.000 đ/trang chứng thực, tối đa 200.000 đ/bản sao. Nhận bản sao đã chứng thực ngay trong buổi làm việc.
Bước 4: Bản sao có chứng thực có giá trị sử dụng trong 12 tháng kể từ ngày chứng thực (trừ trường hợp pháp luật quy định khác).""",
    conditions="""\
Phải xuất trình bản chính để đối chiếu; không chứng thực bản sao từ bản sao khác.
Không chứng thực bản sao các giấy tờ đã hết hạn, bị tẩy xóa, sửa chữa làm thay đổi nội dung.
Người yêu cầu chứng thực chịu trách nhiệm về tính xác thực của bản chính xuất trình.""",
  ),
  dict(
    id='cap-phieu-lltp-so2',
    name='Cấp phiếu lý lịch tư pháp số 2',
    code='TTHC-LLTP2', category='justice', fee=200000, fee_note='Lệ phí: 200.000 đ/phiếu',
    processing_days=10, processing_note='10 ngày làm việc; trường hợp xác minh nước ngoài: 20 ngày',
    level='province', agency='Sở Tư pháp tỉnh Thanh Hóa (34 Đại lộ Lê Lợi, TP Thanh Hóa)',
    steps="""\
Bước 1: Cơ quan/tổ chức có nhu cầu chuẩn bị Văn bản đề nghị cấp Phiếu LLTP số 2 (có chức năng, thẩm quyền theo quy định), Tờ khai yêu cầu theo mẫu, danh sách người cần tra cứu kèm CCCD của từng người.
Bước 2: Nộp hồ sơ tại Bộ phận một cửa Sở Tư pháp tỉnh Thanh Hóa hoặc qua Cổng DVC quốc gia; nộp lệ phí 200.000 đ/phiếu.
Bước 3: Sở Tư pháp tra cứu Cơ sở dữ liệu lý lịch tư pháp quốc gia, xác minh tại Tòa án và Cơ quan thi hành án (nếu cần). Thời hạn: 10 ngày làm việc.
Bước 4: Cơ quan/tổ chức nhận Phiếu LLTP số 2 có đóng dấu của Sở Tư pháp tại nơi nộp hồ sơ hoặc qua bưu chính.""",
    conditions="""\
Chỉ cơ quan nhà nước, tổ chức chính trị, tổ chức chính trị-xã hội có thẩm quyền mới được yêu cầu cấp Phiếu số 2.
Trường hợp cá nhân cần Phiếu số 2 để sử dụng theo quy định pháp luật về đầu tư, kinh doanh phải có văn bản xác nhận.
Nộp lệ phí theo quy định; miễn phí cho một số đối tượng theo Thông tư của Bộ Tư pháp.""",
  ),
  # ── TRANSPORT / Giao thông ───────────────────────────────────────────────
  dict(
    id='doi-cap-lai-gplx',
    name='Đổi / Cấp lại giấy phép lái xe',
    code='TTHC-DCGPLX', category='transport', fee=135000, fee_note='Lệ phí: 135.000 đ (đổi); 270.000 đ (cấp lại do mất)',
    processing_days=5, processing_note='5 ngày làm việc kể từ ngày nộp đủ hồ sơ',
    level='province', agency='Sở Giao thông Vận tải tỉnh Thanh Hóa (09 Đại lộ Hùng Vương, TP Thanh Hóa)',
    steps="""\
Bước 1: Người lái xe chuẩn bị hồ sơ: Đơn đề nghị đổi/cấp lại GPLX (Mẫu 3 theo TT 12/2017/TT-BGTVT), CCCD bản gốc, GPLX cũ (trường hợp đổi), Giấy chứng nhận sức khỏe còn hiệu lực, ảnh 3×4 cm (2 ảnh).
Bước 2: Nộp hồ sơ trực tiếp tại Sở GTVT tỉnh Thanh Hóa hoặc Trung tâm đào tạo/sát hạch lái xe được ủy quyền; hoặc qua Cổng DVC.
Bước 3: Cán bộ kiểm tra hồ sơ, tra cứu thông tin GPLX trên hệ thống quốc gia; cấp phiếu tiếp nhận. Thời hạn: 5 ngày làm việc.
Bước 4: Người lái xe nhận GPLX mới tại Sở GTVT hoặc qua dịch vụ bưu chính; nộp lại GPLX cũ (trường hợp đổi).""",
    conditions="""\
Đổi GPLX: GPLX cũ còn hiệu lực hoặc hết hạn không quá 3 tháng; sức khỏe đạt yêu cầu.
Cấp lại do mất: khai báo mất với cơ quan có thẩm quyền; không đang bị tước GPLX.
Không đang trong thời gian bị tước quyền sử dụng GPLX hoặc chấp hành hình phạt tù.""",
  ),
  dict(
    id='dang-ky-xe-moto',
    name='Đăng ký xe mô tô / xe máy lần đầu',
    code='TTHC-DKXE', category='transport', fee=150000, fee_note='Lệ phí đăng ký biển số: 150.000 – 500.000 đ tùy hạng xe',
    processing_days=3, processing_note='3 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='province', agency='Phòng Cảnh sát QLHC về TTXH — Công an tỉnh Thanh Hóa (PA08)',
    steps="""\
Bước 1: Chủ xe chuẩn bị hồ sơ: Giấy tờ chứng minh nguồn gốc xe (hóa đơn mua bán hoặc Giấy chứng nhận xuất xưởng), CCCD còn hiệu lực, Bảo hiểm trách nhiệm dân sự bắt buộc còn hiệu lực.
Bước 2: Đến Phòng CSQLHC — Công an tỉnh hoặc Công an cấp huyện được ủy quyền; nộp hồ sơ, nộp lệ phí đăng ký biển số và thuế trước bạ (2% giá trị xe).
Bước 3: Cán bộ kiểm tra xe thực tế (số khung, số máy khớp giấy tờ), xử lý hồ sơ, cấp biển số đăng ký. Thời hạn: 3 ngày làm việc.
Bước 4: Chủ xe nhận Giấy chứng nhận đăng ký xe và biển số; gắn biển số đúng quy định trước khi lưu hành.""",
    conditions="""\
Xe có nguồn gốc hợp pháp: mua mới tại đại lý hoặc nhập khẩu chính ngạch có đầy đủ hóa đơn, chứng từ.
Xe đã mua Bảo hiểm trách nhiệm dân sự bắt buộc còn hiệu lực.
Đã nộp thuế trước bạ theo quy định (2% giá trị xe đối với xe mô tô).""",
  ),
  # ── INSURANCE / Bảo hiểm – Lao động ─────────────────────────────────────
  dict(
    id='dang-ky-bhxh-bhyt',
    name='Đăng ký tham gia BHXH, BHYT lần đầu',
    code='TTHC-BHXH', category='insurance', fee=0, fee_note='Không có lệ phí đăng ký; đóng BHXH/BHYT theo tỷ lệ quy định',
    processing_days=5, processing_note='5 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='province', agency='Bảo hiểm xã hội tỉnh Thanh Hóa hoặc BHXH cấp huyện',
    steps="""\
Bước 1: Người lao động hoặc chủ sử dụng lao động chuẩn bị Tờ khai tham gia BHXH (Mẫu TK1-TS), danh sách lao động tham gia (Mẫu D02-LT nếu đơn vị), CCCD của từng người lao động.
Bước 2: Nộp hồ sơ trực tiếp tại BHXH cấp huyện hoặc tỉnh; hoặc qua Cổng DVCQG / Cổng BHXH điện tử (baohiemxahoi.gov.vn).
Bước 3: BHXH kiểm tra hồ sơ, cấp mã số BHXH cho người lao động chưa có; xác nhận tham gia. Thời hạn: 5 ngày làm việc.
Bước 4: Người lao động nhận Sổ BHXH và Thẻ BHYT; bắt đầu đóng BHXH từ tháng tiếp theo.""",
    conditions="""\
Người lao động làm việc theo hợp đồng lao động từ đủ 1 tháng trở lên bắt buộc tham gia BHXH/BHYT.
Người hoạt động không chuyên trách ở xã/phường và một số đối tượng khác tham gia theo quy định riêng.
Hộ gia đình, học sinh/sinh viên có thể đăng ký BHYT tự nguyện tại BHXH cấp huyện.""",
  ),
  dict(
    id='cap-so-bhxh-the-bhyt',
    name='Cấp / Đổi sổ BHXH và thẻ BHYT',
    code='TTHC-SOBHXH', category='insurance', fee=0, fee_note='Miễn phí cấp lần đầu; cấp lại do mất: 20.000 đ/sổ',
    processing_days=10, processing_note='10 ngày làm việc kể từ ngày nhận đủ hồ sơ',
    level='province', agency='Bảo hiểm xã hội tỉnh Thanh Hóa hoặc BHXH cấp huyện',
    steps="""\
Bước 1: Người tham gia BHXH chuẩn bị Tờ khai cấp/đổi sổ BHXH (Mẫu TK1-TS), CCCD còn hiệu lực; trường hợp đổi thẻ BHYT: thẻ cũ (nếu còn) và đơn yêu cầu.
Bước 2: Nộp hồ sơ tại BHXH cấp huyện nơi cư trú hoặc nơi làm việc; hoặc qua Cổng dịch vụ BHXH điện tử.
Bước 3: BHXH kiểm tra thông tin tham gia, tra cứu lịch sử đóng BHXH; cập nhật thông tin trên sổ BHXH điện tử và cấp Thẻ BHYT mới. Thời hạn: 10 ngày làm việc.
Bước 4: Người tham gia nhận Sổ BHXH (bản giấy hoặc điện tử trên ứng dụng VssID) và Thẻ BHYT mới tại BHXH hoặc qua bưu chính.""",
    conditions="""\
Đang tham gia BHXH bắt buộc hoặc tự nguyện; đóng đủ các tháng theo quy định.
Cấp lại sổ BHXH khi: sổ hỏng, mất; thay đổi họ tên, ngày sinh; tách/gộp sổ.
Đổi thẻ BHYT khi: thẻ hết hạn, hỏng, mất; thay đổi thông tin cá nhân hoặc nơi khám chữa bệnh ban đầu.""",
  ),
]

# ─────────────────────────────────────────────────────────────────────────────
# SERVICE REQUIREMENTS
# ─────────────────────────────────────────────────────────────────────────────
REQUIREMENTS = {
  'dang-ky-lai-khai-sinh': [
    ('Tờ khai đăng ký lại khai sinh (Mẫu HTT-2014-01.3)', 'Điền đầy đủ thông tin, ký tên', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực của người yêu cầu', True, 'original', 1),
    ('Giấy tờ chứng minh khai sinh trước đây', 'Tối thiểu 2 giấy tờ: sổ hộ khẩu cũ, học bạ, bảo hiểm, sổ quân đội...', True, 'copy', 2),
    ('Giấy chứng sinh (nếu còn)', 'Bản gốc hoặc bản sao có chứng thực', False, 'certified_copy', 3),
  ],
  'dang-ky-nhan-con': [
    ('Tờ khai đăng ký nhận cha/mẹ/con (Mẫu HTT-2014-05)', 'Điền đầy đủ thông tin, ký tên', True, 'original', 0),
    ('CCCD / Căn cước của người nhận và người được nhận', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Kết quả giám định ADN (nếu có)', 'Xuất trình kết quả từ cơ sở giám định được công nhận', False, 'original', 2),
    ('Văn bản đồng ý của người nuôi dưỡng (nếu trẻ em)', 'Trường hợp trẻ đang được người khác nuôi dưỡng', False, 'original', 3),
  ],
  'thay-doi-canh-chinh-ho-tich': [
    ('Tờ khai thay đổi/cải chính hộ tịch (Mẫu HTT-2014-07)', 'Điền đầy đủ, nêu rõ nội dung cần cải chính', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Trích lục hộ tịch cần cải chính', 'Bản gốc (khai sinh, kết hôn...)', True, 'original', 2),
    ('Giấy tờ chứng minh nội dung đúng', 'Học bạ, bảo hiểm, quân đội, y tế... có ghi thông tin đúng', True, 'certified_copy', 3),
  ],
  'cap-ban-sao-trich-luc-ho-tich': [
    ('Tờ khai yêu cầu cấp bản sao trích lục (Mẫu HTT-2014-09.1)', 'Ghi rõ loại trích lục và mục đích sử dụng', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực; xuất trình để đối chiếu', True, 'original', 1),
    ('Giấy ủy quyền có công chứng (nếu ủy quyền)', 'Xuất trình bản gốc kèm CCCD người được ủy quyền', False, 'original', 2),
  ],
  'dang-ky-tam-tru': [
    ('Tờ khai đăng ký tạm trú (Mẫu CT02)', 'Điền đầy đủ thông tin, ký tên', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Giấy tờ chứng minh chỗ ở hợp lệ', 'Hợp đồng thuê nhà, xác nhận chủ nhà hoặc sở hữu nhà ở', True, 'certified_copy', 2),
  ],
  'tach-ho-khau': [
    ('Tờ khai điều chỉnh thông tin cư trú (Mẫu CT01)', 'Điền đầy đủ thông tin tách hộ', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Giấy tờ chứng minh chỗ ở mới', 'Hợp đồng thuê/mua nhà hoặc giấy tờ sở hữu nhà đất', True, 'certified_copy', 2),
    ('Đồng ý của chủ hộ cũ (nếu tách từ hộ người khác)', 'Văn bản hoặc xác nhận tại UBND/Công an', False, 'original', 3),
  ],
  'cap-tai-khoan-dinh-danh': [
    ('CCCD / Căn cước công dân', 'Xuất trình bản gốc còn hiệu lực để quét QR / NFC', True, 'original', 0),
    ('Ứng dụng VNeID đã cài trên điện thoại', 'Điện thoại có camera rõ nét, kết nối internet ổn định', True, 'original', 1),
    ('Ảnh chân dung sinh trắc học', 'Chụp trực tiếp trong ứng dụng VNeID; khớp với ảnh trên CCCD', True, 'original', 2),
  ],
  'chuyen-nhuong-quyen-su-dung-dat': [
    ('GCN QSDĐ (Sổ đỏ/Sổ hồng)', 'Bản gốc còn hiệu lực của bên bán', True, 'original', 0),
    ('Hợp đồng chuyển nhượng QSDĐ có công chứng', 'Bản chính có chứng nhận của Văn phòng công chứng', True, 'original', 1),
    ('CCCD / Căn cước của hai bên (bên bán và bên mua)', 'Bản gốc còn hiệu lực; xuất trình để đối chiếu', True, 'original', 2),
    ('Tờ khai thuế TNCN và thuế trước bạ', 'Mẫu theo quy định của Chi cục Thuế', True, 'original', 3),
    ('Biên lai nộp thuế TNCN và lệ phí trước bạ', 'Sau khi hoàn thành nghĩa vụ tài chính', True, 'original', 4),
  ],
  'tach-thua-dat': [
    ('GCN QSDĐ (Sổ đỏ/Sổ hồng)', 'Bản gốc của thửa đất cần tách/hợp', True, 'original', 0),
    ('Đơn đề nghị tách thửa/hợp thửa (Mẫu 11/ĐĐ)', 'Điền đầy đủ, nêu rõ ranh giới tách', True, 'original', 1),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 2),
    ('Bản vẽ vị trí và kích thước thửa đất dự kiến', 'Do đơn vị đo đạc có tư cách pháp nhân lập', False, 'copy', 3),
  ],
  'dang-ky-bien-dong-dat-dai': [
    ('GCN QSDĐ (Sổ đỏ/Sổ hồng)', 'Bản gốc cần cập nhật biến động', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Giấy tờ làm căn cứ biến động', 'Hợp đồng thừa kế/tặng cho/thế chấp (có công chứng) hoặc bản án Tòa án', True, 'original', 2),
    ('Tờ khai lệ phí và nghĩa vụ tài chính (nếu có)', 'Theo loại biến động cụ thể', False, 'original', 3),
  ],
  'hoan-cong-cong-trinh': [
    ('Thông báo hoàn thành xây dựng công trình (theo mẫu)', 'Điền đầy đủ, ký bởi chủ đầu tư', True, 'original', 0),
    ('Giấy phép xây dựng gốc', 'Bản gốc kèm toàn bộ bản vẽ đã được phê duyệt', True, 'original', 1),
    ('Bản vẽ hoàn công (as-built)', 'Do đơn vị tư vấn có chứng chỉ hành nghề lập', True, 'copy', 2),
    ('Biên bản nghiệm thu từng phần (nếu có)', 'Móng, kết cấu, hoàn thiện...', False, 'copy', 3),
    ('Biên bản nghiệm thu PCCC (nếu bắt buộc)', 'Xuất trình biên bản đã được Cảnh sát PCCC ký', False, 'original', 4),
  ],
  'thay-doi-noi-dung-dkdn': [
    ('Thông báo thay đổi nội dung ĐKDN (theo loại thay đổi)', 'Mẫu theo quy định của Nghị định 01/2021/NĐ-CP', True, 'original', 0),
    ('GCN đăng ký doanh nghiệp bản gốc', 'Để cập nhật thông tin mới', True, 'original', 1),
    ('Quyết định/Biên bản họp HĐTV/ĐHCĐ', 'Thông qua nội dung thay đổi (nếu có)', False, 'certified_copy', 2),
    ('CCCD / Căn cước của người đại diện pháp luật mới', 'Trường hợp thay đổi người đại diện', False, 'original', 3),
  ],
  'giai-the-doanh-nghiep': [
    ('Thông báo giải thể doanh nghiệp', 'Theo Mẫu II-17 ban hành kèm Thông tư 01/2021/TT-BKHĐT', True, 'original', 0),
    ('Quyết định giải thể của HĐTV/ĐHCĐ/chủ sở hữu', 'Bản gốc có chữ ký của người có thẩm quyền', True, 'original', 1),
    ('GCN đăng ký doanh nghiệp bản gốc', 'Nộp lại cho cơ quan đăng ký khi hoàn tất', True, 'original', 2),
    ('Xác nhận hoàn thành nghĩa vụ thuế', 'Văn bản của Cơ quan thuế quản lý trực tiếp', True, 'original', 3),
    ('Xác nhận hoàn thành nghĩa vụ BHXH', 'Văn bản của BHXH cấp tỉnh/huyện', True, 'original', 4),
  ],
  'tam-ngung-kinh-doanh': [
    ('Thông báo tạm ngừng/tiếp tục kinh doanh (Mẫu II-19 hoặc II-20)', 'Ghi rõ thời gian tạm ngừng/tiếp tục dự kiến', True, 'original', 0),
    ('CCCD / Căn cước của người đại diện pháp luật', 'Bản gốc còn hiệu lực; xuất trình để đối chiếu', True, 'original', 1),
    ('GCN đăng ký doanh nghiệp (bản sao)', 'Để đối chiếu thông tin doanh nghiệp', False, 'copy', 2),
  ],
  'chung-thuc-ban-sao': [
    ('Bản chính giấy tờ cần chứng thực', 'Xuất trình bản chính để cán bộ đối chiếu', True, 'original', 0),
    ('Bản sao đã chụp/in', 'Bản sao rõ ràng, không bị nhòe, kích thước tương đương bản chính', True, 'copy', 1),
    ('CCCD / Căn cước công dân', 'Xuất trình để xác định danh tính người yêu cầu', True, 'original', 2),
  ],
  'cap-phieu-lltp-so2': [
    ('Văn bản đề nghị cấp Phiếu LLTP số 2', 'Có chữ ký, đóng dấu của cơ quan/tổ chức có thẩm quyền', True, 'original', 0),
    ('Tờ khai yêu cầu cấp Phiếu LLTP (theo mẫu)', 'Ghi đầy đủ thông tin người cần tra cứu', True, 'original', 1),
    ('Bản sao CCCD của người được tra cứu', 'Bản sao có chứng thực', True, 'certified_copy', 2),
    ('Chứng từ nộp lệ phí', '200.000 đ/phiếu theo quy định', True, 'original', 3),
  ],
  'doi-cap-lai-gplx': [
    ('Đơn đề nghị đổi/cấp lại GPLX (Mẫu 3 — TT 12/2017/TT-BGTVT)', 'Điền đầy đủ thông tin, ký tên', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('GPLX cũ (trường hợp đổi)', 'Nộp lại GPLX cũ khi nhận GPLX mới', False, 'original', 2),
    ('Giấy chứng nhận sức khỏe', 'Cấp trong vòng 6 tháng bởi cơ sở y tế được phép; còn hiệu lực', True, 'original', 3),
    ('Ảnh 3×4 cm (2 ảnh)', 'Chụp trong vòng 6 tháng, nền trắng, không đeo kính', True, 'original', 4),
  ],
  'dang-ky-xe-moto': [
    ('Giấy tờ chứng minh nguồn gốc xe', 'Hóa đơn mua bán tại đại lý hoặc Giấy chứng nhận xuất xưởng (bản gốc)', True, 'original', 0),
    ('CCCD / Căn cước công dân chủ xe', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Bảo hiểm trách nhiệm dân sự bắt buộc', 'Bản gốc còn hiệu lực tại thời điểm đăng ký', True, 'original', 2),
    ('Biên lai nộp thuế trước bạ', 'Nộp trước tại Chi cục Thuế (2% giá trị xe)', True, 'original', 3),
  ],
  'dang-ky-bhxh-bhyt': [
    ('Tờ khai tham gia BHXH/BHYT (Mẫu TK1-TS)', 'Điền đầy đủ thông tin cá nhân', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Hợp đồng lao động', 'Bản sao hợp đồng còn hiệu lực (đối với người lao động)', True, 'copy', 2),
    ('Danh sách lao động (Mẫu D02-LT)', 'Dành cho đơn vị sử dụng lao động đăng ký theo đợt', False, 'original', 3),
  ],
  'cap-so-bhxh-the-bhyt': [
    ('Tờ khai cấp/đổi sổ BHXH (Mẫu TK1-TS)', 'Điền đầy đủ thông tin, nêu lý do cấp/đổi', True, 'original', 0),
    ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực', True, 'original', 1),
    ('Sổ BHXH cũ / Thẻ BHYT cũ (nếu còn)', 'Nộp lại khi nhận sổ/thẻ mới; xuất trình nếu đổi do mất', False, 'original', 2),
    ('Hợp đồng lao động hiện tại (nếu đổi nơi KCB)', 'Bản sao để xác định đơn vị đang tham gia', False, 'copy', 3),
  ],
}

# ─────────────────────────────────────────────────────────────────────────────
# ICON MAP theo category
# ─────────────────────────────────────────────────────────────────────────────
ICONS = {
  'civil': '👤', 'land': '🏠', 'construction': '🏗️',
  'business': '🏢', 'transport': '🚗', 'justice': '⚖️',
  'insurance': '🛡️', 'tax': '💰', 'health': '⚕️',
}

with app.app_context():
    inserted_proc = 0
    inserted_req  = 0
    skipped = 0

    for p in PROCEDURES:
        try:
            result = db.session.execute(text("""
                INSERT INTO public.procedures
                    (id, name, code, category, fee, fee_note,
                     processing_days, processing_note, legal_basis,
                     implementing_level, agency, is_online, is_active,
                     steps, conditions)
                VALUES
                    (:id, :name, :code, :cat, :fee, :fee_note,
                     :pdays, :pnote, '[]'::jsonb,
                     :level, :agency, true, true,
                     :steps, :conditions)
                ON CONFLICT (id) DO NOTHING
            """), {
                'id': p['id'], 'name': p['name'], 'code': p['code'],
                'cat': p['category'], 'fee': p['fee'], 'fee_note': p['fee_note'],
                'pdays': p['processing_days'], 'pnote': p['processing_note'],
                'level': p['level'], 'agency': p['agency'],
                'steps': p['steps'], 'conditions': p['conditions'],
            })
            if result.rowcount:
                inserted_proc += 1
                print(f"  + PROC {p['id']}")
            else:
                skipped += 1
                print(f"  ~ skip {p['id']} (da ton tai)")
        except Exception as e:
            print(f"  ! ERR {p['id']}: {e}")
            db.session.rollback()
            continue

        # Insert requirements
        reqs = REQUIREMENTS.get(p['id'], [])
        for i, (doc_name, doc_desc, is_req, doc_type, order_idx) in enumerate(reqs):
            req_id = f"{p['id']}-req-{i:03d}"
            try:
                r2 = db.session.execute(text("""
                    INSERT INTO public.service_requirements
                        (id, service_id, doc_name, doc_description,
                         is_required, doc_type, order_index)
                    VALUES (:id, :sid, :name, :desc, :req, :dtype, :order)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    'id': req_id, 'sid': p['id'],
                    'name': doc_name, 'desc': doc_desc,
                    'req': is_req, 'dtype': doc_type, 'order': order_idx,
                })
                inserted_req += r2.rowcount
            except Exception as e:
                print(f"    ! REQ ERR {req_id}: {e}")
                db.session.rollback()

    db.session.commit()
    print(f"\nKet qua:")
    print(f"  Procedures: +{inserted_proc} moi, {skipped} da co")
    print(f"  Requirements: +{inserted_req} moi")
    print(f"  Tong procedures trong DB: {db.session.execute(text('SELECT COUNT(*) FROM public.procedures')).scalar()}")
