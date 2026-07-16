"""
Runner bộ đánh giá Gemini OCR — chạy tích luỹ theo quota.

Nguyên tắc: mỗi ảnh chỉ gọi Gemini ĐÚNG 1 LẦN. Kết quả thô cache theo
SHA-256 của file ảnh vào cache/ — chấm lại điểm, đổi cách so khớp, chạy
lại báo cáo đều không tốn request. Gặp lỗi quota (429) thì dừng nhẹ nhàng,
lần sau chạy tiếp từ chỗ dừng.

Usage:
    python run_eval.py                    # chạy toàn bộ dataset (đến khi hết quota)
    python run_eval.py --sample 100      # lấy mẫu phân tầng 100 ảnh
    python run_eval.py --limit 15        # tối đa 15 lần gọi API trong lần chạy này
    python run_eval.py --doc-type cccd   # chỉ chấm CCCD
    python run_eval.py --report-only     # không gọi API, chấm từ cache
"""
import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')  # console Windows mặc định cp1252

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(HERE, '..', '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from scoring import score_document, score_form, validate_output  # noqa: E402

DATASET_DIR = os.path.join(HERE, 'dataset')
CACHE_DIR = os.path.join(HERE, 'cache')
REPORTS_DIR = os.path.join(HERE, 'reports')

QUOTA_MARKERS = ('429', 'RESOURCE_EXHAUSTED', 'quota', 'rate limit')


def _load_env():
    """Nạp .env của Backend để lấy GEMINI_API_KEY."""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BACKEND_DIR, '.env'))
    except ImportError:
        pass


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:20]


def load_labels(doc_type: str = None) -> list:
    labels_dir = os.path.join(DATASET_DIR, 'labels')
    if not os.path.isdir(labels_dir):
        sys.exit(f'Chưa có dataset. Chạy trước: python generate_dataset.py --count 1000')
    labels = []
    for fn in sorted(os.listdir(labels_dir)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(labels_dir, fn), encoding='utf-8') as f:
            label = json.load(f)
        if doc_type and label.get('docType') != doc_type:
            continue
        labels.append(label)
    return labels


def stratified_sample(labels: list, n: int, seed: int = 42) -> list:
    """Lấy mẫu đều theo (docType, variant) — round-robin từng nhóm."""
    import random
    rng = random.Random(seed)
    groups = defaultdict(list)
    for label in labels:
        groups[(label['docType'], label['variant'])].append(label)
    for g in groups.values():
        rng.shuffle(g)
    picked = []
    keys = sorted(groups.keys())
    while len(picked) < n and any(groups[k] for k in keys):
        for k in keys:
            if groups[k] and len(picked) < n:
                picked.append(groups[k].pop())
    return picked


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(m.lower() in msg for m in QUOTA_MARKERS)


def extract_with_cache(label: dict, retry_errors: bool = False) -> tuple:
    """
    Trả về (cache_entry | None, api_called: bool).
    cache_entry: {'data': dict} hoặc {'error': str}.
    None = ảnh không tồn tại. Raise RuntimeError('quota') khi hết quota.
    """
    image_path = os.path.join(DATASET_DIR, 'images', label['image'])
    if not os.path.exists(image_path):
        return None, False

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, _file_hash(image_path) + '.json')

    if os.path.exists(cache_path):
        with open(cache_path, encoding='utf-8') as f:
            entry = json.load(f)
        if 'data' in entry or not retry_errors:
            return entry, False

    from services.image_extractor import extract_document, extract_form_template
    extractor = extract_form_template if label['docType'] == 'form' else extract_document

    try:
        t0 = time.perf_counter()
        data = extractor(image_path)
        entry = {'image': label['image'], 'data': data,
                 'elapsedSec': round(time.perf_counter() - t0, 2)}
    except Exception as e:
        if _is_quota_error(e):
            raise RuntimeError('quota') from e
        # Lỗi khác (parse JSON hỏng, ảnh không đọc được…) — cache lại để không
        # đốt thêm quota; chạy --retry-errors nếu muốn thử lại.
        entry = {'image': label['image'], 'error': str(e)[:500]}

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=1)
    return entry, True


