# -*-coding:UTF-8-*-
import datetime
from app import db
from app.models import SFILE, SFILEBAK, CallLOG


def operate_db(name, ip, result=None, goal=None):
    """
    光闸插入数据
    :param name:
    :param ip:
    :param result:
    :param goal:
    :return:
    """
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.add(CallLOG(opuser=name.encode('gbk'), optime=time.encode('gbk'), srcip=ip.encode('gbk'),
                           result=result.encode('gbk'),
                           remark='name is {0}, action is {1}, the goal is {2}'.format(name, result, goal).encode(
                               'gbk')))
    db.session.commit()


def uploadfile_db(name, path, filename, file_size, ip):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.session.add(
        SFILE(opuser=name.encode('utf8'), optime=time, fpath=path.encode('utf8'), fname=filename.encode('utf8'),
              fsize=file_size, shortname=filename.encode('utf8'), srcip=ip))
    db.session.add(
        SFILEBAK(opuser=name.encode('utf8'), optime=time, fpath=path.encode('utf8'), fname=filename.encode('utf8'),
                 fsize=file_size, shortname=filename.encode('utf8'), srcip=ip, lasttime=time))
    db.session.add(
        SFILEBAK(opuser=name.encode('utf8'), optime=time, fpath=path.encode('utf8'), fname=filename.encode('utf8'),
                 fsize=file_size,
                 shortname=filename.encode('utf8'), srcip=ip, lasttime=time))

    db.session.commit()


def gatekeeper_db(service, name, ip, destip, dstport, cmd, param, result, isout, remark):
    """
    网闸插入数据
    :param name:
    :param ip:
    :param result:
    :return:
    """
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.add(
        CallLOG(opuser=name.encode('utf8'), optime=time, srcip=ip, result=result.encode('utf8'), srcport=None,
                dstport=dstport, dstip=destip, service=service.encode('utf8'), cmd=cmd.encode('utf8'),
                param=param.encode('utf8'), isout=isout, alarm=None, remark=remark.encode('utf8')))

    db.session.commit()
