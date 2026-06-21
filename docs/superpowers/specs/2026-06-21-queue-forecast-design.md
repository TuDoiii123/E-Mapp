# Thiết kế: Predictive AI dự báo cao điểm hàng chờ

- **Ngày**: 2026-06-21
- **Phạm vi**: Backend `Backend/` (+ panel admin tùy chọn `frontend/`)
- **Bối cảnh**: Báo cáo nghiên cứu nêu định hướng "Predictive AI" — dùng mô hình chuỗi thời gian
  (LSTM) trên dữ liệu lịch sử hàng chờ để **cảnh báo sớm khung giờ/ngày cao điểm quá tải** tại các
  cơ quan. Hiện hệ thống chưa có. Reality-check: `queue_tickets` chỉ có ~3 dòng thật → LSTM trực
  tiếp vô nghĩa.

## Quyết định đã chốt
1. Hướng: **Thống kê (baseline luôn chạy) + LSTM trên dữ liệu tổng hợp** (demo đúng "mô hình AI"
   như báo cáo). Hướng A: bảng lịch sử tổng hợp + baseline + LSTM lazy/fallback + API.
2. Đầu ra: **cả hai** — (1) profile tuần (thứ × giờ) cho mỗi cơ quan; (2) dự báo ngắn hạn N giờ
   tới (số vé + mức tải + cảnh báo quá tải). LSTM lo (2); thống kê lo (1) + fallback cho (2).

## Nguyên tắc cốt lõi
Baseline thống kê **luôn trả kết quả**; LSTM là lớp "AI" đặt lên trên, **degrade an toàn** (thiếu
torch/artifact → tự rơi về thống kê). Mọi import ML lazy. Dữ liệu tổng hợp tách khỏi `queue_tickets`
sống.

## Kiến trúc

```
queue_tickets (thật, ít)          generate_queue_history.py (synthetic)
        │ rollup_real()                     │
        ▼                                    ▼
        ────────► queue_history_daily (agency, date, hour, count, source) ◄────
                          │                                  │
          weekly_profile()│ (thống kê)        train_queue_lstm.py → models/queue_lstm/
                          ▼                                  │ (offline)
                  forecast_short_term(agency, hours) ───► predict_next() [torch lazy]
                          │  (LSTM, fallback → thống kê)
                          ▼
        GET /api/queue/forecast/weekly   |   GET /api/queue/forecast?agency=&hours=
                          ▼
                (tùy chọn) panel admin: heatmap + cảnh báo cao điểm
```

## Data model — `models/db.py` (CREATE TABLE IF NOT EXISTS)
```sql
CREATE TABLE public.queue_history_daily (
  agency_id    VARCHAR(120) NOT NULL,
  date         DATE         NOT NULL,
  hour         SMALLINT     NOT NULL,         -- 0..23 (thực tế 7..17)
  ticket_count INTEGER      NOT NULL DEFAULT 0,
  source       VARCHAR(10)  NOT NULL DEFAULT 'real',  -- 'real' | 'synth'
  PRIMARY KEY (agency_id, date, hour)
);
CREATE INDEX idx_qhist_agency ON public.queue_history_daily(agency_id, date);
```

## Sinh dữ liệu tổng hợp — `scripts/generate_queue_history.py`
- Sinh ~180 ngày × cơ quan (từ bảng `agencies`, hoặc tập demo cố định) × giờ 7..17.
- Hàm thuần `synth_count(base, weekday, hour, rng) -> int`:
  - thứ 2–6 cao, thứ 7 thấp (×0.4), CN ~0;
  - 2 đỉnh/ngày (sáng ~9–10h, chiều ~14–15h) qua hàm hình chuông;
  - base theo cơ quan + nhiễu (Poisson/random); luôn ≥ 0.
- Ghi `source='synth'`, idempotent (xóa synth trong range trước khi sinh).

## ETL thật — `rollup_real()` (trong `queue_forecast.py`)
- `SELECT agency_id, date, EXTRACT(hour FROM created_at) h, COUNT(*) FROM queue_tickets GROUP BY ...`
  → upsert `queue_history_daily` (`source='real'`). Chạy script/định kỳ; không bắt buộc v1.

