from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from config.utils import rol_required
from .forms import HorarioFormSet, MedicoForm
from .models import Especialidad, Medico


@login_required
def lista(request):
    medicos = Medico.objects.select_related('user', 'especialidad', 'consultorio').prefetch_related('horarios')
    esp = request.GET.get('especialidad', '')
    if esp:
        medicos = medicos.filter(especialidad_id=esp)
    if request.user.rol == 'paciente':
        medicos = medicos.filter(activo=True)
    return render(request, 'medicos/lista.html', {'medicos': medicos, 'especialidades': Especialidad.objects.all(), 'esp': esp})


@rol_required('admin')
def guardar(request, pk=None):
    medico = get_object_or_404(Medico, pk=pk) if pk else None
    form = MedicoForm(request.POST or None, instance=medico)
    formset = HorarioFormSet(request.POST or None, instance=medico or Medico())
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        medico = form.save()
        formset.instance = medico
        formset.save()
        messages.success(request, 'Médico guardado.')
        return redirect('medicos:lista')
    return render(request, 'medicos/form.html', {'form': form, 'formset': formset, 'medico': medico})


@rol_required('admin')
@require_POST
def cambiar_estado(request, pk):
    m = get_object_or_404(Medico, pk=pk)
    m.activo = not m.activo
    m.save(update_fields=['activo'])
    messages.success(request, f'Médico {"activado" if m.activo else "desactivado"}.')
    return redirect('medicos:lista')
