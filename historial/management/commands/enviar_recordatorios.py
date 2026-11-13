from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from citas.models import Cita


class Command(BaseCommand):
    help = 'Envía por correo un recordatorio de las citas de mañana (programar con cron/Tareas de Windows).'

    def handle(self, *args, **opts):
        manana = timezone.localdate() + timedelta(days=1)
        citas = Cita.objects.filter(fecha=manana, estado__in=['pendiente', 'confirmada']).select_related('paciente', 'medico__user')
        n = 0
        for c in citas:
            if c.paciente.email:
                send_mail('Recordatorio de cita médica',
                          f'Hola {c.paciente.nombres}, le recordamos su cita mañana {c.fecha:%d/%m/%Y} a las {c.hora:%H:%M} '
                          f'con {c.medico.nombre}. Si no puede asistir, cancele o reprograme a tiempo.', None, [c.paciente.email])
                n += 1
        self.stdout.write(self.style.SUCCESS(f'{n} recordatorio(s) enviado(s).'))
