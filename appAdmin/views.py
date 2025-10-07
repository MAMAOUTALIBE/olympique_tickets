from django.shortcuts import render, redirect
from tickets_bah.core.permissions import is_super_admin, is_admin, admin_is_authenticate
from django.contrib.auth.decorators import user_passes_test
from tickets_bah.models import Utilisateur, Offre, Reservation, Panier
from django.views.decorators.csrf import csrf_exempt
import sweetify
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from appAdmin.forms import OffresForm
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tickets_bah.constance import user_role
from django.views.generic import TemplateView


# Create your views here.
@user_passes_test(admin_is_authenticate, login_url="/")
def dashboard(request):
    reservations = Reservation.objects.count()
    utilisateurs = Utilisateur.objects.count()
    offres = Offre.objects.count()

    get_reservations = Reservation.objects.order_by('-createdAt')[:10]

    count ={
        'reservations': reservations,
        'utilisateurs': utilisateurs,
        'offres': offres
    }    

    context={
        "request": request,
        "count": count,
        "get_reservations": get_reservations,
        "parent": '',
        "child": 'dashboard',
        "title": 'Dashboard',
        "subTitle": 'Dashboard',
        "dataTitle": "réservations",
        "dataSubTitle": "réservation"
    }
    return render(request=request, template_name="dashboard/dashboard.html", context=context)

# CRUD des offres

@user_passes_test(admin_is_authenticate, login_url="/login")
def offres(request):
    offres = Offre.objects.order_by('-createdAt')
    context={
        "offres": offres,
        "request": request,
        "parent": '',
        "child": 'offre',
        "title": 'Offres',
        "subTitle": 'Offre',
        "dataTitle": "offres",
        "dataSubTitle": "offre"
    }
    return render(request=request, template_name="admin/offres/index.html", context=context)


def createOffres(request):
    context = {
        "form": OffresForm(),
        "child": 'offres',
        "title": 'Ajout Offre',
        "subTitle": 'Ajout Offre',
    }
    return render(request=request, template_name="admin/offres/create.html", context=context)

@login_required
def storeOffres(request):
    if request.method == "POST":
        form = OffresForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data.get('nom')
            description = form.cleaned_data.get('description')
            prix = form.cleaned_data.get('prix')
            nombre_de_places = form.cleaned_data.get('nombre_de_places')
            offres = Offre.objects.create(
                nom = nom,
                description = description,
                prix = prix,
                nombre_de_places = nombre_de_places,
            )
            offres.save()
            sweetify.success(request, "Offre enregistrée avec succès !", button='Fermer', timer=3000)
            return redirect("offres.index")
        else:
            errors = " ".join([f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()])
            sweetify.error(request, f"Erreur lors de la création de l'offre : {errors}", button='Fermer', timer=5000)
            return redirect("offres.create")
    return HttpResponseRedirect(reverse('offres.create'))

def editOffres(request, id):
    if request.user.is_authenticated:
        offre = Offre.objects.get(id=id)
        template = loader.get_template('admin/offres/edit.html')
        context = {
            "offre": offre,
            "title": 'Modification Offre',
            "subTitle": 'Modification Offre',
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('login'))
    
@login_required
def updateOffres(request, id):
    offre = Offre.objects.get(id=id)
    if request.method == "POST":
        nom = request.POST['nom']
        description = request.POST['description']
        prix = request.POST['prix']
        nombre_de_places = request.POST['nombre_de_places']
        form = OffresForm(request.POST, instance=offre)
        if form.is_valid():
            offre.nom = nom
            offre.description = description
            offre.prix = prix
            offre.nombre_de_places = nombre_de_places
            offre.save()
            sweetify.success(request, "Offre mise à jour avec succès !", button='Fermer', timer=3000)
            return redirect("offres.index")
        else:
            errors = " ".join([f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()])
            sweetify.error(request, f"Erreur lors de la modification de l'offre : {errors}", button='Fermer', timer=5000)
            return redirect("offres.edit", id=form.instance.id)

    return HttpResponseRedirect(reverse('offres.index'))

