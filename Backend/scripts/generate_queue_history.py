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
