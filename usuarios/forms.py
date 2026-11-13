from django import forms
from django.contrib.auth.forms import UserCreationForm

from config.utils import BootstrapMixin, fecha_widget
from pacientes.models import Paciente
from .models import Usuario


class RegistroPacienteForm(BootstrapMixin, UserCreationForm):
    documento = forms.CharField(max_length=20, label='Documento de identidad')
    telefono = forms.CharField(max_length=20, label='Teléfono')
    fecha_nacimiento = forms.DateField(widget=fecha_widget(), label='Fecha de nacimiento')

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for c in ('first_name', 'last_name', 'email'):
            self.fields[c].required = True

    def clean_documento(self):
        doc = self.cleaned_data['documento'].strip()
        if Paciente.objects.filter(documento=doc).exists():
            raise forms.ValidationError('Ya existe un paciente con ese documento.')
        return doc

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = Usuario.Rol.PACIENTE
        user.save()
        d = self.cleaned_data
        Paciente.objects.create(
            user=user, documento=d['documento'], nombres=user.first_name, apellidos=user.last_name,
            email=user.email, telefono=d['telefono'], fecha_nacimiento=d['fecha_nacimiento'])
        return user


class UsuarioCrearForm(BootstrapMixin, UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'rol', 'is_active')


class UsuarioEditarForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'rol', 'is_active')
