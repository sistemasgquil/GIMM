from rest_framework import serializers
from .models import Socio, Cobro
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission

# ==================================================
# SERIALIZADOR DE SOCIOS
# ==================================================

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


# ==================================================
# SERIALIZADOR DE COBROS
# ==================================================

class CobroSerializer(serializers.ModelSerializer):

    socio_nombre = serializers.SerializerMethodField()

    socio_cedula = serializers.CharField(
        source='socio.cedula',
        read_only=True
    )

    class Meta:
        model = Cobro

        fields = [
            'id',
            'socio',
            'socio_nombre',
            'socio_cedula',
            'concepto',
            'fecha_cobro',
            'fecha_vencimiento',
            'valor',
            'metodo_pago',
            'estado',
            'observacion',
        ]

        read_only_fields = [
            'id',
            'fecha_cobro',
            'socio_nombre',
            'socio_cedula',
        ]

    def get_socio_nombre(self, obj):
        return f'{obj.socio.nombres} {obj.socio.apellidos}'.strip()

    def validate_valor(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                'El valor debe ser mayor que cero.'
            )

        return value

    def validate_socio(self, value):

        if not value.activo:
            raise serializers.ValidationError(
                'No se pueden registrar cobros a socios inactivos.'
            )

        return value

class UsuarioReporteSerializer(serializers.ModelSerializer):

    nombres = serializers.SerializerMethodField()
    apellidos = serializers.CharField(source='last_name')
    telefono = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'nombres',
            'apellidos',
            'email',
            'telefono',
            'rol',
            'estado',
            'date_joined',
            'last_login',
        ]

    def get_nombres(self, obj):
        return obj.first_name

    def get_telefono(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.phone or ''

        return ''

    def get_rol(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role

        return 'SIN PERFIL'

    def get_estado(self, obj):

        if not obj.is_active:
            return 'INACTIVO'

        if hasattr(obj, 'profile') and not obj.profile.active:
            return 'INACTIVO'

        return 'ACTIVO'


class EsAdministradorGIMM(BasePermission):

    message = 'No tienes permisos para consultar este reporte.'

    def has_permission(self, request, view):

        usuario = request.user

        if not usuario or not usuario.is_authenticated:
            return False

        if not usuario.is_active:
            return False

        if not hasattr(usuario, 'profile'):
            return False

        perfil = usuario.profile

        return (
            perfil.active
            and perfil.role == 'ADMIN'
        )