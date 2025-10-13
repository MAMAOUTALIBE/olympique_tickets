
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import StyledSetPasswordForm
from .views import CustomPasswordResetView, ajouter_au_panier

#AJOUTER LES ROUTES DANS L'APPLICATION POUR ACCEDER AUX:
# (OFFRE, RESERVATION , ENREGISTER UNE FORMULAIRE ,SE CONNCTER ET SE DECONNECTER)

urlpatterns = [
    path('', views.home, name='home'),
    path('offres/', views.offres_list, name='offres_list'),
    path('reservation/', views.reservation_create, name = 'reservation_create'),
    #path('reservation/store', views.reservation_store, name = 'reservation_store'),
    path('register/', views.register, name = 'register'),
    path('login/', views.customLogin, name='login'),
    path('login/email-envoye/', views.login_email_sent, name='login_email_sent'),
    path('login/confirmation/<str:token>/', views.login_email_confirm, name='login_email_confirm'),
    path('logout/', views.logOut, name = 'logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('mfa/setup/', views.mfa_setup, name='mfa_setup'),
    path('mfa/verify/', views.mfa_verify, name='mfa_verify'),
    path("mot-de-passe-oublie/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "mot-de-passe-oublie/confirme/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="tickets_bah/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reinitialisation/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="tickets_bah/password_reset_confirm.html",
            form_class=StyledSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reinitialisation/terminee/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="tickets_bah/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path('ajouter_au_panier/ <int:offre_id>/', views.ajouter_au_panier, name = 'ajouter_au_panier'),
    path('panier/', views.panier, name = 'panier'),
    path('e_billet/', views.e_billet, name='e_billet'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('reservation/success', views.reservation_success, name='reservation_success'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path("ebillet/pdf/<int:reservation_id>/", views.ebillet_pdf, name="ebillet_pdf"),
    path("sports", views.sports, name="sports"),
]
