from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from tickets_bah.models import Offre, Reservation, Utilisateur
from tickets_bah.utils import envoyer_confirmation_reservation


class EnvoyerConfirmationReservationTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="john@example.com",
            password="secret",
            nom="John",
            prenom="Doe",
            cle_utilisateur="CLE-JOHN",
        )
        self.offre = Offre.objects.create(
            nom="Billet Duo",
            description="Accès pour deux personnes",
            prix=200,
            nombre_de_places=5,
        )
        self.reservation = Reservation.objects.create(
            utilisateur=self.utilisateur,
            offre=self.offre,
            cle_billet="unique_key",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_envoi_email_confirmation(self):
        envoyer_confirmation_reservation(self.utilisateur, self.reservation)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Confirmation de votre réservation")
        self.assertIn(self.reservation.cle_billet, message.body)
        self.assertEqual(message.to, [self.utilisateur.email])

    def test_envoi_email_exception_est_logguee(self):
        with patch("tickets_bah.utils.send_mail", side_effect=RuntimeError("SMTP indisponible")):
            with self.assertLogs("tickets_bah.utils", level="WARNING") as logs:
                envoyer_confirmation_reservation(self.utilisateur, self.reservation)

        self.assertTrue(any("SMTP indisponible" in entry for entry in logs.output))
