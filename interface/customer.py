from db.modules import Customers


def call_customer(username, pwd='', register=False, update=False, lou_out=False, **kwargs):
    customer = Customers(username, pwd)
    if register:
        customer.save()
        return
    if update:
        if pwd:
            customer.update(password=customer.pwd)
        else:
            customer.update(**kwargs)
        return
    if lou_out:
        customer.log_out()
        return
    return customer.login_check()


