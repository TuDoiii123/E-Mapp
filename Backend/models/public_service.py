import json
from pathlib import Path
from datetime import datetime
from models.user import FileStorage

# Optional DB support
try:
    from models.db import db
    from sqlalchemy import text
    HAS_DB = True
except Exception:
    db = None
    text = None
    HAS_DB = False


def _normalize_row(raw_row):
    """Normalize mapping keys (strip BOM, lower, replace spaces) and keep values."""
    normalized = {}
    for k, v in dict(raw_row).items():
        if k is None:
            continue
        key = str(k).strip()
        # remove BOM and lowercase
        key = key.replace('\ufeff', '')
        key_norm = key.lower().replace(' ', '_')
        normalized[key_norm] = v
    return normalized


def _map_db_row_to_service(row):
    r = _normalize_row(row)

    # heuristics mapping - extend as needed
    svc = {
        'id': str(r.get('id') or r.get('code') or r.get('row_stt') or ''),
        'name': r.get('name') or r.get('ten') or '',
        'description': r.get('description') or r.get('note') or '',
        # try multiple possible category fields
        'categoryId': r.get('category_id') or r.get('category') or r.get('code') or r.get('theloai_id') or None,
        'categoryName': r.get('theloai_name') or r.get('category_name') or None,
        # agency_name or address
        'address': r.get('agency_name') or r.get('address') or r.get('agency') or '',
        # latitude/longitude variants
        'latitude': None,
        'longitude': None,
        'phone': r.get('phone') or r.get('tel') or r.get('telephone') or '',
        'email': r.get('email') or '',
        'website': r.get('website') or '',
        'workingHours': {},
        'services': [r.get('field')] if r.get('field') else [],
        'level': r.get('level') or r.get('leve') or r.get('lvl') or None,
        'rating': float(r.get('rating')) if r.get('rating') is not None and str(r.get('rating')).replace('.', '', 1).isdigit() else 0,
        'status': r.get('status') or 'normal',
        'distance': None,
        'createdAt': None,
        'updatedAt': None,
    }

    # try to parse lat/lng
    for lat_key in ('latitude', 'lat', 'y'):
        if r.get(lat_key) is not None:
            try:
                svc['latitude'] = float(r.get(lat_key))
                break
            except Exception:
                pass

    for lng_key in ('longitude', 'lng', 'lon', 'x'):
        if r.get(lng_key) is not None:
            try:
                svc['longitude'] = float(r.get(lng_key))
                break
            except Exception:
                pass

    # created/updated
    if r.get('created_at'):
        svc['createdAt'] = r.get('created_at')
    if r.get('updated_at'):
        svc['updatedAt'] = r.get('updated_at')

    return svc


