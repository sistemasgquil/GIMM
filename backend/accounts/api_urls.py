from django.urls import path
from .api_views import (
    SocioListCreateAPIView,
    SocioDetailAPIView,
)

urlpatterns = [

    # Listar y registrar socios
    path(
        'socios/',
        SocioListCreateAPIView.as_view(),
        name='api_lista_socios'
    ),

    # Consultar, editar y eliminar un socio
    path(
        'socios/<int:pk>/',
        SocioDetailAPIView.as_view(),
        name='api_detalle_socio'
    ),

]