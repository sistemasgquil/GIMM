"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

#Lista_cobros,
from accounts.views import (
    login_view,
    logout_view,
    lista_socios,
    nuevo_socio,
    editar_socio,
    cambiar_estado_socio,
    lista_cobros,
    nuevo_cobro,
    comprobante_cobro,
    pdf_cobro,
    enviar_email_cobro,
    lista_tipos_articulo,
    nuevo_tipo_articulo,
    editar_tipo_articulo,
    cambiar_estado_tipo_articulo,
    lista_categorias_articulo,
    nuevo_categoria_articulo,
    editar_categoria_articulo,
    cambiar_estado_categoria_articulo,
    lista_productos,
    nuevo_producto,
    editar_producto,
    cambiar_estado_producto,
    reporte_usuarios,
)
from accounts.views import lista_movimientos




urlpatterns = [

    # Administración de Django
    path(
        'admin/',
        admin.site.urls
    ),

    # Login   http://127.0.0.1:8000/login/
    #  path(
     #    'login/',
     #     login_view,
     #    name='login'
    # ),

        # Página principal: redirige al login


        # Login
        path(
            'login/',
            login_view,
            name='login'
        ),


    # Socios
    # Socios
path(
    'socios/',
    lista_socios,
    name='lista_socios'
),

# Nuevo socio
path(
    'socios/nuevo/',
    nuevo_socio,
    name='nuevo_socio'
),

# Editar socio
path(
    'socios/editar/<int:id>/',
    editar_socio,
    name='editar_socio'
),

    # Cerrar sesión
    path(
        'logout/',
        logout_view,
        name='logout'
    ),

# Cambiar estado del socio
    path(
    'socios/estado/<int:id>/',
    cambiar_estado_socio,
    name='cambiar_estado_socio'
    ),
    path('cobros/', lista_cobros, name='lista_cobros'),
    path('cobros/nuevo/', nuevo_cobro, name='nuevo_cobro'),
    path(
        'cobros/comprobante/<int:id>/',
        comprobante_cobro,
        name='comprobante_cobro'
    ),
    path(
        'cobros/pdf/<int:id>/',
        pdf_cobro,
        name='pdf_cobro'
    ),
path(
    'cobros/enviar-email/<int:id>/',
    enviar_email_cobro,
    name='enviar_email_cobro'
),
path(
    'inventario/tipos/',
    lista_tipos_articulo,
    name='lista_tipos_articulo'
),

path(
    'inventario/tipos/nuevo/',
    nuevo_tipo_articulo,
    name='nuevo_tipo_articulo'
),

path(
    'inventario/tipos/editar/<int:id>/',
    editar_tipo_articulo,
    name='editar_tipo_articulo'
),

path(
    'inventario/tipos/estado/<int:id>/',
    cambiar_estado_tipo_articulo,
    name='cambiar_estado_tipo_articulo'
),
path(
    'inventario/categorias/',
    lista_categorias_articulo,
    name='lista_categorias_articulo'
),

path(
    'inventario/categorias/nuevo/',
    nuevo_categoria_articulo,
    name='nuevo_categoria_articulo'
),

path(
    'inventario/categorias/editar/<int:id>/',
    editar_categoria_articulo,
    name='editar_categoria_articulo'
),

path(
    'inventario/categorias/estado/<int:id>/',
    cambiar_estado_categoria_articulo,
    name='cambiar_estado_categoria_articulo'
),
path(
    'inventario/productos/',
    lista_productos,
    name='lista_productos'
),

path(
    'inventario/productos/nuevo/',
    nuevo_producto,
    name='nuevo_producto'
),

path(
    'inventario/productos/editar/<int:id>/',
    editar_producto,
    name='editar_producto'
),

path(
    'inventario/productos/estado/<int:id>/',
    cambiar_estado_producto,
    name='cambiar_estado_producto'
),
path(
    'inventario/movimientos/',
    lista_movimientos,
    name='lista_movimientos',
),

# Reporte de usuarios
path(
    'reportes/usuarios/',
    reporte_usuarios,
    name='reporte_usuarios',
),

]
