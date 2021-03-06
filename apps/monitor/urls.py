from django.conf.urls.defaults import *

MENU_ITEMS_AUTHENTICATED = (
    ('monitor', 'Monitor'),
    ('profile', 'Settings'),
    ('help', 'Help'),
    ('logout', 'Log out'),
)

MENU_ITEMS_UNAUTHENTICATED = (
    ('tour', 'Feature Tour'),
    ('plans', 'Plans & Pricing'),
    ('register', 'Sign Up'),
    ('monitor', 'Log In'),
)

urlpatterns = patterns('monitor.views',
    (r'^$', 'main'),
    (r'^monitor/$', 'monitor'),
    (r'^plans/$', 'plans'),
    (r'^plans/reset$', 'reset_plan'),
    (r'^register/(?P<plan_name>\w*)/?$', 'register', {'SSL':True}),
    (r'^register/$', 'register', {'SSL':True}),
    # TODO: hacky.  set it so that register/ defaults to a particular plan, but can also take an input.
    (r'^profile/$', 'profile'),
    (r'^verify/$', 'verify'),
    (r'^upgrade/$', 'upgrade'),
    (r'^send_phone_activation/$', 'send_phone_activation'),
    (r'^close_account/$', 'close_account'),
    (r'^login/$', 'signin'),
    (r'^logout/$', 'signout'),
    (r'^tour/$', 'tour'),
    (r'^contact/$', 'contact'),
    (r'^help/$', 'help'),
    (r'^privacy/$', 'privacy'),
    (r'^monitor/check/(?P<symbols>[\w\.,]+)$', 'check'),
    (r'^monitor/add/?$', 'monitor_add'),
    (r'^monitor/del/(?P<id>\d+)/?$', 'monitor_del'),
    (r'^monitor/edit/(?P<id>\d+)/(?P<field>\w+)/?$', 'monitor_edit'),
    (r'^monitor/pos/?$', 'monitor_position'),
)

urlpatterns += patterns('',
    # TODO: this is stupid. these shouldn't be in the app urls
    url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template',
        {'template': 'robots.txt', 'mimetype': 'text/plain'}, name='robots',),
    url(r'^refund/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'refund.html'}, name='refund',),
    url(r'^terms/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'terms_of_service.html'}, name='terms_of_service',),
#    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'coming_soon.html'},),
)
