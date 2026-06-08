#!/usr/bin/env python3
"""
Parse chitiet_dvc_tructuyen (trinh_tu, cach_thuc, yeu_cau, co_quan)
→ UPDATE procedures (processing_days, processing_note, fee_note, agency, steps, conditions)

Chỉ update raw procedures (numeric IDs: 1.000894, 2.000033, ...).
Clean procedures đã có data tốt hơn — không đụng vào.

Run: python scripts/enrich_procedures_from_dvc.py [--dry-run]
"""
import re, sys
import psycopg2

DB = dict(host='localhost', port=5432, dbname='postgres',
          user='postgres', password='tubeo123')

_RAW_PROC_RE = re.compile(r'^\d+\.\d+$')


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_cach_thuc(text: str) -> dict:
    """
    Extract processing_days, processing_note, fee_note từ cach_thuc_thuc_hien.
    Format: [{Hình thức nộp: ..., Thời hạn giải quyết: XX Ngày làm việc, Phí, lệ phí: ...}, ...]
    """
    result = {'processing_days': None, 'processing_note': None, 'fee_note': None}
    if not text:
        return result

    # Lấy Thời hạn giải quyết từ record đầu tiên
    m_thoihan = re.search(r'Thời hạn giải quyết:\s*([^,}]+)', text)
    if m_thoihan:
        note = m_thoihan.group(1).strip().rstrip('.,')
        result['processing_note'] = note

        # Tìm số ngày từ note
        m_days = re.search(r'(\d+)\s*[Nn]gày\s*làm\s*việc', note)
        if m_days:
            result['processing_days'] = int(m_days.group(1))
        elif 'ngay trong ngày' in note.lower() or 'ngay trong ngay' in note.lower():
            result['processing_days'] = 1
        elif 'không quy định' in note.lower() or 'khong quy dinh' in note.lower():
            result['processing_days'] = None

    # Lấy phí/lệ phí — tìm số tiền trước
    m_phi_amount = re.search(r'(\d[\d\.]{2,})\s*[ĐđD]ồng', text)
    if m_phi_amount:
        amount_str = m_phi_amount.group(1).replace('.', '')
        try:
            amount = int(amount_str)
            if amount > 0:
                result['fee_note'] = f'{amount:,} đồng'.replace(',', '.')
        except ValueError:
            pass
    else:
        # Tìm text phí có nội dung thực
        m_phi = re.search(r'Phí,?\s*lệ phí:\s*([^,}]{8,200})', text)
        if m_phi:
            fee_raw = m_phi.group(1).strip()
            fee_raw = re.sub(r'Xem chi tiết', '', fee_raw, flags=re.IGNORECASE).strip()
            # Bỏ các giá trị rác
            junk = ('', 'lệ phí:', 'phí:', 'đồng', 'không', 'khong', '0')
            if fee_raw.lower().rstrip('.: ') not in junk and len(fee_raw) > 5:
                result['fee_note'] = fee_raw[:200]

    # Clean processing_note rác
    if result['processing_note'] in ('0', '0.', 'Không quy định', 'khong quy dinh'):
        if result['processing_note'] == '0':
            result['processing_note'] = None

    return result


def parse_trinh_tu(text: str) -> str | None:
    """Clean up trinh_tu_thuc_hien thành text có cấu trúc."""
    if not text or not text.strip():
        return None

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Bỏ các dòng quá ngắn (< 5 chars) hoặc chỉ là số thứ tự
    lines = [l for l in lines if len(l) >= 5 and not re.match(r'^[\d\.\-]+$', l)]
    if not lines:
        return None

    return '\n'.join(lines[:20])  # Giới hạn 20 dòng đầu


def parse_yeu_cau(text: str) -> str | None:
    """Clean up yeu_cau_dieu_kien_thuc_hien."""
    if not text or not text.strip():
        return None
    t = text.strip()
    if t.lower() in ('không', 'khong', 'không quy định', 'không có', 'không có.',
                     'khong quy dinh', 'không.', 'not applicable'):
        return None

    lines = [l.strip() for l in t.splitlines() if l.strip() and len(l.strip()) >= 5]
    if not lines:
        return None
    return '\n'.join(lines[:15])


def parse_co_quan(text: str) -> str | None:
    """Lấy cơ quan thực hiện đầu tiên (không lấy dòng trống / rác)."""
    if not text or not text.strip():
        return None
    lines = [l.strip() for l in text.splitlines() if l.strip() and len(l.strip()) > 3]
    return lines[0] if lines else None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print('=== DRY RUN ===\n')

    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    # Lấy tất cả raw procedures (numeric IDs)
    cur.execute("SELECT id, name FROM procedures WHERE id ~ '^\\d+\\.\\d+' ORDER BY id")
    raw_procs = cur.fetchall()
    print(f'Raw procedures cần enrich: {len(raw_procs)}')

    total_updated = 0

    for proc_id, proc_name in raw_procs:
        # Lấy 1 record từ chitiet_dvc_tructuyen
        cur.execute("""
            SELECT DISTINCT ON (1)
              trinh_tu_thuc_hien,
              cach_thuc_thuc_hien,
              co_quan_thuc_hien,
              yeu_cau_dieu_kien_thuc_hien
            FROM chitiet_dvc_tructuyen
            WHERE url_chi_tiet LIKE %s
              AND url_chi_tiet != 'url_chi_tiet'
            LIMIT 1
        """, (f'%ma_thu_tuc={proc_id}%',))
        row = cur.fetchone()

        if not row:
            print(f'  ⚠ {proc_id}: không tìm thấy trong chitiet_dvc_tructuyen')
            continue

        trinh_tu, cach_thuc, co_quan, yeu_cau = row

        # Parse
        ct = parse_cach_thuc(cach_thuc or '')
        steps      = parse_trinh_tu(trinh_tu or '')
        conditions = parse_yeu_cau(yeu_cau or '')
        agency     = parse_co_quan(co_quan or '')

        print(f'\n▶ {proc_id} — {proc_name[:55]}')
        print(f'  processing_days : {ct["processing_days"]}')
        print(f'  processing_note : {(ct["processing_note"] or "")[:70]}')
        print(f'  fee_note        : {(ct["fee_note"] or "")[:60]}')
        print(f'  agency          : {(agency or "")[:60]}')
        print(f'  steps           : {len(steps.splitlines()) if steps else 0} dòng')
        print(f'  conditions      : {len(conditions.splitlines()) if conditions else 0} dòng')

        if dry_run:
            continue

        cur.execute("""
            UPDATE procedures SET
              processing_days  = COALESCE(%s, processing_days),
              processing_note  = COALESCE(%s, processing_note),
              fee_note         = COALESCE(NULLIF(%s,''), fee_note),
              agency           = COALESCE(%s, agency),
              steps            = %s,
              conditions       = %s,
              updated_at       = NOW()
            WHERE id = %s
        """, (
            ct['processing_days'],
            ct['processing_note'],
            ct['fee_note'],
            agency,
            steps,
            conditions,
            proc_id,
        ))
        total_updated += 1

    if not dry_run:
        conn.commit()
        print(f'\n✅ Updated {total_updated} procedures.')
    else:
        print(f'\n[DRY RUN] Would update {len(raw_procs)} procedures.')

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
