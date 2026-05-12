import os
import json
import threading
import logging
from typing import List, Dict, Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

load_dotenv()

import sys as _sys
_sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent))
try:
    from config import GEMINI_MODEL_RAG as _DEFAULT_RAG_MODEL
except Exception:
    _DEFAULT_RAG_MODEL = os.getenv('GEMINI_MODEL_RAG', 'gemini-2.0-flash')

logger = logging.getLogger(__name__)


# ── API Key Pool ──────────────────────────────────────────────────────────────

class _ApiKeyPool:
    """Thread-safe round-robin key pool. Khi gặp 429 tự động rotate sang key tiếp."""

    _ENV_VARS = ("GOOGLE_API_KEY_1", "GOOGLE_API_KEY_2", "GOOGLE_API_KEY_3", "GOOGLE_API_KEY")

    def __init__(self):
        self._lock = threading.Lock()
        self._keys: List[str] = self._collect_keys()
        self._idx: int = 0

    def _collect_keys(self) -> List[str]:
        seen, result = set(), []
        for env in self._ENV_VARS:
            v = os.getenv(env, "").strip()
            if v and v not in seen:
                seen.add(v)
                result.append(v)
        return result

    def _current_key(self) -> str:
        if not self._keys:
            raise ValueError(
                "Không có Gemini API key nào trong .env. "
                "Đặt GOOGLE_API_KEY_1 / GOOGLE_API_KEY_2 / GOOGLE_API_KEY_3 hoặc GOOGLE_API_KEY."
            )
        return self._keys[self._idx % len(self._keys)]

    def _rotate(self):
        with self._lock:
            self._idx += 1

    def call(self, model_name: str, call_fn) -> str:
        """
        Gọi call_fn(model) với auto-rotate khi 429.
        Thử tất cả key trước khi raise.
        """
        n = max(len(self._keys), 1)
        last_exc: Exception = RuntimeError("Chưa thử key nào.")
        for attempt in range(n):
            with self._lock:
                key = self._current_key()
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            try:
                return call_fn(model)
            except ResourceExhausted as exc:
                last_exc = exc
                logger.warning(
                    "[LLM] Key ...%s hết quota (429) – thử key tiếp theo (%d/%d).",
                    key[-4:], attempt + 1, n,
                )
                self._rotate()
        raise ResourceExhausted(
            "Tất cả Gemini API key đã hết quota (429). "
            "Vui lòng thêm key mới hoặc nâng cấp plan tại https://aistudio.google.com/."
        ) from last_exc


_pool = _ApiKeyPool()


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_api_key(specific_env: str) -> str:
    """Giữ lại để tương thích – trả key đầu tiên có giá trị."""
    key = os.getenv(specific_env) or os.getenv("GOOGLE_API_KEY", "")
    if not key:
        raise ValueError(f"Thiếu API key: đặt {specific_env} hoặc GOOGLE_API_KEY trong .env")
    return key


# ── LLM Classes ──────────────────────────────────────────────────────────────

