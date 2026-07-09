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
    p = Path(__file__).parent.parent / '.env'
    if not p.exists():
        return  # không có .env (vd chạy trong container) → dùng env sẵn có
    for l in open(p, encoding='utf-8'):
        s = l.strip()
        if s and not s.startswith('#') and '=' in s:
            k, _, v = s.partition('=')
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(days: int = 180, seed: int = 42, limit: int | None = None):
    """limit=None → toàn bộ cơ quan curated (không tính POI OSM / UBND xã centroid)."""
    _load_env()
    from flask import Flask
    from models.db import init_db, db
    from sqlalchemy import text
    from services.queue_forecast import synth_count, rollup_real

    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    rng = random.Random(seed)

    q = "SELECT id FROM public.agencies WHERE id NOT LIKE 'osm-%' AND id NOT LIKE 'th-x-%' ORDER BY id"
    if limit:
        q += f' LIMIT {int(limit)}'
    agencies = [r[0] for r in db.session.execute(text(q)).fetchall()]
    if not agencies:
        agencies = [f'demo-agency-{i}' for i in range(1, 6)]
    bases = {a: rng.randint(15, 40) for a in agencies}

    db.session.execute(text("DELETE FROM public.queue_history_daily WHERE source='synth'"))
    today = date.today()
    n = 0
    ins = text('''
        INSERT INTO public.queue_history_daily (agency_id, date, hour, ticket_count, source)
        VALUES (:a, :d, :h, :c, 'synth')
        ON CONFLICT (agency_id, date, hour)
        DO UPDATE SET ticket_count = EXCLUDED.ticket_count, source='synth'
    ''')
    for i, a in enumerate(agencies, 1):
        batch = []  # gom cả cơ quan rồi executemany 1 lần — nhanh hơn hàng chục lần từng dòng
        for d in range(days):
            day = today - timedelta(days=d)
            wd = day.weekday()
            for h in range(7, 18):
                c = synth_count(bases[a], wd, h, rng)
                if c > 0:
                    batch.append({'a': a, 'd': day, 'h': h, 'c': c})
        if batch:
            db.session.execute(ins, batch)
            n += len(batch)
        db.session.commit()
        if i % 20 == 0:
            print(f'  ...{i}/{len(agencies)} cơ quan', flush=True)
    real = rollup_real()
    print(f'Sinh {n} dòng synthetic cho {len(agencies)} cơ quan; rollup_real {real} dòng.')


if __name__ == '__main__':
    import sys as _sys
    main(limit=int(_sys.argv[1]) if len(_sys.argv) > 1 else None)
