# tools/tool_registry.py

"""
Bản đồ ánh xạ tên tool (dưới dạng string) với hàm Python thực tế.
Các node như tool_executor sẽ sử dụng nó để gọi hàm tương ứng.
"""

from .rag import search_project_documents
from .suggest import suggest_procedures_tool

TOOL_REGISTRY = {
    "search_project_documents": search_project_documents,
    "suggest_procedures":       suggest_procedures_tool,
}
