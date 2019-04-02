# -*- coding: utf-8 -*-
import json
import time
import os

from flask import render_template, session, request, jsonify, redirect, url_for
from flask_login import login_required

from app import login_manager
from app.show import show_blueprint
from config import Config
from app.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@show_blueprint.route('/')
@login_required
def index():
    username = session.get('username')
    ip = session.get('ip')
    # http_sta = session.get('http')
    # ftp_sta = session.get('ftp')
    # file_sta = session.get('file')
    # return render_template('authentication.html', username=username, ip=ip, http_sta=http_sta, ftp_sta=ftp_sta,
    #                        file_sta=file_sta)
    return render_template('authentication.html', username=username, ip=ip)


@show_blueprint.route('/file')
@login_required
def file():
    """
    首页函数(展示公共和私有)
    :return:
    """
    username = session.get('username')
    public_dirs = os.path.split(Config.UPLODAG_PATH)[1]
    private_dirs = None
    if username:
        private_dirs = username

    return render_template('wang_upload.html', public_dirs=public_dirs, private_dirs=private_dirs, username=username)


"""
@show_blueprint.route('/strategy')
@login_required
def strategy():
    http_sta = request.args.get('http')
    ftp_sta = request.args.get('ftp')
    file_sta = request.args.get('file')

    session['http'] = http_sta
    session['ftp'] = ftp_sta
    session['file'] = file_sta

    username = session.get('username')
    ip = session.get('ip')
    return render_template('authentication.html', username=username, ip=ip, http_sta=http_sta, ftp_sta=ftp_sta,
                           file_sta=file_sta)

"""


@show_blueprint.route('/public', methods=['GET', 'POST'])
@login_required
def public():
    """
    公共区的接口函数
    :return: jsonfy
    """
    dic = {}

    file_size_lst = []
    file_modify_time_lst = []
    folder_lst = []
    file_name_lst = []
    file_type_lst = []
    file_level_lst = []
    all_file_msg = []
    file_dic = {}

    level = session.get('level')

    folder_name = request.args.get("dir")

    if folder_name:
        path = Config.BASE_DIR + '/' + folder_name

    else:
        path = Config.UPLODAG_PATH

    file_lst = get_file_name(path)
    if file_lst:

        folder_lst = file_lst[1]
        file_path_lst = [folder_name + i for i in file_lst[2]]
        # print(file_path_lst)
        with open(Config.PERMISSION_FILE, "r")as f:
            for line in f:
                if line:
                    ret = json.loads(line)
                    all_file_msg.append(ret)
        # print(all_file_msg)

        for filename in file_path_lst:
            for file_msg in all_file_msg:
                if filename in file_msg and int(level) >= int(file_msg['level']):
                    if filename not in file_dic:
                        file_dic[filename] = file_msg[filename]

                        file_name_lst.append(file_dic[filename])
                        file_type_lst.append(get_file_type(filename))
                        file_level_lst.append(int(file_msg['level']))

        for file in file_name_lst:
            file_path = path + "/" + file
            file_size = get_file_size(file_path)
            modify_time = get_file_modify_time(file_path)
            file_size_lst.append(file_size)
            file_modify_time_lst.append(modify_time)

    # dic['path_name'] = path_name
    dic['dir'] = folder_lst
    dic['file'] = file_name_lst
    dic['file_size'] = file_size_lst
    dic['file_type'] = file_type_lst
    dic['file_level'] = file_level_lst
    dic['modify_time'] = file_modify_time_lst

    return jsonify(dic)


@show_blueprint.route("/private", methods=['GET', 'POST'])
@login_required
def private():
    """
    私有区接口
    :return: jsonfy
    """
    folder_lst = []
    file_name_lst = []

    dic = {}
    file_size_lst = []
    file_type_lst = []

    file_modify_time_lst = []

    username = session.get('username')
    if username:
        path = Config.BASE_DIR

        if not os.path.exists(path):
            os.mkdir(Config.BASE_DIR + '/{}'.format(username))
        folder_name = request.args.get("dir")

        if folder_name:
            path = path + '/' + folder_name
        else:
            path = path

        # print(path)
        file_lst = get_file_name(path)
        # ([文件路径],[文件夹],[文件名])
        if file_lst:
            # print(file_lst)
            folder_lst = file_lst[1]
            file_name_lst = file_lst[2]

            for file in file_name_lst:
                file_path = path + "/" + file
                file_size_lst.append(get_file_size(file_path))
                file_modify_time_lst.append(get_file_modify_time(file_path))
                file_type_lst.append(get_file_type(file_path))

        dic['dir'] = folder_lst
        dic['file'] = file_name_lst
        dic['file_size'] = file_size_lst
        dic['file_type'] = file_type_lst
        dic['modify_time'] = file_modify_time_lst

        return jsonify(dic)


def get_file_size(filePath):
    """
    穿路径,拿到文件大小
    :param filePath:
    :return:
    """
    file_size = os.path.getsize(filePath)

    return file_size


def get_file_modify_time(filePath):
    """
    拿到文件的修改时间
    :param filePath:
    :return:
    """
    time_stamp = os.path.getmtime(filePath)
    struct_time = time.localtime(time_stamp)
    modify_time = time.strftime('%Y-%m-%d %H:%M:%S', struct_time)

    return modify_time


def get_file_name(filePath):
    """
    拿到文件夹当前的路径,当前文件夹下的文件和文件夹
    :param file_dir:
    :return:
    """
    file_dir = r"{}".format(filePath)
    for files in os.walk(file_dir):
        return files


def get_file_type(filepath):
    file_type = filepath.rsplit('.')[-1]
    return file_type


def get_file_level(filepath):
    with open(Config.PERMISSION_FILE, 'r') as f:
        with open(Config.PERMISSION_FILE, "r")as f:
            for line in f:
                if line:
                    ret = json.loads(line)
                    if filepath in ret:
                        return ret['level']
