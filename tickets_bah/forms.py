from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import Utilisateur


class RegisterForm(forms.ModelForm): # enregistrement de formulaire
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'password']

class LoginForm(forms.Form): #enregistrer le login
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class StyledPasswordResetForm(PasswordResetForm):
    """Ajoute les classes CSS attendues sur le formulaire de réinitialisation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "votre@email.com",
                "autocomplete": "email",
            }
        )


class StyledSetPasswordForm(SetPasswordForm):
    """Formulaire pour définir un nouveau mot de passe avec styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Nouveau mot de passe",
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Confirmez le mot de passe",
            }
        )
