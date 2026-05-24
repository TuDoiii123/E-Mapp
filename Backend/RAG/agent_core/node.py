from .state import MultiRoleAgentState
from docx import Document
from typing import List, Dict, Any
from pathlib import Path
from ..utils.llm_wrapper import (
    GeminiSynthesizerLLM,
    GeminiAnalyzerLLM,
    GeminiChatParagraphSummarizer,
)
from ..tools.tool_registry import TOOL_REGISTRY
from ..cache.semantic_cache import get_cache
import yaml
import re
import json
from ..connect_SQL.connect_SQL import connect_sql
import os
from sqlalchemy import text
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from logger import get_logger

logger = get_logger('rag.node')

# Thư mục gốc RAG (2 cấp trên so với file này: RAG/agent_core/node.py → RAG/)
_RAG_DIR = Path(__file__).parent.parent


def user_input(state: MultiRoleAgentState) -> str:
    return state["user_input"]


def _load_base_prompt(state: MultiRoleAgentState) -> str:
    path = _RAG_DIR / "prompt" / "General_Prompt.docx"
    try:
        doc = Document(str(path))
        prompt_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return prompt_text
    except FileNotFoundError:
        logger.warning(f'[RAG] General_Prompt.docx không tìm thấy tại {path} — dùng fallback prompt')
        return "Bạn là trợ lý hành chính, hỗ trợ người dân với câu trả lời rõ ràng và súc tích."
    except Exception as e:
        logger.warning(f'[RAG] Không đọc được General_Prompt.docx: {e} — dùng fallback prompt')
        return "Bạn là trợ lý hành chính, hỗ trợ người dân với câu trả lời rõ ràng và súc tích."

def _load_tool_for_role() -> List[Dict[str, Any]]:
    """
    File YAML có dạng:
    tools:
      - name: search_project_documents
        description: "Tìm kiếm dữ liệu nội bộ theo từ khóa."
        parameters:
          query:
            type: string
            required: true
            description: "Chuỗi truy vấn hoặc từ khóa mô tả thông tin cần tìm"
            example: "doanh thu Q2 2025 khu vực VN"
        returns: "Danh sách bản ghi phù hợp"
    """

    path = _RAG_DIR / "prompt" / "tool.yaml"
    try:
        if not path.is_file():
            return []
        with open(str(path), "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return []
        data = yaml.safe_load(content) or {}

        tools = data.get("tools", [])
        if not isinstance(tools, list):
            return []

        # Chuẩn hóa thông tin
        normalized_tools = []
        for tool in tools:
            normalized_tools.append({
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {}),
                "returns": tool.get("returns", "")
            })
        return normalized_tools

    except Exception:
        return []

def _load_memory(session_id: str) -> str:
    if not session_id:
        return ""

    query = text("""
        SELECT user_message, bot_response
        FROM conversation_history
        WHERE session_id = :session_id
          AND timestamp >= NOW() - INTERVAL '4 hours'
        ORDER BY timestamp DESC
        LIMIT 3
    """)

    try:
        engine = connect_sql()
        if engine is None:
            return ""
        with engine.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            rows = result.fetchall()

        formatted_history = []
        for user_msg, bot_msg in reversed(rows):
            formatted_history.append(f"User: {user_msg}")
            formatted_history.append(f"Assistant: {bot_msg}")
        return "\n".join(formatted_history)

    except Exception as e:
        logger.warning("Không thể tải memory: %s", e)
        return ""

def role_manager(state: MultiRoleAgentState) -> None:
    state["tools"] = _load_tool_for_role()
    base_prompt = _load_base_prompt(state)
    state["base_prompt"] =  base_prompt

    conversation_history = _load_memory(session_id=state.get("session_id", ""))
    if conversation_history:
        summarizer = GeminiChatParagraphSummarizer()
        summarise_conversation_history = summarizer.summarize_each_exchange(chat_json=conversation_history)
    else:
        summarise_conversation_history = ""
    state["conversation_history"] = summarise_conversation_history

    history_section = (
        f"\n---\n### LỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n{summarise_conversation_history}\n---"
        if summarise_conversation_history else ""
    )
    state["full_prompt"] = f"{base_prompt}{history_section}"
    logger.debug("Đã tải và kết hợp memory vào prompt thành công.")


def _normalize_role_tools(role_tools_raw: List[Any]) -> List[Dict[str, Any]]:
    """
    Chuẩn hoá role_tools: nếu item là str -> đổi thành {'name': str}
    Nếu item là dict và có 'name' giữ nguyên.
    """
    normalized = []
    for item in role_tools_raw or []:
        if isinstance(item, str):
            normalized.append({"name": item})
        elif isinstance(item, dict):
            if "name" in item:
                normalized.append(item)
            elif "tool_name" in item:
                item["name"] = item.pop("tool_name")
                normalized.append(item)
            else:
                continue
    return normalized

