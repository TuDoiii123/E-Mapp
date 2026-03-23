"""
AI Voice Backend — E-Mapp
=========================
Module xử lý giọng nói AI cho hệ thống dịch vụ công số.

Kiến trúc:
  config.py        — đọc env vars, hằng số cấu hình
  stt.py           — Speech-to-Text  (Google Cloud + Gemini multimodal fallback)
  tts.py           — Text-to-Speech  (Google Cloud TTS, giọng Việt)
  nlu.py           — NLU: trích xuất intent + entities qua Gemini
  dialog_manager.py— State machine hội thoại đặt lịch multi-turn
  session_store.py — Lưu trạng thái session (memory + JSON file)

Sử dụng từ voice_routes.py:
  from ai_voice_backend import VoiceBackend
  vb = VoiceBackend()
  text  = vb.stt(audio_bytes)
  audio = vb.tts(text)
  resp  = vb.dialog(session_id, text)
"""

from .core import VoiceBackend

__all__ = ['VoiceBackend']
