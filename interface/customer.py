from db.modules import Customers


def call_customer(username: str, pwd='', register=False, update=False, lou_out=False, **kwargs) -> None | tuple:
    """
    用户交互层
    :param username: 用户名
    :param pwd: 密码
    :param register: 注册
    :param update: 数据更新
    :param lou_out: 注销
    :param kwargs: 待更新的数据
    :return: None/检索的数据
    """
    customer = Customers(username, pwd)
    # 顾客注册
    if register:
        customer.save()
        return
    # 顾客信息更新
    if update:
        if pwd:
            customer.update(password=customer.pwd)
        else:
            customer.update(**kwargs)
        return
    # 顾客注销
    if lou_out:
        customer.log_out()
        return
    # 顾客信息检索
    return customer.login_check()


