"""
Sinh dataset synthetic cho bộ đánh giá Gemini OCR.

Render ảnh giả lập CCCD / GPLX / Giấy kết hôn / Biểu mẫu trống bằng Pillow,
với dữ liệu ngẫu nhiên tiếng Việt — vì mình sinh ra dữ liệu nên nhãn (ground
truth) được ghi tự động 100%, không cần gán tay.

Mỗi ảnh có 1 biến thể chất lượng: clean / blur / tilt / dark — để đo độ chính
xác của Gemini theo điều kiện ảnh.

Usage:
    python generate_dataset.py --count 1000 --seed 42
    python generate_dataset.py --count 20            # thử nhanh
"""
import argparse
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows mặc định cp1252

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(HERE, 'dataset')

# Tỷ lệ loại giấy tờ và biến thể ảnh
DOC_WEIGHTS = [('cccd', 0.40), ('gplx', 0.25), ('marriage', 0.25), ('form', 0.10)]
VARIANT_WEIGHTS = [('clean', 0.60), ('blur', 0.15), ('tilt', 0.15), ('dark', 0.10)]


# ── Font helpers ──────────────────────────────────────────────────────────────

_FONT_REGULAR = ['arial.ttf', 'segoeui.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
_FONT_BOLD    = ['arialbd.ttf', 'segoeuib.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for name in (_FONT_BOLD if bold else _FONT_REGULAR):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise OSError('Không tìm thấy font hỗ trợ tiếng Việt (arial/segoeui/DejaVuSans)')


# ── Dữ liệu ngẫu nhiên tiếng Việt ────────────────────────────────────────────

HO = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ',
      'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Trịnh']
DEM_NAM = ['Văn', 'Hữu', 'Đức', 'Minh', 'Quang', 'Xuân', 'Ngọc', 'Đình', 'Công']
DEM_NU  = ['Thị', 'Ngọc', 'Thu', 'Thanh', 'Kim', 'Hồng', 'Phương', 'Mỹ']
TEN_NAM = ['An', 'Bình', 'Cường', 'Dũng', 'Hải', 'Hùng', 'Khánh', 'Long', 'Nam',
           'Phong', 'Quân', 'Sơn', 'Tuấn', 'Việt', 'Thắng', 'Trung', 'Kiên', 'Đạt']
TEN_NU  = ['Anh', 'Chi', 'Dung', 'Hà', 'Hạnh', 'Hoa', 'Hương', 'Lan', 'Linh',
           'Mai', 'Ngân', 'Nhung', 'Phương', 'Thảo', 'Trang', 'Yến', 'Quỳnh', 'Diệp']

DIA_CHI = [
    ('Xã Hoằng Đồng', 'Huyện Hoằng Hóa', 'Tỉnh Thanh Hóa'),
    ('Phường Đông Vệ', 'Thành phố Thanh Hóa', 'Tỉnh Thanh Hóa'),
    ('Xã Quảng Ngọc', 'Huyện Quảng Xương', 'Tỉnh Thanh Hóa'),
    ('Phường Ba Đình', 'Thị xã Bỉm Sơn', 'Tỉnh Thanh Hóa'),
    ('Xã Nga Thủy', 'Huyện Nga Sơn', 'Tỉnh Thanh Hóa'),
    ('Xã Thọ Xương', 'Huyện Thọ Xuân', 'Tỉnh Thanh Hóa'),
    ('Phường Trường Thi', 'Thành phố Thanh Hóa', 'Tỉnh Thanh Hóa'),
    ('Xã Vĩnh Long', 'Huyện Vĩnh Lộc', 'Tỉnh Thanh Hóa'),
    ('Phường Dịch Vọng', 'Quận Cầu Giấy', 'TP. Hà Nội'),
    ('Xã Đông Sơn', 'Huyện Đông Sơn', 'Tỉnh Thanh Hóa'),
    ('Phường Lam Sơn', 'Thành phố Thanh Hóa', 'Tỉnh Thanh Hóa'),
    ('Xã Cẩm Tú', 'Huyện Cẩm Thủy', 'Tỉnh Thanh Hóa'),
    ('Xã Hà Lĩnh', 'Huyện Hà Trung', 'Tỉnh Thanh Hóa'),
    ('Phường Điện Biên', 'Quận Ba Đình', 'TP. Hà Nội'),
    ('Xã Yên Thọ', 'Huyện Yên Định', 'Tỉnh Thanh Hóa'),
]

DAN_TOC = ['Kinh', 'Kinh', 'Kinh', 'Kinh', 'Mường', 'Thái', 'Tày']
GPLX_CLASS = ['A1', 'A', 'B1', 'B', 'C1']


def _rand_name(rng: random.Random, gender: str) -> str:
    if gender == 'Nam':
        return f"{rng.choice(HO)} {rng.choice(DEM_NAM)} {rng.choice(TEN_NAM)}"
    return f"{rng.choice(HO)} {rng.choice(DEM_NU)} {rng.choice(TEN_NU)}"


def _rand_date(rng: random.Random, y1: int, y2: int) -> str:
    y = rng.randint(y1, y2)
    m = rng.randint(1, 12)
    d = rng.randint(1, 28)
    return f'{d:02d}/{m:02d}/{y}'


def _rand_address(rng: random.Random) -> str:
    xa, huyen, tinh = rng.choice(DIA_CHI)
    return f'{xa}, {huyen}, {tinh}'


def _rand_cccd_no(rng: random.Random) -> str:
    return ''.join(str(rng.randint(0, 9)) for _ in range(12))


# ── Vẽ chung ──────────────────────────────────────────────────────────────────

RED = (170, 20, 20)
BLACK = (25, 25, 30)


def _quoc_hieu(draw: ImageDraw.ImageDraw, cx: int, y: int, size: int = 22) -> int:
    """Vẽ quốc hiệu, trả về y tiếp theo."""
    draw.text((cx, y), 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM',
              font=_font(size, bold=True), fill=BLACK, anchor='mm')
    y += size + 8
    draw.text((cx, y), 'Độc lập - Tự do - Hạnh phúc',
              font=_font(size - 2), fill=BLACK, anchor='mm')
    return y + size + 6


def _wrap(text: str, width: int) -> list:
    """Ngắt dòng đơn giản theo số ký tự, ưu tiên ngắt tại dấu phẩy."""
    if len(text) <= width:
        return [text]
    cut = text.rfind(',', 0, width)
    if cut == -1:
        cut = text.rfind(' ', 0, width)
    if cut == -1:
        cut = width
    return [text[:cut + 1].strip(), text[cut + 1:].strip()]


# ── Render từng loại giấy tờ ─────────────────────────────────────────────────

def render_cccd(rng: random.Random) -> tuple:
    gender = rng.choice(['Nam', 'Nữ'])
    data = {
        'type': 'Căn cước công dân',
        'no': _rand_cccd_no(rng),
        'fullName': _rand_name(rng, gender).upper(),
        'dateOfBirth': _rand_date(rng, 1955, 2006),
        'gender': gender,
        'nationality': 'Việt Nam',
        'placeOfOrigin': _rand_address(rng),
        'placeOfResidence': _rand_address(rng),
    }

    img = Image.new('RGB', (900, 570), (206, 227, 208))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 891, 561], outline=(90, 130, 95), width=3)

    y = _quoc_hieu(d, 450, 40, 22)
    d.text((450, y + 22), 'CĂN CƯỚC CÔNG DÂN', font=_font(34, bold=True), fill=RED, anchor='mm')
    d.text((450, y + 52), 'Citizen Identity Card', font=_font(18), fill=BLACK, anchor='mm')

    # Ảnh chân dung giả
    d.rectangle([45, 190, 255, 470], fill=(178, 190, 181), outline=(120, 120, 120), width=2)
    d.ellipse([105, 240, 195, 330], fill=(210, 218, 211))
    d.pieslice([85, 330, 215, 470], 180, 360, fill=(210, 218, 211))

    x, y = 285, 185
    lh = 34

    def field(label, value, value_fill=BLACK, value_bold=True):
        nonlocal y
        d.text((x, y), label, font=_font(17), fill=(70, 70, 75))
        w = d.textlength(label + ' ', font=_font(17))
        d.text((x + w, y - 2), value, font=_font(20, bold=value_bold), fill=value_fill)
        y += lh

    field('Số / No.:', data['no'], value_fill=RED)
    d.text((x, y), 'Họ và tên / Full name:', font=_font(17), fill=(70, 70, 75))
    y += 26
    d.text((x, y), data['fullName'], font=_font(22, bold=True), fill=BLACK)
    y += lh + 2
    field('Ngày sinh / Date of birth:', data['dateOfBirth'])
    field('Giới tính / Sex:', data['gender'] + '        Quốc tịch / Nationality: ' + data['nationality'])
    d.text((x, y), 'Quê quán / Place of origin:', font=_font(17), fill=(70, 70, 75))
    y += 24
    for line in _wrap(data['placeOfOrigin'], 46):
        d.text((x, y), line, font=_font(19, bold=True), fill=BLACK)
        y += 26
    d.text((x, y), 'Nơi thường trú / Place of residence:', font=_font(17), fill=(70, 70, 75))
    y += 24
    for line in _wrap(data['placeOfResidence'], 46):
        d.text((x, y), line, font=_font(19, bold=True), fill=BLACK)
        y += 26

    return img, data


