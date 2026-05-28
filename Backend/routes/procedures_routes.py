"""
Procedures Routes — thông tin thủ tục hành chính từ bảng public.procedures.

GET /api/procedures                 Danh sách thủ tục (có filter, phân trang)
GET /api/procedures/<id>            Chi tiết một thủ tục + danh sách giấy tờ
GET /api/procedures/<id>/requirements  Giấy tờ yêu cầu của thủ tục
"""
import re
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from models.db import db
from models.service_requirement import ServiceRequirement
from logger import get_logger

_RAW_PROC_RE = re.compile(r'^\d+\.\d+$')   # ID dạng "1.000894", "2.002286"


def _deduplicate_procedures(proc_list: list[dict]) -> list[dict]:
    """
    Nếu trong danh sách vừa có procedure clean (ID dạng slug) vừa có raw
    (ID dạng số như 1.000894), ưu tiên giữ clean và bỏ raw trùng lặp.
    Tiêu chí trùng: cùng category + processing_days + fee, hoặc tên gần giống.
    """
    clean_ids = {p['id'] for p in proc_list if not _RAW_PROC_RE.match(p['id'])}
    if not clean_ids:
        return proc_list   # Toàn bộ là raw → giữ nguyên, không lọc

    result = []
    for p in proc_list:
        if not _RAW_PROC_RE.match(p['id']):
            result.append(p)   # Clean → luôn giữ
            continue
        # Raw: kiểm tra xem có clean nào cùng category + gần giống tên không
        raw_name_lower = p['name'].lower()
        # Bỏ tiền tố phổ biến để so sánh cốt lõi
        for prefix in ('thủ tục ', 'thu tuc '):
            raw_name_lower = raw_name_lower.replace(prefix, '')
        has_clean_equiv = any(
            raw_name_lower in c_p['name'].lower() or c_p['name'].lower() in raw_name_lower
            for c_p in proc_list
            if not _RAW_PROC_RE.match(c_p['id']) and c_p.get('category') == p.get('category')
        )
        if not has_clean_equiv:
            result.append(p)   # Không có clean tương đương → giữ lại
    return result

log = get_logger('procedures_routes')

procedures_bp = Blueprint('procedures', __name__, url_prefix='/api/procedures')

# Icon mapping cho frontend
_ICONS: dict = {
    'khai_sinh':            '👶',
    'ket_hon':              '❤️',
    'khai_tu':              '🕊️',
    'nhap_quoc_tich':       '🌏',
    'dang_ky_thuong_tru':   '🏠',
    'xac_nhan_cu_tru':      '📍',
    'cap_cccd':             '🪪',
    'doi_cccd':             '🪪',
    'cap_gplx_b1':          '🚗',
    'doi_gplx':             '🚗',
    'chuyen_nhuong_qsdd':   '📋',
    'cap_gcn_dat':          '📋',
    'cap_phep_xay_dung':    '🏗️',
    'dang_ky_ho_kinh_doanh':'🏪',
    'dang_ky_cong_ty_tnhh': '🏢',
    'cap_so_bhxh':          '🛡️',
    'huong_bhxh_mot_lan':   '💰',
    'cong_nhan_bang':       '🎓',
    'cap_giay_kham_suc_khoe':'🏥',
    'cap_phieu_lltp':       '📄',
    'cong_chung_hop_dong':  '✍️',
    'dang_ky_ma_so_thue':   '💳',
}

_CATEGORY_LABEL: dict = {
    'civil':        'Hộ tịch & Cư trú',
    'land':         'Đất đai',
    'justice':      'Tư pháp',
    'construction': 'Xây dựng',
    'business':     'Kinh doanh',
    'labor':        'Lao động & BHXH',
    'health':       'Y tế',
    'education':    'Giáo dục',
    'tax':          'Thuế',
    'environment':  'Môi trường',
}


