# -*- coding: utf-8 -*-
import datetime
import hashlib
import os
import time
import configparser

from flask import request, session, url_for, render_template
from flask_login import login_required, logout_user, login_user
from werkzeug.utils import redirect
from flask import jsonify
from config import Config
from app.auth import auth_blueprint
from app.models import User


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        uname = request.form.get('username', None)
        pword = request.form.get('password', None)

        if not uname or not pword:
            msg = '请输入用户名和密码'
            return render_template('login.html', msg=msg)

        file_obj = request.files.get('authorized_file', None)
        login_date = datetime.datetime.now().strftime('%Y-%m-%d')

        conf = configparser.ConfigParser()  # 实例化对象
        conf.read('BConfig.cfg', encoding='gbk')  # 以gbk, 读取配置文件, 直接读取BConfig.cfg的文件内容
        nusernum = conf.getint('SYS', 'NUSERNUM')  # 获取指定的SYS下的NUSERNUM对应的值

        section_lst = []
        dic = {}  # 每一个用户的信息以键值对形式存在该字典中
        user_dic = {}  # 将每一个用户的用户名做key,对应的用户信息字典做value 如 bdic = {'user1':{}, 'user2':{}}

        for i in range(nusernum):
            section = 'NUSER{}'.format(i)
            section_lst.append(section)

        for section in section_lst:
            items = conf.items(section)  # 获取指定section下所有的键值对
            # 取到每一个section下的用户名, 密码, 有效期, 授权文件加密后的MD5

            for i in items:
                dic[i[0]] = i[1]
            username = dic.get('uname')
            user_dic[username] = dic

            if uname == username:
                password = user_dic.get(uname).get('upass')
                begin_date = user_dic.get(uname).get('bdate')
                end_date = user_dic.get(uname).get('edate')
                cert = user_dic.get(uname).get('cert').lower()
                level = user_dic.get(uname).get('level')

                if login_date < begin_date or login_date > end_date:  # 判断是否在有效期
                    msg = '未在有效期内, 请重新登录'
                    return render_template('login.html', msg=msg)

                try:
                    b_data = file_obj.getvalue()  # 拿到文件的二进制数据流
                    data_md5 = hashlib.new('md5', b_data).hexdigest().lower()  # 对文件的二进制数据流进行MD5加密

                    if uname == username and pword == password and data_md5 == cert:
                        user = User(username)
                        login_user(user)
                        session['username'] = user.username
                        session['id'] = user.id
                        session['level'] = level
                        session['login_time'] = time.time() * 1000

                        if session.get("username"):
                            path = Config.BASE_DIR + '/' + username
                            if not os.path.exists(path):
                                os.mkdir(Config.BASE_DIR + '/{}'.format(username))

                        return redirect(url_for('show.index'))

                    else:
                        msg = '用户名或密码或文件内容错误,请重新登录'
                        return render_template('login.html', msg=msg)
                except Exception as e:
                    print(e)
                    msg = '未上传文件,请重新上传'
                    return render_template('login.html', msg=msg)

    return render_template('login.html')


@auth_blueprint.route('/logout')
@login_required
def logout():
    """
    登录函数
    :return: 跳转登录页面
    """
    logout_user()
    return redirect(url_for('auth.login'))


@auth_blueprint.route('/online/')
@login_required

def online():
    return jsonify({"online": session.get('login_time')})
