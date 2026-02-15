#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from license_tracker.logger import logger
from license_tracker.models import db, User, UserType, AppSettings
from functools import wraps

admin_blueprint = Blueprint("admin", __name__)


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            logger.warning(f"Non-admin user {current_user.login} attempted admin access")
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ============ User Management ============

@admin_blueprint.route("/users", methods=["GET"])
@admin_required
def get_users():
    """Get all users."""
    users = User.query.all()
    return jsonify({
        "success": True,
        "users": [u.to_dict() for u in users]
    })


@admin_blueprint.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Get a specific user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    return jsonify({
        "success": True,
        "user": user.to_dict()
    })


@admin_blueprint.route("/users", methods=["POST"])
@admin_required
def create_user():
    """Create a new user."""
    data = request.get_json()
    
    if not data.get("login"):
        return jsonify({"success": False, "error": "Login is required"}), 400
    
    if User.query.filter_by(login=data["login"]).first():
        return jsonify({"success": False, "error": "User already exists"}), 400
    
    user_type = UserType.ADMIN if data.get("type") == "ADMIN" else UserType.USER
    
    user = User(
        login=data["login"],
        email=data.get("email"),
        type_=user_type,
        site_code=data.get("site_code", ""),
        password=data.get("password")
    )
    user.is_active = data.get("is_active", True)
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"Admin {current_user.login} created user {user.login}")
    
    return jsonify({
        "success": True,
        "user": user.to_dict()
    }), 201


