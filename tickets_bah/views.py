from math import frexp
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Utilisateur, Offre, Reservation
from .forms import ResisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
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
    if request.method == 'POST':
        form = ResisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.cle_utilisateur = "cle_utilisateur" + user.email # exemple de cle
            user.save()
            return redirect('login')
    else:
        form = ResisterForm()
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