def _row_to_dict(row) -> dict:
    fee = row.fee or 0
    # steps: chuyển text nhiều dòng → list (bỏ dòng rỗng)
    raw_steps = getattr(row, 'steps', None) or ''
    steps_list = [s.strip() for s in raw_steps.splitlines() if s.strip()] if raw_steps else []
    # conditions: tương tự
    raw_cond = getattr(row, 'conditions', None) or ''
    cond_list = [c.strip() for c in raw_cond.splitlines() if c.strip()] if raw_cond else []
    return {
        'id':               row.id,
        'name':             row.name,
        'code':             row.code or '',
        'category':         row.category or '',
        'categoryLabel':    _CATEGORY_LABEL.get(row.category, row.category or ''),
        'icon':             _ICONS.get(row.id, '📄'),
        'fee':              fee,
        'feeFormatted':     'Miễn phí' if fee == 0 else f'{fee:,} VNĐ'.replace(',', '.'),
        'feeNote':          row.fee_note or '',
        'feeColor':         fee == 0,
        'processingDays':   row.processing_days or 0,
        'processingNote':   row.processing_note or '',
        'timeFormatted':    _fmt_time(row.processing_days or 0, row.processing_note or ''),
        'legalBasis':       row.legal_basis or [],
        'implementingLevel':row.implementing_level or 'ward',
        'agency':           row.agency or '',
        'isOnline':         bool(row.is_online),
        'isActive':         bool(row.is_active),
        'steps':            steps_list,
        'conditions':       cond_list,
    }


def _fmt_time(days: int, note: str) -> str:
    if note:
        import re
        m = re.search(r'(\d+)\s*ngày', note)
        if m:
            d = int(m.group(1))
            return f'{d} ngày làm việc'
    if days <= 0:
        return 'Trong ngày'
    if days == 1:
        return '1 ngày làm việc'
    return f'{days} ngày làm việc'


def _has_procedures_table() -> bool:
    try:
        db.session.execute(text("SELECT 1 FROM public.procedures LIMIT 1"))
        return True
    except Exception:
        db.session.rollback()
        return False


