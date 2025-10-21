import base64
import json
import logging
import os
import ssl
import uuid
from datetime import timedelta
from io import BytesIO
from math import frexp

import pyotp
import qrcode
import stripe
import sweetify
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.password_validation import validate_password
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.test.utils import override_settings
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from .forms import LoginForm, RegisterForm, StyledPasswordResetForm
from .models import (LoginVerificationToken, Offre, Panier, Reservation,
                     SportEvent, Utilisateur, UtilisateurPayment,
                     StripeCheckoutSession)
from .utils import envoyer_confirmation_reservation
from tickets_bah.core.permissions import (is_admin, is_super_admin,
                                          user_is_authenticate)

stripe.api_key = settings.STRIPE_SECRET_KEY
LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES = getattr(
    settings, "LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES", 10
)
HOLD_MINUTES = max(1, int(getattr(settings, "RESERVATION_HOLD_MINUTES", 10)))

logger = logging.getLogger(__name__)


# Create your views here.(vue pour la page d'acceuil)

def home(request):
    return render(request, 'tickets_bah/home.html')


def _send_login_verification_email(request, utilisateur):
    """Envoie un lien de confirmation pour une connexion MFA par email."""
    LoginVerificationToken.objects.filter(utilisateur=utilisateur, used=False).update(used=True)

    token = LoginVerificationToken.objects.create(
        utilisateur=utilisateur,
        token=uuid.uuid4().hex,
    )

    confirmation_url = request.build_absolute_uri(
        reverse("login_email_confirm", args=[token.token])
    )
    context = {
        "utilisateur": utilisateur,
        "confirmation_url": confirmation_url,
        "expiration_minutes": LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES,
    }
    subject = "Confirmez votre connexion"
    message = render_to_string("tickets_bah/login_email_verification_email.txt", context)

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [utilisateur.email])
    except ssl.SSLCertVerificationError:
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend",
            EMAIL_FILE_PATH=str(settings.EMAIL_FILE_PATH),
        ):
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [utilisateur.email])

    return token


#Poteger les pages necessitant une authentification
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return HttpResponseRedirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

# vue pour afficher la liste des offres
def offres_list(request):
    offres = Offre.objects.all()
    return render(request, 'tickets_bah/offres_list.html', {'offres':offres})

@user_passes_test(user_is_authenticate, login_url="/login")
def reservation_create(request):
    """Affiche le formulaire de réservation"""
    offre = None
    offre_id = request.GET.get('offre_id')
    
    if offre_id:
        offre = get_object_or_404(Offre, id=offre_id)

    return render(request, 'tickets_bah/reservation_form.html', {'offre': offre, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,})


#CREER LES VUES POUR: INSCRIPTION, CONNEXION, DECONNEXION

#1 INSCRIPTION
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            nom = form.cleaned_data.get("nom")
            prenom = form.cleaned_data.get("prenom")
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password")

            try:
                validate_password(raw_password, user=Utilisateur(email=email))
            except ValidationError as exc:
                for message in exc.messages:
                    form.add_error("password", message)
                sweetify.error(
                    request,
                    "Mot de passe trop faible, merci de respecter les exigences de sécurité.",
                    button="Ok",
                    timer=5000,
                )
            else:
                cle_utilisateur = str(uuid.uuid4())[:12]
                utilisateur = Utilisateur.objects.create_user(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    password=raw_password,
                    cle_utilisateur=cle_utilisateur,
                )
                utilisateur.is_email_verified = True
                utilisateur.email_verification_token = None
                utilisateur.is_totp_enabled = False
                utilisateur.totp_secret = None
                utilisateur.save(update_fields=[
                    "is_email_verified",
                    "email_verification_token",
                    "is_totp_enabled",
                    "totp_secret",
                ])
                sweetify.success(
                    request,
                    "Inscription effectuée ! Connectez-vous pour finaliser la configuration.",
                    button="Ok",
                    timer=5000,
                )
                return redirect("login")
        else:
            errors = " ".join([f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()])
            sweetify.error(request, f"Inscription échouée ! : {errors}", button='Ok', timer=5000)
    else:
        form = RegisterForm()
    return render(request, 'tickets_bah/register.html', {'form': form})


