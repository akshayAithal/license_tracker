#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .db import db
from datetime import datetime


class DashboardLayout(db.Model):
    """Stores per-user dashboard widget layouts (like Grafana)."""
    __tablename__ = "dashboard_layouts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('local_users.id'), nullable=False)
    layout_name = db.Column(db.String(64), default='default')
    layout_json = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'layout_name', name='uq_user_layout'),
    )

    def __init__(self, user_id, layout_json, layout_name='default', is_default=True):
        self.user_id = user_id
        self.layout_json = layout_json
        self.layout_name = layout_name
        self.is_default = is_default

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'layout_name': self.layout_name,
            'layout_json': self.layout_json,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
