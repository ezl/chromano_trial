import site
site.addsitedir('/home/quotesentinel/env/lib/python2.6/site-packages')

import sys
sys.path.append('/home/quotesentinel')
sys.path.append('/home/quotesentinel/quotesentinel')
sys.path.append('/home/quotesentinel/quotesentinel/apps')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'quotesentinel.deploy-settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
