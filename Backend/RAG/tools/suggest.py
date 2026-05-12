"""
SuggestProcedure tool — gợi ý thủ tục hành chính phù hợp với câu hỏi người dùng.

Được đăng ký vào TOOL_REGISTRY để task_analyzer (LLM) tự động gọi khi phát hiện
người dùng hỏi về thủ tục / dịch vụ công.
"""
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from logger import get_logger

log = get_logger('rag.suggest')

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    import pandas as pd
except Exception:
    SentenceTransformer = None  # type: ignore
    cos_sim = None              # type: ignore
    pd = None                   # type: ignore

# ── Singletons (lazy-loaded, tái sử dụng qua mọi lần gọi) ────────────────────
_model = None
_df = None
_embeddings = None
_query_map: Dict[str, List[Dict[str, Any]]] = {}

_BASE_DIR   = Path(__file__).parent.parent.parent          # Backend/
_CSV_PATH   = _BASE_DIR / 'SuggestProcedure' / 'data' / 'dichvucong_QuangNinh - dichvucong_QuangNinh.csv'
_SEED_CSV   = _BASE_DIR / 'SuggestProcedure' / 'data' / 'procedures_seed.csv'
_MODEL_PATH = _BASE_DIR / 'SuggestProcedure' / 'model' / 'fine_tuned_model'
_RANK_PATH  = _BASE_DIR / 'SuggestProcedure' / 'data' / 'query_procedure_ranking_quangninh.csv'
_FALLBACK_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


def _resolve_csv() -> Path:
    """Trả về path CSV khả dụng: ưu tiên bộ Quảng Ninh, fallback về seed."""
    if _CSV_PATH.is_file():
        return _CSV_PATH
    if _SEED_CSV.is_file():
        log.warning('[SuggestProcedure] Dung bo du lieu seed (procedures_seed.csv).')
        return _SEED_CSV
    # Auto-generate seed CSV on-the-fly
    try:
        seed_script = _BASE_DIR / 'SuggestProcedure' / 'data' / 'generate_seed_csv.py'
        if seed_script.is_file():
            import subprocess, sys as _sys
            subprocess.run([_sys.executable, str(seed_script)], check=True, capture_output=True)
            if _SEED_CSV.is_file():
                log.info('[SuggestProcedure] Seed CSV tu dong tao xong.')
                return _SEED_CSV
    except Exception as _gen_err:
        log.warning(f'[SuggestProcedure] Auto-generate seed that bai: {_gen_err}')
    raise FileNotFoundError(
        f'Khong tim thay CSV: {_CSV_PATH}\n'
        f'Chay: python {_BASE_DIR / "SuggestProcedure" / "data" / "generate_seed_csv.py"}'
    )


def init_suggest() -> tuple:
    """
    Khởi tạo model + data một lần duy nhất (singleton).
    Trả về (model, df, embeddings) hoặc raise nếu thất bại.
    """
    global _model, _df, _embeddings, _query_map

    if _model is not None and _df is not None and _embeddings is not None:
        return _model, _df, _embeddings

    if SentenceTransformer is None or pd is None:
        raise RuntimeError('sentence-transformers hoặc pandas chưa được cài đặt.')

    # ── Load CSV ──────────────────────────────────────────────────────────────
    csv_path = _resolve_csv()
    _df = pd.read_csv(str(csv_path))
    if 'NAME' not in _df.columns:
        raise RuntimeError("CSV thiếu cột 'NAME'")

    # ── Load ranking map (nếu có) ─────────────────────────────────────────────
    if not _query_map and _RANK_PATH.is_file():
        try:
            rank_df = pd.read_csv(str(_RANK_PATH))
            rename = {}
            for c in rank_df.columns:
                cl = c.lower()
                if cl == 'relevance':
                    rename[c] = 'label'
                elif cl in ('query_id', 'query_text', 'procedure_id', 'procedure_code', 'procedure_name'):
                    rename[c] = cl
            if rename:
                rank_df.rename(columns=rename, inplace=True)
            required = {'query_text', 'procedure_id', 'procedure_name', 'label'}
            if required.issubset(set(rank_df.columns)):
                rank_df['label'] = pd.to_numeric(rank_df['label'], errors='coerce')
                for _, row in rank_df[rank_df['label'].fillna(0) > 0].iterrows():
                    qtxt = str(row.get('query_text', '')).strip()
                    if not qtxt:
                        continue
                    key = re.sub(r'[^\w\s]', '', qtxt.lower()).strip()
                    _query_map.setdefault(key, []).append({
                        'procedure_id':   row.get('procedure_id'),
                        'procedure_code': row.get('procedure_code'),
                        'procedure_name': row.get('procedure_name'),
                        'label':          int(row.get('label', 1)),
                    })
                log.info(f'[SuggestProcedure] Ranking map: {len(_query_map)} entries')
        except Exception as exc:
            log.warning(f'[SuggestProcedure] Ranking CSV bị lỗi (bỏ qua): {exc}')

    # ── Load model ────────────────────────────────────────────────────────────
    fine_tuned_ok = (
        _MODEL_PATH.is_dir()
        and all((_MODEL_PATH / f).is_file() for f in ['config.json', 'model.safetensors', 'bpe.codes'])
    )
    model_name = str(_MODEL_PATH) if fine_tuned_ok else _FALLBACK_MODEL
    if not fine_tuned_ok:
        log.warning(f'[SuggestProcedure] Fine-tuned model không đủ file → dùng fallback: {_FALLBACK_MODEL}')

    try:
        _model = SentenceTransformer(model_name)
        names = _df['NAME'].astype(str).tolist()
        _embeddings = _model.encode(names, convert_to_tensor=True)
        log.info(f'[SuggestProcedure] Sẵn sàng — {len(names)} thủ tục, model: {model_name}')
    except Exception as exc:
        log.error(f'[SuggestProcedure] Lỗi load model: {exc}')
        _model = _df = _embeddings = None
        raise

    return _model, _df, _embeddings


