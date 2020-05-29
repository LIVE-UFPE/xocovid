"""
Django settings for covidWeb project.

Generated by 'django-admin startproject' using Django 3.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

"""DEBUG = True

# TODO explicar isso aqui
if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    # mimetypes.add_type("application/vue", ".vue", True)"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GOOGLE_RECAPTCHA_SECRET_KEY = '6LcTWegUAAAAAJNd65xHuZoiQOm5UzrU0Ym4isFX'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$_(q*+!(u(ll90!r9^3uppqp03*n&#rq=@!!=$&o=5@t-uvw_7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost',
    'xocovid.herokuapp.com',
    'covidsgis.herokuapp.com'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'background_task',
    'App'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'covidWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'covidWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'd1ibhu3tsi7ghj'),
        'USER': os.environ.get('DB_USER', 'tslryogoucxpjv'),
        'PASSWORD': os.environ.get('DB_PASS', '32432025'),
        'HOST': '172.20.36.172',
        'PORT': '5432'
    }
}"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'App/static/map'),
    os.path.join(BASE_DIR, 'App/static/filter'),
    os.path.join(BASE_DIR, 'App/static/leaflet-heatmap'),
    os.path.join(BASE_DIR, 'App/static/heatmap'),
    os.path.join(BASE_DIR, 'App/static/login'),
    os.path.join(BASE_DIR, 'App/static/stateMap'),
    os.path.join(BASE_DIR, 'App/static/states'),
    os.path.join(BASE_DIR, 'App/static/cityMap'),
    os.path.join(BASE_DIR, 'App/static/dataCidade'),
    os.path.join(BASE_DIR, 'App/static/homeCityMap'),
    os.path.join(BASE_DIR, 'App/static/statesData'),
]
