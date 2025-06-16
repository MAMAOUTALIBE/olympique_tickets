from django.urls import path
from . import views

app_name = 'political_party'

urlpatterns = [
    path('', views.index, name='index'),
]
