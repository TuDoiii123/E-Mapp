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
_MODEL_PATH = _RAG_DIR / "models" / "Vietnamese_Embedding"
_CHROMA_PATH = _RAG_DIR / "chroma_db" / "chroma_db_faqs"


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


@lru_cache(maxsize=1)
def connect_chroma_db():
    client = chromadb.PersistentClient(path=str(_CHROMA_PATH))
    collection = client.get_collection("faqs_collection")
    return collection


def get_embedding(text: str) -> list:
    if not text.strip():
        logger.debug("get_embedding: empty text skipped")
        return []
    model = load_model()
    return model.encode(text).tolist()


def search_project_documents(query: str):
    query_embed = get_embedding(query)
    collection = connect_chroma_db()

    # Request embeddings so we can compute our own metrics
    results = collection.query(
        query_embeddings=[query_embed],
        n_results=5,
        include=["metadatas", "documents", "distances", "embeddings"],
    )

    metadatas        = results["metadatas"][0]        # list[dict]
    chroma_distances = results["distances"][0]        # list[float]  (L2² by default)
    doc_embeddings   = results.get("embeddings", [[]])[0]  # list[list[float]]

    # ── log accuracy metrics to terminal ─────────────────────────────────────
    if doc_embeddings and len(doc_embeddings) == len(metadatas):
        try:
            log_retrieval_metrics(
                query=query,
                query_vec=query_embed,
                doc_embeddings=doc_embeddings,
                doc_metadatas=metadatas,
                chroma_distances=chroma_distances,
            )
        except Exception as exc:
            logger.warning('rag_metrics logging failed: %s', exc)

    return [doc.get("answer_text") for doc in metadatas]






