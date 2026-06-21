# Queue Forecast (Predictive AI) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dự báo cao điểm hàng chờ: baseline thống kê (profile tuần) + LSTM dự báo ngắn hạn trên dữ liệu tổng hợp, qua API; LSTM degrade an toàn về thống kê.

**Architecture:** Bảng `queue_history_daily` (tách khỏi `queue_tickets` sống) là dataset. `queue_forecast.py` lo thống kê + orchestrator. `queue_lstm.py` lo data-prep + inference (torch lazy). Script sinh synthetic + train offline. API `/api/queue/forecast/*`.

**Tech Stack:** Python/Flask, PostgreSQL (db.session + raw SQL), torch 2.8 (CPU), numpy, pytest 7.4.3 (chạy từ `Backend/`).

## Global Constraints
- Mọi import ML (`torch`, `numpy` cho model) **lazy** trong hàm — module import được khi thiếu torch.
- `forecast_short_term` **không bao giờ raise**: LSTM lỗi → fallback thống kê.
- Test thuần không cần torch/DB; chỉ task DDL/seed/train cần Postgres local.
- Helper thuần đặt trong `services/` (scripts/ không phải package); script import từ services.
- Lệnh test: `python -m pytest services/test_queue_forecast.py services/test_queue_lstm.py -q` (từ `Backend/`).
- Syntax gate: `python -m compileall -q Backend/services Backend/routes Backend/scripts Backend/server.py`.

---

## File Structure
| File | Trách nhiệm |
|---|---|
| `Backend/models/db.py` | + DDL `queue_history_daily` |
| `Backend/services/queue_forecast.py` | synth_count, weekday_hour_avg, percentiles, load_level, weekly_profile, rollup_real, forecast_short_term |
| `Backend/services/queue_lstm.py` | build_series, make_windows, scale, unscale, predict_next (torch lazy) |
| `Backend/scripts/generate_queue_history.py` | sinh synthetic + ETL thật → DB |
| `Backend/scripts/train_queue_lstm.py` | train LSTM, lưu `models/queue_lstm/` |
| `Backend/routes/queue_forecast_routes.py` | API `/api/queue/forecast/*` |
| `Backend/server.py` | đăng ký blueprint |
| `Backend/services/test_queue_forecast.py`, `test_queue_lstm.py` | test thuần |

---

## Task 1: DDL `queue_history_daily`
**Files:** Modify `Backend/models/db.py` (thêm khối trong `init_db`)

- [ ] **Step 1: Thêm DDL block** — trong `init_db(app)`, sau khối Notification (`log.debug('Notification tables OK')`), thêm:
```python
        # ── Queue history (forecast) ──────────────────────────────────────────
        try:
            qhist_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.queue_history_daily (
                agency_id    VARCHAR(120) NOT NULL,
                date         DATE         NOT NULL,
                hour         SMALLINT     NOT NULL,
                ticket_count INTEGER      NOT NULL DEFAULT 0,
                source       VARCHAR(10)  NOT NULL DEFAULT 'real',
                PRIMARY KEY (agency_id, date, hour)
            );
            CREATE INDEX IF NOT EXISTS idx_qhist_agency
                ON public.queue_history_daily(agency_id, date);
            ''')
            db.session.execute(qhist_ddl)
            db.session.commit()
            log.debug('Queue history table OK')
        except Exception as e:
            log.warning(f'Ensuring queue_history_daily failed: {e}')
            db.session.rollback()
```

- [ ] **Step 2: Verify** (từ `Backend/`):
```bash
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); app.app_context().push(); print('exists:', db.session.execute(text(\"SELECT to_regclass('public.queue_history_daily')\")).scalar() is not None)"
```
Expected: `exists: True`. (Postgres unreachable → DONE_WITH_CONCERNS.)

- [ ] **Step 3: Commit**
```bash
git add Backend/models/db.py
git commit -m "feat(forecast): DDL queue_history_daily"
```

