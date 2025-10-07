
from django.urls import path
from . import views
from .views import ajouter_au_panier

#AJOUTER LES ROUTES DANS L'APPLICATION POUR ACCEDER AUX:
# (OFFRE, RESERVATION , ENREGISTER UNE FORMULAIRE ,SE CONNCTER ET SE DECONNECTER)

urlpatterns = [
    path('', views.home, name='home'),
    path('offres/', views.offres_list, name='offres_list'),
    path('reservation/', views.reservation_create, name = 'reservation_create'),
    #path('reservation/store', views.reservation_store, name = 'reservation_store'),
    path('register/', views.register, name = 'register'),
    path('login/', views.customLogin, name='login'),
    path('logout/', views.logOut, name = 'logout'),
    path('ajouter_au_panier/ <int:offre_id>/', views.ajouter_au_panier, name = 'ajouter_au_panier'),
    path('panier/', views.panier, name = 'panier'),
    path('e_billet/', views.e_billet, name='e_billet'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('reservation/success', views.reservation_success, name='reservation_success'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path("ebillet/pdf/<int:reservation_id>/", views.ebillet_pdf, name="ebillet_pdf"),
    path("sports", views.sports, name="sports"),
]