class PublicService:
    """PublicService model - file-based storage with optional Postgres mapping"""

    def __init__(self, data):
        self.id = data.get('id', str(int(datetime.now().timestamp() * 1000)))
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.categoryId = data.get('categoryId')
        self.locationId = data.get('locationId')
        self.address = data.get('address')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.website = data.get('website', '')
        self.workingHours = data.get('workingHours', {
            'monday': '7:30-17:30',
            'tuesday': '7:30-17:30',
            'wednesday': '7:30-17:30',
            'thursday': '7:30-17:30',
            'friday': '7:30-17:30',
            'saturday': '7:30-12:00',
            'sunday': 'Closed'
        })
        self.services = data.get('services', [])
        self.level = data.get('level', 'district')  # ward, district, province
        self.rating = data.get('rating', 0)
        self.status = data.get('status', 'normal')  # normal, busy, available
        self.distance = data.get('distance')
        self.createdAt = data.get('createdAt', datetime.now().isoformat())
        self.updatedAt = data.get('updatedAt', datetime.now().isoformat())

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categoryId': self.categoryId,
            'locationId': self.locationId,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'workingHours': self.workingHours,
            'services': self.services,
            'level': self.level,
            'rating': self.rating,
            'status': self.status,
            'distance': self.distance,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }

    @staticmethod
    def find_all():
        """Find all services. If Postgres available, map rows to app format; else use JSON."""
        # Prefer DB
        if HAS_DB and db is not None:
            try:
                    # Try authoritative table `ds_dichvucong` first, then fallback to older `dichvucong_thanhhoa`.
                    # Try ds_dichvucong with a LEFT JOIN to ds_theloai to include category name if available.
                    try:
                        sql = text('''
                            SELECT d.*, t.id AS theloai_id, t.name AS theloai_name
                            FROM ds_dichvucong d
                            LEFT JOIN ds_theloai t ON (COALESCE(d.category_id::text, d.theloai_id::text, d.category::text) = t.id::text)
                        ''')
                        res = db.session.execute(sql)
                        rows = res.mappings().all()
                        mapped = [_map_db_row_to_service(r) for r in rows]
                        return mapped
                    except Exception:
                        # fallback to older table name if present
                        try:
                            sql = text('SELECT * FROM dichvucong_thanhhoa')
                            res = db.session.execute(sql)
                            rows = res.mappings().all()
                            mapped = [_map_db_row_to_service(r) for r in rows]
                            return mapped
                        except Exception:
                            pass
            except Exception:
                # fallback
                pass

        return FileStorage.read_json('public_services.json')

    @staticmethod
    def find_by_id(service_id):
        """Find service by ID. Try DB then JSON."""
        if HAS_DB and db is not None:
            try:
                # Try ds_dichvucong with join to get category info, then fallback to older table
                try:
                    sql = text('''
                        SELECT d.*, t.id AS theloai_id, t.name AS theloai_name
                        FROM ds_dichvucong d
                        LEFT JOIN ds_theloai t ON (COALESCE(d.category_id::text, d.theloai_id::text, d.category::text) = t.id::text)
                        WHERE (d.id::text = :id OR d.code::text = :id) LIMIT 1
                    ''')
                    res = db.session.execute(sql, {'id': service_id})
                    row = res.mappings().first()
                    if row:
                        return _map_db_row_to_service(row)
                except Exception:
                    # fallback to older table lookup
                    try:
                        sql = text('SELECT * FROM dichvucong_thanhhoa WHERE id = :id LIMIT 1')
                        res = db.session.execute(sql, {'id': service_id})
                        row = res.mappings().first()
                        if row:
                            return _map_db_row_to_service(row)
                    except Exception:
                        pass
            except Exception:
                pass

        services = FileStorage.read_json('public_services.json')
        for s in services:
            if s['id'] == service_id:
                return s
        return None

    @staticmethod
    def find_by_category(category_id):
        services = FileStorage.read_json('public_services.json')
        return [s for s in services if s.get('categoryId') == category_id]

    @staticmethod
    def find_by_level(level):
        services = FileStorage.read_json('public_services.json')
        return [s for s in services if s.get('level') == level]

    @staticmethod
    def search(query, category_id=None):
        services = PublicService.find_all()
        results = services

        if query:
            q = query.lower()
            results = [s for s in results if q in (s.get('name') or '').lower() or q in (s.get('description') or '').lower() or q in (s.get('address') or '').lower()]

        if category_id:
            results = [s for s in results if s.get('categoryId') == category_id]

        return results

    @staticmethod
    def create(data):
        services = FileStorage.read_json('public_services.json')
        service = PublicService(data)
        services.append(service.to_dict())
        FileStorage.write_json('public_services.json', services)
        return service.to_dict()

    @staticmethod
    def update(service_id, updates):
        services = FileStorage.read_json('public_services.json')
        for i, s in enumerate(services):
            if s['id'] == service_id:
                services[i].update(updates)
                services[i]['updatedAt'] = datetime.now().isoformat()
                FileStorage.write_json('public_services.json', services)
                return services[i]
        raise ValueError('Service not found')
