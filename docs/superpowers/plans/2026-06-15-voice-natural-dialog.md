# Voice Natural Dialog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Làm hội thoại đặt lịch của `ai_voice_backend` nói chuyện tự nhiên hơn (diễn đạt ấm áp/biến hóa, xử lý đổi ý + tán gẫu + hỏi thủ tục grounded bằng RAG) trong khi phần đặt lịch giữ deterministic.

**Architecture:** Tách "sự thật" (FSM deterministic quyết định, sở hữu slot/mã lịch/booking) khỏi "câu chữ" (lớp NLG dùng Gemini diễn đạt). FSM trả về `DialogAction` có cấu trúc; `ResponseGenerator` biến action+facts thành câu tiếng Việt tự nhiên, có guardrail hậu kiểm và template fallback khi LLM lỗi/tắt.

**Tech Stack:** Python, Gemini (`google.generativeai`), ChromaDB RAG có sẵn (`RAG.tools.rag.search_project_documents`), pytest 7.4.3.

---

## File Structure

| File | Trách nhiệm |
|---|---|
| `Backend/ai_voice_backend/dialog_action.py` | **MỚI** — `ActionType` + `DialogAction` dataclass (module riêng, tránh import vòng) |
| `Backend/ai_voice_backend/rag_bridge.py` | **MỚI** — wrapper lazy gọi RAG, an toàn lỗi |
| `Backend/ai_voice_backend/response_generator.py` | **MỚI** — NLG: template fallback + guardrail + gọi Gemini |
| `Backend/ai_voice_backend/dialog_manager.py` | **SỬA** — trả `DialogAction`, `_recompute_step`, định tuyến off-script, phát hiện đổi ý, gọi NLG trong `process()` |
| `Backend/ai_voice_backend/nlu.py` | **SỬA** — mở rộng whitelist intent |
| `Backend/ai_voice_backend/config.py` | **SỬA** — `VOICE_NLG_ENABLED` |
| `Backend/ai_voice_backend/test_dialog_action.py` | **MỚI** — test |
| `Backend/ai_voice_backend/test_rag_bridge.py` | **MỚI** — test |
| `Backend/ai_voice_backend/test_response_generator.py` | **MỚI** — test |
| `Backend/ai_voice_backend/test_dialog_core.py` | **MỚI** — test FSM deterministic + off-script + đổi ý |

**Lệnh test (chạy từ thư mục `Backend/`):**
`python -m pytest ai_voice_backend/ -q`

---

## Task 1: `dialog_action.py` — kiểu action có cấu trúc

**Files:**
- Create: `Backend/ai_voice_backend/dialog_action.py`
- Test: `Backend/ai_voice_backend/test_dialog_action.py`

- [ ] **Step 1: Write the failing test**

```python
# Backend/ai_voice_backend/test_dialog_action.py
from ai_voice_backend.dialog_action import ActionType, DialogAction


def test_action_defaults_to_empty_facts():
    a = DialogAction(ActionType.ASK_DATE)
    assert a.type == 'ASK_DATE'
    assert a.facts == {}


def test_action_carries_facts():
    a = DialogAction(ActionType.OFFER_SLOTS, {'slots': ['08:00', '09:00']})
    assert a.facts['slots'] == ['08:00', '09:00']


def test_all_action_types_are_unique_strings():
    names = [v for k, v in vars(ActionType).items() if not k.startswith('_')]
    assert len(names) == len(set(names))
    assert 'BOOKING_SUCCESS' in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_dialog_action.py -q`
Expected: FAIL — `ModuleNotFoundError: ai_voice_backend.dialog_action`

- [ ] **Step 3: Write minimal implementation**

```python
# Backend/ai_voice_backend/dialog_action.py
"""
DialogAction — "ý định giao tiếp" có cấu trúc do FSM xuất ra.

Tách "sự thật" (loại action + facts) khỏi "câu chữ" (do ResponseGenerator sinh).
Đặt ở module riêng để dialog_manager và response_generator cùng import mà không vòng.
"""
from dataclasses import dataclass, field
from typing import Any, Dict


class ActionType:
    GREET            = 'GREET'
    ASK_INTENT       = 'ASK_INTENT'
    ASK_LOCATION     = 'ASK_LOCATION'
    ASK_DATE         = 'ASK_DATE'
    OFFER_SLOTS      = 'OFFER_SLOTS'
    NO_SLOTS         = 'NO_SLOTS'
    ASK_TIME_AGAIN   = 'ASK_TIME_AGAIN'
    CONFIRM_DETAILS  = 'CONFIRM_DETAILS'
    SLOT_TAKEN       = 'SLOT_TAKEN'
    BOOKING_SUCCESS  = 'BOOKING_SUCCESS'
    BOOKING_ERROR    = 'BOOKING_ERROR'
    ANSWER_PROCEDURE = 'ANSWER_PROCEDURE'
    SMALL_TALK       = 'SMALL_TALK'
    CANCELLED        = 'CANCELLED'
    ALREADY_DONE     = 'ALREADY_DONE'


@dataclass
class DialogAction:
    type:  str
    facts: Dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_dialog_action.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/dialog_action.py Backend/ai_voice_backend/test_dialog_action.py
git commit -m "feat(voice): thêm DialogAction có cấu trúc"
```

---

## Task 2: `rag_bridge.py` — wrapper RAG an toàn lỗi

**Files:**
- Create: `Backend/ai_voice_backend/rag_bridge.py`
- Test: `Backend/ai_voice_backend/test_rag_bridge.py`

