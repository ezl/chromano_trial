from django.conf.urls.defaults import *

MENU_ITEMS_AUTHENTICATED = (
    ('main', 'Home'),
    ('monitor', 'Monitor'),
    ('monitor', 'Help'),
    ('profile', 'Settings'),
    ('logout', 'Log out'),
)

MENU_ITEMS_UNAUTHENTICATED = (
    ('main', 'Home'),
    ('plans', 'Plans'),
    ('main', 'Tour'),
    ('plans', 'Sign Up!'),
    ('monitor', 'Log in'),
)

urlpatterns = patterns('monitor.views',
    (r'^(?:main)?$', 'main'),
    (r'^monitor/?$', 'monitor'),
    (r'^plans/?$', 'plans'),
    (r'^register/(?P<plan_name>\w*)/?$', 'register'),
    (r'^profile/?$', 'profile'),
    (r'^verify/?$', 'verify'),
    (r'^upgrade/?$', 'upgrade'),
    (r'^login/?$', 'signin'),
    (r'^logout/?$', 'signout'),
    (r'^start/?$', 'start'),
    (r'^help/?$', 'help'),
    (r'^monitor/check/(?P<symbols>[\w\.,]+)$', 'check'),
    (r'^monitor/add/?$', 'monitor_add'),
    (r'^monitor/del/(?P<id>\d+)/?$', 'monitor_del'),
    (r'^monitor/edit/(?P<id>\d+)/(?P<field>\w+)/?$', 'monitor_edit'),
    (r'^monitor/pos/?$', 'monitor_position'),
)
