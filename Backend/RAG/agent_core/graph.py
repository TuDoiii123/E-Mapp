import uuid
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import MultiRoleAgentState
from .node import (
    user_input,
    role_manager,
    cache_check,
    task_analyzer,
    tool_executor,
    llm_response,
    cache_store,
)

# ── CAG routing function ──────────────────────────────────────────────────────
def _route_cache(state: Dict[str, Any]) -> str:
    """
    Điều hướng sau cache_check:
      • 'hit'  → END   (câu trả lời đã có, bỏ qua toàn bộ pipeline LLM)
      • 'miss' → task_analyzer  (chạy pipeline đầy đủ)
    """
    return 'hit' if state.get('cache_hit') else 'miss'


class MultiRoleAgentGraph:
    """
    LangGraph với kiến trúc CAG (Cache Augmented Generation).

    Luồng đầy đủ:
      user_input_node → role_manager → cache_check
                                           ├── HIT  → END
                                           └── MISS → task_analyzer
                                                         → tool_executor
                                                           → llm_response
                                                             → cache_store
                                                               → END
    """

    def __init__(self):
        self.graph  = StateGraph(MultiRoleAgentState)
        self.memory = MemorySaver()

        # ── nodes ──────────────────────────────────────────────────────────
        self.graph.add_node("user_input_node", self._wrap_node(user_input))
        self.graph.add_node("role_manager",    self._wrap_node(role_manager))
        self.graph.add_node("cache_check",     self._wrap_node(cache_check))
        self.graph.add_node("task_analyzer",   self._wrap_node(task_analyzer))
        self.graph.add_node("tool_executor",   self._wrap_node(tool_executor))
        self.graph.add_node("llm_response",    self._wrap_node(llm_response))
        self.graph.add_node("cache_store",     self._wrap_node(cache_store))

        # ── edges (CAG flow) ────────────────────────────────────────────────
        self.graph.set_entry_point("user_input_node")
        self.graph.add_edge("user_input_node", "role_manager")
        self.graph.add_edge("role_manager",    "cache_check")

        # Conditional: cache hit → END, miss → full pipeline
        self.graph.add_conditional_edges(
            "cache_check",
            _route_cache,
            {"hit": END, "miss": "task_analyzer"},
        )

        self.graph.add_edge("task_analyzer", "tool_executor")
        self.graph.add_edge("tool_executor",  "llm_response")
        self.graph.add_edge("llm_response",   "cache_store")
        self.graph.add_edge("cache_store",    END)

        # ------------------------------------------
        # 🚀 Biên dịch đồ thị
        # ------------------------------------------
        self.app = self.graph.compile(checkpointer=self.memory)

    # ------------------------------------------
    # 📦 Gói node để LangGraph có thể xử lý được
    # ------------------------------------------
    def _wrap_node(self, func):
        """
        LangGraph yêu cầu node nhận state và trả về state.
        Trong khi node của ta chỉ cập nhật state trực tiếp (in-place),
        nên cần bọc lại để trả về state sau khi cập nhật.
        """
        def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
            func(state)
            return state
        return wrapped


    def create_new_state(self, user_question: str, session_id: str) -> MultiRoleAgentState:
        """
        Mỗi lần người dùng hỏi, tạo một state hoàn toàn mới,
        tránh dùng lại dữ liệu cũ trong bộ nhớ LangGraph.
        """
        return {
            "user_input":          user_question,
            "session_id":          session_id,
            "conversation_history": "",
            "base_prompt":         None,
            "tools":               None,
            "full_prompt":         "",
            # CAG fields
            "query_embedding":     None,
            "cache_hit":           None,
            # pipeline fields
            "llm_analysis":        None,
            "required_tools":      [],
            "tool_results":        [],
            "final_answer":        None,
        }

    # ------------------------------------------
    # 🚀 Chạy đồ thị
    # ------------------------------------------
    def run(self, state: MultiRoleAgentState) -> Dict[str, Any]:
        """
        Nhận vào 1 state (dict) và trả ra state cuối cùng sau khi chạy qua graph.
        """
        # Dùng thread_id ngẫu nhiên để tránh lưu checkpoint cũ
        thread_id = str(uuid.uuid4())

        final_state = self.app.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )

        return final_state
