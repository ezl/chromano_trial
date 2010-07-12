from settings import *
from os import path

DEBUG = False
DATABASE_NAME = path.join(path.abspath(path.dirname(__file__)),
        '..', 'apache', 'quotemonitorDB.sqlite3')

