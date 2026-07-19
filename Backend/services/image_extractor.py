"""
ImageExtract service — wraps Gemini 2.5 Flash to extract structured data
from personal documents (CCCD, GPLX, marriage cert, …) and form templates.
Supports images (jpg/png/webp/heic/heif) and PDF (via PyMuPDF).
"""
import json
import os
import sys
import time

# Make ImageExtract importable
_IE_PATH = os.path.join(os.path.dirname(__file__), '..', 'ImageExtract')
if _IE_PATH not in sys.path:
    sys.path.insert(0, _IE_PATH)

from logger import get_logger

log = get_logger('image_extractor')

_IMAGE_MIME = {
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png':  'image/png',
    '.webp': 'image/webp',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
}


def _clean_json(text: str) -> str:
    """Strip markdown code fences from model output."""
    text = text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        text = '\n'.join(lines[1:])
        if text.endswith('```'):
            text = text[:-3]
    return text.strip()


def _gemini_client():
    from google import genai
    # Thử GEMINI_API_KEY trước, fallback sang GOOGLE_API_KEY / GOOGLE_API_KEY_1
    api_key = (
        os.environ.get('GEMINI_API_KEY') or
        os.environ.get('GOOGLE_API_KEY') or
        os.environ.get('GOOGLE_API_KEY_1')
    )
    # Bỏ qua placeholder
    if not api_key or api_key.startswith('your_'):
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_API_KEY_1')
    if not api_key:
        raise EnvironmentError('Chưa cấu hình GEMINI_API_KEY hoặc GOOGLE_API_KEY')
    return genai.Client(api_key=api_key)


def _preprocess_image(image_bytes: bytes, mime_type: str) -> tuple:
    """
    Tiền xử lý ảnh trước khi gửi Gemini — cải thiện ảnh tối/mờ/nhỏ:
    - sửa hướng theo EXIF (ảnh chụp điện thoại hay bị xoay)
    - ảnh tối (độ sáng trung bình thấp) → autocontrast
    - ảnh nhỏ (< 1600px cạnh dài) → upscale 2× LANCZOS + unsharp mask nhẹ
    An toàn: thiếu Pillow / định dạng lạ (HEIC…) → trả nguyên bản.
    """
    try:
        import io
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        changed = False

        # Ảnh tối: 2 mức — giấy trắng bị tối chỉ xuống ~120-140 nên autocontrast
        # từ <145 (kéo lại dải trắng-đen, vô hại với ảnh thường vì cutoff=1);
        # tối hẳn (<110, ảnh thẻ nền màu) mới tăng sáng thêm
        brightness = ImageStat.Stat(img.convert('L')).mean[0]
        if brightness < 145:
            img = ImageOps.autocontrast(img, cutoff=1)
            if brightness < 110:
                img = ImageEnhance.Brightness(img).enhance(1.15)
            changed = True

        # Ảnh nhỏ: phóng to giúp Gemini soi dấu thanh + chữ số
        if max(img.size) < 1600:
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=90, threshold=2))
            changed = True

        if not changed:
            return image_bytes, mime_type

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue(), 'image/png'
    except Exception as e:
        log.warning(f'preprocess skipped: {e}')
        return image_bytes, mime_type


def _call_gemini(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    from google.genai import types
    image_bytes, mime_type = _preprocess_image(image_bytes, mime_type)
    client = _gemini_client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ]
    )
    return response.text


# ── Public API ────────────────────────────────────────────────────────────────

def extract_document(file_path: str) -> dict:
    """
    Extract structured info from a personal document image or PDF.
    Returns parsed JSON dict (đã qua hậu xử lý sửa địa danh + kiểm chéo CCCD).
    Raises on failure.
    """
    from prompt import AGENT_MESSAGE
    from services.ocr_postcorrect import postcorrect_document
    from services.ocr_metrics import log_extraction_metrics
    ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    t0 = time.perf_counter()

    if ext == '.pdf':
        pages = _extract_pdf(file_path, AGENT_MESSAGE)
        # Return first page result that parsed successfully
        for page in pages:
            if not page.get('parse_error'):
                data = postcorrect_document(page['data'])
                log_extraction_metrics(data, time.perf_counter() - t0, file_name)
                return data
        return {'pages': pages}

    mime_type = _IMAGE_MIME.get(ext, 'image/jpeg')
    with open(file_path, 'rb') as f:
        image_bytes = f.read()

    raw = _call_gemini(image_bytes, mime_type, AGENT_MESSAGE)
    data = postcorrect_document(json.loads(_clean_json(raw)))
    log_extraction_metrics(data, time.perf_counter() - t0, file_name)
    return data


def extract_form_template(file_path: str) -> dict:
    """
    Analyze a blank government form template image or PDF.
    Returns structured JSON describing the form's fields and metadata.
    """
    from prompt import FORM_TEMPLATE_MESSAGE
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        pages = _extract_pdf(file_path, FORM_TEMPLATE_MESSAGE)
        # Merge fields across pages for multi-page forms
        merged = {'pages': []}
        all_fields = []
        all_sections = []
        for page in pages:
            if page.get('parse_error'):
                continue
            data = page['data']
            merged.update({k: v for k, v in data.items() if k not in ('fields', 'sections')})
            all_fields.extend(data.get('fields') or [])
            all_sections.extend(data.get('sections') or [])
            merged['pages'].append(page['page'])
        if all_fields:
            merged['fields'] = all_fields
        if all_sections:
            merged['sections'] = list(dict.fromkeys(all_sections))  # dedupe
        return merged

    mime_type = _IMAGE_MIME.get(ext, 'image/jpeg')
    with open(file_path, 'rb') as f:
        image_bytes = f.read()

    raw = _call_gemini(image_bytes, mime_type, FORM_TEMPLATE_MESSAGE)
    return json.loads(_clean_json(raw))


# ── PDF helper ────────────────────────────────────────────────────────────────

def _extract_pdf(file_path: str, prompt: str) -> list:
    """Render each PDF page to PNG and call Gemini per page."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError('PyMuPDF is required for PDF extraction. Run: pip install PyMuPDF')

    results = []
    doc = fitz.open(file_path)
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes('png')

            try:
                raw = _call_gemini(image_bytes, 'image/png', prompt)
                data = json.loads(_clean_json(raw))
                results.append({'page': page_num + 1, 'data': data})
            except json.JSONDecodeError as e:
                log.warning(f'PDF page {page_num + 1} JSON parse error: {e}')
                results.append({'page': page_num + 1, 'data': raw, 'parse_error': True})
            except Exception as e:
                log.error(f'PDF page {page_num + 1} Gemini call failed: {e}')
                results.append({'page': page_num + 1, 'data': None, 'parse_error': True})
    finally:
        doc.close()

    return results
