from django.conf.urls.defaults import *

MENU_ITEMS = (
    ('main', 'Home'),
    ('monitor', 'Monitor'),
    ('plans', 'Plans'),
    ('register', 'Register'),
)

urlpatterns = patterns('monitor.views',
    (r'^(?:main)?$', 'main'),
    (r'^monitor/?$', 'monitor'),
    (r'^plans/?$', 'plans'),
    (r'^register/(?P<plan_name>\w*)/?$', 'register'),
    (r'^login/?$', 'signin'),
    (r'^logout/?$', 'signout'),
    (r'^monitor/check/(?P<symbol>[\w\.]+)$', 'check'),
    (r'^monitor/add/?$', 'monitor_add'),
    (r'^monitor/del/(?P<id>\d+)/?$', 'monitor_del'),
    (r'^monitor/edit/(?P<id>\d+)/(?P<field>\w+)/?$', 'monitor_edit'),
    (r'^monitor/pos/?$', 'monitor_position'),
)
