import os


class Config:

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLODAG_PATH = os.path.join(BASE_DIR, 'public')
    PERMISSION_FILE = os.path.join(BASE_DIR, 'permission')
    TEST_VERSION_FILE = os.path.join(BASE_DIR, 'test')
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://susqlroot:suanmitsql@127.0.0.1:3306/sudb?charset=gbk'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/sudb?charset=gbk'


    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
    DEBUG = True

    IPAUTHCONF = os.path.join(TEST_VERSION_FILE, 'PAUTHCONF')

    FILE_COMMAND = '/initrd/abin/uferry' + ' /recvfile/ ' + PERMISSION_FILE
    LOGIN_COMMAND = '/etc/init.d/' + 'ipauth.sh {0} {1}'

    PLATFORM = 1
    if PLATFORM == 1:  # 网闸
        USER_FILE = os.path.join(TEST_VERSION_FILE, 'AUTHUSERCONF')
        # 版本信息
        VERSION = os.path.join(TEST_VERSION_FILE, 'sysset.cf')
        # 设备信息
        PRODUCT = os.path.join(TEST_VERSION_FILE, 'wcfg.php')

    elif PLATFORM == 0:  # 光闸

        USER_FILE = os.path.join(TEST_VERSION_FILE, 'BConfig.cfg')
        # 版本信息
        VERSION = os.path.join(TEST_VERSION_FILE, 'DConfig.cfg')

        PRODUCT = os.path.join(TEST_VERSION_FILE, 'webcfg.php')
    else:
        raise ('platform error !!!')


# class Config:
#     BASE_DIR = '/initrd/data/fsmgmt'
#     # 公共目录
#     UPLODAG_PATH = os.path.join(BASE_DIR, 'public')
#     # 权限文件
#     PERMISSION_FILE = os.path.join(BASE_DIR, 'permission')
#     # 测试文件
#     TEST_VERSION_FILE = os.path.join(BASE_DIR, 'test')
#
#     # TEST_VERSION_FILE = '/etc/init.d/'
#     # 网闸配置文件路径
#     GATEKEEPER_FILE = '/var/www/rules/precfg'
#     # 用户信息存储文件
#
#     # 数据库连接和配置
#     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://susqlroot:suanmitsql@localhost/sudb?'
#     SQLALCHEMY_DATABASE_URI += 'unix_socket=/var/run/mysqld/mysqld.sock&charset=latin1'
#
#
#     SQLALCHEMY_TRACK_MODIFICATIONS = True
#     SQLALCHEMY_COMMIT_TEARDOWN = True
#     DEBUG = True
#
#     IPAUTHCONF = os.path.join('/var/www/rules/precfg', 'IPAUTHCONF')
#
#     # 脚本命令
#     FILE_COMMAND = '/initrd/abin/uferry' + ' /recvfile/ ' + PERMISSION_FILE
#     LOGIN_COMMAND = '/etc/init.d/' + 'ipauth.sh {0} {1}'
#
#     PLATFORM = 1
#     if PLATFORM == 1:  # 网闸
#         USER_FILE = os.path.join('/var/www/rules/precfg', 'AUTHUSERCONF')
#         # 版本信息
#         VERSION = os.path.join('/var/www/rules/conf', 'sysset.cf')
#         # 设备信息
#         PRODUCT = os.path.join('/var/www/', 'wcfg.php')
#
#     elif PLATFORM == 0:  # 光闸
#         USER_FILE = os.path.join('/etc/init.d/', 'BConfig.cfg')
#         # 版本信息
#         VERSION = os.path.join('/etc/init.d/', 'DConfig.cfg')
#         # 设备信息
#         PRODUCT = os.path.join(TEST_VERSION_FILE, 'webcfg.php')
#     else:
#         raise ('platform error !!!')

