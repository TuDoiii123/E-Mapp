"""
PDF Converter — chuyển đổi .doc/.docx sang PDF.
Ưu tiên: LibreOffice headless → docx2pdf (Word COM, Windows) → thất bại.
Cache output theo MD5 nội dung để tránh chuyển đổi lặp lại.
"""
import os
import subprocess
import shutil
import hashlib
import logging
from pathlib import Path

log = logging.getLogger('pdf_converter')

_CACHE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'pdf_cache')
)
os.makedirs(_CACHE_DIR, exist_ok=True)


# ── Tìm engine ────────────────────────────────────────────────────────────────

def _libreoffice_path() -> str | None:
    """Tìm đường dẫn LibreOffice executable."""
    candidates = [
        'libreoffice', 'soffice',
        r'C:\Program Files\LibreOffice\program\soffice.exe',
        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        '/usr/bin/libreoffice', '/usr/bin/soffice',
        '/usr/local/bin/libreoffice',
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    ]
    for c in candidates:
        found = shutil.which(c)
        if found:
            return found
        if os.path.exists(c):
            return c
    return None


def _win32com_available() -> bool:
    """Kiểm tra win32com (Windows) có sẵn không."""
    try:
        import win32com.client  # noqa: F401
        return True
    except ImportError:
        return False


def _docx2pdf_available() -> bool:
    """Kiểm tra docx2pdf có dùng được không."""
    try:
        import docx2pdf  # noqa: F401
        return True
    except ImportError:
        return False


# ── Engines ───────────────────────────────────────────────────────────────────

def _convert_libreoffice(input_path: str, output_path: str) -> bool:
    """Chuyển đổi bằng LibreOffice headless."""
    lo = _libreoffice_path()
    if not lo:
        return False
    try:
        result = subprocess.run(
            [lo, '--headless', '--convert-to', 'pdf',
             '--outdir', _CACHE_DIR, input_path],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, 'HOME': os.path.expanduser('~')}
        )
        if result.returncode != 0:
            log.warning(f'LibreOffice lỗi: {result.stderr[:200]}')
            return False
        # LibreOffice đặt tên output là <stem>.pdf trong outdir
        default_out = os.path.join(_CACHE_DIR, Path(input_path).stem + '.pdf')
        if os.path.exists(default_out):
            if default_out != output_path:
                os.replace(default_out, output_path)
            return True
        return False
    except subprocess.TimeoutExpired:
        log.warning('LibreOffice timeout (60s)')
        return False
    except Exception as e:
        log.warning(f'LibreOffice exception: {e}')
        return False


def _convert_win32com(input_path: str, output_path: str) -> bool:
    """Chuyển đổi bằng win32com (Microsoft Word COM trực tiếp).
    Hoạt động với cả .doc (OLE2) và .docx (OOXML) trên Windows.
    Suppress tất cả dialog/alert để chạy headless."""
    try:
        import win32com.client
        abs_in  = str(Path(input_path).resolve())
        abs_out = str(Path(output_path).resolve())

        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0   # wdAlertsNone — không hiện bất kỳ dialog nào

        try:
            doc = word.Documents.Open(
                abs_in,
                ReadOnly=True,
                ConfirmConversions=False,
                AddToRecentFiles=False,
            )
            doc.SaveAs(abs_out, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close(False)
        finally:
            word.Quit()

        return os.path.exists(abs_out)
    except ImportError:
        return False
    except Exception as e:
        log.warning(f'win32com exception: {e}')
        return False


def _convert_docx2pdf(input_path: str, output_path: str) -> bool:
    """Chuyển đổi bằng docx2pdf (chỉ hoạt động tốt với .docx, không phải .doc)."""
    try:
        from docx2pdf import convert as _d2p_convert
        abs_in  = str(Path(input_path).resolve())
        abs_out = str(Path(output_path).resolve())
        _d2p_convert(abs_in, abs_out)
        return os.path.exists(abs_out)
    except ImportError:
        return False
    except Exception as e:
        log.warning(f'docx2pdf exception: {e}')
        return False


# ── Public API ────────────────────────────────────────────────────────────────

def word_to_pdf(input_path: str, force: bool = False) -> str | None:
    """
    Chuyển đổi file Word sang PDF.
    Thử LibreOffice trước, fallback sang docx2pdf (Word COM, chỉ Windows).
    Trả về đường dẫn file PDF, hoặc None nếu thất bại.
    Kết quả được cache theo MD5 nội dung file.
    """
    if not os.path.exists(input_path):
        log.warning(f'word_to_pdf: file không tồn tại: {input_path}')
        return None

    # Cache key theo nội dung file
    with open(input_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    base_name = Path(input_path).stem
    cache_key  = f'{base_name}_{file_hash[:8]}.pdf'
    cached_path = os.path.join(_CACHE_DIR, cache_key)

    if not force and os.path.exists(cached_path):
        log.debug(f'Cache hit: {base_name}')
        return cached_path

    # 1. LibreOffice (ưu tiên — cross-platform, batch-friendly)
    if _libreoffice_path():
        log.debug(f'Converting via LibreOffice: {base_name}')
        if _convert_libreoffice(input_path, cached_path):
            log.info(f'PDF ready (LibreOffice): {cache_key}')
            return cached_path

    # 2. win32com — dùng Word COM trực tiếp (Windows, xử lý được cả .doc)
    if _win32com_available():
        log.debug(f'Converting via win32com: {base_name}')
        if _convert_win32com(input_path, cached_path):
            log.info(f'PDF ready (win32com): {cache_key}')
            return cached_path

    # 3. docx2pdf — fallback cuối (chỉ tốt với .docx)
    if _docx2pdf_available():
        log.debug(f'Converting via docx2pdf: {base_name}')
        if _convert_docx2pdf(input_path, cached_path):
            log.info(f'PDF ready (docx2pdf): {cache_key}')
            return cached_path

    log.warning(f'Không có engine nào chuyển đổi được: {base_name}')
    return None


def is_available() -> bool:
    """Kiểm tra có ít nhất 1 engine chuyển đổi PDF không."""
    return (
        _libreoffice_path() is not None
        or _win32com_available()
        or _docx2pdf_available()
    )
