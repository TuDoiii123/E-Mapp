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
import threading
import time

import requests
from flask import Blueprint, request, jsonify
from logger import get_logger

log = get_logger('map_routes')

# ── Nominatim rate limiter (max 1 req/sec global — Usage Policy) ──────────────
_nom_lock      = threading.Lock()
_nom_last_call = 0.0
_NOM_MIN_INTERVAL = 1.05  # slightly over 1s to be safe

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
    """Gọi Nominatim với rate-limit 1 req/s (Nominatim Usage Policy)."""
    global _nom_last_call
    with _nom_lock:
        now = time.monotonic()
        wait = _NOM_MIN_INTERVAL - (now - _nom_last_call)
        if wait > 0:
            time.sleep(wait)
        _nom_last_call = time.monotonic()

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


# ── Smart Route ────────────────────────────────────────────────────────────────

# Trọng số điểm: queue quan trọng hơn khoảng cách
_DIST_W   = 0.40
_QUEUE_W  = 0.50
_LEVEL_W  = 0.10
_MAX_WAIT = 30.0   # người chờ → coi là "đầy"
_LOAD_SCORE = {'low': 0.0, 'medium': 0.2, 'high': 0.6}
_SPEED_KMH  = {'driving': 30, 'walking': 5, 'cycling': 15}
_OSM_MODE   = {'driving': 'osrm_car', 'walking': 'osrm_foot', 'cycling': 'osrm_bicycle'}


def _fmt_dist(km: float) -> str:
    return f'{km:.1f} km' if km >= 1 else f'{int(km * 1000)} m'


def _fmt_dur(minutes: int) -> str:
    if minutes >= 60:
        return f'{minutes // 60} giờ {minutes % 60} phút'
    return f'{minutes} phút'


