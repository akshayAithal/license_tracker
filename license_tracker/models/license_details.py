
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from .db import db
from .user_type import UserType
from sqlalchemy.sql import func
from datetime import datetime

class LicenseDetail(UserMixin, db.Model):
    
    __tablename__ = "license_details"
    id_ = db.Column("id", db.Integer, primary_key=True)
    application = db.Column(db.String(16), nullable=True)
    region = db.Column(db.String(16), nullable=True)
    user = db.Column(db.String(64), nullable=False)
    host = db.Column(db.String(64), nullable=True)
    feature = db.Column(db.String(64), nullable=True)
    user_key = db.Column(db.String(64), nullable=True)
    license_used = db.Column(db.Integer, nullable=True)
    site_code = db.Column(db.String(16), nullable=True)
    check_out = db.Column(db.DateTime,  nullable=True)
    check_in = db.Column(db.DateTime,  nullable=True)
    spent_hours = db.Column(db.String(16), nullable=True)
    total_license = db.Column(db.Integer, nullable=True)
    total_license_used = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default = datetime.now())

    def __init__(self, application, region, user, host, feature, user_key, license_used, site_code, check_out, check_in, spent_hours, total_license, total_license_used):
        self.application = application
        self.region = region
        self.user = user
        self.host = host
        self.feature = feature
        self.user_key = user_key
        self.license_used = license_used
        self.total_license = total_license
        self.site_code = site_code
        self.check_out = check_out
        self.check_in = check_in
        self.spent_hours = spent_hours
        self.total_license_used = total_license_used
        self.created_at = datetime.now()
