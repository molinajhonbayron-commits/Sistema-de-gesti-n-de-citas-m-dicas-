import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from config.utils import rol_required
from medicos.models import Medico
from pacientes.models import Paciente
from .forms import CitaForm, PagoForm
from .models import Cita, horas_disponibles


def _medicos_json():
    return [{'id': m.pk, 'nombre': m.nombre, 'esp': m.especialidad_id, 'esp_nombre': m.especialidad.nombre}
            for m in Medico.objects.filter(activo=True).select_related('user', 'especialidad')]


def _correo(cita, asunto):
    if cita.paciente.email:
        send_mail(asunto, f'Hola {cita.paciente.nombres},\n\nCita con {cita.medico.nombre} ({cita.medico.especialidad}) '
                          f'el {cita.fecha:%d/%m/%Y} a las {cita.hora:%H:%M}.\n\nClínica', None,
                  [cita.paciente.email], fail_silently=True)


@login_required
def horas(request):
    """Horas disponibles (JSON) para un médico y una fecha."""
    try:
        medico = Medico.objects.get(pk=request.GET.get('medico'))
        fecha = date.fromisoformat(request.GET.get('fecha', ''))
    except (Medico.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'horas': []})
    cita = Cita.objects.filter(pk=request.GET.get('cita') or 0).first()
    return JsonResponse({'horas': [h.strftime('%H:%M') for h in horas_disponibles(medico, fecha, cita)]})


@rol_required('paciente')
def mis_citas(request):
    paciente = Paciente.para_usuario(request.user)
    citas = paciente.citas.select_related('medico__user', 'medico__especialidad').order_by('-fecha', '-hora')
    return render(request, 'citas/mis_citas.html', {'citas': citas})


@rol_required('paciente', 'recepcionista', 'admin')
def agendar(request):
    es_paciente = request.user.rol == 'paciente'
    instancia = Cita(paciente=Paciente.para_usuario(request.user)) if es_paciente else None
    form = CitaForm(request.POST or None, instance=instancia, paciente_fijo=es_paciente)
    if request.method == 'POST' and form.is_valid():
        cita = form.save()
        _correo(cita, 'Cita médica agendada')
        messages.success(request, 'Cita agendada correctamente.')
        return redirect('citas:mis_citas' if es_paciente else 'citas:lista')
    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Solicitar cita' if es_paciente else 'Agendar cita',
                                               'medicos_data': _medicos_json(), 'cita_id': ''})


@rol_required('recepcionista', 'admin')
def reprogramar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if not cita.activa:
        messages.error(request, 'Solo se pueden reprogramar citas activas.')
        return redirect('citas:lista')
    form = CitaForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        cita = form.save()
        _correo(cita, 'Cita médica reprogramada')
        messages.success(request, 'Cita reprogramada.')
        return redirect('citas:lista')
    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Reprogramar cita',
                                               'medicos_data': _medicos_json(), 'cita_id': cita.pk})


@rol_required('recepcionista', 'admin')
def lista(request):
    g = request.GET
    fecha = g.get('fecha', timezone.localdate().isoformat()) if 'fecha' in g or not g else ''
    citas = Cita.objects.select_related('paciente', 'medico__user', 'medico__especialidad')
    try:
        if fecha:
            citas = citas.filter(fecha=date.fromisoformat(fecha))
    except ValueError:
        fecha = ''
    if g.get('estado'):
        citas = citas.filter(estado=g['estado'])
    if g.get('medico'):
        citas = citas.filter(medico_id=g['medico'])
    return render(request, 'citas/lista.html', {
        'citas': citas, 'fecha': fecha, 'estado': g.get('estado', ''), 'medico': g.get('medico', ''),
        'estados': Cita.ESTADOS, 'medicos': Medico.objects.select_related('user')})


ACCIONES = {  # acción: (nuevo estado, roles permitidos, estados de origen)
    'confirmar': (Cita.CONFIRMADA, ('recepcionista', 'admin'), (Cita.PENDIENTE,)),
    'llegada': (Cita.EN_SALA, ('recepcionista', 'admin'), (Cita.PENDIENTE, Cita.CONFIRMADA)),
    'atender': (Cita.ATENDIDA, ('medico', 'admin'), (Cita.PENDIENTE, Cita.CONFIRMADA, Cita.EN_SALA)),
    'cancelar': (Cita.CANCELADA, ('paciente', 'recepcionista', 'admin'), (Cita.PENDIENTE, Cita.CONFIRMADA, Cita.EN_SALA)),
}


@login_required
@require_POST
def cambiar_estado(request, pk, accion):
    cita = get_object_or_404(Cita, pk=pk)
    u = request.user
    if accion not in ACCIONES:
        raise PermissionDenied
    nuevo, roles, origen = ACCIONES[accion]
    if u.rol not in roles or (u.rol == 'paciente' and cita.paciente.user_id != u.pk) \
            or (u.rol == 'medico' and cita.medico.user_id != u.pk):
        raise PermissionDenied
    if cita.estado not in origen or (u.rol == 'paciente' and cita.estado == Cita.EN_SALA):
        messages.error(request, 'Esa acción no es posible con el estado actual de la cita.')
    else:
        cita.estado = nuevo
        cita.save(update_fields=['estado'])
        if accion == 'cancelar':
            _correo(cita, 'Cita médica cancelada')
        messages.success(request, f'Cita {cita.get_estado_display().lower()}.')
    destino = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect('inicio')


@rol_required('recepcionista', 'admin')
def pago(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    form = PagoForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        c = form.save(commit=False)
        c.fecha_pago = timezone.now() if c.pagado else None
        c.save()
        messages.success(request, 'Pago registrado.')
        return redirect('citas:lista')
    return render(request, 'form.html', {'form': form, 'titulo': f'Pago de la cita: {cita.paciente.nombre_completo}', 'volver': 'citas:lista'})


@rol_required('medico')
def agenda(request):
    medico = get_object_or_404(Medico, user=request.user)
    try:
        fecha = date.fromisoformat(request.GET.get('fecha', ''))
    except ValueError:
        fecha = timezone.localdate()
    vista = request.GET.get('vista', 'dia')
    if vista == 'semana':
        inicio = fecha - timedelta(days=fecha.weekday())
        fin, paso = inicio + timedelta(days=6), 7
    else:
        inicio = fin = fecha
        paso = 1
    citas = medico.citas.filter(fecha__range=(inicio, fin)).exclude(estado=Cita.CANCELADA) \
        .select_related('paciente').order_by('fecha', 'hora')
    return render(request, 'citas/agenda.html', {
        'citas': citas, 'fecha': fecha, 'vista': vista, 'inicio': inicio, 'fin': fin,
        'anterior': fecha - timedelta(days=paso), 'siguiente': fecha + timedelta(days=paso)})
