import os
import dj_database_url
from unipath import Path

from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.child('.env')

if Path.exists(dotenv_path):
    load_dotenv(dotenv_path)


BASE_DIR = Path(__file__).ancestor(2)

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ.get('DEBUG', False)
TESTING = False

APP_HOST = os.environ['APP_HOST']
FRONTEND_APP_HOST = os.environ['FRONTEND_APP_HOST']
FRONTEND_BASE_URL = 'http://' + FRONTEND_APP_HOST

ALLOWED_HOSTS = [APP_HOST]
BASE_URL = 'http://' + APP_HOST
CORS_ORIGIN_ALLOW_ALL = True

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_LIBS = [
    'corsheaders',
    'django_extensions',
    'suit',
    'naomi',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rq',
    'raven.contrib.django.raven_compat',
]

PROJECT_LIBS = [
    'src.core_auth',
]

INSTALLED_APPS = THIRD_PARTY_LIBS + DJANGO_APPS + PROJECT_LIBS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config()
}

AUTH_USER_MODEL = 'core_auth.User'
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.child('static')
STATICFILES_STORAGE = os.environ.get('STATICFILES_STORAGE', 'whitenoise.django.GzipManifestStaticFilesStorage')

SUIT_CONFIG = {
    'ADMIN_NAME': 'Admin',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

DEFAULT_FROM_EMAIL = 'user@service.com'
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_FILE_PATH = BASE_DIR.parent.child('naomi_tmp')
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Django RQ
REDIS_URL = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}
