import os
import json
import time
import threading
import logging
from typing import Generator, List, Dict, Any

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

_QUOTA_COOLDOWN_SECS = 60  # Không thử lại key 429 trong vòng 60 giây

class _ApiKeyPool:
    """Thread-safe round-robin key pool với cooldown cho key bị 429."""

    def __init__(self):
        self._lock = threading.Lock()
        self._keys: List[str] = self._collect_keys()
        self._idx: int = 0
        # key -> timestamp khi bị 429 lần cuối
        self._exhausted_at: Dict[str, float] = {}

    def _collect_keys(self) -> List[str]:
        """
        Đọc tất cả GOOGLE_API_KEY, GOOGLE_API_KEY_1..N từ env (deduplicate).
        Thêm key mới chỉ cần đặt GOOGLE_API_KEY_4=..., GOOGLE_API_KEY_5=... trong .env.
        """
        seen, result = set(), []
        # Đọc key đánh số: GOOGLE_API_KEY_1, _2, ... đến _20
        for i in range(1, 21):
            v = os.getenv(f"GOOGLE_API_KEY_{i}", "").strip().strip('"').strip("'")
            if v and v not in seen:
                seen.add(v)
                result.append(v)
        # Fallback: GOOGLE_API_KEY không đánh số
        v = os.getenv("GOOGLE_API_KEY", "").strip().strip('"').strip("'")
        if v and v not in seen:
            seen.add(v)
            result.append(v)
        logger.info("[LLM] Loaded %d unique Gemini API key(s).", len(result))
        return result

    def _available_keys(self) -> List[str]:
        """Trả danh sách key chưa trong cooldown."""
        now = time.monotonic()
        return [
            k for k in self._keys
            if now - self._exhausted_at.get(k, 0) >= _QUOTA_COOLDOWN_SECS
        ]

    def call(self, model_name: str, call_fn) -> str:
        """Gọi call_fn(model) với auto-rotate + cooldown khi 429."""
        if not self._keys:
            raise ValueError(
                "Không có Gemini API key nào trong .env. "
                "Đặt GOOGLE_API_KEY_1 / GOOGLE_API_KEY_2 / ... hoặc GOOGLE_API_KEY."
            )

        with self._lock:
            candidates = self._available_keys()
            if not candidates:
                # Tất cả đang cooldown — thử key ít bị 429 nhất
                candidates = sorted(
                    self._keys,
                    key=lambda k: self._exhausted_at.get(k, 0)
                )

        last_exc: Exception = RuntimeError("Chưa thử key nào.")
        tried: set = set()

        for key in candidates:
            if key in tried:
                continue
            tried.add(key)
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            try:
                return call_fn(model)
            except ResourceExhausted as exc:
                last_exc = exc
                with self._lock:
                    self._exhausted_at[key] = time.monotonic()
                logger.warning(
                    "[LLM] Key ...%s hết quota (429) – thử key tiếp theo (%d/%d).",
                    key[-4:], len(tried), len(self._keys),
                )

        raise ResourceExhausted(
            "Tất cả Gemini API key đã hết quota (429). "
            "Vui lòng thêm key mới hoặc nâng cấp plan tại https://aistudio.google.com/."
        ) from last_exc

    def stream_call(self, model_name: str, prompt: str) -> Generator[str, None, None]:
        """Gọi generate_content(stream=True) với auto-rotate 429, yield từng chunk text."""
        if not self._keys:
            raise ValueError("Không có Gemini API key nào trong .env.")

        with self._lock:
            candidates = self._available_keys()
            if not candidates:
                candidates = sorted(self._keys, key=lambda k: self._exhausted_at.get(k, 0))

        last_exc: Exception = RuntimeError("Chưa thử key nào.")
        tried: set = set()

        for key in candidates:
            if key in tried:
                continue
            tried.add(key)
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            try:
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    text = getattr(chunk, 'text', None)
                    if text:
                        yield text
                return
            except ResourceExhausted as exc:
                last_exc = exc
                with self._lock:
                    self._exhausted_at[key] = time.monotonic()
                logger.warning(
                    "[LLM] Key ...%s hết quota (429) khi stream – thử key tiếp theo.",
                    key[-4:],
                )

        raise ResourceExhausted(
            "Tất cả Gemini API key đã hết quota (429)."
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

    def stream_run(self, prompt: str) -> Generator[str, None, None]:
        """Yield từng chunk text từ Gemini streaming."""
        yield from _pool.stream_call(self.model_name, prompt)


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
