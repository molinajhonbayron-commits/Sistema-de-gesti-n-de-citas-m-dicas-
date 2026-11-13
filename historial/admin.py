from django.contrib import admin

from .models import Consulta, OrdenExamen, Receta

admin.site.register(Consulta)
admin.site.register(Receta)
admin.site.register(OrdenExamen)
