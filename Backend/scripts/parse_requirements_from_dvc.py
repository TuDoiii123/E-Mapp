#!/usr/bin/env python3
"""
Parse chitiet_dvc_tructuyen.thanh_phan_ho_so → service_requirements (clean records).

Chiến lược:
- Chỉ xử lý các procedure đang có 0 clean records (ID không khớp raw regex).
- Không xóa record nào, chỉ INSERT thêm records với IDs dạng "{service_id}-doc-{n:03d}".
- IDs mới không khớp raw regex → _prefer_clean() tự động ưu tiên chúng.

Run: python scripts/parse_requirements_from_dvc.py [--dry-run]
"""
import re
import sys
import psycopg2
import psycopg2.extras

DB = dict(host='localhost', port=5432, dbname='postgres',
          user='postgres', password='tubeo123')

_RAW_REQ_RE = re.compile(r'^\d+\.\d+-req-\d+$')

# ── Parser ────────────────────────────────────────────────────────────────────

_SKIP_LINES = {
    'Bao gồm', 'Tên giấy tờ', 'Mẫu đơn, tờ khai', 'Số lượng',
    'bao gom', 'ten giay to', 'mau don, to khai', 'so luong',
}
_SECTION_HEADERS = re.compile(
    r'^\*\s*(Giấy tờ phải xuất trình|Lưu ý|Bao gồm|Giấy tờ phải nộp)', re.IGNORECASE
)
_COUNT_RE = re.compile(r'Bản chính:\s*(\d+)\s*-\s*Bản sao:\s*(\d+)', re.IGNORECASE)
_TEMPLATE_RE = re.compile(r'.+\.(doc|docx|pdf|xlsx|xls|doc\.|docx\.)$', re.IGNORECASE)


def _parse(text: str) -> list[dict]:
    """
    Parse thanh_phan_ho_so thành danh sách tài liệu có cấu trúc.
    Trả về list[{name, description, is_required, doc_type, template_file}]
    """
    if not text:
        return []

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    section = 'submit'   # 'submit' | 'present' | 'notes'
    current: dict | None = None
    docs: list[dict] = []

    def flush():
        nonlocal current
        if current:
            docs.append(current)
            current = None

    for line in lines:
        # ── Section header ────────────────────────────────────────────────
        m = _SECTION_HEADERS.match(line)
        if m:
            flush()
            hdr = m.group(1).lower()
            if 'xuất trình' in hdr:
                section = 'present'
            elif 'lưu ý' in hdr:
                section = 'notes'
            else:
                section = 'submit'
            continue

        # ── Notes section → skip all ──────────────────────────────────────
        if section == 'notes':
            continue

        # ── Skip column-header lines ──────────────────────────────────────
        if line in _SKIP_LINES or line.lower() in _SKIP_LINES:
            continue

        # ── Count line ────────────────────────────────────────────────────
        cm = _COUNT_RE.search(line)
        if cm:
            if current:
                current['ban_chinh'] = int(cm.group(1))
                current['ban_sao']   = int(cm.group(2))
            continue

        # ── Template file ─────────────────────────────────────────────────
        if _TEMPLATE_RE.match(line):
            if current:
                current['template_file'] = line.strip()
            continue

        # ── Continuation / sub-item (starts with '+') ─────────────────────
        if line.startswith('+ '):
            continue    # lưu ý kỹ thuật, không thêm vào tên

        # ── Document name line ─────────────────────────────────────────────
        # Có thể bắt đầu bằng "- " (format thường) hoặc là plain text (format khác)
        flush()
        if line.startswith('- '):
            name = line[2:].strip()
        else:
            name = line.strip()
        name = name.rstrip(';,').strip()[:250]
        current = {
            'name':          name,
            'template_file': None,
            'ban_chinh':     0,
            'ban_sao':       0,
            'section':       section,
        }

    flush()

    # ── Chuyển đổi sang format cuối ──────────────────────────────────────
    result = []
    for d in docs:
        name = d['name'].strip()
        if not name or len(name) < 4:
            continue

        # Bỏ item không có số lượng thực (pure instruction)
        if d['ban_chinh'] == 0 and d['ban_sao'] == 0:
            continue

        # Section 'present' → xuất trình bản chính, không cần nộp
        if d['section'] == 'present':
            is_required = False
            doc_type    = 'original'
            desc_prefix = 'Xuất trình bản gốc. '
        else:
            is_required = d['ban_chinh'] >= 1
            doc_type    = 'original' if d['ban_chinh'] >= 1 else 'copy'
            desc_prefix = ''

        # Mô tả số lượng
        parts = []
        if d['ban_chinh'] > 0:
            parts.append(f"Bản chính: {d['ban_chinh']}")
        if d['ban_sao'] > 0:
            parts.append(f"Bản sao: {d['ban_sao']}")
        description = desc_prefix + ', '.join(parts)

        result.append({
            'name':          name,
            'description':   description.strip(),
            'is_required':   is_required,
            'doc_type':      doc_type,
            'template_file': d['template_file'],
        })

    return result


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_procedures_needing_parse(cur):
    """
    Trả về các procedure có 0 clean records trong service_requirements.
    (clean = ID không khớp pattern ^\d+\.\d+-req-\d+$)
    """
    cur.execute("""
        SELECT p.id, p.name
        FROM procedures p
        WHERE NOT EXISTS (
            SELECT 1 FROM service_requirements sr
            WHERE sr.service_id = p.id
              AND sr.id !~ '^\\d+\\.\\d+-req-\\d+$'
        )
        ORDER BY p.id
    """)
    return cur.fetchall()