---

## Task 2: Pure helpers — synth_count, weekday_hour_avg, percentiles, load_level
**Files:** Create `Backend/services/queue_forecast.py`, `Backend/services/test_queue_forecast.py`

**Interfaces — Produces:**
- `synth_count(base:int, weekday:int, hour:int, rng=None) -> int`
- `weekday_hour_avg(rows:list[tuple[int,int,float]]) -> dict[tuple[int,int],float]`
- `percentiles(values:list[float]) -> tuple[float,float]`  # (p50, p85)
- `load_level(value:float, p50:float, p85:float) -> str`  # 'low'|'medium'|'high'

- [ ] **Step 1: Write failing test** `Backend/services/test_queue_forecast.py`
```python
from services.queue_forecast import (
    synth_count, weekday_hour_avg, percentiles, load_level,
)


def test_synth_count_patterns():
    # Thứ 2 (0) cao hơn Chủ nhật (6) cùng giờ
    assert synth_count(20, 0, 9) > synth_count(20, 6, 9)
    # Giờ đỉnh (9) cao hơn giữa trưa (12)
    assert synth_count(20, 0, 9) > synth_count(20, 0, 12)
    # Ngoài giờ hành chính → 0
    assert synth_count(20, 0, 20) == 0
    assert synth_count(20, 0, 6) == 0
    # Không âm
    assert synth_count(5, 6, 13) >= 0


def test_weekday_hour_avg():
    rows = [(0, 9, 10.0), (0, 9, 20.0), (0, 10, 5.0), (1, 9, 8.0)]
    avg = weekday_hour_avg(rows)
    assert avg[(0, 9)] == 15.0
    assert avg[(0, 10)] == 5.0
    assert avg[(1, 9)] == 8.0


def test_percentiles_and_load_level():
    vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    p50, p85 = percentiles(vals)
    assert 5 <= p50 <= 6
    assert 8 <= p85 <= 9.5
    assert load_level(1, p50, p85) == 'low'
    assert load_level(p50 + 0.1, p50, p85) == 'medium'
    assert load_level(p85 + 1, p50, p85) == 'high'


def test_percentiles_empty():
    assert percentiles([]) == (0.0, 0.0)
```

- [ ] **Step 2: Run → FAIL** `python -m pytest services/test_queue_forecast.py -q` (ModuleNotFound)

- [ ] **Step 3: Create `Backend/services/queue_forecast.py`**
```python
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
    if hour < 7 or hour > 17:
        return 0.0
    return sum(math.exp(-((hour - p) ** 2) / (2 * _SIGMA ** 2)) for p in _PEAKS)


def synth_count(base: int, weekday: int, hour: int, rng=None) -> int:
    """Số vé tổng hợp 1 giờ. rng=None → tất định (không nhiễu)."""
    val = base * _WD_MULT.get(weekday, 1.0) * (0.25 + _hour_shape(hour))
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
```

- [ ] **Step 4: Run → PASS** (4 passed) `python -m pytest services/test_queue_forecast.py -q`

- [ ] **Step 5: Commit**
```bash
git add Backend/services/queue_forecast.py Backend/services/test_queue_forecast.py
git commit -m "feat(forecast): pure helpers synth_count/avg/percentiles/load_level"
```

---

## Task 3: DB functions — weekly_profile, rollup_real
**Files:** Modify `Backend/services/queue_forecast.py`

**Interfaces:**
- Consumes: `weekday_hour_avg`, `percentiles`, `load_level` (Task 2); `db` + `text` from models.
- Produces: `weekly_profile(agency_id:str) -> list[dict]` (mỗi item `{weekday,hour,avg,level,peak}`); `rollup_real() -> int`.

