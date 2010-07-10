# Django settings
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# ----- Administration settings
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
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
)

AUTH_PROFILE_MODULE = 'monitor.UserProfile'

# operational settings
ACCOUNTS_EMAIL = 'Accounts@quotesentinel.com'
ALERTS_EMAIL = 'PriceAlert@quotesentinel.com'
GOOGLE_VOICE_USER = 'ezlmail@gmail.com'
GOOGLE_VOICE_PASS = 'idontcare'
TRIAL_PERIOD = 30
TRIAL_WARNING = 21

try:
    from settings_local import *
except ImportError:
    pass
