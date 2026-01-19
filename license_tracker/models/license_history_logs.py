
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from .db import db
from .user_type import UserType
from sqlalchemy.sql import func
from datetime import datetime

class LicenseHistoryLog(UserMixin, db.Model):
    
    __tablename__ = "license_history_logs"
    id_ = db.Column("id", db.Integer, primary_key=True)
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
    license_used = db.Column(db.Integer, nullable=True)
    site_code = db.Column(db.String(16), nullable=True)
    total_license = db.Column(db.Integer, nullable=True)
    total_license_used = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default = datetime.now())

    def __init__(self, application, region, user, server, host, software, feature, version, user_key, date_time, license_used, site_code, total_license, total_license_used):
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
        self.license_used = license_used
        self.site_code = site_code
        self.total_license = total_license
        self.total_license_used = total_license_used
        self.created_at = datetime.now()
