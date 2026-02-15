#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db
from .user_type import UserType
from datetime import datetime


# pylint: disable=no-member
class User(UserMixin, db.Model):
    """User model for use with flask_login."""
    __tablename__ = "local_users"
    id_ = db.Column("id", db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    type_ = db.Column("type", db.Enum(UserType), default=UserType.USER)
    site_code = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, login, type_=UserType.USER, site_code="", email=None, password=None):
        """Creates a new user."""
        self.login = login
        self.type_ = type_
        self.site_code = site_code
        self.email = email
        if password:
            self.set_password(password)

    def get_id(self):
        return self.id_

    def get_site_code(self):
        return self.site_code
    
    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.type_ == UserType.ADMIN
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id_,
            'login': self.login,
            'email': self.email,
            'type': self.type_.name if self.type_ else 'USER',
            'site_code': self.site_code,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