def suggest_procedures(query: str, top_k: int = 4, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Gợi ý tối đa `top_k` thủ tục hành chính liên quan đến `query`.

    Kết quả:
        {
          'suggestions': [...],
          'explanation': str,
          'total_candidates': int
        }
    """
    try:
        model, df, embeddings = init_suggest()
    except Exception as exc:
        return {'suggestions': [], 'explanation': f'Lỗi khởi tạo: {exc}', 'error': 'init_failed'}

    link_base = os.getenv('PROCEDURE_LINK_BASE', 'https://dichvucong.gov.vn/thu-tuc/')

    def _link(pid: Any, name: str) -> str:
        slug = re.sub(r'[^a-zA-Z0-9\- ]', '', name.lower()).strip().replace(' ', '-')
        return f'{link_base}{pid}-{slug}' if pid and str(pid).strip() else f'{link_base}{slug}'

    # Ưu tiên ranking label (exact match)
    norm_q = re.sub(r'[^\w\s]', '', query.lower()).strip()
    suggestions: List[Dict[str, Any]] = []
    for hit in _query_map.get(norm_q, [])[:top_k]:
        pid, pname = hit.get('procedure_id'), hit.get('procedure_name')
        suggestions.append({
            'procedure_internal_id': pid,
            'procedure_name':  pname,
            'procedure_code':  hit.get('procedure_code'),
            'similarity_score': 1.0,
            'source':          'ranking_label',
            'link':            _link(pid, str(pname)),
        })

    # Bổ sung bằng embedding search
    remaining = top_k - len(suggestions)
    if remaining > 0:
        q_emb = model.encode(query, convert_to_tensor=True)
        scores = cos_sim(q_emb, embeddings)[0].cpu().numpy().tolist()
        existing = {s['procedure_name'] for s in suggestions}
        scored = sorted(
            [
                {
                    'procedure_internal_id': int(df['ID'].iloc[i]) if 'ID' in df.columns else i,
                    'procedure_name':  df['NAME'].iloc[i],
                    'procedure_code':  None,
                    'similarity_score': round(float(s), 4),
                    'source':          'embedding',
                    'link':            _link(int(df['ID'].iloc[i]) if 'ID' in df.columns else i, str(df['NAME'].iloc[i])),
                }
                for i, s in enumerate(scores) if s >= threshold
            ],
            key=lambda x: x['similarity_score'],
            reverse=True,
        )
        for item in scored:
            if item['procedure_name'] not in existing:
                suggestions.append(item)
            if len(suggestions) >= top_k:
                break

    explanation = (
        'Các thủ tục hành chính liên quan được đề xuất dựa trên yêu cầu của bạn.'
        if suggestions else
        'Không tìm thấy thủ tục phù hợp với yêu cầu.'
    )
    return {'suggestions': suggestions, 'explanation': explanation, 'total_candidates': len(suggestions)}


def suggest_procedures_tool(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Tool wrapper cho TOOL_REGISTRY.
    Trả về list các suggestion (serializable) để llm_response tổng hợp.
    """
    result = suggest_procedures(query=query, top_k=top_k)
    return result.get('suggestions', [])
