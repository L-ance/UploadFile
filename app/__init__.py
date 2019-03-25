# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = False
# 实现csrf保护
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .auth import auth_blueprint
    from .show import show_blueprint
    from .main import main_blueprint
    from .turn import turn_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(show_blueprint, url_prefix='/show')
    app.register_blueprint(main_blueprint, url_prefix='/main')
    app.register_blueprint(turn_blueprint, url_prefix='/')

    return app
