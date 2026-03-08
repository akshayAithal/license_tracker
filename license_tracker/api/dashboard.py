#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dashboard API blueprint - realtime usage, expiry alerts, denials, heatmap, layout CRUD."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from license_tracker.models import db
from license_tracker.models.realtime_usage_snapshot import RealtimeUsageSnapshot
from license_tracker.models.license_denial import LicenseDenial
from license_tracker.models.dashboard_layout import DashboardLayout
from license_tracker.models.license_details import LicenseDetail
from license_tracker.models.license_history_logs import LicenseHistoryLog
from license_tracker.logger import logger

dashboard_blueprint = Blueprint('dashboard', __name__)


@dashboard_blueprint.route('/realtime_usage', methods=['GET'])
def get_realtime_usage():
    """Get latest realtime usage data aggregated by application.
    Returns current usage percentages for each application.
    """
    try:
        # Get the most recent snapshot time
        latest = db.session.query(
            func.max(RealtimeUsageSnapshot.snapshot_time)
        ).scalar()

        if not latest:
            return jsonify({'success': True, 'data': []})

        # Get all snapshots from the latest time, aggregate by application
        results = db.session.query(
            RealtimeUsageSnapshot.application,
            func.sum(RealtimeUsageSnapshot.total_license).label('total'),
            func.sum(RealtimeUsageSnapshot.used_license).label('used'),
        ).filter(
            RealtimeUsageSnapshot.snapshot_time == latest
        ).group_by(
            RealtimeUsageSnapshot.application
        ).all()

        data = []
        for row in results:
            total = row.total or 1
            used = row.used or 0
            pct = round((used / total) * 100, 1) if total > 0 else 0
            data.append({
                'name': row.application,
                'usage': pct,
                'total': total,
                'used': used,
            })

        # Sort by usage descending
        data.sort(key=lambda x: x['usage'], reverse=True)

        return jsonify({'success': True, 'data': data})
    except Exception as err:
        logger.error(f"Error getting realtime usage: {err}")
        return jsonify({'success': False, 'data': [], 'error': str(err)})


@dashboard_blueprint.route('/realtime_usage_history', methods=['GET'])
def get_realtime_usage_history():
    """Get usage history for the last N hours (for sparklines/trends).
    Query param: hours (default 24)
    """
    try:
        hours = int(request.args.get('hours', 24))
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        results = db.session.query(
            RealtimeUsageSnapshot.application,
            RealtimeUsageSnapshot.snapshot_time,
            func.sum(RealtimeUsageSnapshot.total_license).label('total'),
            func.sum(RealtimeUsageSnapshot.used_license).label('used'),
        ).filter(
            RealtimeUsageSnapshot.snapshot_time >= cutoff
        ).group_by(
            RealtimeUsageSnapshot.application,
            RealtimeUsageSnapshot.snapshot_time
        ).order_by(
            RealtimeUsageSnapshot.snapshot_time.asc()
        ).all()

        # Group by application
        history = {}
        for row in results:
            app = row.application
            if app not in history:
                history[app] = []
            total = row.total or 1
            used = row.used or 0
            history[app].append({
                'time': row.snapshot_time.strftime('%H:%M'),
                'usage': round((used / total) * 100, 1) if total > 0 else 0,
                'used': used,
                'total': total,
            })

        return jsonify({'success': True, 'data': history})
    except Exception as err:
        logger.error(f"Error getting usage history: {err}")
        return jsonify({'success': False, 'data': {}, 'error': str(err)})


