from config.settings.base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cyberdoc',
        'USER': 'postgres',
        "PASSWORD": "0576",
        "HOST": "localhost",
        "PORT": 5432,
    }
}