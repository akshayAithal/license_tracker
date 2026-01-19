#!/usr/bin/env python
# -*- coding: utf-8 -*-

from license_tracker.models import db


class RedmineUser(db.Model):
    """Class for the users table."""
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "users"
    id_ = db.Column("id", db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255))
    status = db.Column(db.Integer)
    admin = db.Column(db.String)
    auth_source_id = db.Column(db.Integer)
    last_login_on = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime)
    easy_system_flag = db.Column(db.Integer)
    groups = db.relationship(
        "Groups_User",
        primaryjoin="Groups_User.user_id == RedmineUser.id_")

    def __repr__(self):
        return "<User : {}, {} [{}:{}]>".format(
            self.lastname, self.firstname, self.id, self.login)

    def get_groups(self):
        return [group.group for group in self.groups]

from sqlalchemy.orm import relationship

from license_tracker.models import db

class Groups_User(db.Model):
    __bind_key__ = "easyredmine"    
    __tablename__ = "groups_users"
    group_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    group = db.relationship("RedmineUser", foreign_keys=group_id)
    user = db.relationship("RedmineUser", foreign_keys=user_id)

    def __repr__(self):
        return "<Groups_User : {} : {}>".format(self.group.lastname, self.user.login)