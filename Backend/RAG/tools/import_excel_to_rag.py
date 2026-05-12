"""
Import dữ liệu từ các file Excel trong RAG/data/ vào ChromaDB.

Chạy:
  python Backend/RAG/tools/import_excel_to_rag.py
  python Backend/RAG/tools/import_excel_to_rag.py --reset   # xóa collection cũ và import lại
  python Backend/RAG/tools/import_excel_to_rag.py --file faq_ho_tich.xlsx  # chỉ import 1 file

Yêu cầu: openpyxl, pandas, chromadb, sentence-transformers
"""
import sys
import os
import argparse
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

_RAG_DIR   = Path(__file__).parent.parent
_DATA_DIR  = _RAG_DIR / 'data'
_CHROMA_PATH = _RAG_DIR / 'chroma_db' / 'chroma_db_faqs'
_MODEL_PATH  = _RAG_DIR / 'models' / 'Vietnamese_Embedding'
_COLLECTION  = 'faqs_collection'

EXCEL_FILES = [
    # Batch 1
    'faq_ho_tich.xlsx',
    'faq_dat_dai.xlsx',
    'faq_cccd_cu_tru.xlsx',
    'faq_giao_thong.xlsx',
    'faq_kinh_doanh.xlsx',
    'faq_bhxh_bhyt.xlsx',
    'faq_thue.xlsx',
    'faq_xay_dung.xlsx',
    'faq_chung.xlsx',
    # Batch 2
    'faq_tu_phap.xlsx',
    'faq_lao_dong.xlsx',
    'faq_y_te.xlsx',
    'faq_giao_duc.xlsx',
    'faq_moi_truong.xlsx',
    'faq_dau_tu.xlsx',
    'faq_khieu_nai.xlsx',
    'faq_nong_nghiep.xlsx',
    # Batch 3
    'faq_ngan_hang.xlsx',
    'faq_ho_tich_2.xlsx',
    'faq_dat_dai_2.xlsx',
    'faq_lao_dong_2.xlsx',
    'faq_thue_2.xlsx',
    'faq_giao_thong_2.xlsx',
    'faq_xay_dung_2.xlsx',
    'faq_xa_hoi.xlsx',
    'faq_pccc.xlsx',
    'faq_vien_thong.xlsx',
    # Batch 4
    'faq_y_te_2.xlsx',
    'faq_giao_duc_2.xlsx',
    'faq_nong_nghiep_2.xlsx',
    'faq_moi_truong_2.xlsx',
    'faq_van_hoa.xlsx',
    'faq_ton_giao.xlsx',
    'faq_khoa_hoc.xlsx',
    'faq_an_ninh.xlsx',
    # Batch 5
    'faq_tien_ich.xlsx',
    'faq_xuat_nhap_canh.xlsx',
    'faq_kinh_doanh_2.xlsx',
    # Batch 6 — chung toàn quốc
    'faq_g_ho_tich.xlsx',
    'faq_g_dat_dai.xlsx',
    'faq_g_cccd_cu_tru.xlsx',
    'faq_g_lao_dong.xlsx',
    'faq_g_thue.xlsx',
    'faq_g_y_te.xlsx',
    'faq_g_kinh_doanh.xlsx',
    'faq_g_xay_dung.xlsx',
    'faq_g_an_ninh.xlsx',
    'faq_g_dvc.xlsx',
    # Batch 7 — chung toàn quốc (tiếp)
    'faq_g_bhxh.xlsx',
    'faq_g_dan_su.xlsx',
    'faq_g_hanh_chinh.xlsx',
    'faq_g_giao_thong.xlsx',
    'faq_g_moi_truong.xlsx',
    'faq_g_tu_phap.xlsx',
    'faq_g_giao_duc.xlsx',
    'faq_g_ngan_hang.xlsx',
]


def load_model() -> SentenceTransformer:
    if not _MODEL_PATH.exists():
        print(f'[WARN] Model path not found: {_MODEL_PATH}')
        print('       Dung model da cai dat san: paraphrase-multilingual-MiniLM-L12-v2')
        return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print(f'Loading embedding model from {_MODEL_PATH} ...')
    return SentenceTransformer(str(_MODEL_PATH))


