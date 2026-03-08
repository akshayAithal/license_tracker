#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Chat API blueprint - natural language querying for license data."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc, cast, String
from datetime import datetime, timedelta
import re

from license_tracker.models import db
from license_tracker.models.license_details import LicenseDetail
from license_tracker.models.license_history_logs import LicenseHistoryLog
from license_tracker.models.license_denial import LicenseDenial
from license_tracker.models.license_cost import LicenseCost
from license_tracker.models.realtime_usage_snapshot import RealtimeUsageSnapshot
from license_tracker.logger import logger

chat_blueprint = Blueprint('chat', __name__)


# ---------------------------------------------------------------------------
# Keyword / intent helpers
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    'active': ['active', 'checked out', 'checkout', 'in use', 'current', 'live', 'running', 'who is using'],
    'history': ['history', 'historical', 'past', 'previous', 'log', 'logs', 'checked in', 'checkin', 'usage history'],
    'denial': ['denial', 'denials', 'denied', 'rejected', 'refused', 'failed'],
    'cost': ['cost', 'costing', 'price', 'billing', 'expense', 'spend', 'budget', 'vendor cost'],
    'expiry': ['expiry', 'expiring', 'expire', 'renewal', 'renew', 'end date'],
    'usage': ['usage', 'utilization', 'utilisation', 'how much', 'consumption'],
    'summary': ['summary', 'overview', 'stats', 'statistics', 'total', 'count', 'how many'],
    'user': ['user', 'who', 'person', 'engineer', 'employee'],
    'feature': ['feature', 'module', 'product', 'software'],
    'top': ['top', 'most', 'highest', 'heaviest', 'busiest', 'maximum'],
}

VENDOR_ALIASES = {
    'msc': 'MSC', 'nastran': 'MSC', 'patran': 'MSC', 'marc': 'MSC',
    'altair': 'Altair', 'hyperworks': 'Altair', 'hypermesh': 'Altair', 'radioss': 'Altair',
    'rlm': 'RLM', 'masta': 'RLM',
    'particleworks': 'Particleworks', 'pw': 'Particleworks',
}

FEATURE_NAMES = [
    'nastran', 'patran', 'marc', 'hyperworks', 'hypermesh', 'radioss',
    'masta', 'particleworks',
]

REGION_ALIASES = {
    'eu': 'EU', 'europe': 'EU',
    'apac': 'APAC', 'asia': 'APAC', 'asia pacific': 'APAC',
    'ame': 'AME', 'america': 'AME', 'americas': 'AME', 'us': 'AME', 'usa': 'AME',
}


def detect_intents(query):
    """Return a set of intent labels found in the query string."""
    q = query.lower()
    found = set()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                found.add(intent)
                break
    return found


def extract_vendor(query):
    q = query.lower()
    for alias, vendor in VENDOR_ALIASES.items():
        if alias in q:
            return vendor
    return None


def extract_feature(query):
    q = query.lower()
    for f in FEATURE_NAMES:
        if f in q:
            return f
    return None


def extract_region(query):
    q = query.lower()
    for alias, region in REGION_ALIASES.items():
        if re.search(r'\b' + re.escape(alias) + r'\b', q):
            return region
    return None


def extract_username(query):
    """Try to pull out a username like john.doe from the query."""
    match = re.search(r'\b([a-z]+\.[a-z]+)\b', query.lower())
    if match:
        candidate = match.group(1)
        # Filter out common phrases
        if candidate not in ['in.use', 'checked.out', 'checked.in']:
            return candidate
    return None


def extract_days(query):
    """Extract a number of days from phrases like 'last 7 days' or 'past 30 days'."""
    match = re.search(r'(?:last|past|recent)\s+(\d+)\s*days?', query.lower())
    if match:
        return int(match.group(1))
    return None


def extract_limit(query):
    """Extract top N from phrases like 'top 5' or 'top 10'."""
    match = re.search(r'top\s+(\d+)', query.lower())
    if match:
        return int(match.group(1))
    return None


# ---------------------------------------------------------------------------
# Query handlers
# ---------------------------------------------------------------------------

