from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),

    # API REST para Flutter
    path('api/', include('accounts.api_urls')),
    path('api/token/', obtain_auth_token, name='api_token'),

    # Aquí permanecen todas las rutas web existentes de GIMM.
]
