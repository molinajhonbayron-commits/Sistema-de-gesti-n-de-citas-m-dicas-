from django.contrib import admin

from .models import Consultorio, Especialidad, HorarioMedico, Medico


class HorarioInline(admin.TabularInline):
    model = HorarioMedico
    extra = 1


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('user', 'especialidad', 'consultorio', 'activo')
    inlines = [HorarioInline]


admin.site.register(Especialidad)
admin.site.register(Consultorio)
