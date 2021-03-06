from . import ENV
from environ import Path

# GENERAL

ROOT_DIR = Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('backend')
TEMPLATES_DIR = ROOT_DIR.path('frontend', 'templates')
COMPONENTS_DIR = TEMPLATES_DIR.path('components')
ROOT_URLCONF = 'config.urls'

DEBUG = ENV.bool('DJANGO_DEBUG')
ADMIN_URL = ENV.str('DJANGO_ADMIN_URL')
SECRET_KEY = ENV.str('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ENV.list('DJANGO_ALLOWED_HOSTS')
SITE_URL = ENV.str('SITE_URL', ALLOWED_HOSTS[0])

DATABASES = {'default': ENV.db('DATABASE_URL')}
DATABASES['default']['ATOMIC_REQUESTS'] = True

TIME_ZONE = ENV.str('TZ', 'UTC')
LANGUAGE_CODE = 'ru-ru'
USE_I18N = True
USE_L10N = False
USE_TZ = True

VERSION = ENV.str('VERSION', 'none')

# APPS

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'crispy_forms',
    'sorl.thumbnail',
    'mathfilters',
    'backend.core',
]

# MIDDLEWARE

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# TEMPLATES

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(TEMPLATES_DIR)],
        'OPTIONS': {
            'debug': DEBUG,
            'libraries': {
                'core.tags': 'backend.core.tags',
            },
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# STATIC & MEDIA

STATIC_URL = '/static/'
STATIC_LOCATION = 'static'
STATIC_ROOT = str(ROOT_DIR.path('static'))
STATICFILES_DIRS = [str(ROOT_DIR.path('frontend', 'static'))]

MEDIA_URL = '/media/'
MEDIA_LOCATION = 'media'
MEDIA_ROOT = str(ROOT_DIR.path('frontend', 'media'))

# PASSWORDS

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    # {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# EMAIL

EMAIL_CONFIG = ENV.email('EMAIL_URL')

EMAIL_BACKEND = EMAIL_CONFIG['EMAIL_BACKEND']
EMAIL_HOST = EMAIL_CONFIG['EMAIL_HOST']
EMAIL_PORT = EMAIL_CONFIG['EMAIL_PORT']
EMAIL_HOST_USER = EMAIL_CONFIG['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = EMAIL_CONFIG.get('EMAIL_USE_TLS', False)
EMAIL_FILE_PATH = str(ROOT_DIR.path('emails'))

DEFAULT_FROM_EMAIL = '"SittingKnitting" <service@sittingknitting.ru>'
TEMPLATED_EMAIL_TEMPLATE_DIR = 'emails/'
TEMPLATED_EMAIL_FILE_EXTENSION = 'html'

# MISC

AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'
CRISPY_TEMPLATE_PACK = 'bootstrap3'

FIXTURE_DIRS = [str(ROOT_DIR.path('fixtures'))]

AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