## Baseline thống kê — `services/queue_forecast.py`
- `weekly_profile(agency_id) -> {weekday: {hour: {avg, level, peak}}}` (đọc DB, group theo weekday×hour).
- Hàm thuần (test không cần DB):
  - `weekday_hour_avg(rows) -> dict[(weekday,hour)] = avg` (rows = list (weekday,hour,count)).
  - `load_level(value, p50, p85) -> 'low'|'medium'|'high'` (ngưỡng phân vị của cơ quan; high = peak).
  - `percentiles(values) -> (p50, p85)`.

## LSTM — `services/queue_lstm.py` + `scripts/train_queue_lstm.py`
- Data-prep thuần (không torch):
  - `build_series(rows) -> list[float]` (chuỗi giờ liên tục, điền 0 cho giờ thiếu).
  - `make_windows(series, lookback=24) -> (X, y)` cửa sổ trượt.
  - `scale(series) -> (scaled, mn, mx)` / `unscale(v, mn, mx)` — min-max khả nghịch.
- Model: `nn.LSTM` nhỏ (1–2 lớp, hidden 16–32) → Linear→1 (số vé giờ kế).
- `train_queue_lstm.py` (offline thủ công): đọc history, train **1 model chung**, lưu
  `models/queue_lstm/model.pt` + `meta.json` (lookback, scaler).
- `predict_next(recent_scaled, horizon) -> list[float]` (import torch + load model **lazy**); thiếu
  torch/artifact → ném/None.

## Orchestrator — `forecast_short_term(agency_id, hours)`
- Thử LSTM; **bất kỳ lỗi nào → fallback `weekly_profile`** cho các khung giờ sắp tới. Luôn trả về.
- Trả `{agency, source: 'lstm'|'stats', forecast: [{time, count, level, peak}], warnings: [khung high]}`.

## API — `routes/queue_forecast_routes.py` (`queue_forecast_bp`, prefix `/api/queue/forecast`)
| Endpoint | Trả về | Auth |
|---|---|---|
| `GET /weekly?agency=<id>` | `{agency, profile:[{weekday,hour,avg,level,peak}], peakHours:[...]}` | đăng nhập |
| `GET /?agency=<id>&hours=<N>` | `{agency, source, forecast:[...], warnings:[...]}` | đăng nhập |
Đăng ký blueprint trong `server.py`. Dùng `request.user_id` (401 nếu thiếu).

## Hiển thị (admin, tùy chọn — task cuối plan)
Panel admin mỏng: heatmap tải thứ×giờ + danh sách khung giờ cao điểm sắp tới (gọi 2 API). Core là backend.

## Config
- `QUEUE_LSTM_ENABLED` (mặc định dùng nếu có artifact). Thư mục `models/queue_lstm/`.

## Degrade / lỗi
- `queue_history_daily` rỗng → profile 0/empty; forecast `source='stats'`, mức `low`. Không crash.
- torch/artifact thiếu → fallback thống kê (log warning). Import ML lazy toàn bộ.

## Testing (đa số không cần torch/DB)
- `synth_count`: thứ trong tuần > cuối tuần; giờ đỉnh > giờ thấp; ≥ 0.
- `weekday_hour_avg`, `percentiles`, `load_level` — thuần.
- `build_series`, `make_windows` (shape đúng), `scale`↔`unscale` (khả nghịch) — thuần.
- `forecast_short_term`: monkeypatch `predict_next` ném lỗi → trả `source='stats'`, không crash.
- API smoke (401 khi chưa auth).

## Files
| File | Action |
|---|---|
| `models/db.py` | + DDL `queue_history_daily` |
| `services/queue_forecast.py` | mới — stats + load_level + weekly_profile + forecast_short_term + rollup_real |
| `services/queue_lstm.py` | mới — data-prep + inference (torch lazy) |
| `scripts/generate_queue_history.py` | mới — synthetic + ETL thật |
| `scripts/train_queue_lstm.py` | mới — train + lưu artifact |
| `routes/queue_forecast_routes.py` | mới — API |
| `server.py` | đăng ký blueprint |
| `services/test_queue_forecast.py`, `services/test_queue_lstm.py` | mới — test thuần |
| (tùy chọn) FE admin panel | mới — heatmap + cảnh báo |

## Không làm (YAGNI)
- Không train tự động lúc khởi động server (script thủ công).
- Không model per-agency riêng (1 model chung v1).
- Không retrain realtime; không Transformer.
