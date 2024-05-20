"""
管理员网络视图层代码:
    直接与数据层进行交互
"""

import time
from functools import partial
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QPushButton, QMessageBox, QTextEdit, QFrame, \
    QHBoxLayout, QInputDialog
from db.ui.admin import Ui_Form as AdminMixin
from db.ui.items import Ui_Form as ItemsMixin
from db.db_handler import admin
from interface.customer import call_customer
from interface.shopkeeper import call_shopkeeper
from lib.common import logging_save


_translate = QtCore.QCoreApplication.translate


# 管理员界面
class AdminUi(AdminMixin, QWidget):
    def __init__(self, start):
        """
        :type start: 开始界面(来自core.src_start StartUi
        """
        super(AdminUi, self).__init__()
        self._sub_win1 = None  # 管理用户窗口
        self._sub_win2 = None  # 管理商家窗口
        self._sub_win3 = None  # 商品上架审核窗口
        self.start = start
        self.setupUi(self)
        self.setWindowTitle('管理员')

    # 检索所有用户
    def check_all_customers(self):
        info = admin(0)
        column = ['用户名', '']
        self._sub_win1 = ManageWindow(info, column)
        self._sub_win1.setWindowTitle('所有用户')
        self._sub_win1.show()

    # 检索所有商家
    def check_all_shopkeepers(self):
        info = admin(1)
        column = ['商家名', '']
        self._sub_win2 = ManageWindow(info, column)
        self._sub_win2.setWindowTitle('所有商家')
        self._sub_win2.show()

    # 检索所有待审核的商品
    def verify_listing_items(self):
        info = admin(2)
        column = ['商品名', '价格', '商家', '类型', '商品介绍', '提交时间', '']
        self._sub_win3 = ManageWindow(info, column)
        self._sub_win3.setWindowTitle('所有待审核商品')
        self._sub_win3.show()

    # 重写关闭方法
    def closeEvent(self, event):
        event.accept()
        # 获取所有子窗口, 若打开则关闭
        for i in [self._sub_win1, self._sub_win2, self._sub_win3]:
            if i:
                i.close()
        time.sleep(1)
        self.start.show()


# 管理窗口(可同时打开上述三个窗口)
class ManageWindow(ItemsMixin, QWidget):
    def __init__(self, info, column):
        super(ManageWindow, self).__init__()
        self._info = info
        self._column = column
        self._mode = 0 if self._column[0] == '用户名' else 1
        self.setupUi(self)
        self._insert_items()

    # tablewidget插入值
    def _insert_items(self):
        self.tableWidget.setColumnCount(len(self._column))  # 设置列
        # 添加表头
        for i in range(self.tableWidget.columnCount()):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
            item = self.tableWidget.horizontalHeaderItem(i)
            item.setText(_translate("Form", f"{self._column[i]}"))
        row = len(self._info)
        if not row:
            return
        self.tableWidget.setRowCount(row)  # 设置行
        # 为每行每列的每个item添加值
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # 设置字体居中
                # 查看用户与商家窗口
                if self.tableWidget.columnCount() == 2:
                    if not j:
                        item.setText(_translate("Form", f"{self._info[i][j]}"))
                    else:
                        button = QPushButton()
                        button.setText(_translate("Form", f"{'解冻' if self._info[i][j] else '冻结'}"))
                        button.clicked.connect(partial(self._do_frozen, self._mode, item))  # type:ignore
                        self.tableWidget.setCellWidget(i, j, button)
                    self.tableWidget.setItem(i, j, item)
                # 审核上架商品窗口
                else:
                    if j == 5:
                        # 给提交时间添加tooltip
                        item.setToolTip(_translate("Form", f"{self._info[i][j]}"))
                    if j == 4:
                        # 创建textedit以存储商品简介以更好的展示
                        textedit = QTextEdit()
                        textedit.setPlainText(_translate("Form", f"{self._info[i][j]}"))
                        textedit.setEnabled(False)
                        self.tableWidget.setCellWidget(i, j, textedit)
                    elif j != 6:
                        item.setText(_translate("Form", f"{self._info[i][j]}"))
                    else:
                        # 设置审核答复按钮
                        frame = QFrame()
                        button1 = QPushButton(frame)
                        button1.setText(_translate("Form", "接受"))
                        button1.clicked.connect(partial(self._confirm, item))  # type:ignore
                        button2 = QPushButton(frame)
                        button2.setText(_translate("Form", "拒绝"))
                        button2.clicked.connect(partial(self._reject, item))  # type:ignore
                        horizontal_layout = QHBoxLayout()
                        horizontal_layout.setSpacing(0)
                        horizontal_layout.addWidget(button1)
                        horizontal_layout.addWidget(button2)
                        horizontal_layout2 = QHBoxLayout(frame)
                        horizontal_layout2.setContentsMargins(0, 0, 0, 0)
                        horizontal_layout2.setSpacing(0)
                        horizontal_layout2.addLayout(horizontal_layout)
                        self.tableWidget.setCellWidget(i, j, frame)
                    self.tableWidget.setItem(i, j, item)

    # 用户/商家的冻结/解冻方法
    def _do_frozen(self, mode, item):
        row = self.tableWidget.row(item)
        # 修改解冻或冻结
        is_frozen = 0 if self._info[row][1] else 1
        if not mode:
            logging_save(0, f"用户{self._info[row][0]}已被{'冻结' if is_frozen else '解冻'}")
            call_customer(self._info[row][0], update=True, is_frozen=is_frozen)
        else:
            logging_save(1, f"商家{self._info[row][0]}已被{'冻结' if is_frozen else '解冻'}")
            call_shopkeeper(self._info[row][0], update=True, is_frozen=is_frozen)
        QMessageBox.information(self, '提示', '修改成功')
        self.close()

    # 审核通过
    def _confirm(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        shop_name = self.tableWidget.item(row, 2).text()
        # 为商家的listing_items添加审核记录 0/1 表示通过或不通过, 后面为理由(主要是不通过的)
        appends = [1, '']
        admin(3, appends=appends, item_name=item_name, shop_name=shop_name)
        self.tableWidget.removeRow(row)

    # 审核拒绝
    def _reject(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        shop_name = self.tableWidget.item(row, 2).text()
        res, status = QInputDialog.getText(self, '', '拒绝原因')
        if not status:
            return
        appends = [0, res]
        admin(3, appends=appends, item_name=item_name, shop_name=shop_name)
        self.tableWidget.removeRow(row)


# 初始化启动
def run(start):
    start.admin = AdminUi(start)
    start.admin.show()
