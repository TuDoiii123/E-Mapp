import re
import time
from datetime import datetime
from flask import Blueprint, jsonify, request
from services.appointments import (
    read_appointments, write_appointments,
    is_valid_time, is_valid_date, create_appointment,
    update_appointment_status,
)
from logger import get_logger

log = get_logger('appointments_routes')

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')


@appointments_bp.route('', methods=['POST'])
def create_appointment_route():
    if not getattr(request, 'user_id', None):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
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

        # userId chỉ từ JWT — không bao giờ lấy từ request body
        user_id = getattr(request, 'user_id', None)

        ok, new_item, err = create_appointment({
            'agencyId':    agency_id,
            'serviceCode': service_code,
            'date':        date_str,
            'time':        time_str,
            'status':      payload.get('status') or 'pending',
            'userId':      user_id,
            'fullName':    payload.get('fullName', ''),
            'phone':       payload.get('phone', ''),
            'info':        payload.get('info', ''),
        })
        if not ok:
            if 'đã đầy' in (err or ''):
                return jsonify({'success': False, 'message': err}), 409
            return jsonify({'success': False, 'message': err}), 400

        try:
            from services.notification_service import emit
            _uid = getattr(request, 'user_id', None)
            _appt_id = new_item.get('id') if new_item else None
            if _uid:
                emit(_uid, 'appointment', 'Đặt lịch hẹn thành công',
                     f'Lịch hẹn mã {_appt_id} đã được tạo.',
                     link='appointments', ref_id=_appt_id, priority='medium')
        except Exception as _e:
            log.debug(f'[notif] hook tạo lịch hẹn bỏ qua: {_e}')

        return jsonify({'success': True, 'message': 'Đặt lịch hẹn thành công', 'data': new_item}), 201

    except Exception as exc:
        log.error(f'create_appointment error: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi khi tạo lịch hẹn: {exc}'}), 500


@appointments_bp.route('/by-date', methods=['GET'])
def get_appointments_by_date():
    try:
        agency_id = request.args.get('agencyId')
        date_str  = request.args.get('date')
        if not agency_id or not date_str:
            return jsonify({'success': False, 'message': 'Thiếu thông tin cơ quan hoặc ngày'}), 400
        items = read_appointments(agency_id=agency_id, date_str=date_str)
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công',
                        'data': {'appointments': items}})
    except Exception as exc:
        log.error(f'appointments_routes error: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500


@appointments_bp.route('/all', methods=['GET'])
def get_all_appointments():
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    try:
        items = read_appointments()
        return jsonify({'success': True, 'message': 'Lấy danh sách lịch hẹn thành công',
                        'data': {'appointments': items}})
    except Exception as exc:
        log.error(f'appointments_routes error: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi khi lấy danh sách lịch hẹn: {exc}'}), 500


@appointments_bp.route('/<appt_id>/status', methods=['PATCH'])
def update_appointment_status_route(appt_id: str):
    """PATCH /api/appointments/:id/status  — Admin cập nhật trạng thái lịch hẹn."""
    if getattr(request, 'role', None) != 'admin':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    try:
        payload    = request.get_json(silent=True) or {}
        new_status = payload.get('status', '').strip()
        if not new_status:
            return jsonify({'success': False, 'message': 'Thiếu trường status'}), 400

        ok, err = update_appointment_status(appt_id, new_status)
        if not ok:
            return jsonify({'success': False, 'message': err}), 400

        return jsonify({
            'success': True,
            'message': f'Đã cập nhật trạng thái lịch hẹn thành "{new_status}"',
            'data':    {'id': appt_id, 'status': new_status},
        })
    except Exception as exc:
        log.error(f'update_appointment_status_route error: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi hệ thống: {exc}'}), 500


@appointments_bp.route('/upcoming', methods=['GET'])
def get_upcoming_appointments():
    if not getattr(request, 'user_id', None):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        user_id   = request.user_id
        now_naive = datetime.now()
        today     = now_naive.strftime('%Y-%m-%d')
        items     = read_appointments(user_id=user_id)
        upcoming  = []
        for a in items:
            if not a.get('date') or not a.get('time'):
                continue
            try:
                dt = datetime.strptime(f"{a['date']} {a['time']}", '%Y-%m-%d %H:%M')
                if dt >= now_naive:
                    upcoming.append(a)
            except Exception:
                pass
        upcoming.sort(key=lambda a: (a.get('date', ''), a.get('time', '')))
        return jsonify({'success': True, 'message': 'Danh sách lịch hẹn sắp tới',
                        'data': {'appointments': upcoming}})
    except Exception as exc:
        log.error(f'appointments_routes error: {exc}', exc_info=True)
        return jsonify({'success': False, 'message': f'Lỗi khi lấy lịch hẹn sắp tới: {exc}'}), 500