def render_gplx(rng: random.Random) -> tuple:
    gender = rng.choice(['Nam', 'Nữ'])
    data = {
        'type': 'Giấy phép lái xe',
        'no': _rand_cccd_no(rng),
        'fullName': _rand_name(rng, gender).upper(),
        'dateOfBirth': _rand_date(rng, 1955, 2004),
        'nationality': 'Việt Nam',
        'address': _rand_address(rng),
        'class': rng.choice(GPLX_CLASS),
    }

    img = Image.new('RGB', (900, 570), (245, 227, 183))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 891, 561], outline=(160, 130, 60), width=3)

    y = _quoc_hieu(d, 450, 38, 20)
    d.text((450, y + 20), 'GIẤY PHÉP LÁI XE', font=_font(32, bold=True), fill=RED, anchor='mm')
    d.text((450, y + 48), "DRIVER'S LICENCE", font=_font(18), fill=BLACK, anchor='mm')

    d.rectangle([45, 185, 245, 445], fill=(200, 200, 195), outline=(120, 120, 120), width=2)
    d.ellipse([100, 230, 190, 320], fill=(222, 222, 216))
    d.pieslice([80, 320, 210, 445], 180, 360, fill=(222, 222, 216))

    x, y = 280, 180
    lh = 40

    def field(label, value, value_fill=BLACK):
        nonlocal y
        d.text((x, y), label, font=_font(17), fill=(70, 70, 75))
        w = d.textlength(label + ' ', font=_font(17))
        d.text((x + w, y - 2), value, font=_font(20, bold=True), fill=value_fill)
        y += lh

    field('Số / No.:', data['no'], value_fill=RED)
    field('Họ tên / Full name:', data['fullName'])
    field('Ngày sinh / Date of birth:', data['dateOfBirth'])
    field('Quốc tịch / Nationality:', data['nationality'])
    d.text((x, y), 'Nơi cư trú / Address:', font=_font(17), fill=(70, 70, 75))
    y += 24
    for line in _wrap(data['address'], 46):
        d.text((x, y), line, font=_font(19, bold=True), fill=BLACK)
        y += 26
    y += 8
    d.text((x, y), 'Hạng / Class:', font=_font(17), fill=(70, 70, 75))
    d.text((x + 130, y - 10), data['class'], font=_font(34, bold=True), fill=RED)

    return img, data


