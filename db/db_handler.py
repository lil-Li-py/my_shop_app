import sqlite3


# 初始化数据库
def init_data():
    """
    username : 用户名 :str
    password : 密码 :str
    nickname : 昵称 :str = username 可设置
    balance : 余额 :float 可设置
    points : 积分 :int 可设置
    shopping_cart : 购物车 :'[]' 内列表 [[商品名, 商家, 数量 ,添加时间], ] 其余的查询获取
    purchased_items : 已购买的物品 :'[]' 内列表嵌元组 [[商品名, 价格, 数量, 商家, 类别, 商品简介, 购买时间], ]
    register_time : 注册时间 : str 第一次注册时录入
    diy : 自定义 : '{}' 内字典 {是否自定义:bool, bg:自定义背景图地址}
    is_frozen : 是否被冻结 :bool
    """
    conn = sqlite3.connect('db/data/customer.db')
    cur = conn.cursor()
    cur.execute(
        "create table if not exists data (username text, password text, nickname text, balance real, "
        "points integer, shopping_cart text, purchased_items text, register_time text , diy text, is_frozen integer)")
    conn.commit()
    cur.close()
    """
    username : 商家名 :str
    password : 密码 :str
    income : 收入 :float
    sub_pwd : 上架或下架要验证的密码 :srt
    listing_items : 正在审核的商品 : '[]' 内列表 [[商品名, 价格, 商家, 类型, 商品介绍, 提交时间, [初始为空:审核结果]], ]
    listed_items : 已上架的商品 : '[]' 内列表 [[商品名, 价格, 商家, 类型, 商品介绍, 折扣, 上架时间], ]
    delisted_items : 已下架的商品 : '[]' 内列表 [[商品名, 价格, 商家, 类型, 商品介绍, 下架时间], ]
    register_time : 注册时间 : str 第一次注册时录入
    is_frozen : 是否被冻结 :bool
    """
    conn = sqlite3.connect('db/data/shopkeeper.db')
    cur = conn.cursor()
    cur.execute("create table if not exists data (username text, password text, income real, sub_pwd text, "
                "listing_items text, listed_items text, delisted_items text, register_time str, is_frozen integer)")
    conn.commit()
    cur.close()
    """
    item_name : 商品名 :str
    price : 价格 :float
    shop_name : 商家名 :str
    sort : 类别 :str
    description : 商品简介 :str
    discount : 折扣 :float
    change_time : 修改时间 :str
    """
    conn = sqlite3.connect('db/data/item.db')
    cur = conn.cursor()
    cur.execute("create table if not exists data (item_name text, price real, shop_name text, sort text, "
                "description text, discount real, change_time text)")
    conn.commit()
    cur.close()


# 登录检索
def logging_check(ob):
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    conn = sqlite3.connect(f'db/data/{dic[ob.mode]}.db')
    cur = conn.cursor()
    if ob.mode == 2:
        if ob.sort:
            info = cur.execute("select item_name, price, shop_name, description, discount from data where sort = ?",
                               (ob.sort,)).fetchall()
            return None, info
        try:
            info = cur.execute("select item_name, price, shop_name, sort, description, discount "
                               "from data where shop_name = ? and item_name = ?",
                               (ob.username, ob.item_name)).fetchone()
        except AttributeError:
            info = ()
        return None, info
    else:
        # 1. 用户名不存在(返回0)
        for i in cur.execute("select username from data").fetchall():
            if ob.username == i[0]:
                break
        else:
            cur.close()
            return 0, None
        # 2. 用户名存在但密码错误(返回1)
        if ob.pwd != cur.execute("select password from data where username = ?", (ob.username,)).fetchone()[0]:
            cur.close()
            return 1, None
        if not ob.mode:
            # 3. 登录成功(返回2, 并返回用户信息)
            # info 这里为一个数据元组
            info = cur.execute(
                "select username, nickname, balance, points, shopping_cart, purchased_items, "
                "diy, is_frozen from data where username = ?", (ob.username,)).fetchone()
        else:
            info = cur.execute(
                "select username, income, sub_pwd ,listing_items, listed_items, delisted_items, is_frozen from data "
                "where username = ?", (ob.username,)).fetchone()
    cur.close()
    return 2, info


# 账号录入
def account_entry(ob):
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    conn = sqlite3.connect(f'db/data/{dic[ob.mode]}.db')
    cur = conn.cursor()
    match ob.mode:
        case 0:
            cur.execute("insert into data values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (ob.username, ob.pwd, ob.username, 0, 0, "[]", "[]", ob.register_time, "{'is_diy':False}",
                         0))
        case 1:
            cur.execute("insert into data values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (ob.username, ob.pwd, 0, '', '[]', '[]', '[]', ob.register_time, 0))
        case 2:
            cur.execute("insert into data values (?, ?, ?, ?, ?, ?, ?)",
                        ob.item_info)
    conn.commit()
    cur.close()


# 用户或商家信息更新
def update_data(ob, **kwargs):
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    conn = sqlite3.connect(f'db/data/{dic[ob.mode]}.db')
    cur = conn.cursor()
    try:
        kwargs['income']
        income = cur.execute("select income from data where username = ?", (ob.username,)).fetchone()[0]
        kwargs['income'] += income
    except KeyError:
        pass
    for i in kwargs.keys():
        cur.execute(f"""update data set "{i}" = "{kwargs[i]}" where username = ?""", (ob.username,))
    conn.commit()
    cur.close()


def log_out(ob):
    dic = {0: 'customer', 1: 'shopkeeper', 2: 'item'}
    conn = sqlite3.connect(f'db/data/{dic[ob.mode]}.db')
    cur = conn.cursor()
    if ob.mode != 2:
        cur.execute("delete from data where username = ?", (ob.username,))
    else:
        if not ob.item_name:
            cur.execute("delete from data where shop_name = ?", (ob.shop_name,))
        else:
            cur.execute("delete from data where shop_name = ? and item_name = ?", (ob.username, ob.item_name))
    conn.commit()
    cur.close()


# 管理员专用
def admin(mode: int, **kwargs):
    info = []
    if not mode:
        conn = sqlite3.connect('db/data/customer.db')
        cur = conn.cursor()
        info = cur.execute("select username, is_frozen from data").fetchall()
    else:
        conn = sqlite3.connect('db/data/shopkeeper.db')
        cur = conn.cursor()
        if mode == 1:
            info = cur.execute("select username, is_frozen from data").fetchall()
        elif mode == 2:
            for i in cur.execute("select listing_items from data").fetchall():
                for j in eval(i[0]):
                    if not j[-1]:
                        info.append(j)
        elif mode == 3:
            data = eval(
                cur.execute("select listing_items from data where username = ?", (kwargs['shop_name'],)).fetchone()[0])
            for i in filter(lambda x: x[0] == kwargs['item_name'], data):
                i[-1] = kwargs['appends']
            cur.execute(f"""update data set listing_items = "{data}" where username = ?""", (kwargs['shop_name'],))
            conn.commit()
            cur.close()
            return
    cur.close()
    return info
