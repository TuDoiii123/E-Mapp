# Spec: Bộ đánh giá Gemini OCR — trích xuất dữ liệu giấy tờ

**Ngày:** 2026-07-16 · **Trạng thái:** Đã triển khai (`Backend/ImageExtract/eval/`)

## Mục đích

Đo chất lượng offline của luồng trích xuất tự động (Gemini 2.5 Flash) trong
E-Mapp — giấy tờ cá nhân (CCCD, GPLX, giấy kết hôn) và phân tích biểu mẫu
trống — để lấy số liệu cho báo cáo đồ án và so sánh khi đổi prompt/model.
Không phải giám sát runtime.

## Ràng buộc chi phối thiết kế

1. **Quota Gemini free-tier ~20 request/ngày** → mỗi ảnh chỉ được gọi API
   đúng 1 lần trong đời; mọi lần chấm lại phải miễn phí.
2. **Ảnh giấy tờ thật là dữ liệu cá nhân nhạy cảm** → không commit, khó gom
   số lượng lớn → dataset chủ lực là ảnh synthetic.
3. Cần bộ dữ liệu lớn (1.000 ảnh) dù quota nhỏ → chạy tích luỹ nhiều ngày.

## Kiến trúc

```
Backend/ImageExtract/eval/
├── generate_dataset.py   # sinh ảnh synthetic + nhãn tự động
├── label_helper.py       # nhãn nháp cho ảnh thật (Gemini 1 lần → sửa tay)
├── run_eval.py           # gọi Gemini (cache + resume) → chấm → báo cáo
├── scoring.py            # chuẩn hoá, so khớp, CER/WER, fuzzy, validate
├── report.py             # xuất report.md + details.csv
├── dataset/              # ảnh + nhãn (gitignore — sinh lại bằng seed 42)
├── cache/                # kết quả thô Gemini, key = SHA-256 ảnh (gitignore)
└── reports/              # đầu ra (gitignore)
```

### Dataset synthetic (1.000 ảnh)

- Phân bổ: 40% CCCD, 25% GPLX, 25% giấy kết hôn, 10% biểu mẫu trống (6 mẫu
  thật: CT01, CC01, đăng ký kết hôn, khai sinh, hộ chiếu TK01, ĐK04).
- Render bằng Pillow, font Arial (đủ glyph tiếng Việt), dữ liệu ngẫu nhiên
  tiếng Việt có dấu (họ/tên, địa chỉ Thanh Hóa + Hà Nội, số 12 chữ số,
  ngày hợp lệ). Nhãn JSON sinh kèm → ground truth tự động 100%.
- Biến thể chất lượng mỗi ảnh: 60% clean, 15% blur (Gaussian 1.8–2.8),
  15% tilt (±5–8°), 10% dark (brightness 0.42–0.58) — để đo suy giảm
  theo điều kiện ảnh.
- Tất định theo `--seed` (mặc định 42) → không commit dataset, sinh lại được.

### Runner chạy tích luỹ theo quota

- Cache theo SHA-256 nội dung ảnh (`cache/<hash>.json`): ảnh trùng nội dung
  dùng chung kết quả; sửa cách chấm → `--report-only` chấm lại 0 request.
- Gặp 429/RESOURCE_EXHAUSTED → dừng nhẹ nhàng, in số ảnh còn lại; chạy lại
  hôm sau tiếp đúng chỗ dừng. `--limit N` giới hạn request/lần chạy.
- Lỗi parse cũng cache (đã tốn quota) — `--retry-errors` mới gọi lại.
- `--sample N`: lấy mẫu phân tầng đều theo (loại giấy tờ × biến thể).

### Chấm điểm (scoring.py)

- **Chuẩn hoá**: NFC, gộp khoảng trắng, casefold; ngày về `dd/mm/yyyy`
  (nhận `dd/mm/yyyy`, `dd-mm-yyyy`, "[ngày] d tháng m năm y").
- **So khớp**: exact match trên dạng chuẩn hoá. Trường có boilerplate hợp lệ
  theo prompt (`type`, `placeOfMarriage` — model trả kèm "ỦY BAN NHÂN DÂN…")
  so bằng chứa-nhau hoặc fuzzy ≥ 0.8.
- **Biểu mẫu trống**: fuzzy match tên trường (SequenceMatcher ≥ 0.75, greedy
  best-match) → precision/recall/F1; formName/formCode fuzzy ≥ 0.8.
- **Bộ chỉ số tổng hợp** (`aggregate_metrics`): Accuracy, Precision/Recall/F1
  (chuẩn IE: TP=trường đúng, chia theo trường model trả ≠ rỗng / trường kỳ
  vọng ≠ rỗng), CER/WER (Levenshtein ÷ độ dài kỳ vọng), Similarity
  (1−Levenshtein chuẩn hoá), Exact Match mức tài liệu, độ chính xác nhận
  diện loại giấy tờ, độ trễ mean/p95 (đo quanh lời gọi API).
- **Mức ảnh hưởng khi tự điền hồ sơ**: phân loại theo hồ sơ — đúng 100% /
  sai trường định danh (số giấy tờ, họ tên, ngày sinh — hồ sơ bị trả) /
  chỉ sai trường phụ; TB số trường phải sửa tay.
- **Hợp lệ định dạng đầu ra** (không cần đáp án): đủ khóa schema, số giấy
  tờ 9/12 chữ số, ngày parse được, giới tính ∈ {Nam, Nữ}, tỷ lệ trường trống.

### Báo cáo

`reports/report.md` (8 mục, kèm định nghĩa công thức — trích thẳng vào đồ án)
+ `details.csv` (từng trường × ảnh, cột `critical` để lọc lỗi nghiêm trọng).

## Xử lý lỗi

- Thiếu API key → EnvironmentError rõ ràng; console Windows cp1252 →
  reconfigure UTF-8 ở mọi script CLI.
- Nhãn nháp từ `label_helper.py` đánh dấu `source: real_draft` — bắt buộc
  sửa tay rồi đổi thành `real` (tránh model tự chấm mình).

## Kiểm thử đã thực hiện

- Pipeline chấm: cache giả cấy 5 lỗi chủ đích → bắt đúng 100%, không báo
  nhầm ngày đổi định dạng; CSV khớp cột.
- End-to-end thật: 20 ảnh (19 request + cache), phát hiện 2 lỗi bộ chấm
  (boilerplate UBND, regex ngày) → sửa → chấm lại từ cache 0 request.

## Kết quả thực đo (29 ảnh đầu, 2026-07-16)

| Loại | Accuracy | F1 | CER | EM tài liệu |
|---|---|---|---|---|
| CCCD | 95.3% | 95.3% | 0.0033 | 75% |
| GPLX | 96.4% | 96.4% | 0.0026 | 75% |
| Kết hôn | 93.3% | 93.3% | 0.0052 | 25% |
| **Tổng** | **94.7%** | **94.7%** | **0.0039** | 62.5% |

Nhận diện loại giấy tờ 100%; độ trễ TB 6.4s/ảnh (p95 11.2s). Ảnh mờ là điều
kiện khó nhất (tỷ lệ "không phải sửa" rơi 100% → 25%). Lỗi điển hình: nhầm
số gần giống (8↔9), sai dấu thanh ("Hoằng"→"Hoàng").

## Vận hành

```bash
python generate_dataset.py --count 1000   # 1 lần
python run_eval.py --sample 100          # mỗi ngày, tự dừng khi hết quota
python run_eval.py --report-only         # chấm lại, 0 request
```