def score_one(label: dict, entry: dict, postcorrect: bool = True) -> dict:
    result = {
        'image': label['image'],
        'docType': label['docType'],
        'variant': label['variant'],
    }
    if entry is None or 'error' in entry:
        result['status'] = 'error'
        result['error'] = (entry or {}).get('error', 'thiếu ảnh')
        return result
    result['status'] = 'ok'
    result['elapsedSec'] = entry.get('elapsedSec')
    if label['docType'] == 'form':
        result['form'] = score_form(label['expected'], entry['data'])
    else:
        data = entry['data']
        if postcorrect:
            # Cùng hậu xử lý với production (idempotent — cache mới đã corrected)
            from services.ocr_postcorrect import postcorrect_document
            data = postcorrect_document(data)
        result['fields'] = score_document(label['expected'], data)
        result['validity'] = validate_output(label['docType'], data)
    return result


def main():
    ap = argparse.ArgumentParser(description='Chạy đánh giá Gemini OCR')
    ap.add_argument('--sample', type=int, help='lấy mẫu phân tầng N ảnh')
    ap.add_argument('--limit', type=int, help='tối đa N lần gọi API lần chạy này')
    ap.add_argument('--doc-type', choices=['cccd', 'gplx', 'marriage', 'form'])
    ap.add_argument('--report-only', action='store_true',
                    help='không gọi API, chỉ chấm từ cache')
    ap.add_argument('--retry-errors', action='store_true',
                    help='gọi lại API cho các ảnh từng lỗi')
    ap.add_argument('--no-postcorrect', action='store_true',
                    help='chấm bản THÔ không hậu xử lý (đo baseline)')
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()
    postcorrect = not args.no_postcorrect

    _load_env()

    labels = load_labels(args.doc_type)
    total_labeled = len(labels)
    if args.sample:
        labels = stratified_sample(labels, args.sample, args.seed)
    print(f'Dataset: {total_labeled} ảnh có nhãn, đánh giá {len(labels)} ảnh')

    results = []
    api_calls = 0
    cached_hits = 0
    quota_hit = False

    for i, label in enumerate(labels):
        if args.report_only:
            image_path = os.path.join(DATASET_DIR, 'images', label['image'])
            entry = None
            if os.path.exists(image_path):
                cache_path = os.path.join(CACHE_DIR, _file_hash(image_path) + '.json')
                if os.path.exists(cache_path):
                    with open(cache_path, encoding='utf-8') as f:
                        entry = json.load(f)
            if entry is None:
                continue  # report-only: bỏ qua ảnh chưa có kết quả
            cached_hits += 1
            results.append(score_one(label, entry, postcorrect))
            continue

        if args.limit and api_calls >= args.limit:
            print(f'Đã chạm --limit {args.limit} lần gọi API, dừng gọi thêm.')
            break
        try:
            entry, called = extract_with_cache(label, args.retry_errors)
        except RuntimeError:
            quota_hit = True
            print(f'⚠ Hết quota Gemini sau {api_calls} lần gọi — dừng. '
                  f'Chạy lại vào ngày mai để tiếp tục từ chỗ này.')
            break
        if called:
            api_calls += 1
            print(f'  [{i + 1}/{len(labels)}] gọi API: {label["image"]}')
        else:
            cached_hits += 1
        if entry is not None:
            results.append(score_one(label, entry, postcorrect))

    if not results:
        print('Chưa có kết quả nào (cache trống và không gọi được API).')
        return

    from report import build_markdown, build_csv
    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_path = os.path.join(REPORTS_DIR, 'report.md')
    csv_path = os.path.join(REPORTS_DIR, 'details.csv')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(build_markdown(results, total_labeled))
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(build_csv(results))

    n_ok = sum(1 for r in results if r['status'] == 'ok')
    doc_fields = [f for r in results if r['status'] == 'ok'
                  for f in r.get('fields', [])]
    ok_fields = sum(1 for f in doc_fields if f['match'])
    print()
    print(f'Kết quả: {len(results)} ảnh chấm được ({n_ok} trích xuất OK), '
          f'API mới: {api_calls}, từ cache: {cached_hits}')
    if doc_fields:
        print(f'Độ chính xác trường (giấy tờ cá nhân): '
              f'{ok_fields}/{len(doc_fields)} = {100.0 * ok_fields / len(doc_fields):.1f}%')
    print(f'Báo cáo: {md_path}')
    print(f'Chi tiết: {csv_path}')
    if quota_hit:
        remaining = total_labeled - len(results)
        print(f'Còn ~{remaining} ảnh chưa chạy — chạy lại lệnh này khi quota reset.')


if __name__ == '__main__':
    main()
