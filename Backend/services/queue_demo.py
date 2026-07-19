"""
Mô phỏng hàng chờ "sống" cho demo — số liệu giả tất định theo (cơ quan × thứ × giờ).

Dùng cho các cơ quan CHƯA có dữ liệu thật trong agency_queue_realtime
(vd toàn bộ cơ quan Hà Nội trên bản deploy). Hàm thuần, không chạm DB:
cùng (cơ quan, giờ) luôn ra cùng con số — refresh trang không nhảy loạn,
sang giờ khác số tự đổi theo hình dạng cao điểm 9h30 / 14h30.

Flag DEMO_QUEUE_ALWAYS_OPEN (mặc định bật): ngoài giờ hành chính / cuối tuần
ánh xạ về khung giờ làm việc để demo buổi tối vẫn có số liệu; đặt =0 nếu muốn
hành xử như thật (đêm và Chủ nhật vắng tanh).
"""
import hashlib
import os
from datetime import datetime

from services.queue_forecast import synth_count


def _h(s: str) -> int:
    """Hash tất định (md5 → int) — không dùng hash() vì đổi theo process."""
    return int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)


def _base_size(agency: dict) -> int:
    """
    Quy mô cơ quan → số người chờ nền, suy từ tên:
    cấp tỉnh/thành/sở/cục đông, quận/huyện vừa, phường/xã vắng.
    Trong cùng nhóm, mỗi cơ quan một base khác nhau (hash id).
    """
    name = str(agency.get('name') or '').lower()
    aid = str(agency.get('id') or '')
    if any(k in name for k in ('thành phố', 'tỉnh', 'sở ', 'cục', 'bảo hiểm',
                               'trung tâm phục vụ', 'công an')):
        lo, hi = 15, 35
    elif any(k in name for k in ('quận', 'huyện', 'thị xã')):
        lo, hi = 8, 20
    elif any(k in name for k in ('phường', 'xã', 'thị trấn')):
        lo, hi = 3, 10
    else:
        lo, hi = 5, 18
    return lo + _h(aid) % (hi - lo + 1)


def _always_open() -> bool:
    return os.getenv('DEMO_QUEUE_ALWAYS_OPEN', '1') not in ('0', 'false', 'False')


# ~30% cơ quan là "văn phòng vắng" (chọn tất định theo id): hàng chờ luôn thấp
# cả ngày → gợi ý AI giờ cao điểm vẫn có lựa chọn 'Vắng' để khuyến nghị,
# thanh tải trên bản đồ có đủ 3 màu thay vì toàn vàng/đỏ.
QUIET_RATIO = 0.30
QUIET_MAX_WAITING = 5   # trần người chờ của cơ quan vắng (= ngưỡng 'low')


def _is_quiet(agency_id: str) -> bool:
    return _h(f'{agency_id}|quiet') % 100 < QUIET_RATIO * 100


def demo_queue(agency: dict, now: datetime = None) -> dict:
    """
    Sinh trạng thái hàng chờ mô phỏng cho 1 cơ quan tại thời điểm now.
    Trả về cùng khóa với agency_queue_realtime: waiting / serving / loadLevel,
    kèm simulated=True để phân biệt với dữ liệu thật.
    """
    now = now or datetime.now()
    aid = str(agency.get('id') or '')
    weekday, hour = now.weekday(), now.hour

    if _always_open():
        if hour < 7 or hour >= 18:
            hour = 8 + (hour % 9)          # đêm → khung 8h–16h
        if weekday >= 5:
            weekday = _h(f'{aid}|{now.date()}') % 5  # cuối tuần → ngày thường giả

    base = _base_size(agency)
    waiting = synth_count(base, weekday, hour)

    # Jitter tất định ±20% theo (cơ quan, ngày, giờ) — mỗi giờ một con số
    jitter = (_h(f'{aid}|{now.date()}|{hour}') % 41 - 20) / 100.0
    waiting = max(0, round(waiting * (1 + jitter)))

    # Văn phòng vắng: nén về mức thấp, vẫn dao động nhẹ theo giờ
    if _is_quiet(aid):
        waiting = min(round(waiting * 0.25), QUIET_MAX_WAITING)

    serving = max(1, min(6, waiting // 5 + 1)) if waiting > 0 else 0
    # Ngưỡng đồng bộ với QueueService.queue_summary (models/queue.py)
    load_level = 'high' if waiting > 15 else ('medium' if waiting > 5 else 'low')

    return {
        'waiting':   waiting,
        'serving':   serving,
        'loadLevel': load_level,
        'simulated': True,
    }


def fill_queue_map(agencies: list, queue_map: dict, now: datetime = None) -> dict:
    """
    Điền số mô phỏng cho các cơ quan THIẾU trong queue_map (đọc từ DB).
    Cơ quan đã có dòng realtime thật (kể cả waiting=0) giữ nguyên dữ liệu thật.
    """
    now = now or datetime.now()
    for agency in agencies:
        aid = str(agency.get('id') or '')
        if aid and aid not in queue_map:
            queue_map[aid] = demo_queue(agency, now)
    return queue_map
