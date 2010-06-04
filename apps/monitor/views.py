from functools import wraps
from annoying.decorators import render_to

from models import SubscriptionPlan, FinancialInstrument, PriceWatch
from urls import MENU_ITEMS


def menu_item(function):
    @wraps(function)
    def wrapper(request, **kwargs):
        res = function(request, **kwargs)
        if isinstance(res, dict):
            res['menu'] = MENU_ITEMS
            res['page'] = function.__name__
        return res
    return wrapper


@render_to('main.html')
@menu_item
def main(request):
    """ Main page """
    return {}


@render_to('monitor.html')
@menu_item
def monitor(request):
    """ Monitor page """
    return {}


@render_to('plans.html')
@menu_item
def plans(request):
    """ Subscription plans page """
    return {}


@render_to('register.html')
@menu_item
def register(request, plan='free'):
    """ Registration page """
    return {}
