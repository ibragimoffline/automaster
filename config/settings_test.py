import os

os.environ.setdefault('DB_NAME', 'test_automaster')
os.environ.setdefault('DB_USER', 'test')
os.environ.setdefault('DB_PASSWORD', 'test')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-not-for-production')

from config.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'automaster-tests',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

DEBUG = False

MEDIA_ROOT = BASE_DIR / 'test_media'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
