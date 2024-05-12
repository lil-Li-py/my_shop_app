from db.modules import Shopkeepers


def call_shopkeeper(username, pwd='', register=False, update=False, log_out=False, **kwargs):
    shopkeeper = Shopkeepers(username, pwd)
    if register:
        shopkeeper.save()
        return
    if update:
        if pwd:
            shopkeeper.update(password=shopkeeper.pwd)
        else:
            shopkeeper.update(**kwargs)
        return
    if log_out:
        shopkeeper.log_out()
        return
    return shopkeeper.login_check()
