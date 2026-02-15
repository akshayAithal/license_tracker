#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class AppSettings(db.Model):
    """Application settings model for storing configuration like LDAP settings."""
    __tablename__ = "app_settings"
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(64), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)
    setting_type = db.Column(db.String(32), default='string')
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, setting_key, setting_value, setting_type='string', description=None):
        self.setting_key = setting_key
        self.setting_value = setting_value
        self.setting_type = setting_type
        self.description = description

    def get_value(self):
        """Get the setting value with proper type conversion."""
        if self.setting_type == 'boolean':
            return self.setting_value.lower() == 'true'
        elif self.setting_type == 'integer':
            try:
                return int(self.setting_value)
            except (ValueError, TypeError):
                return 0
        return self.setting_value

    def to_dict(self):
        """Convert setting to dictionary."""
        return {
            'id': self.id,
            'key': self.setting_key,
            'value': self.setting_value,
            'type': self.setting_type,
            'description': self.description
        }

    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key."""
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if setting:
            return setting.get_value()
        return default

    @staticmethod
    def set_setting(key, value, setting_type='string', description=None):
        """Set a setting value, creating if it doesn't exist."""
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            if setting_type:
                setting.setting_type = setting_type
            if description:
                setting.description = description
        else:
            setting = AppSettings(
                setting_key=key,
                setting_value=str(value),
                setting_type=setting_type,
                description=description
            )
            db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def get_ldap_settings():
        """Get all LDAP-related settings as a dictionary."""
        ldap_keys = [
            'ldap_enabled', 'ldap_server', 'ldap_port', 'ldap_use_ssl',
            'ldap_bind_dn', 'ldap_bind_password', 'ldap_base_dn',
            'ldap_user_filter', 'ldap_username_attribute', 'ldap_email_attribute'
        ]
        settings = {}
        for key in ldap_keys:
            setting = AppSettings.query.filter_by(setting_key=key).first()
            if setting:
                settings[key] = setting.get_value()
            else:
                settings[key] = None
        return settings

    @staticmethod
    def get_all_settings():
        """Get all settings as a dictionary."""
        settings = AppSettings.query.all()
        return {s.setting_key: s.to_dict() for s in settings}
