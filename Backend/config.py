"""
Cấu hình chung — nguồn duy nhất cho JWT, Gemini model names và các constant dùng chung.
"""
import os
import logging

logger = logging.getLogger(__name__)

JWT_SECRET: str = os.getenv('JWT_SECRET', 'default-secret-key-change-in-production')
JWT_EXPIRES_IN: str = os.getenv('JWT_EXPIRES_IN', '7d')

if JWT_SECRET == 'default-secret-key-change-in-production':
    logger.warning('JWT_SECRET chưa được đặt trong .env — không an toàn cho production!')

# ── Gemini model names ────────────────────────────────────────────────────────
# Voice/NLU/STT/TTS: dùng GEMINI_MODEL_NAME (prefix "models/" theo Generative AI SDK)
GEMINI_MODEL_VOICE: str = os.getenv('GEMINI_MODEL_NAME', 'models/gemini-2.5-flash')

# RAG/LLM wrapper: dùng GEMINI_MODEL_RAG (không cần prefix "models/")
GEMINI_MODEL_RAG: str = os.getenv('GEMINI_MODEL_RAG', 'gemini-2.5-flash')
