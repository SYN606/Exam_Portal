from .base import *

SECRET_KEY = 'django-insecure-y#(4vz@y3=r7)!z_v@h#&#a&6p@&^rg$0!0#wph(az$pn#!+q0'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Local SQLite Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}