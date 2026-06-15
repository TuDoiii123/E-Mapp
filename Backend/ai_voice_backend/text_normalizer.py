"""
Chuẩn hóa văn bản tiếng Việt trước khi đưa vào TTS.

Mục tiêu: biến các ký hiệu/định dạng "máy" (ngày dd/mm/yyyy, giờ HH:MM,
số, bullet, viết tắt hành chính...) thành dạng *đọc thành tiếng* tự nhiên,
giúp giọng TTS nghe như người thật chứ không đánh vần ký tự.

Hàm chính:
    normalize(text) -> str        # chuẩn hóa thành text đọc được
    to_ssml(text)   -> str        # bọc <speak> + chèn <break> cho giọng SSML

Toàn bộ là hàm thuần, không phụ thuộc backend TTS → dễ test.
"""
import re
from typing import List

# ── Số → chữ tiếng Việt ─────────────────────────────────────────────────────

_DIGITS = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
_UNITS = ['', 'nghìn', 'triệu', 'tỷ']


def _read_three_digits(num: int, full: bool) -> str:
    """Đọc một nhóm 3 chữ số (0..999).

    full=True khi đây KHÔNG phải nhóm cao nhất → luôn đọc đủ 'không trăm',
    'linh' để nối các nhóm cho đúng (vd 1.005 = một nghìn không trăm linh năm).
    """
    hundreds, rem = divmod(num, 100)
    tens, units = divmod(rem, 10)
    words: List[str] = []

    if hundreds > 0 or full:
        words.append(f'{_DIGITS[hundreds]} trăm')

    if tens == 0:
        if units > 0 and (hundreds > 0 or full):
            words.append('linh')
        if units > 0:
            words.append(_DIGITS[units])
    elif tens == 1:
        words.append('mười')
        if units == 5:
            words.append('lăm')
        elif units > 0:
            words.append(_DIGITS[units])
    else:
        words.append(f'{_DIGITS[tens]} mươi')
        if units == 1:
            words.append('mốt')
        elif units == 4:
            words.append('tư')
        elif units == 5:
            words.append('lăm')
        elif units > 0:
            words.append(_DIGITS[units])

    return ' '.join(words)


def number_to_words(num: int) -> str:
    """Số nguyên → chữ tiếng Việt. Hỗ trợ tới hàng nghìn tỷ."""
    if num == 0:
        return 'không'
    if num < 0:
        return 'âm ' + number_to_words(-num)

    # Tách thành các nhóm 3 chữ số, từ thấp lên cao
    groups: List[int] = []
    n = num
    while n > 0:
        groups.append(n % 1000)
        n //= 1000

    parts: List[str] = []
    highest = len(groups) - 1
    for idx in range(highest, -1, -1):
        g = groups[idx]
        if g == 0 and idx != highest:
            # nhóm 0 ở giữa vẫn cần để giữ đơn vị tỷ/triệu đúng → bỏ qua đọc số
            # nhưng nếu là 'tỷ' lặp lại thì vẫn cần đơn vị; đơn giản: bỏ nhóm 0
            continue
        is_highest = idx == highest
        chunk = _read_three_digits(g, full=not is_highest)
        unit = _UNITS[idx] if idx < len(_UNITS) else _UNITS[-1] * 0 or _read_billion_unit(idx)
        parts.append(f'{chunk} {unit}'.strip())

    return ' '.join(p for p in parts if p).strip()


def _read_billion_unit(idx: int) -> str:
    """Đơn vị cho nhóm > tỷ (nghìn tỷ, triệu tỷ...). idx>=4."""
    extra = idx - 3  # số lần 'tỷ' phụ
    return ' '.join(['tỷ'] + [_UNITS[i] for i in range(1, extra + 1)])


# ── Ngày / giờ ──────────────────────────────────────────────────────────────

def _read_day(d: int) -> str:
    """Ngày trong tháng — mùng 1..10 đọc 'mùng', còn lại đọc số thường."""
    if 1 <= d <= 10:
        return f'mùng {number_to_words(d)}'
    return number_to_words(d)


def _date_repl(m: re.Match) -> str:
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= d <= 31 and 1 <= mo <= 12):
        return m.group(0)
    y_words = number_to_words(y) if y >= 100 else number_to_words(y)
    return f'ngày {_read_day(d)} tháng {number_to_words(mo)} năm {y_words}'


