"""
RAG Retrieval Quality Metrics — terminal-only logging.

Computes and logs three mathematical distance/similarity measures between
the query vector and each retrieved document vector:

  • Cosine Similarity  = dot(A,B) / (‖A‖·‖B‖)        range [-1, 1], higher = more similar
  • Euclidean (L2)     = √Σ(Aᵢ-Bᵢ)²                  range [0, ∞),  lower  = more similar
  • Dot Product        = Σ(Aᵢ·Bᵢ)                     unbounded,     higher = more similar

All output goes to the 'rag.metrics' logger (terminal only).
"""

import math
import sys
from pathlib import Path
from typing import List, Optional

# ── reuse centralized logger ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from logger import get_logger

log = get_logger('rag.metrics')

# ANSI codes for inline coloring inside metric rows (no reset needed per line)
_GREEN  = '\033[92m'
_YELLOW = '\033[93m'
_RED    = '\033[91m'
_CYAN   = '\033[96m'
_BOLD   = '\033[1m'
_DIM    = '\033[2m'
_RESET  = '\033[0m'


# ─────────────────────────── pure math ───────────────────────────────────────

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors. Returns value in [-1, 1]."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """True Euclidean (L2) distance. Lower = more similar."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def dot_product(a: List[float], b: List[float]) -> float:
    """Raw dot product (unnormalized inner product)."""
    return sum(x * y for x, y in zip(a, b))


# ─────────────────────────── color helpers ───────────────────────────────────

def _color_cosine(val: float) -> str:
    """Green ≥ 0.85, yellow ≥ 0.65, red otherwise."""
    s = f'{val:+.4f}'
    if val >= 0.85:
        return f'{_GREEN}{s}{_RESET}'
    if val >= 0.65:
        return f'{_YELLOW}{s}{_RESET}'
    return f'{_RED}{s}{_RESET}'


def _color_l2(val: float, max_l2: float) -> str:
    """Green if in bottom 30 % of range, yellow middle, red top."""
    ratio = val / max_l2 if max_l2 > 0 else 0
    s = f'{val:.4f}'
    if ratio <= 0.30:
        return f'{_GREEN}{s}{_RESET}'
    if ratio <= 0.65:
        return f'{_YELLOW}{s}{_RESET}'
    return f'{_RED}{s}{_RESET}'


def _truncate(text: str, width: int = 35) -> str:
    text = (text or '').replace('\n', ' ').strip()
    return text if len(text) <= width else text[:width - 1] + '…'


# ─────────────────────────── main logging call ───────────────────────────────

def log_retrieval_metrics(
    query: str,
    query_vec: List[float],
    doc_embeddings: List[List[float]],
    doc_metadatas: List[dict],
    chroma_distances: Optional[List[float]] = None,
) -> None:
    """
    Compute and log retrieval metrics for every retrieved document.

    Parameters
    ----------
    query          : original user query string
    query_vec      : embedding of the query  (list[float])
    doc_embeddings : embedding of each retrieved doc (list[list[float]])
    doc_metadatas  : ChromaDB metadata dicts for each doc
    chroma_distances: raw L2² distances returned by ChromaDB (optional, for cross-check)
    """
    n = len(doc_embeddings)
    if n == 0:
        log.warning('[RAG METRICS] No documents retrieved — nothing to evaluate.')
        return

    dim = len(query_vec)

    # ── compute all three metrics ─────────────────────────────────────────────
    rows = []
    for i, (emb, meta) in enumerate(zip(doc_embeddings, doc_metadatas)):
        cos  = cosine_similarity(query_vec, emb)
        l2   = euclidean_distance(query_vec, emb)
        dot  = dot_product(query_vec, emb)
        preview = _truncate(meta.get('answer_text') or meta.get('question_text') or str(meta), 35)
        rows.append({
            'idx':     i + 1,
            'preview': preview,
            'cos':     cos,
            'l2':      l2,
            'dot':     dot,
        })

    max_l2 = max(r['l2'] for r in rows) or 1.0
    best   = max(rows, key=lambda r: r['cos'])

    # ── build ASCII table ─────────────────────────────────────────────────────
    W_IDX  = 3
    W_DOC  = 37   # preview column (visible chars, colors add hidden bytes)
    W_COS  = 10
    W_L2   = 10
    W_DOT  = 12

    sep_top = (f'┌{"─"*(W_IDX+2)}┬{"─"*(W_DOC+2)}┬'
               f'{"─"*(W_COS+2)}┬{"─"*(W_L2+2)}┬{"─"*(W_DOT+2)}┐')
    sep_mid = sep_top.replace('┌', '├').replace('┐', '┤').replace('─', '─')
    sep_bot = sep_top.replace('┌', '└').replace('┐', '┘')

    header = (f'│ {"#":^{W_IDX}} │ {"Document preview":^{W_DOC}} │'
              f' {"Cosine Sim":^{W_COS}} │ {"L2 Dist":^{W_L2}} │ {"Dot Product":^{W_DOT}} │')

    lines = [
        '',
        f'{_BOLD}{_CYAN}[RAG METRICS]{_RESET} query: {_BOLD}"{_truncate(query, 70)}"{_RESET}',
        f'{_DIM}  Embedding dim: {dim}  |  Retrieved: {n} docs{_RESET}',
        sep_top,
        header,
        sep_mid,
    ]

    for r in rows:
        cos_str = _color_cosine(r['cos'])
        l2_str  = _color_l2(r['l2'], max_l2)
        dot_str = f'{r["dot"]:>12.2f}'
        mark    = f' {_GREEN}★{_RESET}' if r['idx'] == best['idx'] else '  '

        # visible padding for preview (no ANSI in preview)
        pad = W_DOC - len(r['preview'])
        doc_cell = r['preview'] + ' ' * pad

        # For cosine and l2, ANSI codes add hidden bytes — pad the visible part
        cos_visible = f'{r["cos"]:+.4f}'
        l2_visible  = f'{r["l2"]:.4f}'
        cos_cell = _color_cosine(r['cos']) + ' ' * (W_COS - len(cos_visible))
        l2_cell  = _color_l2(r['l2'], max_l2) + ' ' * (W_L2 - len(l2_visible))

        line = (f'│{mark}{r["idx"]:^{W_IDX}} │ {doc_cell} │ '
                f'{cos_cell} │ {l2_cell} │ {dot_str} │')
        lines.append(line)

    lines.append(sep_bot)
    lines.append(
        f'  {_BOLD}Best match{_RESET}: doc #{best["idx"]}  '
        f'cosine={_color_cosine(best["cos"])}  '
        f'L2={_color_l2(best["l2"], max_l2)}  '
        f'dot={best["dot"]:.2f}'
    )

    if chroma_distances:
        cd_str = '  '.join(f'doc{i+1}={d:.4f}' for i, d in enumerate(chroma_distances))
        lines.append(f'  {_DIM}ChromaDB L2² distances: {cd_str}{_RESET}')

    lines.append('')

    # emit as a single log.info call so it stays atomic in the terminal
    log.info('\n'.join(lines))
