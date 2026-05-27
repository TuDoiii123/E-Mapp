"""
PDF Converter — chuyển đổi .doc/.docx sang PDF bằng LibreOffice headless.
Cache output để tránh chuyển đổi lặp lại.
"""
import os
import subprocess
import shutil
import hashlib
import logging
from pathlib import Path

log = logging.getLogger('pdf_converter')

_CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'pdf_cache')
os.makedirs(_CACHE_DIR, exist_ok=True)


def _libreoffice_path() -> str | None:
    """Tìm đường dẫn LibreOffice."""
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


def word_to_pdf(input_path: str, force: bool = False) -> str | None:
    """
    Chuyển đổi file Word sang PDF bằng LibreOffice headless.
    Trả về đường dẫn đến file PDF đã tạo, hoặc None nếu thất bại.
    Kết quả được cache theo nội dung file.

    Args:
        input_path: Đường dẫn tới file .doc hoặc .docx
        force: True để bỏ qua cache và chuyển đổi lại
    """
    if not os.path.exists(input_path):
        log.warning(f'word_to_pdf: file không tồn tại: {input_path}')
        return None

    # Tạo cache key từ nội dung file
    with open(input_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    base_name = Path(input_path).stem
    cache_key = f'{base_name}_{file_hash[:8]}.pdf'
    cached_path = os.path.join(_CACHE_DIR, cache_key)

    if not force and os.path.exists(cached_path):
        log.debug(f'Cache hit: {base_name}')
        return cached_path

    lo = _libreoffice_path()
    if not lo:
        log.warning('LibreOffice không tìm thấy — không thể chuyển đổi sang PDF')
        return None

    try:
        result = subprocess.run(
            [lo, '--headless', '--convert-to', 'pdf',
             '--outdir', _CACHE_DIR, input_path],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, 'HOME': os.path.expanduser('~')}
        )
        if result.returncode != 0:
            log.error(f'LibreOffice lỗi: {result.stderr[:500]}')
            return None

        # LibreOffice đặt tên output là <stem>.pdf trong outdir
        default_out = os.path.join(_CACHE_DIR, Path(input_path).stem + '.pdf')
        if os.path.exists(default_out):
            if default_out != cached_path:
                os.replace(default_out, cached_path)
            return cached_path

        log.warning(f'LibreOffice không tạo ra file output tại {default_out}')
        return None

    except subprocess.TimeoutExpired:
        log.error('LibreOffice chuyển đổi quá thời gian (60s)')
        return None
    except Exception as e:
        log.error(f'Lỗi chuyển đổi PDF: {e}')
        return None


def is_available() -> bool:
    """Kiểm tra LibreOffice có sẵn trong hệ thống không."""
    return _libreoffice_path() is not None