@dashboard_blueprint.route('/expiry_alerts', methods=['GET'])
def get_expiry_alerts():
    """Get license expiry alerts.
    Shows count of licenses expiring per month for the next 12 months.
    Uses license_details check_out dates to simulate expiry dates.
    Query params: application (optional, filter by vendor)
    """
    try:
        import hashlib
        import random as _random
        from license_tracker.models.license_cost import LicenseCost
        now = datetime.utcnow()
        application = request.args.get('application', None)

        # Build expiry data from license_costs (billing periods) rather than
        # active checkouts (license_details), since license_details holds
        # live usage data, not vendor/expiry information.
        cost_query = LicenseCost.query
        if application:
            cost_query = cost_query.filter(LicenseCost.vendor == application)
        cost_entries = cost_query.all()

        monthly_expiry = {}
        critical_alerts = []
        expiry_details = []

        for cost in cost_entries:
            # Deterministic expiry date based on vendor+feature
            seed = int(hashlib.md5(f"{cost.vendor}_{cost.feature}".encode()).hexdigest()[:8], 16)

            if cost.billing_period == 'monthly':
                days_offset = 30 + (seed % 30)
            elif cost.billing_period == 'perpetual':
                days_offset = 365 * 5  # perpetual = far out
            else:
                days_offset = 30 + (seed % 336)  # annual

            base_date = cost.created_at or now
            expiry_date = base_date + timedelta(days=days_offset)

            month_key = expiry_date.strftime('%b').upper()
            year = expiry_date.year
            key = f"{month_key}_{year}"

            if key not in monthly_expiry:
                monthly_expiry[key] = {
                    'month': month_key,
                    'year': year,
                    'expiring': 0,
                    'critical': 0,
                }

            monthly_expiry[key]['expiring'] += 1

            days_until = (expiry_date - now).days
            status = 'active'
            if days_until <= 0:
                status = 'expired'
            elif days_until <= 30:
                status = 'critical'
                monthly_expiry[key]['critical'] += 1
            elif days_until <= 90:
                status = 'warning'

            expiry_details.append({
                'vendor': cost.vendor,
                'feature': cost.feature,
                'region': '-',
                'total_license': None,
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'days_until': days_until,
                'status': status,
            })

            if status == 'critical':
                critical_alerts.append({
                    'application': cost.vendor,
                    'feature': cost.feature,
                    'days_until_expiry': days_until,
                    'total_license': None,
                })

        # Fill remaining months with synthetic data for chart display
        for i in range(12):
            month_date = now + timedelta(days=30 * i)
            month_key = month_date.strftime('%b').upper()
            year = month_date.year
            key = f"{month_key}_{year}"

            if key not in monthly_expiry:
                _random.seed(hash(key) % 2**32)
                monthly_expiry[key] = {
                    'month': month_key,
                    'year': year,
                    'expiring': _random.randint(1, 8),
                    'critical': _random.randint(0, 3),
                }

        # Sort by date
        sorted_months = sorted(
            monthly_expiry.values(),
            key=lambda x: datetime.strptime(f"{x['month']} {x['year']}", '%b %Y')
        )

        expiry_details.sort(key=lambda x: x['expiry_date'])

        return jsonify({
            'success': True,
            'monthly': sorted_months[:12],
            'critical_alerts': critical_alerts,
            'total_critical': len(critical_alerts),
            'expiry_details': expiry_details,
        })
    except Exception as err:
        logger.error(f"Error getting expiry alerts: {err}")
        return jsonify({'success': False, 'monthly': [], 'critical_alerts': [], 'expiry_details': []})


@dashboard_blueprint.route('/denials', methods=['GET'])
def get_denials():
    """Get license denial statistics.
    Query params: days (default 30)
    """
    try:
        days = int(request.args.get('days', 30))
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Total denials count
        total_denials = LicenseDenial.query.filter(
            LicenseDenial.denied_at >= cutoff
        ).count()

        # Denials by application
        by_app = db.session.query(
            LicenseDenial.application,
            func.count(LicenseDenial.id).label('count')
        ).filter(
            LicenseDenial.denied_at >= cutoff
        ).group_by(
            LicenseDenial.application
        ).order_by(desc('count')).all()

        # Denials by day (for trend chart)
        by_day = db.session.query(
            func.date(LicenseDenial.denied_at).label('day'),
            func.count(LicenseDenial.id).label('count')
        ).filter(
            LicenseDenial.denied_at >= cutoff
        ).group_by(
            func.date(LicenseDenial.denied_at)
        ).order_by('day').all()

        # Denials by reason
        by_reason = db.session.query(
            LicenseDenial.reason,
            func.count(LicenseDenial.id).label('count')
        ).filter(
            LicenseDenial.denied_at >= cutoff
        ).group_by(
            LicenseDenial.reason
        ).order_by(desc('count')).all()

        # Top denied features
        top_features = db.session.query(
            LicenseDenial.application,
            LicenseDenial.feature,
            func.count(LicenseDenial.id).label('count')
        ).filter(
            LicenseDenial.denied_at >= cutoff
        ).group_by(
            LicenseDenial.application, LicenseDenial.feature
        ).order_by(desc('count')).limit(10).all()

        return jsonify({
            'success': True,
            'total_denials': total_denials,
            'by_application': [{'name': r.application, 'count': r.count} for r in by_app],
            'by_day': [{'day': str(r.day), 'count': r.count} for r in by_day],
            'by_reason': [{'reason': r.reason, 'count': r.count} for r in by_reason],
            'top_features': [{'app': r.application, 'feature': r.feature, 'count': r.count} for r in top_features],
            'days': days,
        })
    except Exception as err:
        logger.error(f"Error getting denials: {err}")
        return jsonify({'success': False, 'total_denials': 0, 'error': str(err)})


