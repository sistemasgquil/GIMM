from rest_framework import serializers
from .models import Socio


class SocioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Socio

        fields = [
            'id',
            'nombres',
            'apellidos',
            'cedula',
            'telefono',
            'email',
            'fecha_nacimiento',
            'fecha_registro',
            'activo',
        ]

        read_only_fields = [
            'id',
            'fecha_registro',
        ]
