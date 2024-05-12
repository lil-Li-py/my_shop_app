import hashlib
import sys


# 密码加密储存
def encrypt(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


# qt报错设置
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)