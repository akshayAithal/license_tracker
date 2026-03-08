#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class LicenseCost(db.Model):
    """Model to store per-vendor per-feature license costs."""
    __tablename__ = "license_costs"
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(64), nullable=False)
    feature = db.Column(db.String(128), nullable=False)
    cost_per_license = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(8), default='USD')
    billing_period = db.Column(db.String(32), default='annual')  # annual, monthly, perpetual
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('vendor', 'feature', name='uq_vendor_feature'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'vendor': self.vendor,
            'feature': self.feature,
            'cost_per_license': self.cost_per_license,
            'currency': self.currency,
            'billing_period': self.billing_period,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
