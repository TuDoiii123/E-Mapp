"""
Lõi chấm điểm smart-route — hàm thuần, dùng chung cho API (/api/map/smart-route)
và bộ đánh giá (eval/smart_route). Không chạm DB, không gọi mạng.

Điểm = dist_norm × DIST_W + queue_norm × QUEUE_W + level_norm × LEVEL_W
(điểm THẤP hơn = tốt hơn; queue nặng hơn khoảng cách theo thiết kế).
"""

# Trọng số mặc định: queue áp đảo khoảng cách — theo kết quả bộ đánh giá
# (eval/smart_route): trong bán kính 10km đi lại tối đa ~20 phút nhưng hàng
# chờ có thể vài giờ; 0.2/0.7 giảm regret từ 4.4 → ~0.6 phút, giữ chút ưu
# tiên gần để phòng sai số ước lượng hàng chờ (thay vì 0.1/0.8 tối ưu lý thuyết)
DIST_W  = 0.20
QUEUE_W = 0.70
LEVEL_W = 0.10

MAX_WAIT   = 30.0   # người chờ → coi là "đầy"
LOAD_SCORE = {'low': 0.0, 'medium': 0.2, 'high': 0.6}
SPEED_KMH  = {'driving': 30, 'walking': 5, 'cycling': 15}

# ── Lọc theo thủ tục ──────────────────────────────────────────────────────────

import unicodedata

def _norm(s: str) -> str:
    """Bỏ dấu tiếng Việt + lowercase + gộp ký tự phân cách về 1 dấu cách."""
    s = str(s).lower().replace('đ', 'd')
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in s).split())


# Slug thủ tục (frontend gửi lên) → từ khóa đã bỏ dấu để khớp với
# services/name/categoryId của cơ quan. Dữ liệu cơ quan là tiếng Việt có dấu
# ("Hộ khẩu", "Khai sinh"...) nên phải so trên dạng chuẩn hoá.
SERVICE_KEYWORDS = {
    'cccd':          ['cccd', 'can cuoc', 'dinh danh dien tu'],
    'ho_khau':       ['ho khau', 'cu tru', 'tam tru', 'thuong tru', 'tam vang'],
    'khai_sinh':     ['khai sinh', 'ho tich'],
    'ket_hon':       ['ket hon', 'ho tich'],
    'dat_dai':       ['dat dai', 'nha o', 'cnqsdd', 'so do', 'quyen su dung dat'],
    'doanh_nghiep':  ['doanh nghiep', 'kinh doanh', 'dau tu'],
    'y_te':          ['y te', 'kham chua benh', 'kham benh', 'tiem chung',
                      'bhyt', 'xet nghiem', 'cap cuu'],
    'gplx':          ['giay phep lai xe', 'gplx', 'sat hach lai xe'],
}


def filter_by_service(agencies: list, service_id) -> list:
    """
    Lọc danh sách cơ quan theo slug thủ tục ('cccd', 'ho_khau'...).

    - 'all' / rỗng / None → trả nguyên danh sách.
    - Slug có trong SERVICE_KEYWORDS → khớp bất kỳ từ khóa nào.
    - Slug lạ → coi là văn bản tự do, khớp chuỗi đã bỏ dấu.
    """
    if not service_id or str(service_id).strip().lower() == 'all':
        return agencies

    keywords = SERVICE_KEYWORDS.get(str(service_id).strip().lower())
    if keywords is None:
        keywords = [_norm(service_id)]

    def _match(a: dict) -> bool:
        haystack = _norm(' '.join([
            str(a.get('id', '')),
            str(a.get('categoryId', '')),
            ' '.join(str(s) for s in a.get('services') or []),
            str(a.get('name', '')),
        ]))
        return any(kw in haystack for kw in keywords)

    return [a for a in agencies if _match(a)]


def est_wait_min(waiting: int) -> int:
    """Ước tính thời gian chờ: bình quân 5 phút/người, tối thiểu 5 phút."""
    return max(5, int(waiting) * 5)


def rank_agencies(nearby: list, queue_map: dict, radius_km: float,
                  dist_w: float = DIST_W, queue_w: float = QUEUE_W,
                  level_w: float = LEVEL_W) -> list:
    """
    Chấm điểm và xếp hạng danh sách cơ quan (đã kèm 'distance' km).

    Args:
        nearby:    list agency dict, mỗi cái có 'id' và 'distance' (km)
        queue_map: {agency_id: {'waiting', 'serving', 'loadLevel', ...}}
        radius_km: bán kính tìm kiếm — dùng chuẩn hoá khoảng cách

    Returns: list dict {agency, queue, waiting, loadLevel, dist_km, score,
             estWaitMin} đã sort điểm tăng dần (tốt nhất trước).
    """
    scored = []
    max_dist = max(radius_km, 1.0)
    for agency in nearby:
        dist_km  = float(agency.get('distance') or 0)
        qs       = queue_map.get(agency['id'], {})
        waiting  = int(qs.get('waiting', 0))
        load_lvl = qs.get('loadLevel', 'low')

        dist_norm  = min(dist_km / max_dist, 1.0)
        queue_norm = min(waiting / MAX_WAIT, 1.0)
        level_norm = LOAD_SCORE.get(load_lvl, 0.0)

        score = dist_norm * dist_w + queue_norm * queue_w + level_norm * level_w

        scored.append({
            'agency':     agency,
            'queue':      qs,
            'waiting':    waiting,
            'loadLevel':  load_lvl,
            'dist_km':    dist_km,
            'score':      round(score, 4),
            'estWaitMin': est_wait_min(waiting),
        })

    scored.sort(key=lambda x: x['score'])
    return scored
