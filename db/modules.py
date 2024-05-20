import time
from lib.common import encrypt
from db.db_handler import logging_check, account_entry, update_data, log_out


class BaseModel:
    """
    Customers|Shopkeepers|Items的基类
    """
    def __init__(self, username='', pwd=''):
        self.username = username
        self.pwd = encrypt(pwd+username)
        self.register_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 数据检索方法
    def login_check(self) -> None | tuple:
        return logging_check(self)

    # 数据保存方法
    def save(self) -> None:
        account_entry(self)

    # 数据更新方法
    def update(self, **kwargs) -> None:
        update_data(self, **kwargs)

    # 注销方法
    def log_out(self) -> None:
        log_out(self)


class Customers(BaseModel):
    """
    顾客类
    """
    def __init__(self, username, pwd):
        super().__init__(username, pwd)
        self.mode = 0


class Shopkeepers(BaseModel):
    """
    商家类
    """
    def __init__(self, username, pwd):
        super().__init__(username, pwd)
        self.mode = 1


class Items(BaseModel):
    """
    物品类
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.item_info = None
        self.mode = 2
        try:
            self.username = kwargs['shop_name']
            self.item_name = kwargs['item_name']
        except KeyError:
            self.username = None
            self.item_name = None
        try:
            self.sort = kwargs['sort']
        except KeyError:
            self.sort = None

    # 重写了数据保存方法
    def save(self, *args) -> None:
        self.item_info = args
        account_entry(self)