# ── Fallback data nếu bảng procedures chưa được seed ─────────────────────────
_FALLBACK = [
    {'id': 'khai_sinh',          'name': 'Đăng ký khai sinh',           'category': 'civil',        'fee': 0,      'processingDays': 3,  'implementingLevel': 'ward'},
    {'id': 'ket_hon',            'name': 'Đăng ký kết hôn',             'category': 'civil',        'fee': 0,      'processingDays': 5,  'implementingLevel': 'ward'},
    {'id': 'khai_tu',            'name': 'Đăng ký khai tử',             'category': 'civil',        'fee': 0,      'processingDays': 3,  'implementingLevel': 'ward'},
    {'id': 'dang_ky_thuong_tru', 'name': 'Đăng ký thường trú',         'category': 'civil',        'fee': 0,      'processingDays': 7,  'implementingLevel': 'ward'},
    {'id': 'xac_nhan_cu_tru',    'name': 'Xác nhận cư trú',             'category': 'civil',        'fee': 0,      'processingDays': 1,  'implementingLevel': 'ward'},
    {'id': 'cap_cccd',           'name': 'Cấp CCCD (lần đầu)',          'category': 'civil',        'fee': 0,      'processingDays': 15, 'implementingLevel': 'district'},
    {'id': 'doi_cccd',           'name': 'Cấp đổi CCCD',                'category': 'civil',        'fee': 0,      'processingDays': 15, 'implementingLevel': 'district'},
    {'id': 'cap_gplx_b1',        'name': 'Cấp GPLX hạng B1',           'category': 'civil',        'fee': 135000, 'processingDays': 15, 'implementingLevel': 'province'},
    {'id': 'doi_gplx',           'name': 'Đổi GPLX hết hạn',           'category': 'civil',        'fee': 135000, 'processingDays': 10, 'implementingLevel': 'province'},
    {'id': 'chuyen_nhuong_qsdd', 'name': 'Chuyển nhượng QSDĐ',         'category': 'land',         'fee': 0,      'processingDays': 15, 'implementingLevel': 'district'},
    {'id': 'cap_gcn_dat',        'name': 'Cấp sổ đỏ lần đầu',          'category': 'land',         'fee': 100000, 'processingDays': 30, 'implementingLevel': 'district'},
    {'id': 'cap_phep_xay_dung',  'name': 'Cấp phép xây dựng',          'category': 'construction', 'fee': 0,      'processingDays': 15, 'implementingLevel': 'district'},
    {'id': 'dang_ky_ho_kinh_doanh','name':'Đăng ký hộ kinh doanh',     'category': 'business',     'fee': 100000, 'processingDays': 3,  'implementingLevel': 'district'},
    {'id': 'dang_ky_cong_ty_tnhh','name': 'Đăng ký Công ty TNHH',     'category': 'business',     'fee': 50000,  'processingDays': 3,  'implementingLevel': 'province'},
    {'id': 'cap_so_bhxh',        'name': 'Cấp sổ BHXH',                'category': 'labor',        'fee': 0,      'processingDays': 10, 'implementingLevel': 'district'},
    {'id': 'huong_bhxh_mot_lan', 'name': 'Hưởng BHXH một lần',        'category': 'labor',        'fee': 0,      'processingDays': 10, 'implementingLevel': 'district'},
    {'id': 'cap_giay_kham_suc_khoe','name':'Cấp GCN sức khỏe',        'category': 'health',       'fee': 80000,  'processingDays': 1,  'implementingLevel': 'province'},
    {'id': 'cap_phieu_lltp',     'name': 'Cấp phiếu lý lịch tư pháp', 'category': 'justice',      'fee': 200000, 'processingDays': 10, 'implementingLevel': 'province'},
    {'id': 'cong_chung_hop_dong','name': 'Công chứng hợp đồng',        'category': 'justice',      'fee': 0,      'processingDays': 2,  'implementingLevel': 'district'},
    {'id': 'dang_ky_ma_so_thue', 'name': 'Đăng ký mã số thuế cá nhân','category': 'tax',          'fee': 0,      'processingDays': 5,  'implementingLevel': 'district'},
    {'id': 'cong_nhan_bang',     'name': 'Công nhận văn bằng nước ngoài','category': 'education',  'fee': 600000, 'processingDays': 30, 'implementingLevel': 'province'},
]


def _fallback_list(q: str = '', category: str = '', level: str = '') -> list:
    result = _FALLBACK
    if q:
        result = [p for p in result if q.lower() in p['name'].lower()]
    if category:
        result = [p for p in result if p['category'] == category]
    if level:
        result = [p for p in result if p['implementingLevel'] == level]
    return [{
        **p,
        'categoryLabel':    _CATEGORY_LABEL.get(p['category'], p['category']),
        'icon':             _ICONS.get(p['id'], '📄'),
        'feeFormatted':     'Miễn phí' if p['fee'] == 0 else f"{p['fee']:,} VNĐ".replace(',', '.'),
        'feeColor':         p['fee'] == 0,
        'timeFormatted':    _fmt_time(p['processingDays'], ''),
        'processingNote':   '',
        'feeNote':          '',
        'legalBasis':       [],
        'agency':           '',
        'isOnline':         True,
        'isActive':         True,
        'code':             '',
    } for p in result]


# ── Routes ────────────────────────────────────────────────────────────────────

