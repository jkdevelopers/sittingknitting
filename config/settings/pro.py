from . import ENV

# DEFAULTS

DEFAULTS = {
    'DJANGO_DEBUG': 'False',
    'DJANGO_USE_AWS': 'True',
    'VERSION': ENV.str('HEROKU_RELEASE_VERSION', None),
}

ENV_FILE = ENV.str('ENV_FILE', None)
if ENV_FILE is not None: ENV.read_env(ENV_FILE)
for key, value in DEFAULTS.items(): ENV.ENVIRON.setdefault(key, value)

from .base import *

# SECURITY

SECURE_HSTS_SECONDS = 31536000
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# AMAZON S3

AWS_STORAGE_BUCKET_NAME = ENV('AWS_BUCKET_NAME')
AWS_S3_REGION_NAME = ENV('AWS_REGION_NAME')
AWS_ACCESS_KEY_ID = ENV('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = ENV('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = AWS_STORAGE_BUCKET_NAME + '.s3.' + AWS_S3_REGION_NAME + '.amazonaws.com'

from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage): location = STATIC_LOCATION
class MediaStorage(S3Boto3Storage): location = MEDIA_LOCATION; file_overwrite = False

STATICFILES_STORAGE = 'config.settings.pro.StaticStorage'
DEFAULT_FILE_STORAGE = 'config.settings.pro.MediaStorage'

# RAVEN & SENTRY

INSTALLED_APPS += ['raven.contrib.django.raven_compat']
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE

SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
RAVEN_CONFIG = {
    'dsn': ENV.str('SENTRY_DSN'),
    'release': VERSION,
}
