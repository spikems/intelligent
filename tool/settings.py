"""
Django settings for intelligent project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'edpqlaf+_&k&t@ltg3_n)q=5x73h$wn@a&bb8rxlq@4#gzt&-z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['112.253.2.41', '112.253.2.36', '192.168.241.8', '192.168.241.3', '192.168.241.44', '192.168.241.48', '192.168.241.43', '192.168.241.45', '192.168.241.47', '192.168.241.42']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'intelligent.urls'

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

WSGI_APPLICATION = 'intelligent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_CHARSET = 'UTF-8'

HERE = os.path.dirname(os.path.dirname(__file__))  
MEDIA_ROOT = os.path.join(HERE,'media').replace('\\','/')  
MEDIA_URL = '/media/'  
  
STATIC_ROOT = os.path.join(HERE,'static').replace('\\','/')  
STATIC_URL = '/static/'  
STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(funcName)s %(lineno)d: %(message)s'
        },
        # INFO 2016-09-03 16:25:20,067 /home/ubuntu/mysite/views.py views.py views get 29: some info...
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
             'formatter':'standard'
        },
        'file_handler': {
             'level': 'INFO',
             'class': 'logging.handlers.TimedRotatingFileHandler',
             'filename': '/home/liuhongyu/develop/intelligent/logs/intelligent.log',
             'formatter':'standard'
        },
        'semeval_handler': {
             'level': 'INFO',
             'class': 'logging.handlers.TimedRotatingFileHandler',
             'filename': '/home/liuhongyu/develop/intelligent/logs/semeval.log',
             'formatter':'standard'
        },
        'error_handler': {
             'level': 'INFO',
             'class': 'logging.handlers.TimedRotatingFileHandler',
             'filename': '/home/liuhongyu/develop/intelligent/logs/error.log',
             'formatter':'standard'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'intelligent': {
            'handlers': ['file_handler'],
            'propagate': True,
            'level':'INFO',
        },
        'semeval': {
            'handlers': ['semeval_handler'],
            'propagate': True,
            'level':'INFO',
        },
        'errinfo': {
            'handlers': ['error_handler'],
            'propagate': True,
            'level':'INFO',
        },
    }
}