def handle_active_licenses(vendor, feature, region, username, limit):
    """Query active/live license checkouts."""
    q = LicenseDetail.query
    if vendor:
        q = q.filter(LicenseDetail.application == vendor)
    if feature:
        q = q.filter(LicenseDetail.feature == feature)
    if region:
        q = q.filter(LicenseDetail.region == region)
    if username:
        q = q.filter(LicenseDetail.user == username)

    count = q.count()
    rows = q.order_by(desc(LicenseDetail.check_out)).limit(limit or 20).all()

    records = []
    for r in rows:
        records.append({
            'user': r.user,
            'application': r.application,
            'feature': r.feature,
            'region': r.region,
            'host': r.host,
            'licenses_used': r.license_used,
            'check_out': r.check_out.strftime('%Y-%m-%d %H:%M') if r.check_out else None,
            'total_license': r.total_license,
            'total_used': r.total_license_used,
        })

    filters_desc = _build_filter_desc(vendor, feature, region, username)
    title = "Active License Checkouts{0}".format(filters_desc)
    summary = "Found **{0}** active checkout(s){1}.".format(count, filters_desc)

    return {
        'title': title,
        'summary': summary,
        'data': records,
        'columns': ['user', 'application', 'feature', 'region', 'host', 'licenses_used', 'check_out', 'total_license', 'total_used'],
        'type': 'table',
    }


def handle_history(vendor, feature, region, username, days, limit):
    """Query license history logs."""
    q = LicenseHistoryLog.query
    if vendor:
        q = q.filter(LicenseHistoryLog.application == vendor)
    if feature:
        q = q.filter(LicenseHistoryLog.feature == feature)
    if region:
        q = q.filter(LicenseHistoryLog.region == region)
    if username:
        q = q.filter(LicenseHistoryLog.user == username)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = q.filter(LicenseHistoryLog.date_time >= cutoff)

    count = q.count()
    rows = q.order_by(desc(LicenseHistoryLog.date_time)).limit(limit or 20).all()

    records = []
    for r in rows:
        records.append({
            'user': r.user,
            'application': r.application,
            'feature': r.feature,
            'region': r.region,
            'check_out': r.check_out.strftime('%Y-%m-%d %H:%M') if r.check_out else None,
            'check_in': r.check_in.strftime('%Y-%m-%d %H:%M') if r.check_in else None,
            'spent_hours': r.spent_hours,
            'licenses_used': r.license_used,
        })

    days_desc = " (last {0} days)".format(days) if days else ""
    filters_desc = _build_filter_desc(vendor, feature, region, username)
    title = "License Usage History{0}{1}".format(filters_desc, days_desc)
    summary = "Found **{0}** history record(s){1}{2}.".format(count, filters_desc, days_desc)

    return {
        'title': title,
        'summary': summary,
        'data': records,
        'columns': ['user', 'application', 'feature', 'region', 'check_out', 'check_in', 'spent_hours', 'licenses_used'],
        'type': 'table',
    }


def handle_denials(vendor, feature, region, username, days, limit):
    """Query license denials."""
    q = LicenseDenial.query
    if vendor:
        q = q.filter(LicenseDenial.application == vendor)
    if feature:
        q = q.filter(LicenseDenial.feature == feature)
    if region:
        q = q.filter(LicenseDenial.region == region)
    if username:
        q = q.filter(LicenseDenial.user == username)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = q.filter(LicenseDenial.denied_at >= cutoff)
    else:
        cutoff = datetime.utcnow() - timedelta(days=30)
        q = q.filter(LicenseDenial.denied_at >= cutoff)

    count = q.count()
    rows = q.order_by(desc(LicenseDenial.denied_at)).limit(limit or 20).all()

    records = []
    for r in rows:
        records.append({
            'user': r.user,
            'application': r.application,
            'feature': r.feature,
            'region': r.region,
            'reason': r.reason,
            'denied_at': r.denied_at.strftime('%Y-%m-%d %H:%M') if r.denied_at else None,
        })

    days_val = days or 30
    filters_desc = _build_filter_desc(vendor, feature, region, username)
    title = "License Denials{0} (last {1} days)".format(filters_desc, days_val)
    summary = "Found **{0}** denial(s){1} in the last {2} days.".format(count, filters_desc, days_val)

    return {
        'title': title,
        'summary': summary,
        'data': records,
        'columns': ['user', 'application', 'feature', 'region', 'reason', 'denied_at'],
        'type': 'table',
    }