Mục tiêu: gọi `RAG.tools.rag.search_project_documents` một cách lazy; mọi lỗi (import nặng, model chưa tải, exception) → trả `[]`, không bao giờ ném ra ngoài.

- [ ] **Step 1: Write the failing test**

```python
# Backend/ai_voice_backend/test_rag_bridge.py
from ai_voice_backend import rag_bridge


def test_empty_query_returns_empty(monkeypatch):
    assert rag_bridge.search('') == []
    assert rag_bridge.search('   ') == []


def test_search_delegates_to_rag(monkeypatch):
    monkeypatch.setattr(rag_bridge, '_load_search',
                        lambda: (lambda q: ['Cần CMND cũ và sổ hộ khẩu.']))
    out = rag_bridge.search('làm căn cước cần gì')
    assert out == ['Cần CMND cũ và sổ hộ khẩu.']


def test_search_swallows_errors(monkeypatch):
    def boom():
        raise RuntimeError('model not ready')
    monkeypatch.setattr(rag_bridge, '_load_search', boom)
    assert rag_bridge.search('bất kỳ') == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_rag_bridge.py -q`
Expected: FAIL — `ModuleNotFoundError: ai_voice_backend.rag_bridge`

- [ ] **Step 3: Write minimal implementation**

```python
# Backend/ai_voice_backend/rag_bridge.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_rag_bridge.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/rag_bridge.py Backend/ai_voice_backend/test_rag_bridge.py
git commit -m "feat(voice): rag_bridge lazy + an toàn lỗi"
```

---

## Task 3: `config.py` — cờ bật/tắt NLG

**Files:**
- Modify: `Backend/ai_voice_backend/config.py` (sau khối `# ── Dialog ──`)

- [ ] **Step 1: Add config flag**

Thêm vào cuối khối Dialog trong `config.py`:

```python
# ── NLG (sinh câu trả lời tự nhiên) ─────────────────────────────────────────
# Bật: dùng Gemini diễn đạt câu trả lời tự nhiên. Tắt: dùng template cố định.
VOICE_NLG_ENABLED = os.getenv('VOICE_NLG_ENABLED', '1') == '1'
```

- [ ] **Step 2: Verify import**

Run (từ `Backend/`): `python -c "from ai_voice_backend.config import VOICE_NLG_ENABLED; print(VOICE_NLG_ENABLED)"`
Expected: `True`

- [ ] **Step 3: Commit**

```bash
git add Backend/ai_voice_backend/config.py
git commit -m "feat(voice): thêm cờ VOICE_NLG_ENABLED"
```

---

## Task 4: `response_generator.py` — template fallback

**Files:**
- Create: `Backend/ai_voice_backend/response_generator.py`
- Test: `Backend/ai_voice_backend/test_response_generator.py`

Xây phần fallback trước (deterministic, không LLM) — đây cũng là lưới an toàn khi Gemini lỗi.

- [ ] **Step 1: Write the failing test**

```python
# Backend/ai_voice_backend/test_response_generator.py
from ai_voice_backend.dialog_action import ActionType, DialogAction
from ai_voice_backend.response_generator import ResponseGenerator


def _gen():
    # enabled=False → luôn dùng template, không gọi Gemini
    return ResponseGenerator(enabled=False)


def test_fallback_ask_date():
    out = _gen().generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert 'ngày' in out.lower()


def test_fallback_offer_slots_lists_times():
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'location': 'UBND Hoàn Kiếm',
                      'slots': ['08:00', '09:00']})
    out = _gen().generate(a, 'ngày mai', [])
    assert '08:00' in out and '09:00' in out


def test_fallback_booking_success_has_code_and_queue():
    a = DialogAction(ActionType.BOOKING_SUCCESS,
                     {'service': 'Làm căn cước', 'location': 'UBND Hoàn Kiếm',
                      'date': '01/07/2026', 'time': '09:00',
                      'code': 'AP-123', 'queue': '7'})
    out = _gen().generate(a, 'xác nhận', [])
    assert 'AP-123' in out and '7' in out


def test_fallback_answer_procedure_uses_snippets():
    a = DialogAction(ActionType.ANSWER_PROCEDURE,
                     {'snippets': ['Cần CMND cũ và sổ hộ khẩu.'],
                      'steer': 'Bạn muốn đặt lịch ngày nào?'})
    out = _gen().generate(a, 'cần giấy gì', [])
    assert 'CMND' in out
    assert 'ngày nào' in out


def test_fallback_answer_procedure_empty_snippets():
    a = DialogAction(ActionType.ANSWER_PROCEDURE,
                     {'snippets': [], 'steer': 'Bạn muốn làm thủ tục gì?'})
    out = _gen().generate(a, 'hỏi linh tinh', [])
    assert 'chưa có thông tin' in out.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q`
Expected: FAIL — `ModuleNotFoundError: ai_voice_backend.response_generator`

- [ ] **Step 3: Write minimal implementation**