@admin_blueprint.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """Update a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    data = request.get_json()
    
    if data.get("login") and data["login"] != user.login:
        if User.query.filter_by(login=data["login"]).first():
            return jsonify({"success": False, "error": "Login already in use"}), 400
        user.login = data["login"]
    
    if "email" in data:
        user.email = data["email"]
    
    if "type" in data:
        user.type_ = UserType.ADMIN if data["type"] == "ADMIN" else UserType.USER
    
    if "site_code" in data:
        user.site_code = data["site_code"]
    
    if "is_active" in data:
        user.is_active = data["is_active"]
    
    if data.get("password"):
        user.set_password(data["password"])
    
    db.session.commit()
    
    logger.info(f"Admin {current_user.login} updated user {user.login}")
    
    return jsonify({
        "success": True,
        "user": user.to_dict()
    })


@admin_blueprint.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    if user.id_ == current_user.id_:
        return jsonify({"success": False, "error": "Cannot delete yourself"}), 400
    
    login = user.login
    db.session.delete(user)
    db.session.commit()
    
    logger.info(f"Admin {current_user.login} deleted user {login}")
    
    return jsonify({"success": True, "message": f"User {login} deleted"})


# ============ Settings Management ============

@admin_blueprint.route("/settings", methods=["GET"])
@admin_required
def get_settings():
    """Get all application settings."""
    settings = AppSettings.get_all_settings()
    return jsonify({
        "success": True,
        "settings": settings
    })


@admin_blueprint.route("/settings/<key>", methods=["GET"])
@admin_required
def get_setting(key):
    """Get a specific setting."""
    setting = AppSettings.query.filter_by(setting_key=key).first()
    if not setting:
        return jsonify({"success": False, "error": "Setting not found"}), 404
    return jsonify({
        "success": True,
        "setting": setting.to_dict()
    })


@admin_blueprint.route("/settings", methods=["PUT"])
@admin_required
def update_settings():
    """Update multiple settings at once."""
    data = request.get_json()
    
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid data"}), 400
    
    updated = []
    for key, value in data.items():
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            updated.append(key)
        else:
            new_setting = AppSettings(
                setting_key=key,
                setting_value=str(value),
                setting_type='string'
            )
            db.session.add(new_setting)
            updated.append(key)
    
    db.session.commit()
    
    logger.info(f"Admin {current_user.login} updated settings: {updated}")
    
    return jsonify({
        "success": True,
        "updated": updated
    })


@admin_blueprint.route("/settings/<key>", methods=["PUT"])
@admin_required
def update_setting(key):
    """Update a specific setting."""
    data = request.get_json()
    
    if "value" not in data:
        return jsonify({"success": False, "error": "Value is required"}), 400
    
    setting = AppSettings.set_setting(
        key=key,
        value=data["value"],
        setting_type=data.get("type", "string"),
        description=data.get("description")
    )
    
    logger.info(f"Admin {current_user.login} updated setting {key}")
    
    return jsonify({
        "success": True,
        "setting": setting.to_dict()
    })


# ============ LDAP Settings ============

@admin_blueprint.route("/ldap/settings", methods=["GET"])
@admin_required
def get_ldap_settings():
    """Get LDAP configuration settings."""
    settings = AppSettings.get_ldap_settings()
    return jsonify({
        "success": True,
        "ldap_settings": settings
    })


@admin_blueprint.route("/ldap/settings", methods=["PUT"])
@admin_required
def update_ldap_settings():
    """Update LDAP configuration settings."""
    data = request.get_json()
    
    ldap_settings = {
        'ldap_enabled': ('boolean', 'Enable LDAP authentication'),
        'ldap_server': ('string', 'LDAP server URL'),
        'ldap_port': ('integer', 'LDAP server port'),
        'ldap_use_ssl': ('boolean', 'Use SSL for LDAP connection'),
        'ldap_bind_dn': ('string', 'LDAP bind DN'),
        'ldap_bind_password': ('string', 'LDAP bind password'),
        'ldap_base_dn': ('string', 'LDAP base DN for user search'),
        'ldap_user_filter': ('string', 'LDAP user search filter'),
        'ldap_username_attribute': ('string', 'LDAP attribute for username'),
        'ldap_email_attribute': ('string', 'LDAP attribute for email')
    }
    
    updated = []
    for key, (setting_type, description) in ldap_settings.items():
        if key in data:
            AppSettings.set_setting(key, data[key], setting_type, description)
            updated.append(key)
    
    logger.info(f"Admin {current_user.login} updated LDAP settings: {updated}")
    
    return jsonify({
        "success": True,
        "updated": updated,
        "ldap_settings": AppSettings.get_ldap_settings()
    })


@admin_blueprint.route("/ldap/test", methods=["POST"])
@admin_required
def test_ldap_connection():
    """Test LDAP connection with current settings."""
    try:
        import ldap3
        from ldap3 import Server, Connection, ALL
        
        settings = AppSettings.get_ldap_settings()
        
        if not settings.get('ldap_server'):
            return jsonify({
                "success": False,
                "error": "LDAP server not configured"
            }), 400
        
        use_ssl = settings.get('ldap_use_ssl', False)
        port = settings.get('ldap_port', 636 if use_ssl else 389)
        
        server = Server(
            settings['ldap_server'],
            port=port,
            use_ssl=use_ssl,
            get_info=ALL
        )
        
        conn = Connection(
            server,
            user=settings.get('ldap_bind_dn'),
            password=settings.get('ldap_bind_password'),
            auto_bind=True
        )
        
        conn.unbind()
        
        logger.info(f"Admin {current_user.login} tested LDAP connection - success")
        
        return jsonify({
            "success": True,
            "message": "LDAP connection successful"
        })
        
    except ImportError:
        return jsonify({
            "success": False,
            "error": "ldap3 library not installed"
        }), 500
    except Exception as e:
        logger.error(f"LDAP connection test failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Connection failed: {str(e)}"
        }), 400


# ============ Auth Settings ============

@admin_blueprint.route("/auth/settings", methods=["GET"])
@admin_required
def get_auth_settings():
    """Get authentication settings."""
    return jsonify({
        "success": True,
        "auth_settings": {
            "auth_mode": AppSettings.get_setting('auth_mode', 'local'),
            "ldap_enabled": AppSettings.get_setting('ldap_enabled', False),
            "redmine_auth_enabled": AppSettings.get_setting('redmine_auth_enabled', False),
            "registration_enabled": AppSettings.get_setting('registration_enabled', True)
        }
    })


@admin_blueprint.route("/auth/settings", methods=["PUT"])
@admin_required
def update_auth_settings():
    """Update authentication settings."""
    data = request.get_json()
    
    auth_settings = {
        'auth_mode': ('string', 'Authentication mode: local, ldap, or redmine'),
        'ldap_enabled': ('boolean', 'Enable LDAP authentication'),
        'redmine_auth_enabled': ('boolean', 'Enable Redmine/ERM authentication'),
        'registration_enabled': ('boolean', 'Allow new user registration')
    }
    
    updated = []
    for key, (setting_type, description) in auth_settings.items():
        if key in data:
            AppSettings.set_setting(key, data[key], setting_type, description)
            updated.append(key)
    
    logger.info(f"Admin {current_user.login} updated auth settings: {updated}")
    
    return jsonify({
        "success": True,
        "updated": updated
    })


# ============ Current User Info ============

@admin_blueprint.route("/current-user", methods=["GET"])
@login_required
def get_current_user():
    """Get current logged-in user info."""
    return jsonify({
        "success": True,
        "user": current_user.to_dict(),
        "is_admin": current_user.is_admin()
    })