def handle_top_users(vendor, feature, region, days, limit):
    """Top users by license usage hours or checkout count."""
    q = db.session.query(
        LicenseHistoryLog.user,
        func.count(LicenseHistoryLog.id_).label('checkout_count'),
        func.sum(func.cast(LicenseHistoryLog.spent_hours, db.Float)).label('total_hours'),
    )
    if vendor:
        q = q.filter(LicenseHistoryLog.application == vendor)
    if feature:
        q = q.filter(LicenseHistoryLog.feature == feature)
    if region:
        q = q.filter(LicenseHistoryLog.region == region)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = q.filter(LicenseHistoryLog.date_time >= cutoff)

    rows = q.group_by(LicenseHistoryLog.user)\
            .order_by(desc('total_hours'))\
            .limit(limit or 10).all()

    records = []
    for r in rows:
        records.append({
            'user': r.user,
            'checkouts': r.checkout_count,
            'total_hours': round(r.total_hours, 2) if r.total_hours else 0,
        })

    days_desc = " (last {0} days)".format(days) if days else ""
    filters_desc = _build_filter_desc(vendor, feature, region, None)
    lim = limit or 10
    title = "Top {0} Users by Usage{1}{2}".format(lim, filters_desc, days_desc)
    summary = "Top **{0}** users ranked by total hours{1}{2}.".format(lim, filters_desc, days_desc)

    return {
        'title': title,
        'summary': summary,
        'data': records,
        'columns': ['user', 'checkouts', 'total_hours'],
        'type': 'table',
    }


def handle_summary(vendor, feature, region, days):
    """General summary / overview stats."""
    active_q = LicenseDetail.query
    hist_q = LicenseHistoryLog.query
    denial_q = LicenseDenial.query

    if vendor:
        active_q = active_q.filter(LicenseDetail.application == vendor)
        hist_q = hist_q.filter(LicenseHistoryLog.application == vendor)
        denial_q = denial_q.filter(LicenseDenial.application == vendor)
    if feature:
        active_q = active_q.filter(LicenseDetail.feature == feature)
        hist_q = hist_q.filter(LicenseHistoryLog.feature == feature)
        denial_q = denial_q.filter(LicenseDenial.feature == feature)
    if region:
        active_q = active_q.filter(LicenseDetail.region == region)
        hist_q = hist_q.filter(LicenseHistoryLog.region == region)
        denial_q = denial_q.filter(LicenseDenial.region == region)

    d = days or 30
    cutoff = datetime.utcnow() - timedelta(days=d)
    hist_q = hist_q.filter(LicenseHistoryLog.date_time >= cutoff)
    denial_q = denial_q.filter(LicenseDenial.denied_at >= cutoff)

    active_count = active_q.count()
    history_count = hist_q.count()
    denial_count = denial_q.count()

    # Unique users in history
    unique_users = hist_q.with_entities(func.count(func.distinct(LicenseHistoryLog.user))).scalar() or 0

    # Unique features in use
    unique_features = active_q.with_entities(func.count(func.distinct(LicenseDetail.feature))).scalar() or 0

    filters_desc = _build_filter_desc(vendor, feature, region, None)
    title = "License Summary{0} (last {1} days)".format(filters_desc, d)

    summary_text = (
        "**Active checkouts:** {0}\n"
        "**History records ({1}d):** {2}\n"
        "**Denials ({1}d):** {3}\n"
        "**Unique users ({1}d):** {4}\n"
        "**Active features:** {5}"
    ).format(active_count, d, history_count, denial_count, unique_users, unique_features)

    stats = [
        {'label': 'Active Checkouts', 'value': active_count},
        {'label': 'History Records ({0}d)'.format(d), 'value': history_count},
        {'label': 'Denials ({0}d)'.format(d), 'value': denial_count},
        {'label': 'Unique Users ({0}d)'.format(d), 'value': unique_users},
        {'label': 'Active Features', 'value': unique_features},
    ]

    return {
        'title': title,
        'summary': summary_text,
        'data': stats,
        'columns': ['label', 'value'],
        'type': 'stats',
    }


