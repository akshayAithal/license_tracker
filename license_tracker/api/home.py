#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint


home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def index():
    """Serve the ReactJS-based index.html"""
    from flask import render_template
    return render_template("home.html")