```python
# Backend/ai_voice_backend/response_generator.py
"""
ResponseGenerator (NLG) — biến DialogAction + facts thành câu tiếng Việt tự nhiên.

Thứ tự ưu tiên:
  1. enabled=False hoặc Gemini lỗi → template fallback (deterministic).
  2. Gemini OK → câu tự nhiên, sau đó qua guardrail hậu kiểm.

Guardrail: facts được bơm vào prompt; số/mã/giờ quan trọng bị thiếu trong câu LLM
sẽ được nối thêm dòng deterministic (xem Task 5).
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from .dialog_action import ActionType, DialogAction
from .config import VOICE_NLG_ENABLED

log = get_logger('voice.nlg')


class ResponseGenerator:
    def __init__(self, enabled: Optional[bool] = None) -> None:
        self._enabled = VOICE_NLG_ENABLED if enabled is None else enabled
        self._model = None

    def generate(self, action: DialogAction, user_text: str,
                 history: Optional[List[Dict]] = None) -> str:
        reply = ''
        if self._enabled:
            reply = self._call_gemini(action, user_text, history or [])
        if not reply:
            reply = self._fallback(action)
        return reply

    # ── template fallback ──────────────────────────────────────────────────
    def _fallback(self, action: DialogAction) -> str:
        f = action.facts
        t = action.type
        if t == ActionType.GREET:
            return ('Xin chào! Tôi là trợ lý đặt lịch hành chính. '
                    'Bạn muốn làm thủ tục gì?')
        if t == ActionType.ASK_INTENT:
            return 'Bạn muốn làm thủ tục gì? Ví dụ: làm căn cước, đăng ký khai sinh.'
        if t == ActionType.ASK_LOCATION:
            return 'Bạn muốn đến cơ quan nào? Ví dụ: UBND quận Hoàn Kiếm.'
        if t == ActionType.ASK_DATE:
            return 'Bạn muốn đặt lịch ngày nào?'
        if t == ActionType.OFFER_SLOTS:
            times = ', '.join(f.get('slots', []))
            return (f"Ngày {f.get('date','')} tại {f.get('location','')} còn trống "
                    f"các khung giờ: {times}. Bạn muốn chọn giờ nào?")
        if t == ActionType.NO_SLOTS:
            return (f"Ngày {f.get('date','')} tại {f.get('location','')} không còn "
                    f"khung giờ trống. Bạn chọn ngày khác nhé?")
        if t == ActionType.ASK_TIME_AGAIN:
            times = ', '.join(f.get('slots', []))
            return f'Bạn vui lòng chọn một trong các khung giờ: {times}.'
        if t == ActionType.SLOT_TAKEN:
            times = ', '.join(f.get('slots', []))
            return f'Khung giờ đó không còn trống. Vui lòng chọn lại: {times}.'
        if t == ActionType.CONFIRM_DETAILS:
            return (f"Xác nhận: {f.get('service','')} tại {f.get('location','')}, "
                    f"ngày {f.get('date','')} lúc {f.get('time','')}. "
                    f"Bạn xác nhận chứ? (Có / Không)")
        if t == ActionType.BOOKING_SUCCESS:
            return (f"Đặt lịch thành công! {f.get('service','')} tại "
                    f"{f.get('location','')}, ngày {f.get('date','')} lúc {f.get('time','')}. "
                    f"Mã lịch {f.get('code','')}, số thứ tự {f.get('queue','')}. "
                    f"Hẹn gặp bạn nhé!")
        if t == ActionType.BOOKING_ERROR:
            return (f"Xin lỗi, chưa đặt được lịch: {f.get('error','')}. "
                    f"Bạn muốn thử thời gian khác không?")
        if t == ActionType.ANSWER_PROCEDURE:
            snippets = f.get('snippets', [])
            steer = f.get('steer', '')
            if not snippets:
                return ('Xin lỗi, mình chưa có thông tin về việc đó. ' + steer).strip()
            return (snippets[0] + ' ' + steer).strip()
        if t == ActionType.SMALL_TALK:
            return ('Mình ở đây để giúp bạn đặt lịch hành chính. '
                    + f.get('steer', '')).strip()
        if t == ActionType.CANCELLED:
            return 'Đã hủy phiên đặt lịch. Khi cần bạn cứ bắt đầu lại nhé.'
        if t == ActionType.ALREADY_DONE:
            return ('Lịch hẹn đã đặt xong trước đó. Nếu muốn đặt lịch mới, '
                    'hãy cho mình biết thủ tục bạn cần.')
        return 'Xin lỗi, đã có lỗi xảy ra. Bạn thử lại giúp mình nhé.'

    # ── Gemini (đặt stub ở Task 6) ─────────────────────────────────────────
    def _call_gemini(self, action: DialogAction, user_text: str,
                     history: List[Dict]) -> str:
        return ''  # tạm thời: chưa gọi LLM (Task 6 sẽ cài)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/response_generator.py Backend/ai_voice_backend/test_response_generator.py
git commit -m "feat(voice): ResponseGenerator template fallback"
```

---

## Task 5: Guardrail hậu kiểm số liệu

**Files:**
- Modify: `Backend/ai_voice_backend/response_generator.py`
- Test: `Backend/ai_voice_backend/test_response_generator.py` (thêm test)

Đảm bảo mã lịch / số thứ tự / khung giờ luôn có mặt trong câu cuối, kể cả khi LLM bỏ sót.

- [ ] **Step 1: Write the failing test (thêm vào cuối file test)**

