# -*- coding: utf-8 -*-
from app import db
from flask_login import UserMixin
import configparser
from app import Config

conf = configparser.ConfigParser()
conf.read(Config.USER_FILE, encoding='gbk')


class User(UserMixin):
    def __init__(self, username):
        self.username = username
        self.id = self.get_id()

    def get_id(self):
        """get user id from profile file, if not exist, it will
        generate a uuid for the user.
        """
        if self.username is not None:
            try:
                if Config.PLATFORM == 0:
                    user_num = conf.getint('SYS', 'NUSERNUM')
                    for i in range(int(user_num)):
                        username = conf.get('NUSER{}'.format(i), 'uname')
                        if username == self.username:
                            return i

                else:
                    user_num = conf.getint("MAIN", 'num')
                    for i in range(int(user_num)):
                        username = conf.get('USER{}'.format(i), 'name')
                        if username == self.username:
                            return i
            except Exception as e:
                print(e)

    @staticmethod
    def get(user_id):
        """try to return user_id corresponding User object.
        This method is used by load_user callback function
        """
        if user_id is None:
            return None
        try:
            if Config.PLATFORM == 0:
                username = conf.get('NUSER{}'.format(user_id), 'uname')
            else:
                username = conf.get('USER{}'.format(user_id), 'name')
            return User(username)
        except Exception as e:
            print(e)
            return None


# class SYSLOG(db.Model):
#     __tablename__ = 'syslogs'
#
#     id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
#     optime = db.Column(db.DateTime, nullable=False)
#     logtype = db.Column(db.String(20), nullable=False)
#     result = db.Column(db.String(20), nullable=False, default='result')
#     remark = db.Column(db.Text, nullable=False, default='remark')
#     ifsend = db.Column(db.SmallInteger, nullable=False, index=True, default='1')


# class CallLOG(db.Model):
#     __tablename__ = 'CallLOG'
# 
#     id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
#     optime = db.Column(db.DateTime, nullable=False)
#     opuser = db.Column(db.String(60), nullable=False)
#     srcip = db.Column(db.String(40), nullable=False)
#     myip = db.Column(db.String(40), nullable=False, default='localhost')
#     myport = db.Column(db.String(10), nullable=False, default='8080')
#     result = db.Column(db.String(20), nullable=False)
#     remark = db.Column(db.Text, nullable=False)
#     ifsend = db.Column(db.SmallInteger, nullable=False, index=True, default=0)


class CallLOG(db.Model):
    """
    网闸的
    """
    __tablename__ = 'CallLOG'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    optime = db.Column(db.DateTime)
    opuser = db.Column(db.String(50))
    srcip = db.Column(db.String(50))
    dstip = db.Column(db.String(50))
    srcport = db.Column(db.String(10))
    dstport = db.Column(db.String(10))
    service = db.Column(db.String(50))
    cmd = db.Column(db.String(50))
    param = db.Column(db.String(100))
    result = db.Column(db.String(50))
    remark = db.Column(db.Text)
    ifsend = db.Column(db.SmallInteger, nullable=False, index=True, default=0)
    isout = db.Column(db.Boolean)
    alarm = db.Column(db.Boolean)


class SFILE(db.Model):
    __tablename__ = 'SFILE'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    optime = db.Column(db.DateTime, nullable=False)
    opuser = db.Column(db.String(60), nullable=False)
    fpath = db.Column(db.String(1080), nullable=False)
    fname = db.Column(db.String(520), nullable=False)
    fsize = db.Column(db.Integer, nullable=False)
    srcip = db.Column(db.String(40), nullable=False)
    src = db.Column(db.String(10), default='访问用户'.encode('gbk'))
    ifdir = db.Column(db.String(20), nullable=False, default='ifdir')
    shortname = db.Column(db.String(260))

    # sfilebak = db.relationship('SFILEBAK', uselist=False)


class SFILEBAK(db.Model):
    __tablename__ = 'SFILEBAK'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    optime = db.Column(db.DateTime, nullable=False, index=True)
    opuser = db.Column(db.String(60), nullable=False)
    fpath = db.Column(db.String(1080), nullable=False)
    fname = db.Column(db.String(520), nullable=False)
    fsize = db.Column(db.Integer, nullable=False, index=True)
    srcip = db.Column(db.String(40), nullable=False)
    src = db.Column(db.String(10), default='访问用户'.encode('gbk'))
    ifdir = db.Column(db.String(20), nullable=False, default='ifdir')
    shortname = db.Column(db.String(260), index=True)
    lasttime = db.Column(db.DateTime, index=True)

    # sfile_id = db.Column(db.Integer, db.ForeignKey('sfile.id'))
    # sfile = db.relationship('SFILE')
