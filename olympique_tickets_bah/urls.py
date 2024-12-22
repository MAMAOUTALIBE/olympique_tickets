

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',include('tickets_bah.urls')), #inclure les urle de lapplication tickets
]