def deleteOffres(request, id):
    try:
        offre = Offre.objects.get(id=id)
        offre.delete()
        sweetify.success(request, "Offre supprimée avec succès !", button='Fermer', timer=3000)
    except Offre.DoesNotExist:
        sweetify.error(request, "Erreur : Cette offre n'existe pas.", button='Fermer', timer=5000)
    except Exception as e:
        sweetify.error(request, f"Erreur lors de la suppression de l'offre : {str(e)}", button='Fermer', timer=5000)
    
    return redirect("offres.index")



# CRUD pour les réservations
@user_passes_test(admin_is_authenticate, login_url="/login")
def reservations(request):
    reservations = Reservation.objects.order_by('-createdAt')
    context={
        "reservations": reservations,
        "request": request,
        "parent": '',
        "child": 'reservation',
        "title": 'Réservations',
        "subTitle": 'Réservation',
        "dataTitle": "réservations",
        "dataSubTitle": "réservation"
    }
    return render(request=request, template_name="admin/reservations/index.html", context=context)

def deleteReservations(request, id):
    try:
        reservation = Reservation.objects.get(id=id)
        reservation.delete()
        sweetify.success(request, "Réservation supprimée avec succès !", button='Fermer', timer=3000)
    except Offre.DoesNotExist:
        sweetify.error(request, "Erreur : Cette réservation n'existe pas.", button='Fermer', timer=5000)
    except Exception as e:
        sweetify.error(request, f"Erreur lors de la suppression de la réservation : {str(e)}", button='Fermer', timer=5000)    
    return redirect("reservations.index")


# CRUD pour les paniers
@user_passes_test(admin_is_authenticate, login_url="/login")
def paniers(request):
    paniers = Panier.objects.order_by('-createdAt')
    context={
        "paniers": paniers,
        "request": request,
        "parent": '',
        "child": 'panier',
        "title": 'Paniers',
        "subTitle": 'Panier',
        "dataTitle": "paniers",
        "dataSubTitle": "panier"
    }
    return render(request=request, template_name="admin/paniers/index.html", context=context)

def deletePaniers(request, id):
    try:
        panier = Panier.objects.get(id=id)
        panier.delete()
        sweetify.success(request, "Panier supprimé avec succès !", button='Fermer', timer=3000)
    except Offre.DoesNotExist:
        sweetify.error(request, "Erreur : Ce panier n'existe pas.", button='Fermer', timer=5000)
    except Exception as e:
        sweetify.error(request, f"Erreur lors de la suppression du panier : {str(e)}", button='Fermer', timer=5000)    
    return redirect("paniers.index")


# CRUD pour les utilisateurs
@user_passes_test(admin_is_authenticate, login_url="/login")
def utilisateurs(request):
    utilisateurs = Utilisateur.objects.filter(default_role=user_role.user).order_by("-createdAt")
    context={
        "utilisateurs": utilisateurs,
        "request": request,
        "parent": '',
        "child": 'utilisateur',
        "title": 'Utilisateurs',
        "subTitle": 'Utilisateur',
        "dataTitle": "utilisateurs",
        "dataSubTitle": "utilisateur"
    }
    return render(request=request, template_name="admin/utilisateurs/index.html", context=context)

def deleteUtilisateurs(request, id):
    try:
        utilisateur = Utilisateur.objects.get(id=id)
        utilisateur.delete()
        sweetify.success(request, "Utilisateur supprimé avec succès !", button='Fermer', timer=3000)
    except Offre.DoesNotExist:
        sweetify.error(request, "Erreur : Cet utilisateur n'existe pas.", button='Fermer', timer=5000)
    except Exception as e:
        sweetify.error(request, f"Erreur lors de la suppression de l'utilisateur : {str(e)}", button='Fermer', timer=5000)    
    return redirect("utilisateurs.index")

# vue page sport
class SportPageView(TemplateView):
    template_name = 'admin/sports.html'


