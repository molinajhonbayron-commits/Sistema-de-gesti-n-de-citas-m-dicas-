from django.urls import path

from . import views

app_name = 'historial'
urlpatterns = [
    path('cita/<int:cita_id>/registrar/', views.registrar, name='registrar'),
    path('paciente/<int:pk>/', views.paciente, name='paciente'),
    path('mi-historial/', views.mi_historial, name='mio'),
    path('consulta/<int:pk>/', views.detalle, name='detalle'),
]
