import os
import shutil
import logging
from datetime import datetime
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import time

# ==============================================================================
# PHẦN 1: LOGGER
# ==============================================================================

def setup_logger(log_dir: str = r"C:/Users/ADMIN/E-Map/Backend/v1/create_vecto_db/logs"):
    """Khởi tạo logger."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"vector_db_log_{timestamp}.log")

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("=== Logger initialized ===")
    return logging


# ==============================================================================
# PHẦN 2: LOAD MODEL
# ==============================================================================

def load_embedding_model(model_path: str) -> SentenceTransformer:
    try:
        logging.info(f"Đang tải mô hình embedding: {model_path}")
        model = SentenceTransformer(model_path)
        logging.info("Tải mô hình embedding thành công")
        return model
    except Exception as e:
        logging.error(f"Lỗi tải mô hình embedding: {e}")
        raise


# ==============================================================================
# PHẦN 3: XÓA DB CŨ
# ==============================================================================

def clear_chroma_db_folder(db_path: str):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        logging.info(f"Đã xoá DB cũ: {db_path}")
    os.makedirs(db_path, exist_ok=True)


# ==============================================================================
# PHẦN 4: XỬ LÝ DỮ LIỆU
# ==============================================================================

def load_and_prepare_faq_data(csv_path: str) -> pd.DataFrame:
    try:
        logging.info(f"Đang đọc dữ liệu CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        required = ["id", "title", "answer_text"]
        if not all(c in df.columns for c in required):
            logging.error(f"Thiếu các cột bắt buộc: {required}")
            return pd.DataFrame()

        df.dropna(subset=required, inplace=True)

        # Xử lý ID
        df.drop_duplicates(subset=["id"], keep="first", inplace=True)
        df["id"] = df["id"].astype(str)

        # Metadata optional
        for col in ["source_url", "answer_html"]:
            if col in df.columns:
                df[col].fillna("N/A", inplace=True)

        logging.info(f"Đã load {len(df)} FAQ.")
        return df

    except Exception as e:
        logging.error(f"Lỗi đọc CSV: {e}")
        return pd.DataFrame()


# ==============================================================================
# PHẦN 5: TẠO EMBEDDINGS
# ==============================================================================

def create_faq_embeddings(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    try:
        logging.info(f"Tạo embedding cho {len(texts)} câu hỏi...")
        t1 = time.time()
        embeddings = model.encode(texts, show_progress_bar=True)
        t2 = time.time()
        logging.info(f"Tạo embeddings xong trong {t2 - t1:.2f}s")
        return embeddings.tolist()
    except Exception as e:
        logging.error(f"Lỗi tạo embedding: {e}")
        return []


# ==============================================================================
# PHẦN 6: LƯU VÀO CHROMADB (CÓ CHIA BATCH)
# ==============================================================================

def store_in_chromadb(
    db_path: str,
    collection_name: str,
    faq_df: pd.DataFrame,
    embeddings: list[list[float]],
    batch_size: int = 4000
):
    try:
        client = chromadb.PersistentClient(path=db_path)

        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logging.info(f"Dùng collection: {collection_name}")

        ids = faq_df["id"].tolist()
        docs = faq_df["title"].tolist()
        metas = faq_df.to_dict(orient="records")

        total = len(ids)
        logging.info(f"Upsert {total} items (batch={batch_size})")

        for i in range(0, total, batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_docs = docs[i:i+batch_size]
            batch_meta = metas[i:i+batch_size]
            batch_emb = embeddings[i:i+batch_size]

            logging.info(f"Upsert batch {i} → {i+len(batch_ids)}")

            collection.upsert(
                ids=batch_ids,
                embeddings=batch_emb,
                documents=batch_docs,
                metadatas=batch_meta
            )

        logging.info(f"Upsert xong. Tổng số record: {collection.count()}")

    except Exception as e:
        logging.error(f"Lỗi ChromaDB: {e}")


# ==============================================================================
# PHẦN 7: MAIN
# ==============================================================================

if __name__ == "__main__":
    logger = setup_logger()

    try:
        CONFIG_PATH = r"C:/Users/ADMIN/E-Map/Backend/v1/create_vecto_db/config.json"
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        logger.error("Không tìm thấy config.json")
        exit()

    CSV_PATH = config["faq_csv_path"]
    DB_PATH = os.path.join(config["db_path"], config["db_folder"])
    MODEL_PATH = config["local_model_path"]
    COLLECTION = config["collection_name"]

    # Xóa DB cũ (nếu muốn chạy lại từ đầu)
    # clear_chroma_db_folder(DB_PATH)

    df = load_and_prepare_faq_data(CSV_PATH)
    if df.empty:
        logger.error("Không có dữ liệu để xử lý.")
        exit()

    model = load_embedding_model(MODEL_PATH)

    titles = df["title"].tolist()
    embeds = create_faq_embeddings(model, titles)

    if embeds:
        store_in_chromadb(DB_PATH, COLLECTION, df, embeds, batch_size=4000)
        logger.info("=== Hoàn tất tạo VectorDB ===")
    else:
        logger.error("Không thể tạo embeddings! Dừng tiến trình.")
