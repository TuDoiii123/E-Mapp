"""
Cấu hình AI Voice Backend — đọc từ biến môi trường.
"""
import os

# ── Gemini ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY', '')
GEMINI_MODEL     = os.getenv('GEMINI_MODEL_NAME', 'models/gemini-2.0-flash')

# ── Google Cloud TTS ────────────────────────────────────────────────────────
GCP_CREDENTIALS  = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
TTS_LANGUAGE     = os.getenv('GOOGLE_TTS_LANGUAGE', 'vi-VN')
# Giọng tự nhiên nhất cho tiếng Việt: Chirp3-HD (KHÔNG nhận SSML/pitch).
# Đổi sang vi-VN-Neural2-A nếu muốn dùng SSML điều khiển ngữ điệu.
TTS_VOICE_NAME   = os.getenv('GOOGLE_TTS_VOICE_NAME', 'vi-VN-Chirp3-HD-Aoede')
TTS_SPEAKING_RATE= float(os.getenv('GOOGLE_TTS_SPEAKING_RATE', '0.96'))  # chậm nhẹ, đỡ gấp
TTS_PITCH        = float(os.getenv('GOOGLE_TTS_PITCH', '-1.0'))          # chỉ áp dụng giọng Neural2/Wavenet

# ── Gemini TTS (không cần GCP credentials, dùng GEMINI_API_KEY) ──────────────
# Backend dự phòng khi không có Google Cloud TTS. Trả audio WAV (PCM 24kHz).
GEMINI_TTS_MODEL = os.getenv('GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts')
GEMINI_TTS_VOICE = os.getenv('GEMINI_TTS_VOICE', 'Kore')   # giọng prebuilt: Kore/Aoede/Leda/Puck...

# ── Google Cloud STT ────────────────────────────────────────────────────────
STT_LANGUAGE     = os.getenv('GOOGLE_STT_LANGUAGE', 'vi-VN')
# Dev mock STT — mặc định OFF để không ảnh hưởng production
# Set VOICE_STT_DEV_MOCK=1 trong .env khi test local không có Google Cloud
STT_MOCK         = os.getenv('VOICE_STT_DEV_MOCK', '0') == '1'
STT_DEFAULT_MOCK = os.getenv('VOICE_STT_MOCK_TEXT', 'đặt lịch làm căn cước công dân ngày mai lúc 9 giờ')

# ── Dialog ──────────────────────────────────────────────────────────────────
DIALOG_TTS_ENABLED = os.getenv('VOICE_DIALOG_TTS', '0') == '1'

# ── NLG (sinh câu trả lời tự nhiên) ─────────────────────────────────────────
# Bật: dùng Gemini diễn đạt câu trả lời tự nhiên. Tắt: dùng template cố định.
VOICE_NLG_ENABLED = os.getenv('VOICE_NLG_ENABLED', '1') == '1'

# ── Session store ───────────────────────────────────────────────────────────
SESSION_DIR      = os.path.join(os.path.dirname(__file__), '..', 'data')
SESSION_FILE     = os.path.join(SESSION_DIR, 'voice_sessions.json')
