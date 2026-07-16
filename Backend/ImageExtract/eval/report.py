"""
Xuất báo cáo đánh giá: markdown (đọc) + CSV (phân tích tiếp).

Input: list kết quả từ run_eval, mỗi phần tử:
  {image, docType, variant, status: 'ok'|'error',
   fields: [...] (giấy tờ cá nhân) | form: {...} (biểu mẫu), error: str?}
"""
import csv
import io
from collections import defaultdict

from scoring import CRITICAL_FIELDS, aggregate_metrics

DOC_NAMES = {
    'cccd': 'Căn cước công dân',
    'gplx': 'Giấy phép lái xe',
    'marriage': 'Giấy chứng nhận kết hôn',
    'form': 'Biểu mẫu trống',
}


def _pct(n, d):
    return f'{100.0 * n / d:.1f}%' if d else '—'


def _doc_results(results):
    return [r for r in results if r['docType'] != 'form']


def _form_results(results):
    return [r for r in results if r['docType'] == 'form']


# ── Markdown ──────────────────────────────────────────────────────────────────

def build_markdown(results: list, total_labeled: int) -> str:
    lines = ['# Báo cáo đánh giá Gemini OCR — trích xuất dữ liệu', '']
    n_eval = len(results)
    n_err = sum(1 for r in results if r['status'] != 'ok')
    lines.append(f'- Số ảnh đã đánh giá: **{n_eval}** / {total_labeled} ảnh có nhãn')
    lines.append(f'- Trích xuất lỗi (không ra JSON / lỗi gọi API đã cache): **{n_err}**')
    lines.append('')

    # ── 1. Tổng quan theo loại giấy tờ ──
    lines.append('## 1. Tổng quan theo loại giấy tờ')
    lines.append('')
    lines.append('| Loại giấy tờ | Số ảnh | Trường đúng / tổng | Độ chính xác trường |')
    lines.append('|---|---|---|---|')
    by_doc = defaultdict(list)
    for r in _doc_results(results):
        by_doc[r['docType']].append(r)
    for doc, rs in sorted(by_doc.items()):
        fields = [f for r in rs if r['status'] == 'ok' for f in r['fields']]
        ok = sum(1 for f in fields if f['match'])
        lines.append(f'| {DOC_NAMES.get(doc, doc)} | {len(rs)} | {ok}/{len(fields)} | {_pct(ok, len(fields))} |')
    forms = _form_results(results)
    if forms:
        oks = [r['form'] for r in forms if r['status'] == 'ok']
        mean_f1 = sum(f['f1'] for f in oks) / len(oks) if oks else 0
        lines.append(f'| Biểu mẫu trống | {len(forms)} | F1 phát hiện trường | {mean_f1 * 100:.1f}% |')
    lines.append('')

    # ── 2. Bộ chỉ số tổng hợp (cho đồ án) ──
    metrics = aggregate_metrics(results)
    if metrics:
        lines.append('## 2. Bộ chỉ số tổng hợp')
        lines.append('')
        lines.append('| Loại giấy tờ | Ảnh | Accuracy | Precision | Recall | F1 | CER | WER | Similarity | EM tài liệu |')
        lines.append('|---|---|---|---|---|---|---|---|---|---|')
        order = [k for k in ('cccd', 'gplx', 'marriage') if k in metrics]
        for doc in order + ['__overall__']:
            m = metrics[doc]
            name = '**Tổng hợp**' if doc == '__overall__' else DOC_NAMES.get(doc, doc)
            lines.append(
                f"| {name} | {m['nDocs']} "
                f"| {m['accuracy'] * 100:.1f}% | {m['precision'] * 100:.1f}% "
                f"| {m['recall'] * 100:.1f}% | {m['f1'] * 100:.1f}% "
                f"| {m['cer']:.4f} | {m['wer']:.4f} "
                f"| {m['similarity'] * 100:.1f}% | {m['docExactMatch'] * 100:.1f}% |")
        lines.append('')
        ov = metrics['__overall__']
        if ov.get('typeAccuracy') is not None:
            lines.append(f'- Nhận diện đúng loại giấy tờ: **{ov["typeAccuracy"] * 100:.1f}%**')
        if ov.get('latencyMean') is not None:
            lines.append(f'- Độ trễ xử lý mỗi ảnh (Gemini 2.5 Flash): trung bình '
                         f'**{ov["latencyMean"]:.1f}s**, p95 **{ov["latencyP95"]:.1f}s**')
        lines.append('')
        lines.append('**Định nghĩa chỉ số** (tính trên ảnh trích xuất thành công, '
                     'chuỗi đã chuẩn hoá khoảng trắng/hoa-thường, ngày đưa về dd/mm/yyyy):')
        lines.append('')
        lines.append('- **Accuracy** — số trường trích đúng / tổng số trường.')
        lines.append('- **Precision** — trường đúng / số trường model trả ra khác rỗng '
                     '(phạt việc "bịa" giá trị sai).')
        lines.append('- **Recall** — trường đúng / số trường kỳ vọng khác rỗng '
                     '(phạt việc bỏ sót, trả rỗng).')
        lines.append('- **F1** — trung bình điều hoà của Precision và Recall.')
        lines.append('- **CER / WER** — tỷ lệ lỗi ký tự / lỗi từ '
                     '(khoảng cách Levenshtein ÷ độ dài kỳ vọng), trung bình mọi trường.')
        lines.append('- **Similarity** — 1 − Levenshtein chuẩn hoá, trung bình mọi trường.')
        lines.append('- **EM tài liệu** — tỷ lệ ảnh mà TOÀN BỘ trường đều đúng (Exact Match).')
        lines.append('')

    # ── 3. Độ chính xác từng trường ──
    lines.append('## 3. Độ chính xác từng trường')
    for doc, rs in sorted(by_doc.items()):
        lines.append('')
        lines.append(f'### {DOC_NAMES.get(doc, doc)}')
        lines.append('')
        lines.append('| Trường | Đúng | Tổng | Chính xác | CER TB (khi sai) |')
        lines.append('|---|---|---|---|---|')
        stat = defaultdict(lambda: {'ok': 0, 'n': 0, 'cers': []})
        for r in rs:
            if r['status'] != 'ok':
                continue
            for f in r['fields']:
                s = stat[f['field']]
                s['n'] += 1
                if f['match']:
                    s['ok'] += 1
                else:
                    s['cers'].append(f['cer'])
        for field, s in stat.items():
            mean_cer = f"{sum(s['cers']) / len(s['cers']):.3f}" if s['cers'] else '—'
            lines.append(f"| {field} | {s['ok']} | {s['n']} | {_pct(s['ok'], s['n'])} | {mean_cer} |")
    lines.append('')

    # ── 3. Theo biến thể chất lượng ảnh ──
    lines.append('## 4. Độ chính xác theo chất lượng ảnh')
    lines.append('')
    lines.append('| Loại giấy tờ | clean | blur | tilt | dark |')
    lines.append('|---|---|---|---|---|')
    for doc, rs in sorted(by_doc.items()):
        row = [DOC_NAMES.get(doc, doc)]
        for variant in ('clean', 'blur', 'tilt', 'dark'):
            fields = [f for r in rs
                      if r['variant'] == variant and r['status'] == 'ok'
                      for f in r['fields']]
            ok = sum(1 for f in fields if f['match'])
            row.append(_pct(ok, len(fields)))
        lines.append('| ' + ' | '.join(row) + ' |')
    if forms:
        row = ['Biểu mẫu (F1)']
        for variant in ('clean', 'blur', 'tilt', 'dark'):
            fs = [r['form'] for r in forms if r['variant'] == variant and r['status'] == 'ok']
            row.append(f"{sum(f['f1'] for f in fs) / len(fs) * 100:.1f}%" if fs else '—')
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')

    # ── 4. Mức ảnh hưởng khi tự điền hồ sơ ──
    doc_ok = [r for r in _doc_results(results) if r['status'] == 'ok']
    if doc_ok:
        perfect, critical_err, minor_err = [], [], []
        n_fix_total = 0
        for r in doc_ok:
            wrong = [f['field'] for f in r['fields'] if not f['match']]
            n_fix_total += len(wrong)
            crit = CRITICAL_FIELDS.get(r['docType'], set())
            if not wrong:
                perfect.append(r)
            elif any(f in crit for f in wrong):
                critical_err.append(r)
            else:
                minor_err.append(r)
        n = len(doc_ok)
        n_fail = len([r for r in _doc_results(results) if r['status'] != 'ok'])
        lines.append('## 5. Mức ảnh hưởng khi tự điền hồ sơ')
        lines.append('')
        lines.append('Trường định danh = số giấy tờ, họ tên, ngày sinh/kết hôn — sai là hồ sơ bị trả lại.')
        lines.append('')
        lines.append('| Kịch bản với người dùng | Số ảnh | Tỷ lệ |')
        lines.append('|---|---|---|')
        lines.append(f'| Tự điền đúng 100%, không phải sửa gì | {len(perfect)} | {_pct(len(perfect), n)} |')
        lines.append(f'| Sai ở trường định danh (rủi ro hồ sơ bị trả) | {len(critical_err)} | {_pct(len(critical_err), n)} |')
        lines.append(f'| Chỉ sai trường phụ (sửa nhanh được) | {len(minor_err)} | {_pct(len(minor_err), n)} |')
        if n_fail:
            lines.append(f'| Trích xuất thất bại, phải nhập tay toàn bộ | {n_fail} | {_pct(n_fail, n + n_fail)} |')
        lines.append('')
        lines.append(f'- Trung bình mỗi hồ sơ phải sửa tay: **{n_fix_total / n:.2f} trường**')
        # tỷ lệ "không phải sửa" theo chất lượng ảnh
        row_ok, row_n = defaultdict(int), defaultdict(int)
        for r in doc_ok:
            row_n[r['variant']] += 1
            if all(f['match'] for f in r['fields']):
                row_ok[r['variant']] += 1
        parts = [f"{v}: {_pct(row_ok[v], row_n[v])}"
                 for v in ('clean', 'blur', 'tilt', 'dark') if row_n[v]]
        lines.append(f'- Tỷ lệ "không phải sửa" theo chất lượng ảnh: ' + ', '.join(parts))
        lines.append('')

    # ── 5. Tính hợp lệ định dạng dữ liệu xuất ra ──
    val_results = [r for r in doc_ok if r.get('validity')]
    if val_results:
        n = len(val_results)
        schema_ok = sum(1 for r in val_results if r['validity']['schemaOk'])
        n_invalid = sum(len(r['validity']['invalidFormat']) for r in val_results)
        total_fields = sum(r['validity']['nKeys'] for r in val_results)
        total_empty = sum(len(r['validity']['emptyFields']) for r in val_results)
        lines.append('## 6. Tính hợp lệ định dạng dữ liệu xuất ra')
        lines.append('')
        lines.append('Kiểm tra độc lập với đáp án — dữ liệu sai định dạng thì form tự điền phía Frontend sẽ điền hỏng dù nội dung đọc đúng.')
        lines.append('')
        lines.append(f'- JSON đủ khóa schema theo prompt: **{_pct(schema_ok, n)}** ({schema_ok}/{n})')
        lines.append(f'- Giá trị sai định dạng (số giấy tờ ≠ 9/12 chữ số, ngày không parse được, giới tính lạ): **{n_invalid}**')
        lines.append(f'- Trường bị bỏ trống: **{total_empty}/{total_fields}** ({_pct(total_empty, total_fields)})')
        bad = [(r, iv) for r in val_results for iv in r['validity']['invalidFormat']]
        for r, iv in bad[:10]:
            lines.append(f"  - {r['image']} — `{iv['field']}` = {iv['value']!r}: {iv['reason']}")
        missing = [(r, k) for r in val_results for k in r['validity']['missingKeys']]
        for r, k in missing[:10]:
            lines.append(f"  - {r['image']} — thiếu khóa `{k}`")
        lines.append('')

    # ── 6. Biểu mẫu trống chi tiết ──
    if forms:
        oks = [r for r in forms if r['status'] == 'ok']
        lines.append('## 7. Biểu mẫu trống — phát hiện cấu trúc')
        lines.append('')
        if oks:
            mean = lambda key: sum(r['form'][key] for r in oks) / len(oks)
            name_ok = [r['form']['formNameMatch'] for r in oks if r['form']['formNameMatch'] is not None]
            code_ok = [r['form']['formCodeMatch'] for r in oks if r['form']['formCodeMatch'] is not None]
            lines.append(f'- Recall phát hiện trường (TB): **{mean("recall") * 100:.1f}%**')
            lines.append(f'- Precision (TB): **{mean("precision") * 100:.1f}%**')
            lines.append(f'- F1 (TB): **{mean("f1") * 100:.1f}%**')
            lines.append(f'- Nhận đúng tên biểu mẫu: **{_pct(sum(name_ok), len(name_ok))}**')
            lines.append(f'- Nhận đúng mã biểu mẫu: **{_pct(sum(code_ok), len(code_ok))}**')
        lines.append('')

    # ── 5. Các case sai nhiều nhất ──
    scored = []
    for r in _doc_results(results):
        if r['status'] != 'ok' or not r['fields']:
            continue
        acc = sum(1 for f in r['fields'] if f['match']) / len(r['fields'])
        scored.append((acc, r))
    scored.sort(key=lambda t: t[0])
    worst = [t for t in scored if t[0] < 1.0][:10]
    if worst:
        lines.append('## 8. Các ảnh sai nhiều nhất')
        lines.append('')
        for acc, r in worst:
            bad = [f"`{f['field']}` (kỳ vọng: {f['expected']!r}, nhận: {f['predicted']!r})"
                   for f in r['fields'] if not f['match']]
            lines.append(f"- **{r['image']}** — đúng {acc * 100:.0f}%: " + '; '.join(bad[:4]))
        lines.append('')

    errors = [r for r in results if r['status'] != 'ok']
    if errors:
        lines.append('## Ảnh trích xuất lỗi')
        lines.append('')
        for r in errors[:20]:
            lines.append(f"- {r['image']}: {r.get('error', 'không rõ')}")
        lines.append('')

    return '\n'.join(lines)


# ── CSV ───────────────────────────────────────────────────────────────────────

def build_csv(results: list) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['image', 'docType', 'variant', 'status', 'field',
                'expected', 'predicted', 'match', 'cer', 'wer', 'sim', 'critical'])
    for r in results:
        if r['docType'] == 'form':
            form = r.get('form') or {}
            w.writerow([r['image'], r['docType'], r['variant'], r['status'],
                        '__form__', form.get('nExpected', ''), form.get('nMatched', ''),
                        form.get('f1', ''), '', '', '', ''])
            continue
        if r['status'] != 'ok':
            w.writerow([r['image'], r['docType'], r['variant'], r['status'],
                        '', '', '', '', '', '', '', ''])
            continue
        crit = CRITICAL_FIELDS.get(r['docType'], set())
        for f in r['fields']:
            w.writerow([r['image'], r['docType'], r['variant'], r['status'],
                        f['field'], f['expected'], f['predicted'],
                        int(f['match']), f['cer'], f.get('wer', ''),
                        f.get('sim', ''), int(f['field'] in crit)])
    return buf.getvalue()
