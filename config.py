# -*- coding: utf-8 -*-
import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLODAG_PATH = os.path.join(BASE_DIR, 'upload')
    PERMISSION_FILE = os.path.join(BASE_DIR, 'permission')
    LOG_FILE = os.path.join(BASE_DIR,'log')
    FILE_COMMAND = '/initrd/abin/uferry /recvfile/'