```python
from ai_voice_backend.response_generator import ResponseGenerator as _RG


def test_guardrail_appends_missing_booking_code():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.BOOKING_SUCCESS,
                     {'service': 'Làm căn cước', 'location': 'UBND',
                      'date': '01/07/2026', 'time': '09:00',
                      'code': 'AP-999', 'queue': '12'})
    # giả lập câu LLM bỏ sót mã + số thứ tự
    fixed = g._guardrail(a, 'Đặt lịch thành công, hẹn gặp bạn!')
    assert 'AP-999' in fixed and '12' in fixed


def test_guardrail_appends_missing_slots():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'location': 'UBND',
                      'slots': ['08:00', '09:00']})
    fixed = g._guardrail(a, 'Còn vài khung giờ trống bạn nhé.')
    assert '08:00' in fixed and '09:00' in fixed


def test_guardrail_noop_when_facts_present():
    g = _RG(enabled=False)
    a = DialogAction(ActionType.BOOKING_SUCCESS, {'code': 'AP-1', 'queue': '3'})
    reply = 'Xong rồi, mã AP-1, số thứ tự 3 nhé.'
    assert g._guardrail(a, reply) == reply
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q -k guardrail`
Expected: FAIL — `AttributeError: ... has no attribute '_guardrail'`

- [ ] **Step 3: Implement guardrail + gọi trong generate()**

Thêm method vào `ResponseGenerator` và gọi nó ở cuối `generate`:

```python
    def generate(self, action: DialogAction, user_text: str,
                 history: Optional[List[Dict]] = None) -> str:
        reply = ''
        if self._enabled:
            reply = self._call_gemini(action, user_text, history or [])
        if not reply:
            reply = self._fallback(action)
        return self._guardrail(action, reply)

    def _guardrail(self, action: DialogAction, reply: str) -> str:
        """Bảo đảm số/mã/giờ quan trọng có mặt; thiếu → nối thêm dòng deterministic."""
        f = action.facts
        missing: List[str] = []
        if action.type == ActionType.BOOKING_SUCCESS:
            code, queue = str(f.get('code', '')), str(f.get('queue', ''))
            if code and code not in reply:
                missing.append(f'Mã lịch: {code}')
            if queue and queue not in reply:
                missing.append(f'Số thứ tự: {queue}')
        elif action.type == ActionType.OFFER_SLOTS:
            absent = [s for s in f.get('slots', []) if s not in reply]
            if absent:
                missing.append('Các khung giờ: ' + ', '.join(absent))
        if missing:
            reply = reply.rstrip('. ') + '. ' + '. '.join(missing) + '.'
        return reply
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/response_generator.py Backend/ai_voice_backend/test_response_generator.py
git commit -m "feat(voice): guardrail hậu kiểm số liệu trong NLG"
```

---

## Task 6: Gọi Gemini sinh câu tự nhiên

**Files:**
- Modify: `Backend/ai_voice_backend/response_generator.py`
- Test: `Backend/ai_voice_backend/test_response_generator.py` (thêm test)

- [ ] **Step 1: Write the failing test**

```python
def test_uses_gemini_reply_when_enabled(monkeypatch):
    g = _RG(enabled=True)
    monkeypatch.setattr(g, '_call_gemini',
                        lambda action, user_text, history: 'Dạ, bạn muốn ngày nào ạ?')
    out = g.generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert out == 'Dạ, bạn muốn ngày nào ạ?'


def test_falls_back_when_gemini_returns_empty(monkeypatch):
    g = _RG(enabled=True)
    monkeypatch.setattr(g, '_call_gemini', lambda action, user_text, history: '')
    out = g.generate(DialogAction(ActionType.ASK_DATE), 'ờ', [])
    assert 'ngày' in out.lower()


def test_build_prompt_includes_facts_and_user_text():
    g = _RG(enabled=True)
    a = DialogAction(ActionType.OFFER_SLOTS,
                     {'date': '01/07/2026', 'slots': ['08:00']})
    prompt = g._build_prompt(a, 'ngày mai nhé', [])
    assert '08:00' in prompt and 'ngày mai nhé' in prompt
    assert 'OFFER_SLOTS' in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q -k "gemini or prompt"`
Expected: FAIL — `AttributeError: ... '_build_prompt'`

- [ ] **Step 3: Implement `_build_prompt` + `_call_gemini`**

Thay thân `_call_gemini` (stub ở Task 4) và thêm `_build_prompt`:

```python
    _SYSTEM = (
        'Bạn là trợ lý đặt lịch hành chính công, nói chuyện qua GIỌNG NÓI với người dân.\n'
        'Nhiệm vụ: viết MỘT câu trả lời tiếng Việt tự nhiên, thân thiện, NGẮN GỌN '
        '(tối đa 2 câu), dựa trên Ý ĐỊNH và DỮ LIỆU bên dưới.\n'
        'QUY TẮC BẮT BUỘC:\n'
        '- Chỉ dùng số/mã/giờ/ngày có trong DỮ LIỆU. TUYỆT ĐỐI không bịa thêm.\n'
        '- Nếu hợp lý, thừa nhận ngắn gọn điều người dùng vừa nói.\n'
        '- Không markdown, không gạch đầu dòng, không emoji. Chỉ trả về câu nói.\n'
    )

    def _build_prompt(self, action: DialogAction, user_text: str,
                      history: List[Dict]) -> str:
        import json
        hist = '\n'.join(f'  [{h["role"]}]: {h["content"]}' for h in history[-4:]) \
            or '(chưa có)'
        facts = json.dumps(action.facts, ensure_ascii=False)
        return (
            f'{self._SYSTEM}\n'
            f'Ý ĐỊNH: {action.type}\n'
            f'DỮ LIỆU: {facts}\n'
            f'Lịch sử gần đây:\n{hist}\n'
            f'Người dùng vừa nói: "{user_text}"\n\n'
            f'Câu trả lời:'
        )

    def _call_gemini(self, action: DialogAction, user_text: str,
                     history: List[Dict]) -> str:
        from .config import GEMINI_API_KEY, GEMINI_MODEL
        if not GEMINI_API_KEY:
            return ''
        try:
            import google.generativeai as genai  # type: ignore
            if self._model is None:
                genai.configure(api_key=GEMINI_API_KEY)
                self._model = genai.GenerativeModel(GEMINI_MODEL)
            resp = self._model.generate_content(
                self._build_prompt(action, user_text, history))
            return (getattr(resp, 'text', None) or '').strip()
        except Exception as e:  # noqa: BLE001
            log.debug(f'[NLG][Gemini] {e}')
            return ''
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_response_generator.py -q`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/response_generator.py Backend/ai_voice_backend/test_response_generator.py
git commit -m "feat(voice): NLG gọi Gemini sinh câu tự nhiên"
```

---

## Task 7: Mở rộng whitelist intent trong NLU

**Files:**
- Modify: `Backend/ai_voice_backend/nlu.py` (`Intent` class + `_parse_gemini_response`)
- Test: `Backend/ai_voice_backend/test_dialog_core.py` (tạo file, test phần NLU trước)

- [ ] **Step 1: Write the failing test**

```python
# Backend/ai_voice_backend/test_dialog_core.py
from ai_voice_backend.nlu import NLUEngine, Intent


