"""
OCR extraction quality metrics — terminal-only logging, cùng phong cách với
RAG/utils/rag_metrics.py. In ra ngay sau mỗi lần extract_document() chạy
THẬT trong production (Backend/services/image_extractor.py), không phải chỉ
lúc chạy bộ eval offline.

Ảnh người dùng tải lên thật không có đáp án đúng để so — nên đây là proxy độ
tin cậy: đủ khoá schema / không rỗng / đúng định dạng (số giấy tờ 9-12 chữ
số, ngày parse được, giới tính hợp lệ). Dùng lại validate_output() +
DOC_KEYS của bộ eval (ImageExtract/eval/scoring.py) để không lệch định nghĩa
"hợp lệ" giữa 2 nơi. Muốn đo ĐÚNG NỘI DUNG (so với đáp án thật) thì chạy
Backend/ImageExtract/eval/run_eval.py trên dataset có nhãn.
"""
import os
import re
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ImageExtract', 'eval'))
from scoring import validate_output, DOC_KEYS  # noqa: E402

from logger import get_logger

log = get_logger('ocr.metrics')

_GREEN, _YELLOW, _RED, _BOLD, _DIM, _CYAN, _RESET = (
    '\033[92m', '\033[93m', '\033[91m', '\033[1m', '\033[2m', '\033[96m', '\033[0m',
)
_ANSI_RE = re.compile(r'\033\[[0-9;]*m')


def _visible_len(s: str) -> int:
    return len(_ANSI_RE.sub('', s))


def _pad(s: str, width: int) -> str:
    return s + ' ' * max(0, width - _visible_len(s))


def _truncate(value, width: int = 32) -> str:
    text = str(value or '').replace('\n', ' ').strip()
    return text if len(text) <= width else text[:width - 1] + '…'


def _guess_doc_type(data: dict) -> Optional[str]:
    """
    Suy loại giấy tờ từ khoá dữ liệu trả về (khớp DOC_KEYS nhiều nhất) —
    không parse chuỗi 'type' vì Gemini trả kèm tên song ngữ không ổn định
    ('Giấy phép lái xe / Driver's License'...).

    'type' KHÔNG tính vào overlap: khoá này có mặt ở CẢ 3 schema (cccd/gplx/
    marriage), nên giấy tờ NGOÀI danh mục (vd 'Giấy đề nghị đăng ký hộ kinh
    doanh') mà Gemini chỉ trả về mỗi {'type': ...} sẽ hoà điểm 1 ở cả 3 loại
    — và luôn bị đoán nhầm thành loại đầu tiên trong dict (cccd) nếu tính cả
    'type'. Yêu cầu khớp ít nhất 1 trường ĐẶC TRƯNG (ngoài 'type') mới nhận
    diện, không thì coi là chưa biết.
    """
    if not data:
        return None
    best, best_score = None, 0
    for doc_type, keys in DOC_KEYS.items():
        distinctive = set(keys) - {'type'}
        overlap = len(distinctive & set(data.keys()))
        if overlap > best_score:
            best, best_score = doc_type, overlap
    return best if best_score else None


def _field_status(field: str, validity: dict) -> tuple:
    """Trả (nhãn màu, lý do nếu sai) cho 1 trường theo kết quả validate_output."""
    if field in validity['missingKeys']:
        return f'{_RED}THIẾU KHOÁ{_RESET}', ''
    if field in validity['emptyFields']:
        return f'{_YELLOW}RỖNG{_RESET}', ''
    bad = next((b for b in validity['invalidFormat'] if b['field'] == field), None)
    if bad:
        return f'{_RED}SAI ĐỊNH DẠNG{_RESET}', bad['reason']
    return f'{_GREEN}OK{_RESET}', ''


def _pct_color(pct: float) -> str:
    return _GREEN if pct >= 90 else (_YELLOW if pct >= 70 else _RED)


W_FIELD, W_VAL, W_STATUS = 24, 32, 15


