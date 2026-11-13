from datetime import date

from django.conf import settings
from django.db import models


class Paciente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='paciente')
    documento = models.CharField('Documento', max_length=20, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Correo', blank=True)
    direccion = models.CharField('Dirección', max_length=150, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['apellidos', 'nombres']

    @classmethod
    def para_usuario(cls, user):
        """Devuelve (o crea) la ficha de paciente del usuario."""
        try:
            return user.paciente
        except cls.DoesNotExist:
            return cls.objects.create(user=user, documento=f'SIN-{user.pk}', nombres=user.first_name or user.username,
                                      apellidos=user.last_name, email=user.email)

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        h = date.today()
        n = self.fecha_nacimiento
        return h.year - n.year - ((h.month, h.day) < (n.month, n.day))

    def __str__(self):
        return f'{self.nombre_completo} ({self.documento})'
