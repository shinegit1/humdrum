import os

from .settings_base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY_PROD')

INSTALLED_APPS.extend(['django_s3_storage', 'django_ses'])

ALLOWED_HOSTS = ['www.myxfate.com']

SITE_ID = 3

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'humdrumprod',
        'USER': os.environ.get("DATABASE_USER_PROD"),
        'PASSWORD': os.environ.get("DATABASE_PASSWORD_PROD"),
        'HOST': 'humdrum.colvnr8liiph.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# Deployment checklist settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 300  # 5 minutes


EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_ACCESS_KEY_ID = os.environ.get("EMAIL_USER_PROD")
AWS_SES_SECRET_ACCESS_KEY = os.environ.get("EMAIL_PASSWORD_PROD")
DEFAULT_FROM_EMAIL = 'noreply@myxfate.com'

# django s3 static file settings
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
AWS_S3_BUCKET_NAME_STATIC = "humdrum-static-data"
AWS_S3_CUSTOM_STATIC_DOMAIN = f'{AWS_S3_BUCKET_NAME_STATIC}.s3.amazonaws.com'
AWS_S3_KEY_PREFIX_STATIC = "prod"
STATIC_URL = f'https://{AWS_S3_CUSTOM_STATIC_DOMAIN}/'
AWS_S3_MAX_AGE_SECONDS_STATIC = "94608000"

STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)

# django s3 media file settings
DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
AWS_S3_BUCKET_NAME = "humdrum-customers-data"
AWS_S3_KEY_PREFIX = "prod"
AWS_S3_CUSTOM_MEDIA_DOMAIN = f'{AWS_S3_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_MEDIA_DOMAIN}/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)