#2 CONNEXION
def customLogin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authentifier l'utilisateur avec Django
            user = authenticate(request, username=email, password=password)

            if user is not None:
                redirect_target = "dashboard" if user.default_role == "super-admin" else "home"
                request.session["post_login_redirect"] = redirect_target
                request.session["pending_email_user_id"] = user.id
                _send_login_verification_email(request, user)
                sweetify.info(
                    request,
                    "Confirmez votre connexion via le lien envoyé par email.",
                    button="Ok",
                    timer=5000,
                )
                return redirect("login_email_sent")
            else:
                sweetify.error(request, "Email ou mot de passe incorrect.", button="Ok", timer=4000)

    else:
        form = LoginForm()

    return render(request, 'tickets_bah/login.html', {'form': form})


def login_email_sent(request):
    pending_user_id = request.session.get("pending_email_user_id")
    if not pending_user_id:
        sweetify.warning(request, "Veuillez vous authentifier d'abord.", button="Ok")
        return redirect("login")

    utilisateur = Utilisateur.objects.filter(id=pending_user_id).first()
    context = {
        "user_email": utilisateur.email if utilisateur else "",
        "expiration_minutes": LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES,
    }
    return render(request, "tickets_bah/login_email_sent.html", context)


def login_email_confirm(request, token):
    try:
        login_token = LoginVerificationToken.objects.select_related("utilisateur").get(token=token)
    except LoginVerificationToken.DoesNotExist:
        sweetify.error(request, "Lien de confirmation invalide.", button="Ok", timer=5000)
        return redirect("login")

    if login_token.used:
        sweetify.error(request, "Ce lien a déjà été utilisé.", button="Ok", timer=5000)
        return redirect("login")

    if login_token.is_expired():
        login_token.used = True
        login_token.save(update_fields=["used"])
        sweetify.error(
            request,
            "Le lien de confirmation a expiré. Veuillez vous reconnecter.",
            button="Ok",
            timer=5000,
        )
        return redirect("login")

    login_token.used = True
    login_token.save(update_fields=["used"])

    utilisateur = login_token.utilisateur
    pending_user_id = request.session.pop("pending_email_user_id", None)
    if pending_user_id and pending_user_id != utilisateur.id:
        sweetify.error(
            request,
            "Cette confirmation ne correspond pas à la session en cours.",
            button="Ok",
            timer=5000,
        )
        return redirect("login")

    request.session["mfa_user_id"] = utilisateur.id

    if utilisateur.is_totp_enabled and utilisateur.totp_secret:
        sweetify.success(
            request,
            "Email confirmé. Entrez le code généré par votre application d'authentification.",
            button="Ok",
            timer=5000,
        )
        return redirect("mfa_verify")

    sweetify.info(
        request,
        "Email confirmé. Configurez maintenant votre code de sécurité via l'application d'authentification.",
        button="Ok",
        timer=6000,
    )
    return redirect("mfa_setup")


class CustomPasswordResetView(PasswordResetView):
    template_name = "tickets_bah/password_reset.html"
    email_template_name = "tickets_bah/password_reset_email.html"
    subject_template_name = "tickets_bah/password_reset_subject.txt"
    form_class = StyledPasswordResetForm
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ssl.SSLCertVerificationError:
            sweetify.warning(
                self.request,
                "Erreur de certificat SSL détectée. L'email a été enregistré localement dans 'sent_emails'.",
                button="Ok",
                timer=6000,
            )
            with override_settings(
                EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend",
                EMAIL_FILE_PATH=str(settings.EMAIL_FILE_PATH),
            ):
                return super().form_valid(form)


