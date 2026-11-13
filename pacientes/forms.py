from django import forms

from config.utils import BootstrapMixin, fecha_widget
from .models import Paciente


class PacienteForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['documento', 'nombres', 'apellidos', 'fecha_nacimiento', 'telefono', 'email', 'direccion']
        widgets = {'fecha_nacimiento': fecha_widget()}


class PerfilPacienteForm(PacienteForm):
    class Meta(PacienteForm.Meta):
        fields = ['nombres', 'apellidos', 'fecha_nacimiento', 'telefono', 'email', 'direccion']