def render_marriage(rng: random.Random) -> tuple:
    xa, huyen, tinh = rng.choice(DIA_CHI)
    dm, dy = rng.randint(1, 28), rng.randint(2005, 2025)
    dmo = rng.randint(1, 12)
    data = {
        'type': 'Giấy chứng nhận kết hôn',
        'husbandName': _rand_name(rng, 'Nam').upper(),
        'husbandNation': rng.choice(DAN_TOC),
        'husbandNationality': 'Việt Nam',
        'husbandDateOfBirth': _rand_date(rng, 1960, 2000),
        'husbandAddress': _rand_address(rng),
        'husbandIDNo': _rand_cccd_no(rng),
        'wifeName': _rand_name(rng, 'Nữ').upper(),
        'wifeDateOfBirth': _rand_date(rng, 1962, 2002),
        'wifeNation': rng.choice(DAN_TOC),
        'wifeNationality': 'Việt Nam',
        'wifeAddress': _rand_address(rng),
        'wifeIDNo': _rand_cccd_no(rng),
        'dateOfMarriage': f'{dm:02d}/{dmo:02d}/{dy}',
        'placeOfMarriage': f'{xa}, {huyen}, {tinh}',
    }

    img = Image.new('RGB', (850, 1100), (250, 233, 233))
    d = ImageDraw.Draw(img)
    d.rectangle([12, 12, 837, 1087], outline=(180, 80, 80), width=4)

    y = _quoc_hieu(d, 425, 55, 22)
    d.text((425, y + 30), 'GIẤY CHỨNG NHẬN KẾT HÔN', font=_font(32, bold=True), fill=RED, anchor='mm')
    y += 80

    def col(x0, title, name, dob, nation, natl, addr, idno):
        yy = y
        d.text((x0, yy), title, font=_font(20, bold=True), fill=RED)
        yy += 36
        rows = [
            ('Họ và tên:', name),
            ('Ngày sinh:', dob),
            ('Dân tộc:', nation),
            ('Quốc tịch:', natl),
            ('Nơi thường trú:', None),
            ('Số CCCD:', idno),
        ]
        for label, value in rows:
            d.text((x0, yy), label, font=_font(16), fill=(70, 70, 75))
            if value is not None:
                d.text((x0, yy + 22), value, font=_font(18, bold=True), fill=BLACK)
                yy += 54
            else:
                yy += 22
                for line in _wrap(addr, 34):
                    d.text((x0, yy), line, font=_font(17, bold=True), fill=BLACK)
                    yy += 24
                yy += 8
        return yy

    y1 = col(55, 'NGƯỜI CHỒNG', data['husbandName'], data['husbandDateOfBirth'],
             data['husbandNation'], data['husbandNationality'],
             data['husbandAddress'], data['husbandIDNo'])
    y2 = col(445, 'NGƯỜI VỢ', data['wifeName'], data['wifeDateOfBirth'],
             data['wifeNation'], data['wifeNationality'],
             data['wifeAddress'], data['wifeIDNo'])

    y = max(y1, y2) + 30
    dd, mm, yyyy = data['dateOfMarriage'].split('/')
    d.text((425, y), f'Đăng ký ngày {dd} tháng {mm} năm {yyyy}',
           font=_font(20, bold=True), fill=BLACK, anchor='mm')
    y += 34
    d.text((425, y), f'Tại: ỦY BAN NHÂN DÂN {xa}, {huyen}, {tinh}',
           font=_font(17), fill=BLACK, anchor='mm')
    y += 60
    d.text((620, y), 'NGƯỜI KÝ GIẤY CHỨNG NHẬN', font=_font(15, bold=True), fill=BLACK, anchor='mm')

    return img, data


