"""
Script embedding dữ liệu Thanh Hóa vào ChromaDB.
Xử lý 3 nguồn dữ liệu:
  - ChiTiet_DVC_CôngAn  (159 thủ tục)
  - ChiTiet_DVC_UBND    (1500 dịch vụ công trực tuyến)
  - Địa_Điểm_DVC_TH     (98k+ địa điểm)
"""

import os, sys, time, json, shutil, logging
from datetime import datetime
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
BASE_DATA = r"C:\Users\ADMIN\E-Mapp\Backend\RAG\Thanh Hóa-20260316T123545Z-3-001\Thanh Hóa"
MODEL_PATH = r"C:\Users\ADMIN\E-Mapp\Backend\RAG\models\Vietnamese_Embedding"
CHROMA_DIR = r"C:\Users\ADMIN\E-Mapp\Backend\RAG\chroma_db\thanhhoa"
LOG_DIR    = r"C:\Users\ADMIN\E-Mapp\Backend\RAG\create_vecto_db\logs"
BATCH_SIZE = 2000

COLLECTIONS = {
    "congán_thủtục":  "thanhhoa_congan",
    "ubnd_dvc":       "thanhhoa_ubnd",
    "địa_điểm":       "thanhhoa_diadiem",
}

# ──────────────────────────────────────────────
# LOGGER
# ──────────────────────────────────────────────
def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"thanhhoa_{ts}.log")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.stream.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            stream_handler,
        ]
    )
    logging.info("=== Bắt đầu embedding dữ liệu Thanh Hóa ===")


# ──────────────────────────────────────────────
# LOAD MODEL
# ──────────────────────────────────────────────
def load_model():
    logging.info(f"Tải mô hình: {MODEL_PATH}")
    model = SentenceTransformer(MODEL_PATH)
    logging.info("Tải mô hình OK")
    return model


# ──────────────────────────────────────────────
# EMBED + UPSERT
# ──────────────────────────────────────────────
def embed_and_store(model, client, collection_name, records: list[dict]):
    """
    records: list of {id, title, answer_text, **metadata}
    title được dùng để embed, answer_text lưu vào metadata để truy xuất.
    """
    if not records:
        logging.warning(f"[{collection_name}] Không có dữ liệu.")
        return

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    ids     = [r["id"] for r in records]
    titles  = [r["title"] for r in records]
    metas   = [{k: str(v)[:2000] for k, v in r.items()} for r in records]

    logging.info(f"[{collection_name}] Tạo embeddings cho {len(titles)} mục...")
    t0 = time.time()
    embeddings = model.encode(titles, show_progress_bar=True, batch_size=32)
    logging.info(f"[{collection_name}] Embedding xong sau {time.time()-t0:.1f}s")

    total = len(ids)
    for i in range(0, total, BATCH_SIZE):
        sl = slice(i, i + BATCH_SIZE)
        collection.upsert(
            ids=ids[sl],
            embeddings=embeddings[sl].tolist(),
            documents=titles[sl],
            metadatas=metas[sl],
        )
        logging.info(f"[{collection_name}] Upsert {i}–{min(i+BATCH_SIZE, total)}/{total}")

    logging.info(f"[{collection_name}] Tổng record: {collection.count()}")


# ──────────────────────────────────────────────
# ĐỌC DỮ LIỆU
# ──────────────────────────────────────────────
def read_csv(path, encodings=("utf-8-sig", "utf-8", "cp1252")):
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    raise ValueError(f"Không đọc được: {path}")


def safe_str(val, limit=1000):
    if pd.isna(val):
        return ""
    return str(val)[:limit].strip()


# ──────────────────────────────────────────────
# NGUỒN 1: CÔNG AN – CHI TIẾT THỦ TỤC
# ──────────────────────────────────────────────
def prepare_congan():
    folder = os.path.join(BASE_DATA, "ChiTiet_DVC_CôngAn")
    ds = read_csv(os.path.join(folder, "DS_DichVuCong.csv"))
    ct = read_csv(os.path.join(folder, "ChiTiet_ThuTuc.csv"))

    merged = ds.merge(ct, on="URL_Chi_Tiet", how="left")

    records = []
    for idx, row in merged.iterrows():
        title = safe_str(row.get("Ten_Dich_Vu", ""))
        if not title:
            continue

        answer_parts = []
        for col, label in [
            ("trình_tự,_cách_thức_thực_hiện", "Trình tự thực hiện"),
            ("thành_phần_hồ_sơ",              "Hồ sơ cần nộp"),
            ("thời_hạn_giải_quyết",           "Thời hạn"),
            ("phí,_lệ_phí_(nếu_có)",          "Phí/lệ phí"),
            ("yêu_cầu_hoặc_điều_kiện_để_thực_hiện_tthc", "Yêu cầu/điều kiện"),
            ("kết_quả_thực_hiện_tthc",        "Kết quả"),
            ("cơ_quan_thực_hiện_tthc",        "Cơ quan thực hiện"),
        ]:
            val = safe_str(row.get(col, ""), 500)
            if val:
                answer_parts.append(f"{label}: {val}")

        records.append({
            "id":          f"congan_{idx}",
            "title":       title,
            "answer_text": "\n".join(answer_parts),
            "the_loai":    safe_str(row.get("The_Loai_Chinh", "")),
            "noi_lam":     safe_str(row.get("Noi_lam_Dich_Vu", ""), 300),
            "url":         safe_str(row.get("URL_Chi_Tiet", "")),
            "nguon":       "Công an Thanh Hóa",
        })

    logging.info(f"[CôngAn] {len(records)} thủ tục")
    return records


