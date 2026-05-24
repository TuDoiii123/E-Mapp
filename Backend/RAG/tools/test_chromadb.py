"""Kiểm tra ChromaDB: query thử và xác nhận embedding hoạt động đúng."""
import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from sentence_transformers import SentenceTransformer

_RAG_DIR     = Path(__file__).parent.parent
_CHROMA_PATH = _RAG_DIR / 'chroma_db' / 'chroma_db_faqs'
_MODEL_PATH  = _RAG_DIR / 'models' / 'Vietnamese_Embedding'
_COLLECTION  = 'faqs_collection'

TEST_QUERIES = [
    'Thủ tục đăng ký kết hôn cần giấy tờ gì?',
    'Làm sổ đỏ mất bao lâu?',
    'Bảo hiểm thất nghiệp hưởng bao nhiêu tháng?',
    'Chứng khoán nộp thuế như thế nào?',
    'Trẻ em bị bạo hành báo ở đâu?',
    'Cách bảo vệ quyền người tiêu dùng khi mua hàng online?',
    'Thủ tục thi hành án dân sự?',
    'Khởi nghiệp startup được nhà nước hỗ trợ gì?',
    'Luật thừa kế phân chia tài sản như thế nào?',
    'Phòng chống bão lũ cần chuẩn bị gì?',
]

def main():
    print('Loading embedding model...')
    if _MODEL_PATH.exists():
        model = SentenceTransformer(str(_MODEL_PATH))
        print(f'  Model: {_MODEL_PATH.name}')
    else:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print('  Model: paraphrase-multilingual-MiniLM-L12-v2')

    client = chromadb.PersistentClient(path=str(_CHROMA_PATH))
    col = client.get_collection(_COLLECTION)
    total = col.count()
    print(f'\nCollection "{_COLLECTION}": {total} docs')

    # Lấy thông tin distance metric
    meta_col = col.metadata or {}
    dist_fn = meta_col.get('hnsw:space', 'l2')
    print(f'Distance function: {dist_fn}\n')

    print('=== QUERY TEST ===')
    ok = 0
    for q in TEST_QUERIES:
        emb = model.encode([q]).tolist()
        res = col.query(query_embeddings=emb, n_results=1, include=['metadatas', 'distances', 'documents'])
        meta = res['metadatas'][0][0]
        dist = res['distances'][0][0]
        matched_q = (meta.get('question') or '')[:65]
        category  = meta.get('category', '')
        file_src  = meta.get('file', '')

        # L2 distance với Vietnamese_Embedding: match tốt ~ 500-900, xấu > 1500
        # Cosine distance: range 0-2, nhỏ hơn là tốt
        good = dist < 1200 if dist_fn == 'l2' else dist < 0.8
        status = 'OK ' if good else 'LOW'
        if good:
            ok += 1

        print(f'[{status}] dist={dist:.2f}')
        print(f'  Query  : {q}')
        print(f'  Matched: {matched_q}')
        print(f'  Source : {file_src} | Category: {category}')
        print()

    print(f'Result: {ok}/{len(TEST_QUERIES)} queries matched')
    print(f'ChromaDB total: {total} docs')
    print('Status: READY' if ok >= 8 else 'WARNING: co the co van de voi embedding')

if __name__ == '__main__':
    main()
