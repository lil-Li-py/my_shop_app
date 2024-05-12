import re

from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QMessageBox

from db.ui.pwd_change_dialog import Ui_Dialog as PwdChangeMixin
from db.modules import Items
from interface.customer import call_customer
from interface.shopkeeper import call_shopkeeper

_translate = QtCore.QCoreApplication.translate


def call_item(*args, register=False, update=False, log_out=False, **kwargs):
    item = Items(**kwargs)
    if register:
        item.save(*args)
        return
    if update:
        item.update(**kwargs)
        return
    if log_out:
        item.log_out()
        return
    return item.login_check()[1]


class PwdChangeWindow(PwdChangeMixin, QDialog):
    def __init__(self, username, father):
        super(PwdChangeWindow, self).__init__()
        self._new_pwd = None
        self._username = username
        self._me = father.me
        self.father = father
        self.setupUi(self)
        self.setWindowTitle('修改密码')
        self.pushButton.setEnabled(False)

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

    def verify_new_pwd(self):
        self._new_pwd = self.lineEdit_2.text()
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}', self._new_pwd):
            self.label_2.setText(_translate("Form", "新密码输入不合法"))
            self.label_2.setStatusTip('0')
        else:
            self.label_2.setStatusTip('1')
            self.label_2.setText(_translate("Form", "新密码合法"))
        self.reverify()

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

    def unlock_click(self):
        if self.label.statusTip() == self.label_2.statusTip() == self.label_3.statusTip() == '1':
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)

    def change(self):
        QMessageBox.information(self, '提示', '密码修改成功')
        if not self._me:
            call_customer(self._username, pwd=self._new_pwd, update=True)
        else:
            call_shopkeeper(self._username, pwd=self._new_pwd, update=True)
        self.close()
        self.father.show_start()
        self.father.start.lineEdit.setText(_translate("Form", f"{self._username}"))
