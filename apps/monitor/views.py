from datetime import datetime, timedelta
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from annoying.decorators import render_to, ajax_request

from forms import RegistrationForm, ProfileForm, ActivationForm
from models import SubscriptionPlan, FinancialInstrument, \
    PriceWatch, UserProfile
from urls import MENU_ITEMS
from ext.yfinance import YahooFinance


def site_page(function):
    @wraps(function)
    def wrapper(request, **kwargs):
        res = function(request, **kwargs)
        if isinstance(res, dict):
            res['menu'] = MENU_ITEMS
            res['page'] = function.__name__
        return res
    return wrapper


@render_to('main.html')
@site_page
def main(request):
    """ Main page """
    return {}


@login_required
@render_to('monitor.html')
@site_page
def monitor(request):
    """ Monitor page """
    qs = PriceWatch.objects.filter(user=request.user)
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None  # admin account

    return {
        'watchlist': qs.order_by('-position', '-id'),
        'watchcount': qs.count(),
        'near_limit': profile and profile.count_watches < 5,
        'plan': profile and profile.plan,
        'profile': profile,
    }


@render_to('plans.html')
@site_page
def plans(request):
    """ Subscription plans page """
    qs = SubscriptionPlan.objects.all()
    return {
        'plans': qs.order_by('billing_period_price'),
    }


@render_to('register.html')
@site_page
def register(request, plan_name=''):
    """ Registration page """
    plan = SubscriptionPlan.objects.get(name__iexact=plan_name or 'free')
    free = not plan.billing_period_price

    if request.method == 'POST':
        form = RegistrationForm(free, data=request.POST)
        if form.is_valid():
            get = lambda k: form.cleaned_data[k]
            user = form.save(commit=False)
            user.email = get('email')
            user.save()
            profile = UserProfile()
            profile.user = user
            profile.plan = plan
            profile.reset()
            args = dict(username=get('username'), password=get('password1'))
            login(request, authenticate(**args))
            return HttpResponseRedirect(reverse(monitor))
    else:
        form = RegistrationForm(free)

    return {
        'plan': plan,
        'form': form,
    }


@login_required
@render_to('profile.html')
@site_page
def profile(request):
    """ Edit profile settings """
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save_email(profile.user)
            form.save_phone(profile)
    else:
        form = ProfileForm()
        form.initial.update({
            'email': profile.user.email,
            'phone': profile.phone_number,
        })
    
    return {
        'form': form,
        'profile': profile,
    }


@login_required
@render_to('verify.html')
@site_page
def verify(request):
    """ Edit profile settings """
    if request.method == 'POST':
        form = ActivationForm(request.POST)
        if form.is_valid():
            form.profile.phone_verified = True
            form.profile.save()
            return HttpResponseRedirect(reverse(profile))
    else:
        form = ActivationForm()
        form.initial['phone'] = request.GET.get('n')
    
    return {
        'form': form,
    }


@login_required
@render_to('upgrade.html')
@site_page
def upgrade(request):
    """ Upgrade/downgrade subscription plan """
    return {}


@render_to('login.html')
@site_page
def signin(request):
    """ Start session """
    if request.method == 'POST':
        get = lambda k: request.POST[k]
        args = dict(username=get('username'), password=get('password'))
        user = authenticate(**args)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse(monitor))
        username, error = get('username'), True
    else:
        username, error = '', False
    
    return {
        'username': username,
        'error': error,
    }


def signout(request):
    """ Close session """
    logout(request)
    return HttpResponseRedirect(reverse(main))


# ----- ajax views -----

