from django import forms
from tickets_bah.models import Offre


class OffresForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['nom', 'description', 'prix', 'nombre_de_places']