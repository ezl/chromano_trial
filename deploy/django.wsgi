import os
import sys

BASE_PATH = '/home/sergey/quotesentinel'
sys.path.append(BASE_PATH)
sys.path.append(BASE_PATH + '/apps')
sys.path.append(BASE_PATH + 'virtual/lib/python2.6/site-packages/')

import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'deploy-settings'
application = django.core.handlers.wsgi.WSGIHandler()
