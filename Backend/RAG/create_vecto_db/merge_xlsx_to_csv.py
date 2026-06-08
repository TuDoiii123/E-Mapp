"""
Merge tất cả xlsx files trong Backend/RAG/data/ vào faqs.csv.

Chạy:
  python Backend/RAG/create_vecto_db/merge_xlsx_to_csv.py
  python Backend/RAG/create_vecto_db/merge_xlsx_to_csv.py --dry-run   # xem trước, không ghi
  python Backend/RAG/create_vecto_db/merge_xlsx_to_csv.py --file faq_ho_tich.xlsx  # chỉ 1 file

Mapping cột:
  xlsx: id, question, answer, category, procedure, source, level
  csv:  id, title,    answer_text, answer_html, source_url
"""
import argparse
import textwrap
from pathlib import Path

import pandas as pd

_DIR      = Path(__file__).parent
_DATA_DIR = _DIR.parent / "data"
_CSV_PATH = _DIR / "faqs.csv"

XLSX_FILES = [
    "faq_ho_tich.xlsx", "faq_dat_dai.xlsx", "faq_cccd_cu_tru.xlsx",
    "faq_giao_thong.xlsx", "faq_kinh_doanh.xlsx", "faq_bhxh_bhyt.xlsx",
    "faq_thue.xlsx", "faq_xay_dung.xlsx", "faq_chung.xlsx",
    "faq_tu_phap.xlsx", "faq_lao_dong.xlsx", "faq_y_te.xlsx",
    "faq_giao_duc.xlsx", "faq_moi_truong.xlsx", "faq_dau_tu.xlsx",
    "faq_khieu_nai.xlsx", "faq_nong_nghiep.xlsx",
    "faq_ngan_hang.xlsx", "faq_ho_tich_2.xlsx", "faq_dat_dai_2.xlsx",
    "faq_lao_dong_2.xlsx", "faq_thue_2.xlsx", "faq_giao_thong_2.xlsx",
    "faq_xay_dung_2.xlsx", "faq_xa_hoi.xlsx", "faq_pccc.xlsx",
    "faq_vien_thong.xlsx", "faq_y_te_2.xlsx", "faq_giao_duc_2.xlsx",
    "faq_nong_nghiep_2.xlsx", "faq_moi_truong_2.xlsx", "faq_van_hoa.xlsx",
    "faq_ton_giao.xlsx", "faq_khoa_hoc.xlsx", "faq_an_ninh.xlsx",
    "faq_tien_ich.xlsx", "faq_xuat_nhap_canh.xlsx", "faq_kinh_doanh_2.xlsx",
    "faq_g_ho_tich.xlsx", "faq_g_dat_dai.xlsx", "faq_g_cccd_cu_tru.xlsx",
    "faq_g_lao_dong.xlsx", "faq_g_thue.xlsx", "faq_g_y_te.xlsx",
    "faq_g_kinh_doanh.xlsx", "faq_g_xay_dung.xlsx", "faq_g_an_ninh.xlsx",
    "faq_g_dvc.xlsx", "faq_g_bhxh.xlsx", "faq_g_dan_su.xlsx",
    "faq_g_hanh_chinh.xlsx", "faq_g_giao_thong.xlsx", "faq_g_moi_truong.xlsx",
    "faq_g_tu_phap.xlsx", "faq_g_giao_duc.xlsx", "faq_g_ngan_hang.xlsx",
    "faq_g_bao_hiem.xlsx", "faq_g_quyen_tieu_dung.xlsx", "faq_g_so_huu_tri_tue.xlsx",
    "faq_g_chuyen_doi_so.xlsx", "faq_g_nha_o.xlsx", "faq_g_cong_an.xlsx",
    "faq_g_phuc_loi.xlsx", "faq_g_hon_nhan.xlsx", "faq_g_thua_ke.xlsx",
    "faq_g_doanh_nghiep.xlsx", "faq_g_chung_khoan.xlsx", "faq_g_ho_chieu.xlsx",
    "faq_g_thue_tncn.xlsx", "faq_g_xuat_khau_ld.xlsx", "faq_g_nvqs.xlsx",
    "faq_g_tuyen_sinh.xlsx", "faq_g_viec_lam.xlsx", "faq_g_thi_hanh_an.xlsx",
    "faq_g_du_lich.xlsx", "faq_g_dien_luc.xlsx", "faq_g_van_tai.xlsx",
    "faq_g_thu_y.xlsx", "faq_g_lam_nghiep.xlsx", "faq_g_thuy_san.xlsx",
    "faq_g_the_thao.xlsx", "faq_g_quy_hoach.xlsx", "faq_g_duoc_pham.xlsx",
    "faq_g_tmdt.xlsx", "faq_g_thien_tai.xlsx", "faq_g_tre_em.xlsx",
    "faq_g_tai_chinh_ca_nhan.xlsx", "faq_g_suc_khoe_tam_than.xlsx",
    "faq_g_khoi_nghiep.xlsx", "faq_g_van_bang.xlsx",
]


