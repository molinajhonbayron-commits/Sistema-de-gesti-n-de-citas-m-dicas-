from django.urls import path

from . import views

app_name = 'medicos'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.guardar, name='nuevo'),
    path('<int:pk>/editar/', views.guardar, name='editar'),
    path('<int:pk>/estado/', views.cambiar_estado, name='estado'),
]
