import json
import logging
import os

logger = logging.getLogger(__name__)


def process_document(file_path: str, original_name: str = None) -> str:
    """Extract text/structured data from a document.

    - .txt  → read as plain text
    - images / PDF → call Gemini via image_extractor (requires GEMINI_API_KEY)

    Returns extracted content as a string, or None on failure.
    """
    if not file_path or not os.path.exists(file_path):
        return None

    _, ext = os.path.splitext(file_path)
    ext = ext.lower().lstrip('.')

    try:
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

        if ext in ('jpg', 'jpeg', 'png', 'webp', 'heic', 'heif', 'pdf'):
            from services.image_extractor import extract_document
            result = extract_document(file_path)
            return json.dumps(result, ensure_ascii=False, indent=2)

        return None
    except Exception as e:
        logger.warning("Failed to process %s: %s", file_path, e)
        return None
