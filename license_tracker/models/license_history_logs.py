
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class LicenseHistoryLog(db.Model):
    """Completed license usage records. Created when a license is checked
    back in (moved from license_details)."""
    __tablename__ = "license_history_logs"
    id_ = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('local_users.id'), nullable=True)
    application = db.Column(db.String(16), nullable=True)
    region = db.Column(db.String(16), nullable=True)
    user = db.Column(db.String(64), nullable=False)
    server = db.Column(db.String(64), nullable=True)
    host = db.Column(db.String(64), nullable=True)
    software = db.Column(db.String(64), nullable=True)
    feature = db.Column(db.String(64), nullable=True)
    version = db.Column(db.String(64), nullable=True)
    user_key = db.Column(db.String(64), nullable=True)
    date_time = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    check_in = db.Column(db.DateTime, nullable=True)
    spent_hours = db.Column(db.String(16), nullable=True)
    license_used = db.Column(db.Integer, nullable=True)
    site_code = db.Column(db.String(16), nullable=True)
    total_license = db.Column(db.Integer, nullable=True)
    total_license_used = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_history_user_id', 'user_id'),
        db.Index('idx_history_datetime', 'date_time'),
        db.Index('idx_history_app_feature', 'application', 'feature'),
    )

    # ORM relationship
    owner = db.relationship('User', backref=db.backref('license_history', lazy='dynamic'))

    def __init__(self, application, region, user, server, host, software, feature, version, user_key, date_time, license_used, site_code, total_license, total_license_used, user_id=None, check_out=None, check_in=None, spent_hours=None):
        self.user_id = user_id
        self.application = application
        self.region = region
        self.user = user
        self.server = server
        self.host = host
        self.software = software
        self.feature = feature
        self.version = version
        self.user_key = user_key
        self.date_time = date_time
        self.check_out = check_out
        self.check_in = check_in
        self.spent_hours = spent_hours
        self.license_used = license_used
        self.site_code = site_code
        self.total_license = total_license
        self.total_license_used = total_license_used
        self.created_at = datetime.utcnow()
