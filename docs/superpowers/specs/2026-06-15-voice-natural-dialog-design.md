# Thiết kế: Hội thoại voice tự nhiên cho E-Mapp

- **Ngày**: 2026-06-15
- **Phạm vi**: `Backend/ai_voice_backend`
- **Mục tiêu**: Bot đặt lịch hành chính nói chuyện tự nhiên hơn — diễn đạt ấm áp/biến hóa,
  xử lý nói lạc đề, đổi ý giữa chừng, trả lời câu hỏi về thủ tục (grounded bằng RAG),
  trong khi **phần nghiệp vụ đặt lịch giữ deterministic tuyệt đối**.

## Bối cảnh

Kiến trúc hiện tại:
- `nlu.py` — Gemini trích `intent` + `entities`. Phần "hiểu" đã linh hoạt.
- `dialog_manager.py` — máy trạng thái (FSM) với **câu trả lời cố định** (`_PROMPTS` + chuỗi
  hardcode). Đây là nguyên nhân nghe "máy móc".
- Booking (`services.appointments.create_appointment`) tạo lịch thật: mã lịch, số thứ tự,
  khung giờ trống → **không được để LLM bịa**.
- RAG có sẵn: `RAG.tools.rag.search_project_documents(query)` trả top-5 `answer_text`.
- TTS: đã chuẩn hóa text + giọng Chirp3-HD (việc trước đó).

## Quyết định thiết kế (đã chốt)

1. Mức độ tự nhiên = **trò chuyện linh hoạt**: tự nhiên + off-script (tán gẫu, đổi ý,
   hỏi thủ tục) + guardrail chống bịa. (Không chọn full LLM-driven agent.)
2. Câu hỏi thủ tục **grounded bằng RAG/FAQ có sẵn**; ngoài kho → trả lời "chưa có thông tin".
3. Hướng kiến trúc: **A — lõi deterministic + lớp diễn đạt LLM + định tuyến ý định**.

## Nguyên tắc cốt lõi

**Tách "sự thật" (hệ thống quyết định) khỏi "câu chữ" (LLM diễn đạt).**
LLM chỉ làm câu nói tự nhiên; không bao giờ quyết định nghiệp vụ hay sinh ra số liệu.

## Kiến trúc

```
Audio → STT → text
                │
                ▼
        NLU (Gemini)            intent + entities  (mở rộng intent)
                │
                ▼
   DialogManager (lõi FSM, deterministic)
     ─ định tuyến off-script (hỏi thủ tục / tán gẫu / hủy)
     ─ sở hữu mọi sự thật: slot trống, mã lịch, đặt lịch thật
     ─ trả về DialogAction + facts  (KHÔNG ghép chuỗi reply ở đây)
                │                      │ (nếu hỏi thủ tục)
                │                      ▼
                │            search_project_documents()  (RAG có sẵn)
                ▼
   ResponseGenerator (NLG, mới)
     ─ Gemini diễn đạt từ (Action + Facts + câu user + history)
     ─ bơm sự thật, cấm bịa; lỗi → template fallback
                │
                ▼  (+ guardrail hậu kiểm)
         reply text → TTS (normalize + Chirp3-HD)
```

## Thành phần

### 1. `response_generator.py` (MỚI) — lớp NLG
- `ResponseGenerator.generate(action, facts, user_text, history) -> str`
- Prompt cho Gemini: vai "trợ lý hành chính thân thiện, nói qua giọng nói"; loại action;
  **DỮ LIỆU sự thật (phải dùng đúng, cấm thêm số/mã/giờ/ngày)**; câu user vừa nói (để thừa nhận);
  tóm tắt lịch sử; ràng buộc (≤ ~2 câu, tiếng Việt tự nhiên, hợp đọc thành tiếng).
- **Fallback**: Gemini lỗi/tắt → câu template deterministic theo action (chuyển `_PROMPTS`
  hiện tại về đây làm fallback).
- Tái dùng cấu hình genai như `nlu.py` (api key, model `GEMINI_MODEL`).

### 2. `DialogAction` (MỚI, trong `dialog_manager.py`)
"Ý định giao tiếp" có cấu trúc thay cho chuỗi reply cứng. Mỗi loại kèm `facts: dict`.

Các loại:
`GREET, ASK_INTENT, ASK_LOCATION, ASK_DATE, OFFER_SLOTS, NO_SLOTS, ASK_TIME_AGAIN,
CONFIRM_DETAILS, SLOT_TAKEN, BOOKING_SUCCESS, BOOKING_ERROR, ANSWER_PROCEDURE,
SMALL_TALK, CANCELLED, ALREADY_DONE`.

### 3. `DialogManager` (REFACTOR)
- `_dispatch` trả về `DialogAction` (không ghép reply). `process()` chạy action qua
  `ResponseGenerator` để ra `reply`, rồi đóng gói `DialogResponse` **giữ nguyên API ngoài**
  (`reply/step/done/appointment/...`).
