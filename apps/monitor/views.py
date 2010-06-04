from datetime import datetime, timedelta
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect
from annoying.decorators import render_to, ajax_request

from models import SubscriptionPlan, FinancialInstrument, PriceWatch
from urls import MENU_ITEMS
from ext.yfinance import YahooFinance


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
    qs = PriceWatch.objects.filter(user=request.user)
    return {
        'watchlist': qs.order_by('-id'),
    }


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


@ajax_request
def check(request, symbol=''):
    """ Fetch symbol information """
    convert = lambda x: dict(symbol=symbol, name=x.name, price=x.last_price)

    # check database first (not to stress API)
    try:
        item = FinancialInstrument.objects.get(symbol=symbol)
        if datetime.now() - item.last_update < timedelta(minutes=1):
            return convert(item)
    except FinancialInstrument.DoesNotExist:
        item = FinancialInstrument(symbol=symbol)

    # load content from yahoo API
    yapi = YahooFinance()
    info = yapi.query_single(symbol)
    if not info.price:
        return {'error': 'NO_SYMBOL'}

    # update database
    item.name = info.name
    item.last_price = info.price
    item.save()
    return convert(item)


def monitor_add(request):
    """ Add symbol (via html or ajax) """
    # fetch form data
    data = request.POST
    symbol = data.get('s')
    lower_bound = data.get('l') or None
    upper_bound = data.get('h') or None
    ajax = not data.get('html')

    # load content from yahoo API
    yapi = YahooFinance()
    info = yapi.query_single(symbol)

    try:
        # validate input
        if not info.price:
            raise ValueError
        if lower_bound is not None:
            lower_bound = float(lower_bound)
        if upper_bound is not None:
            upper_bound = float(lower_bound)
    except ValueError:
        # output error
        if ajax:
            return HttpResponse('{error:true}')
        # ??? should print some error here
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    # create database record (instrument)
    try:
        item = FinancialInstrument.objects.get(symbol=symbol)
    except FinancialInstrument.DoesNotExist:
        item = FinancialInstrument(symbol=symbol,
            name=info.name, last_price=info.price)
        item.save()

    # create database record (watch)
    watch = PriceWatch(user=request.user, instrument=item,
        lower_bound=lower_bound, upper_bound=upper_bound)
    watch.save()

    # output result or redirect
    if ajax:
        return HttpResponse('{id:%d}' % watch.id)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    