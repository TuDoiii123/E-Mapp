from pathlib import Path
import sys
import chromadb
from sentence_transformers import SentenceTransformer
from functools import lru_cache

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from logger import get_logger
from RAG.utils.rag_metrics import log_retrieval_metrics

logger = get_logger('rag.retrieval')

_RAG_DIR = Path(__file__).parent.parent  # RAG/
_MODEL_PATH  = _RAG_DIR / "models" / "Vietnamese_Embedding"
_CHROMA_PATH = _RAG_DIR / "chroma_db" / "chroma_db_faqs"
_CHROMA_PATH_TH = _RAG_DIR / "chroma_db" / "thanhhoa"  # Thanh Hóa DVC collections

# Collections được query theo thứ tự ưu tiên (tên collection, đường dẫn chroma db)
_COLLECTIONS = [
    ("faqs_collection",  _CHROMA_PATH),
    ("thanhhoa_ubnd",    _CHROMA_PATH_TH),
    ("thanhhoa_congan",  _CHROMA_PATH_TH),
]

# Ngưỡng cosine tối thiểu — kết quả dưới ngưỡng này bị loại bỏ
_MIN_COSINE = 0.30


_HF_MODEL_REPO  = "AITeamVN/Vietnamese_Embedding"
_HF_TOKENIZER_REPO = "BAAI/bge-m3"

_REQUIRED_MODEL_FILES = {"config.json", "model.safetensors", "modules.json"}
_TOKENIZER_FILES      = {"tokenizer.json", "sentencepiece.bpe.model"}


def _model_is_ready(path: Path) -> bool:
    existing = {f.name for f in path.iterdir() if f.is_file()} if path.exists() else set()
    return _REQUIRED_MODEL_FILES.issubset(existing) and _TOKENIZER_FILES.issubset(existing)


def _hf_download(repo_id: str, filename: str, local_dir: Path) -> None:
    from huggingface_hub import hf_hub_download
    import inspect
    sig = inspect.signature(hf_hub_download).parameters
    kwargs: dict = {"repo_id": repo_id, "filename": filename, "local_dir": str(local_dir)}
    if "local_dir_use_symlinks" in sig:
        kwargs["local_dir_use_symlinks"] = False
    hf_hub_download(**kwargs)


def _download_missing_files(path: Path) -> None:
    """Download model weights + tokenizer files còn thiếu từ HuggingFace."""
    path.mkdir(parents=True, exist_ok=True)

    # Model weights — từ AITeamVN/Vietnamese_Embedding
    weight_files = [f for f in _REQUIRED_MODEL_FILES if not (path / f).exists()]
    if weight_files:
        logger.info("Thiếu model weights %s — download từ %s ...", weight_files, _HF_MODEL_REPO)
        try:
            for fname in weight_files:
                logger.info("  Downloading %s ...", fname)
                _hf_download(_HF_MODEL_REPO, fname, path)
                logger.info("  [ok] %s", fname)
        except Exception as exc:
            raise RuntimeError(
                f"Không thể download model weights: {exc}\n"
                f"Chạy thủ công: python Backend/RAG/models/setup_rag_model.py"
            ) from exc

    # Tokenizer — từ BAAI/bge-m3 (dùng chung tokenizer với Vietnamese_Embedding)
    tok_files = [f for f in _TOKENIZER_FILES if not (path / f).exists()]
    if tok_files:
        logger.info("Thiếu tokenizer files %s — download từ %s ...", tok_files, _HF_TOKENIZER_REPO)
        try:
            for fname in tok_files:
                logger.info("  Downloading %s ...", fname)
                _hf_download(_HF_TOKENIZER_REPO, fname, path)
                logger.info("  [ok] %s", fname)
        except Exception as exc:
            raise RuntimeError(
                f"Không thể download tokenizer: {exc}\n"
                f"Chạy thủ công: python Backend/RAG/models/setup_rag_model.py"
            ) from exc


@lru_cache(maxsize=1)
def load_model():
    if not _model_is_ready(_MODEL_PATH):
        _download_missing_files(_MODEL_PATH)
    model = SentenceTransformer(str(_MODEL_PATH))
    return model


@lru_cache(maxsize=4)
def _get_collection(chroma_path: str, collection_name: str):
    """Mở một ChromaDB collection, trả None nếu không tồn tại."""
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        return client.get_collection(collection_name)
    except Exception as e:
        logger.debug("Collection %s không tồn tại (%s)", collection_name, e)
        return None


def get_embedding(text: str) -> list:
    if not text.strip():
        logger.debug("get_embedding: empty text skipped")
        return []
    model = load_model()
    # normalize_embeddings=True → unit vector → cosine ≡ dot product, L2 đúng hơn
    return model.encode(text, normalize_embeddings=True).tolist()


def _query_collection(collection, query_embed: list, n: int = 5) -> list[dict]:
    """Query một collection, trả về list {cosine, metadata}."""
    try:
        results = collection.query(
            query_embeddings=[query_embed],
            n_results=n,
            include=["metadatas", "distances", "embeddings"],
        )
    except Exception as e:
        logger.warning("Query collection lỗi: %s", e)
        return []

    metadatas  = results["metadatas"][0]
    distances  = results["distances"][0]   # cosine space → distance = 1 - cosine
    embeddings = results.get("embeddings", [[]])[0]

    # Log metrics
    if embeddings and len(embeddings) == len(metadatas):
        try:
            log_retrieval_metrics(
                query="(multi-collection)",
                query_vec=query_embed,
                doc_embeddings=embeddings,
                doc_metadatas=metadatas,
                chroma_distances=distances,
            )
        except Exception:
            pass

    hits = []
    for meta, dist in zip(metadatas, distances):
        cosine = 1.0 - dist  # ChromaDB cosine space: distance = 1 - similarity
        if cosine >= _MIN_COSINE:
            hits.append({"cosine": cosine, "meta": meta})
    return hits


def search_project_documents(query: str):
    """
    Tìm kiếm trên tất cả collections, merge kết quả theo cosine giảm dần.
    Trả về top-5 answer_text tốt nhất.
    """
    query_embed = get_embedding(query)
    if not query_embed:
        return []

    all_hits: list[dict] = []

    for col_name, chroma_path in _COLLECTIONS:
        col = _get_collection(str(chroma_path), col_name)
        if col is None:
            continue
        hits = _query_collection(col, query_embed, n_results=5)
        for h in hits:
            h["source"] = col_name
        all_hits.extend(hits)
        logger.debug("[RAG] %s → %d hits (≥%.2f)", col_name, len(hits), _MIN_COSINE)

    if not all_hits:
        logger.warning("[RAG] Không có kết quả nào vượt ngưỡng %.2f trên %d collections",
                       _MIN_COSINE, len(_COLLECTIONS))
        return []

    # Sắp xếp theo cosine giảm dần, lấy top-5
    all_hits.sort(key=lambda x: x["cosine"], reverse=True)
    top = all_hits[:5]

    logger.info("[RAG] Top-%d từ %d collections: cosine=[%s]",
                len(top), len(_COLLECTIONS),
                ", ".join(f"{h['cosine']:.3f}({h['source']})" for h in top))

    return [h["meta"].get("answer_text") or h["meta"].get("answer") or "" for h in top]






