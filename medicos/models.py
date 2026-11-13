from django.conf import settings
from django.db import models


class Especialidad(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name_plural = 'especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Consultorio(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    ubicacion = models.CharField('Ubicación', max_length=100, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medico')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='medicos')
    consultorio = models.ForeignKey(Consultorio, null=True, blank=True, on_delete=models.SET_NULL)
    tarifa = models.DecimalField('Valor de la consulta', max_digits=10, decimal_places=0, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    @property
    def nombre(self):
        return f'Dr(a). {self.user.nombre}'

    def __str__(self):
        return f'{self.nombre} — {self.especialidad}'


class HorarioMedico(models.Model):
    DIAS = [(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')]
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    dia = models.PositiveSmallIntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ['dia', 'hora_inicio']
        verbose_name_plural = 'horarios'

    def __str__(self):
        return f'{self.get_dia_display()} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}'
