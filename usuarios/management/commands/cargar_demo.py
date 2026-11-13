from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from citas.models import Cita
from medicos.models import Consultorio, Especialidad, HorarioMedico, Medico
from pacientes.models import Paciente
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Carga datos de demostración (usuarios, médicos, horarios y citas).'

    def handle(self, *args, **opts):
        def usuario(username, nombre, apellido, rol, clave):
            u, creado = Usuario.objects.get_or_create(
                username=username, defaults=dict(first_name=nombre, last_name=apellido, rol=rol,
                                                 email=f'{username}@clinica.local'))
            if creado:
                u.set_password(clave)
                u.save()
            return u

        usuario('admin', 'Administrador', 'General', 'admin', 'admin12345')
        usuario('recepcion', 'Rosa', 'Mendoza', 'recepcionista', 'recep12345')
        cons = [Consultorio.objects.get_or_create(nombre=f'Consultorio {i}', defaults={'ubicacion': f'Piso {i}'})[0] for i in (1, 2, 3)]
        esp = [Especialidad.objects.get_or_create(nombre=n)[0] for n in ('Medicina General', 'Pediatría', 'Cardiología')]
        datos = [('medico1', 'Carlos', 'Ramírez', esp[0], cons[0], 60000), ('medico2', 'Laura', 'Gómez', esp[1], cons[1], 80000),
                 ('medico3', 'Andrés', 'Pérez', esp[2], cons[2], 120000)]
        medicos = []
        for un, n, a, e, c, t in datos:
            u = usuario(un, n, a, 'medico', 'medico12345')
            m, creado = Medico.objects.get_or_create(user=u, defaults=dict(especialidad=e, consultorio=c, tarifa=t))
            if creado:
                for dia in range(5):
                    HorarioMedico.objects.create(medico=m, dia=dia, hora_inicio=time(8), hora_fin=time(12))
                    HorarioMedico.objects.create(medico=m, dia=dia, hora_inicio=time(14), hora_fin=time(17))
            medicos.append(m)
        u = usuario('paciente1', 'Juan', 'Torres', 'paciente', 'paciente12345')
        p = Paciente.para_usuario(u)
        if p.documento.startswith('SIN-'):
            p.documento, p.telefono, p.fecha_nacimiento = '1000000001', '3001234567', date(1995, 5, 20)
            p.save()
        if not Cita.objects.exists():
            manana = timezone.localdate() + timedelta(days=1)
            while manana.weekday() > 4:
                manana += timedelta(days=1)
            Cita.objects.create(paciente=p, medico=medicos[0], fecha=manana, hora=time(9), motivo='Control general')
            Cita.objects.create(paciente=p, medico=medicos[2], fecha=manana, hora=time(14, 30), motivo='Dolor de pecho', estado='confirmada')
        self.stdout.write(self.style.SUCCESS(
            'Demo lista. Usuarios: admin/admin12345, recepcion/recep12345, medico1/medico12345, paciente1/paciente12345'))
