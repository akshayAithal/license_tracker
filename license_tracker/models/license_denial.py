#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class LicenseDenial(db.Model):
    """Tracks license denial events when users are refused a license checkout."""
    __tablename__ = "license_denials"
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.String(16), nullable=True)
    region = db.Column(db.String(16), nullable=True)
    user = db.Column(db.String(64), nullable=False)
    host = db.Column(db.String(64), nullable=True)
    feature = db.Column(db.String(64), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    denied_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_license = db.Column(db.Integer, nullable=True)
    total_license_used = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, application, region, user, host, feature, reason,
                 denied_at=None, total_license=None, total_license_used=None):
        self.application = application
        self.region = region
        self.user = user
        self.host = host
        self.feature = feature
        self.reason = reason
        self.denied_at = denied_at or datetime.utcnow()
        self.total_license = total_license
        self.total_license_used = total_license_used
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'application': self.application,
            'region': self.region,
            'user': self.user,
            'host': self.host,
            'feature': self.feature,
            'reason': self.reason,
            'denied_at': self.denied_at.isoformat() if self.denied_at else None,
            'total_license': self.total_license,
            'total_license_used': self.total_license_used,
        }
