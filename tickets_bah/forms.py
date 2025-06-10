from symtable import Class

from django import forms
from .models import Utilisateur


class RegisterForm(forms.ModelForm): # enregistrement de formulaire
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'password']

class LoginForm(forms.Form): #enregistrer le login
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
