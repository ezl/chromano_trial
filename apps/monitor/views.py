from datetime import datetime, timedelta
from functools import wraps

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson
from annoying.decorators import render_to, ajax_request

from forms import RegistrationForm, ProfileForm, ActivationForm, UpgradeForm
from models import SubscriptionPlan, FinancialInstrument, \
    PriceWatch, UserProfile
from urls import MENU_ITEMS_AUTHENTICATED, MENU_ITEMS_UNAUTHENTICATED
from ext.yfinance import YahooFinance
from ext.gvoice import GoogleVoiceLogin, TextSender
import random


def site_page(function):
    @wraps(function)
    def wrapper(request, **kwargs):
        res = function(request, **kwargs)
        if isinstance(res, dict):
            if request.user.is_authenticated():
                res['menu'] = MENU_ITEMS_AUTHENTICATED
            else:
                res['menu'] = MENU_ITEMS_UNAUTHENTICATED
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
        count = profile.count_watches
    except UserProfile.DoesNotExist:
        profile = None  # admin account
        count = 9999

    return {
        'watchlist': qs.order_by('-position', '-id'),
        'watchcount': qs.filter(active=True).count(),
        'near_limit': count < 5,
        'reached_limit': not count,
        'plan': profile and profile.plan,
        'title': 'Dashboard',
        'profile': profile,
    }


@render_to('plans.html')
@site_page
def plans(request):
    """ Subscription plans page """
    qs = SubscriptionPlan.objects.all()
    return {
        'plans': qs.order_by('-billing_period_price'),
        'title': 'Plans & Pricing',
    }


@render_to('register.html')
@site_page
def register(request, plan_name=''):
    """ Registration page """
    DEFAULT_PLAN = "Trader"
    plan = SubscriptionPlan.objects.get(name__iexact=plan_name or DEFAULT_PLAN)
    if request.method == 'POST':
        form = RegistrationForm(plan.free, data=request.POST)
        if form.is_valid():
            # save user
            user = form.save(commit=False)
            user.email = form.cleaned_data['username']
            user.save()
            # save profile
            profile = UserProfile()
            profile.user = user
            profile.plan = plan
            profile.reset()
            # send welcome email
            if plan.billing_period_price:
                tpl = loader.get_template('email_welcome_paid.txt')
            else:
                tpl = loader.get_template('email_welcome_free.txt')
            first_charge_date = datetime.now().date() + timedelta(days=30)
            ctx = Context({'user': user, 'profile': profile,
                           'first_charge_date': first_charge_date,})
            subject, message = tpl.render(ctx).split('\n', 1)
            send_mail(subject=subject, message=message,
                from_email=settings.ACCOUNTS_EMAIL,
                recipient_list=[user.email])
            # log in automatically
            login(request, authenticate(
                username=user.email,
                password=form.cleaned_data['password1'],
            ))
            return HttpResponseRedirect(reverse(monitor))
    else:
        form = RegistrationForm(plan.free)

    return {
        'plan': plan,
        'title': 'Sign up!',
        'form': form,
    }


@login_required
@render_to('profile.html')
@site_page
def profile(request):
    """ Edit profile settings """
    profile = UserProfile.objects.get(user=request.user)
    
    if 'email' in request.POST:
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save_email(profile.user)
            form.save_phone(profile)
            return HttpResponseRedirect('?')
    else:
        form = ProfileForm()
        form.initial.update({
            'email': profile.user.email,
            'phone': profile.phone_number,
        })
        
    if 'old_password' in request.POST:
        form_p = PasswordChangeForm(request.user, request.POST)
        if form_p.is_valid():
            form_p.save()
            return HttpResponseRedirect('?pc=1')
    else:
        form_p = PasswordChangeForm(request.user)
    
    return {
        'user': request.user,
        'form': form,
        'form_p': form_p,
        'title': 'Settings',
        'profile': profile,
        'updated_pass': request.GET.get('pc'),
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
        'title': 'Activate Phone',
    }


@login_required
@render_to('upgrade.html')
@site_page
def upgrade(request):
    """ Upgrade/downgrade subscription plan """
    plans = SubscriptionPlan.objects.all().order_by('billing_period_price')
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        plan = SubscriptionPlan.objects.get(id=request.POST['plan_id'])
        form = UpgradeForm(plan.free, data=request.POST)
        if form.is_valid():
            profile.plan = plan
            profile.save()
            return HttpResponseRedirect(reverse(upgrade))
    else:
        plan = profile.plan
        form = UpgradeForm(plan.free)

    return {
        'plans': plans,
        'profile': profile,
        'form': form,
        'plan_record': plan,
        'title': 'Modify your plan',
    }


