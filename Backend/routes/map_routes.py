"""
Map Routes — dùng OpenStreetMap / Nominatim / OSRM (hoàn toàn miễn phí, không cần API key).

Endpoints:
  GET /api/map/config                         Cấu hình bản đồ
  GET /api/map/geocode?address=               Địa chỉ → tọa độ (Nominatim)
  GET /api/map/reverse-geocode?lat=&lng=      Tọa độ → địa chỉ (Nominatim)
  GET /api/map/autocomplete?input=&lat=&lng=  Gợi ý địa chỉ (Nominatim search)
  GET /api/map/place?place_id=               Chi tiết địa điểm (Nominatim details)
  GET /api/map/directions?olat=&olng=&dlat=&dlng= Lộ trình (OSRM)
"""

import os
import requests
from flask import Blueprint, request, jsonify
from logger import get_logger

log = get_logger('map_routes')

map_bp = Blueprint('map', __name__, url_prefix='/api/map')

# ── Constants ─────────────────────────────────────────────────────────────────

NOMINATIM_BASE = 'https://nominatim.openstreetmap.org'
OSRM_BASE      = 'https://router.project-osrm.org/route/v1'

# User-Agent bắt buộc theo Nominatim Usage Policy
APP_USER_AGENT = os.getenv('APP_NAME', 'E-Mapp/1.0 (dichvucong)')

NOMINATIM_HEADERS = {
    'User-Agent':     APP_USER_AGENT,
    'Accept-Language':'vi,en',
}

# Default: Hà Nội
DEFAULT_CENTER = {'lat': 21.0285, 'lng': 105.8542}
DEFAULT_ZOOM   = 13


# ── Helpers ───────────────────────────────────────────────────────────────────

def _nom_get(path: str, params: dict) -> dict:
    """Gọi Nominatim, trả về JSON."""
    resp = requests.get(
        f'{NOMINATIM_BASE}{path}',
        params={**params, 'format': 'json', 'addressdetails': 1},
        headers=NOMINATIM_HEADERS,
        timeout=8,
    )
    resp.raise_for_status()
    return resp.json()


def _ok(data):
    return jsonify({'success': True, 'data': data})


def _err(msg: str, code: int = 500):
    return jsonify({'success': False, 'message': msg}), code


