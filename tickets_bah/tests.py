from django.core import mail
from django.test import TestCase
from tickets_bah.models import Utilisateur, Offre, Reservation

# Create your tests here.
class UtilisateurTest(TestCase):
    def test_creation_utilisateur(self):
        user = Utilisateur.objects.create(
            nom="bah",
            prenom="mamadou",
            email="bah@gmail.com",
            mot_de_pass="bah",
            cle_utilisateur="CLE-12345"
        )
        self.assertEqual(user.nom, "bah")
        self.assertEqual(user.prenom, "mamadou")


#test pour envoyer email
class EmailTestCase(TestCase):
    def test_envoi_email_confirmation(self):
        utilisateur = Utilisateur.objects.create(nom="John", prenom="Doe", email="john@example.com")
        offre = Offre.objects.create(nom="Billet Solo", description="Accès pour une personne", prix=100.00)

        reservation = Reservation.objects.create(utilisateur=utilisateur, offre=offre, cle_billet="unique_key")

        # Simuler l'envoi d'e-mail
        from .views import envoyer_confirmation_reservation
        envoyer_confirmation_reservation(utilisateur, reservation)

        # Vérifier si un e-mail a été envoyé
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Confirmation de votre réservation")
        self.assertIn("Votre réservation a bien été effectuée", mail.outbox[0].body)
