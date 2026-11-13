from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from config.utils import rol_required
from .forms import RegistroPacienteForm, UsuarioCrearForm, UsuarioEditarForm
from .models import Usuario

DESTINOS = {
    'paciente': 'citas:mis_citas',
    'medico': 'citas:agenda',
    'recepcionista': 'reportes:dashboard',
    'admin': 'reportes:dashboard',
}


@login_required
def inicio(request):
    """Redirige a cada usuario a su panel según su rol."""
    return redirect(DESTINOS.get(request.user.rol, 'reportes:dashboard'))


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = RegistroPacienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registro exitoso. ¡Bienvenido!')
        return redirect('inicio')
    return render(request, 'usuarios/registro.html', {'form': form})


@rol_required('admin')
def lista(request):
    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '')
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    if q:
        usuarios = usuarios.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
    if rol:
        usuarios = usuarios.filter(rol=rol)
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios, 'q': q, 'rol': rol, 'roles': Usuario.Rol.choices})


@rol_required('admin')
def nuevo(request):
    form = UsuarioCrearForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save()
        msg = f'Usuario {u.username} creado.'
        if u.rol == 'medico':
            msg += ' Ahora complete su perfil en el módulo Médicos.'
        messages.success(request, msg)
        return redirect('usuarios:lista')
    return render(request, 'form.html', {'form': form, 'titulo': 'Nuevo usuario', 'volver': 'usuarios:lista'})


@rol_required('admin')
def editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioEditarForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        if usuario == request.user and not form.cleaned_data['is_active']:
            messages.error(request, 'No puede desactivar su propio usuario.')
        else:
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('usuarios:lista')
    return render(request, 'form.html', {'form': form, 'titulo': f'Editar {usuario.username}', 'volver': 'usuarios:lista'})
