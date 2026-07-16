"""
Kiểm tra độ chính xác ETA của smart-route: ước tính khoảng_cách ÷ 30 km/h
so với thời gian lái xe thật từ OSRM (router.project-osrm.org, miễn phí).

Tôn trọng rate limit ~1 req/s; mọi response cache vào cache_osrm.json —
chạy lại 0 request.
"""
import json
import os
import random
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.distance import calculate_distance          # noqa: E402
from services.smart_route_core import SPEED_KMH           # noqa: E402
from simulate import load_hanoi_agencies                  # noqa: E402

CACHE_PATH = os.path.join(HERE, 'cache_osrm.json')
OSRM_BASE = 'https://router.project-osrm.org/route/v1/driving'


def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict):
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)


def _osrm_route(olat, olng, dlat, dlng, cache: dict) -> dict:
    """Trả {'durationMin', 'distanceKm'} từ OSRM, có cache. None nếu lỗi."""
    key = f'{olat:.4f},{olng:.4f}->{dlat:.4f},{dlng:.4f}'
    if key in cache:
        return cache[key]
    try:
        resp = requests.get(
            f'{OSRM_BASE}/{olng},{olat};{dlng},{dlat}',
            params={'overview': 'false'}, timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get('code') != 'Ok' or not data.get('routes'):
            return None
        route = data['routes'][0]
        result = {
            'durationMin': route['duration'] / 60.0,
            'distanceKm':  route['distance'] / 1000.0,
        }
        cache[key] = result
        _save_cache(cache)
        time.sleep(1.1)   # rate limit OSRM public
        return result
    except Exception:
        return None


def sample_pairs(n_pairs: int = 30, seed: int = 42) -> list:
    """
    Lấy mẫu cặp (điểm xuất phát, cơ quan) phân tầng theo cự ly:
    1/3 gần (<2km), 1/3 trung (2–5km), 1/3 xa (5–12km).
    """
    rng = random.Random(seed)
    agencies = load_hanoi_agencies()
    buckets = {'near': [], 'mid': [], 'far': []}
    attempts = 0
    while attempts < n_pairs * 60 and any(len(b) < n_pairs // 3 + 1 for b in buckets.values()):
        attempts += 1
        a, b = rng.choice(agencies), rng.choice(agencies)
        olat = float(a['latitude']) + rng.uniform(-0.02, 0.02)
        olng = float(a['longitude']) + rng.uniform(-0.02, 0.02)
        dlat, dlng = float(b['latitude']), float(b['longitude'])
        km = calculate_distance(olat, olng, dlat, dlng)
        bucket = 'near' if km < 2 else ('mid' if km <= 5 else 'far')
        if km > 12 or km < 0.3:
            continue
        if len(buckets[bucket]) < n_pairs // 3 + 1:
            buckets[bucket].append({'olat': olat, 'olng': olng,
                                    'dlat': dlat, 'dlng': dlng,
                                    'haversineKm': km, 'bucket': bucket,
                                    'destName': b.get('name', '')})
    pairs = [p for b in buckets.values() for p in b][:n_pairs]
    return pairs


def run_eta_check(n_pairs: int = 30, seed: int = 42, log=print) -> dict:
    """So ETA heuristic vs OSRM. Trả về summary + chi tiết từng cặp."""
    cache = _load_cache()
    pairs = sample_pairs(n_pairs, seed)
    speed = SPEED_KMH['driving']

    rows = []
    n_api = 0
    for i, p in enumerate(pairs):
        key_cached = f"{p['olat']:.4f},{p['olng']:.4f}->{p['dlat']:.4f},{p['dlng']:.4f}" in cache
        osrm = _osrm_route(p['olat'], p['olng'], p['dlat'], p['dlng'], cache)
        if osrm is None:
            continue
        if not key_cached:
            n_api += 1
            log(f'  [{i + 1}/{len(pairs)}] OSRM: {p["destName"][:40]} ({p["haversineKm"]} km)')
        est_min = p['haversineKm'] / speed * 60.0
        rows.append({
            **p,
            'estMin':   round(est_min, 1),
            'osrmMin':  round(osrm['durationMin'], 1),
            'osrmKm':   round(osrm['distanceKm'], 2),
            'absErr':   round(abs(est_min - osrm['durationMin']), 1),
            'detour':   round(osrm['distanceKm'] / p['haversineKm'], 2)
                        if p['haversineKm'] else None,
        })

    if not rows:
        return {'n': 0, 'nApi': n_api, 'rows': []}

    n = len(rows)
    mae = sum(r['absErr'] for r in rows) / n
    mape = sum(r['absErr'] / r['osrmMin'] for r in rows if r['osrmMin']) / n * 100
    mean_detour = sum(r['detour'] for r in rows if r['detour']) / n
    bias = sum(r['estMin'] - r['osrmMin'] for r in rows) / n

    return {
        'n': n, 'nApi': n_api,
        'maeMin': round(mae, 2),
        'mapePct': round(mape, 1),
        'meanDetour': round(mean_detour, 2),
        'biasMin': round(bias, 2),   # âm = heuristic lạc quan (ước ít hơn thật)
        'rows': rows,
    }
