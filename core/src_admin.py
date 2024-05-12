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

_translate = QtCore.QCoreApplication.translate


class AdminUi(AdminMixin, QWidget):
    def __init__(self, start):
        super(AdminUi, self).__init__()
        self.start = start
        self._win = None
        self.setupUi(self)
        self.setWindowTitle('管理员')

    def check_all_customers(self):
        info = admin(0)
        column = ['用户名', '']
        self._win = ManageWindow(info, column)
        self._win.show()

    def check_all_shopkeepers(self):
        info = admin(1)
        column = ['商家名', '']
        self._win = ManageWindow(info, column)
        self._win.show()

    def verify_listing_items(self):
        info = admin(2)
        column = ['商品名', '价格', '商家', '类型', '商品介绍', '提交时间', '']
        self._win = ManageWindow(info, column)
        self._win.show()

    def closeEvent(self, event):
        event.accept()
        time.sleep(1)
        self.start.show()


class ManageWindow(ItemsMixin, QWidget):
    def __init__(self, info, column):
        super(ManageWindow, self).__init__()
        self._info = info
        self._column = column
        self.setupUi(self)
        self._insert_items()

    def _insert_items(self):
        self.tableWidget.setColumnCount(len(self._column))
        for i in range(self.tableWidget.columnCount()):
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
            item = self.tableWidget.horizontalHeaderItem(i)
            item.setText(_translate("Form", f"{self._column[i]}"))
        row = len(self._info)
        if not row:
            return
        self.tableWidget.setRowCount(row)
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                item = QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                # 查看用户与商家窗口
                if self.tableWidget.columnCount() == 2:
                    if not j:
                        item.setText(_translate("Form", f"{self._info[i][j]}"))
                    else:
                        button = QPushButton()
                        button.setText(_translate("Form", f"{'解冻' if self._info[i][j] else '冻结'}"))
                        button.clicked.connect(partial(self._do_frozen, item))  # type:ignore
                        self.tableWidget.setCellWidget(i, j, button)
                    self.tableWidget.setItem(i, j, item)
                # 审核上架商品窗口
                else:
                    if j == 5:
                        item.setToolTip(_translate("Form", f"{self._info[i][j]}"))
                    if j == 4:
                        textedit = QTextEdit()
                        textedit.setPlainText(_translate("Form", f"{self._info[i][j]}"))
                        textedit.setEnabled(False)
                        self.tableWidget.setCellWidget(i, j, textedit)
                    elif j != 6:
                        item.setText(_translate("Form", f"{self._info[i][j]}"))
                    else:
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

    def _do_frozen(self, item):
        row = self.tableWidget.row(item)
        is_frozen = 0 if self._info[row][1] else 1
        call_customer(self._info[row][0], update=True, is_frozen=is_frozen)
        QMessageBox.information(self, '提示', '修改成功')
        self.close()

    def _confirm(self, item):
        row = self.tableWidget.row(item)
        item_name = self.tableWidget.item(row, 0).text()
        shop_name = self.tableWidget.item(row, 2).text()
        appends = [1, '']
        admin(3, appends=appends, item_name=item_name, shop_name=shop_name)
        self.tableWidget.removeRow(row)

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


def run(start):
    start.admin = AdminUi(start)
    start.admin.show()
