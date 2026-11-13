from functools import wraps

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def rol_required(*roles):
    """Restringe una vista a los roles indicados (el superusuario siempre pasa)."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if request.user.rol not in roles and not request.user.is_superuser:
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return login_required(envoltura)
    return decorador


class BootstrapMixin:
    """Agrega clases de Bootstrap a todos los campos del formulario."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, forms.CheckboxInput):
                clase = 'form-check-input'
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                clase = 'form-select'
            else:
                clase = 'form-control'
            w.attrs['class'] = (w.attrs.get('class', '') + ' ' + clase).strip()


def fecha_widget():
    return forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
