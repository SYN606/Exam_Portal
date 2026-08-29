import os
from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Configure production database (e.g., PostgreSQL or SQLite from ENV)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Example: PostgreSQL for production
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'examportal_db',
#         'USER': 'db_user',
#         'PASSWORD': 'db_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Security Headers for Production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True