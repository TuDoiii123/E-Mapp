"""
Bộ đánh giá Smart-Route — AI gợi ý cơ quan tối ưu + chỉ đường.

Usage:
    python run_eval.py                    # 1000 kịch bản + quét trọng số + ETA
    python run_eval.py --n 200           # nhanh hơn
    python run_eval.py --skip-eta        # bỏ phần gọi OSRM
    python run_eval.py --skip-sweep      # bỏ quét trọng số

Xuất: reports/report.md + reports/details.csv
"""
import argparse
import csv
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows mặc định cp1252

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from simulate import run_simulation                                   # noqa: E402
from metrics import (decision_summary, split_by_peak, ranking_summary,  # noqa: E402
                     weight_sweep, POLICIES)
from services.smart_route_core import DIST_W, QUEUE_W, LEVEL_W          # noqa: E402

REPORTS_DIR = os.path.join(HERE, 'reports')

POLICY_NAMES = {
    'smart':      f'Smart-route ({int(DIST_W*100)}/{int(QUEUE_W*100)}/{int(LEVEL_W*100)})',
    'nearest':    'Baseline: gần nhất',
    'least_busy': 'Baseline: vắng nhất',
    'random':     'Baseline: ngẫu nhiên',
    'oracle':     'Oracle (tối ưu tuyệt đối)',
}


def build_report(records, decision, peak_split, ranking, sweep_rows, eta) -> str:
    n = len(records)
    lines = ['# Báo cáo đánh giá Smart-Route — AI gợi ý cơ quan tối ưu', '']
    lines.append(f'- Số kịch bản mô phỏng: **{n}** (vị trí × thời điểm ngẫu nhiên '
                 f'quanh Hà Nội, giờ hành chính T2–T6, seed cố định)')
    lines.append(f'- Nguồn hàng chờ: mô phỏng tất định theo (cơ quan × thứ × giờ) '
                 f'— cùng nguồn với dữ liệu demo trên deploy')
    lines.append('- Chi phí thật = thời gian đi (30 km/h) + thời gian chờ (5 phút/người)')
    lines.append('')

    # 1. So sánh chính sách
    oracle_cost = sum(r['oracleCost'] for r in records) / n
    lines.append('## 1. Chất lượng quyết định — so 4 chính sách')
    lines.append('')
    lines.append('| Chính sách | Tổng thời gian TB (phút) | Regret TB (phút) | Top-1 = oracle | Thắng "gần nhất" |')
    lines.append('|---|---|---|---|---|')
    lines.append(f"| {POLICY_NAMES['oracle']} | {oracle_cost:.1f} | 0.0 | 100.0% | — |")
    for pol in POLICIES:
        d = decision[pol]
        beat = f"{d['beatNearest'] * 100:.1f}%" if pol != 'nearest' else '—'
        lines.append(f"| {POLICY_NAMES[pol]} | {d['meanCost']:.1f} "
                     f"| {d['meanRegret']:.1f} | {d['top1Acc'] * 100:.1f}% | {beat} |")
    sv = decision['__savings__']
    lines.append('')
    lines.append(f"**Kết luận chính**: smart-route tiết kiệm trung bình "
                 f"**{sv['minutesVsNearest']:.1f} phút/lượt ({sv['pctVsNearest']:.1f}%)** "
                 f"so với chọn cơ quan gần nhất, và "
                 f"{sv['minutesVsRandom']:.1f} phút so với chọn ngẫu nhiên.")
    lines.append('')

    # 2. Cao điểm vs thấp điểm
    lines.append('## 2. Theo khung giờ')
    lines.append('')
    lines.append('| Khung giờ | Kịch bản | Smart tiết kiệm vs gần nhất | Regret smart (phút) | Top-1 |')
    lines.append('|---|---|---|---|---|')
    for label, key, cnt in (('Cao điểm (9–10h, 14–15h)', 'peak', peak_split['nPeak']),
                            ('Thấp điểm', 'offPeak', peak_split['nOffPeak'])):
        d = peak_split[key]
        if not d:
            continue
        s = d['__savings__']
        lines.append(f"| {label} | {cnt} | {s['minutesVsNearest']:.1f} phút "
                     f"({s['pctVsNearest']:.1f}%) | {d['smart']['meanRegret']:.1f} "
                     f"| {d['smart']['top1Acc'] * 100:.1f}% |")
    lines.append('')

    # 3. Xếp hạng
    lines.append('## 3. Chất lượng xếp hạng danh sách gợi ý')
    lines.append('')
    lines.append(f"- **NDCG@5**: {ranking['ndcg@5']:.4f}")
    lines.append(f"- **MRR**: {ranking['mrr']:.4f}")
    lines.append(f"- Oracle nằm ở gợi ý #1: {ranking['oracleInTop1'] * 100:.1f}%")
    lines.append(f"- Oracle nằm trong top-5: {ranking['oracleInTop5'] * 100:.1f}%")
    lines.append('')

    # 4. Quét trọng số
    if sweep_rows:
        lines.append('## 4. Độ nhạy trọng số (level_w cố định 0.1)')
        lines.append('')
        lines.append('| dist_w | queue_w | Regret TB (phút) | Top-1 | Ghi chú |')
        lines.append('|---|---|---|---|---|')
        best = min(sweep_rows, key=lambda r: r['meanRegret'])
        for r in sweep_rows:
            note = []
            if r['distW'] == round(DIST_W, 1):
                note.append('**cấu hình hiện tại**')
            if r is best:
                note.append('tối ưu')
            if r['distW'] == 0.9:
                note.append('~chỉ khoảng cách')
            if r['distW'] == 0.0:
                note.append('~chỉ hàng chờ')
            lines.append(f"| {r['distW']:.1f} | {r['queueW']:.1f} "
                         f"| {r['meanRegret']:.2f} | {r['top1Acc'] * 100:.1f}% "
                         f"| {', '.join(note)} |")
        lines.append('')

    # 5. ETA
    if eta and eta['n']:
        lines.append('## 5. Độ chính xác ước tính thời gian đi (vs OSRM)')
        lines.append('')
        lines.append(f"- Số tuyến kiểm tra: **{eta['n']}** (phân tầng gần/trung/xa, "
                     f"{eta['nApi']} gọi API mới, còn lại từ cache)")
        lines.append(f"- **MAE**: {eta['maeMin']} phút — **MAPE**: {eta['mapePct']}%")
        lines.append(f"- Bias: {eta['biasMin']:+.2f} phút "
                     f"({'ước tính THẤP hơn thật' if eta['biasMin'] < 0 else 'ước tính CAO hơn thật'})")
        lines.append(f"- Hệ số đường vòng TB (đường thật ÷ đường chim bay): "
                     f"**{eta['meanDetour']}×**")
        lines.append('')

    # Định nghĩa
    lines.append('## Định nghĩa chỉ số')
    lines.append('')
    lines.append('- **Chi phí thật** — tổng phút: đi (khoảng cách ÷ 30 km/h) + chờ (số người × 5 phút).')
    lines.append('- **Oracle** — lựa chọn có chi phí thật thấp nhất trong các ứng viên (biết trước tất cả).')
    lines.append('- **Regret** — chi phí của chính sách trừ chi phí oracle; 0 = luôn chọn tối ưu.')
    lines.append('- **Top-1 accuracy** — tỷ lệ kịch bản chính sách chọn đúng cơ quan tối ưu (hoặc đồng chi phí).')
    lines.append('- **NDCG@5** — chất lượng thứ tự 5 gợi ý so với thứ tự lý tưởng theo chi phí thật (1.0 = hoàn hảo).')
    lines.append('- **MRR** — trung bình 1/vị trí của lựa chọn tối ưu trong danh sách gợi ý.')
    lines.append('- **MAE / MAPE (ETA)** — sai số tuyệt đối trung bình (phút / %) giữa ước tính và OSRM.')
    lines.append('')
    return '\n'.join(lines)


