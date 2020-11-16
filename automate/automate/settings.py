"""
Django settings for automate project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import json
# import ldap
import string
import random
import logging
import dj_database_url

# from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


#
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SETTINGS_FILE = os.path.abspath(os.path.join(BASE_DIR, "settings.json"))
# if os.path.isfile(SETTINGS_FILE):
#   with open(SETTINGS_FILE) as f:
#       env = json.loads(f.read())
# else:
#   raise Exception('Could not open settings.json')


# =====================================
# Core settings
# =====================================
SECRET_KEY = "hdhdhdhdue38939"
DEBUG = True
'''if 'secret_key' in env['django']:
    SECRET_KEY = env['django']['secret_key']
else:
    SECRET_KEY = ''.join([random.SystemRandom().choice("{}{}{}".format(string.ascii_letters, string.digits, string.punctuation)) for i in range(50)])
    env['django']['secret_key'] = SECRET_KEY
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(env, f, sort_keys=True, indent=4)
DEBUG = env['django']['debug']
ALLOWED_HOSTS = env['django']['allowed_hosts']'''

ALLOWED_HOSTS = ['*']
# =====================================
# Application definition
# =====================================
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Project
    'dashboard',
    'deploy',
    'dms',
    'platforms',
    'routing',
    'automate',
    'tools',
    'sansayvcm_client',
    'reseller',

    # Third Party
    'crispy_forms',
    'django_rq',
    'rest_framework',
    'rest_framework.authtoken',
    'sniplates',
    'widget_tweaks',
    'django_extensions',
    'django_celery_results',
    'django_celery_beat',
    'django_select2'
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'automate.middleware.TimezoneMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

]
ROOT_URLCONF = 'automate.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['{}/templates'.format(BASE_DIR)],
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
WSGI_APPLICATION = 'automate.wsgi.application'

# =====================================
# Authentication
# =====================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# logger = logging.getLogger('django_auth_ldap')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


# =====================================
# Database
# =====================================
# DATABASES = {
#    'default': {
#        'ENGINE': env['database']['engine'],
#        'NAME': env['database']['db_name'],
#        'USER': env['database']['username'],
#        'PASSWORD': env['database']['password'],
#        'HOST': env['database']['host'],
#        'PORT': env['database']['port'],
# 
#    }
# }

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dbdva6l9frlj4n',
            'USER': 'hsijukvgyrmriz',
            'PASSWORD': '07bc3c22b4c27d2f6e0798eca842c64d8988baf29f7b7decfdc77fbd43464a58',
            'HOST': 'ec2-34-232-24-202.compute-1.amazonaws.com',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'toolbox',
            'USER': 'toolbox',
            'PASSWORD': 'Layerstack1!',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
#
# DATABASES = {
# 'default': {
#     'ENGINE': 'django.db.backends.postgresql_psycopg2',
#     'NAME': 'postgres',
#     'USER': 'postgres',
#     'PASSWORD': 'postgres',
#     'HOST': 'localhost',
#     'PORT': '5432',
# }
# }
# =====================================
# Platforms
# =====================================
# PLATFORMS = env['platforms']


# =====================================
# Password validation
# =====================================
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

# =====================================
# Where to redirect after login (and no next reference)
# =====================================
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
LOGOUT_REDIRECT_URL = '/accounts/login/'

# =====================================
# Internationalization
# =====================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =====================================
# Static files (CSS, JavaScript, Images)
# =====================================
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static/'),)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = '{}/media/'.format(BASE_DIR)
PROTECTED_URL = '/protected/'
PROTECTED_ROOT = '{}/protected/'.format(BASE_DIR)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =====================================
# Redis Queues
# =====================================

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT-TIMEOUT': 360,
    }
}
'''RQ_QUEUES = {
    'default': {
        'HOST': env['redis']['host'],
        'PORT': env['redis']['port'],
        'DB': env['redis']['db'],
    },
    'tool': {
        'HOST': env['redis']['host'],
        'PORT': env['redis']['port'],
        'DB': env['redis']['db'],
    }'''
#    'deploy': {
#        'HOST': env['redis']['host'],
#        'PORT': env['redis']['port'],
#        'DB': env['redis']['db'],
#    },
'''}'''

# =====================================
# Django REST Framework
# =====================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # added django_filters.rest_framework.DjangoFilterBackend'
    # after installing django_filters
    # and removed 'rest_framework.filters.DjangoFilterBackend',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',

        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 1000,
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# =====================================
# Email
# =====================================
'''EMAIL_HOST = env['email']['smtp_server']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = env['email']['from_address']
SERVER_EMAIL = env['email']['from_address']


# =====================================
# Admins & Managers
# =====================================
ADMINS = env['admins']
MANAGERS = ADMINS'''

# celery configuration
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
if not DEBUG:
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
else:
    CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# django setting.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SELECT2_CACHE_BACKEND = "select2"

CRISPY_TEMPLATE_PACK = 'bootstrap4'

