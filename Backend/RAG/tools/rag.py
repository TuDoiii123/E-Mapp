from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

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
        logger.debug("Attempted to get embedding for empty text.")
        return []

    model = load_model()
    embedding = model.encode(text)

    return embedding.tolist()

def search_project_documents(query: str):
    query_embed = get_embedding(query)
    answer = []
    collection = connect_chroma_db()
    results = collection.query(
        query_embeddings=[query_embed],  # danh sách các vector query
        n_results=5  # số kết quả muốn lấy
    )
    for doc in results["metadatas"][0]:
        answer.append(doc.get("answer_text"))
    return answer






