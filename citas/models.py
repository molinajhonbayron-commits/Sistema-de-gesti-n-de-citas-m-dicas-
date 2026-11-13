from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

SLOT_MINUTOS = 30


def horas_disponibles(medico, fecha, excluir=None):
    """Horas libres (bloques de 30 min) de un médico en una fecha, según su horario."""
    if not medico or not fecha or fecha < timezone.localdate():
        return []
    ocupadas = Cita.objects.filter(medico=medico, fecha=fecha).exclude(estado=Cita.CANCELADA)
    if excluir is not None and excluir.pk:
        ocupadas = ocupadas.exclude(pk=excluir.pk)
    ocupadas = {h.replace(second=0, microsecond=0) for h in ocupadas.values_list('hora', flat=True)}
    ahora = timezone.localtime().time() if fecha == timezone.localdate() else None
    horas = []
    for h in medico.horarios.filter(dia=fecha.weekday()):
        actual = datetime.combine(fecha, h.hora_inicio)
        fin = datetime.combine(fecha, h.hora_fin)
        while actual + timedelta(minutes=SLOT_MINUTOS) <= fin:
            t = actual.time()
            if t not in ocupadas and (ahora is None or t > ahora):
                horas.append(t)
            actual += timedelta(minutes=SLOT_MINUTOS)
    return sorted(horas)


class Cita(models.Model):
    PENDIENTE, CONFIRMADA, EN_SALA, ATENDIDA, CANCELADA = 'pendiente', 'confirmada', 'en_sala', 'atendida', 'cancelada'
    ESTADOS = [(PENDIENTE, 'Pendiente'), (CONFIRMADA, 'Confirmada'), (EN_SALA, 'Paciente en sala'),
               (ATENDIDA, 'Atendida'), (CANCELADA, 'Cancelada')]
    COLORES = {PENDIENTE: 'warning text-dark', CONFIRMADA: 'primary', EN_SALA: 'info text-dark',
               ATENDIDA: 'success', CANCELADA: 'secondary'}
    METODOS = [('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia')]

    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.PROTECT, related_name='citas')
    medico = models.ForeignKey('medicos.Medico', on_delete=models.PROTECT, related_name='citas', verbose_name='Médico')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)
    valor = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    pagado = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=15, choices=METODOS, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'hora']
        constraints = [models.UniqueConstraint(
            fields=['medico', 'fecha', 'hora'], condition=~models.Q(estado='cancelada'), name='cita_unica_por_medico')]

    @property
    def color(self):
        return self.COLORES.get(self.estado, 'secondary')

    @property
    def activa(self):
        return self.estado in (self.PENDIENTE, self.CONFIRMADA, self.EN_SALA)

    def clean(self):
        if not (self.medico_id and self.fecha and self.hora) or self.estado == self.CANCELADA:
            return
        if not self.medico.activo:
            raise ValidationError('El médico seleccionado no está activo.')
        if self.hora.replace(second=0, microsecond=0) not in horas_disponibles(self.medico, self.fecha, self):
            raise ValidationError('El médico no tiene disponible ese horario. Elija otra fecha u hora.')
        if self.paciente_id and Cita.objects.filter(paciente_id=self.paciente_id, fecha=self.fecha, hora=self.hora) \
                .exclude(estado=self.CANCELADA).exclude(pk=self.pk).exists():
            raise ValidationError('El paciente ya tiene una cita a esa misma fecha y hora.')

    def save(self, *args, **kwargs):
        if self.valor is None and self.medico_id:
            self.valor = self.medico.tarifa
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.fecha} {self.hora:%H:%M} · {self.paciente} · {self.medico}'
