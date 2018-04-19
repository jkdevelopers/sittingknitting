from django.urls import path, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('backend.core.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
