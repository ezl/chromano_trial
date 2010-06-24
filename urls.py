from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete
from settings import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'^' + MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/', 'monitor.views.signin'),
    (r'^accounts/reset_form/', password_reset),
    (r'^accounts/reset_done/', password_reset_done),
    (r'^accounts/reset/(?P<uidb36>\w+)-(?P<token>.+)', password_reset_confirm),
    (r'^accounts/reset_complete/', password_reset_complete),
)

from monitor.urls import urlpatterns as extra
urlpatterns += extra