# ── Biểu mẫu trống ────────────────────────────────────────────────────────────

FORM_DEFS = [
    {
        'formCode': 'Mẫu CT01',
        'formName': 'TỜ KHAI THAY ĐỔI THÔNG TIN CƯ TRÚ',
        'fields': ['Họ, chữ đệm và tên', 'Ngày, tháng, năm sinh', 'Giới tính',
                   'Số định danh cá nhân', 'Số điện thoại liên hệ', 'Nơi thường trú',
                   'Nơi ở hiện tại', 'Nội dung đề nghị', 'Chữ ký người kê khai'],
    },
    {
        'formCode': 'Mẫu CC01',
        'formName': 'PHIẾU THU NHẬN THÔNG TIN CĂN CƯỚC',
        'fields': ['Họ, chữ đệm và tên', 'Ngày, tháng, năm sinh', 'Giới tính',
                   'Số định danh cá nhân', 'Dân tộc', 'Tôn giáo', 'Quê quán',
                   'Nơi thường trú', 'Nghề nghiệp', 'Chữ ký người khai'],
    },
    {
        'formCode': 'Mẫu số 01',
        'formName': 'TỜ KHAI ĐĂNG KÝ KẾT HÔN',
        'fields': ['Họ, chữ đệm, tên bên nam', 'Ngày, tháng, năm sinh bên nam',
                   'Số CCCD bên nam', 'Nơi cư trú bên nam',
                   'Họ, chữ đệm, tên bên nữ', 'Ngày, tháng, năm sinh bên nữ',
                   'Số CCCD bên nữ', 'Nơi cư trú bên nữ', 'Chữ ký hai bên'],
    },
    {
        'formCode': 'Mẫu số 02',
        'formName': 'TỜ KHAI ĐĂNG KÝ KHAI SINH',
        'fields': ['Họ, chữ đệm, tên người khai', 'Quan hệ với người được khai sinh',
                   'Họ, chữ đệm, tên trẻ em', 'Ngày, tháng, năm sinh của trẻ',
                   'Nơi sinh', 'Giới tính', 'Dân tộc', 'Quốc tịch',
                   'Họ tên cha', 'Họ tên mẹ', 'Chữ ký người khai'],
    },
    {
        'formCode': 'Mẫu TK01',
        'formName': 'TỜ KHAI ĐỀ NGHỊ CẤP HỘ CHIẾU PHỔ THÔNG',
        'fields': ['Họ, chữ đệm và tên', 'Ngày, tháng, năm sinh', 'Giới tính',
                   'Số CCCD', 'Ngày cấp CCCD', 'Nơi sinh', 'Nơi thường trú',
                   'Số điện thoại', 'Nội dung đề nghị', 'Chữ ký người đề nghị'],
    },
    {
        'formCode': 'Mẫu ĐK04',
        'formName': 'ĐƠN ĐỀ NGHỊ XÁC NHẬN THÔNG TIN VỀ CƯ TRÚ',
        'fields': ['Kính gửi', 'Họ, chữ đệm và tên', 'Ngày, tháng, năm sinh',
                   'Số định danh cá nhân', 'Nơi thường trú', 'Nơi ở hiện tại',
                   'Thông tin đề nghị xác nhận', 'Lý do', 'Chữ ký người đề nghị'],
    },
]


