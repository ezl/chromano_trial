from django.conf.urls.defaults import *
from django.contrib import admin
from settings import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'^' + MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
)

MENU_ITEMS = (
    ('Home', 'main', '/'),
    ('Monitor', 'monitor', '/pricewatch'),
    ('Plans', 'plans', '/plans'),
    ('Register', 'register', '/register/free'),
)
context = lambda page: {'MENU_ITEMS': MENU_ITEMS, 'page': page}

urlpatterns += patterns('django.views.generic.simple',
    (r'^$', 'direct_to_template', {'template': 'main.html', 'extra_context': context('main')}),
    (r'^pricewatch/?$', 'direct_to_template', {'template': 'pricewatch.html', 'extra_context': context('monitor')}),
    (r'^plans/?$', 'direct_to_template', {'template': 'plans.html', 'extra_context': context('plans')}),
    (r'^register/(?P<plan>\w+)/?$', 'direct_to_template', {'template': 'register.html', 'extra_context': context('register')}),
)
