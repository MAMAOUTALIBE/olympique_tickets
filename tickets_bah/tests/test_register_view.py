# Placeholder file for register view tests.
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from unittest.mock import patch

from tickets_bah.models import Utilisateur
from tickets_bah.views import register


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class RegisterViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.existing_user = Utilisateur.objects.create_user(
            email="existing@example.com",
            password="StrongPass123!",
            nom="Existing",
            prenom="User",
            cle_utilisateur="CLE-EXIST",
        )

    def _attach_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

    @patch("tickets_bah.views.sweetify.success")
    def test_register_success_creates_user_and_redirects(self, mock_success):
        request = self.factory.post(
            "/register",
            data={
                "nom": "Nouveau",
                "prenom": "Client",
                "email": "newuser@example.com",
                "password": "SuperSecure123!",
            },
        )
        self._attach_session_and_messages(request)

        response = register(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/")
        self.assertTrue(
            Utilisateur.objects.filter(email="newuser@example.com").exists()
        )
        created_user = Utilisateur.objects.get(email="newuser@example.com")
        self.assertIsNotNone(created_user.cle_utilisateur)
        self.assertGreater(len(created_user.cle_utilisateur), 0)
        mock_success.assert_called_once()

    @patch("tickets_bah.views.sweetify.error")
    def test_register_rejects_weak_password(self, mock_error):
        initial_count = Utilisateur.objects.count()
        request = self.factory.post(
            "/register",
            data={
                "nom": "Nouveau",
                "prenom": "Client",
                "email": "weak@example.com",
                "password": "short",
            },
        )
        self._attach_session_and_messages(request)

        response = register(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Utilisateur.objects.count(), initial_count)
        mock_error.assert_called()

    @patch("tickets_bah.views.sweetify.error")
    def test_register_fails_when_email_already_exists(self, mock_error):
        initial_count = Utilisateur.objects.count()
        request = self.factory.post(
            "/register",
            data={
                "nom": "Existing",
                "prenom": "User",
                "email": self.existing_user.email,
                "password": "AnotherStrong123!",
            },
        )
        self._attach_session_and_messages(request)

        response = register(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Utilisateur.objects.count(), initial_count)
        mock_error.assert_called()

    @patch("tickets_bah.views.sweetify.error")
    def test_register_requires_mandatory_fields(self, mock_error):
        initial_count = Utilisateur.objects.count()
        request = self.factory.post("/register", data={})
        self._attach_session_and_messages(request)

        response = register(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Utilisateur.objects.count(), initial_count)
        mock_error.assert_called()
    
