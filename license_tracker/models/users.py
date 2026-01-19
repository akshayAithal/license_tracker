#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from .db import db
from .user_type import UserType



# pylint: disable=no-member
class User(UserMixin, db.Model):
    """User model for use with flask_login."""
    __tablename__ = "local_users"
    id_ = db.Column("id", db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    type_ = db.Column("type", db.Enum(UserType), default=UserType.USER)
    site_code = db.Column(db.String(255), nullable=True)

    def __init__(self, login, type_, site_code):
        """Creates a new user."""
        self.login = login
        self.type_ = type_
        self.site_code = site_code

    def get_id(self):
        return self.id_

    def get_site_code(self):
        return self.site_code
    
