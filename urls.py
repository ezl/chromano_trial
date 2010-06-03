from django.conf.urls.defaults import *
from django.contrib import admin
from settings import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'^' + MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),
    (r'^admin/', include(admin.site.urls)),
)
