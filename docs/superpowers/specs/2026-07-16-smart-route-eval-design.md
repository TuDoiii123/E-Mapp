# Spec: Bộ đánh giá Smart-Route — AI gợi ý cơ quan tối ưu + chỉ đường

**Ngày:** 2026-07-16 · **Trạng thái:** Đã triển khai (`Backend/eval/smart_route/`);
kết quả đã dùng để tinh chỉnh trọng số production (xem spec queue-demo).

## Mục đích

Định lượng chất lượng của thuật toán gợi ý cơ quan (điểm = dist·w₁ +
queue·w₂ + level·w₃) và phần ước tính thời gian đi, lấy số liệu cho đồ án.
Bốn góc đo: chất lượng quyết định, chất lượng xếp hạng, độ chính xác ETA,
độ nhạy trọng số.

## Phương pháp

### Mô phỏng kịch bản (simulate.py)

- 1.000 kịch bản = (vị trí ngẫu nhiên quanh 1 cơ quan Hà Nội ± ~3km) ×
  (T2–T6, 8h–16h30). Nguồn cơ quan: `data/hanoi_agencies.json` (106).
- Hàng chờ từ `services/queue_demo` — tất định theo (cơ quan × thứ × giờ)
  → toàn bộ mô phỏng tái lập được với cùng seed (mặc định 42).
- **Chi phí thật** của việc chọn cơ quan a:
  `cost(a) = dist_km ÷ 30km/h × 60 + waiting × 5 phút`
  (cùng mô hình ước lượng chờ với `est_wait_min` của smart-route).
- **Oracle** = argmin cost trong các ứng viên (≥3 trong bán kính 10km).
- 4 chính sách so sánh: smart-route, gần-nhất, vắng-nhất (tie→gần), ngẫu nhiên.

**Tính trung thực của phép đo:** smart-route tối ưu điểm chuẩn hoá có trọng
số chứ KHÔNG tối ưu trực tiếp tổng phút, nên so với oracle là đánh giá thật
— baseline có thể thắng (và thực tế "vắng nhất" từng thắng cấu hình cũ).

### Chỉ số (metrics.py)

- **Quyết định**: cost TB, regret TB (cost − oracle), Top-1 accuracy
  (chọn đúng oracle hoặc đồng chi phí, ε=1e-6), % thắng baseline gần-nhất;
  tách cao điểm (9–10h, 14–15h) vs thấp điểm.
- **Xếp hạng**: NDCG@5 (relevance = 1/(hạng theo cost thật + 1)), MRR của
  oracle trong top-5, % oracle lọt top-1/top-5.
- **Quét trọng số**: dist_w 0.0→0.9 bước 0.1 (queue_w = 0.9−dist_w,
  level_w cố định 0.1), cùng bộ kịch bản → bảng regret/Top-1 theo cấu hình.

### ETA check (eta_check.py)

- 30 cặp (điểm xuất phát, cơ quan) phân tầng gần (<2km) / trung (2–5) /
  xa (5–12), gọi OSRM public 1 req/s, **cache `cache_osrm.json`** — chạy
  lại 0 request (pattern giống bộ eval OCR).
- Đo: MAE/MAPE giữa ước tính `haversine ÷ 30km/h` và duration OSRM, bias
  (âm = ước thấp hơn thật), hệ số đường vòng (km OSRM ÷ km chim bay).

## Đầu ra

`reports/report.md` (5 mục + định nghĩa chỉ số) + `details.csv`
(per-scenario, per-policy). Chạy: `python run_eval.py [--n 1000]
[--skip-eta] [--skip-sweep]` — mô phỏng ~10 giây, ETA lần đầu ~35 giây.

## Kết quả thực đo (2026-07-16, 1.000 kịch bản)

**Trọng số cũ 0.4/0.5/0.1:** regret 4.4 phút, Top-1 61.0%; baseline
"vắng nhất" thắng (regret 0.5). Quét trọng số chỉ ra tối ưu tại 0.1/0.8
(regret 0.02) — khoảng cách bị đánh quá nặng.

**Sau tinh chỉnh 0.2/0.7/0.1** (production hiện tại):

| Chính sách | Cost TB (phút) | Regret | Top-1 |
|---|---|---|---|
| Oracle | 53.7 | 0 | 100% |
| **Smart-route 20/70/10** | **54.3** | **0.7** | **83.3%** |
| Vắng nhất | 54.2 | 0.5 | 85.6% |
| Gần nhất | 102.6 | 49.0 | 16.8% |
| Ngẫu nhiên | 105.6 | 51.9 | 11.5% |

- Tiết kiệm **48.3 phút/lượt (47%)** vs chọn gần nhất; cao điểm 55 phút (45.1%).
- NDCG@5 = 0.85, MRR = 0.73, oracle lọt top-5: 93.2%.
- ETA: MAE 2.73 phút, MAPE 30.7%, bias −0.70 phút; **hệ số đường vòng
  Hà Nội 1.73×** (đường thật dài gấp 1.73 lần đường chim bay).
- Lý do chọn 0.2/0.7 thay vì 0.1/0.8 tối ưu lý thuyết: giữ khoảng cách làm
  hàng rào khi ước lượng hàng chờ sai; chênh regret chấp nhận được (0.7 vs 0.02).

## Giới hạn đã biết

- Hàng chờ trong mô phỏng = chính nguồn `queue_demo` mà smart-route đọc trên
  deploy → đo "thuật toán chọn có tốt không khi biết đúng hàng chờ", không đo
  sai số dự báo hàng chờ (việc của LSTM forecast, đã có eval riêng).
- Mô hình chờ 5 phút/người chưa chia số quầy đang phục vụ — hướng cải tiến:
  `wait = waiting × 5 ÷ active_counters`.
- Eval dùng 106 cơ quan `hanoi_agencies.json`; prod dùng 3.414 cơ quan OSM —
  muốn eval trên dữ liệu prod chỉ cần đổi nguồn trong `load_hanoi_agencies`.
