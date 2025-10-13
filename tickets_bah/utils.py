import logging
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def envoyer_confirmation_reservation(utilisateur, reservation):
    sujet = "Confirmation de votre réservation"
    message = f"""
    Bonjour {utilisateur.nom},

    Votre réservation a bien été effectuée avec succès.

    Voici les détails de votre réservation :
    - Offre : {reservation.offre.nom}
    - Clé du billet : {reservation.cle_billet}

    Merci d'avoir choisi nos services !

    Cordialement,
    L'équipe des Jeux Olympiques
    """
    destinataire = [utilisateur.email]

    # Envoi de l'e-mail
    try:
        send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, destinataire)
    except Exception as exc:
        # Ne pas bloquer le flux si l'envoi d'email échoue (ex: SMTP mal configuré)
        logger.warning("Échec de l'envoi de l'email de confirmation : %s", exc)


def envoyer_email_verification(utilisateur, request):
    """
    Envoie le lien de validation de l'adresse email à l'utilisateur.
    """
    if not utilisateur.email_verification_token:
        logger.warning(
            "Impossible d'envoyer l'email de vérification: aucun token pour l'utilisateur %s",
            utilisateur.email,
        )
        return

    verification_url = request.build_absolute_uri(
        reverse("verify_email", args=[utilisateur.email_verification_token])
    )
    sujet = "Vérification de votre adresse email"
    message = (
        f"Bonjour {utilisateur.prenom},\n\n"
        "Merci pour votre inscription. Pour finaliser la création de votre compte, "
        "merci de confirmer votre adresse email en cliquant sur le lien suivant :\n\n"
        f"{verification_url}\n\n"
        "Ce lien expirera lorsque vous aurez confirmé votre compte. "
        "Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.\n\n"
        "Cordialement,\n"
        "L'équipe Jeux Olympiques"
    )
    try:
        send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [utilisateur.email])
    except Exception as exc:
        logger.warning("Échec de l'envoi de l'email de vérification : %s", exc)
