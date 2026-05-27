"""
Audit đơn giản — KHÔNG cần DB/Flask.
Parse seed_procedures.py + service_requirement.py trực tiếp.
Chạy: python scripts/audit_templates_simple.py
"""
import os, re, sys

BASE = os.path.join(os.path.dirname(__file__), '..')
TEMPLATES_DIR = os.path.join(BASE, 'data', 'templates')

# ── 1. Đọc file Word ──────────────────────────────────────────────────────────
template_files = sorted(
    f for f in os.listdir(TEMPLATES_DIR)
    if f.endswith(('.doc', '.docx'))
)
print(f"Tìm thấy {len(template_files)} file Word mẫu.\n")

# ── 2. Parse seed_procedures.py ────────────────────────────────────────────────
seed_path = os.path.join(BASE, 'scripts', 'seed_procedures.py')
with open(seed_path, encoding='utf-8') as f:
    src = f.read()

# Tìm các procedure block
# Mỗi block: 'proc_id': { ... 'requirements': [ ... ] ... }
proc_blocks = re.findall(
    r"'(\w+)':\s*\{[^}]*?'requirements':\s*\[(.*?)\],",
    src, re.DOTALL
)

# Pattern để parse requirement tuple — hỗ trợ cả 5 và 6 phần tử:
# ('doc_name', 'desc', True/False, 'dtype', N)
# ('doc_name', 'desc', True/False, 'dtype', N, 'template_file')
req5_pattern = re.compile(
    r"\(\s*'([^']+)',\s*'[^']*',\s*(?:True|False),\s*'[^']*',\s*\d+\s*\)"
)
req6_pattern = re.compile(
    r"\(\s*'([^']+)',\s*'[^']*',\s*(?:True|False),\s*'[^']*',\s*\d+,\s*'([^']+)'\s*\)"
)

proc_req_map   = {}   # proc_id → [doc_names]
proc_tmpl_map  = {}   # proc_id → {template_file: doc_name}
all_req_names  = set()
referenced_tmpls = set()  # template_file values actually referenced

for proc_id, reqs_str in proc_blocks:
    doc_names = []
    for m in req6_pattern.finditer(reqs_str):
        doc_name, tmpl = m.group(1), m.group(2)
        doc_names.append(doc_name)
        all_req_names.add(doc_name)
        referenced_tmpls.add(tmpl)
        proc_tmpl_map.setdefault(proc_id, {})[tmpl] = doc_name
    # Collect names from 5-elem tuples too (may overlap, that's OK)
    for m in req5_pattern.finditer(reqs_str):
        doc_name = m.group(1)
        if doc_name not in doc_names:
            doc_names.append(doc_name)
            all_req_names.add(doc_name)
    proc_req_map[proc_id] = doc_names

# ── Parse _DEFAULTS từ service_requirement.py ────────────────────────────────
svc_req_path = os.path.join(BASE, 'models', 'service_requirement.py')
with open(svc_req_path, encoding='utf-8') as f:
    svc_src = f.read()
for m in req5_pattern.finditer(svc_src):
    all_req_names.add(m.group(1))
for m in req6_pattern.finditer(svc_src):
    all_req_names.add(m.group(1))
    referenced_tmpls.add(m.group(2))

print(f"Tìm thấy {len(proc_req_map)} thủ tục, tổng {len(all_req_names)} giấy tờ duy nhất.")
print(f"Tổng {len(referenced_tmpls)} file template được tham chiếu trực tiếp.\n")

# ── 3. Phân loại file Word ─────────────────────────────────────────────────────
# Cách 1: Khớp trực tiếp theo template_file (accurate)
directly_referenced  = sorted(f for f in template_files if f in referenced_tmpls)
not_referenced       = sorted(f for f in template_files if f not in referenced_tmpls)

