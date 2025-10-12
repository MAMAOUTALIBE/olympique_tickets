from django.urls import path, include
from appAdmin import views
from django.urls import path

urlpatterns = [
    path('', views.dashboard, name="dashboard"),

    path('offres/', views.offres, name="offres.index"),
    path('offres/create', views.createOffres, name="offres.create"),    
    path('offres/store', views.storeOffres, name="offres.store"),
    path('offres/<int:id>/edit', views.editOffres, name="offres.edit"),
    path('offres/<int:id>/update', views.updateOffres, name="offres.update"),
    path('offres/<int:id>/delete', views.deleteOffres, name="offres.delete"),

    path('reservations/', views.reservations, name="reservations.index"),
    path('reservations/<int:id>/delete', views.deleteReservations, name="reservations.delete"),

    path('paniers/', views.paniers, name="paniers.index"),
    path('paniers/<int:id>/delete', views.deletePaniers, name="paniers.delete"),


    path('utilisateurs/', views.utilisateurs, name="utilisateurs.index"),
    path('utilisateurs/<int:id>/delete', views.deleteUtilisateurs, name="utilisateurs.delete"),
    path('sports/', views.sports, name="admin_sports"),
    path('sports/<int:id>/delete', views.deleteSport, name="admin_sports.delete"),

]
