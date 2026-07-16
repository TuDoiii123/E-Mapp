# Bộ đánh giá Gemini OCR — trích xuất dữ liệu giấy tờ

Đo độ chính xác của luồng trích xuất tự động (Gemini 2.5 Flash) trong E-Mapp:
giấy tờ cá nhân (CCCD, GPLX, giấy kết hôn) và phân tích biểu mẫu trống.

## Cài đặt

Cần thêm Pillow (chỉ cho máy dev, không cần trên server):

```
pip install Pillow
```

## Quy trình chuẩn

```bash
# 1. Sinh 1000 ảnh synthetic + nhãn tự động (miễn phí, không gọi API)
python generate_dataset.py --count 1000

# 2. Chạy đánh giá — mỗi ảnh gọi Gemini đúng 1 lần, kết quả cache vĩnh viễn
python run_eval.py --sample 100     # lấy mẫu phân tầng 100 ảnh đại diện
python run_eval.py                  # hoặc chạy cả bộ (tự dừng khi hết quota)

# 3. Xem báo cáo
#    reports/report.md   — bảng tổng hợp (đưa thẳng vào báo cáo/luận văn)
#    reports/details.csv — từng trường từng ảnh (phân tích thêm bằng Excel)
```

**Quota:** key Gemini free-tier chỉ ~20 request/ngày. Runner tự dừng khi gặp
lỗi 429 và **chạy lại hôm sau sẽ tiếp tục đúng chỗ dừng** (ảnh đã chạy nằm
trong `cache/`, không bao giờ gọi lại). Chấm lại điểm không tốn quota:

```bash
python run_eval.py --report-only    # chấm từ cache, 0 request
```

## Thêm ảnh thật

Ảnh CCCD/GPLX thật là dữ liệu nhạy cảm — `dataset/images/` đã nằm trong
`.gitignore`, không bị commit.

```bash
python label_helper.py duong_dan/anh_cccd.jpg --doc-type cccd
```

Lệnh này gọi Gemini 1 lần, ghi **nhãn nháp** vào `dataset/labels/`.
**Bắt buộc mở file nhãn, sửa từng trường cho đúng thực tế**, rồi đổi
`"source": "real_draft"` thành `"real"` — nếu không sửa thì đang lấy chính
model chấm điểm cho nó (vô nghĩa).

## Cách chấm điểm

| Loại | Cách chấm |
|---|---|
| Bộ chỉ số tổng hợp | Accuracy, Precision, Recall, F1, CER, WER, Similarity, Exact Match tài liệu, độ chính xác nhận diện loại giấy tờ, độ trễ (mean/p95) — kèm định nghĩa công thức ngay trong `report.md`, trích thẳng vào đồ án được. |
| Giấy tờ cá nhân | So từng trường sau chuẩn hoá (khoảng trắng, hoa/thường, ngày về `dd/mm/yyyy`). Trường sai tính thêm CER (tỷ lệ lỗi ký tự). |
| Biểu mẫu trống | Fuzzy match tên trường (ngưỡng 0.75) → precision / recall / F1; formName, formCode so mờ ngưỡng 0.8. |
| Mức ảnh hưởng | Gộp theo hồ sơ: % ảnh tự điền đúng 100% / sai ở **trường định danh** (số giấy tờ, họ tên, ngày sinh — sai là hồ sơ bị trả) / chỉ sai trường phụ; TB số trường phải sửa tay. |
| Hợp lệ định dạng | Không cần đáp án: JSON đủ khóa schema, số giấy tờ đúng 9/12 chữ số, ngày parse được, giới tính thuộc Nam/Nữ, tỷ lệ trường trống. |

Mỗi ảnh có biến thể chất lượng (`clean` / `blur` / `tilt` / `dark`) — báo cáo
tách độ chính xác theo từng điều kiện để thấy model chịu ảnh xấu đến đâu.

## Cấu trúc

```
eval/
├── generate_dataset.py   # sinh ảnh synthetic + nhãn
├── label_helper.py       # gán nhãn nháp cho ảnh thật
├── run_eval.py           # gọi Gemini (cache + resume) rồi chấm
├── scoring.py            # chuẩn hoá, so khớp, CER, fuzzy match
├── report.py             # xuất markdown + CSV
├── dataset/              # ảnh + nhãn (gitignore — sinh lại bằng script, seed 42)
├── cache/                # kết quả thô Gemini theo hash ảnh (gitignore)
└── reports/              # báo cáo đầu ra (gitignore)
```