def verify_email(request, token):
    try:
        utilisateur = Utilisateur.objects.get(email_verification_token=token)
    except Utilisateur.DoesNotExist:
        sweetify.error(
            request,
            "Lien de vérification invalide ou déjà utilisé.",
            button="Ok",
            timer=5000,
        )
        return redirect("login")

    if utilisateur.is_email_verified:
        sweetify.info(
            request,
            "Votre adresse email est déjà vérifiée. Connectez-vous pour continuer.",
            button="Ok",
            timer=4000,
        )
        return redirect("login")

    utilisateur.is_email_verified = True
    utilisateur.email_verification_token = None
    utilisateur.save(update_fields=["is_email_verified", "email_verification_token"])
    sweetify.success(
        request,
        "Adresse email confirmée ! Vous pouvez maintenant vous connecter.",
        button="Ok",
        timer=4000,
    )
    return redirect("login")


def _get_pending_mfa_user(request):
    user_id = request.session.get("mfa_user_id")
    if not user_id:
        return None
    try:
        return Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return None


def mfa_setup(request):
    utilisateur = _get_pending_mfa_user(request)
    if not utilisateur:
        sweetify.error(
            request,
            "Veuillez vous authentifier pour activer la vérification en deux étapes.",
            button="Ok",
        )
        return redirect("login")

    if not utilisateur.totp_secret:
        utilisateur.totp_secret = pyotp.random_base32()
        utilisateur.save(update_fields=["totp_secret"])

    totp = pyotp.TOTP(utilisateur.totp_secret)
    provisioning_uri = totp.provisioning_uri(name=utilisateur.email, issuer_name="Jeux Olympiques")
    qr_image = qrcode.make(provisioning_uri)
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        if totp.verify(code, valid_window=1):
            utilisateur.is_totp_enabled = True
            utilisateur.save(update_fields=["is_totp_enabled"])
            login(request, utilisateur)
            redirect_target = request.session.pop("post_login_redirect", "home")
            request.session.pop("mfa_user_id", None)
            sweetify.success(
                request,
                "Vérification en deux étapes activée avec succès.",
                button="Ok",
                timer=4000,
            )
            return redirect(redirect_target)
        sweetify.error(request, "Code invalide. Veuillez réessayer.", button="Ok", timer=4000)

    context = {
        "qr_code_base64": qr_base64,
        "secret": utilisateur.totp_secret,
    }
    return render(request, "tickets_bah/mfa_setup.html", context)


def mfa_verify(request):
    utilisateur = _get_pending_mfa_user(request)
    if not utilisateur:
        sweetify.error(request, "Session expirée. Veuillez vous reconnecter.", button="Ok")
        return redirect("login")

    if not utilisateur.is_totp_enabled or not utilisateur.totp_secret:
        return redirect("mfa_setup")

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        totp = pyotp.TOTP(utilisateur.totp_secret)
        if totp.verify(code, valid_window=1):
            login(request, utilisateur)
            redirect_target = request.session.pop("post_login_redirect", "home")
            request.session.pop("mfa_user_id", None)
            sweetify.success(request, "Authentification réussie.", button="Ok", timer=3000)
            return redirect(redirect_target)
        sweetify.error(request, "Code invalide. Veuillez réessayer.", button="Ok", timer=4000)

    return render(request, "tickets_bah/mfa_verify.html")


#3 DECONNEXION
def logOut(request):
    logout(request)
    request.session.pop("mfa_user_id", None)
    request.session.pop("post_login_redirect", None)
    messages.success(request, 'Vous êtes bien déconnectés')
    return HttpResponseRedirect(reverse('login'))



#vue pour ajouter une offre dans le panier
@user_passes_test(user_is_authenticate, login_url="/login")
def ajouter_au_panier(request, offre_id):
    if request.user.is_authenticated:
        user = request.user
        utilisateur = get_object_or_404(Utilisateur, id=user.id)
        offre = get_object_or_404(Offre, id=offre_id)

        # Supprimer l'offre existante si elle existe
        Panier.objects.filter(utilisateur=utilisateur).delete()

        # Ajouter la nouvelle offre
        Panier.objects.create(utilisateur=utilisateur, offre=offre)
        sweetify.success(request, "Offre ajoutée au panier avec succès !", button='Ok', timer=3000)

        return redirect('panier')


