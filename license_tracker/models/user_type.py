#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

class UserType(Enum):
    """User types enum for the user column."""
    ADMIN = 0
    USER = 1