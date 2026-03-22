"""
Appointment helpers shared by appointments_routes and voice_routes.
Thread-safe via a single module-level lock.
"""
import json
import os
import re
import time
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

_LOCK = threading.Lock()
_APPOINTMENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'appointments.json')


# ── internal (call only while _LOCK is held) ──────────────────────────────────

def _read_unsafe() -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(_APPOINTMENTS_FILE):
            os.makedirs(os.path.dirname(_APPOINTMENTS_FILE), exist_ok=True)
            with open(_APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        with open(_APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _write_unsafe(items: List[Dict[str, Any]]) -> None:
    with open(_APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# ── public API ─────────────────────────────────────────────────────────────────

def read_appointments() -> List[Dict[str, Any]]:
    with _LOCK:
        return _read_unsafe()


def write_appointments(items: List[Dict[str, Any]]) -> None:
    with _LOCK:
        _write_unsafe(items)


def is_valid_time(t: str) -> bool:
    return bool(re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', t))


def is_valid_date(d: str) -> bool:
    try:
        datetime.strptime(d, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def create_appointment(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """Validate, check capacity, persist and return (ok, item, error_msg)."""
    agency_id = payload.get('agencyId')
    service_code = payload.get('serviceCode')
    date_str = payload.get('date')
    time_str = payload.get('time')

    errors: List[str] = []
    if not agency_id:
        errors.append('Thiếu agencyId')
    if not service_code:
        errors.append('Thiếu serviceCode')
    if not date_str or not is_valid_date(date_str):
        errors.append('Ngày không hợp lệ')
    if not time_str or not is_valid_time(time_str):
        errors.append('Giờ không hợp lệ')
    if errors:
        return False, {}, ', '.join(errors)

    try:
        appt_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    except Exception as e:
        return False, {}, f'Lỗi thời gian: {e}'
    if appt_dt < datetime.now():
        return False, {}, 'Không thể đặt lịch trong quá khứ'

    with _LOCK:
        items = _read_unsafe()
        slot_count = sum(
            1 for a in items
            if a.get('agencyId') == agency_id
            and a.get('date') == date_str
            and a.get('time') == time_str
        )
        if slot_count >= 5:
            return False, {}, f'Thời điểm {time_str} ngày {date_str} đã đầy'

        new_item: Dict[str, Any] = {
            'id': f"apt-{int(time.time() * 1000)}",
            'userId': payload.get('userId') or f"user-{int(time.time() * 1000)}",
            'agencyId': agency_id,
            'serviceCode': service_code,
            'date': date_str,
            'time': time_str,
            'status': payload.get('status') or 'pending',
            'fullName': payload.get('fullName'),
            'phone': payload.get('phone'),
            'info': payload.get('info'),
            'queueNumber': slot_count + 1,
        }
        items.append(new_item)
        _write_unsafe(items)

    return True, new_item, None


def suggest_slots(date_iso: str, agency_id: str = 'agency-001') -> List[str]:
    """Return available HH:MM:SS slots for a given date and agency."""
    candidate_slots = ['08:00', '09:00', '10:00', '14:00', '15:00']
    items = read_appointments()
    available = []
    for s in candidate_slots:
        count = sum(
            1 for a in items
            if a.get('date') == date_iso
            and a.get('time') == s
            and a.get('agencyId') == agency_id
        )
        if count < 5:
            available.append(s + ':00')
    return available