def render_form(rng: random.Random) -> tuple:
    form = rng.choice(FORM_DEFS)
    data = {
        'type': 'form_template',
        'formName': form['formName'],
        'formCode': form['formCode'],
        'fields': list(form['fields']),
    }

    img = Image.new('RGB', (850, 1100), (252, 252, 250))
    d = ImageDraw.Draw(img)

    d.text((70, 40), form['formCode'], font=_font(16, bold=True), fill=BLACK)
    y = _quoc_hieu(d, 425, 55, 20)
    y += 30
    for line in _wrap(form['formName'], 44):
        d.text((425, y), line, font=_font(26, bold=True), fill=BLACK, anchor='mm')
        y += 34
    y += 24

    x = 70
    for label in form['fields']:
        if 'Chữ ký' in label:
            continue  # vẽ ở khối chữ ký cuối trang
        d.text((x, y), f'{label}:', font=_font(18), fill=BLACK)
        w = d.textlength(f'{label}: ', font=_font(18))
        dots_w = 850 - 70 - x - w
        n_dots = max(4, int(dots_w / d.textlength('.', font=_font(18))))
        d.text((x + w, y + 2), '.' * n_dots, font=_font(18), fill=(120, 120, 120))
        y += 46
        if 'Giới tính' in label:
            # checkbox Nam / Nữ
            d.rectangle([x + 20, y - 8, x + 36, y + 8], outline=BLACK, width=2)
            d.text((x + 44, y - 10), 'Nam', font=_font(17), fill=BLACK)
            d.rectangle([x + 120, y - 8, x + 136, y + 8], outline=BLACK, width=2)
            d.text((x + 144, y - 10), 'Nữ', font=_font(17), fill=BLACK)
            y += 40

    sig = [f for f in form['fields'] if 'Chữ ký' in f]
    if sig:
        y = max(y + 30, 950)
        d.text((620, y), '..., ngày ... tháng ... năm ...', font=_font(15), fill=BLACK, anchor='mm')
        d.text((620, y + 28), sig[0].upper(), font=_font(16, bold=True), fill=BLACK, anchor='mm')
        d.text((620, y + 52), '(Ký, ghi rõ họ tên)', font=_font(14), fill=(90, 90, 90), anchor='mm')

    return img, data