- **Định tuyến off-script trước FSM**:
  - `QUERY_PROCEDURE` → `ANSWER_PROCEDURE(snippets, current_step)`, **không đổi step**,
    có câu kéo về bước hiện tại.
  - `GREETING/SMALL_TALK` → `SMALL_TALK(current_step)`.
  - `CANCEL` → `CANCELLED`.
- **`_recompute_step(entities, state)`** thay cho đẩy bước tuyến tính: suy ra bước từ entity
  đã có (thiếu service→COLLECT_INTENT; thiếu location→COLLECT_LOCATION; thiếu date→COLLECT_DATE;
  đủ nhưng chưa có slot phù hợp→SUGGEST_SLOTS; đủ→CONFIRM).
- **Phát hiện đổi ý**: nếu turn này `date`/`location`/`service` khác giá trị đã lưu →
  xóa `suggested_slots` + `appointment_time` + `confirmed`, rồi recompute. ("à đổi sang thứ 6"
  tự quay lại lấy slot mới, không kẹt ở CONFIRM.)

### 4. `nlu.py` (mở rộng nhẹ)
Thêm intent hợp lệ `QUERY_PROCEDURE, GREETING, SMALL_TALK` vào whitelist
`_parse_gemini_response` (hiện ép về UNKNOWN). Không phá fallback regex.

### 5. `rag_bridge.py` (MỚI, nhỏ)
Wrapper lazy gọi `RAG.tools.rag.search_project_documents`, bọc import nặng (model embedding).
Lỗi/không khả dụng → trả `[]`. Không bao giờ ném exception ra dialog.

### 6. `config.py`
Thêm `VOICE_NLG_ENABLED` (mặc định bật; tắt → dùng template fallback, tiết kiệm chi phí).

## Luồng một lượt hội thoại

1. STT → `text`.
2. `NLU.analyze(text, history)` → `intent` + `entities`.
3. Merge entities (giá trị mới ghi đè — đã sẵn trong `Entities.merge`).
4. Định tuyến (trước FSM): QUERY_PROCEDURE→RAG; GREETING/SMALL_TALK; CANCEL; còn lại→FSM.
5. FSM `_recompute_step` + dispatch → `DialogAction` + `facts`.
6. `ResponseGenerator.generate(...)` → `reply` tự nhiên.
7. Guardrail hậu kiểm → `reply` cuối.
8. Đóng gói `DialogResponse` → TTS.

## Guardrail (bắt buộc)

- **Bơm sự thật, cấm bịa**: NLG chỉ nhận facts trong prompt; chỉ thị "không tự thêm
  số/mã/giờ/ngày".
- **Hậu kiểm số liệu quan trọng**: với `BOOKING_SUCCESS` và `OFFER_SLOTS`, sau khi NLG sinh câu,
  kiểm tra mã lịch / số thứ tự / các khung giờ có mặt trong reply; nếu thiếu → **nối thêm dòng
  deterministic** chứa đúng dữ liệu. Đảm bảo đúng số liệu kể cả khi LLM diễn giải lệch.
- **Booking vẫn gated**: chỉ `create_appointment` khi intent `CONFIRM` + đã qua bước CONFIRM.
  NLG không bao giờ tự đặt lịch.
- **RAG rỗng** → ANSWER_PROCEDURE: "mình chưa có thông tin về việc đó" + kéo về bước đang dở.
- **Degradation**: Gemini/NLG lỗi → template fallback; RAG lỗi → coi như rỗng. Lớp LLM không
  bao giờ làm chết hệ thống.

## Chiến lược test (chạy không cần GCP/Gemini credentials)

- **Lõi deterministic (quan trọng nhất)**: bảng `(step, intent, entities) → DialogAction`.
  Ca: thiếu từng trường; đổi ý ở CONFIRM (đổi ngày → quay lại SUGGEST_SLOTS); slot hết;
  hỏi thủ tục giữa chừng giữ nguyên step.
- **Guardrail hậu kiểm**: mock NLG trả câu thiếu mã/slot → reply cuối vẫn chứa đủ.
- **NLG fallback**: tắt Gemini → mỗi action ra đúng câu template.
- **rag_bridge**: import lỗi/rỗng → trả `[]`, không ném exception.
- **normalizer**: giữ 16 test sẵn có.

## File đụng tới

| File | Việc |
|---|---|
| `response_generator.py` | mới — NLG + template fallback |
| `dialog_manager.py` | refactor: trả `DialogAction`, `_recompute_step`, định tuyến off-script |
| `rag_bridge.py` | mới — wrapper RAG lazy, an toàn lỗi |
| `nlu.py` | mở rộng whitelist intent |
| `config.py` | `VOICE_NLG_ENABLED` |
| `test_dialog_*.py` | mới — test lõi + guardrail + fallback |

## Không làm (YAGNI)

- Không full LLM-driven agent / tool-calling.
- Không streaming token.
- Không thêm kho kiến thức mới — chỉ dùng RAG sẵn có.
- Không đổi API public của `VoiceBackend` / `voice_routes.py`.
```
