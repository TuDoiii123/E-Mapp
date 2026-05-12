"""
SuggestService — bridge giữa SuggestProcedure (embedding model) và ServiceRequirement.

Cung cấp:
  suggest_with_requirements(query)  → gợi ý thủ tục + giấy tờ kèm theo
  format_for_voice(suggestions)     → chuỗi hội thoại thân thiện cho voice bot
  format_for_chat(suggestions)      → markdown cho RAG chatbot
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from logger import get_logger

log = get_logger('suggest_service')

# ── Bản đồ từ khoá → service_id/key để tra cứu ServiceRequirement ────────────
# Key trùng với _KEYWORD_MAP trong service_requirement.py
_NAME_TO_KEY = {
    'ket_hon':   ['kết hôn', 'hôn nhân', 'đăng ký kết hôn'],
    'khai_sinh': ['khai sinh', 'đăng ký khai sinh', 'khai báo trẻ sơ sinh'],
    'cccd':      ['cccd', 'căn cước', 'chứng minh nhân dân', 'định danh'],
    'ho_khau':   ['hộ khẩu', 'thường trú', 'tạm trú', 'cư trú', 'đăng ký thường trú'],
    'dat_dai':   ['đất đai', 'quyền sử dụng đất', 'sổ đỏ', 'sổ hồng', 'cấp giấy chứng nhận'],
    'gplx':      ['giấy phép lái xe', 'bằng lái xe', 'bằng lái', 'gplx', 'đổi gplx'],
}


def _name_to_service_key(procedure_name: str) -> str:
    """Chuyển tên thủ tục → service_key để tra ServiceRequirement."""
    lower = procedure_name.lower()
    for key, keywords in _NAME_TO_KEY.items():
        if any(kw in lower for kw in keywords):
            return key
    return 'default'


def _get_requirements(service_key: str) -> List[Dict]:
    """
    Trả về danh sách giấy tờ cho service_key.
    Dùng DB nếu có, fallback về defaults tĩnh.
    """
    try:
        from models.service_requirement import ServiceRequirement
        return ServiceRequirement.find_by_service_id(service_key)
    except Exception as e:
        log.debug(f'[SuggestService] DB requirements failed: {e}')
    # Fallback tĩnh — không cần DB/Flask context
    try:
        from models.service_requirement import ServiceRequirement
        return ServiceRequirement._make_defaults(service_key)
    except Exception:
        pass
    # Last resort: trả về mặc định cứng
    return [
        {'id': f'{service_key}-0', 'serviceId': service_key, 'docName': 'CCCD / Căn cước công dân',
         'docDescription': 'Bản gốc còn hiệu lực', 'isRequired': True, 'docType': 'original', 'orderIndex': 0},
        {'id': f'{service_key}-1', 'serviceId': service_key, 'docName': 'Đơn yêu cầu theo mẫu',
         'docDescription': 'Điền đầy đủ thông tin', 'isRequired': True, 'docType': 'original', 'orderIndex': 1},
    ]


# ── Main API ──────────────────────────────────────────────────────────────────

def suggest_with_requirements(
    query: str,
    top_k: int = 4,
    threshold: float = 0.45,
    include_requirements: bool = True,
) -> Dict[str, Any]:
    """
    Gợi ý thủ tục hành chính phù hợp với query và kèm danh sách giấy tờ.

    Returns
    -------
    {
      'suggestions': [
        {
          'procedure_name': str,
          'procedure_internal_id': int,
          'similarity_score': float,
          'source': 'embedding' | 'ranking_label',
          'link': str,
          'service_key': str,           # key cho ServiceRequirement
          'requirements': [             # chỉ khi include_requirements=True
            { id, docName, docDescription, isRequired, docType, orderIndex }
          ]
        }, ...
      ],
      'explanation': str,
      'total': int,
      'query': str,
    }
    """
    try:
        from RAG.tools.suggest import suggest_procedures
    except ImportError as e:
        return {
            'suggestions': [],
            'explanation': 'Mô-đun gợi ý chưa sẵn sàng.',
            'error': str(e),
            'total': 0,
            'query': query,
        }

    raw = suggest_procedures(query=query, top_k=top_k, threshold=threshold)

    if raw.get('error'):
        return {
            'suggestions': [],
            'explanation': raw.get('explanation', 'Lỗi gợi ý thủ tục.'),
            'error': raw['error'],
            'total': 0,
            'query': query,
        }

    enriched: List[Dict] = []
    req_cache: Dict[str, List[Dict]] = {}  # cache by service_key

    for s in raw.get('suggestions', []):
        name    = s.get('procedure_name', '')
        svc_key = _name_to_service_key(name)
        requirements: List[Dict] = []

        if include_requirements:
            if svc_key not in req_cache:
                req_cache[svc_key] = _get_requirements(svc_key)
            requirements = req_cache[svc_key]

        enriched.append({
            **s,
            'service_key':  svc_key,
            'requirements': requirements,
        })

    explanation = (
        f'Tìm thấy {len(enriched)} thủ tục liên quan đến yêu cầu của bạn.'
        if enriched else
        'Không tìm thấy thủ tục phù hợp. Bạn có thể thử với từ khóa khác.'
    )

    return {
        'suggestions': enriched,
        'explanation': explanation,
        'total':       len(enriched),
        'query':       query,
    }


# ── Formatters ────────────────────────────────────────────────────────────────

def format_for_voice(suggestions: List[Dict], max_procedures: int = 2) -> str:
    """
    Tạo chuỗi hội thoại ngắn gọn cho voice chatbot.
    Chỉ đọc tên thủ tục + danh sách giấy tờ bắt buộc.
    """
    if not suggestions:
        return 'Tôi không tìm thấy thủ tục phù hợp. Bạn có thể mô tả cụ thể hơn không?'

    lines = ['Tôi tìm được các thủ tục phù hợp:']
    for i, sug in enumerate(suggestions[:max_procedures], 1):
        name = sug.get('procedure_name', 'Thủ tục không rõ')
        lines.append(f'{i}. {name}.')
        reqs = [r for r in sug.get('requirements', []) if r.get('isRequired')]
        if reqs:
            doc_names = ', '.join(r['docName'] for r in reqs[:4])
            lines.append(f'   Giấy tờ cần: {doc_names}.')

    if len(suggestions) > max_procedures:
        lines.append(f'Và {len(suggestions) - max_procedures} thủ tục khác. Bạn muốn biết thêm thủ tục nào?')

    return ' '.join(lines)


def format_for_chat(suggestions: List[Dict]) -> str:
    """
    Tạo markdown cho RAG chatbot.
    """
    if not suggestions:
        return 'Không tìm thấy thủ tục phù hợp với yêu cầu của bạn.'

    parts = ['**Các thủ tục hành chính phù hợp:**\n']
    for i, sug in enumerate(suggestions, 1):
        name  = sug.get('procedure_name', 'Thủ tục không rõ')
        score = sug.get('similarity_score', 0)
        link  = sug.get('link', '')
        parts.append(f'### {i}. {name}')
        if link:
            parts.append(f'[Xem chi tiết]({link})')

        reqs = sug.get('requirements', [])
        if reqs:
            required = [r for r in reqs if r.get('isRequired')]
            optional = [r for r in reqs if not r.get('isRequired')]
            parts.append('\n**Giấy tờ cần chuẩn bị:**')
            for r in required:
                parts.append(f'- ✅ **{r["docName"]}** — {r.get("docDescription", "")}')
            for r in optional:
                parts.append(f'- 📎 {r["docName"]} *(không bắt buộc)* — {r.get("docDescription", "")}')
        parts.append('')

    return '\n'.join(parts)
