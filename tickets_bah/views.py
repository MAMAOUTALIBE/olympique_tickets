from django.shortcuts import render,get_object_or_404, redirect

import tickets_bah
from .models import Offre, Reservation, Utilisateur
from django.http import HttpResponse

# Create your views here.(vue pour la page d'acceuil)

def home(request):
    return render(request, 'tickets_bah/home.html')
# vue pour afficher la liste des offres

def offres_list(request):
    offres = Offre.objects.all()
    return render(request, 'tickets_bah/offres_list.html', {'offres':offres})

#vue pour creer une reservation
def reservation_create(request):
    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur_id')
        offre_id = request.POST.get('offre_id')

        utilisateur =get_object_or_404(Utilisateur, id=utilisateur_id)
        offre = get_object_or_404(Offre, id=offre_id)

        #creer une reservation
        reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre,
        cle_billet="unique_key_here", #generer une clés ici
        qr_code="qr_code_placeholder.png" # generer le qr code
     )
        return HttpResponse("Reservation creer avec succes")
    return render(request, "tickets_bah/Reservation_form.html")


