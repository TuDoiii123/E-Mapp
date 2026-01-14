## AI Đặt lịch
## 1. Endpoint & Luồng
### 1.1 /voice/stt (POST)
Nhận file `audio/webm` (Opus) → Gọi Google STT → trả `{ status, text }`.
Trường hợp không nghe thấy gì: trả `status=error`.

### 1.2 /voice/tts (POST)
Input: `{ text: "..." }` → Tổng hợp giọng (vi-VN, neutral) → trả về bytes MP3 (`audio/mpeg`). Dùng trực tiếp làm nguồn HTML5 Audio.

### 1.3 /appointments (POST)
Tạo lịch hẹn từ payload đầy đủ (dùng nội bộ sau khi trích JSON). DB fields:
- citizen_name, phone, id_number, service_type, location
- appointment_date (DATE), appointment_time (TIME), note

### 1.4 /appointments (GET)
Liệt kê tối đa 50 lịch sắp xếp theo ngày + giờ.

### 1.5 /appointments/by-phone (GET?phone=...)
Truy xuất 10 lịch mới nhất theo số điện thoại.

### 1.6 /voice/appointments/auto-create (POST)
One-shot booking. Nhận `{ text, phone? }` → Prompt Gemini trích xuất 8 trường JSON:
```
citizen_name, phone, id_number, service_type, location,
appointment_date (YYYY-MM-DD), appointment_time (HH:MM:SS), note
```
- Nếu thiếu bất kỳ trường quan trọng (service_type, location, appointment_date, appointment_time) → `status=missing_fields + missing=[...]`.
- Nếu đủ → chuyển đổi định dạng ngày/giờ, gọi `/appointments` nội bộ → trả `status=success + appointment`.

### 1.7 /voice/dialog (POST)
Hội thoại đa bước với `session_id` cố định cho phiên:
Các bước (`DialogStep`):
1. ASK_INTENT → trích `service_type`.
2. ASK_LOCATION → trích `location`.
3. ASK_DATE → trích `appointment_date`.
4. CONFIRM (sau khi gợi ý giờ) → chọn 1 trong các slot trống.
5. DONE → lịch đã tạo; có thể reset nếu người dùng lại đề cập thủ tục mới.

Gợi ý giờ (`suggest_slots_for_state`): so sánh các khung cố định `[08:00,09:00,10:00,14:00,15:00]` với DB để bỏ slot bận. Nếu kín hết → yêu cầu ngày khác.

Gemini được gọi ở mỗi bước để trích JSON tối giản:
- ASK_INTENT: `{ service_type }`
- ASK_LOCATION: `{ location }`
- ASK_DATE: `{ appointment_date }`
- CONFIRM: `{ appointment_time }` (khớp một slot trong danh sách gợi ý)

Khi người dùng chọn giờ hợp lệ → tạo lịch hẹn DB → state chuyển sang DONE và trả về thông tin lịch.

## 2. Môi trường & Biến .env
Các biến cần có trong `.env`:
```
GEMINI_API_KEY=""
DB_HOST=""
DB_PORT=""
DB_USER=""
DB_PASSWORD=""
DB_NAME=""
```
Yêu cầu thiết lập Google Application Credentials nếu dùng service account:
```
GOOGLE_APPLICATION_CREDENTIALS=""
```

## 3. Cài đặt & Chạy
### 3.1 Cài đặt dependencies
`requirements.txt` chứa các gói chính: `fastapi`, `uvicorn`, `google-cloud-speech`, `google-cloud-texttospeech`, `google-generativeai`, `mysql-connector-python`, `python-dotenv`.

Cài đặt:
```bash
pip install -r requirements.txt
```

### 3.2 Chạy dev
```bash
python main.py
```
FastAPI mặc định sẽ chạy tại `http://127.0.0.1:8000`.


## RAG
## 1. Cài đặt môi trường

### Clone project

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd <your-repo>
```

### Tạo môi trường Python

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## 2. Tạo file `.env`

Tạo file `.env` ở thư mục gốc:

```
GOOGLE_API_KEY=<your-openai-key>
```

Tạo file `config.json` ở thư mục `connect_SQL` cho database tương ứng:

```
{
    "connection": {
        "server": "",
        "database": "",
        "username": "",
        "password": ""
    }
} 
```

## 3. Tải mô hình Embedding

Mô hình không kèm theo repo để giảm dung lượng.

Tạo folder `models` trong thư mục dự án và tải từ Hugging Face:

https://huggingface.co/AITeamVN/Vietnamese_Embedding


## 4. Tạo vector database (Chroma)

1. Tạo file `config.json` ở thư mục `create_vecto_db` tương ứng:
```
{
  "faq_csv_path": "",
  "db_path": "", # Tên folder chứa model
  "db_folder": "chroma_db_faqs", # Tạo thêm 1 folder con trong db_path để giúp thao tác xóa
  "collection_name": "faqs_collection",  # Tên collection trong ChromaDB, mặc định là faqs_collection
  "local_model_path": "" # Path của file model đã tải
}
```

2 Tạo vector DB:
```bash
python create_vect_db/create_faq_db.py
```
---

## 5. Chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng chạy tại:
```
http://localhost:8888
```
---

## 6. Tính năng chính

* Chatbot hỏi đáp tiếng Việt dựa trên RAG
* Tìm kiếm embedding qua ChromaDB
* Agent sử dụng tools RAG
* Tạo DB từ file CSV câu hỏi thường gặp

## Quick Start SERVER — Python/Flask (recommended for migration)

## 1. Cài đặt môi trường:

## Cài đặt biến
``
pip install -r requirements.txt
# if requirements.txt is missing, at minimum install:
pip install flask flask-cors pyjwt
```

2. Run the Flask server:

```powershell
python server.py
```
