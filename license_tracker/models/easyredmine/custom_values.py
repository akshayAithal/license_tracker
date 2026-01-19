#!/usr/bin/env python
# -*- coding: utf-8 -*-

from license_tracker.models import db


class CustomValue(db.Model):
    # pylint: disable=no-member
    __bind_key__ = "easyredmine"
    __tablename__ = "custom_values"
    id_ = db.Column("id", db.Integer, primary_key=True)
    customized_type = db.Column(db.String(30), nullable=False)
    # key of the project / Issue etc
    customized_id = db.Column(db.Integer, nullable=False)
    custom_field_id = db.Column(db.Integer, db.ForeignKey("custom_fields.id"))
    custom_field = db.relationship("CustomField")
    value = db.Column(db.Text)

    def __repr__(self):
        return "<Custom Value : {}: {} : [{}]>".format(
            self.custom_field.name, repr(self.value), self.id_)