@map_bp.route('/smart-route', methods=['GET'])
def smart_route():
    """
    Gợi ý cơ quan tối ưu dựa trên khoảng cách + số người đang chờ.

    Query params:
      lat, lng    — vị trí người dùng (bắt buộc)
      serviceId   — loại thủ tục ('all' hoặc để trống = không lọc)
      category    — loại cơ quan (tuỳ chọn)
      radius      — bán kính tìm kiếm km (mặc định 20)
      mode        — driving | walking | cycling (mặc định driving)
      limit       — số kết quả (mặc định 5, tối đa 10)
    """
    lat_str = request.args.get('lat')
    lng_str = request.args.get('lng')
    if not lat_str or not lng_str:
        return _err('Thiếu lat/lng', 400)
    try:
        user_lat = float(lat_str)
        user_lng = float(lng_str)
    except ValueError:
        return _err('lat/lng không hợp lệ', 400)

    service_id = (request.args.get('serviceId') or '').strip().lower()
    category   = (request.args.get('category') or '').strip()
    radius_km  = max(1.0, min(float(request.args.get('radius') or 20), 50.0))
    mode       = request.args.get('mode', 'driving')
    if mode not in _SPEED_KMH:
        mode = 'driving'
    limit = min(max(int(request.args.get('limit') or 5), 1), 10)

    # Load agencies (file-based, no Nominatim call needed)
    try:
        from models.public_service import PublicService
        from services.distance import find_nearby
        agencies = PublicService.find_all()
    except Exception as e:
        log.error(f'smart_route: load agencies failed: {e}', exc_info=True)
        return _err('Không thể tải danh sách cơ quan', 500)

    # Filter by service keyword
    if service_id and service_id != 'all':
        def _match(a: dict) -> bool:
            haystack = ' '.join([
                str(a.get('id', '')),
                str(a.get('categoryId', '')),
                ' '.join(str(s) for s in a.get('services', [])),
                str(a.get('name', '')),
            ]).lower()
            return service_id in haystack
        agencies = [a for a in agencies if _match(a)]

    if category and category != 'all':
        agencies = [a for a in agencies if a.get('categoryId') == category]

    # Find nearby + distances (Haversine — no API call)
    nearby = find_nearby(agencies, user_lat, user_lng, radius_km)
    if not nearby:
        return _ok({'recommendations': [], 'total': 0,
                    'message': 'Không tìm thấy cơ quan phù hợp trong bán kính này'})

    # Get live queue data from PostgreSQL
    queue_map: dict = {}
    try:
        from models.db import db
        from sqlalchemy import text as _text
        rows = db.session.execute(
            _text('SELECT agency_id, total_waiting, total_serving, load_level '
                  'FROM public.agency_queue_realtime')
        ).fetchall()
        queue_map = {
            r.agency_id: {
                'waiting':   r.total_waiting or 0,
                'serving':   r.total_serving or 0,
                'loadLevel': r.load_level or 'low',
            }
            for r in rows
        }
    except Exception as e:
        log.warning(f'smart_route: queue fetch failed: {e}')

    # Score each agency
    scored = []
    max_dist = max(radius_km, 1.0)
    for agency in nearby:
        dist_km   = float(agency.get('distance') or 0)
        qs        = queue_map.get(agency['id'], {})
        waiting   = int(qs.get('waiting', 0))
        load_lvl  = qs.get('loadLevel', 'low')

        dist_norm  = min(dist_km / max_dist, 1.0)
        queue_norm = min(waiting / _MAX_WAIT, 1.0)
        level_norm = _LOAD_SCORE.get(load_lvl, 0.0)

        score = dist_norm * _DIST_W + queue_norm * _QUEUE_W + level_norm * _LEVEL_W

        # Ước tính thời gian chờ: bình quân 5 phút/người, tối thiểu 5 phút
        est_wait_min = max(5, waiting * 5)

        scored.append({
            'agency':       agency,
            'queue':        qs,
            'waiting':      waiting,
            'loadLevel':    load_lvl,
            'dist_km':      dist_km,
            'score':        round(score, 4),
            'estWaitMin':   est_wait_min,
        })

    scored.sort(key=lambda x: x['score'])
    top = scored[:limit]

    # Tag đặc biệt cho nearest / least_busy
    nearest_id    = min(scored, key=lambda x: x['dist_km'])['agency']['id']
    least_busy_id = min(scored, key=lambda x: x['waiting'])['agency']['id']

    recommendations = []
    for rank, item in enumerate(top, 1):
        a         = item['agency']
        agency_id = a['id']
        dist_km   = item['dist_km']
        waiting   = item['waiting']
        load_lvl  = item['loadLevel']

        # Tag
        if rank == 1:
            tag = 'recommended'
        elif agency_id == nearest_id:
            tag = 'nearest'
        elif agency_id == least_busy_id:
            tag = 'least_busy'
        else:
            tag = None

        # Lý do gợi ý
        dist_text = _fmt_dist(dist_km)
        if rank == 1:
            if load_lvl == 'low' and dist_km < 3:
                reason = 'Gần và ít người chờ — lý tưởng nhất lúc này'
            elif load_lvl == 'low':
                reason = f'Chỉ {waiting} người chờ, ước tính khoảng {_fmt_dur(item["estWaitMin"])}'
            elif dist_km < 2:
                reason = f'Gần nhất ({dist_text}), mức tải chấp nhận được'
            else:
                reason = f'Cân bằng tốt nhất: {dist_text} — {waiting} người đang chờ'
        elif tag == 'nearest':
            reason = f'Gần nhất ({dist_text}) nhưng đang có {waiting} người chờ'
        elif tag == 'least_busy':
            reason = f'Ít đông nhất ({waiting} người chờ), xa hơn một chút so với lựa chọn #1'
        else:
            reason = f'{dist_text} — {waiting} người chờ, ước tính {_fmt_dur(item["estWaitMin"])}'

        # Đường dẫn chỉ đường
        a_lat = a.get('latitude')
        a_lng = a.get('longitude')
        osm_mode = _OSM_MODE.get(mode, 'osrm_car')
        if a_lat and a_lng:
            osm_url   = (f'https://www.openstreetmap.org/directions'
                         f'?engine={osm_mode}&route={user_lat},{user_lng};{a_lat},{a_lng}')
            gmaps_url = (f'https://www.google.com/maps/dir/?api=1'
                         f'&origin={user_lat},{user_lng}'
                         f'&destination={a_lat},{a_lng}&travelmode={mode}')
        else:
            osm_url = gmaps_url = ''

        # Thời gian di chuyển ước tính (không gọi OSRM để tránh rate limit)
        speed = _SPEED_KMH.get(mode, 30)
        dur_min = max(1, round((dist_km / speed) * 60))

        recommendations.append({
            'rank':   rank,
            'tag':    tag,
            'reason': reason,
            'score':  item['score'],
            'agency': {
                'id':        agency_id,
                'name':      a.get('name', ''),
                'address':   a.get('address', ''),
                'phone':     a.get('phone', ''),
                'latitude':  a_lat,
                'longitude': a_lng,
                'status':    a.get('status', 'normal'),
            },
            'distance': {
                'text': _fmt_dist(dist_km),
                'km':   round(dist_km, 2),
            },
            'duration': {
                'text':    _fmt_dur(dur_min),
                'minutes': dur_min,
            },
            'queue': {
                'waiting':     waiting,
                'serving':     item['queue'].get('serving', 0),
                'loadLevel':   load_lvl,
                'estWaitMin':  item['estWaitMin'],
                'estWaitText': _fmt_dur(item['estWaitMin']),
            },
            'navigation': {
                'osmUrl':      osm_url,
                'googleMapsUrl': gmaps_url,
            },
        })

    return _ok({
        'recommendations': recommendations,
        'total': len(recommendations),
        'searchParams': {
            'lat': user_lat, 'lng': user_lng,
            'serviceId': service_id or None,
            'radius': radius_km,
            'mode': mode,
        },
    })
