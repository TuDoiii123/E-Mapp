"""Queue forecast API — yêu cầu đăng nhập (phân tích vận hành)."""
from flask import Blueprint, jsonify, request

from logger import get_logger
from services.queue_forecast import weekly_profile, forecast_short_term

log = get_logger('queue_forecast_routes')
queue_forecast_bp = Blueprint('queue_forecast', __name__, url_prefix='/api/queue/forecast')


def _auth_ok():
    return getattr(request, 'user_id', None) is not None


@queue_forecast_bp.route('/weekly', methods=['GET'])
def weekly():
    if not _auth_ok():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    agency = (request.args.get('agency') or '').strip()
    if not agency:
        return jsonify({'success': False, 'message': 'Thiếu agency'}), 400
    profile = weekly_profile(agency)
    peaks = [p for p in profile if p['peak']]
    return jsonify({'success': True, 'agency': agency,
                    'profile': profile, 'peakHours': peaks}), 200


@queue_forecast_bp.route('', methods=['GET'])
def short_term():
    if not _auth_ok():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    agency = (request.args.get('agency') or '').strip()
    if not agency:
        return jsonify({'success': False, 'message': 'Thiếu agency'}), 400
    try:
        hours = min(max(int(request.args.get('hours', 8)), 1), 48)
    except ValueError:
        hours = 8
    return jsonify({'success': True, **forecast_short_term(agency, hours)}), 200
