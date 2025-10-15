import ssl
from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, TestCase

from tickets_bah.models import LoginVerificationToken, Utilisateur
from tickets_bah.views import _send_login_verification_email


class SendLoginVerificationEmailTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.utilisateur = Utilisateur.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            nom="John",
            prenom="Doe",
            cle_utilisateur="CLE-UTIL",
        )
        self.request = self.factory.get("/")

    def test_old_tokens_are_marked_used_and_new_token_created(self):
        old_token = LoginVerificationToken.objects.create(
            utilisateur=self.utilisateur,
            token="oldtoken123",
            used=False,
        )

        new_token = _send_login_verification_email(self.request, self.utilisateur)

        old_token.refresh_from_db()
        self.assertTrue(old_token.used)
        self.assertEqual(new_token.utilisateur, self.utilisateur)
        self.assertFalse(
            LoginVerificationToken.objects.exclude(id=new_token.id)
            .filter(utilisateur=self.utilisateur, used=False)
            .exists()
        )

    @patch("tickets_bah.views.send_mail", return_value=1)
    def test_send_mail_called_with_expected_arguments(self, mock_send_mail):
        _send_login_verification_email(self.request, self.utilisateur)

        mock_send_mail.assert_called_once()
        subject, message, from_email, recipients = mock_send_mail.call_args[0]
        self.assertEqual(subject, "Confirmez votre connexion")
        self.assertIsInstance(message, str)
        self.assertEqual(from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(recipients, [self.utilisateur.email])

    @patch("tickets_bah.views.send_mail")
    def test_ssl_error_triggers_filebased_fallback(self, mock_send_mail):
        mock_send_mail.side_effect = [ssl.SSLCertVerificationError(), 1]

        _send_login_verification_email(self.request, self.utilisateur)

        self.assertEqual(mock_send_mail.call_count, 2)
