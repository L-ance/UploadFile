import datetime
import hashlib
import os
import time
import configparser

from flask import request, session, url_for, render_template
from flask_login import login_required, logout_user, login_user
from werkzeug.utils import redirect
from flask import jsonify
from app.auth import auth_blueprint
from app.models import User
from app.operat_db import operate_db, gatekeeper_db
from app.myconfig.myconfig import MyConfigParser
from app import Config
from threading import Lock

login_user_list = []


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    res = ProductionConfig.product_message()
    PLATFORM = Config.PLATFORM


    lock = Lock()
    login_cnt = 0
    lock_time = 0
    global login_user_list


    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        destip = request.host_url.split(':')[1].split('//')[1]
        destport = request.host_url.split(':')[2].split('/')[0]

        if not username or not password:
            return jsonify({"status": 2, "msg": "请输入用户名和密码"})

        file_obj = request.files.get("authorized_file", None)
        if not file_obj:
            return jsonify({"status": 2, "msg": "请上传文件"})

        try:
            cert_key = hashlib.new('md5', file_obj.getvalue()).hexdigest().lower()

        except Exception as e:
            print(e)
            return jsonify({"status": 2, "msg": "文件不合法"})

        ip = get_request_ip()
        user_info_list = UserInfoConfig.get_user(username)

        if not user_info_list:
            if PLATFORM == 0:
                operate_db(username, ip, result='login_error')

            else:
                isout = False
                gatekeeper_db('用户认证', username, ip, destip, destport, '登录', username, '失败', isout, '用户名不存在')

            return jsonify({"status": 2, "msg": "用户名不存在"})

        for user_info in user_info_list:
            if username in user_info:
                begin_data = user_info.get('begin', None)
                upp_pwd = user_info.get('update_time', None)

                if begin_data:
                    # 光闸的登陆逻辑
                    login_date = datetime.datetime.now().strftime('%Y-%m-%d')
                    end_data = user_info.get('end', None)

                    if login_date < begin_data or login_date > end_data:
                        operate_db(username, ip, result='login_error')
                        return jsonify({"status": 2, "msg": "密码已失效,联系管理员修改密码"})

                if upp_pwd:
                    # 网闸的登陆逻辑
                    login_date = datetime.datetime.now()
                    pwd_day = user_info.get('pwd_day', None)
                    login_cnt = user_info.get('login_cnt', None)
                    lock_time = user_info.get('lock_time', None)

                    upp_pwd = datetime.datetime.strptime(upp_pwd, '%Y-%m-%d %H:%M:%S')

                    if login_date - datetime.timedelta(days=int(pwd_day)) > upp_pwd:
                        isout = False
                        gatekeeper_db('用户认证', username, ip, destip, destport, '登录', username, '失败', isout, '密码已失效')
                        return jsonify({"status": 2, "msg": "密码已失效,联系管理员修改密码"})

                if login_user_list:
                    for try_login in login_user_list:
                        if username in try_login and try_login["login_cnt"] >= int(login_cnt):
                            last_login_time = try_login["try_login_time"] + int(lock_time) * 60
                            time_now = time.time()
                            if time_now >= last_login_time:
                                lock.acquire()
                                login_user_list.remove(try_login)
                                lock.release()
                            else:
                                time_sleep = last_login_time - time_now

                                return jsonify({"status": 2, "msg": "账号被锁定%d秒后重试" % round(time_sleep, 0)})

                if password == user_info.get("password") and cert_key == user_info.get("cert_key"):
                    level = user_info.get("level")
                    user = User(username)
                    login_user(user)

                    session["username"] = username
                    session["id"] = user.id
                    session["level"] = level
                    session["login_time"] = time.time() * 1000
                    session["ip"] = ip
                    session["destip"] = destip
                    session["destport"] = destport

                    conf1 = MyConfigParser()
                    count = 0
                    conf1.add_section('MAIN')

                    while True:
                        ip_section = 'IP{}'.format(count)
                        conf1.read(Config.IPAUTHCONF, encoding='gbk')
                        session['ip_section'] = ip_section

                        if not conf1.has_section(ip_section):
                            conf1.add_section(ip_section)

                        if not conf1.has_option(ip_section, 'Name'):
                            conf1[ip_section]['Name'] = ''
                            write_conf(ip_section, username, level, ip, destip, destport, conf1)
                            break
                        else:
                            if conf1.get(ip_section, 'Name') == username:
                                write_conf(ip_section, username, level, ip, destip, destport, conf1)
                                break
                            else:
                                count += 1

                    conf1.set('MAIN', 'Num', '{}'.format(count + 1))
                    with open(Config.IPAUTHCONF, 'w') as f:
                        conf1.write(f)
                    if PLATFORM == 0:
                        operate_db(username, ip, result='login_success')
                    else:
                        isout = False
                        gatekeeper_db('用户认证', username, ip, destip, destport, '登录', username, '成功', isout, '登录成功')

                    # 登录成功执行该脚本
                    os.system(Config.LOGIN_COMMAND.format(ip, 'I'))

                    if session.get("username"):
                        path = os.path.join(Config.BASE_DIR, username)
                        if not os.path.exists(path):
                            os.mkdir(path)

                    return jsonify({'url': url_for('show.index')})

                else:
                    if PLATFORM == 0:
                        operate_db(username, ip, result='login_error')
                    else:

                        if login_user_list:
                            for try_login in login_user_list:
                                if username not in try_login:
                                    try_login_time = time.time()
                                    dic = {username: username, "login_cnt": 1, "try_login_time": try_login_time}
                                    lock.acquire()
                                    login_user_list.append(dic)
                                    lock.release()

                                try_login["login_cnt"] = try_login["login_cnt"] + 1
                                try_login["try_login_time"] = time.time()

                        else:
                            try_login_time = time.time()
                            dic = {username: username, "login_cnt": 1, "try_login_time": try_login_time}
                            lock.acquire()
                            login_user_list.append(dic)
                            lock.release()

                        isout = False
                        gatekeeper_db('用户认证', username, ip, destip, destport, '登录', username, '失败', isout, '密码或者校验文件失败')

                    return jsonify({"status": 2, "msg": "密码或者校验文件失败"})

    return render_template('login.html', res=res)