# ──────────────────────────────────────────────
# NGUỒN 2: UBND – DVC TRỰC TUYẾN
# ──────────────────────────────────────────────
def prepare_ubnd():
    folder = os.path.join(BASE_DATA, "ChiTiet_DVC_UBND")
    ds = read_csv(os.path.join(folder, "DS_DVC_TrucTuyen.csv"))
    ct = read_csv(os.path.join(folder, "ChiTiet_DVC_TrucTuyen.csv"))

    # Group ChiTiet by URL (tránh cartesian product khi merge)
    text_cols = [
        "trình_tự_thực_hiện", "cách_thức_thực_hiện",
        "thành_phần_hồ_sơ", "cơ_quan_thực_hiện",
        "yêu_cầu,_điều_kiện_thực_hiện"
    ]
    existing_cols = [c for c in text_cols if c in ct.columns]
    ct_grouped = (
        ct.groupby("URL_Chi_Tiet")[existing_cols]
        .first()  # lấy dòng đầu tiên mỗi URL (tránh trùng)
        .reset_index()
    )

    # Dedup DS trước để tránh duplicate IDs
    ds = ds.drop_duplicates(subset=["TTHC_MA"])
    merged = ds.merge(ct_grouped, on="URL_Chi_Tiet", how="left")

    records = []
    for enum_idx, (idx, row) in enumerate(merged.iterrows()):
        title = safe_str(row.get("NAME", ""))
        if not title:
            continue

        answer_parts = []
        for col, label in [
            ("trình_tự_thực_hiện",            "Trình tự thực hiện"),
            ("cách_thức_thực_hiện",           "Cách thức thực hiện"),
            ("thành_phần_hồ_sơ",             "Hồ sơ cần nộp"),
            ("cơ_quan_thực_hiện",            "Cơ quan thực hiện"),
            ("yêu_cầu,_điều_kiện_thực_hiện", "Yêu cầu/điều kiện"),
        ]:
            val = safe_str(row.get(col, ""), 500)
            if val:
                answer_parts.append(f"{label}: {val}")

        records.append({
            "id":          f"ubnd_{enum_idx}",
            "title":       title,
            "answer_text": "\n".join(answer_parts),
            "ma_tthc":     safe_str(row.get("TTHC_MA", "")),
            "url":         safe_str(row.get("URL_Chi_Tiet", "")),
            "nguon":       "UBND Thanh Hóa",
        })

    logging.info(f"[UBND] {len(records)} dịch vụ")
    return records


# ──────────────────────────────────────────────
# NGUỒN 3: ĐỊA ĐIỂM DVC
# ──────────────────────────────────────────────
def prepare_diadiem():
    folder = os.path.join(BASE_DATA, "Địa_Điểm_DVC_TH")
    df = read_csv(os.path.join(folder, "dichvucong_thanhhoa.csv"))
    df = df.dropna(subset=["NAME"])
    df = df.drop_duplicates(subset=["ID"])

    records = []
    for _, row in df.iterrows():
        name         = safe_str(row.get("NAME", ""))
        agency_name  = safe_str(row.get("AGENCY_NAME", ""))
        field        = safe_str(row.get("FIELD", ""))

        title = name
        answer_parts = []
        if agency_name:
            answer_parts.append(f"Cơ quan: {agency_name}")
        if field:
            answer_parts.append(f"Lĩnh vực: {field}")

        records.append({
            "id":          f"diadiem_{safe_str(row.get('ID', ''))}",
            "title":       title,
            "answer_text": "\n".join(answer_parts),
            "code":        safe_str(row.get("CODE", "")),
            "level":       safe_str(row.get("LEVE", "")),
            "nguon":       "Địa điểm DVC Thanh Hóa",
        })

    logging.info(f"[Địa điểm] {len(records)} địa điểm")
    return records


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    setup_logger()

    os.makedirs(CHROMA_DIR, exist_ok=True)

    model  = load_model()
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # --- CôngAn ---
    records_ca = prepare_congan()
    embed_and_store(model, client, COLLECTIONS["congán_thủtục"], records_ca)

    # --- UBND ---
    records_ub = prepare_ubnd()
    embed_and_store(model, client, COLLECTIONS["ubnd_dvc"], records_ub)

    # --- Địa điểm ---
    records_dd = prepare_diadiem()
    embed_and_store(model, client, COLLECTIONS["địa_điểm"], records_dd)

    total = len(records_ca) + len(records_ub) + len(records_dd)
    logging.info(f"=== Hoàn tất! Tổng {total} mục đã embed vào {CHROMA_DIR} ===")
