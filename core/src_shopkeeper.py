"""
商家网络视图层代码
"""

import time
from functools import partial
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QMessageBox, QDialog, QInputDialog, QTableWidgetItem, QPushButton, \
    QTextEdit
from db.ui.shopkeeper import Ui_Form as ShopKeeperMixin
from db.ui.edit_items import Ui_Dialog as EditItemsMixin
from db.ui.items import Ui_Form as ItemsMixin
from interface.common import PwdChangeWindow
from interface.shopkeeper import call_shopkeeper
from interface.common import call_item
from lib.common import logging_save


_translate = QtCore.QCoreApplication.translate


class ShopkeeperUI(ShopKeeperMixin, QWidget):
    def __init__(self, start, info):
        super(ShopkeeperUI, self).__init__()
        self.listing = None
        self.listed = None
        self.delisted = None
        self.sub_window1 = None
        self.edit_items = None
        self.start = start
        # 用于分类顾客与商家
        self.me = 1
        self.username = info[0]
        self.income = info[1]
        self.sub_pwd = info[2]
        self.listing_items = eval(info[3])
        self.listed_items = eval(info[4])
        self.delisted_items = eval(info[5])
        self.setupUi(self)
        self.setWindowTitle('商家')
        self.label.setText(_translate('Form', f"总收入为:{self.income}"))

    def list_items(self):
        self.edit_items = EditItems(self)
        self.edit_items.show()

    def change_pwd(self):
        self.sub_window1 = PwdChangeWindow(self.username, self)
        self.sub_window1.show()

    def change_sub_pwd(self):
        new_sub_pwd, status = QInputDialog.getText(self, '', '请输入你的新上架密码')
        if status and new_sub_pwd:
            QMessageBox.information(self, '提示', '设置成功')
            self.sub_pwd = new_sub_pwd
            logging_save(1, f"用户{self.username}成功设置了上架密码")
        else:
            return

    def check_listing_items(self):
        self.listing = ListingItemsWindow(self)
        self.listing.show()

    def check_listed_items(self):
        self.listed = ListedItemsWindow(self)
        self.listed.show()

    def check_delisted_items(self):
        self.delisted = DelistedItemsWindow(self)
        self.delisted.show()

    def show_start(self):
        self.close()
        self.start.lineEdit.setFocus()
        self.start.checkBox.setChecked(False)

    def log_out(self):
        res = QMessageBox.question(self, '确认', '您确认要注销此账号吗???')
        if res.name == 'Yes':
            call_shopkeeper(self.username, logout=True)
            call_item(log_out=True, shop_name=self.username, item_name=None)
            QMessageBox.information(self, '提示', '注销成功')
            logging_save(1, f"商家{self.username}成功注销了此账号")
            self.show_start()

    def save(self):
        shopkeeper_info = {'sub_pwd': self.sub_pwd, 'listing_items': self.listing_items, 'listed_items': self.listed_items, 'delisted_items': self.delisted_items}
        call_shopkeeper(self.username, update=True, **shopkeeper_info)

    def closeEvent(self, event):
        self.save()
        event.accept()
        logging_save(1, f"商家{self.username}成功退出登录")
        for i in [self.listing, self.listed, self.delisted, self.sub_window1, self.edit_items]:
            if i:
                i.close()
        time.sleep(1)
        self.start.show()


class EditItems(EditItemsMixin, QDialog):
    def __init__(self, father):
        import configparser
        super(EditItems, self).__init__()
        self.father = father
        self.username = father.username
        self.name = ''
        self.price = 0
        self.setupUi(self)
        self.setWindowTitle('编辑商品')
        config = configparser.ConfigParser()
        config.read('conf/setting.ini', encoding='utf-8')
        for i, j in enumerate((i[1] for i in config.items('sort'))):
            self.comboBox.addItem("")
            self.comboBox.setItemText(i, _translate("Form", f"{j}"))
        self.comboBox.setCurrentIndex(0)

    def set_name(self):
        if not self.lineEdit.text():
            self.lineEdit.setPlaceholderText('商品名不能为空!')
            return
        self.name = self.lineEdit.text()

    def set_price(self):
        price, status = QInputDialog.getInt(self, ' ', '请输入价格', min=1, max=99999)
        if not status:
            return
        self.price = price
        self.pushButton.setText(f'当前设置的价格为 {self.price}元')

    def click_it(self):
        sub_pwd, status = QInputDialog.getText(self, '', '请输入你的上架密码')
        if not self.name or not self.price or not status:
            return
        if self.father.sub_pwd != sub_pwd:
            QMessageBox.warning(self, '警告', '上架密码输入错误!!!')
            return
        items = [i for i in self.father.listing_items + self.father.listed_items]
        for i in items:
            if self.name == i[0]:
                QMessageBox.warning(self, '警告', '抱歉, 该商品名与您正在上架的商品名重复')
                self.lineEdit.clear()
                return
        item_info = {'item_name': self.name, 'price': self.price, 'shop_name': self.father.username,
                     'sort': self.comboBox.currentText(), 'description': self.textEdit.toPlainText()}
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.father.listing_items.append([i for i in item_info.values()] + [now_time] + [[]])
        self.close()
        QMessageBox.information(self, '提示', '商品上架成功, 请等待审核')
        logging_save(1, f"商家{self.username}上架了商品{self.name}(待审核)")