- [ ] **Step 1: Append functions to `queue_forecast.py`**
```python
def _db():
    from models.db import db
    from sqlalchemy import text
    return db, text


def weekly_profile(agency_id: str) -> list:
    """Profile tải theo (weekday 0=Mon..6=Sun, hour) cho 1 cơ quan."""
    db, text = _db()
    rows = db.session.execute(text('''
        SELECT EXTRACT(DOW FROM date)::int AS dow, hour, ticket_count
        FROM public.queue_history_daily WHERE agency_id = :a
    '''), {'a': agency_id}).fetchall()
    # Postgres DOW: 0=Sun..6=Sat → đổi sang 0=Mon..6=Sun
    norm = [((int(r[0]) + 6) % 7, int(r[1]), float(r[2])) for r in rows]
    avg = weekday_hour_avg(norm)
    p50, p85 = percentiles(list(avg.values()))
    out = []
    for (wd, h), v in sorted(avg.items()):
        lvl = load_level(v, p50, p85)
        out.append({'weekday': wd, 'hour': h, 'avg': round(v, 2),
                    'level': lvl, 'peak': lvl == 'high'})
    return out


def rollup_real() -> int:
    """Gộp queue_tickets thật → queue_history_daily (source='real'). Trả số dòng upsert."""
    db, text = _db()
    rows = db.session.execute(text('''
        SELECT agency_id, date, EXTRACT(HOUR FROM created_at)::int AS h, COUNT(*) AS c
        FROM public.queue_tickets
        WHERE agency_id IS NOT NULL AND agency_id <> ''
        GROUP BY agency_id, date, h
    ''')).fetchall()
    n = 0
    for r in rows:
        db.session.execute(text('''
            INSERT INTO public.queue_history_daily (agency_id, date, hour, ticket_count, source)
            VALUES (:a, :d, :h, :c, 'real')
            ON CONFLICT (agency_id, date, hour)
            DO UPDATE SET ticket_count = EXCLUDED.ticket_count, source = 'real'
        '''), {'a': r[0], 'd': r[1], 'h': int(r[2]), 'c': int(r[3])})
        n += 1
    db.session.commit()
    return n
```

- [ ] **Step 2: Verify compile + DB smoke** (từ `Backend/`):
```bash
python -m compileall -q services/queue_forecast.py
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); app.app_context().push(); from services.queue_forecast import weekly_profile, rollup_real; db.session.execute(text(\"INSERT INTO public.queue_history_daily VALUES ('smoke-ag','2026-06-15',9,30,'synth') ON CONFLICT DO NOTHING\")); db.session.commit(); p=weekly_profile('smoke-ag'); print('profile rows', len(p), p[0] if p else None); db.session.execute(text(\"DELETE FROM public.queue_history_daily WHERE agency_id='smoke-ag'\")); db.session.commit(); print('ok')"
```
Expected: `profile rows 1 {...'avg': 30.0...}` then `ok`. (Postgres unreachable → DONE_WITH_CONCERNS.)

- [ ] **Step 3: Commit**
```bash
git add Backend/services/queue_forecast.py
git commit -m "feat(forecast): weekly_profile + rollup_real (DB)"
```

---

## Task 4: Synthetic data script `generate_queue_history.py`
**Files:** Create `Backend/scripts/generate_queue_history.py`

**Interfaces:** Consumes `synth_count` (Task 2), `rollup_real` (Task 3).