@procedures_bp.route('', methods=['GET'])
def list_procedures():
    """Danh sách thủ tục hành chính với filter và phân trang."""
    try:
        q        = (request.args.get('q') or '').strip()
        category = (request.args.get('category') or '').strip()
        level    = (request.args.get('level') or '').strip()
        page     = max(int(request.args.get('page', 1)), 1)
        limit    = min(int(request.args.get('limit', 50)), 100)

        if not _has_procedures_table():
            result = _fallback_list(q, category, level)
            total  = len(result)
            paged  = result[(page-1)*limit: page*limit]
            return jsonify({'success': True, 'data': paged,
                            'total': total, 'source': 'fallback',
                            'pagination': {'page': page, 'limit': limit, 'total': total}})

        conditions, params = ['is_active = TRUE'], {}
        if q:
            conditions.append('(LOWER(name) LIKE :q OR LOWER(agency) LIKE :q OR code LIKE :q)')
            params['q'] = f'%{q.lower()}%'
        if category:
            conditions.append('category = :cat')
            params['cat'] = category
        if level:
            conditions.append('implementing_level = :level')
            params['level'] = level

        where = 'WHERE ' + ' AND '.join(conditions)

        total = db.session.execute(
            text(f'SELECT COUNT(*) FROM public.procedures {where}'), params
        ).scalar() or 0

        # Lấy thêm để bù sau khi deduplicate (raw có thể bị loại)
        fetch_limit = limit * 3
        rows = db.session.execute(text(f'''
            SELECT id, name, code, category, fee, fee_note, processing_days,
                   processing_note, legal_basis, implementing_level, agency,
                   is_online, is_active, steps, conditions
            FROM public.procedures {where}
            ORDER BY
                CASE WHEN id ~ '^\d+\.\d+$' THEN 1 ELSE 0 END,  -- clean trước
                category, processing_days, name
            LIMIT :limit OFFSET :offset
        '''), {**params, 'limit': fetch_limit, 'offset': (page-1)*limit}).fetchall()

        all_procs   = [_row_to_dict(r) for r in rows]
        deduped     = _deduplicate_procedures(all_procs)
        paged       = deduped[:limit]

        return jsonify({
            'success': True,
            'data': paged,
            'total': len(deduped),
            'source': 'database',
            'pagination': {'page': page, 'limit': limit, 'total': len(deduped)},
        })

    except Exception as e:
        log.error(f'list_procedures: {e}', exc_info=True)
        # Fallback nếu DB lỗi
        try:
            result = _fallback_list()
            return jsonify({'success': True, 'data': result, 'total': len(result),
                            'source': 'fallback', 'pagination': {'page': 1, 'limit': 50, 'total': len(result)}})
        except Exception:
            return jsonify({'success': False, 'message': str(e)}), 500


@procedures_bp.route('/<proc_id>', methods=['GET'])
def get_procedure(proc_id: str):
    """Chi tiết một thủ tục + danh sách giấy tờ yêu cầu."""
    try:
        proc = None
        if _has_procedures_table():
            row = db.session.execute(
                text('SELECT * FROM public.procedures WHERE id = :id AND is_active = TRUE'),
                {'id': proc_id}
            ).fetchone()
            if row:
                proc = _row_to_dict(row)

        if not proc:
            # Fallback về list tĩnh
            matches = [p for p in _fallback_list() if p['id'] == proc_id]
            if not matches:
                return jsonify({'success': False, 'message': 'Không tìm thấy thủ tục'}), 404
            proc = matches[0]

        # Lấy danh sách giấy tờ
        requirements = ServiceRequirement.find_by_service_id(proc_id)
        proc['requirements'] = requirements
        proc['requirementCount'] = len(requirements)
        proc['requiredCount']    = sum(1 for r in requirements if r.get('isRequired'))

        return jsonify({'success': True, 'data': proc})

    except Exception as e:
        log.error(f'get_procedure: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@procedures_bp.route('/<proc_id>/requirements', methods=['GET'])
def get_requirements(proc_id: str):
    """Chỉ trả giấy tờ yêu cầu — dùng ở bước 2 form nộp hồ sơ."""
    try:
        requirements = ServiceRequirement.find_by_service_id(proc_id)
        return jsonify({
            'success':      True,
            'serviceId':    proc_id,
            'requirements': requirements,
            'total':        len(requirements),
        })
    except Exception as e:
        log.error(f'get_requirements: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
