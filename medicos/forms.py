from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory

from config.utils import BootstrapMixin
from usuarios.models import Usuario
from .models import HorarioMedico, Medico


class MedicoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['user', 'especialidad', 'consultorio', 'tarifa', 'activo']
        labels = {'user': 'Usuario (rol médico)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = Usuario.objects.filter(rol='medico').filter(
            Q(medico__isnull=True) | Q(pk=self.instance.user_id))
        self.fields['user'].label_from_instance = lambda u: u.nombre


class HorarioForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = HorarioMedico
        fields = ['dia', 'hora_inicio', 'hora_fin']
        widgets = {'hora_inicio': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
                   'hora_fin': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')}

    def clean(self):
        d = super().clean()
        if d.get('hora_inicio') and d.get('hora_fin') and d['hora_inicio'] >= d['hora_fin']:
            raise forms.ValidationError('La hora de inicio debe ser menor que la hora de fin.')
        return d


HorarioFormSet = inlineformset_factory(Medico, HorarioMedico, form=HorarioForm, extra=2, can_delete=True)
