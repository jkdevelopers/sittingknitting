from django.core.wsgi import get_wsgi_application
# from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
from os import environ

environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.pro')

application = get_wsgi_application()
# application = Sentry(application)