# ── 4. Tìm giấy tờ trong DB chưa có template_file ────────────────────────────
# Các giấy tờ KHÔNG cần file (ảnh, lệ phí, chứng từ vật chất…)
skip_kws = ['ảnh ', 'lệ phí', 'biên lai', 'tài khoản ngân hàng',
            'bản vẽ', 'hồ sơ thiết kế', 'sổ bảo hiểm xã hội',
            'giấy phép lái xe cũ', 'bảng điểm', 'bản sao văn bằng',
            'điều lệ công ty', 'văn bản đồng ý', 'chứng từ',
            'trích lục bản đồ', 'giấy báo tử',
            'giấy chứng sinh', 'giấy tờ về quốc tịch', 'bản sao hộ chiếu',
            'cccd/', 'cccd cũ', 'cmnd cũ', 'sổ hộ khẩu',
            'giấy tờ pháp lý', 'giấy tờ chứng minh', 'một trong các',
            'đăng ký kết hôn của cha', 'giấy xác nhận của cha, mẹ',
            'giấy khai sinh (nếu', 'hợp đồng chuyển nhượng', 'văn bản ủy quyền',
            'giấy chứng nhận đào tạo', 'giấy chứng nhận qsd',
            'danh sách thành viên', 'giấy tờ chứng minh',
            'mẫu sản phẩm', 'tài liệu kỹ thuật',
            'biên bản điều tra', 'giấy ra viện', 'sổ bhxh',
            'bảng điểm', 'học bạ', 'thẻ sinh viên',
            'sơ đồ thửa đất', 'hóa đơn mua bán', 'chứng từ nộp',
            'hồ sơ thiết kế', 'báo cáo đánh giá', 'kế hoạch quản lý',
            'văn bản phê duyệt', 'hồ sơ dự án', 'hồ sơ chứng minh',
            'hồ sơ xác nhận', 'giấy chứng nhận đkdn', 'quyết định',
            'giấy chứng nhận đăng ký đầu tư', 'tài liệu giải trình',
            'tài liệu, chứng cứ', 'sơ yếu lý lịch', 'văn bằng, chứng chỉ',
            'giấy tờ liên quan', 'giấy khám sức khoẻ (nếu',
           ]

# Gom tất cả doc_name có template_file được gán
has_template_names = set()
for reqs_str in [match[1] for match in proc_blocks]:
    for m in req6_pattern.finditer(reqs_str):
        has_template_names.add(m.group(1))

missing_template = []
for req in sorted(all_req_names):
    req_l = req.lower()
    if any(kw in req_l for kw in skip_kws):
        continue
    if req in has_template_names:
        continue
    procs = [pid for pid, docs in proc_req_map.items() if req in docs]
    missing_template.append((req, procs))

# ── 5. In kết quả ─────────────────────────────────────────────────────────────
W = 75
print('='*W)
print('  AUDIT: File Word ↔ Giấy tờ yêu cầu trong DB')
print('='*W)

print(f'\n✅ FILE CÓ TEMPLATE_FILE TRONG DB ({len(directly_referenced)}/{len(template_files)}):')
print('-'*W)
for fname in directly_referenced:
    # Tìm proc(s) tham chiếu file này
    procs = [pid for pid, tmap in proc_tmpl_map.items() if fname in tmap]
    doc = next((tmap[fname] for _, tmap in proc_tmpl_map.items() if fname in tmap), '')
    print(f'  ✓ {fname}')
    print(f'      Giấy tờ : "{doc[:65]}"')
    print(f'      Thủ tục : {", ".join(procs[:4]) if procs else "(default)"}')

print(f'\n⚠️  FILE CHƯA ĐƯỢC THAM CHIẾU TRONG DB ({len(not_referenced)}):')
print('-'*W)
for f in not_referenced:
    print(f'  ○ {f}')

print(f'\n❌ GIẤY TỜ TRONG DB THIẾU TEMPLATE ({len(missing_template)}):')
print('-'*W)
for req, procs in missing_template:
    pstr = ', '.join(procs[:3]) if procs else '(default)'
    print(f'  ✗ "{req}"')
    print(f'      Thủ tục: {pstr}')

print('\n' + '='*W)
print(f'  TỔNG KẾT:')
print(f'    File Word tổng:                {len(template_files):3d}')
print(f'    File có template_file trong DB: {len(directly_referenced):3d}')
print(f'    File chưa được tham chiếu:      {len(not_referenced):3d}')
print(f'    Giấy tờ DB thiếu template:      {len(missing_template):3d}')
print('='*W)
