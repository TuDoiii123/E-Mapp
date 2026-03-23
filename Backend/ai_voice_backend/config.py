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
TTS_VOICE_NAME   = os.getenv('GOOGLE_TTS_VOICE_NAME', '')          # để trống = auto
TTS_SPEAKING_RATE= float(os.getenv('GOOGLE_TTS_SPEAKING_RATE', '1.0'))
TTS_PITCH        = float(os.getenv('GOOGLE_TTS_PITCH', '0.0'))

# ── Google Cloud STT ────────────────────────────────────────────────────────
STT_LANGUAGE     = os.getenv('GOOGLE_STT_LANGUAGE', 'vi-VN')
STT_MOCK         = os.getenv('VOICE_STT_DEV_MOCK', '1') == '1'
STT_DEFAULT_MOCK = 'đặt lịch làm căn cước công dân ngày mai lúc 9 giờ'

# ── Dialog ──────────────────────────────────────────────────────────────────
DIALOG_TTS_ENABLED = os.getenv('VOICE_DIALOG_TTS', '0') == '1'

# ── Session store ───────────────────────────────────────────────────────────
SESSION_DIR      = os.path.join(os.path.dirname(__file__), '..', 'data')
SESSION_FILE     = os.path.join(SESSION_DIR, 'voice_sessions.json')
