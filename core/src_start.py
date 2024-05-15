"""
开始页面网络视图层代码
"""

import sys
import re
import time
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QLineEdit
from db.ui.start import Ui_Form as LoginUiMixin
from lib.common import except_hook
from core import src_customer, src_shopkeeper, src_admin
from interface.customer import call_customer
from interface.shopkeeper import call_shopkeeper
from lib.common import logging_save

_translate = QtCore.QCoreApplication.translate


class StartUi(LoginUiMixin, QWidget):
    def __init__(self):
        super(StartUi, self).__init__()
        self.username = ''
        self.pwd = ''
        self.setupUi(self)
        self.setWindowTitle('欢迎光临')

    def login(self):
        username = self.lineEdit.text()
        pwd = self.lineEdit_2.text()
        if not username and not pwd and self.checkBox.isChecked() and self.checkBox_2.isChecked():
            src_admin.run(self)
            self.hide()
            return
        if not username:
            QMessageBox.warning(self, '警告', '用户名不能为空')
            return
        if self.checkBox.isChecked():
            res, info = call_shopkeeper(username, pwd=pwd)
        else:
            res, info = call_customer(username, pwd=pwd)
        match res:
            case 0:
                QMessageBox.warning(self, '警告', '该用户名不存在')
                self.lineEdit.clear()
                self.lineEdit_2.clear()
                self.lineEdit.setFocus()
            case 1:
                QMessageBox.warning(self, '警告', '密码输入错误')
                self.lineEdit_2.clear()
                self.lineEdit_2.setFocus()
            case 2:
                self.lineEdit.clear()
                self.lineEdit_2.clear()
                if info[-1]:
                    QMessageBox.warning(self, '警告', f'抱歉账户{username}已被冻结!!!')
                    return
                QMessageBox.information(self, '提示', '登录成功, 等待跳转')
                if self.checkBox.isChecked():
                    logging_save(1, f"商家{info[0]}登录成功")
                    self.hide()
                    src_shopkeeper.run(self, info)
                else:
                    self.hide()
                    logging_save(0, f"用户{info[0]}登录成功")
                    src_customer.run(self, info)

    def show_pwd(self):
        self.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Normal) if self.checkBox_2.isChecked() else self.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)

    # 打开注册界面
    def open_register_page(self):
        self.stackedWidget.setCurrentIndex(1)
        self.lineEdit_3.setFocus()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.label_3.clear()
        self.label_4.clear()
        self.label_5.clear()

    # 回到开始的界面
    def back_to_start(self):
        self.stackedWidget.setCurrentIndex(0)
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()

    # 动态检查用户名合法性
    def check_username(self):
        if not self.lineEdit_3.text():
            self.label_3.clear()
            self.label_3.setStatusTip('0')
            return
        self.username = self.lineEdit_3.text()
        if re.match(r'[a-zA-Z]{2,4}[a-zA-Z\d]{4,8}', self.username):
            if call_customer(self.username)[0]:
                self.label_3.setText(_translate("Form", "抱歉，该用户名已存在"))
                self.label_3.setStatusTip('0')
                return
            self.label_3.setText(_translate("Form", "用户名输入合法√"))
            self.label_3.setStatusTip('1')
        else:
            self.label_3.setText(_translate("Form", "用户名输入非法！！"))
            self.label_3.setStatusTip('0')

    # 动态校验密码强度
    def verify_pwd_strength(self):
        if not self.lineEdit_4.text():
            self.label_4.clear()
            self.label_4.setStatusTip('0')
            return
        if re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}', self.lineEdit_4.text()):
            self.label_4.setText(_translate("Form", "密码合法√"))
            self.label_4.setStatusTip('1')
        else:
            self.label_4.setText(_translate("Form", "密码设置非法！！"))
            self.label_4.setStatusTip('0')
        self.pwd_check()

    # 动态校验密码确认
    def pwd_check(self):
        if not self.lineEdit_5.text():
            self.label_5.clear()
            self.label_5.setStatusTip('0')
        elif self.label_4.statusTip() == '0':
            self.label_5.setText(_translate("Form", "密码设置非法！！"))
            self.label_5.setStatusTip('0')
        elif self.lineEdit_4.text() == self.lineEdit_5.text():
            self.pwd = self.lineEdit_5.text()
            self.label_5.setText(_translate("Form", "成功!"))
            self.label_5.setStatusTip('1')
        else:
            self.label_5.setText(_translate("Form", "两次密码不一致请重新输入!!!"))
            self.label_5.setStatusTip('0')

    # 注册函数
    def register(self):
        if self.label_3.statusTip() == self.label_4.statusTip() == self.label_5.statusTip() == '1':
            call_customer(self.username, pwd=self.pwd, register=True)
            QMessageBox.information(self, '提示', '恭喜你注册成功！！！')
            logging_save(0, f"用户{self.username}注册成功")
            self.lineEdit.setText(_translate("Form", f"{self.username}"))
            self.lineEdit_2.setFocus()
            self.back_to_start()


def run():
    app = QApplication(sys.argv)
    login_window = StartUi()
    login_window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