class ListingItemsWindow(ItemsMixin, QWidget):
    def __init__(self, father):
        super(ListingItemsWindow, self).__init__()
        self.username = father.username
        self.items = father.listing_items
        self.listed_items = father.listed_items
        self.id = 0
        self.setupUi(self)
        self.setWindowTitle('正在审核的商品')
        self.column_name = ['商品名', '价格', '商家', '类型', '商品简介', '提交时间', '', '审核结果']
        insert_items(self)

    def f(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        self.tableWidget.removeRow(row)
        for i in self.items:
            if i[0] == item_name:
                self.items.remove(i)
        QMessageBox.information(self, "提示", "取消上架成功")
        logging_save(1, f"商家{self.username}取消上架了商品{item_name}")

    def acknowledge(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        self.tableWidget.removeRow(row)
        for i in self.items:
            if i[0] == item_name:
                self.items.remove(i)
                i = i[0:len(i) - 2]
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                i.extend([1, now_time])
                self.listed_items.append(i)
                call_item(*i, register=True)
        QMessageBox.information(self, "提示", "上架成功")
        logging_save(1, f"商家{self.username}成功上架了商品{item_name}")
        logging_save(2, f"商品{item_name}(来自{self.username})已成功上架")


class ListedItemsWindow(ItemsMixin, QWidget):
    def __init__(self, father):
        super(ListedItemsWindow, self).__init__()
        self.username = father.username
        self.items = father.listed_items
        self.delisted_items = father.delisted_items
        self.id = 1
        self.column_name = ['商品名', '价格', '商家', '类型', '商品简介', '上架时间', '折扣', '']
        self.setupUi(self)
        self.setWindowTitle('已上架的商品')
        insert_items(self)

    def f(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        self.tableWidget.removeRow(row)
        for i in self.items:
            if i[0] == item_name:
                self.items.remove(i)
                i = i[0:len(i) - 2]
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                i.append(now_time)
                self.delisted_items.append(i)
                call_item(log_out=True, item_name=item_name, shop_name=self.username)
        QMessageBox.information(self, "提示", "下架成功")
        logging_save(1, f"商家{self.username}下架了商品{item_name}")
        logging_save(2, f"商品{item_name}(来自{self.username})已被下架")


class DelistedItemsWindow(ItemsMixin, QWidget):
    def __init__(self, father):
        super(DelistedItemsWindow, self).__init__()
        self.items = father.delisted_items
        self.id = 2
        self.setupUi(self)
        self.setWindowTitle('已下架的商品')
        self.column_name = ['商品名', '价格', '商家', '类型', '商品简介', '下架时间']
        insert_items(self)


def insert_items(ob):
    ob.tableWidget.setColumnCount(len(ob.column_name))
    for i in range(column := ob.tableWidget.columnCount()):
        item = QTableWidgetItem()
        ob.tableWidget.setHorizontalHeaderItem(i, item)
        item = ob.tableWidget.horizontalHeaderItem(i)
        item.setText(_translate("Form", f"{ob.column_name[i]}"))
    if not (row := len(ob.items)):
        return
    ob.tableWidget.setRowCount(row)
    for i in range(ob.tableWidget.rowCount()):
        item = QTableWidgetItem()
        ob.tableWidget.setVerticalHeaderItem(i, item)
        item = ob.tableWidget.verticalHeaderItem(i)
        item.setText(_translate("Form", f"{i + 1}."))
        for j in range(column):
            item = QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            if j < 6:
                if j == 5:
                    item.setToolTip(_translate("Form", f"{ob.items[i][j]}"))
                if j == 4:
                    textedit = QTextEdit()
                    textedit.setPlainText(_translate("Form", f"{ob.items[i][j]}"))
                    textedit.setEnabled(False)
                    ob.tableWidget.setCellWidget(i, j, textedit)
                else:
                    item.setText(_translate("Form", f"{ob.items[i][j]}"))
            else:
                if not ob.id:
                    button = QPushButton()
                    if j == 6:
                        button.setText(_translate("Form", f"{'取消上架'}"))
                        button.clicked.connect(partial(ob.f, item))  # type:ignore
                    elif j == 7:
                        if ob.items[i][j-1]:
                            if ob.items[i][j-1][0]:
                                button.setText(_translate("Form", "上架"))
                            else:
                                button.setText(_translate("Form", "已拒绝"))
                                button.setToolTip(_translate("Form", f"拒绝原因:{ob.items[i][j-1][1]}"))
                                button.setEnabled(False)
                            button.clicked.connect(partial(ob.acknowledge, item))  # type:ignore
                        else:
                            button.setText(_translate("Form", "正在等待审核..."))
                            button.setEnabled(False)
                    ob.tableWidget.setCellWidget(i, j, button)
                else:
                    if j == 6:
                        item.setText(_translate("Form", f"{ob.items[i][j]}"))
                    elif j == 7:
                        button = QPushButton()
                        button.setText(_translate("Form", f"{'下架'}"))
                        button.clicked.connect(partial(ob.f, item))  # type:ignore
                        ob.tableWidget.setCellWidget(i, j, button)
            ob.tableWidget.setItem(i, j, item)


def run(start, info):
    start.shopkeeper = ShopkeeperUI(start, info)
    start.shopkeeper.show()
