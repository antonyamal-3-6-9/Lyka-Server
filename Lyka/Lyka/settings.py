"""
Django settings for Lyka project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q_v4=ogy&&gki0skymrd$oyp-ebk$znv8_*s=8(z&q+@5oum#a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django_celery_results',
    'django_celery_beat',
    'rest_framework',
    'corsheaders',
    'lyka_address',
    'lyka_cart',
    'lyka_categories',
    'lyka_customer',
    'lyka_order',
    'lyka_payment',
    'lyka_products',
    'lyka_seller',
    'lyka_user',
    'channels',
    'rest_framework_simplejwt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
}

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'middleware.TokenBlacklistMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CORS_EXPOSE_HEADERS = [
    'Authorization',
]

CORS_ALLOW_HEADERS = [
    'Authorization',
    'Content-Type'
]

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'



# BROKER_URL = 'amqp://guest:guest@localhost:5672/' 

ROOT_URLCONF = 'Lyka.urls'

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

WSGI_APPLICATION = 'Lyka.wsgi.application'
ASGI_APPLICATION = 'Lyka.routing.application'


SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    # Add any other JWT settings you require
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Lyka',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# CELERY_RESULT_BACKEND = 'db+postgresql://postgres:root@localhost:5432/Lyka'

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_rabbitmq.core.RabbitmqChannelLayer',
#         'CONFIG': {
#             "URL": "amqp://guest:guest@localhost:5672//",
#         },
#     },
# }


# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': "channels.layers.InMemoryChannelLayer"
#     }
# }


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}




AUTHENTICATION_BACKENDS = [
    'custom_auth_backend.EmailBackend',
    'django.contrib.auth.backends.ModelBackend'
]

AUTH_USER_MODEL = 'lyka_user.LykaUser'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

CORS_ORIGIN_ALLOW_ALL = True



# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

CELERY_TIMEZONE = "UTC"

CELERY_ALWAYS_EAGER = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

OTP_AUTH_TOKEN = "8b7ecbf5-0cfd-11ee-addf-0200cd936042"

RAZORPAY_API_KEY = "rzp_test_R79QGigrBUV08W"
RAZORPAY_API_SECRET = "E8vVAje6KvZgiFaP6z8E4wPw"

EASYPOST_API_KEY = "EZTKb48cb65bc5354fc18d42b1e73e6741ca5UwJpl0kXIqfpprz0x4elw"

PAYPAL_CLIENT_ID = "AYQ78uXRJKJsvFWNX49FPhjxCGJ-0NNx7YooDZ4Tml6h53XKYfdcqiwSUG_1TZrJbhJ2nIqS8DafBuzB"
PAYPAL_CLIENT_SECRET = "EAw2mG3kU-idbk79SbkXHcFZ4U81LHMYy9pK1jh_utgfAzo6JoKeOPNMkltMjaiZJIrmCJeDbngZwLN6"

STRIPE_API_KEY = "sk_test_51NNgMcSFoVzzDNdPTrQ2slu3CU6K7MFAwVpH3jTmtrG908AFQqMmPZlRHNNsSsXPSbRWj6RarUOI0leQfXFHQYr900EttvNCJg"
SEND_GRID_KEY = "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"
