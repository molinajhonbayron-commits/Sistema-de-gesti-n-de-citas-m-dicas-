from django.db import models


class Consulta(models.Model):
    cita = models.OneToOneField('citas.Cita', on_delete=models.CASCADE, related_name='consulta')
    diagnostico = models.TextField('Diagnóstico')
    tratamiento = models.TextField('Tratamiento', blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cita__fecha', '-cita__hora']

    def __str__(self):
        return f'Consulta {self.cita}'


class Receta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='recetas')
    medicamento = models.CharField(max_length=120)
    dosis = models.CharField(max_length=120, blank=True)
    indicaciones = models.CharField(max_length=200, blank=True)


class OrdenExamen(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='ordenes')
    examen = models.CharField(max_length=120)
    indicaciones = models.CharField(max_length=200, blank=True)
    resultado = models.TextField('Resultado', blank=True)
