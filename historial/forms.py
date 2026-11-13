from django import forms
from django.forms import inlineformset_factory

from config.utils import BootstrapMixin
from .models import Consulta, OrdenExamen, Receta


class ConsultaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['diagnostico', 'tratamiento', 'observaciones']
        widgets = {c: forms.Textarea(attrs={'rows': 3}) for c in fields}


class RecetaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['medicamento', 'dosis', 'indicaciones']


class OrdenForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = OrdenExamen
        fields = ['examen', 'indicaciones', 'resultado']
        widgets = {'resultado': forms.Textarea(attrs={'rows': 1})}


RecetaFormSet = inlineformset_factory(Consulta, Receta, form=RecetaForm, extra=1, can_delete=True)
OrdenFormSet = inlineformset_factory(Consulta, OrdenExamen, form=OrdenForm, extra=1, can_delete=True)
