"""Main application package."""

# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import os
from flask import Flask,  current_app
from config import app_config
from .extensions import db, login, migrate, bcrypt
from .api.restplus import api

def create_app(config_name):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    register_extensions(app)
    register_blueprints(app)
    
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app)    
                
    return None


def register_blueprints(app):
    """Register Flask Blueprints."""
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix = '/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix = '/main')

    from app.home import bp as home_bp
    app.register_blueprint(home_bp, url_prefix = '/home')
    
    return None




from app import models

