from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # admin urls
    path('admin/', admin.site.urls),

    # accounts urls
    path('accounts/', include('allauth.urls')),

    # core urls
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
