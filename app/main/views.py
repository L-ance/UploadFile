# -*-coding:UTF-8-*-
import json
import os
from flask import request, session, jsonify, make_response, send_from_directory
from flask_login import login_required
from app.main import main_blueprint
from config import Config
from app.auth.views import get_request_ip
from app.operat_db import operate_db, uploadfile_db, gatekeeper_db


def get_file_size(filePath):
    """
    穿路径,拿到文件大小
    :param filePath:
    :return:
    """
    file_size = os.path.getsize(filePath)
    return file_size


@main_blueprint.route("/upload/", methods=["GET", "POST"])
@login_required
def upload():
    """
    上传文件函数
    :return:
    """
    PLATFORM = Config.PLATFORM
    dic = {}
    permission = {}

    file = request.files.get('file')
    position = request.values.get('type')
    folder = request.values.get('dir')

    username = session.get("username")
    level = session.get("level")
    destip = session.get('destip')
    destport = session.get('destport')
    ip = get_request_ip()
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
        position_file = path + "/{}".format(file.filename)

        if os.path.exists(position_file):
            os.remove(position_file)


        with open(position_file, 'wb') as f:
            file.save(f)
        # 发送文件的命令
        os.system(Config.FILE_COMMAND)

        file_size = get_file_size(position_file)
        dic['type'] = int(position)
        dic['path'] = folder
        dic["status"] = 1

        if PLATFORM == 0:
            operate_db(username, ip, result='upload_success', goal=file.filename)  # 上传成功记入数据库


        else:
            isout = False
            gatekeeper_db('文件交换', username, ip, destip, destport, '上传', file.filename, '成功', isout, '上传成功')

        uploadfile_db(username, path, file.filename, file_size, ip)  # 上传到sfiles数据库和sfilebaks备份数据库

    except Exception as e:
        print(e)
        dic["status"] = 0
        if PLATFORM == 0:
            operate_db(username, ip, result='upload_error', goal=file.filename)  # 上传失败记入数据库
        else:
            isout = False
            gatekeeper_db('文件交换', username, ip, destip, destport, '上传', file.filename, '失败', isout, '上传失败')

    return jsonify(dic)


@main_blueprint.route('/download/', methods=['GET', 'POST'])
@login_required
def download_file():
    """
    下载文件函数
    :return:
    """
    base_path = Config.BASE_DIR
    PLATFORM = Config.PLATFORM

    name = request.args.get('d')

    username = session.get('username')
    destip = session.get('destip')
    destport = session.get('destport')
    ip = get_request_ip()

    if '/' in name:
        split_list = name.rsplit('/', 1)
        filename = split_list[-1]
        file_path = base_path + "/" + split_list[0]

    else:
        file_path = base_path
        filename = name

    response = make_response(send_from_directory(file_path, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    if PLATFORM == 0:
        operate_db(username, ip, result='download_success', goal=filename)  # 下载成功记入数据库

    if PLATFORM == 0:
        operate_db(username, ip, result='download_success', goal=filename)  # 下载成功记入数据库
    else:
        isout = False
        gatekeeper_db('文件交换', username, ip, destip, destport, '下载', filename, '成功', isout, '下载成功')

    # os.system(os.path.join(Config.FILE_COMMAND, file_path))

    return response


@main_blueprint.route('/make_dir/', methods=['POST'])
def make_dir():
    dic = {}
    PLATFORM = Config.PLATFORM

    destip = session.get('destip')
    destport = session.get('destport')
    username = session.get('username')
    ip = get_request_ip()

    original = request.get_json().get('original')
    add = request.get_json().get('add')
    path = Config.BASE_DIR + original + "/" + add

    PLATFORM = Config.PLATFORM
    destip = session.get('destip')
    destport = session.get('destport')

    if not os.path.exists(path):
        try:
            make_path = Config.BASE_DIR + original
            os.mkdir(make_path + './{}'.format(add))
            dic['status'] = 1

            if PLATFORM == 0:
                operate_db(username, ip, result='mkdir_success', goal='{}/{}'.format(original, add))  # 创建目录成功记入数据库

            else:
                isout = False
                gatekeeper_db('文件交换', username, ip, destip, destport, '创建目录', add, '成功', isout, '创建目录成功')

        except Exception as e:
            print(e)
            dic["status"] = 0

            if PLATFORM == 0:
                operate_db(username, ip, result='mkdir_error', goal='{}/{}'.format(original, add))  # 创建目录失败记入数据库

            else:
                isout = False
                gatekeeper_db('文件交换', username, ip, destip, destport, '创建目录', add, '成功', isout, '创建目录成功')
        except Exception as e:
            print(e)
            dic["status"] = 0
            if PLATFORM == 0:
                operate_db(username, ip, result='mkdir_error', goal='{}/{}'.format(original, add))  # 创建目录失败记入数据库

            else:
                isout = False
                gatekeeper_db('文件交换', username, ip, destip, destport, '创建目录', add, '失败', isout, '创建目录失败')
    else:
        dic['status'] = 2
        dic['msg'] = '文件夹已存在'

        if PLATFORM == 0:
            operate_db(username, ip, result='mkdir_error', goal='{}/{}'.format(original, add))  # 创建目录失败记入数据库

        else:
            isout = False
            gatekeeper_db('文件交换', username, ip, destip, destport, '创建目录', add, '失败', isout, '文件夹已存在')
    return jsonify(dic)


@main_blueprint.route('/rv_file/', methods=['DELETE'])
def rv_file():
    dic = {}
    username = session.get('username')
    ip = get_request_ip()

    PLATFORM = Config.PLATFORM
    destip = session.get('destip')
    destport = session.get('destport')

    try:
        folder_path = request.get_json().get('file')
        path = Config.BASE_DIR + folder_path
        os.remove(path)
        dic['status'] = 1

        if PLATFORM == 0:
            operate_db(username, ip, result='rmfile_success', goal=folder_path)  # 删除文件成功记入数据库
        else:
            isout = False
            gatekeeper_db('文件交换', username, ip, destip, destport, '删除文件', folder_path, '成功', isout, '删除文件成功')
        # 删除文件的命令
        os.system(Config.FILE_COMMAND)
        print(Config.FILE_COMMAND)

    except Exception as e:
        print(e)
        dic["status"] = 0

        if PLATFORM == 0:
            operate_db(username, ip, result='rmfile_error')  # 删除文件失败记入数据库
        else:
            isout = False
            gatekeeper_db('文件交换', username, ip, destip, destport, '删除文件', None, '失败', isout, '删除文件失败')

    return jsonify(dic)
