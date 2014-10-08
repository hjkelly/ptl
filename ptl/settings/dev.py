import os

from .base import *

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, os.pardir, 'llama.sqlite3'),
        #'HOST': '',
        #'USER': '',
        #'PASSWORD': '',
    }
}
