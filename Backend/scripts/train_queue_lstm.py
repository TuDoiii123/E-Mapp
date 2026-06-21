"""
Train LSTM dự báo hàng chờ trên queue_history_daily, lưu models/queue_lstm/.
Chạy:  python -X utf8 -m scripts.train_queue_lstm   (từ Backend/, cần .env + Postgres + dữ liệu synth)
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
        print('Khong co du lieu de train.'); return
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
    print(f'Saved model -> {_MODEL_DIR} ({len(X_all)} samples).')


if __name__ == '__main__':
    main()
