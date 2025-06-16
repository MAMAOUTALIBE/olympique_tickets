

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("djangoAdmin/", admin.site.urls),
    path('',include('tickets_bah.urls')), #inclure les urle de lapplication tickets
    path('admin/', include('appAdmin.urls')),
    path('party/', include('political_party.urls', namespace='political_party')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