class GeminiAnalyzerLLM:
    """Phân tích câu hỏi, chọn tool, suy luận logic."""

    def __init__(self, model_name: str = _DEFAULT_RAG_MODEL, api_key_env: str = "GOOGLE_API_KEY_1"):
        self.model_name = model_name

    def analyze_task(
        self,
        base_prompt: str,
        user_question: str,
        role_tools: List[Dict[str, Any]],
    ) -> str:
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t.get('description', '')}\n"
            f"  Parameters: {t.get('parameters', {})}\n"
            f"  Returns: {t.get('returns', '')}"
            for t in role_tools
        ])
        system_instruction = (
            "Bạn là một AI chuyên phân tích nhiệm vụ cho hệ thống Multi-Role Agent.\n"
            "Dựa trên prompt của vai trò và danh sách tool có sẵn dưới đây, "
            "hãy chọn một hoặc nhiều tool cần dùng cho câu hỏi người dùng và xác định tham số cho từng tool.\n\n"
            "RẤT QUAN TRỌNG: Đầu ra PHẢI LÀ CHỈ MỘT đối tượng JSON hợp lệ (KHÔNG có giải thích văn bản). "
            "Schema mong muốn:\n"
            "{\n"
            "  \"analysis\": \"<mô tả ngắn về logic>\",\n"
            "  \"required_tools\": [\n"
            "    {\"tool_name\": \"<tên>\", \"params\": {<param_name>: <value>, ...}},\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "Nếu không cần gọi tool nào, trả required_tools = [].\n"
            "Ngôn ngữ trả về: nếu input là tiếng Việt thì trả bằng tiếng Việt."
        )
        example = (
            "Ví dụ JSON hợp lệ:\n"
            "{\n"
            "  \"analysis\": \"Người dùng muốn biết doanh thu Q2, cần tra DB và tóm tắt.\",\n"
            "  \"required_tools\": [\n"
            "    {\"tool_name\": \"search_database\", \"params\": {\"query\": \"doanh thu Q2 2025\", \"limit\": 10}},\n"
            "    {\"tool_name\": \"summarize_report\", \"params\": {\"file_path\": \"search_database:0\"}}\n"
            "  ]\n"
            "}\n"
        )
        prompt = (
            f"{system_instruction}\n\n"
            f"--- ROLE PROMPT ---\n{base_prompt}\n\n"
            f"--- AVAILABLE TOOLS ---\n{tool_descriptions}\n\n"
            f"--- USER QUESTION ---\n{user_question}\n\n"
            f"{example}\n"
            "TRẢ LẠI CHỈ JSON, KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC."
        )

        def _call(model):
            response = model.generate_content(prompt)
            raw_text = getattr(response, "text", None) or str(response)
            return raw_text.strip()

        return _pool.call(self.model_name, _call)


class GeminiSynthesizerLLM:
    """Tổng hợp kết quả từ tool và sinh câu trả lời cuối cùng."""

    def __init__(self, model_name: str = _DEFAULT_RAG_MODEL, api_key_env: str = "GOOGLE_API_KEY_2"):
        self.model_name = model_name

    def run(self, prompt: str) -> str:
        try:
            def _call(model):
                return model.generate_content(prompt).text
            return _pool.call(self.model_name, _call)
        except Exception as e:
            logger.error("[GeminiSynthesizerLLM] Lỗi: %s", e)
            return "Lỗi"


class GeminiChatParagraphSummarizer:
    """Tóm tắt từng cặp hội thoại (user – chatbot)."""

    def __init__(self, model_name: str = _DEFAULT_RAG_MODEL, api_key_env: str = "GOOGLE_API_KEY_3"):
        self.model_name = model_name

    def summarize_each_exchange(self, chat_json: list) -> str:
        chat_data = json.dumps(chat_json, ensure_ascii=False, indent=2)
        system_prompt = f"""
        Bạn là một chuyên gia ngôn ngữ có nhiệm vụ viết lại từng cặp hội thoại giữa người dùng và chatbot
        thành các đoạn văn ngắn, dễ hiểu, mô tả nội dung trao đổi của từng lượt.

        ### Dữ liệu hội thoại
        {chat_data}

        ### Yêu cầu
        - Mỗi cặp {{user, chatbot}} được viết thành **một đoạn văn riêng** (xuống dòng giữa các đoạn).
        - Diễn đạt tự nhiên, tóm tắt ý chính của cả người dùng và chatbot.
        - Không thêm số thứ tự, không dùng gạch đầu dòng.
        - Đầu ra chỉ là các đoạn văn, không kèm ký hiệu hay chú thích khác.
        """

        def _call(model):
            response = model.generate_content(system_prompt)
            raw_text = getattr(response, "text", None) or str(response)
            return raw_text.strip()

        try:
            return _pool.call(self.model_name, _call)
        except ResourceExhausted as e:
            logger.error("[GeminiChatParagraphSummarizer] Tất cả key hết quota: %s", e)
            return ""
        except Exception as e:
            logger.error("[GeminiChatParagraphSummarizer] Lỗi: %s", e)
            return ""
