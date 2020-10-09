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
DEBUG = False
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
    'channels',

    # Project
    'dashboard',
    'deploy',
    'dms',
    'platforms',
    'routing',
    'automate',
    'tools',
    'sansayvcm_client',

    # Third Party
    'crispy_forms',
    'django_rq',
    'rest_framework',
    'rest_framework.authtoken',
    'sniplates',
    'widget_tweaks',
    'django_extensions'
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
redis_host = os.environ.get('REDIS_HOST', 'localhost')
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation channels_redis
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
    },
}
ASGI_APPLICATION = 'automate.routing.application'
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
            'NAME': 'd10q8ccdiidlvq',
            'USER': 'qhyghmxpdmyail',
            'PASSWORD': '8789966b1ae854a0f2ec0f84e411afaf1bce869aef1baa14b6864c90938fb824',
            'HOST': 'ec2-18-214-211-47.compute-1.amazonaws.com',
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
