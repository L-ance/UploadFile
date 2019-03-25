# -*- coding: utf-8 -*-
from flask_login import UserMixin
import configparser

conf = configparser.ConfigParser()
conf.read('BConfig.cfg', encoding='gbk')


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

                value = conf.getint('SYS', 'NUSERNUM')

                for i in range(value):
                    section = 'NUSER{}'.format(i)
                    username = conf.get(section, 'UNAME')
                    if username == self.username:
                        return i
            except Exception as e:
                print(e)

                def get_id(self):
                    """get user id from profile file, if not exist, it will
                    generate a uuid for the user.
                    """
                    if self.username is not None:
                        try:

                            value = conf.getint('SYS', 'NUSERNUM')

                            for i in range(value):
                                section = 'NUSER{}'.format(i)
                                username = conf.get(section, 'UNAME')
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
            section = 'NUSER{}'.format(user_id)
            username = conf.get(section, 'UNAME')
            return User(username)
        except Exception as e:
            print(e)
            return None
