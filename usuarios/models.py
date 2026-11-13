from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        PACIENTE = 'paciente', 'Paciente'
        MEDICO = 'medico', 'Médico'
        RECEPCIONISTA = 'recepcionista', 'Recepcionista'
        ADMIN = 'admin', 'Administrador'

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PACIENTE)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.Rol.ADMIN
        self.is_staff = self.rol == self.Rol.ADMIN
        super().save(*args, **kwargs)

    @property
    def nombre(self):
        return self.get_full_name() or self.username

    def __str__(self):
        return f'{self.nombre} ({self.get_rol_display()})'
