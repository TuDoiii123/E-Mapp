# Spec: Mô phỏng hàng chờ "sống" cho smart-route (dữ liệu demo Hà Nội)

**Ngày:** 2026-07-16 · **Trạng thái:** Đã triển khai + deploy
(`Backend/services/queue_demo.py`, tinh chỉnh `smart_route_core.py`)

## Vấn đề

`/api/map/smart-route` chấm điểm cơ quan theo khoảng cách + số người chờ,
nhưng bảng `agency_queue_realtime` chỉ được seed cho cơ quan Thanh Hóa.
Toàn bộ cơ quan Hà Nội (và ~3.300 cơ quan OSM toàn quốc) hiện 0 người chờ
→ smart-route thoái hoá thành "chọn gần nhất", tính năng "vắng nhất" vô
nghĩa trên bản deploy.

## Quyết định thiết kế

**Mô phỏng sống tính-khi-đọc** (không seed tĩnh, không cron):

- Số người chờ = hàm tất định của (agency_id × thứ × giờ), tính ngay tại
  điểm đọc. Không ghi DB, không job nền, demo lúc nào cũng "sống".
- Tái dùng đường cong tải của `queue_forecast.synth_count` (cao điểm
  9h30/14h30, T7 hệ số 0.4, CN 0.05).
- Quy mô nền suy từ **tên cơ quan**: cấp tỉnh/thành/sở/cục/công an 15–35
  người, quận/huyện/thị xã 8–20, phường/xã/thị trấn 3–10, khác 5–18;
  trong nhóm phân biệt bằng hash md5(agency_id) — không dùng `hash()`
  built-in (đổi theo process).
- Jitter ±20% tất định theo hash(id|ngày|giờ) → refresh trang không nhảy
  số, sang giờ khác số đổi.
- `DEMO_QUEUE_ALWAYS_OPEN` (mặc định bật): ngoài 7–18h ánh xạ giờ về khung
  8–16h, cuối tuần → ngày thường giả — demo buổi tối vẫn có số liệu.
  Đặt `=0` để hành xử như thật. Trong giờ hành chính thật thì không remap.
- `loadLevel` đồng ngưỡng với `QueueService.queue_summary`: >15 high,
  >5 medium.

**Nguyên tắc ưu tiên dữ liệu thật:** chỉ điền mô phỏng cho cơ quan **thiếu
dòng** trong `agency_queue_realtime`. Dòng thật (kể cả waiting=0) không bao
giờ bị ghi đè. Response gắn cờ `simulated: true/false`.

## Điểm nối (2 chỗ đọc, cùng 1 nguồn)

1. `map_routes.smart_route`: sau khi đọc DB, `fill_queue_map(nearby, queue_map)`
   điền cơ quan thiếu; khối `queue` trong response thêm `simulated`.
2. `queue_routes.map_overview`: giá trị khởi tạo mỗi cơ quan = `demo_queue(svc)`
   thay cho 0; dòng DB ghi đè với `simulated: false` → marker bản đồ và
   gợi ý smart-route luôn khớp số.

Cả hai chỗ bọc try/except — module mô phỏng lỗi thì hành vi cũ giữ nguyên.

## Tinh chỉnh trọng số smart-route (từ bộ đánh giá)

Nhân việc này, tách logic chấm điểm khỏi route thành
`services/smart_route_core.py` (hàm thuần `rank_agencies`, dùng chung với
bộ eval). Bộ đánh giá (spec riêng) chỉ ra trọng số cũ 0.4/0.5/0.1 lệch:
trong bán kính 10km đi lại tối đa ~20 phút nhưng hàng chờ có thể vài giờ.

**Đổi 0.4/0.5/0.1 → 0.2/0.7/0.1** (giữ 0.2 cho khoảng cách làm hàng rào
phòng sai số ước lượng hàng chờ, thay vì 0.1/0.8 tối ưu lý thuyết):
regret 4.4 → 0.7 phút, Top-1 61% → 83.3% trên 1.000 kịch bản.

## Kiểm thử

- `services/test_queue_demo.py` (8 test, local): tất định; 2 cơ quan khác
  số; UBND TP > phường; 9h30 > 12h; 22h vẫn sống khi ALWAYS_OPEN, =0 khi
  tắt; CN ≤ 2 khi tắt; ngưỡng loadLevel; fill không ghi đè dữ liệu thật.
- E2E Flask test client (không DB): 5 gợi ý quanh Hoàn Kiếm số khác nhau,
  tag đúng, 2 lần gọi cùng giờ cùng số, map-overview khớp smart-route.
- Verify prod sau deploy: 3.414 cơ quan đều có tải (3.319 mô phỏng + 95
  realtime thật Thanh Hóa), phân bố 772 low / 1.659 medium / 983 high.

## Không làm (YAGNI)

- Không sửa Frontend (API giữ shape cũ, chỉ thêm trường).
- Không mô phỏng số quầy/serving chi tiết (serving ước lượng waiting//5+1).
- Không cron/CronJob k3s.
