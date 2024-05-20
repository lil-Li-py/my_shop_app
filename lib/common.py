import hashlib
import sys
import logging
import conf.settings


def encrypt(pwd: str) -> str:
    """
    密码加密
    :return: 返回加密后的密码
    """
    return hashlib.sha256(pwd.encode()).hexdigest()


def except_hook(cls, exception, traceback):
    """
    Qt文件报错设置
    """
    sys.__excepthook__(cls, exception, traceback)


def logging_save(mode: int, content: str) -> None:
    """
    日志记录
    :param mode: 0 for customer, 1 for shopkeeper
    :param content: 拒绝原因|...
    """
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    _logging = logging.getLogger(dic[mode])
    _logging.info(content)
