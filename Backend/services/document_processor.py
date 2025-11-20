import os


def process_document(file_path: str, original_name: str = None) -> str:
    """Try to extract text from a document.

    - If the file is a plain `.txt`, read and return its content.
    - For other types (images, pdf), return None (placeholder for OCR integration).

    This function is intentionally dependency-free so it will work without extra packages.
    If you want OCR/PDF extraction, replace the implementation and add required packages
    to `requirements.txt` (e.g., `pytesseract`, `pdfminer.six`, `PyMuPDF`).
    """
    if not file_path or not os.path.exists(file_path):
        return None

    _, ext = os.path.splitext(file_path)
    ext = ext.lower().lstrip('.')

    try:
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

        # Placeholder: if you later install OCR/PDF libraries, handle them here.
        # Example: for images use pytesseract.image_to_string(Image.open(file_path))
        # For PDF, use PyPDF2 or pdfminer.six to extract text.
        return None
    except Exception as e:
        # Never raise from background worker; log and return None
        print(f"document_processor: failed to process {file_path}: {e}")
        return None
