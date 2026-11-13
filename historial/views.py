from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from citas.models import Cita
from config.utils import rol_required
from pacientes.models import Paciente
from .forms import ConsultaForm, OrdenFormSet, RecetaFormSet
from .models import Consulta


@rol_required('medico')
def registrar(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('paciente', 'medico__user'), pk=cita_id)
    if cita.medico.user_id != request.user.pk:
        raise PermissionDenied
    if cita.estado == Cita.CANCELADA:
        messages.error(request, 'No se puede registrar una consulta de una cita cancelada.')
        return redirect('citas:agenda')
    consulta = getattr(cita, 'consulta', None) or Consulta(cita=cita)
    form = ConsultaForm(request.POST or None, instance=consulta)
    recetas = RecetaFormSet(request.POST or None, instance=consulta, prefix='rec')
    ordenes = OrdenFormSet(request.POST or None, instance=consulta, prefix='ord')
    if request.method == 'POST' and all([form.is_valid(), recetas.is_valid(), ordenes.is_valid()]):
        consulta = form.save()
        recetas.instance = ordenes.instance = consulta
        recetas.save()
        ordenes.save()
        if cita.estado != Cita.ATENDIDA:
            cita.estado = Cita.ATENDIDA
            cita.save(update_fields=['estado'])
        messages.success(request, 'Consulta registrada y cita marcada como atendida.')
        return redirect('historial:detalle', pk=consulta.pk)
    previo = Consulta.objects.filter(cita__paciente=cita.paciente).exclude(pk=consulta.pk or 0)[:5]
    return render(request, 'historial/registrar.html', {'cita': cita, 'form': form, 'recetas': recetas,
                                                        'ordenes': ordenes, 'previo': previo})


def _consultas(paciente):
    return Consulta.objects.filter(cita__paciente=paciente).select_related('cita__medico__user', 'cita__medico__especialidad') \
        .prefetch_related('recetas', 'ordenes')


@rol_required('medico', 'admin')
def paciente(request, pk):
    p = get_object_or_404(Paciente, pk=pk)
    return render(request, 'historial/paciente.html', {'paciente': p, 'consultas': _consultas(p)})


@rol_required('paciente')
def mi_historial(request):
    p = Paciente.para_usuario(request.user)
    return render(request, 'historial/paciente.html', {'paciente': p, 'consultas': _consultas(p), 'propio': True})


@login_required
def detalle(request, pk):
    consulta = get_object_or_404(Consulta.objects.select_related('cita__paciente', 'cita__medico__user', 'cita__medico__especialidad'), pk=pk)
    u = request.user
    if u.rol == 'paciente' and consulta.cita.paciente.user_id != u.pk:
        raise PermissionDenied
    if u.rol == 'recepcionista':
        raise PermissionDenied
    return render(request, 'historial/detalle.html', {'c': consulta})
