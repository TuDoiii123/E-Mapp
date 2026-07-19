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


def log_extraction_metrics(data: dict, elapsed_sec: float, file_name: str = '') -> None:
    """In bảng độ tin cậy ra terminal Backend ngay sau khi extract_document() trả kết quả."""
    doc_type = _guess_doc_type(data)
    if doc_type is None:
        log.info(f'[OCR METRICS] {file_name}: không nhận diện được loại giấy tờ đã biết '
                 f'(cccd/gplx/marriage) — bỏ qua kiểm tra định dạng.')
        return

    validity = validate_output(doc_type, data)
    keys = DOC_KEYS[doc_type]
    n_bad = len(validity['missingKeys']) + len(validity['emptyFields']) + len(validity['invalidFormat'])
    n_ok = len(keys) - n_bad
    pct = 100.0 * n_ok / len(keys) if keys else 0.0
    pct_color = _GREEN if pct >= 90 else (_YELLOW if pct >= 70 else _RED)

    W_FIELD, W_VAL, W_STATUS = 22, 32, 15
    sep_top = f'┌{"─"*(W_FIELD+2)}┬{"─"*(W_VAL+2)}┬{"─"*(W_STATUS+2)}┐'
    sep_mid = sep_top.replace('┌', '├').replace('┐', '┤')
    sep_bot = sep_top.replace('┌', '└').replace('┐', '┘')
    header = (f'│ {_pad("Trường", W_FIELD)} │ {_pad("Giá trị trích xuất", W_VAL)} │ '
              f'{_pad("Định dạng", W_STATUS)} │')

    lines = [
        '',
        f'{_BOLD}{_CYAN}[OCR METRICS]{_RESET} {file_name}  loại={_BOLD}{doc_type}{_RESET}  '
        f'{elapsed_sec:.1f}s',
        sep_top, header, sep_mid,
    ]
    for field in keys:
        status, reason = _field_status(field, validity)
        line = (f'│ {_pad(field, W_FIELD)} │ {_pad(_truncate(data.get(field)), W_VAL)} │ '
                f'{_pad(status, W_STATUS)} │')
        if reason:
            line += f'  {_DIM}{reason}{_RESET}'
        lines.append(line)

    lines.append(sep_bot)
    lines.append(f'  {_BOLD}Hợp lệ định dạng{_RESET}: {n_ok}/{len(keys)} trường  '
                f'{pct_color}{pct:.0f}%{_RESET}')
    lines.append('')

    log.info('\n'.join(lines))