def write_csv(records: list, path: str):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scenarioId', 'isPeak', 'nCandidates', 'oracleCost'] +
                   [f'{p}_{k}' for p in POLICIES for k in ('id', 'cost')])
        for r in records:
            row = [r['scenarioId'], int(r['isPeak']), r['nCandidates'], r['oracleCost']]
            for p in POLICIES:
                row += [r['policies'][p]['id'], r['policies'][p]['cost']]
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser(description='Đánh giá smart-route')
    ap.add_argument('--n', type=int, default=1000, help='số kịch bản')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--sweep-n', type=int, default=300,
                    help='số kịch bản mỗi bộ trọng số khi quét')
    ap.add_argument('--eta-pairs', type=int, default=30)
    ap.add_argument('--skip-eta', action='store_true')
    ap.add_argument('--skip-sweep', action='store_true')
    args = ap.parse_args()

    print(f'Mô phỏng {args.n} kịch bản quanh Hà Nội ...')
    records = run_simulation(n=args.n, seed=args.seed)
    print(f'  → {len(records)} kịch bản hợp lệ (≥3 ứng viên trong 10 km)')

    decision = decision_summary(records)
    peak_split = split_by_peak(records)
    ranking = ranking_summary(records)

    sweep_rows = []
    if not args.skip_sweep:
        print(f'Quét 10 bộ trọng số × {args.sweep_n} kịch bản ...')
        sweep_rows = weight_sweep(run_simulation, n=args.sweep_n, seed=args.seed)

    eta = None
    if not args.skip_eta:
        print(f'Kiểm tra ETA với OSRM ({args.eta_pairs} tuyến, ~1 req/s) ...')
        from eta_check import run_eta_check
        eta = run_eta_check(args.eta_pairs, args.seed)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_path = os.path.join(REPORTS_DIR, 'report.md')
    csv_path = os.path.join(REPORTS_DIR, 'details.csv')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(build_report(records, decision, peak_split, ranking, sweep_rows, eta))
    write_csv(records, csv_path)

    sv = decision['__savings__']
    print()
    print(f"Smart-route: regret TB {decision['smart']['meanRegret']:.1f} phút, "
          f"Top-1 {decision['smart']['top1Acc'] * 100:.1f}%, "
          f"tiết kiệm {sv['minutesVsNearest']:.1f} phút ({sv['pctVsNearest']:.1f}%) vs gần nhất")
    print(f'Báo cáo: {md_path}')
    print(f'Chi tiết: {csv_path}')


if __name__ == '__main__':
    main()
