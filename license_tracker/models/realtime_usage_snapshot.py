#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class RealtimeUsageSnapshot(db.Model):
    """Periodic snapshots of license usage taken every 5 minutes by the scheduler."""
    __tablename__ = "realtime_usage_snapshots"
    id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.String(16), nullable=False)
    region = db.Column(db.String(16), nullable=True)
    feature = db.Column(db.String(64), nullable=True)
    total_license = db.Column(db.Integer, nullable=True)
    used_license = db.Column(db.Integer, nullable=True)
    snapshot_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, application, region, feature, total_license, used_license,
                 snapshot_time=None):
        self.application = application
        self.region = region
        self.feature = feature
        self.total_license = total_license
        self.used_license = used_license
        self.snapshot_time = snapshot_time or datetime.utcnow()
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'application': self.application,
            'region': self.region,
            'feature': self.feature,
            'total_license': self.total_license,
            'used_license': self.used_license,
            'snapshot_time': self.snapshot_time.isoformat() if self.snapshot_time else None,
        }
