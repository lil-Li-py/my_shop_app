from db.modules import Shopkeepers


def call_shopkeeper(username: str, pwd='', register=False, update=False, log_out=False, **kwargs) -> None | tuple:
    """
    商家交互层
    :param username: 用户名
    :param pwd: 密码
    :param register: 注册
    :param update: 数据更新
    :param log_out: 注销
    :param kwargs: 待更新的数据
    :return: None/检索的数据
    """
    shopkeeper = Shopkeepers(username, pwd)
    # 商家注册
    if register:
        shopkeeper.save()
        return
    # 商家信息更新
    if update:
        if pwd:
            shopkeeper.update(password=shopkeeper.pwd)
        else:
            shopkeeper.update(**kwargs)
        return
    # 商家注销
    if log_out:
        shopkeeper.log_out()
        return
    # 商家信息检索
    return shopkeeper.login_check()
