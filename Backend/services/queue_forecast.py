"""
Dự báo cao điểm hàng chờ — baseline thống kê + orchestrator.
Hàm thuần (synth_count, weekday_hour_avg, percentiles, load_level) test được không cần DB.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('queue.forecast')

_PEAKS = (9.5, 14.5)
_SIGMA = 1.5
_WD_MULT = {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.4, 6: 0.05}


def _hour_shape(hour: int) -> float:
    if hour < 7 or hour >= 18:
        return 0.0
    return sum(math.exp(-((hour - p) ** 2) / (2 * _SIGMA ** 2)) for p in _PEAKS)


def synth_count(base: int, weekday: int, hour: int, rng=None) -> int:
    """Số vé tổng hợp 1 giờ. rng=None → tất định (không nhiễu)."""
    hour_val = _hour_shape(hour)
    if hour_val == 0:
        return 0
    val = base * _WD_MULT.get(weekday, 1.0) * (0.25 + hour_val)
    if rng is not None:
        val += rng.gauss(0, base * 0.1)
    return max(0, int(round(val)))


def weekday_hour_avg(rows) -> dict:
    """rows = list (weekday, hour, count) → dict[(weekday,hour)] = trung bình."""
    acc: dict = {}
    for wd, h, cnt in rows:
        acc.setdefault((wd, h), []).append(float(cnt))
    return {k: sum(v) / len(v) for k, v in acc.items()}


def percentiles(values) -> tuple:
    """Trả (p50, p85) bằng nội suy tuyến tính. [] → (0,0)."""
    xs = sorted(float(v) for v in values)
    if not xs:
        return (0.0, 0.0)

    def _p(q):
        if len(xs) == 1:
            return xs[0]
        pos = q * (len(xs) - 1)
        lo = int(math.floor(pos))
        frac = pos - lo
        hi = min(lo + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * frac

    return (_p(0.50), _p(0.85))


def load_level(value: float, p50: float, p85: float) -> str:
    if value > p85:
        return 'high'
    if value > p50:
        return 'medium'
    return 'low'