def test_query_procedure_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'QUERY_PROCEDURE', 'entities': {}})
    assert res.intent == Intent.QUERY_PROCEDURE


def test_greeting_intent_preserved():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'GREETING', 'entities': {}})
    assert res.intent == Intent.GREETING


def test_unknown_intent_falls_back():
    nlu = NLUEngine()
    res = nlu._parse_gemini_response({'intent': 'XYZ', 'entities': {}})
    assert res.intent == Intent.UNKNOWN
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q`
Expected: FAIL — `AttributeError: type object 'Intent' has no attribute 'QUERY_PROCEDURE'`

- [ ] **Step 3: Implement**

Trong `nlu.py`, thêm vào class `Intent`:

```python
    QUERY_PROCEDURE  = 'QUERY_PROCEDURE'
    GREETING         = 'GREETING'
    SMALL_TALK       = 'SMALL_TALK'
```

Trong `_parse_gemini_response`, mở rộng `valid_intents`:

```python
        valid_intents = {
            Intent.BOOK_APPOINTMENT, Intent.QUERY_SERVICE, Intent.QUERY_PROCEDURE,
            Intent.CONFIRM, Intent.DENY, Intent.CANCEL,
            Intent.GREETING, Intent.SMALL_TALK, Intent.UNKNOWN,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/nlu.py Backend/ai_voice_backend/test_dialog_core.py
git commit -m "feat(voice): NLU giữ intent QUERY_PROCEDURE/GREETING/SMALL_TALK"
```

---

## Task 8: FSM trả `DialogAction` + `_recompute_step` (lõi deterministic)

**Files:**
- Modify: `Backend/ai_voice_backend/dialog_manager.py`
- Test: `Backend/ai_voice_backend/test_dialog_core.py` (thêm test)

Đây là task trọng tâm. Refactor `_dispatch` để **trả `DialogAction`** (không ghép reply), và thay đẩy bước tuyến tính bằng `_recompute_step`. `process()` tạm thời dùng `_fallback` để ráp reply (Task 10 nối NLG).

- [ ] **Step 1: Write the failing test**

```python
from ai_voice_backend.dialog_manager import DialogManager, Step
from ai_voice_backend.nlu import NLUResult, Entities, Intent
from ai_voice_backend.dialog_action import ActionType


def _dm():
    dm = DialogManager()
    return dm


def test_recompute_step_missing_service():
    dm = _dm()
    e = Entities()
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.COLLECT_INTENT


def test_recompute_step_missing_date():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND Hoàn Kiếm')
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.COLLECT_DATE


def test_recompute_step_ready_for_slots_when_no_cached_slots():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND',
                 appointment_date='2026-07-01', appointment_time='09:00:00')
    assert dm._recompute_step(e, {'suggested_slots': []}) == Step.SUGGEST_SLOTS


def test_recompute_step_confirm_when_all_present():
    dm = _dm()
    e = Entities(service_type='Làm căn cước', location='UBND',
                 appointment_date='2026-07-01', appointment_time='09:00:00')
    assert dm._recompute_step(e, {'suggested_slots': ['09:00:00']}) == Step.CONFIRM


def test_dispatch_ask_date_returns_action():
    dm = _dm()
    state = dm._init_state()
    state['entities'] = Entities(service_type='Làm căn cước',
                                 location='UBND Hoàn Kiếm').to_dict()
    nlu = NLUResult(intent=Intent.BOOK_APPOINTMENT, entities=Entities())
    action = dm._dispatch('s1', state, nlu, 'tôi muốn làm căn cước ở Hoàn Kiếm')
    assert action.type == ActionType.ASK_DATE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q -k "recompute or dispatch"`
Expected: FAIL — `AttributeError: ... '_recompute_step'` / `_dispatch` trả `DialogResponse` không có `.type`

- [ ] **Step 3: Implement**

Trong `dialog_manager.py`:

(a) Thêm import ở đầu file:

```python
from .dialog_action import ActionType, DialogAction
```

(b) Thêm method `_recompute_step`:

```python
    def _recompute_step(self, entities: Entities, state: Dict) -> str:
        if not entities.service_type:
            return Step.COLLECT_INTENT
        if not entities.location:
            return Step.COLLECT_LOCATION
        if not entities.appointment_date:
            return Step.COLLECT_DATE
        if not state.get('suggested_slots'):
            return Step.SUGGEST_SLOTS
        if not entities.appointment_time:
            return Step.SUGGEST_SLOTS
        return Step.CONFIRM
