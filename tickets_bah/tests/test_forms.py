from django import forms
from django.test import SimpleTestCase, TestCase

from tickets_bah.forms import LoginForm, RegisterForm


class RegisterFormTests(TestCase):
    def test_register_form_valid_data(self):
        form = RegisterForm(
            data={
                "nom": "Jean",
                "prenom": "Dupont",
                "email": "jean.dupont@example.com",
                "password": "motdepasse",
            }
        )

        self.assertTrue(form.is_valid())

    def test_register_form_password_widget(self):
        form = RegisterForm()
        self.assertIsInstance(form.fields["password"].widget, forms.PasswordInput)


class LoginFormTests(SimpleTestCase):
    def test_login_form_requires_fields(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("password", form.errors)

    def test_login_form_password_widget(self):
        form = LoginForm()
        self.assertIsInstance(form.fields["password"].widget, forms.PasswordInput)
