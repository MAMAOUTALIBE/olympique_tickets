# Placeholder for custom login view tests.
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from tickets_bah.models import Utilisateur
from tickets_bah.views import customLogin

#classe du setUP pour effectuer les test 
@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class CustomLoginViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Utilisateur.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            nom="Test",
            prenom="User",
            cle_utilisateur="CLE-TESTUSER",
        )

    def _attach_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

    @patch("tickets_bah.views._send_login_verification_email")
    @patch("tickets_bah.views.sweetify.info")
    def test_login_success_redirects_and_sets_session(self, mock_info, mock_send_mail):
        request = self.factory.post(
            "/login",
            data={
                "email": "user@example.com",
                "password": "StrongPass123!",
            },
        )
        self._attach_session_and_messages(request)

        response = customLogin(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login_email_sent"))
        self.assertEqual(request.session["pending_email_user_id"], self.user.id)
        self.assertEqual(request.session["post_login_redirect"], "home")
        mock_send_mail.assert_called_once_with(request, self.user)
        mock_info.assert_called_once()
        
    @patch("tickets_bah.views.sweetify.error")
    def test_login_invalid_credentials_shows_error(self, mock_error):
        request = self.factory.post(
            "/login",
            data={
                "email": "user@example.com",
                "password": "WrongPassword!",
            },
        )
        self._attach_session_and_messages(request)

        response = customLogin(request)

        self.assertEqual(response.status_code, 200)
        mock_error.assert_called_once()
        self.assertNotIn("pending_email_user_id", request.session)
        self.assertNotIn("post_login_redirect", request.session)
        
    @patch("tickets_bah.views._send_login_verification_email")
    @patch("tickets_bah.views.sweetify.info")
    def test_login_super_admin_redirects_to_dashboard(self, mock_info, mock_send_mail):
        self.user.default_role = "super-admin"
        self.user.save(update_fields=["default_role"])

        request = self.factory.post(
            "/login",
            data={
                "email": "user@example.com",
                "password": "StrongPass123!",
            },
        )
        self._attach_session_and_messages(request)

        response = customLogin(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login_email_sent"))
        self.assertEqual(request.session["post_login_redirect"], "dashboard")
        mock_send_mail.assert_called_once_with(request, self.user)
        mock_info.assert_called_once()


    