```

(c) Thay toàn bộ `_dispatch` bằng phiên bản trả `DialogAction`:

```python
    def _dispatch(self, session_id: str, state: Dict, nlu: NLUResult,
                  user_text: str) -> DialogAction:
        entities: Entities = Entities.from_dict(state['entities'])
        state['step'] = self._recompute_step(entities, state)
        step = state['step']

        if step == Step.COLLECT_INTENT:
            return DialogAction(ActionType.ASK_INTENT)
        if step == Step.COLLECT_LOCATION:
            return DialogAction(ActionType.ASK_LOCATION)
        if step == Step.COLLECT_DATE:
            return DialogAction(ActionType.ASK_DATE)

        if step == Step.SUGGEST_SLOTS:
            slots = self._get_slots(entities.location, entities.appointment_date)
            d_str = self._fmt_date(entities.appointment_date)
            if not slots:
                state['suggested_slots'] = []
                return DialogAction(ActionType.NO_SLOTS,
                                    {'date': d_str, 'location': entities.location})
            state['suggested_slots'] = slots
            short = [s[:5] for s in slots]
            return DialogAction(ActionType.OFFER_SLOTS,
                                {'date': d_str, 'location': entities.location,
                                 'slots': short})

        if step == Step.CONFIRM:
            slots = state.get('suggested_slots', [])
            short = [s[:5] for s in slots]
            chosen = entities.appointment_time
            if chosen and slots and chosen not in slots:
                matched = next((s for s in slots if s.startswith(chosen[:5])), None)
                if matched:
                    chosen = matched
                    state['entities']['appointment_time'] = matched
                    entities = Entities.from_dict(state['entities'])
                else:
                    return DialogAction(ActionType.SLOT_TAKEN, {'slots': short})
            if nlu.intent != Intent.CONFIRM and not state.get('confirmed'):
                return DialogAction(ActionType.CONFIRM_DETAILS, {
                    'service': entities.service_type, 'location': entities.location,
                    'date': self._fmt_date(entities.appointment_date),
                    'time': (chosen or '')[:5]})
            state['confirmed'] = True
            return self._create_appointment_action(session_id, state, entities)

        return DialogAction(ActionType.ASK_INTENT)
```

(d) Đổi tên + kiểu trả của `_create_appointment` thành `_create_appointment_action` trả `DialogAction`. Giữ nguyên logic gọi `create_appointment`, chỉ đổi phần `return`:

```python
    def _create_appointment_action(self, session_id: str, state: Dict,
                                    entities: Entities) -> DialogAction:
        try:
            from services.appointments import create_appointment
            svc_code = self._service_code(entities.service_type or '')
            agency_id = self._agency_id(entities.location or '')
            raw_time = entities.appointment_time or '09:00:00'
            from datetime import datetime as _dt
            for fmt in ('%H:%M:%S', '%H:%M', '%H'):
                try:
                    hhmm = _dt.strptime(raw_time, fmt).strftime('%H:%M'); break
                except ValueError:
                    continue
            else:
                hhmm = raw_time[:5] if len(raw_time) >= 5 else '09:00'
            ok, appt, err = create_appointment({
                'agencyId': agency_id, 'serviceCode': svc_code,
                'date': entities.appointment_date, 'time': hhmm,
                'phone': entities.phone, 'fullName': entities.citizen_name or 'Người dân',
                'info': entities.note or 'Đặt lịch qua voice AI'})
        except Exception as e:
            log.error(f'[Dialog] create_appointment error: {e}', exc_info=True)
            state['step'] = Step.CONFIRM
            return DialogAction(ActionType.BOOKING_ERROR, {'error': str(e)})
        if not ok:
            state['step'] = Step.COLLECT_DATE
            state['suggested_slots'] = []
            return DialogAction(ActionType.BOOKING_ERROR, {'error': err or 'lỗi'})
        state['step'] = Step.DONE
        state['appointment'] = appt
        log.info(f'[Dialog][{session_id}] appointment created: {appt.get("id")}')
        return DialogAction(ActionType.BOOKING_SUCCESS, {
            'service': entities.service_type, 'location': entities.location,
            'date': self._fmt_date(entities.appointment_date), 'time': hhmm,
            'code': appt.get('id', 'N/A'), 'queue': appt.get('queueNumber', 'N/A')})
```

(e) `process()` tạm ráp reply bằng fallback (Task 10 thay bằng NLG). Sửa phần cuối `process()`:

```python
        action = self._dispatch(session_id, state, nlu, user_text)
        from .response_generator import ResponseGenerator
        if not hasattr(self, '_nlg'):
            self._nlg = ResponseGenerator()
        reply = self._nlg.generate(action, user_text, state.get('history', []))

        history.append({'role': 'bot', 'content': reply})
        state['history'] = history[-10:]
        self._store.set(session_id, state)
        return DialogResponse(
            reply=reply, step=state['step'],
            done=(state['step'] == Step.DONE),
            appointment=state.get('appointment'),
            slots=state.get('suggested_slots', []), state=state)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/dialog_manager.py Backend/ai_voice_backend/test_dialog_core.py
