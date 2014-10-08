import os

from .base import *

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  #postgresql_psycopg2',
        #'HOST': 'pass-the-llama-dev.clmjmz7pusfx.us-west-2.rds.amazonaws.com',
        'NAME': os.path.join(BASE_DIR, os.pardir, 'llama.sqlite3'),
        #'USER': 'dev',
        #'PASSWORD': 'harrisonkelly',
    }
}