def _render_table(title: str, rows: list, summary_label: str, n_ok: int, n_total: int) -> str:
    """
    Dựng bảng ASCII dùng chung cho cả giấy tờ đã biết schema lẫn giấy tờ tự do.
    rows: list (field_display, value, status_colored, reason).
    """
    sep_top = f'┌{"─"*(W_FIELD+2)}┬{"─"*(W_VAL+2)}┬{"─"*(W_STATUS+2)}┐'
    sep_mid = sep_top.replace('┌', '├').replace('┐', '┤')
    sep_bot = sep_top.replace('┌', '└').replace('┐', '┘')
    header = (f'│ {_pad("Trường", W_FIELD)} │ {_pad("Giá trị trích xuất", W_VAL)} │ '
              f'{_pad("Trạng thái", W_STATUS)} │')

    lines = ['', title, sep_top, header, sep_mid]
    for field_display, value, status, reason in rows:
        line = (f'│ {_pad(field_display, W_FIELD)} │ {_pad(_truncate(value), W_VAL)} │ '
                f'{_pad(status, W_STATUS)} │')
        if reason:
            line += f'  {_DIM}{reason}{_RESET}'
        lines.append(line)

    pct = 100.0 * n_ok / n_total if n_total else 0.0
    lines.append(sep_bot)
    lines.append(f'  {_BOLD}{summary_label}{_RESET}: {n_ok}/{n_total} trường  '
                f'{_pct_color(pct)}{pct:.0f}%{_RESET}')
    lines.append('')
    return '\n'.join(lines)


def _display_field(name: str) -> str:
    """'dia_chi_thuong_tru' → 'Dia chi thuong tru' — chỉ để hiện gọn trong bảng debug."""
    text = name.replace('_', ' ').strip()
    return text[:1].upper() + text[1:] if text else name


def _log_known_schema(data: dict, doc_type: str, elapsed_sec: float, file_name: str) -> None:
    """CCCD/GPLX/giấy kết hôn — có DOC_KEYS/validate_output để kiểm định dạng cụ thể."""
    validity = validate_output(doc_type, data)
    keys = DOC_KEYS[doc_type]
    n_bad = len(validity['missingKeys']) + len(validity['emptyFields']) + len(validity['invalidFormat'])
    n_ok = len(keys) - n_bad

    rows = []
    for field in keys:
        status, reason = _field_status(field, validity)
        rows.append((field, data.get(field), status, reason))

    title = (f'{_BOLD}{_CYAN}[OCR METRICS]{_RESET} {file_name}  loại={_BOLD}{doc_type}{_RESET}  '
             f'{elapsed_sec:.1f}s')
    log.info(_render_table(title, rows, 'Hợp lệ định dạng', n_ok, len(keys)))


def _log_generic(data: dict, elapsed_sec: float, file_name: str) -> None:
    """
    Giấy tờ NGOÀI cccd/gplx/marriage — không có schema cố định để đối chiếu
    (đúng chủ trương không bó OCR vào vài loại giấy tờ cứng). Field do Gemini
    tự đặt tên (tiếng Việt, phẳng — theo rule 9 của AGENT_MESSAGE) nên chỉ
    kiểm được RỖNG/ĐÃ ĐIỀN, không kiểm được định dạng cụ thể như CCCD.
    """
    fields = list(data.keys())
    if not fields:
        log.info(f'[OCR METRICS] {file_name}: không trích xuất được trường nào.')
        return

    rows = []
    n_ok = 0
    for field in fields:
        value = data.get(field)
        filled = bool(str(value or '').strip())
        n_ok += filled
        status = f'{_GREEN}OK{_RESET}' if filled else f'{_YELLOW}RỖNG{_RESET}'
        rows.append((_display_field(field), value, status, ''))

    title = (f'{_BOLD}{_CYAN}[OCR METRICS]{_RESET} {file_name}  '
             f'loại={_BOLD}(ngoài danh mục — {len(fields)} trường tự do){_RESET}  {elapsed_sec:.1f}s')
    log.info(_render_table(title, rows, 'Đã điền', n_ok, len(fields)))


def log_extraction_metrics(data: dict, elapsed_sec: float, file_name: str = '') -> None:
    """
    In bảng độ tin cậy ra terminal Backend ngay sau khi extract_document()
    trả kết quả — LUÔN in bảng, dù giấy tờ có khớp CCCD/GPLX/kết hôn hay là
    loại tự do nào khác (OCR không bó cứng vào 3 loại này, chỉ 3 loại đó mới
    kiểm được định dạng chi tiết hơn).
    """
    doc_type = _guess_doc_type(data)
    if doc_type:
        _log_known_schema(data, doc_type, elapsed_sec, file_name)
    else:
        _log_generic(data, elapsed_sec, file_name)