git commit -m "feat(voice): FSM trả DialogAction + recompute_step"
```

---

## Task 9: Định tuyến off-script + phát hiện đổi ý

**Files:**
- Modify: `Backend/ai_voice_backend/dialog_manager.py` (`process()`)
- Test: `Backend/ai_voice_backend/test_dialog_core.py` (thêm test)

- [ ] **Step 1: Write the failing test**

```python
import types
from ai_voice_backend import dialog_manager as DM


def _force_nlu(dm, intent, entities):
    dm._nlu.analyze = lambda text, history=None: NLUResult(intent=intent, entities=entities)


def test_procedure_question_keeps_step_and_uses_rag(monkeypatch):
    from ai_voice_backend.response_generator import ResponseGenerator
    monkeypatch.setattr(DM, 'rag_search', lambda q: ['Cần CMND cũ và sổ hộ khẩu.'],
                        raising=False)
    dm = DialogManager()
    dm._nlg = ResponseGenerator(enabled=False)   # template, không gọi Gemini
    sid = 'p1'
    dm.reset(sid)
    # đã có service → bước hiện tại phải là hỏi địa điểm
    st = dm._init_state(); st['entities'] = Entities(service_type='Làm căn cước').to_dict()
    dm._store.set(sid, st)
    _force_nlu(dm, Intent.QUERY_PROCEDURE, Entities())
    resp = dm.process(sid, 'làm căn cước cần giấy gì')
    # vẫn ở COLLECT_LOCATION (không bị đẩy bước), reply có nội dung RAG
    assert dm._store.get(sid)['step'] == Step.COLLECT_LOCATION
    assert 'CMND' in resp.reply


def test_change_of_mind_resets_and_refetches(monkeypatch):
    from ai_voice_backend.response_generator import ResponseGenerator
    dm = DialogManager()
    dm._nlg = ResponseGenerator(enabled=False)
    monkeypatch.setattr(dm, '_get_slots', lambda loc, date: ['08:00:00'])  # slot mới
    sid = 'c1'; dm.reset(sid)
    st = dm._init_state()
    st['entities'] = Entities(service_type='Làm căn cước', location='UBND',
                              appointment_date='2026-07-01',
                              appointment_time='09:00:00').to_dict()
    st['suggested_slots'] = ['09:00:00']; st['confirmed'] = True
    st['step'] = Step.CONFIRM
    dm._store.set(sid, st)
    # người dùng đổi sang ngày khác → phải reset confirm + lấy slot mới
    _force_nlu(dm, Intent.BOOK_APPOINTMENT, Entities(appointment_date='2026-07-05'))
    dm.process(sid, 'à cho mình đổi sang ngày mùng 5')
    after = dm._store.get(sid)
    assert after['confirmed'] is False
    assert after['entities']['appointment_date'] == '2026-07-05'
    assert after['suggested_slots'] == ['08:00:00']   # slot cũ '09:00:00' đã bị thay
    assert after['step'] == Step.SUGGEST_SLOTS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q -k "procedure or change_of_mind"`
Expected: FAIL — chưa có định tuyến / `rag_search` chưa import

- [ ] **Step 3: Implement**

Trong `dialog_manager.py`:

(a) Thêm import (cạnh các import khác):

```python
from .rag_bridge import search as rag_search
```

(b) Trong `process()`, NGAY SAU khi tính `saved` và TRƯỚC khi merge, thêm phát hiện đổi ý:

```python
        saved  = Entities.from_dict(state.get('entities', {}))
        new_e  = nlu.entities
        changed_fields = ('appointment_date', 'location', 'service_type')
        changed = any(getattr(new_e, fld) and getattr(new_e, fld) != getattr(saved, fld)
                      for fld in changed_fields)
        merged = saved.merge(new_e)
        state['entities'] = merged.to_dict()
        if changed:
            state['suggested_slots'] = []
            state['confirmed'] = False
            if not new_e.appointment_time:
                state['entities']['appointment_time'] = None
        # Luôn đồng bộ step với entity hiện có (off-script không đẩy bước nhưng vẫn cần đúng step)
        state['step'] = self._recompute_step(
            Entities.from_dict(state['entities']), state)
```

(c) Trong `process()`, SAU khối xử lý `CANCEL` và TRƯỚC `_dispatch`, thêm định tuyến off-script:

```python
        if nlu.intent in (Intent.QUERY_PROCEDURE, Intent.QUERY_SERVICE):
            snippets = rag_search(user_text)
            action = DialogAction(ActionType.ANSWER_PROCEDURE,
                                  {'snippets': snippets,
                                   'steer': self._steer_prompt(state)})
            return self._finish(session_id, state, action, user_text, history)

        if nlu.intent in (Intent.GREETING, Intent.SMALL_TALK):
            action = DialogAction(ActionType.SMALL_TALK,
                                  {'steer': self._steer_prompt(state)})
            return self._finish(session_id, state, action, user_text, history)
