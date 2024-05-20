import re
from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QMessageBox
from db.ui.pwd_change_dialog import Ui_Dialog as PwdChangeMixin
from db.modules import Items
from interface.customer import call_customer
from interface.shopkeeper import call_shopkeeper
from lib.common import logging_save

_translate = QtCore.QCoreApplication.translate


def call_item(*args, register=False, update=False, log_out=False, **kwargs) -> None | tuple:
    """
    物品与其类的交互
    :param args:
    :param register: 注册
    :param update: 更新数据
    :param log_out: 注销
    :param kwargs: 待更新的数据
    :return: None/检索的数据
    """
    item = Items(**kwargs)
    # 物品注册(商品上架)
    if register:
        item.save(*args)
        return
    # 物品更新(价格, 名称, 折扣等的修改)
    if update:
        item.update(**kwargs)
        return
    # 物品注销(商品下架)
    if log_out:
        item.log_out()
        return
    # 物品检索
    return item.login_check()[1]


class PwdChangeWindow(PwdChangeMixin, QDialog):
    """
    密码修改窗口
    """
    def __init__(self, username, father):
        super(PwdChangeWindow, self).__init__()
        self._new_pwd = None
        self._username = username
        # 这里的me属性对应了顾客和商家的密码的修改
        self._me = father.me
        self._father = father
        self.setupUi(self)
        self.setWindowTitle('修改密码')
        self.pushButton.setEnabled(False)

    # 原密码检验
    def check_previous_pwd(self):
        old_pwd = self.lineEdit.text()
        if not self._me:
            res = call_customer(self._username, pwd=old_pwd)[0]
        else:
            res = call_shopkeeper(self._username, pwd=old_pwd)[0]
            if res == 2 and not old_pwd:
                self.label.setStatusTip('1')
                return
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}', old_pwd):
            self.label.setText(_translate("Form", "密码输入不合法"))
            self.label.setStatusTip('0')
            self.unlock_click()
            return
        if res == 1:
            self.label.setText(_translate("Form", "原密码输入错误！！"))
            self.label.setStatusTip('0')
            self.unlock_click()
            return
        self.label.setStatusTip('1')
        self.label.setText(_translate("Form", "原密码输入正确！！"))
        self.unlock_click()

    # 新密码强度校验
    def verify_new_pwd(self):
        self._new_pwd = self.lineEdit_2.text()
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}', self._new_pwd):
            self.label_2.setText(_translate("Form", "新密码输入不合法"))
            self.label_2.setStatusTip('0')
        else:
            self.label_2.setStatusTip('1')
            self.label_2.setText(_translate("Form", "新密码合法"))
        self.reverify()

    # 新密码再次确认
    def reverify(self):
        re_pwd = self.lineEdit_3.text()
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}', re_pwd):
            self.label_3.setText(_translate("Form", "新密码输入不合法"))
            self.label_3.setStatusTip('0')
            self.unlock_click()
            return
        if re_pwd != self._new_pwd:
            self.label_3.setText(_translate("Form", "两次新密码不相等"))
            self.label_3.setStatusTip('0')
            self.unlock_click()
            return
        self.label_3.setStatusTip('1')
        self.label_3.setText(_translate("Form", "成功"))
        self.unlock_click()

    # 确认按钮的解锁(只有当上述三个校验通过后再开放确认按钮以确认)
    def unlock_click(self):
        if self.label.statusTip() == self.label_2.statusTip() == self.label_3.statusTip() == '1':
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)

    # 密码修改成功的反馈
    def change(self):
        QMessageBox.information(self, '提示', '密码修改成功')
        if not self._me:
            call_customer(self._username, pwd=self._new_pwd, update=True)
            logging_save(0, f"用户{self._username}成功修改了密码")
        else:
            call_shopkeeper(self._username, pwd=self._new_pwd, update=True)
            logging_save(1, f"商家{self._username}成功修改了密码")
        self.close()
        self._father.show_start()
        self._father.start.lineEdit.setText(_translate("Form", f"{self._username}"))
