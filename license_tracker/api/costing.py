#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Costing API blueprint - file management, AI document analysis, license cost CRUD."""

import os
import shutil
from flask import Blueprint, jsonify, request, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from license_tracker.models import db
from license_tracker.models.license_cost import LicenseCost
from license_tracker.models.app_settings import AppSettings
from license_tracker.logger import logger

costing_blueprint = Blueprint('costing', __name__)

ALLOWED_EXTENSIONS = {'txt', 'csv', 'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def _get_user_base_dir():
    """Get the base directory for all user files."""
    return os.path.join(current_app.instance_path, 'user_files')


def _get_user_dir(username):
    """Get a specific user's file directory, creating it if needed."""
    base = _get_user_base_dir()
    user_dir = os.path.join(base, secure_filename(username))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
        logger.info("Created user directory: %s", user_dir)
    return user_dir


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _safe_subpath(user_dir, subpath):
    """Resolve subpath safely to prevent directory traversal."""
    if not subpath:
        return user_dir
    clean = os.path.normpath(subpath)
    if clean.startswith('..') or os.path.isabs(clean):
        return None
    full = os.path.join(user_dir, clean)
    full = os.path.normpath(full)
    if not full.startswith(os.path.normpath(user_dir)):
        return None
    return full


def _read_file_text(filepath):
    """Read file content as text. Supports txt, csv, and basic pdf extraction."""
    ext = filepath.rsplit('.', 1)[-1].lower()
    if ext in ('txt', 'csv'):
        with open(filepath, 'r', errors='replace') as f:
            return f.read()
    elif ext == 'pdf':
        try:
            # Try PyPDF2 first
            import PyPDF2
            text_parts = []
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text_parts.append(page.extract_text() or '')
            return '\n'.join(text_parts)
        except ImportError:
            pass
        try:
            # Fallback: pdfminer
            from pdfminer.high_level import extract_text
            return extract_text(filepath)
        except ImportError:
            return '[PDF reading libraries not installed. Install PyPDF2 or pdfminer.six]'
    return '[Unsupported file type]'


def ensure_user_folder(username):
    """Create user folder if it does not exist. Called at login."""
    _get_user_dir(username)


# ============ File Management ============

@costing_blueprint.route('/files', methods=['GET'])
@login_required
def list_files():
    """List files and folders in the user's directory.
    Query param: path (subfolder path, default root)
    """
    user_dir = _get_user_dir(current_user.login)
    subpath = request.args.get('path', '')
    target = _safe_subpath(user_dir, subpath)

    if not target or not os.path.isdir(target):
        return jsonify({'success': False, 'error': 'Invalid path'}), 400

    items = []
    for name in sorted(os.listdir(target)):
        full = os.path.join(target, name)
        rel = os.path.relpath(full, user_dir).replace('\\', '/')
        if os.path.isdir(full):
            items.append({'name': name, 'path': rel, 'type': 'folder', 'size': 0})
        else:
            ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
            items.append({
                'name': name,
                'path': rel,
                'type': 'file',
                'ext': ext,
                'size': os.path.getsize(full),
            })

    return jsonify({'success': True, 'items': items, 'current_path': subpath or '/'})


@costing_blueprint.route('/files/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload a file (txt, csv, pdf) to the user's directory.
    Form data: file (multipart), path (optional subfolder)
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not _allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Only txt, csv, and pdf files are allowed'}), 400

    user_dir = _get_user_dir(current_user.login)
    subpath = request.form.get('path', '')
    target_dir = _safe_subpath(user_dir, subpath)

    if not target_dir:
        return jsonify({'success': False, 'error': 'Invalid path'}), 400

    os.makedirs(target_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(target_dir, filename)
    file.save(filepath)

    logger.info("User %s uploaded file: %s", current_user.login, filepath)
    return jsonify({'success': True, 'message': 'File uploaded', 'filename': filename})


@costing_blueprint.route('/files/folder', methods=['POST'])
@login_required
def create_folder():
    """Create a subfolder in the user's directory.
    JSON body: { "name": "folder_name", "path": "parent_path" }
    """
    data = request.get_json()
    folder_name = data.get('name', '').strip()
    if not folder_name:
        return jsonify({'success': False, 'error': 'Folder name is required'}), 400

    user_dir = _get_user_dir(current_user.login)
    parent = _safe_subpath(user_dir, data.get('path', ''))
    if not parent:
        return jsonify({'success': False, 'error': 'Invalid parent path'}), 400

    new_folder = os.path.join(parent, secure_filename(folder_name))
    if os.path.exists(new_folder):
        return jsonify({'success': False, 'error': 'Folder already exists'}), 400

    os.makedirs(new_folder, exist_ok=True)
    logger.info("User %s created folder: %s", current_user.login, new_folder)
    return jsonify({'success': True, 'message': 'Folder created'})


@costing_blueprint.route('/files/delete', methods=['POST'])
@login_required
def delete_file():
    """Delete a file or folder.
    JSON body: { "path": "relative/path" }
    """
    data = request.get_json()
    user_dir = _get_user_dir(current_user.login)
    target = _safe_subpath(user_dir, data.get('path', ''))

    if not target or target == os.path.normpath(user_dir):
        return jsonify({'success': False, 'error': 'Cannot delete root folder'}), 400

    if not os.path.exists(target):
        return jsonify({'success': False, 'error': 'Not found'}), 404

    if os.path.isdir(target):
        shutil.rmtree(target)
    else:
        os.remove(target)

    logger.info("User %s deleted: %s", current_user.login, target)
    return jsonify({'success': True, 'message': 'Deleted successfully'})


@costing_blueprint.route('/files/download', methods=['GET'])
@login_required
def download_file():
    """Download a file.
    Query param: path (relative path to file)
    """
    user_dir = _get_user_dir(current_user.login)
    target = _safe_subpath(user_dir, request.args.get('path', ''))

    if not target or not os.path.isfile(target):
        return jsonify({'success': False, 'error': 'File not found'}), 404

    return send_file(target, as_attachment=True)


# ============ AI Document Analysis ============

@costing_blueprint.route('/files/analyze', methods=['POST'])
@login_required
def analyze_file():
    """Send a file to the configured AI service for analysis.
    JSON body: { "path": "relative/path/to/file", "prompt": "optional custom prompt" }
    """
    data = request.get_json()
    user_dir = _get_user_dir(current_user.login)
    target = _safe_subpath(user_dir, data.get('path', ''))

    if not target or not os.path.isfile(target):
        return jsonify({'success': False, 'error': 'File not found'}), 404

    # Read file content
    text = _read_file_text(target)
    if text.startswith('[') and text.endswith(']'):
        return jsonify({'success': False, 'error': text}), 400

    # Get AI service - allow inline api_key override
    from license_tracker.utils.ai_service import get_ai_service, OpenAIService
    inline_key = data.get('api_key', '').strip()
    if inline_key:
        # User provided a key inline; use it directly with OpenAI
        model = AppSettings.get_setting('openai_model', 'gpt-4o-mini')
        service, err = OpenAIService(inline_key, model), None
    else:
        service, err = get_ai_service()
    if not service:
        return jsonify({'success': False, 'error': 'AI not configured: ' + (err or 'Unknown'), 'needs_key': True}), 400

    prompt = data.get('prompt', 'Analyze this license document and extract: vendor names, feature names, license counts, costs per license, billing periods, and any expiry dates. Provide a structured summary.')

    result = service.analyze_document(text, prompt)
    return jsonify(result)


@costing_blueprint.route('/ai/test', methods=['POST'])
@login_required
def test_ai_connection():
    """Test the current AI service connection."""
    from license_tracker.utils.ai_service import get_ai_service
    service, err = get_ai_service()
    if not service:
        return jsonify({'success': False, 'error': err or 'AI not configured'}), 400
    return jsonify(service.test_connection())


# ============ License Costs CRUD ============

@costing_blueprint.route('/costs', methods=['GET'])
@login_required
def get_costs():
    """Get all license costs."""
    costs = LicenseCost.query.order_by(LicenseCost.vendor, LicenseCost.feature).all()
    return jsonify({'success': True, 'costs': [c.to_dict() for c in costs]})


@costing_blueprint.route('/costs', methods=['POST'])
@login_required
def create_cost():
    """Create or update a license cost entry.
    JSON body: { vendor, feature, cost_per_license, currency, billing_period, notes }
    """
    data = request.get_json()
    vendor = data.get('vendor', '').strip()
    feature = data.get('feature', '').strip()
    if not vendor or not feature:
        return jsonify({'success': False, 'error': 'Vendor and feature are required'}), 400

    existing = LicenseCost.query.filter_by(vendor=vendor, feature=feature).first()
    if existing:
        existing.cost_per_license = float(data.get('cost_per_license', existing.cost_per_license))
        existing.currency = data.get('currency', existing.currency)
        existing.billing_period = data.get('billing_period', existing.billing_period)
        existing.notes = data.get('notes', existing.notes)
        db.session.commit()
        return jsonify({'success': True, 'cost': existing.to_dict()})

    cost = LicenseCost(
        vendor=vendor,
        feature=feature,
        cost_per_license=float(data.get('cost_per_license', 0)),
        currency=data.get('currency', 'USD'),
        billing_period=data.get('billing_period', 'annual'),
        notes=data.get('notes', ''),
    )
    db.session.add(cost)
    db.session.commit()
    return jsonify({'success': True, 'cost': cost.to_dict()}), 201


@costing_blueprint.route('/costs/<int:cost_id>', methods=['PUT'])
@login_required
def update_cost(cost_id):
    """Update a license cost entry."""
    cost = LicenseCost.query.get(cost_id)
    if not cost:
        return jsonify({'success': False, 'error': 'Not found'}), 404

    data = request.get_json()
    if 'cost_per_license' in data:
        cost.cost_per_license = float(data['cost_per_license'])
    if 'currency' in data:
        cost.currency = data['currency']
    if 'billing_period' in data:
        cost.billing_period = data['billing_period']
    if 'notes' in data:
        cost.notes = data['notes']
    if 'vendor' in data:
        cost.vendor = data['vendor']
    if 'feature' in data:
        cost.feature = data['feature']

    db.session.commit()
    return jsonify({'success': True, 'cost': cost.to_dict()})


@costing_blueprint.route('/costs/<int:cost_id>', methods=['DELETE'])
@login_required
def delete_cost(cost_id):
    """Delete a license cost entry."""
    cost = LicenseCost.query.get(cost_id)
    if not cost:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    db.session.delete(cost)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted'})


@costing_blueprint.route('/costs/summary', methods=['GET'])
@login_required
def cost_summary():
    """Get cost summary - total annual costs per vendor, overall total."""
    costs = LicenseCost.query.all()
    vendor_totals = {}
    grand_total = 0.0

    for c in costs:
        annual = c.cost_per_license
        if c.billing_period == 'monthly':
            annual = c.cost_per_license * 12
        elif c.billing_period == 'perpetual':
            annual = c.cost_per_license  # one-time, show as-is

        if c.vendor not in vendor_totals:
            vendor_totals[c.vendor] = {'vendor': c.vendor, 'total': 0.0, 'count': 0, 'currency': c.currency}
        vendor_totals[c.vendor]['total'] += annual
        vendor_totals[c.vendor]['count'] += 1
        grand_total += annual

    return jsonify({
        'success': True,
        'vendors': list(vendor_totals.values()),
        'grand_total': round(grand_total, 2),
    })
