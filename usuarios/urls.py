from django.contrib.auth import views as auth
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', auth.LoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('password/', auth.PasswordChangeView.as_view(
        template_name='form.html', success_url=reverse_lazy('inicio'),
        extra_context={'titulo': 'Cambiar contraseña', 'volver': 'inicio'}), name='password_change'),
]
