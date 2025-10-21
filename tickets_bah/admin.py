from django.contrib import admin
from .models import Utilisateur, Offre, Reservation, UtilisateurPayment, SportEvent
from .views import panier


#Enregistrer les models
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email')  # Colonnes affichées dans la liste
    search_fields = ('nom', 'prenom', 'email')  # Barre de recherche
    list_filter = ('nom', 'prenom')  # Filtres disponibles dans la liste

class OffreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'nombre_de_places', 'places_restantes')
    search_fields = ('nom',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'offre', 'cle_billet')
    list_filter = ('offre',)
    search_fields = ('utilisateur__nom', 'offre__nom')

# Enregistrement avec personnalisation
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Offre, OffreAdmin)
admin.site.register(Reservation, ReservationAdmin)

admin.site.register(UtilisateurPayment)
admin.site.register(SportEvent)

