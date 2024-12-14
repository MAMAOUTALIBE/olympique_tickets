from django.contrib import admin
from .models import Utilisateur, Offre, Reservation

#Enregistrer les models

admin.site.register(Utilisateur)
admin.site.register(Offre)
admin.site.register(Reservation)

