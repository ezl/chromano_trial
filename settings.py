# Django settings
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# ----- Administration settings
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS
INTERNAL_IPS = ('127.0.0.1',)

# ----- Database settings
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'quotemonitorDB.sqlite3'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

# ----- Django default settings
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')
MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = 'zqq)b7kh_yd681c8,o.nxtsougcyi.hdk,onthidevh2,iluo.'
ROOT_URLCONF = 'urls'

# ----- Template settings
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# ----- Applications and plugins
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django_extensions',
    'debug_toolbar',
    'monitor',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# operational settings
ALERTS_EMAIL = 'pricealert@92.114.206.30'
GOOGLE_VOICE_USER = 'ezlmail@gmail.com'
GOOGLE_VOICE_PASS = 'idontcare'

try:
    from settings_local import *
except ImportError:
    pass
