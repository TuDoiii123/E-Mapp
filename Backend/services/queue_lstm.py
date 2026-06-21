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


def _build_model(lookback: int):
    import torch.nn as nn

    class _LSTM(nn.Module):
        def __init__(self, hidden=32):
            super().__init__()
            self.lstm = nn.LSTM(input_size=1, hidden_size=hidden, num_layers=1, batch_first=True)
            self.fc = nn.Linear(hidden, 1)

        def forward(self, x):                 # x: (batch, lookback, 1)
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])     # (batch, 1)

    return _LSTM()


_model = None
_meta = None


def _load():
    """Load model + meta 1 lần. Trả (model, meta) hoặc (None, None)."""
    global _model, _meta
    if _model is not None:
        return _model, _meta
    if not QUEUE_LSTM_ENABLED:
        return None, None
    pt = _MODEL_DIR / 'model.pt'
    mj = _MODEL_DIR / 'meta.json'
    if not pt.exists() or not mj.exists():
        log.info('[lstm] chưa có artifact → dùng fallback thống kê')
        return None, None
    try:
        import json
        import torch
        meta = json.loads(mj.read_text('utf-8'))
        model = _build_model(meta['lookback'])
        model.load_state_dict(torch.load(pt, map_location='cpu'))
        model.eval()
        _model, _meta = model, meta
        return _model, _meta
    except Exception as e:  # noqa: BLE001
        log.warning(f'[lstm] load lỗi → fallback: {e}')
        return None, None


def predict_next(recent_scaled, horizon: int):
    """Dự báo đệ quy `horizon` giá trị (đã scale). None nếu model không khả dụng."""
    model, meta = _load()
    if model is None:
        return None
    try:
        import torch
        lookback = meta['lookback']
        seq = list(recent_scaled)[-lookback:]
        if len(seq) < lookback:
            seq = [0.0] * (lookback - len(seq)) + seq
        preds = []
        with torch.no_grad():
            for _ in range(horizon):
                x = torch.tensor(seq[-lookback:], dtype=torch.float32).view(1, lookback, 1)
                p = float(model(x).item())
                p = min(1.0, max(0.0, p))
                preds.append(p)
                seq.append(p)
        return preds
    except Exception as e:  # noqa: BLE001
        log.warning(f'[lstm] predict lỗi → fallback: {e}')
        return None
