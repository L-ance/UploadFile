# -*- coding: utf-8 -*-
from flask import redirect, url_for, session

from app.turn import turn_blueprint


@turn_blueprint.route('/', methods=['GET'])
def turn():
    if session.get('username'):
        return redirect(url_for('show.index'))
    return redirect(url_for('auth.login'))
