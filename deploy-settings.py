from settings import *
from os import path

DEBUG = False
# DATABASE_NAME = path.join(path.abspath(path.dirname(__file__)),
#         '..', 'apache', 'quotemonitorDB.sqlite3')
DATABASE_ENGINE = 'postgres_psycopg2'
DATABASE_NAME = 'quotesentinel'
DATABASE_USER = 'quotesentinel'
DATABASE_PASSWORD = 'acf02da87'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
    }
}
