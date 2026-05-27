"""
Audit: cross-reference giữa file Word mẫu và service_requirements trong DB.

Chạy: python scripts/audit_templates.py
"""
import os, sys, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'templates')

# ── 1. Lấy danh sách file Word ───────────────────────────────────────────────
template_files = sorted(
    f for f in os.listdir(TEMPLATES_DIR)
    if f.endswith(('.doc', '.docx')) and f != 'README.md'
)

# ── 2. Import dữ liệu gốc từ seed_procedures ────────────────────────────────
from scripts.seed_procedures import PROCEDURES
from models.service_requirement import _DEFAULTS

# Gom tất cả requirement (doc_name) từ DB data
db_docs = {}  # doc_name → [procedure_id, ...]
for proc_id, proc in PROCEDURES.items():
    for req in proc['requirements']:
        doc_name = req[0]
        db_docs.setdefault(doc_name, []).append(proc_id)

# Gom defaults
for key, reqs in _DEFAULTS.items():
    for req in reqs:
        doc_name = req[0]
        db_docs.setdefault(doc_name, []).append(f'_default:{key}')

# ── 3. Mapping thủ công: template_file → keyword → DB doc_name ──────────────
# keyword xuất hiện trong tên file → phần tên giấy tờ trong DB
KEYWORD_MAP = {
    'khai-sinh':              ['khai sinh', 'birth'],
    'ket-hon':                ['kết hôn', 'ket hon'],
    'khai-tu':                ['khai tử', 'khai tu'],
    'lai-khai-sinh':          ['đăng ký lại khai sinh'],
    'nhan-cha-me-con':        ['nhận cha', 'cha, mẹ, con'],
    'thay-doi-cai-chinh':     ['thay đổi, cải chính'],
    'trich-luc-ho-tich':      ['trích lục hộ tịch', 'bản sao trích lục'],
    'giam-ho':                ['giám hộ'],
    'CCCD':                   ['căn cước', 'cccd', 'CC01'],
    'CMND':                   ['chứng minh nhân dân', 'cmnd'],
    'cu-tru':                 ['cư trú', 'hộ khẩu', 'CT01'],
    'thuong-tru':             ['thường trú'],
    'xe-co-gioi':             ['đăng ký xe', 'khai đăng ký xe'],
    'tinh-trang-hon-nhan':    ['tình trạng hôn nhân'],
    'ly-hon':                 ['ly hôn', 'ly hon'],
    'ly-lich-tu-phap-so1':    ['lý lịch tư pháp số 1', 'phiếu lltp'],
    'ly-lich-tu-phap-so2':    ['lý lịch tư pháp số 2'],
    'ho-chieu':               ['hộ chiếu', 'ho chieu'],
    'hai-quan':               ['hải quan'],
    'so-do':                  ['giấy chứng nhận quyền sử dụng đất', 'sổ đỏ', 'gcnqsd'],
    'cap-doi-gcnqsdd':        ['cấp đổi giấy chứng nhận', 'cap doi'],
    'le-phi-truoc-ba':        ['lệ phí trước bạ', 'truoc ba'],
    'cap-phep-xay-dung':      ['giấy phép xây dựng', 'xây dựng'],
    'bien-dong-dat-dai':      ['biến động đất đai', 'mẫu 09'],
    'tach-thua':              ['tách thửa', 'hợp thửa'],
    'giao-dat-cho-thue':      ['giao đất', 'cho thuê đất', 'chuyển mục đích'],
    'thue-thu-nhap-ca-nhan':  ['thuế thu nhập cá nhân', 'tncn'],
    'thue-thu-nhap-doanh-nghiep': ['thuế thu nhập doanh nghiệp', 'tndn'],
    'thue-mon-bai':           ['môn bài', 'mon bai'],
    'hoan-thue':              ['hoàn trả', 'hoàn thuế'],
    'uy-quyen':               ['ủy quyền', 'uy quyen'],
    'suc-khoe':               ['sức khỏe', 'chứng nhận sức khỏe'],
    'kham-suc-khoe-lai-xe':   ['khám sức khỏe lái xe', 'sức khỏe lái xe'],
    'xet-nghiem':             ['xét nghiệm', 'kiểm nghiệm'],
    '05A-HSB':                ['tai nạn lao động', 'tnlđ', '05A'],
    '05-HSB':                 ['tai nạn lao động', 'bệnh nghề nghiệp', '05-HSB'],
    'bhxh-bhyt':              ['bhxh', 'bhyt', 'tk1-ts', 'tham gia bảo hiểm'],
    'cap-the-bao-hiem-y-te':  ['thẻ bhyt', 'thẻ bảo hiểm y tế'],
    'bao-tro-xa-hoi':         ['bảo trợ xã hội', 'trợ giúp xã hội'],
    'tro-cap-that-nghiep':    ['trợ cấp thất nghiệp'],
    'tro-cap-xa-hoi':         ['trợ cấp xã hội'],
    'hop-dong-lao-dong':      ['hợp đồng lao động', 'ký kết hợp đồng'],
    'hoc-bong':               ['học bổng'],
    'xin-viec':               ['xin việc', 'dự tuyển'],
    'ho-tro-nha-o':           ['nhà ở', 'hỗ trợ nhà'],
    'nguoi-co-cong':          ['người có công', 'thân nhân'],
    'chuyen-truong':          ['chuyển trường'],
    'thoi-hoc':               ['thôi học'],
    'tot-nghiep':             ['tốt nghiệp'],
    'phuc-khao':              ['phúc khảo'],
    'mien-giam-hoc-phi':      ['miễn giảm học phí'],
    'dang-ky-doanh-nghiep':   ['đăng ký doanh nghiệp', 'phụ lục i-1'],
    'phu-luc-i2':             ['phụ lục i-2'],
    'thay-doi-dkdn':          ['thay đổi nội dung đăng ký'],
    'giai-the-doanh-nghiep':  ['giải thể doanh nghiệp'],
    'ho-kinh-doanh':          ['hộ kinh doanh'],
    'dieu-chinh-dau-tu':      ['điều chỉnh dự án đầu tư'],
    'vi-pham-hanh-chinh':     ['vi phạm hành chính', 'biên bản vi phạm'],
    'khieu-nai':              ['khiếu nại'],
    'giay-phep-moi-truong':   ['giấy phép môi trường', 'môi trường'],
}