@ajax_request
def check(request, symbols=''):
    """ Fetch symbol information """
    convert = lambda x: dict(symbol=x.symbol, name=x.name, price=x.last_price)
    symbols = set([s.upper() for s in symbols.split(',')])

    # fetch item records, detect new and expired items
    items = list(FinancialInstrument.objects.filter(symbol__in=symbols))
    items_update, items_map = [], {}
    for item in items:
        if datetime.now() - item.last_update >= timedelta(minutes=1):
            items_update.append(item)
        items_map[item.symbol] = item
    for symbol in symbols:
        if symbol not in items_map:
            items_update.append(FinancialInstrument(symbol=symbol))

    # load content from yahoo API
    if items_update:
        yapi = YahooFinance()
        yapi.query_multiple([x.symbol for x in items_update])
        for item in items_update:
            info = yapi[item.symbol]
            item.last_price = info.price
            if not info.price:
                break
            if item.symbol not in items_map:
                item.name = info.name
            item.save()

    # return values
    if not items:
        return {'error': 'NO_SYMBOL'}
    return {'data': map(convert, items)}


def json_or_redirect(request, data):
    """ Output json or redirect to previous page """
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def monitor_add(request):
    """ Add symbol (via html or ajax) """
    # fetch form data
    data = request.POST
    symbol = data.get('s').upper()
    lower_bound = data.get('l') or None
    upper_bound = data.get('h') or None
    error = lambda msg: json_or_redirect(request, {'error': msg})

    # verify user subscription
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.count_watches:
            return error("Plan limit reached")
    except UserProfile.DoesNotExist:
        pass  # admin account

    # load content from yahoo API
    yapi = YahooFinance()
    info = yapi.query_single(symbol)

    try:
        # validate input
        if not info.price:
            return error("Symbol %s not found" % symbol)
        if lower_bound is not None:
            lower_bound = float(lower_bound)
            if lower_bound >= info.price:
                return error("Low alert above current price")
        if upper_bound is not None:
            upper_bound = float(upper_bound)
            if upper_bound <= info.price:
                return error("High alert below current price")
    except ValueError:
        # output error
        return error("Invalid value")

    # create database record (instrument)
    try:
        item = FinancialInstrument.objects.get(symbol=symbol)
    except FinancialInstrument.DoesNotExist:
        item = FinancialInstrument(symbol=symbol,
            name=info.name, last_price=info.price)
        item.save()

    try:
        # get next position
        qs = PriceWatch.objects.filter(user=request.user)
        pos = 1 + (qs.aggregate(Max('position'))['position__max'] or 0)

        # create database record (watch)
        watch = PriceWatch(user=request.user, instrument=item,
            lower_bound=lower_bound, upper_bound=upper_bound, position=pos)
        watch.save()
    except IntegrityError:
        # output error
        return error("Symbol exists")

    # output result or redirect
    return json_or_redirect(request, {
        'id': watch.id,
        'symbol': symbol,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'price': info.price,
    })


@login_required
def monitor_del(request, id=0):
    """ Remove symbol (via html or ajax) """
    item = PriceWatch.objects.get(id=id, user=request.user)

    # output result or redirect
    item.delete()
    return json_or_redirect(request, {})


@login_required
def monitor_edit(request, id=0, field=''):
    """ Toggle value (via html or ajax) """
    item = PriceWatch.objects.get(id=id, user=request.user)
    value = request.GET.get('value')

    # verify user subscription
    if field == 'active':
        allow_toggle = True
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not item.active and not profile.count_watches:
                allow_toggle = False
        except UserProfile.DoesNotExist:
            pass  # admin account

    # update database record
    if field == 'active':
        if allow_toggle:
            item.active = not item.active
        value = item.active
    elif field == 'lower':
        item.lower_bound = value and float(value)
    elif field == 'upper':
        item.upper_bound = value and float(value)

    # output result or redirect
    item.save()
    return json_or_redirect(request, {'value': value})


@ajax_request
def monitor_position(request):
    """ Reposition values (ajax only) """
    id_list = map(int, reversed(request.GET['order'].split(',')))
    qs = PriceWatch.objects.filter(user=request.user)

    # update item positions
    id_map = dict([(v, k + 1) for k, v in enumerate(id_list)])
    for item in qs:
        item.position = id_map[item.id]
        item.save()

    # no output
    return {}
