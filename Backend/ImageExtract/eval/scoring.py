"""
Logic chấm điểm cho bộ đánh giá Gemini OCR.

- Giấy tờ cá nhân (cccd/gplx/marriage): so từng trường sau chuẩn hoá
  (khoảng trắng, hoa thường, định dạng ngày) → match đúng/sai + CER.
- Biểu mẫu trống (form): so danh sách trường bằng fuzzy match
  → precision/recall/F1, cộng đúng/sai formName + formCode.
"""
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

# Các trường là ngày tháng → chuẩn hoá về dd/mm/yyyy trước khi so
DATE_FIELDS = {
    'dateOfBirth', 'husbandDateOfBirth', 'wifeDateOfBirth', 'dateOfMarriage',
}

# Khóa schema chuẩn theo prompt của từng loại giấy tờ
DOC_KEYS = {
    'cccd': ['type', 'no', 'fullName', 'dateOfBirth', 'gender', 'nationality',
             'placeOfOrigin', 'placeOfResidence'],
    'gplx': ['type', 'no', 'fullName', 'dateOfBirth', 'nationality', 'address', 'class'],
    'marriage': ['type', 'husbandName', 'husbandNation', 'husbandNationality',
                 'husbandDateOfBirth', 'husbandAddress', 'husbandIDNo',
                 'wifeName', 'wifeDateOfBirth', 'wifeNation', 'wifeNationality',
                 'wifeAddress', 'wifeIDNo', 'dateOfMarriage', 'placeOfMarriage'],
}

# Trường định danh: sai là hồ sơ nộp lên bị trả lại — dùng để đo mức ảnh hưởng
CRITICAL_FIELDS = {
    'cccd': {'no', 'fullName', 'dateOfBirth'},
    'gplx': {'no', 'fullName', 'dateOfBirth', 'class'},
    'marriage': {'husbandName', 'wifeName', 'husbandIDNo', 'wifeIDNo', 'dateOfMarriage'},
}

# Trường là số giấy tờ → phải toàn chữ số, dài 9 (CMND cũ) hoặc 12
ID_NUMBER_FIELDS = {'no', 'husbandIDNo', 'wifeIDNo'}

FUZZY_FIELD_THRESHOLD = 0.75   # ngưỡng khớp tên trường biểu mẫu
FUZZY_META_THRESHOLD = 0.80    # ngưỡng khớp formName/formCode

# Trường so bằng chứa-nhau thay vì exact: giá trị model trả kèm boilerplate
# hợp lệ theo prompt ('CCCD / Citizen Identity Card', 'ỦY BAN NHÂN DÂN Xã …')
CONTAINMENT_FIELDS = {'type', 'placeOfMarriage'}


# ── Chuẩn hoá ─────────────────────────────────────────────────────────────────

def normalize(value) -> str:
    """Chuẩn hoá chuỗi: NFC, gộp khoảng trắng, bỏ đầu đuôi, thường hoá."""
    if value is None:
        return ''
    s = unicodedata.normalize('NFC', str(value))
    s = re.sub(r'\s+', ' ', s).strip()
    return s.casefold()


