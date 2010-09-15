# Django settings
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# ----- Administration settings
ADMINS = (
    ('Eric Liu, 'ericzliu@gmail.com'),
    ('Chris Chang', 'crchang@gmail.com'),
    ('Rodrigo Guzman',rodguze@gmail.com'),
)
MANAGERS = ADMINS
INTERNAL_IPS = ('76.29.38.47',)

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
    'monitor',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'monitor.SSLRedirectMiddleware',
)

AUTH_PROFILE_MODULE = 'monitor.UserProfile'

# operational settings
DEFAULT_FROM_EMAIL = "Accounts@quotesentinel.com"
ACCOUNTS_EMAIL = 'Accounts@quotesentinel.com'
ALERTS_EMAIL = 'PriceAlert@quotesentinel.com'
GOOGLE_VOICE_USER = 'ezlmail@gmail.com'
GOOGLE_VOICE_PASS = 'idontcare'
CHEDDAR_GETTER_USER = 'quotesentinel@gmail.com'
CHEDDAR_GETTER_PASS = 'acf02da87'
CHEDDAR_GETTER_PRODUCT = 'QUOTE_SENTINEL'
TRIAL_PERIOD = 7
TRIAL_WARNING = 2

try:
    from settings_local import *
except ImportError:
    pass
