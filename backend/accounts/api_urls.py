from django.urls import path

from accounts.api_views import (
    SocioListCreateAPIView,
    SocioDetailAPIView,
)

urlpatterns = [
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
]