- [ ] **Step 1: Create script**
```python
"""
Sinh dữ liệu lịch sử hàng chờ tổng hợp vào queue_history_daily (source='synth')
để huấn luyện LSTM + tính thống kê. Cũng chạy rollup_real() cho dữ liệu thật.

Chạy:  python -m scripts.generate_queue_history        (từ Backend/, cần .env + Postgres)
"""
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _load_env():
    for l in open(Path(__file__).parent.parent / '.env', encoding='utf-8'):
        s = l.strip()
        if s and not s.startswith('#') and '=' in s:
            k, _, v = s.partition('=')
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(days: int = 180, seed: int = 42):
    _load_env()
    from flask import Flask
    from models.db import init_db, db
    from sqlalchemy import text
    from services.queue_forecast import synth_count, rollup_real

    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    rng = random.Random(seed)

    agencies = [r[0] for r in db.session.execute(text(
        "SELECT id FROM public.agencies LIMIT 8")).fetchall()]
    if not agencies:
        agencies = [f'demo-agency-{i}' for i in range(1, 6)]
    bases = {a: rng.randint(15, 40) for a in agencies}

    db.session.execute(text("DELETE FROM public.queue_history_daily WHERE source='synth'"))
    today = date.today()
    n = 0
    for a in agencies:
        for d in range(days):
            day = today - timedelta(days=d)
            wd = day.weekday()
            for h in range(7, 18):
                c = synth_count(bases[a], wd, h, rng)
                if c <= 0:
                    continue
                db.session.execute(text('''
                    INSERT INTO public.queue_history_daily (agency_id, date, hour, ticket_count, source)
                    VALUES (:a, :d, :h, :c, 'synth')
                    ON CONFLICT (agency_id, date, hour)
                    DO UPDATE SET ticket_count = EXCLUDED.ticket_count, source='synth'
                '''), {'a': a, 'd': day, 'h': h, 'c': c})
                n += 1
        db.session.commit()
    real = rollup_real()
    print(f'Sinh {n} dòng synthetic cho {len(agencies)} cơ quan; rollup_real {real} dòng.')
    print('agencies:', agencies)


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run it to seed** (từ `Backend/`): `python -m scripts.generate_queue_history`
Expected: `Sinh <vài nghìn> dòng synthetic cho N cơ quan; ...` và in danh sách agencies. Ghi lại 1 agency id để dùng ở Task 6/8.

- [ ] **Step 3: Verify rows** (từ `Backend/`):
```bash
python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); app.app_context().push(); print('synth rows:', db.session.execute(text(\"SELECT COUNT(*) FROM public.queue_history_daily WHERE source='synth'\")).scalar())"
```
Expected: synth rows > 1000.

- [ ] **Step 4: Commit**
```bash
git add Backend/scripts/generate_queue_history.py
git commit -m "feat(forecast): script sinh dữ liệu hàng chờ tổng hợp"
```

---

## Task 5: LSTM data-prep (pure) — build_series, make_windows, scale, unscale
**Files:** Create `Backend/services/queue_lstm.py`, `Backend/services/test_queue_lstm.py`

**Interfaces — Produces:**
- `build_series(rows:list[tuple]) -> list[float]`  # rows=(date,hour,count) → chuỗi count sắp xếp
- `make_windows(series:list[float], lookback:int=24) -> tuple[list[list[float]], list[float]]`
- `scale(series:list[float]) -> tuple[list[float], float, float]`  # (scaled, mn, mx)
- `unscale(value:float, mn:float, mx:float) -> float`

- [ ] **Step 1: Write failing test** `Backend/services/test_queue_lstm.py`
```python
from services.queue_lstm import build_series, make_windows, scale, unscale


def test_build_series_sorted():
    rows = [('2026-06-02', 9, 5), ('2026-06-01', 8, 3), ('2026-06-01', 9, 7)]
    # sắp theo (date, hour): (06-01,8)=3, (06-01,9)=7, (06-02,9)=5
    assert build_series(rows) == [3.0, 7.0, 5.0]


def test_make_windows_shapes():
    series = [1.0, 2.0, 3.0, 4.0, 5.0]
    X, y = make_windows(series, lookback=2)
    assert X == [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
    assert y == [3.0, 4.0, 5.0]


def test_make_windows_too_short():
    assert make_windows([1.0, 2.0], lookback=5) == ([], [])


def test_scale_unscale_invertible():
    series = [0.0, 5.0, 10.0]
    scaled, mn, mx = scale(series)
    assert scaled == [0.0, 0.5, 1.0]
    assert abs(unscale(scaled[1], mn, mx) - 5.0) < 1e-9


def test_scale_constant_series():
    scaled, mn, mx = scale([4.0, 4.0, 4.0])
    assert all(s == 0.0 for s in scaled)        # tránh chia 0
    assert unscale(0.0, mn, mx) == 4.0
```

- [ ] **Step 2: Run → FAIL** `python -m pytest services/test_queue_lstm.py -q`

- [ ] **Step 3: Create `Backend/services/queue_lstm.py`**
```python
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
```

- [ ] **Step 4: Run → PASS** (5 passed) `python -m pytest services/test_queue_lstm.py -q`

- [ ] **Step 5: Commit**
```bash
git add Backend/services/queue_lstm.py Backend/services/test_queue_lstm.py
git commit -m "feat(forecast): LSTM data-prep thuần (build_series/make_windows/scale)"
```

---

## Task 6: LSTM model + train script + inference
**Files:** Modify `Backend/services/queue_lstm.py`; Create `Backend/scripts/train_queue_lstm.py`

**Interfaces — Produces:** `predict_next(recent_scaled:list[float], horizon:int) -> list[float] | None`
(trả None nếu `QUEUE_LSTM_ENABLED` False / thiếu torch / thiếu artifact).

- [ ] **Step 1: Append to `queue_lstm.py`** model def + lazy inference:
```python
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
```

- [ ] **Step 2: Create `Backend/scripts/train_queue_lstm.py`**
```python
"""
Train LSTM dự báo hàng chờ trên queue_history_daily, lưu models/queue_lstm/.
Chạy:  python -m scripts.train_queue_lstm   (từ Backend/, cần .env + Postgres + dữ liệu synth)
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main(lookback: int = 24, epochs: int = 8):
    for l in open(Path(__file__).parent.parent / '.env', encoding='utf-8'):
        s = l.strip()
        if s and not s.startswith('#') and '=' in s:
            k, _, v = s.partition('='); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    from flask import Flask
    from models.db import init_db, db
    from sqlalchemy import text
    import torch
    from torch import nn
    from services.queue_lstm import build_series, make_windows, scale, _build_model, _MODEL_DIR

    app = Flask(__name__); init_db(app); app.app_context().push()
    agencies = [r[0] for r in db.session.execute(text(
        "SELECT DISTINCT agency_id FROM public.queue_history_daily")).fetchall()]
    X_all, y_all = [], []
    for a in agencies:
        rows = db.session.execute(text('''
            SELECT date, hour, ticket_count FROM public.queue_history_daily WHERE agency_id=:a
        '''), {'a': a}).fetchall()
        series = build_series([(r[0], r[1], r[2]) for r in rows])
        scaled, _, _ = scale(series)
        X, y = make_windows(scaled, lookback)
        X_all += X; y_all += y
    if not X_all:
        print('Không có dữ liệu để train.'); return
    Xt = torch.tensor(X_all, dtype=torch.float32).unsqueeze(-1)   # (N, lookback, 1)
    yt = torch.tensor(y_all, dtype=torch.float32).unsqueeze(-1)   # (N, 1)
    model = _build_model(lookback)
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    lossf = nn.MSELoss()
    model.train()
    for ep in range(epochs):
        opt.zero_grad(); out = model(Xt); loss = lossf(out, yt); loss.backward(); opt.step()
        print(f'epoch {ep+1}/{epochs} loss={loss.item():.4f}')
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), _MODEL_DIR / 'model.pt')
    (_MODEL_DIR / 'meta.json').write_text(json.dumps({'lookback': lookback}), 'utf-8')
    print(f'Đã lưu model → {_MODEL_DIR} ({len(X_all)} mẫu).')


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Train (cần Task 4 đã seed)** (từ `Backend/`): `python -m scripts.train_queue_lstm`
Expected: in loss giảm dần các epoch, rồi `Đã lưu model → .../models/queue_lstm (N mẫu).` Verify artifact: `ls Backend/models/queue_lstm/` có `model.pt` + `meta.json`.
(Nếu torch/DB lỗi → DONE_WITH_CONCERNS; data-prep tests vẫn pass và fallback sẽ hoạt động.)

- [ ] **Step 4: Verify predict_next round-trip** (từ `Backend/`):
```bash
python -c "from services.queue_lstm import predict_next; import os; out=predict_next([0.5]*24, 3); print('preds', out if out is None else [round(x,3) for x in out])"
```
Expected: nếu artifact có → list 3 số trong [0,1]; nếu chưa train → `preds None` (fallback path — vẫn hợp lệ).

- [ ] **Step 5: Commit** (artifact KHÔNG commit — thêm `Backend/models/queue_lstm/` vào .gitignore nếu chưa ignore)
```bash
grep -q "models/queue_lstm" .gitignore || echo "Backend/models/queue_lstm/" >> .gitignore
git add Backend/services/queue_lstm.py Backend/scripts/train_queue_lstm.py .gitignore
git commit -m "feat(forecast): LSTM model + train script + inference lazy"
```

---

## Task 7: Orchestrator `forecast_short_term` (LSTM + fallback)
**Files:** Modify `Backend/services/queue_forecast.py`; Test `Backend/services/test_queue_forecast.py`

**Interfaces — Produces:** `forecast_short_term(agency_id:str, hours:int=8, now=None) -> dict`
`{ 'agency':..., 'source':'lstm'|'stats', 'forecast':[{'time','count','level','peak'}], 'warnings':[...] }`

- [ ] **Step 1: Append tests** to `test_queue_forecast.py`
```python
import services.queue_forecast as qf
from datetime import datetime


def test_forecast_fallback_to_stats(monkeypatch):
    # LSTM không khả dụng → fallback thống kê
    monkeypatch.setattr(qf, '_try_lstm', lambda agency, hours, now: None)
    # profile giả: weekday bất kỳ, mọi giờ avg=10 trừ 15h cao
    prof = [{'weekday': wd, 'hour': h, 'avg': (50.0 if h == 15 else 10.0),
             'level': ('high' if h == 15 else 'low'), 'peak': h == 15}
            for wd in range(7) for h in range(7, 18)]
    monkeypatch.setattr(qf, 'weekly_profile', lambda a: prof)
    out = qf.forecast_short_term('ag1', hours=6, now=datetime(2026, 6, 15, 13, 0))
    assert out['source'] == 'stats'
    assert out['agency'] == 'ag1'
    assert len(out['forecast']) == 6
    assert all('count' in f and 'level' in f for f in out['forecast'])
    # 15h là cao điểm → có trong warnings
    assert any(w['level'] == 'high' for w in out['warnings'])


def test_forecast_uses_lstm_when_available(monkeypatch):
    monkeypatch.setattr(qf, '_try_lstm', lambda agency, hours, now: [5, 6, 7])
    monkeypatch.setattr(qf, 'weekly_profile', lambda a: [
        {'weekday': wd, 'hour': h, 'avg': 5.0, 'level': 'low', 'peak': False}
        for wd in range(7) for h in range(7, 18)])
    out = qf.forecast_short_term('ag1', hours=3, now=datetime(2026, 6, 15, 8, 0))
    assert out['source'] == 'lstm'
    assert [f['count'] for f in out['forecast']] == [5, 6, 7]
```

- [ ] **Step 2: Run → FAIL** `python -m pytest services/test_queue_forecast.py -q -k forecast`

- [ ] **Step 3: Append to `queue_forecast.py`**
```python
from datetime import datetime, timedelta


def _profile_lookup(profile):
    return {(p['weekday'], p['hour']): p for p in profile}


def _try_lstm(agency_id, hours, now):
    """Lấy chuỗi gần đây từ DB, scale, gọi LSTM, unscale → list count. None nếu lỗi/không có."""
    try:
        from services import queue_lstm
        db, text = _db()
        rows = db.session.execute(text('''
            SELECT date, hour, ticket_count FROM public.queue_history_daily
            WHERE agency_id=:a ORDER BY date DESC, hour DESC LIMIT 240
        '''), {'a': agency_id}).fetchall()
        if not rows:
            return None
        series = queue_lstm.build_series([(r[0], r[1], r[2]) for r in reversed(rows)])
        scaled, mn, mx = queue_lstm.scale(series)
        preds = queue_lstm.predict_next(scaled, hours)
        if preds is None:
            return None
        return [max(0, int(round(queue_lstm.unscale(p, mn, mx)))) for p in preds]
    except Exception as e:  # noqa: BLE001
        log.debug(f'[forecast] _try_lstm bỏ qua: {e}')
        return None


def forecast_short_term(agency_id: str, hours: int = 8, now=None) -> dict:
    """Dự báo `hours` giờ tới. Luôn trả kết quả (LSTM → fallback thống kê)."""
    now = now or datetime.now()
    profile = weekly_profile(agency_id)
    lookup = _profile_lookup(profile)
    avgs = [p['avg'] for p in profile] or [0.0]
    p50, p85 = percentiles(avgs)

    counts = _try_lstm(agency_id, hours, now)
    source = 'lstm' if counts is not None else 'stats'
    if counts is None:
        counts = []
        for i in range(1, hours + 1):
            t = now + timedelta(hours=i)
            p = lookup.get((t.weekday(), t.hour))
            counts.append(int(round(p['avg'])) if p else 0)

    forecast, warnings = [], []
    for i, c in enumerate(counts, start=1):
        t = now + timedelta(hours=i)
        lvl = load_level(c, p50, p85)
        item = {'time': t.isoformat(timespec='hours'), 'count': c,
                'level': lvl, 'peak': lvl == 'high'}
        forecast.append(item)
        if lvl == 'high':
            warnings.append({'time': item['time'], 'level': lvl})
    return {'agency': agency_id, 'source': source, 'forecast': forecast, 'warnings': warnings}
```

- [ ] **Step 4: Run → PASS** `python -m pytest services/test_queue_forecast.py -q` (6 passed)

- [ ] **Step 5: Commit**
```bash
git add Backend/services/queue_forecast.py Backend/services/test_queue_forecast.py
git commit -m "feat(forecast): forecast_short_term orchestrator + fallback"
```

---

## Task 8: API routes `/api/queue/forecast/*`
**Files:** Create `Backend/routes/queue_forecast_routes.py`; Modify `Backend/server.py`

- [ ] **Step 1: Create `Backend/routes/queue_forecast_routes.py`**
```python
"""Queue forecast API — yêu cầu đăng nhập (phân tích vận hành)."""
from flask import Blueprint, jsonify, request

from logger import get_logger
from services.queue_forecast import weekly_profile, forecast_short_term

log = get_logger('queue_forecast_routes')
queue_forecast_bp = Blueprint('queue_forecast', __name__, url_prefix='/api/queue/forecast')


def _auth_ok():
    return getattr(request, 'user_id', None) is not None


@queue_forecast_bp.route('/weekly', methods=['GET'])
def weekly():
    if not _auth_ok():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    agency = (request.args.get('agency') or '').strip()
    if not agency:
        return jsonify({'success': False, 'message': 'Thiếu agency'}), 400
    profile = weekly_profile(agency)
    peaks = [p for p in profile if p['peak']]
    return jsonify({'success': True, 'agency': agency,
                    'profile': profile, 'peakHours': peaks}), 200


@queue_forecast_bp.route('', methods=['GET'])
def short_term():
    if not _auth_ok():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    agency = (request.args.get('agency') or '').strip()
    if not agency:
        return jsonify({'success': False, 'message': 'Thiếu agency'}), 400
    try:
        hours = min(max(int(request.args.get('hours', 8)), 1), 48)
    except ValueError:
        hours = 8
    return jsonify({'success': True, **forecast_short_term(agency, hours)}), 200
```

- [ ] **Step 2: Register blueprint in `server.py`** — thêm vào list `_blueprints`:
```python
    ('routes.queue_forecast_routes', 'queue_forecast_bp'),
```

- [ ] **Step 3: Verify** compile + registered:
```bash
python -m compileall -q routes/queue_forecast_routes.py server.py
python -c "s=open('server.py',encoding='utf-8').read(); print('registered:', 'queue_forecast_routes' in s and 'queue_forecast_bp' in s)"
```
Expected: `registered: True`. (Tùy chọn live smoke: start server, `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8888/api/queue/forecast/weekly` → 401.)

- [ ] **Step 4: Commit**
```bash
git add Backend/routes/queue_forecast_routes.py Backend/server.py
git commit -m "feat(forecast): API /api/queue/forecast + đăng ký blueprint"
```

---

## Task 9: Integration smoke + full suite
**Files:** (no new code — verification)

- [ ] **Step 1: Full forecast tests** (từ `Backend/`): `python -m pytest services/test_queue_forecast.py services/test_queue_lstm.py -q` → expect 11 passed.

- [ ] **Step 2: Syntax gate** (từ gốc repo): `python -m compileall -q Backend/services Backend/routes Backend/scripts Backend/server.py` → no errors.

- [ ] **Step 3: End-to-end smoke (DB + đã seed Task 4)** — gọi orchestrator + weekly thật cho 1 agency từ Task 4:
```bash
cd Backend && python -c "import os; [os.environ.setdefault(*l.strip().split('=',1)) for l in open('.env',encoding='utf-8') if '=' in l and not l.startswith('#')]; from flask import Flask; from models.db import init_db, db; from sqlalchemy import text; app=Flask(__name__); init_db(app); app.app_context().push(); from services.queue_forecast import weekly_profile, forecast_short_term; a=db.session.execute(text(\"SELECT agency_id FROM public.queue_history_daily WHERE source='synth' LIMIT 1\")).scalar(); print('agency', a); print('weekly len', len(weekly_profile(a))); f=forecast_short_term(a, 6); print('source', f['source'], 'forecast', len(f['forecast']), 'warnings', len(f['warnings']))"
```
Expected: in agency, `weekly len` > 0, `source` = 'lstm' (nếu đã train ở Task 6) hoặc 'stats', `forecast 6`. Không lỗi.

- [ ] **Step 4: Commit (nếu có thay đổi nhỏ)**: `git commit -am "test(forecast): smoke tích hợp" || echo "không có thay đổi"`

---

## Task 10 (TÙY CHỌN): Panel admin hiển thị
**Files:** Create FE component hiển thị heatmap thứ×giờ + cảnh báo cao điểm; gọi `GET /api/queue/forecast/weekly` và `GET /api/queue/forecast?agency=&hours=`.
Chi tiết: thêm một mục trong khu admin (vd `frontend/src/screens/admin/`), dùng cùng http client (`apiRequest`/`./api`). Bảng màu theo `level` (low/medium/high). Build `npm run build` phải sạch. Đây là task tô điểm — chỉ làm nếu muốn demo trực quan; backend đã đủ giá trị.

---

## Ghi chú triển khai
- `synth_count` đặt trong `queue_forecast.py` (không phải script) để test được — script import từ đó.
- Artifact LSTM (`models/queue_lstm/`) KHÔNG commit (gitignore); train lại bằng script.
- Thứ tự phụ thuộc: Task 4 (seed) trước Task 6 (train) trước Task 9 smoke `source='lstm'`. Nếu bỏ qua train, mọi thứ vẫn chạy với `source='stats'`.