# ── Biến thể chất lượng ảnh ───────────────────────────────────────────────────

def apply_variant(img: Image.Image, variant: str, rng: random.Random) -> Image.Image:
    if variant == 'blur':
        return img.filter(ImageFilter.GaussianBlur(rng.uniform(1.8, 2.8)))
    if variant == 'tilt':
        angle = rng.choice([-1, 1]) * rng.uniform(5, 8)
        return img.rotate(angle, expand=True, fillcolor=(245, 245, 245),
                          resample=Image.BICUBIC)
    if variant == 'dark':
        return ImageEnhance.Brightness(img).enhance(rng.uniform(0.42, 0.58))
    return img


# ── Main ──────────────────────────────────────────────────────────────────────

RENDERERS = {
    'cccd': render_cccd,
    'gplx': render_gplx,
    'marriage': render_marriage,
    'form': render_form,
}


def _weighted_plan(count: int, weights: list, rng: random.Random) -> list:
    """Chia count theo trọng số, phần dư phân ngẫu nhiên."""
    plan = []
    for key, w in weights:
        plan.extend([key] * int(count * w))
    while len(plan) < count:
        plan.append(rng.choices([k for k, _ in weights], [w for _, w in weights])[0])
    rng.shuffle(plan)
    return plan[:count]


def main():
    ap = argparse.ArgumentParser(description='Sinh dataset synthetic cho eval OCR')
    ap.add_argument('--count', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out', default=DATASET_DIR)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    images_dir = os.path.join(args.out, 'images')
    labels_dir = os.path.join(args.out, 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    doc_plan = _weighted_plan(args.count, DOC_WEIGHTS, rng)
    variant_plan = _weighted_plan(args.count, VARIANT_WEIGHTS, rng)

    counters = {}
    for doc_type, variant in zip(doc_plan, variant_plan):
        idx = counters.get(doc_type, 0)
        counters[doc_type] = idx + 1
        stem = f'{doc_type}_{idx:04d}_{variant}'

        img, expected = RENDERERS[doc_type](rng)
        img = apply_variant(img, variant, rng)
        img.save(os.path.join(images_dir, f'{stem}.png'))

        label = {
            'image': f'{stem}.png',
            'docType': doc_type,
            'variant': variant,
            'source': 'synthetic',
            'expected': expected,
        }
        with open(os.path.join(labels_dir, f'{stem}.json'), 'w', encoding='utf-8') as f:
            json.dump(label, f, ensure_ascii=False, indent=2)

        total = sum(counters.values())
        if total % 100 == 0:
            print(f'  ... {total}/{args.count}')

    print(f'Đã sinh {sum(counters.values())} ảnh vào {images_dir}')
    for k, v in sorted(counters.items()):
        print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
