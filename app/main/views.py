# -*- coding: utf-8 -*-
import json
import os

from flask import request, session, jsonify, make_response, send_from_directory, abort
from flask_login import login_required

from app.main import main_blueprint
from config import Config


@main_blueprint.route("/upload/", methods=["GET", "POST"])
@login_required
def upload():
    """
    上传文件函数
    :return:
    """

    dic = {}
    permission = {}

    file = request.files.get('file')
    position = request.values.get('type')
    folder = request.values.get('dir')

    username = session.get("username")
    level = session.get("level")
    #  1 是私有区 0 是共有区
    if int(position) == 0:
        permission['username'] = username
        permission['level'] = level
        permission[folder + file.filename] = file.filename
        file_info = json.dumps(permission)
        with open(Config.PERMISSION_FILE, "a+")as f:
            f.write(file_info)
            f.write('\n')

    path = Config.BASE_DIR + folder

    try:
        absolute_path = path + "/{}".format(file.filename)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)

        file.save(absolute_path)
        """
        以后要用
           os.system(Config.FILE_COMMAND + absolute_path)
        """

        dic['type'] = int(position)
        dic['path'] = folder
        dic["status"] = 1
        # print(dic)
    except Exception as e:
        dic["status"] = 0
        print(e)

    return jsonify(dic)


@main_blueprint.route('/download/', methods=['GET', 'POST'])
@login_required
def download_file():
    """
    下载文件函数
    :return:
    """
    base_path = Config.BASE_DIR
    name = request.args.get('d')
    level = session.get('level')

    with open(Config.PERMISSION_FILE, "r")as f:
        for line in f:
            if line:
                ret = json.loads(line)
                if name not in ret or int(level) > int(ret['level']):
                    abort(403)

    if '/' in name:
        split_list = name.rsplit('/', 1)
        filename = split_list[-1]
        file_path = base_path + "/" + split_list[0]

    else:
        file_path = base_path
        filename = name

    response = make_response(send_from_directory(file_path, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    """
    以后要用
    os.system(Config.FILE_COMMAND + file_path)
    """

    return response


@main_blueprint.route('/make_dir/', methods=['POST'])
@login_required
def make_dir():
    dic = {}
    # print(request.get_json())
    original = request.get_json().get('original')
    add = request.get_json().get('add')
    path = Config.BASE_DIR + original + "/" + add
    if not os.path.exists(path):
        print(os.path.exists(path))
        try:
            make_path = Config.BASE_DIR + original
            os.mkdir(make_path + './{}'.format(add))
            dic['status'] = 1
        except Exception as e:
            print(e)
            dic["status"] = 0
    else:
        dic['status'] = 2
        dic['msg'] = '文件夹已存在'
    return jsonify(dic)


@main_blueprint.route('/rv_file/', methods=['DELETE'])
@login_required
def rv_file():
    dic = {}
    try:
        folder_path = request.get_json().get('file')
        path = Config.BASE_DIR + folder_path
        os.remove(path)
        dic['status'] = 1

    except Exception as e:
        dic["status"] = 0

    return jsonify(dic)
