"""
CAG — Semantic Cache Engine
============================

Kiến trúc CAG (Cache Augmented Generation) tối ưu hóa RAG bằng cách:
  1. Embed câu hỏi của người dùng thành vector nhiều chiều.
  2. Tính Cosine Similarity giữa vector đó và các câu hỏi đã cache.
  3. Nếu similarity ≥ threshold → trả ngay câu trả lời từ cache (bỏ qua
     toàn bộ pipeline: task_analyzer + tool_executor + llm_response).
  4. Nếu miss → chạy pipeline đầy đủ, rồi lưu kết quả vào cache.

Luồng xử lý:
  Query ──► [Embed] ──► [Cosine Search] ──► HIT ──► Return cached answer
                                         └── MISS ──► Full RAG ──► [Store] ──► Return

Tham số cấu hình (biến môi trường):
  RAG_CACHE_THRESHOLD  : float, default 0.92  — ngưỡng cosine để coi là hit
  RAG_CACHE_TTL_HOURS  : int,   default 24    — thời gian sống của mỗi entry (giờ)
  RAG_CACHE_MAX_SIZE   : int,   default 1000  — số entry tối đa trong bộ nhớ (LRU)

Lưu ý: toàn bộ output chỉ ghi ra terminal qua logger 'rag.cache'.
"""

import hashlib
import json
import math
import os
import sys
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from logger import get_logger

log = get_logger('rag.cache')

# ── cấu hình từ env ───────────────────────────────────────────────────────────
CACHE_THRESHOLD: float = float(os.getenv('RAG_CACHE_THRESHOLD', '0.92'))
CACHE_TTL_HOURS: int   = int(os.getenv('RAG_CACHE_TTL_HOURS', '24'))
CACHE_MAX_SIZE:  int   = int(os.getenv('RAG_CACHE_MAX_SIZE', '1000'))

# ANSI helpers (terminal only)
_G = '\033[92m'; _Y = '\033[93m'; _R = '\033[91m'
_C = '\033[96m'; _B = '\033[1m';  _D = '\033[2m'; _X = '\033[0m'


# ─────────────────────────── data model ──────────────────────────────────────

@dataclass
class CacheEntry:
    query:           str
    query_embedding: List[float]
    answer:          str
    created_at:      datetime
    last_hit_at:     datetime
    hit_count:       int = 0
    expires_at:      datetime = field(default_factory=lambda: (
        datetime.utcnow() + timedelta(hours=CACHE_TTL_HOURS)
    ))


# ─────────────────────────── math primitives ─────────────────────────────────

