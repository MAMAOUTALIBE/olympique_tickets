from django import forms
from tickets_bah.models import Offre, SportEvent


class OffresForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['nom', 'description', 'prix', 'nombre_de_places']


class SportEventForm(forms.ModelForm):
    date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Laissez vide si la date n'est pas encore définie."
    )

    class Meta:
        model = SportEvent
        fields = ["nom", "discipline", "lieu", "date", "description", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_classes = field.widget.attrs.get("class", "")
            extra_class = "form-control"
            if isinstance(field.widget, forms.FileInput):
                extra_class = "form-control"
            field.widget.attrs["class"] = f"{css_classes} {extra_class}".strip()
