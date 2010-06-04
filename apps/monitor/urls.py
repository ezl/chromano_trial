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
    (r'^register/(?P<plan>\w*)/?$', 'register'),
)
