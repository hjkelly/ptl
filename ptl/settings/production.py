
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'btbajx^escm4)fx%g2!)c6-ft8eh3@lb-wvhlmb_#gz1yvvat#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
