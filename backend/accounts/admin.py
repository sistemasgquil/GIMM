from django.contrib import admin
# Register your models here.
from .models import Socio


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombres',
        'apellidos',
        'cedula',
        'telefono',
        'email',
        'activo',
    )

    search_fields = (
        'nombres',
        'apellidos',
        'cedula',
    )

    list_filter = (
        'activo',
    )