@auth_blueprint.route('/logout')
@login_required
def logout():
    """
    登出函数
    :return: 跳转登录页面
    """
    PLATFORM = Config.PLATFORM
    ip = get_request_ip()
    destip = session.get('destip')
    destport = session.get('destport')
    opuser = session.get('username')
    if PLATFORM == 0:
        operate_db(opuser, ip, result='logout_success')  # 登出成功记入数据库
    else:
        isout = False
        gatekeeper_db('用户认证', opuser, ip, destip, destport, '登出', opuser, '成功', isout, '登出成功')
    logout_user()

    conf2 = MyConfigParser()
    conf2.read(Config.IPAUTHCONF, encoding='gbk')
    ip_section = session.get('ip_section')

    conf2.remove_section(ip_section)
    num = conf2.getint('MAIN', 'Num') - 1
    conf2.set('MAIN', 'Num', str(num))

    with open(Config.IPAUTHCONF, 'w', encoding='gbk') as f:
        conf2.write(f)

    # 登出成功执行该命令
    os.system(Config.LOGIN_COMMAND.format(ip, 'D'))
    return redirect(url_for('auth.login'))


@auth_blueprint.route('/online/', methods=['GET'])
@login_required
def online():
    """
    在线时长
    :return:
    """
    return jsonify({"online": session.get('login_time')})


@auth_blueprint.route('/verpro/', methods=['GET'])
@login_required
def verpro():
    return jsonify(ProductionConfig.product_message())


def get_request_ip():
    # 获取请求的ip
    try:
        ip = request.remote_addr
        return ip
    except Exception as e:
        print(e)


def write_conf(ip_section, uname, level, ip, destip, destport, conf1):
    # 写配置文件
    login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lst = [('Name', uname), ('Level', '{}'.format(int(level))), ('IP', ip), ('SrcPort', ''),
           ('DestIp', destip), ('DestPort', destport), ('LGTime', login_time), ('UTime', login_time),
           ('TXTime', '')]
    for j in lst:
        conf1.set(ip_section, j[0], j[1])


@auth_blueprint.route('/upgrade_time/', methods=['GET'])
@login_required
def upgrade_time():
    conf3 = MyConfigParser()
    conf3.read(Config.IPAUTHCONF, encoding='gbk')

    username = session.get('username')
    ip_section = session.get('ip_section')
    try:
        if conf3.get(ip_section, 'Name') == username:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conf3.set(ip_section, 'UTime', time)
            with open(Config.IPAUTHCONF, 'w') as f:
                conf3.write(f)
        else:
            pass
    except Exception as e:
        print(e)
    return jsonify()


