"""
Admin Divisions Routes — danh mục hành chính VN (tỉnh/xã theo mô hình 2025).

Dữ liệu từ repo thanglequoc/vietnamese-provinces-database (34 tỉnh, 3.321 xã,
bỏ cấp huyện). Nạp bằng scripts/import_admin_divisions.* → bảng provinces, wards.

Endpoints:
  GET /api/admin-divisions/provinces                    Danh sách 34 tỉnh/thành
  GET /api/admin-divisions/wards?province_code=<code>   Xã/phường của 1 tỉnh
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import text

from models.db import db
from logger import get_logger

log = get_logger('admin_divisions_routes')

admin_divisions_bp = Blueprint('admin_divisions', __name__, url_prefix='/api/admin-divisions')


def _ok(data):
    return jsonify({'success': True, 'data': data})


def _err(msg, code=400):
    return jsonify({'success': False, 'error': msg}), code


@admin_divisions_bp.route('/provinces', methods=['GET'])
def list_provinces():
    """Danh sách tỉnh/thành, sắp theo tên."""
    try:
        rows = db.session.execute(text('''
            SELECT code, name, full_name
            FROM public.provinces
            ORDER BY name
        ''')).fetchall()
        return _ok([
            {'code': r.code, 'name': r.name, 'fullName': r.full_name}
            for r in rows
        ])
    except Exception as e:
        log.error(f'list_provinces: {e}', exc_info=True)
        return _err('Không tải được danh sách tỉnh (bảng provinces chưa được nạp?)', 500)


@admin_divisions_bp.route('/wards', methods=['GET'])
def list_wards():
    """Danh sách xã/phường theo province_code."""
    province_code = (request.args.get('province_code') or '').strip()
    if not province_code:
        return _err('Thiếu tham số province_code', 400)
    try:
        rows = db.session.execute(text('''
            SELECT code, name, full_name
            FROM public.wards
            WHERE province_code = :pc
            ORDER BY name
        '''), {'pc': province_code}).fetchall()
        return _ok([
            {'code': r.code, 'name': r.name, 'fullName': r.full_name}
            for r in rows
        ])
    except Exception as e:
        log.error(f'list_wards: {e}', exc_info=True)
        return _err('Không tải được danh sách xã/phường', 500)
