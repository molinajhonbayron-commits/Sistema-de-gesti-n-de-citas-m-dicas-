from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('usuarios/', include('usuarios.urls_admin')),
    path('pacientes/', include('pacientes.urls')),
    path('medicos/', include('medicos.urls')),
    path('citas/', include('citas.urls')),
    path('historial/', include('historial.urls')),
    path('reportes/', include('reportes.urls')),
]
