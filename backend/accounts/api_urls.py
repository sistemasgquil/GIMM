from django.urls import path

from .api_views import (
    SocioListCreateAPIView,
    SocioDetailAPIView,
    CobroListCreateAPIView,
    ReporteUsuariosAPIView,
)


urlpatterns = [

    # ==========================================
    # API DE SOCIOS
    # ==========================================

    path(
        'socios/',
        SocioListCreateAPIView.as_view(),
        name='api_lista_socios'
    ),

    path(
        'socios/<int:pk>/',
        SocioDetailAPIView.as_view(),
        name='api_detalle_socio'
    ),

    # ==========================================
    # API DE COBROS
    # ==========================================

    path(
        'cobros/',
        CobroListCreateAPIView.as_view(),
        name='api_lista_cobros'
    ),

    # ==========================================
    # REPORTE DE USUARIOS
    # ==========================================

    path(
        'reportes/usuarios/',
        ReporteUsuariosAPIView.as_view(),
        name='api_reporte_usuarios'
    ),

]