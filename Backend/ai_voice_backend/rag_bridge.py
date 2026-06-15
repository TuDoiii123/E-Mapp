"""
Cầu nối tới RAG có sẵn (RAG.tools.rag.search_project_documents).

Lazy + an toàn lỗi: import nặng (model embedding) chỉ xảy ra khi gọi lần đầu;
mọi lỗi → trả [] để hội thoại không bao giờ chết vì RAG.
"""
import sys
from pathlib import Path
from typing import Callable, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('voice.rag')


def _load_search() -> Callable[[str], List[str]]:
    """Trả về hàm search_project_documents (import lazy)."""
    from RAG.tools.rag import search_project_documents
    return search_project_documents


def search(query: str, top_k: int = 3) -> List[str]:
    """Trả về tối đa top_k đoạn answer_text liên quan; lỗi/rỗng → []."""
    if not query or not query.strip():
        return []
    try:
        fn = _load_search()
        results = fn(query) or []
        return [r for r in results if r][:top_k]
    except Exception as e:  # noqa: BLE001
        log.debug(f'[RAG bridge] lỗi: {e}')
        return []