def _time_repl(m: re.Match) -> str:
    h, mi = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        return m.group(0)
    if mi == 0:
        return f'{number_to_words(h)} giờ'
    if mi == 30:
        return f'{number_to_words(h)} giờ rưỡi'
    return f'{number_to_words(h)} giờ {number_to_words(mi)} phút'


# ── Viết tắt hành chính phổ biến (dịch vụ công) ─────────────────────────────

_ABBREV = {
    'CCCD': 'căn cước công dân',
    'CMND': 'chứng minh nhân dân',
    'UBND': 'Ủy ban nhân dân',
    'TTHC': 'thủ tục hành chính',
    'DVC': 'dịch vụ công',
    'BHYT': 'bảo hiểm y tế',
    'BHXH': 'bảo hiểm xã hội',
    'GPLX': 'giấy phép lái xe',
    'KT3': 'tạm trú',
    'TP': 'thành phố',
    'Q.': 'quận ',
    'P.': 'phường ',
}

# Số thứ tự / ký hiệu thường gặp
_SYMBOLS = {
    '•': ',',
    '–': ',',
    '—': ',',
    '%': ' phần trăm',
    '&': ' và ',
    '+': ' cộng ',
}


# ── Pipeline chuẩn hóa ──────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Chuẩn hóa text tiếng Việt → dạng đọc thành tiếng tự nhiên."""
    if not text:
        return text

    s = text

    # 1. Viết tắt (word-boundary để tránh khớp nhầm trong từ khác)
    for abbr, full in _ABBREV.items():
        s = re.sub(rf'\b{re.escape(abbr)}', full, s)

    # 2. Ngày dd/mm/yyyy (hoặc d/m/yyyy)
    s = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', _date_repl, s)

    # 3. Giờ HH:MM (hoặc H:MM)
    s = re.sub(r'\b(\d{1,2}):(\d{2})\b', _time_repl, s)

    # 4. Ký hiệu
    for sym, repl in _SYMBOLS.items():
        s = s.replace(sym, repl)

    # 5. Số nguyên còn sót (vd "9 giờ", "có 5 hồ sơ") — bỏ dấu phân tách nghìn
    def _num_repl(m: re.Match) -> str:
        raw = m.group(0).replace('.', '').replace(',', '')
        try:
            return number_to_words(int(raw))
        except ValueError:
            return m.group(0)

    s = re.sub(r'\b\d{1,3}(?:[.,]\d{3})+\b|\b\d+\b', _num_repl, s)

    # 6. Dọn lặp do thay thế: "Ngày ngày" / "tháng tháng" / "giờ giờ"...
    s = re.sub(r'\b([Nn])gày:?\s+ngày\b', r'\1gày', s)
    s = re.sub(r'\b([Tt])háng:?\s+tháng\b', r'\1háng', s)
    s = re.sub(r'\b([Nn])ăm:?\s+năm\b', r'\1ăm', s)

    # 7. Dọn khoảng trắng / dấu câu thừa
    s = re.sub(r' *\n+ *', '. ', s)        # xuống dòng → câu mới (nghỉ tự nhiên)
    s = re.sub(r'\s+([,.!?])', r'\1', s)
    s = re.sub(r'(,\s*)+,', ',', s)
    s = re.sub(r'\.\s*,', '.', s)          # ". ," → "."
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'^[\s,.;:]+', '', s)       # bỏ dấu câu thừa đầu chuỗi
    return s.strip()


# ── SSML (cho giọng Neural2 / Wavenet) ──────────────────────────────────────

def _xml_escape(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def to_ssml(text: str, break_comma: str = '250ms', break_sentence: str = '450ms') -> str:
    """Bọc text (ĐÃ normalize) thành SSML, chèn ngắt nghỉ tự nhiên.

    Lưu ý: chỉ dùng cho giọng hỗ trợ SSML (Neural2, Wavenet). Chirp3-HD
    KHÔNG nhận SSML — dùng trực tiếp text từ normalize().
    """
    s = _xml_escape(text)
    s = s.replace(',', f',<break time="{break_comma}"/>')
    s = re.sub(r'([.!?])(\s|$)', rf'\1<break time="{break_sentence}"/>\2', s)
    return f'<speak>{s}</speak>'