class ProductionConfig(Config):

    @classmethod
    def product_message(cls):
        if Config.PLATFORM == 1:
            res = cls.gatekeeper()
            return res
        else:
            res = cls.optical_shutter()
            return res

    @staticmethod
    def optical_shutter():
        dic = {}
        conf = configparser.ConfigParser()
        conf.read(Config.VERSION)
        devtype = conf.get('ROOT', 'devname')
        dic['devtype'] = devtype
        with open(Config.PRODUCT, 'r', encoding='utf8') as f:
            for line in f:
                if line.startswith("$config['SYS_VER'] = "):
                    version = line.split("$config['SYS_VER'] = ")[-1].split("'")[1].strip()
                    dic['version'] = version
                if line.startswith("$config['PDGAP_TITLE'] = "):
                    product = line.split("$config['PDGAP_TITLE'] = ")[-1].split("'")[1].strip()
                    dic['product'] = product
                if line.startswith("$config['PDGAP_COPYRIGHT'] = "):
                    bottom = line.split("$config['PDGAP_COPYRIGHT'] = ")[-1].split("'")[1].strip()
                    dic['bottom'] = bottom

        return dic

    @staticmethod
    def gatekeeper():
        dic = {}

        conf = configparser.ConfigParser()
        conf.read(Config.VERSION, encoding='gbk')
        version = conf.get('SYSTEM', 'ver')
        devtype = conf.get('SYSTEM', 'devtype')
        dic['version'] = version
        dic['devtype'] = devtype

        with open(Config.PRODUCT, 'r', encoding='utf8') as f:
            for line in f:
                if line.startswith("$config['PDGAP_TITLE'] = "):
                    product = line.split("$config['PDGAP_TITLE'] = ")[-1].split("'")[1].strip()
                    dic['product'] = product
                if line.startswith("$config['PDGAP_COPYRIGHT'] = "):
                    bottom = line.split("$config['PDGAP_COPYRIGHT'] = ")[-1].split("'")[1].strip()
                    dic['bottom'] = bottom

        return dic


class UserInfoConfig(Config):
    @classmethod
    def get_user(cls, user_input):
        if Config.PLATFORM == 1:
            return cls.gatekeeper_user(user_input)
        else:
            return cls.optical_shutter_user(user_input)

    @staticmethod
    def gatekeeper_user(user_input):
        user_list = []
        conf = configparser.ConfigParser()
        conf.read(Config.USER_FILE, encoding='gbk')
        user_number = conf.get('MAIN', 'num')
        if user_number:
            for i in range(int(user_number)):
                username = conf.get('USER{}'.format(i), 'name')
                if username == user_input:
                    password = conf.get('USER{}'.format(i), 'passwd').lower()
                    level = conf.get('USER{}'.format(i), 'type')
                    cert_key = conf.get('USER{}'.format(i), 'certkey')
                    update_time = conf.get('USER{}'.format(i), 'uppwdtime')
                    login_cnt = conf.get('MAIN', 'logincnt')
                    lock_time = conf.get('MAIN', 'locktime')
                    pwd_day = conf.get('MAIN', 'pwdday')
                    user_list.append({username: username, "password": password, "level": level, "cert_key": cert_key,
                                      "update_time": update_time, "login_cnt": login_cnt, "lock_time": lock_time,
                                      "pwd_day": pwd_day})

        return user_list

    @staticmethod
    def optical_shutter_user(user_input):
        user_list = []
        conf = configparser.ConfigParser()
        conf.read(Config.USER_FILE, encoding='gbk')
        user_number = conf.get('SYS', 'nusernum')
        if user_number:
            for i in range(int(user_number)):
                username = conf.get('NUSER{}'.format(i), 'uname')
                if username == user_input:
                    password = conf.get('NUSER{}'.format(i), 'upass').lower()
                    level = conf.get('NUSER{}'.format(i), 'level')
                    cert = conf.get('NUSER{}'.format(i), 'cert')
                    max_day = conf.get('NUSER{}'.format(i), 'max_days')
                    begin = conf.get('NUSER{}'.format(i), 'bdate')
                    end = conf.get('NUSER{}'.format(i), 'edate')
                    user_list.append(
                        {username: username, "password": password, "level": level, "cert_key": cert, "pwd_day": max_day,
                         "begin": begin, "end": end})

        return user_list
