import re
import time
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request
from services.appointments import (
    read_appointments, write_appointments,
    is_valid_time, is_valid_date, create_appointment,
)

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')


@appointments_bp.route('', methods=['POST'])
def create_appointment_route():
    try:
        payload = request.get_json(silent=True) or {}
        agency_id = payload.get('agencyId')
        service_code = payload.get('serviceCode')
        date_str = payload.get('date')
        time_str = payload.get('time')

        errors = []
        if not agency_id:
            errors.append({'msg': 'Cơ quan là bắt buộc', 'param': 'agencyId'})
        if not service_code:
            errors.append({'msg': 'Dịch vụ là bắt buộc', 'param': 'serviceCode'})
        if not date_str or not is_valid_date(date_str):
            errors.append({'msg': 'Ngày không hợp lệ', 'param': 'date'})
        if not time_str or not is_valid_time(time_str):
            errors.append({'msg': 'Thời gian không hợp lệ (HH:mm)', 'param': 'time'})
        if errors:
            return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ', 'errors': errors}), 400

        try:
            appointment_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except Exception as parse_exc:
            return jsonify({'success': False, 'message': f'Dữ liệu thời gian không hợp lệ: {parse_exc}'}), 400

        if appointment_dt < datetime.now():
            return jsonify({'success': False, 'message': 'Không thể đặt lịch trong quá khứ'}), 400

        ok, new_item, err = create_appointment({
            'agencyId': agency_id,
            'serviceCode': service_code,
            'date': date_str,
            'time': time_str,
            'status': payload.get('status') or 'pending',
            'userId': payload.get('userId'),
        })
        if not ok:
            if 'đã đầy' in (err or ''):
                return jsonify({'success': False, 'message': err}), 409
            return jsonify({'success': False, 'message': err}), 400

        return jsonify({'success': True, 'message': 'Đặt lịch hẹn thành công', 'data': new_item}), 201

    except Exception as exc:
        print('[appointments][POST][ERROR]', exc)
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Lỗi khi tạo lịch hẹn: {exc}'}), 500


@appointments_bp.route('/by-date', methods=['GET'])
def get_appointments_by_date():
    try:
        agency_id = request.args.get('agencyId')
        date_str = request.args.get('date')
        if not agency_id or not date_str:
            return jsonify({'success': False, 'message': 'Thiếu thông tin cơ quan hoặc ngày'}), 400
        items = read_appointments()
        filtered = [a for a in items if a.get('agencyId') == agency_id and a.get('date') == date_str]
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công', 'data': {'appointments': filtered}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500


@appointments_bp.route('/all', methods=['GET'])
def get_all_appointments():
    try:
        items = read_appointments()
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công', 'data': {'appointments': items}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500


@appointments_bp.route('/upcoming', methods=['GET'])
def get_upcoming_appointments():
    try:
        items = read_appointments()
        now_naive = datetime.now()

        def _to_dt(a):
            try:
                return datetime.strptime(f"{a.get('date')} {a.get('time')}", '%Y-%m-%d %H:%M')
            except Exception:
                return None

        upcoming = [a for a in items if a.get('date') and a.get('time') and _to_dt(a) and _to_dt(a) >= now_naive]
        upcoming.sort(key=lambda a: _to_dt(a) or datetime.max)
        return jsonify({'success': True, 'message': 'Danh sách lịch hẹn sắp tới', 'data': {'appointments': upcoming}})
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Lỗi khi lấy lịch hẹn sắp tới: {exc}'}), 500