```

(d) Thêm helper `_steer_prompt` (câu kéo về bước hiện tại) và `_finish` (gom phần ráp reply + lưu state, dùng chung cho cả off-script lẫn FSM — refactor phần cuối `process()` Task 8 thành gọi `_finish`):

```python
    def _steer_prompt(self, state: Dict) -> str:
        entities = Entities.from_dict(state['entities'])
        step = self._recompute_step(entities, state)
        return {
            Step.COLLECT_INTENT:   'Bạn muốn làm thủ tục gì?',
            Step.COLLECT_LOCATION: 'Bạn muốn đến cơ quan nào?',
            Step.COLLECT_DATE:     'Bạn muốn đặt lịch ngày nào?',
            Step.SUGGEST_SLOTS:    'Mình kiểm tra khung giờ giúp bạn nhé?',
            Step.CONFIRM:          'Bạn xác nhận đặt lịch chứ?',
        }.get(step, 'Mình giúp bạn đặt lịch nhé?')

    def _finish(self, session_id: str, state: Dict, action: DialogAction,
                user_text: str, history: List[Dict]) -> DialogResponse:
        if not hasattr(self, '_nlg'):
            from .response_generator import ResponseGenerator
            self._nlg = ResponseGenerator()
        reply = self._nlg.generate(action, user_text, history)
        history.append({'role': 'bot', 'content': reply})
        state['history'] = history[-10:]
        self._store.set(session_id, state)
        return DialogResponse(
            reply=reply, step=state['step'],
            done=(state['step'] == Step.DONE),
            appointment=state.get('appointment'),
            slots=state.get('suggested_slots', []), state=state)
```

(e) Thay phần cuối `process()` (đoạn ráp reply ở Task 8) bằng:

```python
        action = self._dispatch(session_id, state, nlu, user_text)
        return self._finish(session_id, state, action, user_text, history)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest ai_voice_backend/test_dialog_core.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add Backend/ai_voice_backend/dialog_manager.py Backend/ai_voice_backend/test_dialog_core.py
git commit -m "feat(voice): định tuyến hỏi thủ tục/tán gẫu + phát hiện đổi ý"
```

---

## Task 10: Kiểm tra tích hợp toàn pipeline (mock LLM)

**Files:**
- Test: `Backend/ai_voice_backend/test_dialog_core.py` (thêm test)

- [ ] **Step 1: Write integration test**

```python
def test_full_booking_flow_offline(monkeypatch):
    """NLU + NLG bị mock; kiểm tra FSM dẫn dắt đúng tới CONFIRM."""
    dm = DialogManager()
    sid = 'flow1'; dm.reset(sid)
    # ép NLG dùng template (tắt Gemini) để output deterministic
    from ai_voice_backend.response_generator import ResponseGenerator
    dm._nlg = ResponseGenerator(enabled=False)
    # ép suggest_slots trả về cố định
    monkeypatch.setattr(dm, '_get_slots',
                        lambda loc, date: ['08:00:00', '09:00:00'])

    # turn 1: cung cấp đủ service + location + date
    _force_nlu(dm, Intent.BOOK_APPOINTMENT,
               Entities(service_type='Làm căn cước', location='UBND Hoàn Kiếm',
                        appointment_date='2026-07-01'))
    r1 = dm.process(sid, 'làm căn cước ở Hoàn Kiếm ngày 1 tháng 7')
    assert '08:00' in r1.reply and '09:00' in r1.reply   # OFFER_SLOTS

    # turn 2: chọn giờ
    _force_nlu(dm, Intent.BOOK_APPOINTMENT,
               Entities(appointment_time='09:00:00'))
    r2 = dm.process(sid, 'chọn 9 giờ')
    assert 'xác nhận' in r2.reply.lower()                # CONFIRM_DETAILS
```

- [ ] **Step 2: Run full suite**

Run (từ `Backend/`): `python -m pytest ai_voice_backend/ -q`
Expected: PASS — toàn bộ test (action, rag_bridge, response_generator, dialog_core, text_normalizer cũ nếu thu thập)

- [ ] **Step 3: Syntax gate (giống CI)**

Run (từ gốc repo): `python -m compileall -q Backend/ai_voice_backend`
Expected: không lỗi

- [ ] **Step 4: Commit**

```bash
git add Backend/ai_voice_backend/test_dialog_core.py
git commit -m "test(voice): integration test pipeline đặt lịch offline"
```

---

## Task 11: Cập nhật tài liệu module

**Files:**
- Modify: `Backend/ai_voice_backend/dialog_manager.py` (docstring đầu file — phản ánh luồng mới)

- [ ] **Step 1: Cập nhật docstring**

Sửa docstring đầu `dialog_manager.py`: bổ sung mô tả lớp NLG + định tuyến off-script (hỏi thủ tục → RAG; tán gẫu; đổi ý → recompute), và rằng FSM xuất `DialogAction` thay vì chuỗi reply.

- [ ] **Step 2: Syntax check**

Run: `python -c "import ai_voice_backend.dialog_manager"` (từ `Backend/`)
Expected: không lỗi

- [ ] **Step 3: Commit**

```bash
git add Backend/ai_voice_backend/dialog_manager.py
git commit -m "docs(voice): cập nhật docstring luồng hội thoại mới"
```

---

## Ghi chú triển khai

- **Đổi ý ở mức giá trị đã sẵn**: `Entities.merge` dùng `other.x or self.x` → giá trị turn mới ghi đè. Việc còn lại là xóa cache slot/confirm khi `date/location/service` đổi (Task 9b).
- **Không đổi API ngoài**: `VoiceBackend.dialog/process_audio` và `voice_routes.py` không cần sửa — `DialogResponse` giữ nguyên các field.
- **Chi phí/độ trễ**: 2 lần gọi Gemini/lượt (NLU + NLG). Tắt nhanh bằng `VOICE_NLG_ENABLED=0` → trở lại template, vẫn chạy đủ luồng.
- **TTS**: reply đi qua normalizer + Chirp3-HD đã làm trước đó — không đụng lại.
```