def find_matching_docs(filename):
    """Tìm doc_name trong DB khớp với template filename."""
    fname_lower = filename.lower()
    matched = []
    for keyword, doc_keywords in KEYWORD_MAP.items():
        if keyword.lower() in fname_lower:
            for doc_name in db_docs:
                doc_lower = doc_name.lower()
                if any(kw in doc_lower for kw in doc_keywords):
                    matched.append(doc_name)
    return list(dict.fromkeys(matched))  # deduplicate

# ── 4. Chạy audit ─────────────────────────────────────────────────────────────
print('\n' + '='*75)
print('  AUDIT: File Word mẫu ↔ Service Requirements trong DB')
print('='*75)

matched_templates   = []
orphan_templates    = []  # có file Word, không có DB doc
db_docs_no_template = {}  # có DB doc, không có file Word

for fname in template_files:
    matches = find_matching_docs(fname)
    if matches:
        matched_templates.append((fname, matches))
    else:
        orphan_templates.append(fname)

# Tìm DB docs không có template
all_matched_docnames = set()
for _, docs in matched_templates:
    all_matched_docnames.update(docs)

for doc_name, proc_ids in sorted(db_docs.items()):
    # Bỏ qua các loại không cần file (CCCD gốc, ảnh, lệ phí tiền mặt, biên lai...)
    skip_keywords = ['ảnh', 'lệ phí', 'biên lai', 'tài khoản ngân hàng',
                     'bản vẽ', 'hồ sơ thiết kế', 'sổ bảo hiểm', 'giấy phép lái xe cũ',
                     'bảng điểm', 'bản sao văn bằng', 'điều lệ công ty',
                     'văn bản đồng ý', 'chứng từ', 'trích lục bản đồ']
    if any(kw in doc_name.lower() for kw in skip_keywords):
        continue
    if doc_name not in all_matched_docnames:
        db_docs_no_template[doc_name] = proc_ids

# ── 5. In kết quả ─────────────────────────────────────────────────────────────
print(f'\n✅ CÓ KHỚP ({len(matched_templates)} / {len(template_files)} file):')
print('-'*75)
for fname, docs in matched_templates:
    procs = set()
    for d in docs:
        procs.update(db_docs.get(d, []))
    proc_list = ', '.join(sorted(procs)[:4])
    print(f'  {fname}')
    print(f'    → {docs[0][:65]}')
    print(f'    thuộc: {proc_list}')
    print()

print(f'\n⚠️  ORPHAN — có file Word nhưng CHƯA có trong DB ({len(orphan_templates)}):')
print('-'*75)
for fname in orphan_templates:
    print(f'  ✗ {fname}')

print(f'\n❌ THIẾU TEMPLATE — có trong DB nhưng CHƯA có file Word ({len(db_docs_no_template)}):')
print('-'*75)
for doc_name, proc_ids in sorted(db_docs_no_template.items()):
    short_procs = [p for p in proc_ids if not p.startswith('_default')][:3]
    print(f'  ✗ {doc_name}')
    if short_procs:
        print(f'    thuộc thủ tục: {", ".join(short_procs)}')

print('\n' + '='*75)
print(f'TỔNG KẾT:')
print(f'  File Word:        {len(template_files):3d}')
print(f'  Đã khớp DB:      {len(matched_templates):3d}')
print(f'  Orphan (chưa DB): {len(orphan_templates):3d}')
print(f'  DB thiếu template:{len(db_docs_no_template):3d}')
print('='*75 + '\n')