def _answer_to_html(text: str) -> str:
    """Chuyển plain text answer sang HTML đơn giản."""
    if not text:
        return ""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras:
        paras = [text.strip()]
    return "".join(f"<p>{textwrap.shorten(p, width=10000, placeholder='')}</p>" for p in paras)


def load_xlsx(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="FAQ", dtype=str).fillna("")
    if "question" not in df.columns or "answer" not in df.columns:
        raise ValueError(f"{path.name}: thiếu cột 'question' hoặc 'answer'")
    df["id"] = df["id"].str.strip()
    df = df[df["id"] != ""]
    return df


def xlsx_to_csv_rows(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        answer_text = str(r.get("answer", "")).strip()
        rows.append({
            "id":          r["id"],
            "title":       str(r.get("question", "")).strip(),
            "answer_text": answer_text,
            "answer_html": _answer_to_html(answer_text),
            "source_url":  str(r.get("source", "")).strip(),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Chỉ xem trước kết quả, không ghi file")
    parser.add_argument("--file", type=str, default=None,
                        help="Chỉ merge 1 file xlsx cụ thể")
    args = parser.parse_args()

    # Load faqs.csv hiện tại
    df_existing = pd.read_csv(_CSV_PATH, encoding="utf-8")
    existing_ids = set(df_existing["id"].astype(str))
    print(f"faqs.csv hiện tại: {len(df_existing)} rows, {len(existing_ids)} unique IDs")

    # Chọn file cần xử lý
    if args.file:
        target = _DATA_DIR / args.file
        if not target.exists():
            print(f"[ERROR] Không tìm thấy: {target}")
            return
        targets = [target]
    else:
        targets = [_DATA_DIR / f for f in XLSX_FILES if (_DATA_DIR / f).exists()]
        missing = [f for f in XLSX_FILES if not (_DATA_DIR / f).exists()]
        if missing:
            print(f"[WARN] Không tìm thấy ({len(missing)} files): {missing[:5]}...")

    # Merge từng file
    new_rows = []
    skipped_dup = 0
    for path in targets:
        try:
            df_xls  = load_xlsx(path)
            df_rows = xlsx_to_csv_rows(df_xls, path.name)

            added = 0
            for _, row in df_rows.iterrows():
                if str(row["id"]) in existing_ids:
                    skipped_dup += 1
                else:
                    new_rows.append(row)
                    existing_ids.add(str(row["id"]))
                    added += 1
            print(f"  {path.name}: +{added} mới, bỏ qua {len(df_rows) - added} trùng")
        except Exception as e:
            print(f"  [ERROR] {path.name}: {e}")

    print(f"\nTổng cần thêm: {len(new_rows)} rows (bỏ qua {skipped_dup} trùng ID)")

    if not new_rows:
        print("Không có dữ liệu mới để thêm.")
        return

    if args.dry_run:
        print("[DRY-RUN] Không ghi file. Dữ liệu mẫu:")
        sample = pd.DataFrame(new_rows).head(3)
        for _, r in sample.iterrows():
            print(f"  id={r['id']}  title={r['title'][:60]}")
        return

    # Ghi vào faqs.csv
    df_new   = pd.DataFrame(new_rows, columns=["id", "title", "answer_text", "answer_html", "source_url"])
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    df_final.to_csv(_CSV_PATH, index=False, encoding="utf-8")

    print(f"\nĐã ghi faqs.csv: {len(df_final)} rows (+{len(new_rows)} mới)")
    print(f"Tiếp theo: chạy python create_faq_db.py để rebuild ChromaDB")


if __name__ == "__main__":
    main()