#VUE POUR AFFICHER LE PANIER
@user_passes_test(user_is_authenticate, login_url="/login")
def panier(request):
    if request.user.is_authenticated:
        user = request.user
        utilisateur = get_object_or_404(Utilisateur, id=user.id)
        panier_items = Panier.objects.filter(utilisateur=utilisateur)

        context = {
            "panier_items": panier_items
        }
        return render(request, 'tickets_bah/panier.html', context) 



def _generate_ticket_key():
    """Génère une clé de billet courte unique."""
    for _ in range(5):
        candidate = uuid.uuid4().hex[:12]
        if not Reservation.objects.filter(cle_billet=candidate).exists():
            return candidate
    return uuid.uuid4().hex


def _hold_cache_key(session_id: str) -> str:
    return f"ticket_hold:{session_id}"


def _cleanup_expired_holds(offre: Offre, now=None):
    reference_time = now or timezone.now()
    expired_qs = StripeCheckoutSession.objects.filter(
        offre=offre,
        is_completed=False,
        hold_expires_at__isnull=False,
        hold_expires_at__lte=reference_time,
    )
    expired_ids = list(expired_qs.values_list("stripe_session_id", flat=True))
    deleted, _ = expired_qs.delete()
    if deleted:
        for session_id in expired_ids:
            cache.delete(_hold_cache_key(session_id))