def _cosine(a: List[float], b: List[float]) -> float:
    """Cosine similarity: dot(A,B) / (‖A‖·‖B‖)  ∈ [-1, 1]."""
    dot  = sum(x * y for x, y in zip(a, b))
    na   = math.sqrt(sum(x * x for x in a))
    nb   = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _euclidean(a: List[float], b: List[float]) -> float:
    """Euclidean (L2) distance: √Σ(Aᵢ-Bᵢ)²  ∈ [0, ∞)."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _dot(a: List[float], b: List[float]) -> float:
    """Raw dot product: Σ(Aᵢ·Bᵢ)."""
    return sum(x * y for x, y in zip(a, b))


def _naive(dt: datetime) -> datetime:
    """Strip timezone info so naive/aware datetimes compare safely."""
    return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt


# ─────────────────────────── cache engine ────────────────────────────────────

class SemanticCache:
    """
    Thread-safe, in-memory LRU semantic cache with optional PostgreSQL
    persistence.  Uses cosine similarity to find semantically equivalent
    queries across sessions.
    """

    def __init__(self) -> None:
        self._store:  OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock    = threading.Lock()
        self._hits    = 0
        self._misses  = 0
        self._evicted = 0
        self._db_loaded = False

        log.info(
            f'{_B}[CAG]{_X} SemanticCache ready — '
            f'threshold={_C}{CACHE_THRESHOLD}{_X}  '
            f'ttl={CACHE_TTL_HOURS}h  '
            f'max={CACHE_MAX_SIZE} entries'
        )

    # ── public API ────────────────────────────────────────────────────────────

    def lookup(
        self,
        query_embedding: List[float],
        threshold: Optional[float] = None,
    ) -> Optional[CacheEntry]:
        """
        Tìm entry có cosine similarity cao nhất với query_embedding.

        Trả về CacheEntry nếu similarity ≥ threshold, ngược lại None.

        Độ phức tạp: O(n·d) với n = số entry, d = chiều vector.
        Trong thực tế n ≤ 1000 và d = 768, đủ nhanh cho realtime.
        """
        if not self._db_loaded:
            self._load_from_db()

        thr = threshold if threshold is not None else CACHE_THRESHOLD
        now = datetime.utcnow()

        best_key: Optional[str]       = None
        best_entry: Optional[CacheEntry] = None
        best_cos  = -1.0
        best_l2   = float('inf')
        best_dot  = float('-inf')

        with self._lock:
            expired_keys = []
            for key, entry in self._store.items():
                if _naive(entry.expires_at) < now:
                    expired_keys.append(key)
                    continue
                cos = _cosine(query_embedding, entry.query_embedding)
                if cos > best_cos:
                    best_cos   = cos
                    best_l2    = _euclidean(query_embedding, entry.query_embedding)
                    best_dot   = _dot(query_embedding, entry.query_embedding)
                    best_key   = key
                    best_entry = entry

            for k in expired_keys:
                del self._store[k]
                self._evicted += 1

        # ── log distance metrics regardless of hit/miss ───────────────────
        self._log_lookup_metrics(best_cos, best_l2, best_dot, thr, best_entry)

        if best_entry is not None and best_cos >= thr:
            with self._lock:
                best_entry.hit_count  += 1
                best_entry.last_hit_at = now
                if best_key in self._store:
                    self._store.move_to_end(best_key)
            self._hits += 1
            self._persist_hit(best_key, best_entry)
            return best_entry

        self._misses += 1
        return None

    def store(
        self,
        query: str,
        query_embedding: List[float],
        answer: str,
    ) -> None:
        """Cache một cặp (query, answer) kèm vector embedding."""
        key   = self._hash(query)
        entry = CacheEntry(
            query=query,
            query_embedding=query_embedding,
            answer=answer,
            created_at=datetime.utcnow(),
            last_hit_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=CACHE_TTL_HOURS),
        )
        with self._lock:
            if key in self._store:
                # already cached (concurrent request) — skip
                return
            if len(self._store) >= CACHE_MAX_SIZE:
                evicted_key, evicted = next(iter(self._store.items()))
                del self._store[evicted_key]
                self._evicted += 1
                log.debug(
                    f'{_D}[CAG] LRU evict: "{evicted.query[:55]}…"{_X}'
                )
            self._store[key] = entry

        dim = len(query_embedding)
        log.info(
            f'{_B}[CAG]{_X} {_G}STORED{_X}  '
            f'size={_C}{len(self._store)}{_X}  '
            f'dim={dim}  '
            f'ttl={CACHE_TTL_HOURS}h  '
            f'"{query[:60]}"'
        )
        self._persist_to_db(key, entry)

    def log_stats(self) -> None:
        """Ghi thống kê tổng hợp ra terminal."""
        total    = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        color    = _G if hit_rate >= 0.5 else (_Y if hit_rate >= 0.2 else _R)
        log.info(
            f'{_B}[CAG] Cache Stats{_X}  '
            f'entries={_C}{len(self._store)}{_X}  '
            f'hits={_G}{self._hits}{_X}  '
            f'misses={_R}{self._misses}{_X}  '
            f'evicted={self._evicted}  '
            f'hit_rate={color}{hit_rate:.1%}{_X}'
        )

    # ── internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _hash(query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode('utf-8')).hexdigest()

    def _log_lookup_metrics(
        self,
        cos: float,
        l2: float,
        dot: float,
        threshold: float,
        entry: Optional[CacheEntry],
    ) -> None:
        """
        In bảng chỉ số khoảng cách toán học ra terminal.

        Cosine Similarity  = dot(Q,C) / (‖Q‖·‖C‖)   — đo góc ngữ nghĩa
        Euclidean Distance = √Σ(Qᵢ-Cᵢ)²             — khoảng cách hình học
        Dot Product        = Σ(Qᵢ·Cᵢ)               — tích vô hướng thô
        """
        if entry is None:
            log.info(
                f'{_B}[CAG]{_X} {_Y}MISS{_X}  '
                f'cache empty  no similarity computed'
            )
            return

        hit   = cos >= threshold
        label = f'{_G}HIT {_X}' if hit else f'{_R}MISS{_X}'
        bar   = self._sim_bar(cos)

        cos_color = _G if cos >= 0.85 else (_Y if cos >= 0.65 else _R)

        log.info(
            f'\n'
            f'{_B}[CAG] Similarity Metrics{_X}  →  {label}\n'
            f'  Cosine Similarity  : {cos_color}{cos:+.6f}{_X}  {bar}  '
            f'(threshold {_C}{threshold}{_X})\n'
            f'  Euclidean Distance : {l2:.6f}   {_D}(lower = closer){_X}\n'
            f'  Dot Product        : {dot:.4f}\n'
            f'  Cached query       : {_D}"{(entry.query[:70] + "…") if len(entry.query) > 70 else entry.query}"{_X}\n'
            f'  Cache hits so far  : {entry.hit_count}  |  '
            f'Age: {self._age_str(entry.created_at)}'
        )

    @staticmethod
    def _sim_bar(cos: float, width: int = 20) -> str:
        """Thanh tiến trình trực quan hóa cosine similarity."""
        filled = max(0, min(width, round((cos + 1) / 2 * width)))
        color  = _G if cos >= 0.85 else (_Y if cos >= 0.65 else _R)
        bar    = '█' * filled + '░' * (width - filled)
        return f'{color}[{bar}]{_X}'

    @staticmethod
    def _age_str(created_at: datetime) -> str:
        delta = datetime.utcnow() - _naive(created_at)
        s = int(delta.total_seconds())
        if s < 60:   return f'{s}s'
        if s < 3600: return f'{s//60}m {s%60}s'
        return f'{s//3600}h {(s%3600)//60}m'

    # ── PostgreSQL persistence (non-fatal) ────────────────────────────────────

    def _load_from_db(self) -> None:
        self._db_loaded = True
        try:
            from models.db import db
            from sqlalchemy import text
            rows = db.session.execute(text("""
                SELECT query_hash, query_text, query_vector, answer_text,
                       hit_count, created_at, last_hit_at, expires_at
                FROM public.rag_semantic_cache
                WHERE expires_at > now()
                ORDER BY last_hit_at DESC
                LIMIT :lim
            """), {'lim': CACHE_MAX_SIZE}).fetchall()

            count = 0
            for row in rows:
                try:
                    vec = json.loads(row[2])
                    entry = CacheEntry(
                        query=row[1], query_embedding=vec,
                        answer=row[3], created_at=row[5],
                        last_hit_at=row[6], hit_count=row[4],
                        expires_at=row[7],
                    )
                    self._store[row[0]] = entry
                    count += 1
                except Exception:
                    pass

            if count:
                log.info(
                    f'{_B}[CAG]{_X} Loaded {_C}{count}{_X} '
                    f'entries from PostgreSQL cache'
                )
        except Exception as exc:
            log.debug(f'[CAG] DB load skipped ({exc})')

    def _persist_to_db(self, key: str, entry: CacheEntry) -> None:
        try:
            from models.db import db
            from sqlalchemy import text
            db.session.execute(text("""
                INSERT INTO public.rag_semantic_cache
                    (query_hash, query_text, query_vector, answer_text,
                     hit_count, created_at, last_hit_at, expires_at)
                VALUES
                    (:key, :query, :vec, :answer,
                     :hits, :created, :last_hit, :expires)
                ON CONFLICT (query_hash) DO UPDATE SET
                    hit_count   = EXCLUDED.hit_count,
                    last_hit_at = EXCLUDED.last_hit_at,
                    expires_at  = EXCLUDED.expires_at
            """), {
                'key':      key,
                'query':    entry.query,
                'vec':      json.dumps(entry.query_embedding),
                'answer':   entry.answer,
                'hits':     entry.hit_count,
                'created':  entry.created_at,
                'last_hit': entry.last_hit_at,
                'expires':  entry.expires_at,
            })
            db.session.commit()
        except Exception as exc:
            log.debug(f'[CAG] DB persist failed (non-fatal): {exc}')
            try:
                from models.db import db as _db
                _db.session.rollback()
            except Exception:
                pass

    def _persist_hit(self, key: str, entry: CacheEntry) -> None:
        try:
            from models.db import db
            from sqlalchemy import text
            db.session.execute(text("""
                UPDATE public.rag_semantic_cache
                SET hit_count = :hits, last_hit_at = now()
                WHERE query_hash = :key
            """), {'hits': entry.hit_count, 'key': key})
            db.session.commit()
        except Exception:
            pass


# ── module-level singleton (one cache per process) ────────────────────────────

_cache_instance: Optional[SemanticCache] = None
_cache_lock = threading.Lock()


def get_cache() -> SemanticCache:
    """Trả về singleton SemanticCache. Thread-safe."""
    global _cache_instance
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = SemanticCache()
    return _cache_instance
