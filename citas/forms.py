from django import forms

from config.utils import BootstrapMixin, fecha_widget
from medicos.models import Especialidad, Medico
from pacientes.models import Paciente
from .models import Cita


class CitaForm(BootstrapMixin, forms.ModelForm):
    especialidad = forms.ModelChoiceField(Especialidad.objects.all(), required=False)

    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'hora', 'motivo']
        widgets = {'fecha': fecha_widget(), 'hora': forms.Select(choices=[])}

    def __init__(self, *args, paciente_fijo=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['paciente', 'especialidad', 'medico', 'fecha', 'hora', 'motivo'])
        self.fields['medico'].queryset = Medico.objects.filter(activo=True).select_related('user', 'especialidad')
        self.fields['medico'].label_from_instance = lambda m: f'{m.nombre} — {m.especialidad}'
        if paciente_fijo:
            del self.fields['paciente']
        else:
            self.fields['paciente'].queryset = Paciente.objects.filter(activo=True)
        if self.instance.pk:
            self.fields['especialidad'].initial = self.instance.medico.especialidad_id


class PagoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['valor', 'metodo_pago', 'pagado']
        labels = {'pagado': 'Pago recibido'}
