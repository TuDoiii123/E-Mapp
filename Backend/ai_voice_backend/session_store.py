"""
Session Store — lưu trạng thái hội thoại voice theo session_id.

Ưu tiên: in-memory dict (nhanh) + ghi xuống JSON file khi thay đổi (bền vững).
Thread-safe với threading.Lock.
"""
import json
import os
import threading
from typing import Any, Dict, Optional

from .config import SESSION_FILE


class SessionStore:
    def __init__(self, filepath: str = SESSION_FILE) -> None:
        self._path  = filepath
        self._lock  = threading.Lock()
        self._store: Dict[str, Any] = self._load()

    # ── public ────────────────────────────────────────────────────────────────

    def get(self, session_id: str) -> Optional[Dict]:
        with self._lock:
            return self._store.get(session_id)

    def set(self, session_id: str, state: Dict) -> None:
        with self._lock:
            self._store[session_id] = state
            self._persist()

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)
            self._persist()

    def all(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._store)

    # ── internal ──────────────────────────────────────────────────────────────

    def _load(self) -> Dict:
        try:
            if os.path.exists(self._path):
                with open(self._path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _persist(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(self._store, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# module-level singleton
_store_instance: Optional[SessionStore] = None
_store_lock = threading.Lock()


def get_store() -> SessionStore:
    global _store_instance
    if _store_instance is None:
        with _store_lock:
            if _store_instance is None:
                _store_instance = SessionStore()
    return _store_instance
