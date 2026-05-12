"""
Appointment helpers — PostgreSQL-backed với file fallback.
Interface giữ nguyên để không phải sửa routes.
"""
import os
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from logger import get_logger

log = get_logger('appointments')

# Giờ làm việc mặc định (configurable qua env)
_SLOT_CONFIG = os.getenv('APPOINTMENT_SLOTS', '08:00,09:00,10:00,11:00,14:00,15:00,16:00')
_DEFAULT_SLOTS: List[str] = [s.strip() for s in _SLOT_CONFIG.split(',') if s.strip()]
_MAX_PER_SLOT = int(os.getenv('APPOINTMENT_MAX_PER_SLOT', '5'))


# ── Validators ────────────────────────────────────────────────────────────────

def is_valid_time(t: str) -> bool:
    return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', t))


def is_valid_date(d: str) -> bool:
    try:
        datetime.strptime(d, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_db():
    try:
        from models.db import db
        from sqlalchemy import text
        return db, text
    except Exception:
        return None, None


def _row_to_dict(row) -> Dict[str, Any]:
    keys = ['id', 'userId', 'agencyId', 'serviceCode', 'date', 'time',
            'status', 'fullName', 'phone', 'info', 'queueNumber', 'createdAt', 'updatedAt']
    d = {}
    for i, k in enumerate(keys):
        v = row[i]
        d[k] = v.isoformat() if hasattr(v, 'isoformat') else v
    return d


# ── Public API ─────────────────────────────────────────────────────────────────

def read_appointments(agency_id: Optional[str] = None,
                      date_str: Optional[str] = None,
                      user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Đọc danh sách lịch hẹn từ PostgreSQL. Hỗ trợ filter."""
    db, text = _get_db()
    if db is None:
        return _file_read()

    try:
        conditions, params = [], {}
        if agency_id:
            conditions.append('agency_id = :agency_id')
            params['agency_id'] = agency_id
        if date_str:
            conditions.append('date = :date')
            params['date'] = date_str
        if user_id:
            conditions.append('user_id = :user_id')
            params['user_id'] = user_id

        where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
        rows = db.session.execute(text(f'''
            SELECT id, user_id, agency_id, service_code, date, time,
                   status, full_name, phone, info, queue_number, created_at, updated_at
            FROM public.appointments
            {where}
            ORDER BY date, time
        '''), params).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as e:
        log.warning(f'read_appointments DB failed: {e}')
        return _file_read()


def write_appointments(items: List[Dict[str, Any]]) -> None:
    """Kept for backward-compat — không dùng với PostgreSQL."""
    _file_write(items)


def create_appointment(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """Validate, kiểm tra slot, tạo lịch hẹn. Trả về (ok, item, error_msg)."""
    agency_id    = payload.get('agencyId', '')
    service_code = payload.get('serviceCode', '')
    date_str     = payload.get('date', '')
    time_str     = payload.get('time', '')

    errors: List[str] = []
    if not agency_id:    errors.append('Thiếu agencyId')
    if not service_code: errors.append('Thiếu serviceCode')
    if not date_str or not is_valid_date(date_str):  errors.append('Ngày không hợp lệ')
    if not time_str or not is_valid_time(time_str):  errors.append('Giờ không hợp lệ')
    if errors:
        return False, {}, ', '.join(errors)

    try:
        appt_dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
    except Exception as e:
        return False, {}, f'Lỗi thời gian: {e}'

    if appt_dt < datetime.now():
        return False, {}, 'Không thể đặt lịch trong quá khứ'

    db, text = _get_db()
    if db is None:
        return _file_create(payload)

    try:
        # Kiểm tra slot còn chỗ
        slot_count = db.session.execute(text('''
            SELECT COUNT(*) FROM public.appointments
            WHERE agency_id = :aid AND date = :date AND time = :time
              AND status NOT IN ('cancelled')
        '''), {'aid': agency_id, 'date': date_str, 'time': time_str}).scalar() or 0

        if slot_count >= _MAX_PER_SLOT:
            return False, {}, f'Thời điểm {time_str} ngày {date_str} đã đầy ({_MAX_PER_SLOT} lịch/slot)'

        appt_id      = str(uuid.uuid4())
        queue_number = int(slot_count) + 1

        row = db.session.execute(text('''
            INSERT INTO public.appointments
                (id, user_id, agency_id, service_code, date, time,
                 status, full_name, phone, info, queue_number)
            VALUES (:id, :uid, :aid, :svc, :date, :time,
                    :status, :fname, :phone, :info, :qnum)
            RETURNING id, user_id, agency_id, service_code, date, time,
                      status, full_name, phone, info, queue_number, created_at, updated_at
        '''), {
            'id':     appt_id,
            'uid':    payload.get('userId'),
            'aid':    agency_id,
            'svc':    service_code,
            'date':   date_str,
            'time':   time_str,
            'status': payload.get('status', 'pending'),
            'fname':  payload.get('fullName', ''),
            'phone':  payload.get('phone', ''),
            'info':   payload.get('info', ''),
            'qnum':   queue_number,
        }).fetchone()
        db.session.commit()
        return True, _row_to_dict(row), None

    except Exception as e:
        db.session.rollback()
        log.error(f'create_appointment DB error: {e}', exc_info=True)
        return False, {}, f'Lỗi hệ thống: {e}'


def suggest_slots(date_iso: str, agency_id: str = 'default') -> List[str]:
    """Trả về danh sách khung giờ còn trống (HH:MM:SS) cho ngày và cơ quan."""
    db, text = _get_db()
    available = []

    if db is not None:
        try:
            for slot in _DEFAULT_SLOTS:
                count = db.session.execute(text('''
                    SELECT COUNT(*) FROM public.appointments
                    WHERE agency_id = :aid AND date = :date AND time = :time
                      AND status NOT IN ('cancelled')
                '''), {'aid': agency_id, 'date': date_iso, 'time': slot}).scalar() or 0
                if count < _MAX_PER_SLOT:
                    available.append(slot + ':00')
            return available
        except Exception as e:
            log.warning(f'suggest_slots DB failed: {e}')

    # File fallback
    items = _file_read()
    for slot in _DEFAULT_SLOTS:
        count = sum(
            1 for a in items
            if a.get('date') == date_iso and a.get('time') == slot
            and a.get('agencyId') == agency_id
        )
        if count < _MAX_PER_SLOT:
            available.append(slot + ':00')
    return available


# ── File fallback (backward-compat) ──────────────────────────────────────────

import json
import os as _os
import threading

_LOCK = threading.Lock()
_FILE = _os.path.join(_os.path.dirname(__file__), '..', 'data', 'appointments.json')


def _file_read() -> List[Dict[str, Any]]:
    with _LOCK:
        try:
            if not _os.path.exists(_FILE):
                return []
            with open(_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []


def _file_write(items: List[Dict[str, Any]]) -> None:
    with _LOCK:
        _os.makedirs(_os.path.dirname(_FILE), exist_ok=True)
        with open(_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)


def _file_create(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    agency_id    = payload.get('agencyId', '')
    service_code = payload.get('serviceCode', '')
    date_str     = payload.get('date', '')
    time_str     = payload.get('time', '')

    with _LOCK:
        items = _file_read()
        slot_count = sum(
            1 for a in items
            if a.get('agencyId') == agency_id
            and a.get('date') == date_str
            and a.get('time') == time_str
        )
        if slot_count >= _MAX_PER_SLOT:
            return False, {}, f'Thời điểm {time_str} ngày {date_str} đã đầy'

        new_item: Dict[str, Any] = {
            'id':          f'apt-{int(time.time() * 1000)}',
            'userId':      payload.get('userId'),
            'agencyId':    agency_id,
            'serviceCode': service_code,
            'date':        date_str,
            'time':        time_str,
            'status':      payload.get('status', 'pending'),
            'fullName':    payload.get('fullName', ''),
            'phone':       payload.get('phone', ''),
            'info':        payload.get('info', ''),
            'queueNumber': slot_count + 1,
        }
        items.append(new_item)
        _file_write(items)

    return True, new_item, None
