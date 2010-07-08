from django.conf.urls.defaults import *

MENU_ITEMS_AUTHENTICATED = (
    ('monitor', 'Monitor'),
    ('profile', 'Settings'),
    ('logout', 'Log out'),
)

MENU_ITEMS_UNAUTHENTICATED = (
    ('tour', 'Feature Tour'),
    ('plans', 'Plans & Pricing'),
    ('contact', 'Contact'),
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
    (r'^close_account/?$', 'close_account'),
    (r'^login/?$', 'signin'),
    (r'^logout/?$', 'signout'),
    (r'^getting_started/?$', 'getting_started'),
    (r'^tour/?$', 'tour'),
    (r'^contact/?$', 'contact'),
    (r'^help/?$', 'help'),
    (r'^monitor/check/(?P<symbols>[\w\.,]+)$', 'check'),
    (r'^monitor/add/?$', 'monitor_add'),
    (r'^monitor/del/(?P<id>\d+)/?$', 'monitor_del'),
    (r'^monitor/edit/(?P<id>\d+)/(?P<field>\w+)/?$', 'monitor_edit'),
    (r'^monitor/pos/?$', 'monitor_position'),
)
