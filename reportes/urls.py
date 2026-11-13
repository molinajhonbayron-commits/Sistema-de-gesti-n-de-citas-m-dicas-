from django.urls import path

from . import views

app_name = 'reportes'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('citas/', views.citas, name='citas'),
    path('ingresos/', views.ingresos, name='ingresos'),
]
