#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Table definitions for the easyredmine database.
Note: For each table, ensure you set the
__bind_key__ = "easyredmine"

value. It doesn't need to be `easyredmine`, but
it needs to be the key which you give in your config file.

Additionally, the following needs to be set in your config.

``
SQLALCHEMY_BINDS = {
    "easyredmine": "mysql+pymysql://user:password@redmine.domain.com/databasename"
}

``
# """

# from .users import User
