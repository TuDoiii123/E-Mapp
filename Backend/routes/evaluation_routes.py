"""
Evaluation routes — citizen feedback on completed public-service applications.

Endpoints:
  GET  /api/evaluations        — list evaluatable (approved) apps + past evals
  POST /api/evaluations        — submit a new evaluation
  GET  /api/evaluations/stats  — aggregated public stats
"""
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from models.db import db
from logger import get_logger

log = get_logger('evaluation_routes')

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluations')


def _new_id() -> str:
    return str(uuid.uuid4())


@evaluation_bp.route('', methods=['GET'])
def list_evaluations():
    """Approved applications the user can rate, plus their already-submitted ratings."""
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'success': False, 'message': 'Chưa xác thực'}), 401

    try:
        apps = db.session.execute(
            text('''
                SELECT id, service_id, data, updated_at
                FROM public.applications
                WHERE applicant_id = :uid AND status = 'approved'
                ORDER BY updated_at DESC
            '''),
            {'uid': user_id},
        ).fetchall()

        evals = db.session.execute(
            text('''
                SELECT application_id, attitude_rating, time_rating,
                       facilities_rating, avg_rating, comment, submitted_at
                FROM public.evaluations
                WHERE user_id = :uid
            '''),
            {'uid': user_id},
        ).fetchall()

        evaluated_ids = {e.application_id for e in evals}
        eval_by_app   = {e.application_id: e for e in evals}

        evaluatable = []
        for app in apps:
            app_data    = app.data or {}
            service_name = app_data.get('serviceName') or app.service_id or ''
            agency_name  = app_data.get('agencyName') or ''
            updated_str  = app.updated_at.isoformat() if app.updated_at else None

            if app.id in evaluated_ids:
                ev = eval_by_app[app.id]
                evaluatable.append({
                    'id':            app.id,
                    'applicationId': app.id,
                    'agency':        agency_name,
                    'service':       service_name,
                    'status':        'done',
                    'code':          app.id[:8].upper(),
                    'rating':        round(ev.avg_rating),
                    'updatedAt':     updated_str,
                })
            else:
                evaluatable.append({
                    'id':            app.id,
                    'applicationId': app.id,
                    'agency':        agency_name,
                    'service':       service_name,
                    'status':        'evaluatable',
                    'code':          app.id[:8].upper(),
                    'updatedAt':     updated_str,
                })

        past_evaluations = [
            {
                'applicationId':   ev.application_id,
                'attitudeRating':  ev.attitude_rating,
                'timeRating':      ev.time_rating,
                'facilitiesRating':ev.facilities_rating,
                'avgRating':       ev.avg_rating,
                'comment':         ev.comment,
                'submittedAt':     ev.submitted_at.isoformat() if ev.submitted_at else None,
            }
            for ev in evals
        ]

        return jsonify({
            'success': True,
            'data': {
                'evaluatable':     evaluatable,
                'pastEvaluations': past_evaluations,
            },
        }), 200

    except Exception as e:
        log.error(f'list_evaluations: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@evaluation_bp.route('', methods=['POST'])
def submit_evaluation():
    """Submit a rating for a completed application."""
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return jsonify({'success': False, 'message': 'Chưa xác thực'}), 401

    payload  = request.get_json(silent=True) or {}
    app_id   = (payload.get('applicationId') or '').strip()
    attitude = int(payload.get('attitudeRating', 0))
    time_r   = int(payload.get('timeRating', 0))
    fac      = int(payload.get('facilitiesRating', 0))
    comment  = (payload.get('comment') or '').strip()[:2000]

    if not app_id:
        return jsonify({'success': False, 'message': 'Thiếu applicationId'}), 400
    if not (1 <= attitude <= 5 and 1 <= time_r <= 5 and 1 <= fac <= 5):
        return jsonify({'success': False, 'message': 'Rating phải từ 1 đến 5'}), 400

    try:
        app_row = db.session.execute(
            text('''
                SELECT id, service_id, data
                FROM public.applications
                WHERE id = :id AND applicant_id = :uid AND status = 'approved'
            '''),
            {'id': app_id, 'uid': user_id},
        ).fetchone()

        if not app_row:
            return jsonify({'success': False, 'message': 'Hồ sơ không tồn tại hoặc chưa được duyệt'}), 404

        existing = db.session.execute(
            text('SELECT id FROM public.evaluations WHERE application_id = :aid AND user_id = :uid'),
            {'aid': app_id, 'uid': user_id},
        ).fetchone()
        if existing:
            return jsonify({'success': False, 'message': 'Bạn đã đánh giá hồ sơ này rồi'}), 409

        avg_r     = round((attitude + time_r + fac) / 3, 2)
        app_data  = app_row.data or {}
        agency_id = app_data.get('agencyId') or ''
        svc_name  = app_data.get('serviceName') or app_row.service_id or ''

        db.session.execute(
            text('''
                INSERT INTO public.evaluations
                    (id, application_id, user_id, agency_id, service_name,
                     attitude_rating, time_rating, facilities_rating, avg_rating, comment)
                VALUES (:id, :aid, :uid, :agency, :svc, :att, :tm, :fac, :avg, :cmt)
            '''),
            {
                'id': _new_id(), 'aid': app_id, 'uid': user_id,
                'agency': agency_id, 'svc': svc_name,
                'att': attitude, 'tm': time_r, 'fac': fac,
                'avg': avg_r, 'cmt': comment,
            },
        )
        db.session.commit()

        return jsonify({'success': True, 'data': {'avgRating': avg_r}}), 201

    except Exception as e:
        db.session.rollback()
        log.error(f'submit_evaluation: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@evaluation_bp.route('/stats', methods=['GET'])
def evaluation_stats():
    """Aggregated public statistics — no auth required."""
    try:
        row = db.session.execute(
            text('''
                SELECT COUNT(*)                                              AS total,
                       COALESCE(AVG(avg_rating), 0)                         AS avg_rating,
                       SUM(CASE WHEN avg_rating >= 4 THEN 1 ELSE 0 END)     AS satisfied
                FROM public.evaluations
            ''')
        ).fetchone()

        total  = row.total or 0
        avg    = round(float(row.avg_rating or 0), 1)
        sat    = row.satisfied or 0
        sat_pct = round((sat / total) * 100) if total else 0

        return jsonify({
            'success': True,
            'data': {
                'totalEvaluations': total,
                'avgRating':        avg,
                'satisfactionRate': sat_pct,
            },
        }), 200

    except Exception as e:
        log.error(f'evaluation_stats: {e}', exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
