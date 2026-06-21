"""
LSTM dự báo số vé hàng chờ giờ kế tiếp. Data-prep thuần (không torch);
inference import torch + load model LAZY → thiếu torch/artifact trả None.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

log = get_logger('queue.lstm')

_MODEL_DIR = Path(__file__).parent.parent / 'models' / 'queue_lstm'
QUEUE_LSTM_ENABLED = os.getenv('QUEUE_LSTM_ENABLED', '1') == '1'


def build_series(rows) -> list:
    """rows = list (date, hour, count) → list[float] sắp theo (date, hour)."""
    return [float(c) for _, _, c in sorted(rows, key=lambda r: (str(r[0]), int(r[1])))]


def make_windows(series, lookback: int = 24):
    X, y = [], []
    for i in range(len(series) - lookback):
        X.append([float(v) for v in series[i:i + lookback]])
        y.append(float(series[i + lookback]))
    return X, y


def scale(series):
    xs = [float(v) for v in series]
    mn, mx = (min(xs), max(xs)) if xs else (0.0, 0.0)
    rng = mx - mn
    scaled = [0.0 for _ in xs] if rng == 0 else [(v - mn) / rng for v in xs]
    return scaled, mn, mx


def unscale(value: float, mn: float, mx: float) -> float:
    return mn + value * (mx - mn)
