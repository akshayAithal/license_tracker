#!/usr/bin/env python
# -*- coding: utf-8 -*-

from license_tracker.models import db


class CustomField(db.Model):
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "custom_fields"
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    type_ = db.Column("type", db.String(255), nullable=False)

    def __repr__(self):
        return "<CustomField {} : {}: [{}]>".format(
            self.type, self.name, self.id)
