

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('offres/', views.offres_list, name='offres_list'),
    path('reservations/', views.reservation_create, name='reservations_create'),

]