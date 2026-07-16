"""
Hậu xử lý kết quả OCR Gemini — sửa lỗi kiểu OCR bằng tri thức tiếng Việt.

1. Sửa địa danh: so từng đơn vị (Xã/Huyện/Tỉnh) với danh mục hành chính thật
   (data/place_lexicon.json) KHÔNG phân biệt dấu, thu hẹp phạm vi theo đơn vị
   cha đã khớp (tỉnh → huyện → xã). Chỉ thay khi khớp DUY NHẤT một địa danh
   thật lệch dấu: "Hoàng Đông" (trong Huyện Hoằng Hóa) → "Hoằng Đồng".
   Mơ hồ thì giữ nguyên — không bịa.

2. Kiểm chéo số CCCD (Thông tư 07/2016/TT-BCA): 3 số đầu = mã tỉnh (001–096),
   số thứ 4 = thế kỷ + giới tính (0/1 = nam/nữ 19xx, 2/3 = nam/nữ 20xx),
   số 5–6 = 2 số cuối năm sinh. Lệch với gender/dateOfBirth đã đọc →
   gắn cảnh báo (không tự sửa — không biết trường nào sai).

Kết quả trả kèm meta `_corrections` / `_warnings` để UI highlight.
"""
import json
import os
import re
import unicodedata

_LEXICON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'place_lexicon.json')

# Trường địa chỉ theo từng loại giấy tờ
PLACE_FIELDS = {
    'placeOfOrigin', 'placeOfResidence', 'address',
    'husbandAddress', 'wifeAddress', 'placeOfMarriage',
}

# prefix đơn vị → cấp ('ward' | 'district' | 'province'); thứ tự thử match
_UNIT_PREFIXES = [
    ('thị trấn',   ['ward']),
    ('thành phố',  ['province', 'district']),
    ('thị xã',     ['district']),
    ('phường',     ['ward']),
    ('quận',       ['district']),
    ('huyện',      ['district']),
    ('tỉnh',       ['province']),
    ('tp.',        ['province', 'district']),
    ('xã',         ['ward']),
]

_index = None  # lazy singleton