def get_or_create_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(_CHROMA_PATH))
    if reset:
        try:
            client.delete_collection(_COLLECTION)
            print(f'[RESET] Collection "{_COLLECTION}" da xoa.')
        except Exception:
            pass
    try:
        collection = client.get_collection(_COLLECTION)
        print(f'[OK] Collection "{_COLLECTION}" da ton tai ({collection.count()} docs).')
    except Exception:
        collection = client.create_collection(_COLLECTION)
        print(f'[OK] Tao moi collection "{_COLLECTION}".')
    return collection


def load_excel(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='FAQ', dtype=str)
    df = df.fillna('')
    required = {'id', 'question', 'answer'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'File {path.name} thieu cot: {missing}')
    return df


def build_document_text(row: pd.Series) -> str:
    """Ghép question + answer thành đoạn văn để embed."""
    question = (row.get('question') or '').strip()
    answer   = (row.get('answer')   or '').strip()
    category = (row.get('category') or '').strip()
    proc     = (row.get('procedure') or '').strip()

    parts = []
    if category:
        parts.append(f'Danh muc: {category}.')
    if proc:
        parts.append(f'Thu tuc: {proc}.')
    if question:
        parts.append(f'Cau hoi: {question}')
    if answer:
        parts.append(f'Tra loi: {answer}')
    return '\n'.join(parts)


def import_file(file_path: Path, model: SentenceTransformer, collection, batch_size: int = 32) -> int:
    print(f'\n  -- {file_path.name} --')
    df = load_excel(file_path)

    # Lấy danh sách id đã có trong collection để tránh trùng
    existing_ids: set = set()
    try:
        existing = collection.get(include=[])
        existing_ids = set(existing.get('ids', []))
    except Exception:
        pass

    docs, embeddings, metadatas, ids = [], [], [], []
    skipped = 0

    for _, row in df.iterrows():
        raw_id = str(row.get('id') or '').strip()
        doc_id = raw_id if raw_id else f'excel-{uuid.uuid4().hex[:8]}'

        if doc_id in existing_ids:
            skipped += 1
            continue

        text = build_document_text(row)
        if not text.strip():
            continue

        answer_text = str(row.get('answer') or '').strip()
        meta = {
            'doc_id':    doc_id,
            'category':  str(row.get('category')  or ''),
            'procedure': str(row.get('procedure')  or ''),
            'level':     str(row.get('level')      or ''),
            'source':    str(row.get('source')     or ''),
            'question':  str(row.get('question')   or '')[:500],
            'answer_text': answer_text[:2000],
            'file':      file_path.name,
        }

        docs.append(text)
        metadatas.append(meta)
        ids.append(doc_id)

    if not docs:
        print(f'    (khong co ban ghi moi, bo qua {skipped} da ton tai)')
        return 0

    # Embed theo batch
    inserted = 0
    for i in range(0, len(docs), batch_size):
        batch_docs  = docs[i:i + batch_size]
        batch_meta  = metadatas[i:i + batch_size]
        batch_ids   = ids[i:i + batch_size]
        batch_embs  = model.encode(batch_docs, show_progress_bar=False).tolist()

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embs,
            documents=batch_docs,
            metadatas=batch_meta,
        )
        inserted += len(batch_ids)
        print(f'    [{i + len(batch_docs)}/{len(docs)}] embedded & upserted')

    if skipped:
        print(f'    Bo qua {skipped} ban ghi da co trong collection.')
    print(f'    => Them {inserted} ban ghi moi.')
    return inserted


def main():
    parser = argparse.ArgumentParser(description='Import Excel FAQ vao ChromaDB RAG')
    parser.add_argument('--reset', action='store_true', help='Xoa collection cu truoc khi import')
    parser.add_argument('--file',  type=str, default=None, help='Chi import 1 file cu the')
    args = parser.parse_args()

    model      = load_model()
    collection = get_or_create_collection(reset=args.reset)

    if args.file:
        target = _DATA_DIR / args.file
        if not target.exists():
            print(f'[ERROR] Khong tim thay file: {target}')
            sys.exit(1)
        files = [target]
    else:
        files = [_DATA_DIR / f for f in EXCEL_FILES if (_DATA_DIR / f).exists()]
        missing = [f for f in EXCEL_FILES if not (_DATA_DIR / f).exists()]
        if missing:
            print(f'[WARN] Chua tim thay: {missing} — bo qua.')

    total = 0
    for f in files:
        total += import_file(f, model, collection)

    print(f'\nHoan thanh. Tong cong them {total} ban ghi moi.')
    print(f'Collection hien co: {collection.count()} docs.')


if __name__ == '__main__':
    main()