@login_required
@render_to('close_account.html')
@site_page
def close_account(request):
    """ Mark account as closed """
    close = 'close' in request.POST
    if close:
        user = request.user
        user.username = user.username + " cancelled " + str(datetime.now())
        user.is_active = False
        user.save()
        logout(request)

    return {
        'closed': close,
        'title': 'Close Account',
    }


@render_to('login.html')
@site_page
def signin(request):
    """ Start session """
    if request.method == 'POST':
        get = lambda k: request.POST[k]
        args = dict(username=get('email'), password=get('password'))
        user = authenticate(**args)
        if user and user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse(monitor))
        email, error = get('email'), True
    else:
        email, error = '', False
    
    return {
        'email': email,
        'error': error,
        'title': 'Log in',
    }


def signout(request):
    """ Close session """
    logout(request)
    return HttpResponseRedirect(reverse(main))


@render_to('privacy.html')
@site_page
def privacy(request):
    return {'title': 'Privacy policy'}


@render_to('tour.html')
@site_page
def tour(request):
    return {'title': 'Feature tour'}


@render_to('contact.html')
@site_page
def contact(request):
    return {'title': 'Get in touch'}


@render_to('help.html')
@site_page
def help(request):
    return {'title': 'Help'}


# ----- ajax views -----

@ajax_request
def check(request, symbols=''):
    """ Fetch symbol information """
    convert = lambda x: dict(symbol=x.symbol, name=x.name, price=x.last_price)
    symbols = set([s.upper() for s in symbols.split(',')])

    # fetch item records, detect new and expired items
    items = list(FinancialInstrument.objects.filter(symbol__in=symbols))
    items_insert, items_update, items_map = set(), set(), set()
    for item in items:
        if datetime.now() - item.last_update >= timedelta(minutes=1):
            items_update.add(item)
        items_map.add(item.symbol)
    for symbol in symbols:
        if symbol not in items_map:
            items_insert.add(FinancialInstrument(symbol=symbol))

    # load content from yahoo API
    items_query = items_update.union(items_insert)
    if items_query:
        yapi = YahooFinance()
        yapi.query_multiple([x.symbol for x in items_query])
        for item in items_query:
            info = yapi[item.symbol]
            item.last_price = info.price
            if not info.price:
                break
            if item.symbol in items_insert:
                item.name = info.name
                items.append(item)
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
def send_phone_activation(request):
    profile = UserProfile.objects.get(user=request.user)

    # generate random token
    chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPRSTUVWXY3456789'
    token = ''.join(random.sample(chars, 6))

    profile.phone_activation_string = token
    profile.phone_verified = False
    profile.save()

    # send text message
    user_, pass_ = settings.GOOGLE_VOICE_USER, settings.GOOGLE_VOICE_PASS
    gvoice = GoogleVoiceLogin(user_, pass_)

    sender = TextSender(gvoice.opener, gvoice.key)
    sender.text = 'Your activation key: %s' % token
    sender.send_text(profile.phone_number)
    return json_or_redirect(request, {})


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
        profile = None  # admin account

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
                return error("Low alert must be below current price")
        if upper_bound is not None:
            upper_bound = float(upper_bound)
            if upper_bound <= info.price:
                return error("High alert must be above current price")
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
        watch.set_alert_flags(profile)
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
        'alert_email': watch.alert_email,
        'alert_phone': watch.alert_phone,
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

    if field == 'active' or field.startswith('alert'):
        # verify user subscription
        allow_toggle = True
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not item.active and not profile.count_watches:
                allow_toggle = False
        except UserProfile.DoesNotExist:
            profile = None  # admin account

        # verify boundaries
        price = item.instrument.last_price
        if item.lower_bound and price < item.lower_bound:
            return json_or_redirect(request, {'breach': 'Lower'})
        if item.upper_bound and price > item.upper_bound:
            return json_or_redirect(request, {'breach': 'Upper'})

        # verify alert options
        if field == 'alert_email' and profile and not profile.user.email:
            return json_or_redirect(request, {'alert': 'email'})
        if field == 'alert_phone' and profile and not profile.phone_verified:
            return json_or_redirect(request, {'alert': 'phone'})

    # update database record
    if field == 'active':
        if allow_toggle:
            item.active = not item.active
        value = item.active
    elif field == 'lower':
        item.lower_bound = value and float(value)
    elif field == 'upper':
        item.upper_bound = value and float(value)
    elif field.startswith('alert'):
        value = not getattr(item, field)
        setattr(item, field, value)

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