def handle_usage_by_feature(vendor, region, days, limit):
    """Usage breakdown by feature."""
    q = db.session.query(
        LicenseHistoryLog.application,
        LicenseHistoryLog.feature,
        func.count(LicenseHistoryLog.id_).label('checkout_count'),
        func.sum(func.cast(LicenseHistoryLog.spent_hours, db.Float)).label('total_hours'),
    )
    if vendor:
        q = q.filter(LicenseHistoryLog.application == vendor)
    if region:
        q = q.filter(LicenseHistoryLog.region == region)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = q.filter(LicenseHistoryLog.date_time >= cutoff)

    rows = q.group_by(LicenseHistoryLog.application, LicenseHistoryLog.feature)\
            .order_by(desc('total_hours'))\
            .limit(limit or 20).all()

    records = []
    for r in rows:
        records.append({
            'application': r.application,
            'feature': r.feature,
            'checkouts': r.checkout_count,
            'total_hours': round(r.total_hours, 2) if r.total_hours else 0,
        })

    days_desc = " (last {0} days)".format(days) if days else ""
    title = "Usage by Feature{0}".format(days_desc)
    summary = "Feature usage breakdown{0}, sorted by total hours.".format(days_desc)

    return {
        'title': title,
        'summary': summary,
        'data': records,
        'columns': ['application', 'feature', 'checkouts', 'total_hours'],
        'type': 'table',
    }


def _build_filter_desc(vendor, feature, region, username):
    parts = []
    if vendor:
        parts.append(vendor)
    if feature:
        parts.append(feature)
    if region:
        parts.append(region)
    if username:
        parts.append(username)
    if parts:
        return " for " + ", ".join(parts)
    return ""


# ---------------------------------------------------------------------------
# Main query router
# ---------------------------------------------------------------------------

def process_query(query):
    """Parse the user's natural language query and return structured results."""
    intents = detect_intents(query)
    vendor = extract_vendor(query)
    feature = extract_feature(query)
    region = extract_region(query)
    username = extract_username(query)
    days = extract_days(query)
    limit = extract_limit(query)

    # Route to appropriate handler based on detected intents
    if 'denial' in intents:
        return handle_denials(vendor, feature, region, username, days, limit)

    if 'top' in intents and ('user' in intents or 'usage' in intents or not intents.difference({'top'})):
        return handle_top_users(vendor, feature, region, days, limit)

    if 'active' in intents:
        return handle_active_licenses(vendor, feature, region, username, limit)

    if 'history' in intents:
        return handle_history(vendor, feature, region, username, days, limit)

    if 'summary' in intents or 'usage' in intents:
        if 'feature' in intents or feature:
            return handle_usage_by_feature(vendor, region, days, limit)
        return handle_summary(vendor, feature, region, days)

    if 'expiry' in intents:
        return handle_summary(vendor, feature, region, days)

    if 'user' in intents and username:
        return handle_history(vendor, feature, region, username, days, limit)

    # Default: show summary
    if vendor or feature or region:
        return handle_summary(vendor, feature, region, days)

    return handle_summary(None, None, None, days)


# ---------------------------------------------------------------------------
# Suggestion prompts
# ---------------------------------------------------------------------------

SUGGESTIONS = [
    "Show active checkouts for MSC",
    "Top 10 users by usage in the last 30 days",
    "Show denials for Altair in APAC",
    "License usage history for nastran last 7 days",
    "Summary of all licenses",
    "Who is using hyperworks?",
    "Show history for john.doe",
    "Feature usage breakdown for last 30 days",
]


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------

@chat_blueprint.route('/query', methods=['POST'])
@login_required
def chat_query():
    """Process a natural language query about license data.
    
    Request body: { "query": "..." }
    Response: {
        "success": true,
        "result": {
            "title": "...",
            "summary": "...",
            "data": [...],
            "columns": [...],
            "type": "table" | "stats"
        }
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('query', '').strip():
            return jsonify({'success': False, 'error': 'Please provide a query.'}), 400

        query = data['query'].strip()
        logger.info("Chat query from %s: %s" % (current_user.login, query))

        result = process_query(query)
        return jsonify({'success': True, 'result': result})

    except Exception as e:
        logger.error("Chat query error: %s" % str(e), exc_info=True)
        return jsonify({'success': False, 'error': 'An error occurred processing your query.'}), 500


@chat_blueprint.route('/suggestions', methods=['GET'])
@login_required
def chat_suggestions():
    """Return suggested queries for the chat interface."""
    return jsonify({'success': True, 'suggestions': SUGGESTIONS})
