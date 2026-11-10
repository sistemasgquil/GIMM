from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Socio, Cobro
from .serializers import SocioSerializer, CobroSerializer


User = get_user_model()


# ==================================================
# PERMISO: ADMINISTRADOR GIMM
# ==================================================

class EsAdministradorGIMM(BasePermission):

    message = "No tienes permisos para consultar este reporte."

    def has_permission(self, request, view):

        usuario = request.user

        if not usuario or not usuario.is_authenticated:
            return False

        if not usuario.is_active:
            return False

        perfil = getattr(usuario, 'profile', None)

        if perfil is None:
            return False

        if not perfil.active:
            return False

        return perfil.role == 'ADMIN'


# ==================================================
# API DE SOCIOS
# ==================================================

class SocioListCreateAPIView(generics.ListCreateAPIView):

    queryset = Socio.objects.all().order_by('-id')

    serializer_class = SocioSerializer

    permission_classes = [IsAuthenticated]


class SocioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Socio.objects.all()

    serializer_class = SocioSerializer

    permission_classes = [IsAuthenticated]


# ==================================================
# API DE COBROS
# ==================================================

class CobroListCreateAPIView(generics.ListCreateAPIView):

    queryset = Cobro.objects.select_related(
        'socio'
    ).all().order_by('-id')

    serializer_class = CobroSerializer

    permission_classes = [IsAuthenticated]


# ==================================================
# REPORTE DE USUARIOS - API MOVIL
# ==================================================

class ReporteUsuariosAPIView(APIView):

    authentication_classes = [TokenAuthentication]

    permission_classes = [
        IsAuthenticated,
        EsAdministradorGIMM
    ]

    def get(self, request):

        try:

            # CONSULTAR USUARIOS

            usuarios = User.objects.select_related(
                'profile'
            ).all().order_by('username')

            # FILTRO DE BUSQUEDA

            buscar = request.query_params.get(
                'buscar', ''
            ).strip()

            if buscar:

                usuarios = usuarios.filter(
                    username__icontains=buscar
                ) | usuarios.filter(
                    first_name__icontains=buscar
                ) | usuarios.filter(
                    last_name__icontains=buscar
                ) | usuarios.filter(
                    email__icontains=buscar
                )

                usuarios = usuarios.distinct()

            # CONSTRUIR LISTA DE USUARIOS

            lista_usuarios = []

            for usuario in usuarios:

                perfil = getattr(usuario, 'profile', None)

                telefono = perfil.phone if perfil else ''

                rol = perfil.role if perfil else 'SIN PERFIL'

                perfil_activo = perfil.active if perfil else False

                activo = usuario.is_active and perfil_activo

                lista_usuarios.append({

                    'id': usuario.id,

                    'username': usuario.username,

                    'nombres': usuario.first_name,

                    'apellidos': usuario.last_name,

                    'email': usuario.email,

                    'telefono': telefono,

                    'rol': rol,

                    'estado': (
                        'ACTIVO' if activo else 'INACTIVO'
                    ),

                    'fecha_registro': (
                        usuario.date_joined.isoformat()
                        if usuario.date_joined else None
                    ),

                    'ultimo_acceso': (
                        usuario.last_login.isoformat()
                        if usuario.last_login else None
                    )

                })

            # ESTADISTICAS

            total_usuarios = len(lista_usuarios)

            usuarios_activos = sum(
                1 for usuario in lista_usuarios
                if usuario['estado'] == 'ACTIVO'
            )

            usuarios_inactivos = (
                total_usuarios - usuarios_activos
            )

            # RESPUESTA JSON

            return Response({

                'success': True,

                'mensaje': 'Reporte de usuarios obtenido correctamente.',

                'total_usuarios': total_usuarios,

                'usuarios_activos': usuarios_activos,

                'usuarios_inactivos': usuarios_inactivos,

                'usuarios': lista_usuarios

            }, status=status.HTTP_200_OK)

        except Exception:

            return Response({

                'success': False,

                'mensaje': 'Error al generar el reporte de usuarios.'

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)