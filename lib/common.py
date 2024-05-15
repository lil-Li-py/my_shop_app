import hashlib
import sys
import logging
import conf.settings


# 密码加密储存
def encrypt(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# qt报错设置
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# 日志记录
def logging_save(mode: int, content: str) -> None:
    """
    :param mode: 0 for customer, 1 for shopkeeper
    :param content:
    :return: nothing
    """
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    _logging = logging.getLogger(dic[mode])
    _logging.info(content)
