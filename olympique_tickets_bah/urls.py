

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin


urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoAdmin/", admin.site.urls),  # alias legacy pour compatibilité si besoin
    path('',include('tickets_bah.urls')), #inclure les urle de lapplication tickets
    path('dashboard/', include('appAdmin.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
