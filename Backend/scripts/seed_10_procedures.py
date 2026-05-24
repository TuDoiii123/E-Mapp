# -*- coding: utf-8 -*-
"""
Seed 10 thủ tục hành chính phổ biến nhất với đầy đủ giấy tờ.
Dữ liệu chuẩn từ dichvucong.gov.vn và quy định pháp luật hiện hành.
Chạy: python scripts/seed_10_procedures.py
"""
import sys, os, io, logging
logging.disable(logging.CRITICAL)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FLASK_ENV'] = 'production'
from dotenv import load_dotenv; load_dotenv()
from flask import Flask
app = Flask(__name__)
u=os.getenv('DB_USER','postgres'); pw=os.getenv('DB_PASSWORD','')
h=os.getenv('DB_HOST','localhost'); pt=os.getenv('DB_PORT','5432'); dbn=os.getenv('DB_NAME','postgres')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{u}:{pw}@{h}:{pt}/{dbn}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from flask_sqlalchemy import SQLAlchemy; db = SQLAlchemy(app)

# ─── 10 thủ tục + giấy tờ đầy đủ ─────────────────────────────────────────────
PROCEDURES = [
    {
        'id': 'dang-ky-ket-hon',
        'name': 'Đăng ký kết hôn',
        'code': 'TTHC-1.000894',
        'category': 'civil',
        'icon': '💍',
        'fee': 0,
        'fee_note': 'Miễn lệ phí',
        'processing_days': 3,
        'processing_note': '3 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'agency': 'UBND cấp xã/phường/thị trấn nơi cư trú của một trong hai bên',
        'requirements': [
            ('Tờ khai đăng ký kết hôn (Mẫu TP/HT-2014-TKKH.1)', 'Hai bên nam nữ điền đầy đủ thông tin và cùng ký tên. Lấy mẫu tại UBND hoặc tải trên cổng DVC.', True, 'original'),
            ('CCCD / Căn cước công dân (hai bên)', 'Bản gốc còn hiệu lực của cả hai bên nam và nữ', True, 'original'),
            ('Giấy xác nhận tình trạng hôn nhân', 'Do UBND nơi đăng ký thường trú cấp, trong vòng 6 tháng', True, 'original'),
            ('Giấy khai sinh (hai bên)', 'Bản chính hoặc bản sao có chứng thực', True, 'certified_copy'),
            ('Ảnh 3×4 cm (mỗi người 2 ảnh)', 'Ảnh chụp trong 6 tháng gần nhất, nền trắng', True, 'original'),
            ('Giấy tờ chứng minh về ly hôn/góa (nếu đã từng kết hôn)', 'Bản án/quyết định ly hôn hoặc giấy chứng tử của vợ/chồng cũ', False, 'certified_copy'),
        ],
    },
    {
        'id': 'dang-ky-khai-sinh',
        'name': 'Đăng ký khai sinh',
        'code': 'TTHC-1.001193',
        'category': 'civil',
        'icon': '👶',
        'fee': 0,
        'fee_note': 'Miễn lệ phí',
        'processing_days': 3,
        'processing_note': '3 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'agency': 'UBND cấp xã/phường/thị trấn nơi cư trú của cha hoặc mẹ',
        'requirements': [
            ('Tờ khai đăng ký khai sinh (Mẫu TP/HT-2014-TKKH.1)', 'Điền đầy đủ thông tin theo hướng dẫn, ký tên', True, 'original'),
            ('Giấy chứng sinh', 'Do bệnh viện hoặc cơ sở y tế nơi trẻ sinh ra cấp', True, 'original'),
            ('CCCD / Căn cước công dân của cha hoặc mẹ', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy đăng ký kết hôn của cha mẹ', 'Bản chính (nếu cha mẹ đã đăng ký kết hôn)', False, 'original'),
            ('Sổ hộ khẩu hoặc giấy xác nhận cư trú', 'Bản gốc hoặc bản sao chứng thực', False, 'certified_copy'),
        ],
    },
    {
        'id': 'cap-doi-cccd',
        'name': 'Cấp mới / Đổi thẻ Căn cước công dân',
        'code': 'TTHC-2.001642',
        'category': 'civil',
        'icon': '🪪',
        'fee': 0,
        'fee_note': 'Miễn phí (cấp lần đầu). Cấp lại/đổi: theo quy định',
        'processing_days': 7,
        'processing_note': '7 ngày làm việc với cấp xã; 15 ngày với vùng xa',
        'agency': 'Cơ quan Công an cấp xã/huyện/tỉnh nơi đăng ký thường trú',
        'requirements': [
            ('Phiếu thu nhận thông tin căn cước', 'Điền theo mẫu tại cơ quan Công an', True, 'original'),
            ('CCCD hoặc CMND cũ (nếu đã có)', 'Nộp lại bản gốc khi đổi/cấp lại', False, 'original'),
            ('Sổ hộ khẩu hoặc giấy xác nhận thường trú', 'Bản gốc hoặc bản sao chứng thực', False, 'certified_copy'),
            ('Giấy khai sinh (đối với trẻ em dưới 14 tuổi)', 'Bản chính hoặc bản sao có chứng thực', False, 'certified_copy'),
        ],
    },
    {
        'id': 'dang-ky-thuong-tru',
        'name': 'Đăng ký thường trú',
        'code': 'TTHC-1.003018',
        'category': 'civil',
        'icon': '🏘️',
        'fee': 0,
        'fee_note': 'Miễn lệ phí',
        'processing_days': 7,
        'processing_note': '7 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'agency': 'Cơ quan Công an cấp xã/phường nơi đề nghị đăng ký thường trú',
        'requirements': [
            ('Phiếu báo thay đổi hộ khẩu, nhân khẩu (Mẫu HK02)', 'Điền đầy đủ thông tin và ký tên', True, 'original'),
            ('CCCD / Căn cước công dân', 'Bản gốc còn hiệu lực của người đề nghị', True, 'original'),
            ('Giấy tờ chứng minh chỗ ở hợp pháp', 'Sổ đỏ, hợp đồng thuê nhà công chứng, hoặc giấy cho phép ở nhờ', True, 'certified_copy'),
            ('Sổ hộ khẩu cũ (nếu có)', 'Nộp lại khi chuyển từ nơi khác đến', False, 'original'),
            ('Giấy tờ chứng minh quan hệ nhân thân', 'Nếu đăng ký cùng hộ gia đình (Giấy khai sinh, ĐKKH)', False, 'certified_copy'),
        ],
    },
    {
        'id': 'cap-giay-phep-xay-dung',
        'name': 'Cấp giấy phép xây dựng nhà ở riêng lẻ',
        'code': 'TTHC-1.003705',
        'category': 'construction',
        'icon': '🏗️',
        'fee': 75000,
        'fee_note': '75.000 đồng/lần cấp (theo NĐ 79/2014)',
        'processing_days': 15,
        'processing_note': '15 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'agency': 'Phòng Quản lý Đô thị / Ban Quản lý xây dựng cấp huyện',
        'requirements': [
            ('Đơn đề nghị cấp giấy phép xây dựng', 'Mẫu theo Phụ lục II, Nghị định 15/2021/NĐ-CP', True, 'original'),
            ('Giấy tờ về quyền sử dụng đất (Sổ đỏ/Sổ hồng)', 'Bản sao có chứng thực hoặc bản gốc đối chiếu', True, 'certified_copy'),
            ('Bản vẽ thiết kế xây dựng (3 bộ)', 'Mặt bằng, mặt đứng, mặt cắt; thang tỷ lệ 1/50 đến 1/200', True, 'original'),
            ('CCCD / Căn cước công dân chủ đầu tư', 'Bản gốc còn hiệu lực', True, 'original'),
            ('Giấy tờ chứng minh về phòng cháy chữa cháy (nếu diện tích > 300 m²)', 'Theo yêu cầu của cơ quan PCCC', False, 'original'),
            ('Biên bản thỏa thuận ranh giới với hàng xóm (nếu xây sát mốc)', 'Có chữ ký của các bên liên quan', False, 'original'),
        ],
    },
    {
        'id': 'cap-gcn-quyen-su-dung-dat',
        'name': 'Cấp Giấy chứng nhận quyền sử dụng đất (lần đầu)',
        'code': 'TTHC-1.003966',
        'category': 'land',
        'icon': '📜',
        'fee': 100000,
        'fee_note': 'Theo quy định từng địa phương (thường 50.000–500.000 đồng)',
        'processing_days': 30,
        'processing_note': '30 ngày làm việc kể từ ngày nhận đủ hồ sơ (vùng sâu: 40 ngày)',
        'agency': 'Văn phòng Đăng ký đất đai cấp huyện hoặc UBND cấp xã (ủy quyền)',
        'requirements': [
            ('Đơn đăng ký đất đai, tài sản gắn liền với đất (Mẫu 04a/ĐK)', 'Theo mẫu tại Thông tư 24/2014/TT-BTNMT', True, 'original'),
            ('Giấy tờ về quyền sử dụng đất (nếu có)', 'Các loại giấy tờ được quy định tại Điều 100 Luật Đất đai 2013', True, 'original'),
            ('CCCD / Căn cước công dân / Hộ chiếu', 'Bản sao có chứng thực', True, 'certified_copy'),
            ('Trích đo địa chính thửa đất', 'Do đơn vị đo đạc có chức năng thực hiện', True, 'original'),
            ('Chứng từ thực hiện nghĩa vụ tài chính về đất', 'Biên lai nộp thuế, lệ phí trước bạ (nếu có)', False, 'original'),
            ('Văn bản của cơ quan có thẩm quyền về giải quyết nguồn gốc đất', 'Đối với đất có tranh chấp hoặc lấn chiếm', False, 'original'),
        ],
    },
    {
        'id': 'dang-ky-ho-kinh-doanh',
        'name': 'Đăng ký thành lập hộ kinh doanh',
        'code': 'TTHC-1.001090',
        'category': 'business',
        'icon': '🏪',
        'fee': 100000,
        'fee_note': '100.000 đồng/lần đăng ký',
        'processing_days': 3,
        'processing_note': '3 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ',
        'agency': 'Phòng Tài chính – Kế hoạch cấp huyện nơi đặt địa điểm kinh doanh',
        'requirements': [
            ('Giấy đề nghị đăng ký hộ kinh doanh', 'Mẫu theo Phụ lục III-1, Nghị định 01/2021/NĐ-CP', True, 'original'),
            ('CCCD / Căn cước công dân / Hộ chiếu chủ hộ', 'Bản sao có chứng thực, còn hiệu lực', True, 'certified_copy'),
            ('Danh sách thành viên hộ gia đình tham gia kinh doanh', 'Nếu có nhiều thành viên cùng kinh doanh', False, 'original'),
            ('Văn bản ủy quyền (nếu chủ hộ ủy quyền cho người khác nộp)', 'Có công chứng/chứng thực', False, 'certified_copy'),
        ],
    },
    {
        'id': 'cap-gplx',
        'name': 'Cấp giấy phép lái xe (hạng B1, B2)',
        'code': 'TTHC-1.000703',
        'category': 'transport',
        'icon': '🚗',
        'fee': 135000,
        'fee_note': '135.000 đồng/lần cấp (theo TT 65/2020/TT-BTC)',
        'processing_days': 3,
        'processing_note': '3 ngày làm việc sau khi trúng tuyển kỳ thi sát hạch',
        'agency': 'Sở Giao thông Vận tải tỉnh/thành phố nơi học lái xe',
        'requirements': [
            ('Đơn đề nghị cấp giấy phép lái xe', 'Mẫu theo quy định của Tổng cục ĐBVN', True, 'original'),
            ('CCCD / Căn cước công dân / Hộ chiếu', 'Bản sao có chứng thực, còn hiệu lực', True, 'certified_copy'),
            ('Giấy chứng nhận sức khỏe', 'Do cơ sở y tế được phép cấp, trong vòng 6 tháng', True, 'original'),
            ('Ảnh 3×4 cm (2 ảnh)', 'Ảnh chụp trong 6 tháng, nền trắng, không đeo kính màu', True, 'original'),
            ('Chứng chỉ học lái xe / Giấy chứng nhận tốt nghiệp', 'Do cơ sở đào tạo lái xe cấp', True, 'original'),
        ],
    },
    {
        'id': 'cap-phieu-lltp',
        'name': 'Cấp phiếu lý lịch tư pháp (số 1)',
        'code': 'TTHC-1.001135',
        'category': 'justice',
        'icon': '📋',
        'fee': 200000,
        'fee_note': '200.000 đồng/phiếu (theo TT 241/2016/TT-BTC)',
        'processing_days': 10,
        'processing_note': '10 ngày làm việc (05 ngày với trường hợp cấp bách có căn cứ)',
        'agency': 'Sở Tư pháp nơi thường trú hoặc Trung tâm LLTP Quốc gia (Bộ Tư pháp)',
        'requirements': [
            ('Tờ khai yêu cầu cấp phiếu lý lịch tư pháp (Mẫu số 03/2013/TT-BTP)', 'Điền đầy đủ thông tin cá nhân, ký tên', True, 'original'),
            ('CCCD / Căn cước công dân / Hộ chiếu', 'Bản sao có chứng thực, còn hiệu lực', True, 'certified_copy'),
            ('Biên lai nộp lệ phí', 'Nộp tại ngân hàng hoặc trực tiếp tại cơ quan', True, 'original'),
            ('Giấy ủy quyền (nếu nộp qua người đại diện)', 'Có công chứng/chứng thực', False, 'certified_copy'),
        ],
    },
    {
        'id': 'dang-ky-khai-tu',
        'name': 'Đăng ký khai tử',
        'code': 'TTHC-1.004879',
        'category': 'civil',
        'icon': '📃',
        'fee': 0,
        'fee_note': 'Miễn lệ phí',
        'processing_days': 2,
        'processing_note': '2 ngày làm việc kể từ ngày nhận đủ hồ sơ',
        'agency': 'UBND cấp xã/phường/thị trấn nơi cư trú cuối cùng của người chết',
        'requirements': [
            ('Tờ khai đăng ký khai tử (Mẫu TP/HT-2014-TKKT)', 'Do người đi đăng ký điền và ký tên', True, 'original'),
            ('Giấy báo tử hoặc Giấy chứng tử', 'Do bệnh viện, công an hoặc cơ quan có thẩm quyền cấp', True, 'original'),
            ('CCCD / Căn cước công dân của người đi đăng ký', 'Bản gốc còn hiệu lực', True, 'original'),
            ('CCCD / Giấy tờ tùy thân của người đã mất (nếu có)', 'Nộp lại cho cơ quan đăng ký để hủy', False, 'original'),
            ('Sổ hộ khẩu (nếu còn sổ giấy)', 'Để xóa nhân khẩu', False, 'original'),
        ],
    },
]

with app.app_context():
    from sqlalchemy import text

    print("🚀 Seeding 10 thủ tục hành chính phổ biến...")
    p_ok = 0
    r_ok = 0

    for proc in PROCEDURES:
        proc_id = proc['id']
        try:
            db.session.execute(text("""
                INSERT INTO public.procedures
                    (id, name, code, category, fee, fee_note,
                     processing_days, processing_note, legal_basis,
                     implementing_level, agency, is_online, is_active,
                     created_at, updated_at)
                VALUES
                    (:id, :name, :code, :cat, :fee, :fee_note,
                     :days, :note, '[]'::jsonb,
                     '', :agency, true, true,
                     NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name            = EXCLUDED.name,
                    category        = EXCLUDED.category,
                    fee             = EXCLUDED.fee,
                    fee_note        = EXCLUDED.fee_note,
                    processing_days = EXCLUDED.processing_days,
                    processing_note = EXCLUDED.processing_note,
                    agency          = EXCLUDED.agency,
                    updated_at      = NOW()
            """), {
                'id': proc_id, 'name': proc['name'], 'code': proc['code'],
                'cat': proc['category'], 'fee': proc['fee'],
                'fee_note': proc['fee_note'], 'days': proc['processing_days'],
                'note': proc['processing_note'], 'agency': proc['agency'],
            })
            p_ok += 1
        except Exception as e:
            print(f"  ⚠ Procedure {proc_id}: {str(e)[:80]}")
            db.session.rollback()
            continue

        # Insert requirements
        for i, (name, desc, req, dtype) in enumerate(proc['requirements']):
            req_id = f"{proc_id}-req-{i:03d}"
            try:
                db.session.execute(text("""
                    INSERT INTO public.service_requirements
                        (id, service_id, doc_name, doc_description,
                         is_required, doc_type, order_index)
                    VALUES (:id, :sid, :name, :desc, :req, :dtype, :ord)
                    ON CONFLICT (id) DO UPDATE SET
                        doc_name        = EXCLUDED.doc_name,
                        doc_description = EXCLUDED.doc_description,
                        is_required     = EXCLUDED.is_required,
                        doc_type        = EXCLUDED.doc_type,
                        order_index     = EXCLUDED.order_index
                """), {
                    'id': req_id, 'sid': proc_id, 'name': name,
                    'desc': desc, 'req': req, 'dtype': dtype, 'ord': i,
                })
                r_ok += 1
            except Exception as e:
                print(f"    ⚠ Req {req_id}: {str(e)[:60]}")
                db.session.rollback()

    db.session.commit()

    # Verify
    total_procs = db.session.execute(text("SELECT COUNT(*) FROM public.procedures")).scalar()
    total_reqs  = db.session.execute(text(
        "SELECT COUNT(*) FROM public.service_requirements WHERE service_id IS NOT NULL"
    )).scalar()

    print(f"\n{'='*55}")
    print(f"✅ HOÀN THÀNH:")
    print(f"   Procedures seeded:           {p_ok}/10")
    print(f"   Service requirements seeded: {r_ok}")
    print(f"   DB total procedures:         {total_procs}")
    print(f"   DB total requirements:       {total_reqs}")
    print(f"{'='*55}")

    print("\n📋 Danh sách thủ tục đã seed:")
    rows = db.session.execute(text(
        "SELECT id, name, category, processing_days, fee FROM public.procedures ORDER BY name"
    )).fetchall()
    for r in rows:
        print(f"  [{r[2]}] {r[1]} | {r[3]} ngày | {r[4]:,} đ")
