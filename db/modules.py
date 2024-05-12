from lib.common import encrypt
from db.db_handler import logging_check, account_entry, update_data, log_out


class BaseModel:
    def __init__(self, username='', pwd=''):
        self.username = username
        self.mode = 0
        self.pwd = encrypt(pwd+username)

    def login_check(self):
        return logging_check(self)

    def save(self):
        account_entry(self)

    def update(self, **kwargs):
        update_data(self, **kwargs)

    def log_out(self):
        log_out(self)


# 顾客
class Customers(BaseModel):
    def __init__(self, username, pwd):
        super().__init__(username, pwd)
        self.mode = 0


# 商家
class Shopkeepers(BaseModel):
    def __init__(self, username, pwd):
        super().__init__(username, pwd)
        self.mode = 1


# 物品类
class Items(BaseModel):
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

    def save(self, *args):
        self.item_info = args
        account_entry(self)