def normalize_date(value) -> str:
    """Đưa ngày về dd/mm/yyyy. Nhận dd/mm/yyyy, dd-mm-yyyy, 'ngày d tháng m năm y'."""
    s = normalize(value)
    m = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', s)
    if not m:
        # "ngày 01 tháng 10 năm 2022" hoặc "01 tháng 10 năm 2022"
        m = re.search(r'(?:ngày\s*)?(\d{1,2})\s*tháng\s*(\d{1,2})\s*năm\s*(\d{4})', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f'{d:02d}/{mo:02d}/{y}'
    return s


def levenshtein(a, b) -> int:
    """Khoảng cách Levenshtein (DP 2 hàng). Nhận chuỗi (CER) hoặc list từ (WER)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(expected: str, predicted: str) -> float:
    """Character Error Rate trên chuỗi đã chuẩn hoá."""
    e, p = normalize(expected), normalize(predicted)
    if not e:
        return 0.0 if not p else 1.0
    return levenshtein(e, p) / len(e)


def wer(expected: str, predicted: str) -> float:
    """Word Error Rate: Levenshtein trên mức từ, chia số từ kỳ vọng."""
    e, p = normalize(expected).split(), normalize(predicted).split()
    if not e:
        return 0.0 if not p else 1.0
    return levenshtein(e, p) / len(e)


def similarity(expected: str, predicted: str) -> float:
    """Độ tương đồng chuỗi = 1 − khoảng cách Levenshtein chuẩn hoá [0..1]."""
    e, p = normalize(expected), normalize(predicted)
    longest = max(len(e), len(p))
    if not longest:
        return 1.0
    return 1.0 - levenshtein(e, p) / longest


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


# ── Chấm giấy tờ cá nhân ─────────────────────────────────────────────────────

def score_document(expected: dict, predicted: dict) -> list:
    """
    So từng trường trong expected với predicted.
    Trả về list dict: {field, expected, predicted, match, cer}.
    Trường 'type' chấm bằng chứa-nhau (Gemini hay trả 'Căn cước công dân / Citizen Identity Card').
    """
    predicted = predicted or {}
    results = []
    for field, exp_val in expected.items():
        pred_val = predicted.get(field)
        if field in DATE_FIELDS:
            e, p = normalize_date(exp_val), normalize_date(pred_val)
            match = (e == p)
        elif field in CONTAINMENT_FIELDS:
            e, p = normalize(exp_val), normalize(pred_val)
            match = bool(e and p and (e in p or p in e)) or _ratio(e, p) >= FUZZY_META_THRESHOLD
        else:
            e, p = normalize(exp_val), normalize(pred_val)
            match = (e == p)
        # Các chỉ số khoảng cách tính trên dạng đã chuẩn hoá dùng để so khớp (e, p)
        if match:
            f_cer, f_wer, f_sim = 0.0, 0.0, 1.0
        else:
            f_cer = levenshtein(e, p) / len(e) if e else (0.0 if not p else 1.0)
            ew, pw = e.split(), p.split()
            f_wer = levenshtein(ew, pw) / len(ew) if ew else (0.0 if not pw else 1.0)
            longest = max(len(e), len(p))
            f_sim = 1.0 - levenshtein(e, p) / longest if longest else 1.0
        results.append({
            'field': field,
            'expected': '' if exp_val is None else str(exp_val),
            'predicted': '' if pred_val is None else str(pred_val),
            'match': bool(match),
            'cer': round(f_cer, 4),
            'wer': round(f_wer, 4),
            'sim': round(f_sim, 4),
        })
    return results


# ── Tính hợp lệ của dữ liệu xuất ra (không cần ground truth) ─────────────────

def validate_output(doc_type: str, predicted: dict) -> dict:
    """
    Kiểm tra định dạng dữ liệu Gemini xuất ra, độc lập với đáp án:
    - đủ khóa schema theo prompt chưa
    - số giấy tờ có đúng 9/12 chữ số không
    - ngày có parse được về dd/mm/yyyy không
    - giới tính có nằm trong Nam/Nữ không
    - bao nhiêu trường bỏ trống
    Đây là chất lượng "xuất ra để tự điền hồ sơ": dù nội dung đúng mà định
    dạng sai thì form phía Frontend vẫn điền hỏng.
    """
    keys = DOC_KEYS.get(doc_type, [])
    predicted = predicted or {}

    missing_keys = [k for k in keys if k not in predicted]
    empty_fields = [k for k in keys if k in predicted and not normalize(predicted.get(k))]

    invalid = []
    for k in keys:
        v = predicted.get(k)
        if not normalize(v):
            continue
        if k in ID_NUMBER_FIELDS:
            digits = re.sub(r'\s', '', str(v))
            if not re.fullmatch(r'\d{9}|\d{12}', digits):
                invalid.append({'field': k, 'value': str(v),
                                'reason': 'số giấy tờ không phải 9/12 chữ số'})
        elif k in DATE_FIELDS:
            if not re.fullmatch(r'\d{2}/\d{2}/\d{4}', normalize_date(v)):
                invalid.append({'field': k, 'value': str(v),
                                'reason': 'ngày không parse được'})
        elif k == 'gender':
            if normalize(v) not in ('nam', 'nữ'):
                invalid.append({'field': k, 'value': str(v),
                                'reason': 'giới tính ngoài Nam/Nữ'})

    return {
        'schemaOk': not missing_keys,
        'missingKeys': missing_keys,
        'emptyFields': empty_fields,
        'invalidFormat': invalid,
        'nKeys': len(keys),
    }


# ── Chấm biểu mẫu trống ──────────────────────────────────────────────────────

# Phần tử PHỤ TRỢ có vẽ thật trên biểu mẫu nhưng nhãn không liệt kê là "trường":
# ô checkbox Nam/Nữ (option của Giới tính) và khối ký tên cuối trang
# ("..., ngày ... tháng ... năm ...", "(Ký, ghi rõ họ tên)"). Model đọc ra
# chúng là ĐÚNG với tờ giấy. CHỈ áp lên trường thừa CHƯA ghép cặp (không ảnh
# hưởng recall — 'Ngày, tháng, năm sinh' đã ghép với expected thì không bị đụng).
_AUX_FORM_LABELS = re.compile(
    r'^(nam|nữ|nu)$'
    r'|ngày.{0,4}tháng.{0,4}năm'
    r'|ký.{0,15}họ tên'
    r'|chữ ký'
    r'|địa điểm lập'
)


def _extract_predicted_labels(predicted: dict) -> list:
    """Lấy danh sách tên trường Gemini phát hiện được (label ưu tiên, fallback fieldName)."""
    labels = []
    for f in (predicted or {}).get('fields') or []:
        if isinstance(f, dict):
            label = f.get('label') or f.get('fieldName') or ''
        else:
            label = str(f)
        if normalize(label):
            labels.append(str(label))
    return labels


def score_form(expected: dict, predicted: dict) -> dict:
    """
    Chấm biểu mẫu: recall/precision tên trường (fuzzy, greedy best-match),
    và đúng/sai formName, formCode.
    """
    predicted = predicted or {}
    exp_fields = expected.get('fields') or []
    pred_labels = _extract_predicted_labels(predicted)

    # Greedy match: mỗi trường expected bắt cặp với label dự đoán tốt nhất còn lại
    remaining = [(i, normalize(l)) for i, l in enumerate(pred_labels)]
    matches = []
    for exp in exp_fields:
        e = normalize(exp)
        best, best_score = None, 0.0
        for idx, p in remaining:
            score = _ratio(e, p)
            if e and p and (e in p or p in e):
                score = max(score, FUZZY_FIELD_THRESHOLD)
            if score > best_score:
                best, best_score = idx, score
        if best is not None and best_score >= FUZZY_FIELD_THRESHOLD:
            matches.append({'expected': exp, 'predicted': pred_labels[best],
                            'score': round(best_score, 3)})
            remaining = [(i, p) for i, p in remaining if i != best]

    # Trường thừa chưa ghép cặp nhưng là phần tử phụ trợ có thật trên giấy
    # → loại khỏi mẫu số precision (model không "bịa")
    matched_pred = {m['predicted'] for m in matches}
    aux_extras = [l for l in pred_labels
                  if l not in matched_pred and _AUX_FORM_LABELS.search(normalize(l))]

    n_exp, n_match = len(exp_fields), len(matches)
    n_pred = len(pred_labels) - len(aux_extras)
    recall = n_match / n_exp if n_exp else 0.0
    precision = n_match / n_pred if n_pred else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    def meta_match(key):
        e, p = normalize(expected.get(key)), normalize(predicted.get(key))
        if not e:
            return None  # không có đáp án → bỏ qua
        return bool(p) and (e in p or p in e or _ratio(e, p) >= FUZZY_META_THRESHOLD)

    return {
        'nExpected': n_exp,
        'nPredicted': n_pred,
        'nMatched': n_match,
        'recall': round(recall, 4),
        'precision': round(precision, 4),
        'f1': round(f1, 4),
        'formNameMatch': meta_match('formName'),
        'formCodeMatch': meta_match('formCode'),
        'matchedPairs': matches,
        'missedFields': [e for e in exp_fields
                         if e not in [m['expected'] for m in matches]],
    }


# ── Bộ chỉ số tổng hợp (cho báo cáo/đồ án) ───────────────────────────────────

def aggregate_metrics(results: list) -> dict:
    """
    Tổng hợp các chỉ số chuẩn IE/OCR từ kết quả run_eval (giấy tờ cá nhân):
    Accuracy, Precision, Recall, F1 (micro), CER, WER, Similarity trung bình,
    Exact Match mức tài liệu, độ chính xác nhận diện loại giấy tờ, độ trễ.
    Trả về dict {docType: {...}, '__overall__': {...}}.
    Các chỉ số tính trên ảnh trích xuất thành công; tỷ lệ thất bại báo riêng.
    """
    groups = defaultdict(list)
    for r in results:
        if r.get('docType') != 'form' and r.get('status') == 'ok' and r.get('fields'):
            groups[r['docType']].append(r)
            groups['__overall__'].append(r)

    out = {}
    for doc, rs in groups.items():
        fields = [f for r in rs for f in r['fields']]
        n = len(fields)
        n_match = sum(1 for f in fields if f['match'])

        # IE chuẩn: TP = trường đúng; precision chia số trường model trả ra
        # (khác rỗng); recall chia số trường kỳ vọng (khác rỗng).
        exp_nonempty = [f for f in fields if normalize(f['expected'])]
        pred_nonempty = [f for f in fields if normalize(f['predicted'])]
        tp = sum(1 for f in exp_nonempty if f['match'])
        precision = tp / len(pred_nonempty) if pred_nonempty else 0.0
        recall = tp / len(exp_nonempty) if exp_nonempty else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

        latencies = sorted(r['elapsedSec'] for r in rs if r.get('elapsedSec'))
        type_fields = [f for f in fields if f['field'] == 'type']

        out[doc] = {
            'nDocs': len(rs),
            'nFields': n,
            'accuracy': n_match / n if n else 0.0,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'cer': sum(f['cer'] for f in fields) / n if n else 0.0,
            'wer': sum(f.get('wer', 0.0) for f in fields) / n if n else 0.0,
            'similarity': sum(f.get('sim', 1.0) for f in fields) / n if n else 0.0,
            'docExactMatch': sum(1 for r in rs if all(f['match'] for f in r['fields'])) / len(rs),
            'typeAccuracy': (sum(1 for f in type_fields if f['match']) / len(type_fields))
                            if type_fields else None,
            'latencyMean': sum(latencies) / len(latencies) if latencies else None,
            # p95 nearest-rank: phần tử thứ ceil(0.95·n)
            'latencyP95': latencies[-(-len(latencies) * 95 // 100) - 1] if latencies else None,
        }
    return out