def _extract_address(addr: dict) -> dict:
    """Trích ward / district / province từ address dict của Nominatim."""
    return {
        'ward':     addr.get('suburb') or addr.get('quarter') or addr.get('village') or '',
        'district': (addr.get('city_district') or addr.get('county') or
                     addr.get('municipality') or addr.get('town') or addr.get('city') or ''),
        'province': addr.get('state') or addr.get('province') or '',
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@map_bp.route('/config', methods=['GET'])
def get_map_config():
    """Cấu hình cơ bản — tile URL, center mặc định, zoom."""
    return _ok({
        'defaultCenter': DEFAULT_CENTER,
        'defaultZoom':   DEFAULT_ZOOM,
        'tileUrl':       'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attribution':   '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        'maxZoom':       19,
        'region':        'VN',
        'language':      'vi',
    })


@map_bp.route('/geocode', methods=['GET'])
def geocode():
    """
    Chuyển địa chỉ văn bản → tọa độ.

    Query params:
      address  (bắt buộc)
    """
    address = (request.args.get('address') or '').strip()
    if not address:
        return _err('Thiếu tham số address', 400)
    try:
        results = _nom_get('/search', {
            'q':            address,
            'countrycodes': 'vn',
            'limit':        1,
        })
        if not results:
            return _err('Không tìm thấy địa chỉ', 404)
        r = results[0]
        addr = _extract_address(r.get('address', {}))
        return _ok({
            'lat':              float(r['lat']),
            'lng':              float(r['lon']),
            'formattedAddress': r.get('display_name', ''),
            'placeId':          str(r.get('place_id', '')),
            **addr,
        })
    except requests.exceptions.Timeout:
        return _err('Nominatim timeout', 504)
    except Exception as e:
        log.error(f'geocode error: {e}', exc_info=True)
        return _err('Lỗi khi geocode địa chỉ')


@map_bp.route('/reverse-geocode', methods=['GET'])
def reverse_geocode():
    """
    Chuyển tọa độ → địa chỉ.

    Query params: lat, lng
    """
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    if not lat or not lng:
        return _err('Thiếu tham số lat / lng', 400)
    try:
        float(lat); float(lng)
    except ValueError:
        return _err('lat / lng không hợp lệ', 400)
    try:
        r = _nom_get('/reverse', {'lat': lat, 'lon': lng})
        if r.get('error'):
            return _ok({'formattedAddress': '', 'ward': '', 'district': '', 'province': '', 'placeId': ''})
        addr = _extract_address(r.get('address', {}))
        return _ok({
            'formattedAddress': r.get('display_name', ''),
            'placeId':          str(r.get('place_id', '')),
            **addr,
        })
    except requests.exceptions.Timeout:
        return _err('Nominatim timeout', 504)
    except Exception as e:
        log.error(f'reverse_geocode error: {e}', exc_info=True)
        return _err('Lỗi khi reverse geocode')


@map_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Gợi ý địa chỉ / địa điểm theo từ khoá.

    Query params:
      input        (bắt buộc)
      lat, lng     (tuỳ chọn) — để bias kết quả về gần vị trí này
    """
    text = (request.args.get('input') or '').strip()
    if not text:
        return _ok({'predictions': []})

    lat = request.args.get('lat')
    lng = request.args.get('lng')

    params: dict = {
        'q':            text,
        'countrycodes': 'vn',
        'limit':        6,
    }
    # Bias kết quả theo vị trí (viewbox: box ~2° quanh điểm)
    if lat and lng:
        try:
            flat, flng = float(lat), float(lng)
            params['viewbox'] = f'{flng-1},{flat+1},{flng+1},{flat-1}'
            params['bounded'] = 0  # không bắt buộc nằm trong viewbox
        except ValueError:
            pass

    try:
        results = _nom_get('/search', params)
        preds = []
        for r in results:
            display = r.get('display_name', '')
            parts   = display.split(',', 2)
            main    = parts[0].strip() if parts else display
            secondary = ', '.join(p.strip() for p in parts[1:]) if len(parts) > 1 else ''
            preds.append({
                'placeId':       str(r.get('place_id', '')),
                'description':   display,
                'mainText':      main,
                'secondaryText': secondary,
                'lat':           float(r['lat']),
                'lng':           float(r['lon']),
            })
        return _ok({'predictions': preds})
    except requests.exceptions.Timeout:
        return _err('Nominatim timeout', 504)
    except Exception as e:
        log.error(f'autocomplete error: {e}', exc_info=True)
        return _err('Lỗi autocomplete')


@map_bp.route('/place', methods=['GET'])
def place_detail():
    """
    Chi tiết địa điểm theo place_id (Nominatim OSM ID).

    Query params: place_id
    """
    place_id = (request.args.get('place_id') or '').strip()
    if not place_id:
        return _err('Thiếu tham số place_id', 400)
    try:
        # Dùng /details endpoint của Nominatim
        resp = requests.get(
            f'{NOMINATIM_BASE}/details',
            params={'place_id': place_id, 'format': 'json', 'addressdetails': 1, 'linkedplaces': 0},
            headers=NOMINATIM_HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
        r = resp.json()

        centroid = r.get('centroid', {}).get('coordinates', [None, None])  # [lng, lat]
        addr_obj  = r.get('address', {})
        addr_parts = _extract_address(addr_obj.get('properties', {}))

        return _ok({
            'name':             r.get('localname') or r.get('names', {}).get('name:vi') or r.get('names', {}).get('name', ''),
            'formattedAddress': ', '.join(filter(None, [
                addr_obj.get('properties', {}).get('road', ''),
                addr_parts['ward'],
                addr_parts['district'],
                addr_parts['province'],
            ])),
            'lat':              centroid[1] if centroid[1] is not None else None,
            'lng':              centroid[0] if centroid[0] is not None else None,
            'phone':            '',
            'website':          '',
            'rating':           None,
            'openNow':          None,
            'weekdayText':      [],
            'osmType':          r.get('osm_type', ''),
        })
    except requests.exceptions.Timeout:
        return _err('Nominatim timeout', 504)
    except Exception as e:
        log.error(f'place_detail error: {e}', exc_info=True)
        return _err('Lỗi lấy chi tiết địa điểm')


@map_bp.route('/directions', methods=['GET'])
def directions():
    """
    Lấy thông tin lộ trình (OSRM — Open Source Routing Machine, miễn phí).

    Query params:
      olat, olng  — tọa độ điểm xuất phát
      dlat, dlng  — tọa độ điểm đến
      mode        — driving | walking | cycling (mặc định: driving)
    """
    try:
        olat = float(request.args.get('olat', 0))
        olng = float(request.args.get('olng', 0))
        dlat = float(request.args.get('dlat', 0))
        dlng = float(request.args.get('dlng', 0))
    except (TypeError, ValueError):
        return _err('Tọa độ không hợp lệ', 400)

    if not (olat and olng and dlat and dlng):
        return _err('Thiếu tọa độ origin hoặc destination', 400)

    mode_map = {'driving': 'driving', 'walking': 'foot', 'cycling': 'cycling', 'bicycling': 'cycling'}
    mode = mode_map.get(request.args.get('mode', 'driving'), 'driving')

    osm_url = (
        f'https://www.openstreetmap.org/directions'
        f'?engine=osrm_car'
        f'&route={olat},{olng};{dlat},{dlng}'
    )
    google_url = (
        f'https://www.google.com/maps/dir/?api=1'
        f'&origin={olat},{olng}&destination={dlat},{dlng}'
    )

    fallback = {
        'distance':    {'text': 'N/A', 'meters': None},
        'duration':    {'text': 'N/A', 'seconds': None},
        'summary':     '',
        'osmUrl':      osm_url,
        'googleMapsUrl': google_url,
    }

    try:
        # OSRM coordinates format: lng,lat (chú ý thứ tự)
        url = f'{OSRM_BASE}/{mode}/{olng},{olat};{dlng},{dlat}'
        resp = requests.get(url, params={'overview': 'false', 'steps': 'false'}, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if data.get('code') != 'Ok' or not data.get('routes'):
            return _ok(fallback)

        route = data['routes'][0]
        dist_m = route.get('distance', 0)  # metres
        dur_s  = route.get('duration', 0)  # seconds

        dist_text = (f'{dist_m/1000:.1f} km' if dist_m >= 1000 else f'{int(dist_m)} m')
        dur_min   = int(dur_s / 60)
        dur_text  = (f'{dur_min // 60} giờ {dur_min % 60} phút' if dur_min >= 60 else f'{dur_min} phút')

        return _ok({
            'distance':      {'text': dist_text,  'meters':  int(dist_m)},
            'duration':      {'text': dur_text,   'seconds': int(dur_s)},
            'summary':       '',
            'osmUrl':        osm_url,
            'googleMapsUrl': google_url,
        })
    except requests.exceptions.Timeout:
        return _ok({**fallback, 'note': 'OSRM timeout'})
    except Exception as e:
        log.error(f'directions error: {e}', exc_info=True)
        return _ok(fallback)