def _active_hold_quantity(offre: Offre, now=None) -> int:
    reference_time = now or timezone.now()
    total = (
        StripeCheckoutSession.objects.filter(
            offre=offre,
            is_completed=False,
            hold_expires_at__gt=reference_time,
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )
    return int(total)


def _upsert_hold_cache(session_id: str, quantity: int, expires_at):
    ttl_seconds = max(60, HOLD_MINUTES * 60)
    cache.set(
        _hold_cache_key(session_id),
        {"quantity": quantity, "expires_at": expires_at.isoformat()},
        ttl_seconds,
    )


def _finalize_checkout_session(stripe_session):
    """
    Idempotent handler used by le webhook Stripe et la redirection success.
    Crée la réservation et marque la session comme complétée.
    """
    session_id = stripe_session.get("id")
    metadata = stripe_session.get("metadata") or {}
    utilisateur_id = metadata.get("utilisateur_id") or stripe_session.get("client_reference_id")
    offre_id = metadata.get("offre_id")
    raw_quantity = metadata.get("quantity", "1")

    if not session_id or not utilisateur_id or not offre_id:
        raise ValueError("Checkout session metadata manquante.")

    try:
        utilisateur_id = int(utilisateur_id)
        offre_id = int(offre_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("Métadonnées Stripe invalides.") from exc

    try:
        quantity_from_metadata = int(raw_quantity)
    except (TypeError, ValueError):
        quantity_from_metadata = 1
    quantity_from_metadata = max(1, quantity_from_metadata)

    with transaction.atomic():
        checkout_session, _ = StripeCheckoutSession.objects.select_for_update().get_or_create(
            stripe_session_id=session_id,
            defaults={
                "utilisateur_id": utilisateur_id,
                "offre_id": offre_id,
                "quantity": quantity_from_metadata,
            },
        )

        if checkout_session.utilisateur_id != utilisateur_id or checkout_session.offre_id != offre_id:
            raise ValueError("Session Stripe associée à un autre utilisateur ou une autre offre.")

        if checkout_session.is_completed and checkout_session.reservation_id:
            return checkout_session.reservation

        utilisateur = checkout_session.utilisateur
        offre = Offre.objects.select_for_update().get(id=offre_id)

        now = timezone.now()
        _cleanup_expired_holds(offre, now=now)

        quantity = max(1, checkout_session.quantity or quantity_from_metadata)
        if offre.places_restantes < quantity:
            raise ValueError("Plus de places disponibles pour finaliser cette réservation.")

        payment_intent_id = stripe_session.get("payment_intent")
        amount_total = stripe_session.get("amount_total") or int(offre.prix * quantity * 100)
        currency = (stripe_session.get("currency") or "eur").upper()

        payment_method_id = None
        last4 = None
        expiry_date = None

        if payment_intent_id:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                payment_method_id = payment_intent.payment_method
                customer_id = payment_intent.customer
                if customer_id and not utilisateur.stripe_customer_id:
                    utilisateur.stripe_customer_id = customer_id
                    utilisateur.save(update_fields=["stripe_customer_id"])

                if payment_intent.charges and payment_intent.charges.data:
                    charge = payment_intent.charges.data[0]
                    card_info = charge.payment_method_details.get("card") if charge.payment_method_details else None
                    if card_info:
                        last4 = card_info.get("last4")
                        exp_month = card_info.get("exp_month")
                        exp_year = card_info.get("exp_year")
                        if exp_month and exp_year:
                            expiry_date = f"{exp_month}/{exp_year}"
            except Exception as exc:
                logger.warning("Impossible de récupérer les détails de paiement Stripe %s: %s", payment_intent_id, exc)

        offre.reserver_places(quantity)

        reservation = Reservation.objects.create(
            utilisateur=utilisateur,
            offre=offre,
            cle_billet=_generate_ticket_key(),
        )
        reservation.generate_qr_code()
        reservation.save()

        UtilisateurPayment.objects.create(
            utilisateur=utilisateur,
            offre=offre,
            quantity=quantity,
            price=amount_total,
            currency=currency,
            has_paid=True,
            stripe_customer_id=utilisateur.stripe_customer_id,
            stripe_payment_method_id=payment_method_id,
            last4=last4,
            expiry_date=expiry_date,
        )

        checkout_session.quantity = quantity
        checkout_session.is_completed = True
        checkout_session.reservation = reservation
        checkout_session.stripe_payment_intent_id = payment_intent_id
        checkout_session.hold_expires_at = now
        checkout_session.save(
            update_fields=[
                "quantity",
                "is_completed",
                "reservation",
                "stripe_payment_intent_id",
                "hold_expires_at",
                "updated_at",
            ]
        )

    cache.delete(_hold_cache_key(session_id))
    envoyer_confirmation_reservation(utilisateur, reservation)

    return reservation


# Intégration de Stripe pour les réservations de tickets
@user_passes_test(user_is_authenticate, login_url="/login")
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée."}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Corps de requête invalide."}, status=400)

    utilisateur = request.user
    utilisateur_id = data.get("utilisateur_id") or utilisateur.id
    offre_id = data.get("offre_id")
    quantity_raw = data.get("quantity", 1)

    try:
        utilisateur_id = int(utilisateur_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Paramètres utilisateur ou quantité invalides."}, status=400)

    try:
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    if utilisateur_id != utilisateur.id:
        return JsonResponse({"error": "Utilisateur non autorisé."}, status=403)

    if not offre_id:
        return JsonResponse({"error": "Offre manquante."}, status=400)

    offre = get_object_or_404(Offre, id=offre_id)

    try:
        if not utilisateur.stripe_customer_id:
            customer = stripe.Customer.create(
                email=utilisateur.email,
                name=f"{utilisateur.nom} {utilisateur.prenom}",
            )
            utilisateur.stripe_customer_id = customer.id
            utilisateur.save(update_fields=["stripe_customer_id"])
    except stripe.error.StripeError as exc:
        logger.exception("Erreur lors de la création du client Stripe pour %s: %s", utilisateur.email, exc)
        return JsonResponse({"error": "Création du client de paiement impossible."}, status=502)

    metadata = {
        "utilisateur_id": str(utilisateur.id),
        "offre_id": str(offre.id),
        "quantity": str(quantity),
    }

    idempotency_key = f"checkout_{utilisateur.id}_{offre.id}_{uuid.uuid4().hex}"
    placeholder_session_id = f"pending-{uuid.uuid4().hex}"
    now = timezone.now()
    hold_expires_at = now + timedelta(minutes=HOLD_MINUTES)

    with transaction.atomic():
        offre_locked = Offre.objects.select_for_update().get(id=offre.id)
        _cleanup_expired_holds(offre_locked, now=now)
        active_hold_qty = _active_hold_quantity(offre_locked, now=now)
        available = offre_locked.places_restantes - active_hold_qty
        if available < quantity:
            return JsonResponse(
                {"error": "Plus de places disponibles pour cette offre.", "remaining": max(0, available)},
                status=409,
            )

        StripeCheckoutSession.objects.filter(
            utilisateur=utilisateur,
            offre=offre_locked,
            is_completed=False,
        ).delete()

        placeholder = StripeCheckoutSession.objects.create(
            utilisateur=utilisateur,
            offre=offre_locked,
            stripe_session_id=placeholder_session_id,
            quantity=quantity,
            hold_expires_at=hold_expires_at,
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": offre.nom,
                        },
                        "unit_amount": int(offre.prix * 100),
                    },
                    "quantity": quantity,
                },
            ],
            mode="payment",
            customer=utilisateur.stripe_customer_id,
            client_reference_id=str(utilisateur.id),
            success_url=request.build_absolute_uri(
                reverse("reservation_success")
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("panier")),
            metadata=metadata,
            idempotency_key=idempotency_key,
        )
    except stripe.error.StripeError as exc:
        logger.exception("Création de la session Checkout Stripe échouée: %s", exc)
        with transaction.atomic():
            StripeCheckoutSession.objects.filter(pk=placeholder.pk).delete()
        return JsonResponse({"error": "Impossible de démarrer le paiement."}, status=502)

    update_time = timezone.now()
    new_expiration = update_time + timedelta(minutes=HOLD_MINUTES)

    with transaction.atomic():
        placeholder_locked = StripeCheckoutSession.objects.select_for_update().get(pk=placeholder.pk)
        offre_locked = Offre.objects.select_for_update().get(id=offre.id)
        _cleanup_expired_holds(offre_locked, now=update_time)

        active_hold_qty = _active_hold_quantity(offre_locked, now=update_time)
        if placeholder_locked.hold_active:
            active_hold_qty -= placeholder_locked.quantity

        available = offre_locked.places_restantes - active_hold_qty
        if available < placeholder_locked.quantity:
            placeholder_locked.delete()
            cache.delete(_hold_cache_key(placeholder_session_id))
            return JsonResponse(
                {"error": "Plus de places disponibles pour cette offre.", "remaining": max(0, available)},
                status=409,
            )

        placeholder_locked.stripe_session_id = checkout_session.id
        placeholder_locked.hold_expires_at = new_expiration
        placeholder_locked.save(update_fields=["stripe_session_id", "hold_expires_at", "updated_at"])

    _upsert_hold_cache(checkout_session.id, quantity, new_expiration)

    return JsonResponse({"id": checkout_session.id})


