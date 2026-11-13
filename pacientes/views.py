from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from config.utils import rol_required
from .forms import PacienteForm, PerfilPacienteForm
from .models import Paciente


@rol_required('recepcionista', 'admin', 'medico')
def lista(request):
    q = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.all()
    if q:
        pacientes = pacientes.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(documento__icontains=q))
    return render(request, 'pacientes/lista.html', {'pacientes': pacientes, 'q': q})


@rol_required('recepcionista', 'admin')
def nuevo(request):
    form = PacienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Paciente registrado.')
        return redirect('pacientes:lista')
    return render(request, 'form.html', {'form': form, 'titulo': 'Nuevo paciente', 'volver': 'pacientes:lista'})


@rol_required('recepcionista', 'admin')
def editar(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Paciente actualizado.')
        return redirect('pacientes:lista')
    return render(request, 'form.html', {'form': form, 'titulo': f'Editar a {paciente.nombre_completo}', 'volver': 'pacientes:lista'})


@rol_required('recepcionista', 'admin')
@require_POST
def cambiar_estado(request, pk):
    p = get_object_or_404(Paciente, pk=pk)
    p.activo = not p.activo
    p.save(update_fields=['activo'])
    messages.success(request, f'Paciente {"activado" if p.activo else "desactivado"}.')
    return redirect('pacientes:lista')


@rol_required('paciente')
def mi_perfil(request):
    paciente = Paciente.para_usuario(request.user)
    form = PerfilPacienteForm(request.POST or None, instance=paciente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Datos actualizados.')
        return redirect('pacientes:perfil')
    return render(request, 'form.html', {'form': form, 'titulo': 'Mis datos personales', 'volver': 'inicio'})