def strip_accents(s: str) -> str:
    """Bỏ dấu tiếng Việt + đ→d, thường hoá — làm khoá so khớp."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.replace('đ', 'd').replace('Đ', 'D').casefold().strip()


def _norm_space(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()


def _load_index():
    """Index: mỗi cấp {khoá_bỏ_dấu: [bản ghi]}, kèm map code→parent."""
    global _index
    if _index is not None:
        return _index
    with open(_LEXICON_PATH, encoding='utf-8') as f:
        lex = json.load(f)

    idx = {'ward': {}, 'district': {}, 'province': {},
           'district_province': {}, 'ward_district': {}}
    for p in lex['provinces']:
        idx['province'].setdefault(strip_accents(p['name']), []).append(p)
    for d in lex['districts']:
        idx['district'].setdefault(strip_accents(d['name']), []).append(d)
        idx['district_province'][d['code']] = d['province_code']
    for w in lex['wards']:
        idx['ward'].setdefault(strip_accents(w['name']), []).append(w)
        idx['ward_district'][w['code']] = w['district_code']
    _index = idx
    return idx


def _split_prefix(part: str):
    """'Huyện Hoằng Hóa' → (đầu_thừa, 'Huyện', 'Hoằng Hóa', [cấp]) — prefix có thể
    đứng giữa chuỗi (vd 'ỦY BAN NHÂN DÂN Xã Nga Thủy')."""
    low = part.casefold()
    best = None
    for prefix, levels in _UNIT_PREFIXES:
        pos = low.find(prefix + ' ')
        if pos != -1 and (pos == 0 or not low[pos - 1].isalnum()):
            if best is None or pos < best[0]:
                best = (pos, prefix, levels)
    if best is None:
        return '', '', part.strip(), ['province', 'district', 'ward']
    pos, prefix, levels = best
    head = part[:pos]
    raw_prefix = part[pos:pos + len(prefix)]
    name = part[pos + len(prefix):].strip()
    return head, raw_prefix, name, levels


def _match_unit(name: str, levels: list, scope: dict) -> tuple:
    """
    Tìm địa danh thật khớp `name` (bỏ dấu) trong các cấp cho phép,
    thu hẹp theo scope {'province': code, 'district': code} nếu có.
    Trả (tên_chuẩn | None, cấp, code) — None nếu không khớp hoặc mơ hồ.
    """
    idx = _load_index()
    key = strip_accents(_norm_space(name))
    if not key:
        return None, None, None

    candidates = []  # (level, record)
    for level in levels:
        for rec in idx[level].get(key, []):
            if level == 'district' and scope.get('province') and \
                    rec['province_code'] != scope['province']:
                continue
            if level == 'ward':
                if scope.get('district') and rec['district_code'] != scope['district']:
                    continue
                if not scope.get('district') and scope.get('province'):
                    prov = idx['district_province'].get(rec['district_code'])
                    if prov != scope['province']:
                        continue
            candidates.append((level, rec))

    if not candidates:
        return None, None, None, set()
    names = {c[1]['name'] for c in candidates}
    if len(names) != 1:
        return None, None, None, names  # mơ hồ — không sửa, trả gợi ý
    level, rec = candidates[0]
    return rec['name'], level, rec['code'], names


def correct_place(text: str) -> tuple:
    """
    Sửa dấu địa danh trong 1 chuỗi địa chỉ 'Xã A, Huyện B, Tỉnh C'.
    Duyệt phải→trái để đơn vị cha (tỉnh/huyện) thu hẹp phạm vi đơn vị con.
    Trả (chuỗi_mới, [{'from', 'to'}], [gợi_ý_khi_mơ_hồ]).
    """
    if not text or not isinstance(text, str):
        return text, [], []
    parts = [p for p in text.split(',')]
    scope = {}
    corrections = []
    suggestions = []
    out = [None] * len(parts)

    for i in range(len(parts) - 1, -1, -1):
        part = parts[i].strip()
        head, prefix, name, levels = _split_prefix(part)
        canonical, level, code, names = _match_unit(name, levels, scope)

        # Mơ hồ + tên đọc được không phải địa danh thật → cảnh báo kèm gợi ý
        if canonical is None and names and _norm_space(name) not in names:
            opts = ' / '.join(f'"{n}"' for n in sorted(names))
            suggestions.append(
                f'"{name}" không có trong danh mục địa danh — có thể là {opts}')

        if canonical is not None:
            if level == 'province':
                scope['province'] = code
            elif level == 'district':
                scope['district'] = code
                scope.setdefault('province',
                                 _load_index()['district_province'].get(code))
            if _norm_space(canonical) != _norm_space(name):
                corrections.append({'from': name, 'to': canonical})
                rebuilt = f'{head}{prefix} {canonical}' if prefix else f'{head}{canonical}'
                out[i] = rebuilt.strip()
                continue
        out[i] = part

    return ', '.join(out), corrections, suggestions


# ── Kiểm chéo cấu trúc số CCCD ────────────────────────────────────────────────

def validate_cccd_no(no: str, gender: str = None, date_of_birth: str = None) -> list:
    """Cảnh báo khi số CCCD lệch cấu trúc hoặc lệch giới tính / năm sinh đã đọc."""
    warnings = []
    digits = re.sub(r'\s', '', str(no or ''))
    if not re.fullmatch(r'\d{12}', digits):
        return warnings  # không phải CCCD 12 số (CMND 9 số cũ…) — bỏ qua

    province = int(digits[:3])
    if not (1 <= province <= 96):
        warnings.append(f'Mã tỉnh trong số CCCD ({digits[:3]}) không hợp lệ (001–096)')

    century_gender = int(digits[3])
    m = re.search(r'(\d{4})', str(date_of_birth or ''))
    birth_year = int(m.group(1)) if m else None

    if birth_year:
        expect_century = 0 if birth_year < 2000 else 2  # 0/1: 19xx, 2/3: 20xx
        if century_gender not in (expect_century, expect_century + 1):
            warnings.append(
                f'Số thứ 4 của CCCD ({century_gender}) không khớp thế kỷ '
                f'năm sinh {birth_year} — kiểm tra lại số CCCD hoặc ngày sinh')
        if int(digits[4:6]) != birth_year % 100:
            warnings.append(
                f'Hai số năm sinh trong CCCD ({digits[4:6]}) không khớp '
                f'năm sinh đã đọc ({birth_year}) — một trong hai bị đọc sai')

    g = strip_accents(str(gender or ''))
    if g in ('nam', 'nu'):
        # chẵn = nam, lẻ = nữ
        if (century_gender % 2 == 0) != (g == 'nam'):
            warnings.append(
                f'Số thứ 4 của CCCD ({century_gender}) không khớp giới tính '
                f'"{gender}" đã đọc — kiểm tra lại')
    return warnings


# ── API chính ─────────────────────────────────────────────────────────────────

def postcorrect_document(data: dict) -> dict:
    """
    Áp hậu xử lý lên kết quả trích xuất giấy tờ cá nhân.
    Trả về dict MỚI, kèm '_corrections' / '_warnings' khi có gì để nói.
    An toàn: lỗi bất kỳ → trả nguyên bản.
    """
    if not isinstance(data, dict):
        return data
    try:
        out = dict(data)
        corrections = []
        warnings = []
        for field in PLACE_FIELDS:
            if out.get(field):
                fixed, corr, sugg = correct_place(str(out[field]))
                if corr:
                    out[field] = fixed
                    corrections.extend({**c, 'field': field} for c in corr)
                warnings.extend(f'{field}: {s}' for s in sugg)

        warnings += validate_cccd_no(out.get('no'), out.get('gender'),
                                     out.get('dateOfBirth'))

        if corrections:
            out['_corrections'] = corrections
        if warnings:
            out['_warnings'] = warnings
        return out
    except Exception:
        return data
