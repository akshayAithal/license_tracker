#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""idash_connector application server definition."""

# pylint: disable=no-member

import os
import warnings

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from license_tracker.models import db
from license_tracker.logger import install_logger, logger
from license_tracker.extensions import migrate
from license_tracker.extensions import login_manager
from flask_apscheduler import APScheduler

def create_app(config_filename=None, config=None):
    """Application factory function that returns the flask app
    with the configs loaded correctly.
    
    For secret key, use os.urandom(32). Don't put the function into the file.
    Open an interpreter, calculate this value and put that value into the file
    as a string.

    Protip: If something does not work, try accessing this in incognito mode.

    Args:
        config_filename: Path to a config file. This can be
            relative to the instance folder.
        config: This is the name of one of the configs that should be loaded.
            This is loaded from the config file. Example: config='test' will
            load test.py

    """
    app = Flask(
        __name__,
        static_folder="ui/assets",
        template_folder="ui",
        instance_relative_config=True)
    if config_filename:
        app.config.from_pyfile(config_filename)
    else:
        if os.environ.get("CFG_LOCATION"):
            app.config.from_envvar("CFG_LOCATION")
        else:
            warnings.warn(
                "Either set the CFG_LOCATION environment variable"
                "or provide the config_filename argument to the "
                "application factory function. The default configuration "
                "has been used, but the changes to the database are "
                "now stored in memory, which is not recommended.",
                UserWarning)
    logger.debug("SQLALCHEMY_DATABASE_URI = {}".format(app.config.get("SQLALCHEMY_DATABASE_URI")))
    install_logger(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    login_manager.init_app(app)
    login_manager.login_view = "license.login"
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024    # 100 Mb limit
    from license_tracker.models.users import User
    @login_manager.user_loader
    def load_user(user_id):
       logger.debug(f"Attempting to load user #{user_id}")
       return User.query.filter(User.id_==user_id).first()
   
    from license_tracker.utils.license_history_data_utils import get_license_data, get_license_history_data
    scheduler = APScheduler()
    scheduler.api_enabled = True
    scheduler.init_app(app)
    @scheduler.task('interval', id='get_license', seconds=300, misfire_grace_time=900)
    def licensedata():
        with app.app_context():
            get_license_data()
    
    @scheduler.task('interval', id='license_details',hours=19, misfire_grace_time=900)
    def license_with_spent_hours():
        with app.app_context():
            get_license_history_data()
    
    scheduler.start()
    
    # from apscheduler.schedulers.background import BackgroundScheduler
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=get_license_data, trigger="interval", seconds=300)
    # scheduler.start()
    
    #from feedback_collector.api import process_blueprint
    # Configure CORS
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True,
            "max_age": 600
        },
        r"/license/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True,
            "max_age": 600
        }
    })
    
    # API health check endpoint
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'service': 'backend',
            'database': 'connected' if db.engine else 'disconnected'
        })
    
    #from feedback_collector.api import process_blueprint
    from license_tracker.api import license_blueprint,home_blueprint
    from license_tracker.api.admin import admin_blueprint
    app.register_blueprint(home_blueprint)
    app.register_blueprint(license_blueprint,url_prefix="/license")
    app.register_blueprint(admin_blueprint,url_prefix="/api/admin")
    return app