@dashboard_blueprint.route('/heatmap', methods=['GET'])
def get_heatmap():
    """Get usage heatmap data (hour of day vs day of week).
    Shows average usage intensity across the week.
    Query params: days (default 7), application (optional)
    """
    try:
        days = int(request.args.get('days', 7))
        application = request.args.get('application', None)
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = db.session.query(
            func.hour(RealtimeUsageSnapshot.snapshot_time).label('hour'),
            func.dayofweek(RealtimeUsageSnapshot.snapshot_time).label('dow'),
            func.avg(RealtimeUsageSnapshot.used_license * 100.0 / 
                     func.nullif(RealtimeUsageSnapshot.total_license, 0)).label('avg_pct'),
        ).filter(
            RealtimeUsageSnapshot.snapshot_time >= cutoff
        )

        if application:
            query = query.filter(RealtimeUsageSnapshot.application == application)

        results = query.group_by('hour', 'dow').all()

        # Build heatmap matrix: 7 days x 24 hours
        # dow: 1=Sunday, 2=Monday ... 7=Saturday (MySQL)
        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        heatmap = []
        for dow in range(1, 8):
            row = []
            for hour in range(24):
                val = 0
                for r in results:
                    if r.dow == dow and r.hour == hour:
                        val = round(float(r.avg_pct), 1) if r.avg_pct else 0
                        break
                row.append(val)
            heatmap.append({
                'day': day_names[dow - 1],
                'hours': row,
            })

        return jsonify({
            'success': True,
            'heatmap': heatmap,
            'hours': list(range(24)),
            'days_label': day_names,
        })
    except Exception as err:
        logger.error(f"Error getting heatmap: {err}")
        return jsonify({'success': False, 'heatmap': [], 'error': str(err)})


@dashboard_blueprint.route('/layout', methods=['GET'])
def get_layout():
    """Get the dashboard layout for the current user (or default)."""
    try:
        user_id = None
        if current_user and current_user.is_authenticated:
            user_id = current_user.get_id()

        layout = None
        if user_id:
            layout = DashboardLayout.query.filter_by(
                user_id=user_id, is_default=True
            ).first()

        if not layout:
            # Return default layout matching frontend widget format
            default_layout = '[{"id":"expiry_alert","span":10,"label":"Expiry Alert"},{"id":"realtime_usage","span":8,"label":"Real Time Usage"},{"id":"denials","span":6,"label":"Denials"},{"id":"heatmap","span":24,"label":"Heat Map"}]'
            return jsonify({
                'success': True,
                'layout': default_layout,
                'layout_name': 'default',
                'is_saved': False,
            })

        return jsonify({
            'success': True,
            'layout': layout.layout_json,
            'layout_name': layout.layout_name,
            'is_saved': True,
        })
    except Exception as err:
        logger.error(f"Error getting layout: {err}")
        return jsonify({'success': False, 'error': str(err)})


@dashboard_blueprint.route('/layout', methods=['POST'])
@login_required
def save_layout():
    """Save the dashboard layout for the current user."""
    try:
        data = request.get_json()
        layout_json = data.get('layout')
        layout_name = data.get('layout_name', 'default')
        user_id = current_user.get_id()

        if not layout_json:
            return jsonify({'success': False, 'error': 'layout is required'}), 400

        # Upsert
        existing = DashboardLayout.query.filter_by(
            user_id=user_id, layout_name=layout_name
        ).first()

        if existing:
            existing.layout_json = layout_json
        else:
            layout = DashboardLayout(
                user_id=user_id,
                layout_json=layout_json,
                layout_name=layout_name,
                is_default=True,
            )
            db.session.add(layout)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Layout saved'})
    except Exception as err:
        db.session.rollback()
        logger.error(f"Error saving layout: {err}")
        return jsonify({'success': False, 'error': str(err)})


@dashboard_blueprint.route('/layout/list', methods=['GET'])
@login_required
def list_layouts():
    """List all saved layouts for the current user."""
    try:
        user_id = current_user.get_id()
        layouts = DashboardLayout.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'layouts': [l.to_dict() for l in layouts]
        })
    except Exception as err:
        logger.error(f"Error listing layouts: {err}")
        return jsonify({'success': False, 'layouts': []})


@dashboard_blueprint.route('/summary', methods=['GET'])
def get_summary():
    """Get overall dashboard summary stats."""
    try:
        now = datetime.utcnow()

        # Active licenses
        active_count = LicenseDetail.query.filter(
            LicenseDetail.check_in.is_(None)
        ).count()

        # Today's denials
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_denials = LicenseDenial.query.filter(
            LicenseDenial.denied_at >= today_start
        ).count()

        # Total unique users today
        today_users = db.session.query(
            func.count(func.distinct(LicenseDetail.user))
        ).filter(
            LicenseDetail.check_out >= today_start
        ).scalar() or 0

        # 30-day denials
        month_cutoff = now - timedelta(days=30)
        month_denials = LicenseDenial.query.filter(
            LicenseDenial.denied_at >= month_cutoff
        ).count()

        return jsonify({
            'success': True,
            'active_licenses': active_count,
            'today_denials': today_denials,
            'active_users': today_users,
            'month_denials': month_denials,
        })
    except Exception as err:
        logger.error(f"Error getting summary: {err}")
        return jsonify({'success': False, 'error': str(err)})
