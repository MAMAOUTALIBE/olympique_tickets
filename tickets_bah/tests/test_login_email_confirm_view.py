from datetime import timedelta

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch

from tickets_bah.models import LoginVerificationToken, Utilisateur
from tickets_bah.views import login_email_confirm, login_email_sent


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class LoginEmailConfirmViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.utilisateur = Utilisateur.objects.create_user(
            email="tokenuser@example.com",
            password="StrongPass123!",
            nom="Token",
            prenom="User",
            cle_utilisateur="CLE-TOKEN",
        )

    def _attach_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    @patch("tickets_bah.views.sweetify.warning")
    def test_login_email_sent_requires_pending_user(self, mock_warning):
        request = self._attach_session_and_messages(self.factory.get("/login_email_sent"))

        response = login_email_sent(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_warning.assert_called_once()

    def test_login_email_sent_context_contains_user_email(self):
        request = self._attach_session_and_messages(self.factory.get("/login_email_sent"))
        request.session["pending_email_user_id"] = self.utilisateur.id

        response = login_email_sent(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.utilisateur.email.encode(), response.content)

    @patch("tickets_bah.views.sweetify.info")
    def test_login_email_confirm_without_totp_redirects_to_setup(self, mock_info):
        token = LoginVerificationToken.objects.create(utilisateur=self.utilisateur, token="abc123", used=False)
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/abc123"))
        request.session["pending_email_user_id"] = self.utilisateur.id

        response = login_email_confirm(request, token.token)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("mfa_setup"))
        self.assertEqual(request.session["mfa_user_id"], self.utilisateur.id)
        mock_info.assert_called_once()

    @patch("tickets_bah.views.sweetify.success")
    def test_login_email_confirm_with_totp_redirects_to_verify(self, mock_success):
        self.utilisateur.is_totp_enabled = True
        self.utilisateur.totp_secret = "SECRET"
        self.utilisateur.save(update_fields=["is_totp_enabled", "totp_secret"])

        token = LoginVerificationToken.objects.create(utilisateur=self.utilisateur, token="def456", used=False)
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/def456"))
        request.session["pending_email_user_id"] = self.utilisateur.id

        response = login_email_confirm(request, token.token)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("mfa_verify"))
        self.assertEqual(request.session["mfa_user_id"], self.utilisateur.id)
        mock_success.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_login_email_confirm_rejects_mismatched_session(self, mock_error):
        other_user = Utilisateur.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            nom="Other",
            prenom="User",
            cle_utilisateur="CLE-OTHER",
        )
        token = LoginVerificationToken.objects.create(utilisateur=self.utilisateur, token="ghi789", used=False)
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/ghi789"))
        request.session["pending_email_user_id"] = other_user.id

        response = login_email_confirm(request, token.token)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_login_email_confirm_rejects_used_token(self, mock_error):
        token = LoginVerificationToken.objects.create(utilisateur=self.utilisateur, token="usedtoken", used=True)
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/usedtoken"))

        response = login_email_confirm(request, token.token)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_login_email_confirm_rejects_expired_token(self, mock_error):
        token = LoginVerificationToken.objects.create(utilisateur=self.utilisateur, token="expired", used=False)
        LoginVerificationToken.objects.filter(id=token.id).update(
            created_at=timezone.now() - timedelta(minutes=20)
        )
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/expired"))

        response = login_email_confirm(request, token.token)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_login_email_confirm_rejects_unknown_token(self, mock_error):
        request = self._attach_session_and_messages(self.factory.get("/login/confirm/unknown"))

        response = login_email_confirm(request, "unknown")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()
