# -*- coding: utf-8 -*-
from flask import Blueprint
from app import Config

show_blueprint = Blueprint('show', __name__)
view = ['wang_view']
if Config.PLATFORM == 1:
    from . import wang_view
    from .wang_view import *
if Config.PLATFORM == 0:
    from . import guang_view
    from .guang_view import *
