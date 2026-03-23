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


@lru_cache(maxsize=1)
def load_model():
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