def get_dvc_data(cur, ma_thu_tuc: str) -> str | None:
    """Lấy thanh_phan_ho_so từ chitiet_dvc_tructuyen theo mã thủ tục."""
    cur.execute("""
        SELECT thanh_phan_ho_so
        FROM chitiet_dvc_tructuyen
        WHERE url_chi_tiet LIKE %s
          AND thanh_phan_ho_so IS NOT NULL
          AND thanh_phan_ho_so NOT IN ('', 'thanh_phan_ho_so')
        LIMIT 1
    """, (f'%ma_thu_tuc={ma_thu_tuc}%',))
    row = cur.fetchone()
    return row[0] if row else None


def insert_requirements(cur, service_id: str, docs: list[dict], dry_run: bool):
    """Insert parsed documents into service_requirements."""
    inserted = 0
    for i, doc in enumerate(docs):
        req_id = f'{service_id}-doc-{i:03d}'
        if dry_run:
            print(f'  [DRY] INSERT {req_id}: {doc["name"][:60]}')
            inserted += 1
            continue

        cur.execute("""
            INSERT INTO service_requirements
                (id, service_id, doc_name, doc_description,
                 is_required, doc_type, order_index, template_file)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                doc_name        = EXCLUDED.doc_name,
                doc_description = EXCLUDED.doc_description,
                is_required     = EXCLUDED.is_required,
                doc_type        = EXCLUDED.doc_type,
                order_index     = EXCLUDED.order_index,
                template_file   = EXCLUDED.template_file
        """, (
            req_id, service_id,
            doc['name'], doc['description'],
            doc['is_required'], doc['doc_type'],
            i,
            doc['template_file'] or None,
        ))
        inserted += 1
    return inserted


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print('=== DRY RUN MODE (không ghi vào DB) ===\n')

    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    procedures = get_procedures_needing_parse(cur)
    print(f'Procedures cần parse: {len(procedures)}')
    for pid, pname in procedures:
        print(f'  - {pid}: {pname[:60]}')
    print()

    total_inserted = 0

    for proc_id, proc_name in procedures:
        print(f'▶ {proc_id} — {proc_name[:70]}')

        raw_text = get_dvc_data(cur, proc_id)
        if not raw_text:
            print('  ⚠ Không tìm thấy dữ liệu trong chitiet_dvc_tructuyen → skip\n')
            continue

        docs = _parse(raw_text)
        if not docs:
            print('  ⚠ Parser không tìm thấy giấy tờ nào → skip\n')
            continue

        print(f'  Tìm thấy {len(docs)} giấy tờ:')
        for d in docs:
            req_marker = '✓' if d['is_required'] else '○'
            tag = 'xuất trình' if d['doc_type'] == 'original' and not d['is_required'] else d['doc_type']
            print(f'    {req_marker} [{tag}] {d["name"][:70]}')

        n = insert_requirements(cur, proc_id, docs, dry_run)
        total_inserted += n
        print(f'  → Inserted {n} records\n')

    if not dry_run:
        conn.commit()
        print(f'✅ Commit xong. Tổng: {total_inserted} records đã insert.')
    else:
        print(f'\n[DRY RUN] Sẽ insert tổng {total_inserted} records nếu chạy thật.')

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
