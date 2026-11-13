from django.urls import path

from . import views

app_name = 'citas'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('mis-citas/', views.mis_citas, name='mis_citas'),
    path('agendar/', views.agendar, name='agendar'),
    path('<int:pk>/reprogramar/', views.reprogramar, name='reprogramar'),
    path('<int:pk>/pago/', views.pago, name='pago'),
    path('<int:pk>/<str:accion>/', views.cambiar_estado, name='estado'),
    path('horas/', views.horas, name='horas'),
    path('agenda/', views.agenda, name='agenda'),
]
