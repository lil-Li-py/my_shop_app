"""
顾客界面网络视图层代码
"""

import configparser
import time
import os
import random
from functools import partial
import requests
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QPushButton, QFrame, QHBoxLayout, \
    QInputDialog, QFileDialog, QTextEdit, QVBoxLayout
from db.ui.customer import Ui_Form as CustomerUiMixin
from db.ui.items import Ui_Form as ItemsMixin
from db.ui.user_setting import Ui_Form as UserSettingMixin
from interface.customer import call_customer
from interface.shopkeeper import call_shopkeeper
from interface.common import PwdChangeWindow, call_item
from lib.common import logging_save

_translate = QtCore.QCoreApplication.translate
font = QtGui.QFont()
font.setPointSize(10)


class CustomerUI(CustomerUiMixin, QWidget):
    def __init__(self, start, info):
        self._sub_window1 = None
        self._sub_window2 = None
        self._sub_window3 = None
        self.start = start
        # 用于分类顾客与商家
        self.me = 0
        # 次数检测
        self.page2 = 0
        self._username = info[0]
        self._nickname = info[1]
        self._balance = float(info[2])
        self._points = info[3]
        self._shopping_cart = eval(info[4])  # 列表
        self._purchased_items = eval(info[5])  # 列表
        self._diy = eval(info[6])
        self._all_cost = 0.0
        super(CustomerUI, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('傻逼')
        self._init_bg(self._diy)
        self.refresh_text()
        config = configparser.ConfigParser()
        config.read('conf/setting.ini', encoding='utf-8')
        self._sort = [i[1] for i in config.items('sort')]
        self._open_shop()
        self._get_items(self._sort[0])

    def _init_bg(self, diy):
        # 判断默认背景目录是否为空
        if not (default := os.listdir('imgs/customer/bg')):
            return
        # 判断是否是用户自定义
        if diy['is_diy']:
            if os.path.exists(diy['bg']):
                img_url = diy['bg']
            else:
                QMessageBox.warning(self, '警告', '您的自定义背景文件是否已移动, 请重新设置')
                del (self._diy['bg'])
                img_url = f"imgs/customer/bg/{random.choice(default)}"
        else:
            img_url = f"imgs/customer/bg/{random.choice(default)}"
        self.frame.setStyleSheet("#frame{border-image:url(%s);}" % img_url)

    # 回到主页或刷新
    def turn_to_0(self):
        self.stackedWidget.setCurrentIndex(0)

    # 打开购物车
    def turn_to_1(self):
        self._load_shopping_cart()
        self.stackedWidget.setCurrentIndex(1)

    # 打开我的
    def turn_to_2(self):
        if not self.page2:
            self._my_profile()
            self.page2 += 1
        self.stackedWidget.setCurrentIndex(2)

    # 商店界面
    def _open_shop(self):
        horizontalLayout = QHBoxLayout(self.home)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        horizontalLayout.setSpacing(0)
        verticalLayout = QVBoxLayout()
        verticalLayout.setSpacing(0)
        horizontalLayout_2 = QHBoxLayout()
        horizontalLayout_2.setSpacing(0)
        for i, j in enumerate(self._sort):
            exec(f'self.button{i} = QPushButton("{j}", self)')
            exec(f'self.button{i}.clicked.connect(partial(self._get_items, "{j}"))')
            exec(f'horizontalLayout_2.addWidget(self.button{i})')
        verticalLayout.addLayout(horizontalLayout_2)
        verticalLayout.addWidget(self.tableWidget)
        horizontalLayout.addLayout(verticalLayout)

    # 每次点击标签刷新table widget里的数据
    def _get_items(self, sort_name):
        items = call_item(sort=sort_name)
        self.tableWidget.setRowCount(length := len(items))
        for i in range(length):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(_translate("Form", f"{i + 1}."))
            for j in range(self.tableWidget.columnCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                if j == 3:
                    textedit = QTextEdit()
                    textedit.setPlainText(_translate("Form", f"{items[i][j]}"))
                    textedit.setEnabled(False)
                    self.tableWidget.setCellWidget(i, j, textedit)
                elif j == 4 or j == 5:
                    button = QPushButton()
                    button.setText(_translate("Form", f"{'添加至购物车' if j == 4 else '购买'}"))
                    if j == 4:
                        button.clicked.connect(partial(self._insert_to_shopping_cart, item))  # type:ignore
                    else:
                        button.clicked.connect(partial(self._buy, item))  # type:ignore
                    self.tableWidget.setCellWidget(i, j, button)
                else:
                    if j == 1:
                        if items[i][4] != 1:
                            item.setToolTip(_translate("Form", f"原价为:{items[i][j]}"))
                            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                            item.setText(_translate("Form", f"{items[i][j] * items[i][4]}"))
                            continue
                    item.setText(_translate("Form", f"{items[i][j]}"))
                self.tableWidget.setItem(i, j, item)

    def _insert_to_shopping_cart(self, item):
        amount, status = QInputDialog.getInt(self, '', '请输入你的购买数量', min=1, max=99)
        if not status:
            return
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        shop_name = self.tableWidget.item(row, 2).text()
        for i in self._shopping_cart:
            if item_name == i[0] and shop_name == i[1]:
                QMessageBox.warning(self, '警告', '抱歉该商品已在您的购物车里.')
                return
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item_info = [item_name, shop_name, amount, now_time]
        self._shopping_cart.append(item_info)
        logging_save(0, f"用户{self._username}将商品{item_name}(来自{shop_name})添加至购物车")
        QMessageBox.information(self, '提示', '添加购物车成功!')

    def _buy(self, item):
        amount, status = QInputDialog.getInt(self, '', '请输入你的购买数量', min=1, max=99)
        if not status:
            return
        row = self.tableWidget.row(item)
        single_price = eval(self.tableWidget.item(row, 1).text())
        price = single_price * amount
        if self._balance < price:
            QMessageBox.warning(self, '警告', '你当前的余额不足!')
            return
        item_name = self.tableWidget.item(row, 0).text()
        shop_name = self.tableWidget.item(row, 2).text()
        item_info = list(call_item(item_name=item_name, shop_name=shop_name))
        item_info.pop()
        item_info.insert(2, amount)
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item_info.append(now_time)
        self._balance -= price
        self._points += price // 10 + 1
        self._purchased_items.append(item_info)
        call_shopkeeper(shop_name, update=True, income=price)
        logging_save(1, f"商家{shop_name}收入金额{price}元")
        logging_save(0, f"用户{self._username}购买商品{item_name}(来自{shop_name})")
        QMessageBox.information(self, '提示', '购买成功!')

    # 购物车界面操作
    # 展示：商家名 价格 商家 类型 简介 添加时间
    def _load_shopping_cart(self):
        self.tableWidget_2.setRowCount(cart := len(self._shopping_cart))
        self._all_cost = 0.0
        self.label.setText(_translate("Form", f"总金额为: {self._all_cost:.2f}元."))
        if not cart:
            return
        for i in range(self.tableWidget_2.rowCount()):
            item = QTableWidgetItem()
            self.tableWidget_2.setVerticalHeaderItem(i, item)
            item_info = list(call_item(item_name=self._shopping_cart[i][0], shop_name=self._shopping_cart[i][1]))
            if not (tmp := item_info):
                item_info = [self._shopping_cart[i][0], '', '', self._shopping_cart[i][1], '', '', '', '']
            discount = item_info.pop()
            item_info.insert(1, self._shopping_cart[i][2])
            item_info.append(self._shopping_cart[i][3])
            # item_info: [商品名, 数量, 单价, 商家, 类别, 商品简介, 时间]
            price = item_info[2] * item_info[1] * discount
            self._all_cost += price
            for j in range(self.tableWidget_2.columnCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                if j == 6:
                    item.setToolTip(_translate("Form", f"{item_info[j]}"))
                if j == 1:
                    item.setText(_translate("Form", f"{item_info[2]}&{item_info[1]}"))
                elif j == 2:
                    if discount != 1:
                        item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                        item.setToolTip(_translate("Form", f"折扣为:{discount * 10}折"))
                    item.setText(_translate("Form", f"{price}"))
                elif j == 5:
                    textedit = QTextEdit()
                    textedit.setPlainText(_translate("Form", f"{item_info[j]}"))
                    textedit.setEnabled(False)
                    self.tableWidget_2.setCellWidget(i, j, textedit)
                elif j != 7:
                    item.setText(_translate("Form", f"{item_info[j]}"))
                else:
                    frame = QFrame()
                    frame.setStyleSheet("background-color:rgb(255, 255, 255, 0);")
                    button1 = QPushButton(frame)
                    button1.setText(_translate("Form", "购买"))
                    if tmp:
                        button1.setToolTip(_translate("Form", "点我购买"))
                    else:
                        button1.setToolTip(_translate("Form", "抱歉该商品已下架"))
                        button1.setEnabled(False)
                    button1.setStyleSheet("QPushButton{"
                                          "color: rgb(255, 145, 90);"
                                          "border-radius: 0px;}"
                                          "QPushButton:hover{"
                                          "color: rgb(255, 225, 190);}"
                                          "QPushButton:pressed{"
                                          "color: rgb(255, 0, 0);}")
                    button2 = QPushButton(frame)
                    button2.setText(_translate("Form", "X"))
                    button2.setToolTip(_translate("Form", "删除"))
                    button2.setStyleSheet("QPushButton{"
                                          "color: rgb(255, 0, 0);"
                                          "border-radius: 0px;}"
                                          "QPushButton:hover{"
                                          "color: rgb(255, 225, 190);}"
                                          "QPushButton:pressed{"
                                          "color:rgb(255,0,0);}")
                    button1.setFont(font)
                    button2.setFont(font)
                    button1.clicked.connect(partial(self._buy_it, item))  # type:ignore
                    button2.clicked.connect(partial(self._remove_one_row, item))  # type:ignore
                    horizontal_layout = QHBoxLayout()
                    horizontal_layout.setSpacing(0)
                    horizontal_layout.addWidget(button1)
                    horizontal_layout.addWidget(button2)
                    horizontal_layout2 = QHBoxLayout(frame)
                    horizontal_layout2.setContentsMargins(0, 0, 0, 0)
                    horizontal_layout2.setSpacing(0)
                    horizontal_layout2.addLayout(horizontal_layout)
                    horizontal_layout.setStretch(0, 10)
                    horizontal_layout.setStretch(1, 1)
                    self.tableWidget_2.setCellWidget(i, j, frame)
                self.tableWidget_2.setItem(i, j, item)
            self.label.setText(_translate("Form", f"总金额为: {self._all_cost:.2f}元."))

    def _buy_it(self, row):
        row = self.tableWidget_2.row(row)
        now_price = eval(self.tableWidget_2.item(row, 1).text().split('&')[1]) * eval(self.tableWidget_2.item(row, 2).text())
        if self._balance < now_price:
            QMessageBox.warning(self, '警告', '您当前的余额不足\n请充值!!!')
            return
        amount = self.tableWidget_2.item(row, 1).text()
        shop_name = self.tableWidget_2.item(row, 3).text()
        call_shopkeeper(shop_name, update=True, income=now_price)
        self._balance -= now_price
        self._all_cost -= now_price
        self._points += now_price // 10 + 1
        self.label.setText(_translate("Form", f"总金额为: {self._all_cost:.2f}元."))
        self.tableWidget_2.removeRow(row)
        bought = self._shopping_cart.pop(row)
        purchased = list(call_item(item_name=bought[0], shop_name=bought[1]))
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if purchased[-1]:
            purchased[1] *= purchased.pop()
        purchased.insert(2, amount)
        purchased.append(now_time)
        self._purchased_items.append(purchased)
        logging_save(1, f"商家{shop_name}收入金额{now_price}元")
        logging_save(0, f"用户{self._username}购买商品{bought[0]}(来自{bought[1]})")
        QMessageBox.information(self, '提示', '购买成功!')

    def _remove_one_row(self, row):
        row = self.tableWidget_2.row(row)
        now_price = eval(self.tableWidget_2.item(row, 2).text())
        self.tableWidget_2.removeRow(row)
        self._all_cost -= now_price
        self.label.setText(_translate("Form", f"总金额为: {self._all_cost:.2f}元."))
        self._shopping_cart.pop(row)
        item_name = self.tableWidget_2.item(row, 0).text()
        shop_name = self.tableWidget_2.item(row, 3).text()
        logging_save(0, f"用户{self._username}将商品{item_name}(来自{shop_name})移除购物车")

    def buy_all(self):
        if not self._shopping_cart:
            return
        if self._balance < self._all_cost:
            QMessageBox.warning(self, '警告', '您当前的余额不足\n请充值!!!')
            return
        self._balance -= self._all_cost
        self._points += self._all_cost // 10 + 1
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for i in self._shopping_cart:
            bought = list(call_item(item_name=i[0], shop_name=i[1]))
            if bought[-1]:
                bought[1] *= bought.pop()
            call_shopkeeper(i[1], update=True, income=bought[1])
            bought.append(now_time)
            self._purchased_items.append(bought)
            logging_save(1, f"商家{i[1]}收入金额{bought[1]}元")
            logging_save(0, f"用户{self._username}购买商品{i[0]}(来自{i[1]})")
        self.clear_all()
        QMessageBox.information(self, '提示', '购买完成!')

    def clear_all(self):
        while self._shopping_cart:
            tmp = self._shopping_cart.pop()
            logging_save(0, f"用户{self._username}将商品{tmp[0]}(来自{tmp[1]})移除购物车")
        self._load_shopping_cart()

    # 我的界面操作
    def _my_profile(self):
        self.label_2.setText(_translate("Form", f"欢迎您 {self._nickname}"))
        self.pushButton_8.setText(_translate("Form", f"您的余额为:{self._balance}元"))

    def refresh_text(self):
        res = requests.get('https://v.api.aa1.cn/api/tiangou/index.php')
        if res.status_code != 200:
            text = ''
        else:
            text = res.text
        self.textBrowser.setText(_translate("Form", f"{text}"))

    # 修改昵称
    def change_nickname(self):
        nickname, status = QInputDialog.getText(self, '修改昵称', '请输入您的昵称')
        if not status:
            return
        if not nickname:
            QMessageBox.warning(self, '警告', '昵称不能为空!!!')
            return
        if len(nickname) > 15:
            QMessageBox.warning(self, '警告', '昵称不能超过15位!!!')
            return
        QMessageBox.information(self, '提示', '昵称设置成功!')
        self._nickname = nickname
        self.label_2.setText(_translate("Form", f"欢迎您 {self._nickname}"))
        logging_save(0, f"用户{self._username}修改了昵称{self._nickname}")

    # 修改密码
    def change_password(self):
        self._sub_window1 = PwdChangeWindow(self._username, self)
        self._sub_window1.show()

    # 充值
    def charge(self):
        balance, status = QInputDialog.getInt(self, '充值', '请输入充值的金额', min=1, max=99999)
        if not status:
            return
        self._balance += balance
        self.pushButton_8.setText(_translate("Form", f"您的余额为:{self._balance}元"))
        QMessageBox.information(self, '提示', '充值成功!!!')
        logging_save(0, f"用户{self._username}充值了{balance}元")

    # 查看已购买的商品
    def check_purchased_items(self):
        self._sub_window2 = PurchasedItemsWindow(self._purchased_items)
        self._sub_window2.show()

    # 打开积分商城
    def open_points_mall(self):
        ...

    # 自定义背景图片
    def user_setting(self):
        self._sub_window3 = UserSettingsWindow(self._username)
        self._sub_window3.show()

    def register_shopkeeper(self):
        res = QMessageBox.question(self, '确认', '您确认注册为商家吗?(消费1000元)')
        if res.name == 'Yes':
            if call_shopkeeper(self._username)[0]:
                QMessageBox.warning(self, '警告', '抱歉你的用户名已注册为商家\n不能再注册')
                return
            if self._balance < 5000:
                QMessageBox.warning(self, '警告', '您的账号余额过少, 不能注册为商户')
                return
            self._balance -= 1000
            call_shopkeeper(self._username, register=True)
            QMessageBox.information(self, '提示', '恭喜你注册成功!\n密码为空, 请尽快登录修改密码')
            logging_save(1, f"商家{self._username}注册成功")
            logging_save(0, f"用户{self._username}成功注册为商家")
            self.start.lineEdit.setText(_translate("Form", f"{self._username}"))
            self.start.checkBox.setChecked(True)
            self.show_start()

    # 返回开始界面
    def show_start(self):
        self.close()
        self.turn_to_0()
        self.start.lineEdit.setFocus()

    def log_out(self):
        res = QMessageBox.question(self, '确认', '您确认要注销此账号吗???')
        if res.name == 'Yes':
            call_customer(self._username, logout=True)
            QMessageBox.information(self, '提示', '注销成功')
            logging_save(0, f"用户{self._username}注销成功")
            self.show_start()

    def save(self):
        customer_info = {'nickname': self._nickname, 'balance': self._balance, 'points': self._points,
                         'shopping_cart': self._shopping_cart, 'purchased_items': self._purchased_items,
                         'diy': self._diy}
        call_customer(self._username, update=True, **customer_info)

    def closeEvent(self, event):
        self.save()
        event.accept()
        logging_save(0, f"用户{self._username}成功退出")
        for i in [self._sub_window1, self._sub_window2, self._sub_window3]:
            if i:
                i.close()
        time.sleep(1)
        self.start.show()


class PurchasedItemsWindow(ItemsMixin, QWidget):
    def __init__(self, items):
        super(PurchasedItemsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('历史购买')
        self._insert_items(items)

    def _insert_items(self, items):
        column_name = ['商品名', '单价', '数量', '商家', '类型', '商品简介', '购买时间']
        self.tableWidget.setColumnCount(len(column_name))
        for i in range(self.tableWidget.columnCount()):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
            item = self.tableWidget.horizontalHeaderItem(i)
            item.setText(_translate("Form", f"{column_name[i]}"))
        if not items:
            return
        self.tableWidget.setRowCount(row := len(items))
        for i in range(row):
            item = QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(_translate("Form", f"{i + 1}."))
            for j, k in enumerate(items[i]):
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                if j == 6:
                    item.setToolTip(_translate("Form", f"{k}"))
                if j == 5:
                    textedit = QTextEdit()
                    textedit.setPlainText(_translate("Form", f"{k}"))
                    textedit.setEnabled(False)
                    self.tableWidget.setCellWidget(i, j, textedit)
                else:
                    item.setText(_translate("Form", f"{k}"))
                self.tableWidget.setItem(i, j, item)


class UserSettingsWindow(UserSettingMixin, QWidget):
    def __init__(self, username):
        super(UserSettingsWindow, self).__init__()
        self._username = username
        self.setupUi(self)

    def diy_background(self):
        new_bg, status = QFileDialog.getOpenFileName(self, "选择你要上传的图片", r"d:\\",
                                                     "图片类型 (*.png *.jpg *.bmp)")
        if not status:
            return
        QMessageBox.information(self, '提示', '自定义背景图完成\n请手动重新登录以刷新')
        diy = {'is_diy': True, 'bg': new_bg}
        # 整体修改了 diy 仍需完善
        call_customer(self._username, update=True, diy=diy)
        logging_save(0, f"用户{self._username}成功设置了自定义背景图片")
        self.close()


def run(start, info):
    start.customer_window = CustomerUI(start, info)
    start.customer_window.show()
