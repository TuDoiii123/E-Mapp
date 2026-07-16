"""
Sinh kịch bản mô phỏng cho bộ đánh giá smart-route.

Mỗi kịch bản = (vị trí người dùng quanh Hà Nội, thời điểm trong giờ hành chính).
Hàng chờ lấy từ services.queue_demo — tất định theo (cơ quan × thứ × giờ) nên
toàn bộ mô phỏng tái lập được với cùng seed.

Chi phí thật của việc chọn cơ quan a:
    cost(a) = thời gian đi (dist/tốc độ) + thời gian chờ (số người × 5 phút)
Oracle = cơ quan có cost thấp nhất trong các ứng viên.
"""
import json
import os
import random
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.distance import find_nearby                     # noqa: E402
from services.queue_demo import demo_queue                    # noqa: E402
from services.smart_route_core import (                       # noqa: E402
    rank_agencies, SPEED_KMH, DIST_W, QUEUE_W, LEVEL_W,
)

WAIT_MIN_PER_PERSON = 5      # cùng mô hình với est_wait_min của smart-route
BASE_MONDAY = datetime(2026, 7, 13)   # thứ 2 — mốc dựng ngày theo weekday
PEAK_HOURS = {9, 10, 14, 15}


def load_hanoi_agencies() -> list:
    path = os.path.join(BACKEND_DIR, 'data', 'hanoi_agencies.json')
    with open(path, encoding='utf-8') as f:
        agencies = json.load(f)
    return [a for a in agencies
            if a.get('latitude') is not None and a.get('longitude') is not None]


def gen_scenarios(n: int, seed: int = 42) -> list:
    """N kịch bản: vị trí = quanh 1 cơ quan ngẫu nhiên ± ~3km, giờ 8h–16h30 T2–T6."""
    rng = random.Random(seed)
    agencies = load_hanoi_agencies()
    scenarios = []
    for i in range(n):
        anchor = rng.choice(agencies)
        lat = float(anchor['latitude']) + rng.uniform(-0.03, 0.03)
        lng = float(anchor['longitude']) + rng.uniform(-0.03, 0.03)
        weekday = rng.randint(0, 4)
        hour    = rng.randint(8, 16)
        minute  = rng.choice([0, 30])
        when = BASE_MONDAY + timedelta(days=weekday, hours=hour, minutes=minute)
        scenarios.append({'id': i, 'lat': lat, 'lng': lng, 'when': when,
                          'isPeak': hour in PEAK_HOURS})
    return scenarios


def true_cost(entry: dict, mode: str = 'driving') -> float:
    """Tổng phút thật: đi + chờ. entry từ rank_agencies (có dist_km, waiting)."""
    travel_min = entry['dist_km'] / SPEED_KMH[mode] * 60.0
    wait_min = entry['waiting'] * WAIT_MIN_PER_PERSON
    return travel_min + wait_min


def run_scenario(sc: dict, agencies: list, radius_km: float = 10.0,
                 weights: tuple = (DIST_W, QUEUE_W, LEVEL_W),
                 rng: random.Random = None) -> dict:
    """
    Chạy 1 kịch bản: xếp hạng theo smart-route + tính cost mọi chính sách.
    Trả về None nếu quá ít ứng viên (< 3).
    """
    nearby = find_nearby(agencies, sc['lat'], sc['lng'], radius_km)
    if len(nearby) < 3:
        return None

    queue_map = {a['id']: demo_queue(a, sc['when']) for a in nearby}
    ranked = rank_agencies(nearby, queue_map, radius_km, *weights)

    # Cost thật của từng ứng viên, theo thứ tự smart-route
    for e in ranked:
        e['cost'] = true_cost(e)

    by_cost = sorted(ranked, key=lambda e: e['cost'])
    oracle = by_cost[0]

    def cost_of(entry):
        return round(entry['cost'], 2)

    smart      = ranked[0]
    nearest    = min(ranked, key=lambda e: e['dist_km'])
    least_busy = min(ranked, key=lambda e: (e['waiting'], e['dist_km']))
    rand_pick  = (rng or random).choice(ranked)

    return {
        'scenarioId': sc['id'],
        'isPeak':     sc['isPeak'],
        'nCandidates': len(ranked),
        'oracleId':   oracle['agency']['id'],
        'oracleCost': cost_of(oracle),
        'policies': {
            'smart':      {'id': smart['agency']['id'],      'cost': cost_of(smart)},
            'nearest':    {'id': nearest['agency']['id'],    'cost': cost_of(nearest)},
            'least_busy': {'id': least_busy['agency']['id'], 'cost': cost_of(least_busy)},
            'random':     {'id': rand_pick['agency']['id'],  'cost': cost_of(rand_pick)},
        },
        # cho NDCG/MRR: thứ tự smart-route (top 5) + cost thật từng vị trí
        'rankedIds':  [e['agency']['id'] for e in ranked[:5]],
        'rankedCosts': [cost_of(e) for e in ranked[:5]],
        'allCostsSorted': [cost_of(e) for e in by_cost],
    }


def run_simulation(n: int = 1000, seed: int = 42, radius_km: float = 10.0,
                   weights: tuple = (DIST_W, QUEUE_W, LEVEL_W)) -> list:
    agencies = load_hanoi_agencies()
    rng = random.Random(seed + 1)
    records = []
    for sc in gen_scenarios(n, seed):
        rec = run_scenario(sc, agencies, radius_km, weights, rng)
        if rec:
            records.append(rec)
    return records
