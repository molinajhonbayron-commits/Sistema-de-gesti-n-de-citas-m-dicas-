from django.urls import path

from . import views

app_name = 'pacientes'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.nuevo, name='nuevo'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/estado/', views.cambiar_estado, name='estado'),
    path('mi-perfil/', views.mi_perfil, name='perfil'),
]