def _extract_json_from_text(text: str) -> Any:
    """
    Trích khối JSON từ văn bản trả về của LLM.
    """
    if not text:
        return None

    obj_match = re.search(r'(\{.*\})', text, flags=re.DOTALL)
    arr_match = re.search(r'(\[.*\])', text, flags=re.DOTALL)

    candidate = obj_match.group(1) if obj_match else (arr_match.group(1) if arr_match else text)

    # try direct json.loads
    try:
        return json.loads(candidate)
    except Exception:
        pass

    # sửa lỗi phổ biến: single quotes -> double quotes
    repaired = candidate.replace("'", '"')

    # remove trailing commas before } or ]
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)

    try:
        return json.loads(repaired)
    except Exception:
        return None

def _validate_and_format_required_tools(parsed_required: Any, normalized_role_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    parsed_required: parsed JSON 'required_tools' (list)
    normalized_role_tools: list of dicts with 'name' keys
    Trả về list chuẩn: [{'tool_name': name, 'params': {...}, 'available': True/False?}]
    """
    if not parsed_required:
        return []

    result = []
    available_names = {t["name"] for t in normalized_role_tools}

    for item in parsed_required:
        if isinstance(item, str):
            tool_name = item
            params = {}
        elif isinstance(item, dict):
            tool_name = item.get("tool_name") or item.get("name") or item.get("tool")
            params = item.get("params") or item.get("parameters") or {}
        else:
            continue

        if not isinstance(params, dict):
            if isinstance(params, str):
                params = {"value": params}
            else:
                params = {}

        entry = {"tool_name": tool_name, "params": params}
        if tool_name not in available_names:
            entry["available"] = False
        else:
            entry["available"] = True
        result.append(entry)

    return result


def task_analyzer(state: MultiRoleAgentState) -> None:
    """
    Node task_analyzer (in-place update).
    - Reads: state['user_question'], state['base_prompt'], state['role_tools']
    - Updates: state['llm_analysis'] (raw text) and state['required_tools'] (List[Dict])
    """
    user_question = state.get("user_input")
    base_prompt = state.get("full_prompt")
    role_tools_raw = state.get("tools", [])
    if not user_question or not base_prompt:
        raise ValueError("task_analyzer: state thiếu user_question hoặc base_prompt")

    normalized_role_tools = _normalize_role_tools(role_tools_raw)

    analyzer = GeminiAnalyzerLLM()
    raw_response = analyzer.analyze_task(base_prompt=base_prompt, user_question=user_question, role_tools=normalized_role_tools)

    state["llm_analysis"] = raw_response
    parsed = _extract_json_from_text(raw_response)
    if isinstance(parsed, dict) and "required_tools" in parsed:
        required_raw = parsed["required_tools"]
    elif isinstance(parsed, list):
        required_raw = parsed
    else:
        required_raw = []

    required_tools_normalized = _validate_and_format_required_tools(required_raw, normalized_role_tools)

    state["required_tools"] = required_tools_normalized



def tool_executor(state: MultiRoleAgentState) -> None:

    required_tools = state.get("required_tools", [])
    tool_results = []

    for tool_info in required_tools:
        tool_name = tool_info.get("tool_name") or tool_info.get("name")
        params = tool_info.get("params", {})

        if not tool_name:
            continue
        tool_func = TOOL_REGISTRY.get(tool_name)

        if not tool_func:
            tool_results.append({
                "tool_name": tool_name,
                "params": params,
                "result": None
            })
            continue

        try:
            result = tool_func(**params)
        except Exception as e:
            result = f"❌ Lỗi khi thực thi {tool_name}: {str(e)}"

        tool_results.append({"tool_name": tool_name, "params": params, "result": result})

    state["tool_results"] = tool_results

def build_synthesis_prompt(state: MultiRoleAgentState) -> str:
    """Xây dựng prompt tổng hợp từ state — dùng chung cho llm_response và streaming."""
    base_prompt = state.get("full_prompt", "")
    user_question = state.get("user_input", "")
    tool_results = state.get("tool_results", [])

    if not base_prompt or not user_question:
        raise ValueError("build_synthesis_prompt: thiếu full_prompt hoặc user_input trong state.")

    formatted_tool_results = (
        json.dumps(tool_results, ensure_ascii=False, indent=2)
        if tool_results
        else "Không có tool nào được gọi hoặc không có kết quả."
    )

    return f"""Bạn là chuyên gia hành chính công Việt Nam với kiến thức sâu rộng về mọi thủ tục, biểu mẫu, quy trình hành chính.

Câu hỏi: {user_question.strip()}

Dữ liệu tra cứu: {formatted_tool_results}

QUY TẮC BẮT BUỘC — VI PHẠM LÀ SAI:
1. Trả lời trực tiếp vào câu hỏi ngay từ câu đầu tiên. Không dẫn nhập dài dòng.
2. Dùng toàn bộ dữ liệu tra cứu được. Nếu dữ liệu thiếu, bổ sung bằng kiến thức chuyên môn về pháp luật và hành chính Việt Nam.
3. CẤM hoàn toàn các cụm từ sau (dù bất kỳ lý do gì):
   - "hệ thống chưa có" / "chưa có trong hệ thống"
   - "thông tin chưa có sẵn" / "chưa được cập nhật"
   - "tôi không tìm thấy" / "không có thông tin"
   - "bạn có thể tra cứu thêm" / "bạn có thể đến cơ quan"
   - "E-Map" / "E-Mapp" / "ứng dụng" / "hệ thống" (không tự nhắc đến tên app)
   - "tệp tài liệu" / "tài liệu hệ thống"
4. Nếu không có số liệu cụ thể: đưa ra thông tin chuẩn theo quy định chung, ghi rõ "theo quy định thông thường" hoặc "thường là".
5. Kết thúc câu trả lời gọn gàng, không kêu gọi user tự tra cứu thêm.
6. Chỉ dùng văn bản thuần — không dùng ###, **, *, ---, ```, không markdown."""


def llm_response(state: MultiRoleAgentState) -> None:
    """Node tổng hợp kết quả cuối cùng."""
    system_prompt = build_synthesis_prompt(state)
    synthesizer = GeminiSynthesizerLLM()
    state["final_answer"] = synthesizer.run(system_prompt).strip()


# ══════════════════════════════════════════════════════════════════════════════
# CAG — Cache Augmented Generation nodes
# ══════════════════════════════════════════════════════════════════════════════

def cache_check(state: MultiRoleAgentState) -> None:
    """
    CAG Node 1/2 — Kiểm tra semantic cache trước khi chạy pipeline đầy đủ.

    Luồng:
      1. Embed câu hỏi người dùng thành vector d-chiều bằng SentenceTransformer.
      2. Tính Cosine Similarity giữa vector đó và mọi entry đã cache.
      3. HIT  (similarity ≥ threshold): ghi final_answer từ cache, đặt cache_hit=True.
         → Graph sẽ nhảy thẳng đến END, bỏ qua task_analyzer / tool_executor / llm_response.
      4. MISS (similarity <  threshold): đặt cache_hit=False, lưu embedding vào state
         để cache_store tái sử dụng mà không cần embed lại.

    Tiết kiệm:
      • ~2 lần gọi Gemini API (task_analyzer + llm_response)
      • 1 lần truy vấn ChromaDB + encode SentenceTransformer
      → Giảm latency từ ~3-8 s xuống còn ~50-200 ms khi hit.
    """
    from ..tools.rag import get_embedding

    user_question = state.get("user_input", "")
    if not user_question:
        state["cache_hit"] = False
        return

    # Embed câu hỏi (SentenceTransformer local — nhanh)
    query_embedding = get_embedding(user_question)
    state["query_embedding"] = query_embedding

    if not query_embedding:
        state["cache_hit"] = False
        return

    # Tìm trong cache
    cache = get_cache()
    hit   = cache.lookup(query_embedding)

    if hit is not None:
        state["cache_hit"]    = True
        state["final_answer"] = hit.answer
        logger.info(
            '[CAG] Cache HIT — skipping task_analyzer + tool_executor + llm_response'
        )
        cache.log_stats()
    else:
        state["cache_hit"] = False
        logger.debug('[CAG] Cache MISS — proceeding with full RAG pipeline')


def cache_store(state: MultiRoleAgentState) -> None:
    """
    CAG Node 2/2 — Lưu câu trả lời mới vào semantic cache sau khi RAG hoàn thành.

    Chỉ lưu khi:
      • cache_hit == False  (kết quả vừa được sinh ra bởi LLM, chưa có trong cache)
      • final_answer không rỗng
      • query_embedding đã được tính ở cache_check (tránh embed lại)

    Sau khi lưu, in thống kê tổng hợp (hit rate, số entries) ra terminal.
    """
    if state.get("cache_hit"):
        return  # không cần lưu lại entry đã có

    answer = state.get("final_answer", "").strip()
    query  = state.get("user_input", "").strip()
    emb    = state.get("query_embedding")

    if not answer or not query:
        return

    # Nếu embedding chưa có (edge case), tính lại
    if not emb:
        from ..tools.rag import get_embedding
        emb = get_embedding(query)

    if emb:
        cache = get_cache()
        cache.store(query=query, query_embedding=emb, answer=answer)
        cache.log_stats()