@user_passes_test(user_is_authenticate, login_url="/login")
def reservation_success(request):
    """Affiche l'état du paiement Stripe et redirige vers le billet une fois confirmé."""
    session_id = request.GET.get("session_id")
    if not session_id:
        sweetify.error(request, "Session de paiement manquante.", button="Ok", timer=4000)
        return redirect("panier")

    try:
        checkout_session = StripeCheckoutSession.objects.select_related("reservation", "utilisateur").get(
            stripe_session_id=session_id
        )
    except StripeCheckoutSession.DoesNotExist:
        checkout_session = None

    if checkout_session and checkout_session.utilisateur_id != request.user.id:
        sweetify.error(request, "Cette session de paiement ne vous appartient pas.", button="Ok", timer=4000)
        return redirect("panier")

    if checkout_session and checkout_session.is_completed and checkout_session.reservation:
        request.session["reservation_id"] = checkout_session.reservation_id
        sweetify.success(request, "Paiement confirmé !", button="Ok", timer=3000)
        return redirect("e_billet")

    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)
    except Exception as exc:
        logger.warning("Impossible de récupérer la session Stripe %s: %s", session_id, exc)
        sweetify.info(
            request,
            "Votre paiement est en cours de validation. Réessayez dans quelques secondes.",
            button="Ok",
            timer=6000,
        )
        return render(
            request,
            "tickets_bah/reservation_pending.html",
            {"session_id": session_id},
        )

    metadata = stripe_session.get("metadata") or {}
    if str(metadata.get("utilisateur_id")) != str(request.user.id):
        sweetify.error(request, "Session de paiement invalide.", button="Ok", timer=5000)
        return redirect("panier")

    if stripe_session.get("payment_status") == "paid":
        try:
            reservation = _finalize_checkout_session(stripe_session)
        except Exception as exc:
            logger.exception("Erreur lors de la finalisation de la session %s: %s", session_id, exc)
            sweetify.error(
                request,
                "Une erreur est survenue lors de la finalisation du paiement. Contactez le support.",
                button="Ok",
                timer=6000,
            )
            return redirect("panier")

        request.session["reservation_id"] = reservation.id
        sweetify.success(request, "Paiement confirmé !", button="Ok", timer=3000)
        return redirect("e_billet")

    sweetify.info(
        request,
        "Votre paiement est en cours de validation.",
        button="Ok",
        timer=6000,
    )
    return render(
        request,
        "tickets_bah/reservation_pending.html",
        {"session_id": session_id},
    )

 

