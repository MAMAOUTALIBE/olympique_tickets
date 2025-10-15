from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from unittest.mock import MagicMock, patch

from tickets_bah.models import Utilisateur
from tickets_bah.views import mfa_setup, mfa_verify


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class MfaViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.utilisateur = Utilisateur.objects.create_user(
            email="mfa@example.com",
            password="StrongPass123!",
            nom="MFA",
            prenom="User",
            cle_utilisateur="CLE-MFA",
        )

    def _attach_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    @patch("tickets_bah.views.sweetify.error")
    def test_mfa_setup_requires_session_user(self, mock_error):
        request = self._attach_session_and_messages(self.factory.get("/mfa/setup"))

        response = mfa_setup(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()

    @patch("tickets_bah.views.qrcode.make")
    @patch("tickets_bah.views.pyotp.TOTP")
    @patch("tickets_bah.views.pyotp.random_base32", return_value="RANDOMSECRET")
    def test_mfa_setup_generates_secret_and_qr(self, mock_random, mock_totp, mock_qrcode):
        mock_totp_instance = MagicMock()
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp"
        mock_totp.return_value = mock_totp_instance

        request = self._attach_session_and_messages(self.factory.get("/mfa/setup"))
        request.session["mfa_user_id"] = self.utilisateur.id

        response = mfa_setup(request)

        self.assertEqual(response.status_code, 200)
        self.utilisateur.refresh_from_db()
        self.assertEqual(self.utilisateur.totp_secret, "RANDOMSECRET")
        mock_totp.assert_called_once_with("RANDOMSECRET")
        mock_totp_instance.provisioning_uri.assert_called_once_with(
            name=self.utilisateur.email, issuer_name="Jeux Olympiques"
        )

    @patch("tickets_bah.views.login")
    @patch("tickets_bah.views.sweetify.success")
    @patch("tickets_bah.views.qrcode.make")
    @patch("tickets_bah.views.pyotp.TOTP")
    def test_mfa_setup_post_valid_code_enables_totp(self, mock_totp, mock_qrcode, mock_success, mock_login):
        mock_totp_instance = MagicMock()
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp"
        mock_totp_instance.verify.return_value = True
        mock_totp.return_value = mock_totp_instance

        self.utilisateur.totp_secret = "EXISTINGSECRET"
        self.utilisateur.save(update_fields=["totp_secret"])

        request = self._attach_session_and_messages(self.factory.post("/mfa/setup", data={"code": "123456"}))
        request.session["mfa_user_id"] = self.utilisateur.id
        request.session["post_login_redirect"] = "home"

        response = mfa_setup(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.utilisateur.refresh_from_db()
        self.assertTrue(self.utilisateur.is_totp_enabled)
        mock_success.assert_called_once()
        mock_login.assert_called_once_with(request, self.utilisateur)

    @patch("tickets_bah.views.sweetify.error")
    @patch("tickets_bah.views.qrcode.make")
    @patch("tickets_bah.views.pyotp.TOTP")
    def test_mfa_setup_post_invalid_code_shows_error(self, mock_totp, mock_qrcode, mock_error):
        mock_totp_instance = MagicMock()
        mock_totp_instance.provisioning_uri.return_value = "otpauth://totp"
        mock_totp_instance.verify.return_value = False
        mock_totp.return_value = mock_totp_instance

        self.utilisateur.totp_secret = "EXISTINGSECRET"
        self.utilisateur.save(update_fields=["totp_secret"])

        request = self._attach_session_and_messages(self.factory.post("/mfa/setup", data={"code": "000000"}))
        request.session["mfa_user_id"] = self.utilisateur.id

        response = mfa_setup(request)

        self.assertEqual(response.status_code, 200)
        self.utilisateur.refresh_from_db()
        self.assertFalse(self.utilisateur.is_totp_enabled)
        mock_error.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_mfa_verify_requires_session(self, mock_error):
        request = self._attach_session_and_messages(self.factory.get("/mfa/verify"))

        response = mfa_verify(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        mock_error.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_mfa_verify_redirects_if_totp_not_enabled(self, mock_error):
        request = self._attach_session_and_messages(self.factory.get("/mfa/verify"))
        request.session["mfa_user_id"] = self.utilisateur.id

        response = mfa_verify(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("mfa_setup"))
        mock_error.assert_not_called()

    @patch("tickets_bah.views.login")
    @patch("tickets_bah.views.sweetify.success")
    @patch("tickets_bah.views.pyotp.TOTP")
    def test_mfa_verify_accepts_valid_code(self, mock_totp, mock_success, mock_login):
        self.utilisateur.totp_secret = "EXISTINGSECRET"
        self.utilisateur.is_totp_enabled = True
        self.utilisateur.save(update_fields=["totp_secret", "is_totp_enabled"])

        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp.return_value = mock_totp_instance

        request = self._attach_session_and_messages(self.factory.post("/mfa/verify", data={"code": "123456"}))
        request.session["mfa_user_id"] = self.utilisateur.id
        request.session["post_login_redirect"] = "dashboard"

        response = mfa_verify(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))
        mock_success.assert_called_once()
        mock_login.assert_called_once_with(request, self.utilisateur)
        self.assertNotIn("mfa_user_id", request.session)

    @patch("tickets_bah.views.sweetify.error")
    @patch("tickets_bah.views.pyotp.TOTP")
    def test_mfa_verify_rejects_invalid_code(self, mock_totp, mock_error):
        self.utilisateur.totp_secret = "EXISTINGSECRET"
        self.utilisateur.is_totp_enabled = True
        self.utilisateur.save(update_fields=["totp_secret", "is_totp_enabled"])

        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = False
        mock_totp.return_value = mock_totp_instance

        request = self._attach_session_and_messages(self.factory.post("/mfa/verify", data={"code": "000000"}))
        request.session["mfa_user_id"] = self.utilisateur.id

        response = mfa_verify(request)

        self.assertEqual(response.status_code, 200)
        mock_error.assert_called_once()
