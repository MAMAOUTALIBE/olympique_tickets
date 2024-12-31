from io import BytesIO
from math import frexp
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Utilisateur, Offre, Reservation, Panier
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
import qrcode
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .utils import envoyer_confirmation_reservation  # Import depuis utils.py

# Create your views here.(vue pour la page d'acceuil)

def home(request):
    return render(request, 'tickets_bah/home.html')
# vue pour afficher la liste des offres

def offres_list(request):
    offres = Offre.objects.all()
    return render(request, 'tickets_bah/offres_list.html', {'offres':offres})

#Poteger les pages necessitant une authentification
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return HttpResponseRedirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

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

#CREER LES VUES POUR: INSCRIPTION, CONNEXION, DECONNEXION

#1 INSCRIPTION
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Ne sauvegarde pas encore dans la base
            user.set_password(form.cleaned_data['password'])  # Hash le mot de passe
            user.save()  # Sauvegarde dans la base de données
            return redirect('login')  # Redirige vers la page de connexion
    else:
        form = RegisterForm()
    return render(request, 'tickets_bah/register.html', {'form': form})


#2 CONNEXION
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = Utilisateur.objects.get(email=email)
                if user.check_password(password):
                    request.session['user_id'] = user.id # STOCKER L'UTILISATEUR
                    return redirect('home')
            except Utilisateur.DoesNotExist:
                pass
        return HttpResponse("email ou mot de passe incorrect")
    else:
        form = LoginForm()
    return render(request, 'tickets_bah/login.html', {'form': form})

#3DECONNEXION
def logout(request):
    logout(request)
    return redirect('login')

#GENERATION DE QR CODE AVEC LES BILLETS
def generate_qr_code(reservation):
    qr_dara = f"{reservation.utilisateur.cle_utilisateur} - {reservation.cle_billet}"
    qr = qrcode.make(qr_dara)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f"qrcode_{reservation.id}.png")

#CREER LA RESERVATION
def reservation_create(request):
    if request.method == 'POST':
        if 'user_id' not in request.session:  # Vérifie si l'utilisateur est connecté
            return redirect('login')

        utilisateur = get_object_or_404(Utilisateur, id=request.session['user_id'])
        offre = get_object_or_404(Offre, id=request.POST.get('offre_id'))

        # Créer une clé unique pour la réservation
        cle_billet = str(uuid.uuid4())[:12]

        # Créer la réservation
        reservation = Reservation.objects.create(
            utilisateur=utilisateur,
            offre=offre,
            cle_billet=cle_billet
        )

        # Générer et sauvegarder le QR code
        reservation.generate_qr_code()
        reservation.save()

        # Envoyer l'e-mail de confirmation
        envoyer_confirmation_reservation(utilisateur, reservation)

        return render(request, 'tickets_bah/e_billet.html', {'reservation': reservation})

    return render(request, 'tickets_bah/reservation_form.html')


#vue pour ajouter une offre dans le panier
def ajouter_au_panier(request, offre_id):
    if 'user_id' not in request.session:  #verifier si l'utilisateur est connecter
        return redirect('login')
    utilisateur = get_object_or_404(Utilisateur, id=request.session['user_id'])
    offre = get_object_or_404(Offre, id=offre_id)

    #ajouter l'offre au panier
    Panier.objects.create(utilisateur=utilisateur, offre=offre)
    return redirect('panier') # redirige vers la page du panier

#VUE POUR AFFICHER LAE PANIER
def panier(request):
    if 'user_id' not in request.session: return redirect('login')
    utilisateur = get_object_or_404(Utilisateur, id=request.session['user_id'])
    panier_items = Panier.objects.filter(utilisateur=utilisateur)

    return render(request, 'tickets_bah/panier.html', {})

# UNE FONCTION POUE ENVOYER EMEIL DE CONFIRMATION