@user_passes_test(user_is_authenticate, login_url="/login")
def e_billet(request):
    reservation_id = request.session.get('reservation_id')

    if not reservation_id:
        sweetify.error(request, "Aucune réservation trouvée.", button='Ok')
        return redirect('home')  # Redirection en cas d'erreur

    reservation = get_object_or_404(Reservation, id=reservation_id)
    context = {
        "reservation": reservation
    }
    return render(request, "tickets_bah/e_billet.html", context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        logger.warning("Requête webhook Stripe sans signature.")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.warning("Payload Stripe invalide.")
        return HttpResponse(status=400)
    
    except stripe.error.SignatureVerificationError:
        logger.warning("Signature Stripe invalide.")
        return HttpResponse(status=400)
    
    event_type = event.get('type')

    if event_type in {'checkout.session.completed', 'checkout.session.async_payment_succeeded'}:
        stripe_session = event['data']['object']
        try:
            reservation = _finalize_checkout_session(stripe_session)
            logger.info(
                "Session Stripe %s finalisée pour l'utilisateur %s",
                stripe_session.get("id"),
                reservation.utilisateur_id,
            )
        except Exception as exc:
            logger.exception(
                "Erreur lors du traitement du webhook Stripe pour la session %s: %s",
                stripe_session.get("id"),
                exc,
            )
            return HttpResponse(status=500)
    elif event_type == 'checkout.session.async_payment_failed':
        stripe_session = event['data']['object']
        logger.warning("Paiement Stripe échoué pour la session %s", stripe_session.get("id"))

    return HttpResponse(status=200)


#vue pour mettre le E-billet en pdf
def _link_callback(uri, rel):
    """
    Convertit les URLs statiques/médias en chemins absolus pour xhtml2pdf.
    """
    # Static
    result = finders.find(uri.replace(settings.STATIC_URL, '')) if uri.startswith(settings.STATIC_URL) else None
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        path = os.path.realpath(result[0])
        return path

    # Media
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        if os.path.isfile(path):
            return path

    # Absolu (http/https) -> laisse tel quel (QR code en URL absolue)
    return uri

def ebillet_pdf(request, reservation_id):
    from .models import Reservation
    reservation = Reservation.objects.get(id=reservation_id)

    html = render_to_string("tickets_bah/ebillet_pdf.html", {"reservation": reservation, "request": request})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="E-Billet_{reservation.cle_billet}.pdf"'

    pisa_status = pisa.CreatePDF(
        src=html, dest=response, link_callback=_link_callback, encoding='UTF-8'
    )

    if pisa_status.err:
        return HttpResponse("Erreur de génération PDF", status=500)
    return response

def sports(request):
    query = request.GET.get("q", "").strip()
    events = SportEvent.objects.all()

    if query:
        events = events.filter(
            Q(nom__icontains=query)
            | Q(discipline__icontains=query)
            | Q(lieu__icontains=query)
        )

    context = {
        "events": events,
        "query": query,
        "events_count": events.count(),
    }
    return render(request, 'tickets_bah/sports.html', context)
