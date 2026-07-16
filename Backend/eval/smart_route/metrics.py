"""
Chỉ số đánh giá smart-route từ các bản ghi mô phỏng (simulate.py).

- Chất lượng quyết định: Top-1 accuracy vs oracle, regret (phút), so baseline.
- Chất lượng xếp hạng: NDCG@5, MRR.
- Độ nhạy trọng số: quét dist_w/queue_w trên cùng bộ kịch bản.
"""
import math

POLICIES = ('smart', 'nearest', 'least_busy', 'random')
EPS = 1e-6


# ── Chất lượng quyết định ────────────────────────────────────────────────────

def decision_summary(records: list) -> dict:
    """Tổng hợp per-policy: cost TB, regret TB, top-1 acc, % thắng nearest."""
    out = {}
    n = len(records)
    for pol in POLICIES:
        costs   = [r['policies'][pol]['cost'] for r in records]
        regrets = [r['policies'][pol]['cost'] - r['oracleCost'] for r in records]
        top1    = sum(1 for r in records
                      if r['policies'][pol]['cost'] <= r['oracleCost'] + EPS)
        beat_nearest = sum(
            1 for r in records
            if r['policies'][pol]['cost'] < r['policies']['nearest']['cost'] - EPS)
        tie_nearest = sum(
            1 for r in records
            if abs(r['policies'][pol]['cost'] - r['policies']['nearest']['cost']) <= EPS)
        out[pol] = {
            'meanCost':    sum(costs) / n,
            'meanRegret':  sum(regrets) / n,
            'top1Acc':     top1 / n,
            'beatNearest': beat_nearest / n,
            'tieNearest':  tie_nearest / n,
        }
    smart, nearest = out['smart'], out['nearest']
    out['__savings__'] = {
        'minutesVsNearest': nearest['meanCost'] - smart['meanCost'],
        'pctVsNearest': ((nearest['meanCost'] - smart['meanCost']) / nearest['meanCost'] * 100)
                        if nearest['meanCost'] else 0.0,
        'minutesVsRandom': out['random']['meanCost'] - smart['meanCost'],
    }
    return out


def split_by_peak(records: list) -> dict:
    peak     = [r for r in records if r['isPeak']]
    off_peak = [r for r in records if not r['isPeak']]
    return {
        'peak':    decision_summary(peak) if peak else None,
        'offPeak': decision_summary(off_peak) if off_peak else None,
        'nPeak':   len(peak),
        'nOffPeak': len(off_peak),
    }


# ── Chất lượng xếp hạng ──────────────────────────────────────────────────────

def _dcg(relevances: list) -> float:
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


def ranking_summary(records: list) -> dict:
    """
    NDCG@5: relevance của ứng viên = nghịch đảo thứ hạng theo cost thật
    (tốt nhất = 1.0, thứ nhì 0.5, ...). MRR: 1/vị trí của oracle trong top-5
    smart-route (0 nếu không lọt top-5).
    """
    ndcgs, rrs = [], []
    for r in records:
        cost_rank = {c: i for i, c in enumerate(sorted(set(r['allCostsSorted'])))}
        rels = [1.0 / (cost_rank[c] + 1) for c in r['rankedCosts']]
        ideal = sorted((1.0 / (i + 1) for i in range(len(r['allCostsSorted']))),
                       reverse=True)[:len(rels)]
        idcg = _dcg(ideal)
        ndcgs.append(_dcg(rels) / idcg if idcg else 0.0)

        rr = 0.0
        for pos, aid in enumerate(r['rankedIds'], 1):
            if aid == r['oracleId']:
                rr = 1.0 / pos
                break
        rrs.append(rr)
    n = len(records)
    return {
        'ndcg@5': sum(ndcgs) / n if n else 0.0,
        'mrr':    sum(rrs) / n if n else 0.0,
        'oracleInTop1': sum(1 for x in rrs if x == 1.0) / n if n else 0.0,
        'oracleInTop5': sum(1 for x in rrs if x > 0) / n if n else 0.0,
    }


# ── Độ nhạy trọng số ─────────────────────────────────────────────────────────

def weight_sweep(run_simulation, n: int, seed: int, level_w: float = 0.10) -> list:
    """
    Quét dist_w từ 0.0→0.9 (queue_w = 0.9 − dist_w, level_w cố định 0.1)
    trên CÙNG bộ kịch bản (cùng seed). dist_w=0.9 ~ 'chỉ nhìn khoảng cách',
    dist_w=0.0 ~ 'chỉ nhìn hàng chờ'.
    """
    rows = []
    for step in range(10):
        dist_w = round(step * 0.1, 1)
        queue_w = round(0.9 - dist_w, 1)
        records = run_simulation(n=n, seed=seed, weights=(dist_w, queue_w, level_w))
        summary = decision_summary(records)['smart']
        rows.append({
            'distW': dist_w,
            'queueW': queue_w,
            'meanRegret': summary['meanRegret'],
            'top1Acc': summary['top1Acc'],
            'meanCost': summary['meanCost'],
        })
    return rows
