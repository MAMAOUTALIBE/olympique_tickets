from django.core.mail import send_mail
from django.conf import settings

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
    send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, destinataire)
