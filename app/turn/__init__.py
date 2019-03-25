# -*- coding: utf-8 -*-
from flask import Blueprint

turn_blueprint = Blueprint('turn', __name__)

from . import views

from .views import *
