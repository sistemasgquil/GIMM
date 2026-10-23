from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.core.mail import EmailMessage

from weasyprint import HTML

from .models import (
    Socio,
    Cobro,
    TipoArticulo,
    CategoriaArticulo,
    Producto,
    MovimientoInventario,
)
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)

            return redirect('lista_socios')

        return render(
            request,
            'accounts/login.html',
            {
                'error': 'Usuario o contraseña incorrectos'
            }
        )

    return render(
        request,
        'accounts/login.html'
    )


# ==========================================================
# LOGOUT
# ==========================================================

def logout_view(request):

    logout(request)

    return redirect('login')


# ==========================================================
# LISTA DE SOCIOS
# ==========================================================

@login_required
def lista_socios(request):

    buscar = request.GET.get(
        'buscar',
        ''
    ).strip()

    if buscar:

        socios = Socio.objects.filter(
            Q(nombres__icontains=buscar)
            | Q(apellidos__icontains=buscar)
            | Q(cedula__icontains=buscar)
        )

    else:

        socios = Socio.objects.all()

    return render(
        request,
        'accounts/socios/lista.html',
        {
            'socios': socios,
            'buscar': buscar,
        }
    )


# ==========================================================
# NUEVO SOCIO
# ==========================================================

@login_required
def nuevo_socio(request):

    if request.method == 'POST':

        nombres = request.POST.get(
            'nombres',
            ''
        ).strip()

        apellidos = request.POST.get(
            'apellidos',
            ''
        ).strip()

        cedula = request.POST.get(
            'cedula',
            ''
        ).strip()

        telefono = request.POST.get(
            'telefono',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        fecha_nacimiento = request.POST.get(
            'fecha_nacimiento',
            ''
        ).strip()

        socio = Socio(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            telefono=telefono,
            email=email,
            fecha_nacimiento=fecha_nacimiento or None
        )

        socio.save()

        return redirect(
            'lista_socios'
        )

    return render(
        request,
        'accounts/socios/nuevo.html'
    )


# ==========================================================
# EDITAR SOCIO
# ==========================================================

@login_required
def editar_socio(request, id):

    socio = get_object_or_404(
        Socio,
        id=id
    )

    if request.method == 'POST':

        socio.nombres = request.POST.get(
            'nombres',
            ''
        ).strip()

        socio.apellidos = request.POST.get(
            'apellidos',
            ''
        ).strip()

        socio.cedula = request.POST.get(
            'cedula',
            ''
        ).strip()

        socio.telefono = request.POST.get(
            'telefono',
            ''
        ).strip()

        socio.email = request.POST.get(
            'email',
            ''
        ).strip()

        fecha_nacimiento = request.POST.get(
            'fecha_nacimiento',
            ''
        ).strip()

        if fecha_nacimiento:

            socio.fecha_nacimiento = fecha_nacimiento

        else:

            socio.fecha_nacimiento = None

        socio.save()

        return redirect(
            'lista_socios'
        )

    return render(
        request,
        'accounts/socios/editar.html',
        {
            'socio': socio
        }
    )


# ==========================================================
# CAMBIAR ESTADO DEL SOCIO
# ==========================================================

@login_required
def cambiar_estado_socio(request, id):

    socio = get_object_or_404(
        Socio,
        id=id
    )

    if request.method == 'POST':

        socio.activo = not socio.activo

        socio.save()

    return redirect(
        'lista_socios'
    )


# ==========================================================
# LISTA DE COBROS
# ==========================================================

@login_required
def lista_cobros(request):

    cobros = Cobro.objects.select_related(
        'socio'
    ).order_by(
        '-fecha_cobro'
    )

    return render(
        request,
        'accounts/cobros/lista.html',
        {
            'cobros': cobros
        }
    )


# ==========================================================
# NUEVO COBRO
# ==========================================================

@login_required
def nuevo_cobro(request):

    socios = Socio.objects.filter(
        activo=True
    ).order_by(
        'apellidos',
        'nombres'
    )

    if request.method == 'POST':

        socio_id = request.POST.get(
            'socio'
        )

        concepto = request.POST.get(
            'concepto',
            ''
        ).strip()

        fecha_vencimiento = request.POST.get(
            'fecha_vencimiento'
        )

        valor = request.POST.get(
            'valor'
        )

        metodo_pago = request.POST.get(
            'metodo_pago'
        )

        estado = request.POST.get(
            'estado'
        )

        observacion = request.POST.get(
            'observacion',
            ''
        ).strip()

        socio = get_object_or_404(
            Socio,
            id=socio_id
        )

        Cobro.objects.create(
            socio=socio,
            concepto=concepto,
            fecha_vencimiento=fecha_vencimiento or None,
            valor=valor,
            metodo_pago=metodo_pago,
            estado=estado,
            observacion=observacion
        )

        return redirect(
            'lista_cobros'
        )

    return render(
        request,
        'accounts/cobros/nuevo.html',
        {
            'socios': socios
        }
    )


# ==========================================================
# COMPROBANTE DE COBRO
# ==========================================================

@login_required
def comprobante_cobro(request, id):

    cobro = get_object_or_404(
        Cobro.objects.select_related(
            'socio'
        ),
        id=id
    )

    return render(
        request,
        'accounts/cobros/comprobante.html',
        {
            'cobro': cobro
        }
    )


# ==========================================================
# GENERAR PDF DEL COBRO
# ==========================================================

@login_required
def pdf_cobro(request, id):

    cobro = get_object_or_404(
        Cobro.objects.select_related(
            'socio'
        ),
        id=id
    )

    html_string = render(
        request,
        'accounts/cobros/comprobante.html',
        {
            'cobro': cobro
        }
    ).content.decode(
        'utf-8'
    )

    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
    ).write_pdf()

    response = HttpResponse(
        pdf,
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="comprobante_{cobro.id}.pdf"'
    )

    return response


# ==========================================================
# ENVIAR COMPROBANTE POR EMAIL
# ==========================================================

@login_required
def enviar_email_cobro(request, id):

    if request.method != 'POST':

        return redirect(
            'comprobante_cobro',
            id=id
        )

    cobro = get_object_or_404(
        Cobro.objects.select_related(
            'socio'
        ),
        id=id
    )

    # ------------------------------------------------------
    # Obtener el email del socio
    # ------------------------------------------------------

    email_destino = cobro.socio.email.strip()

    # ------------------------------------------------------
    # Verificar que tenga email
    # ------------------------------------------------------

    if not email_destino:

        return render(
            request,
            'accounts/cobros/comprobante.html',
            {
                'cobro': cobro,
                'email_error': (
                    'El socio no tiene un correo '
                    'electrónico registrado.'
                )
            }
        )

    # ------------------------------------------------------
    # Generar PDF
    # ------------------------------------------------------

    html_string = render(
        request,
        'accounts/cobros/comprobante.html',
        {
            'cobro': cobro
        }
    ).content.decode(
        'utf-8'
    )

    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
    ).write_pdf()

    # ------------------------------------------------------
    # Datos del correo
    # ------------------------------------------------------

    asunto = 'Comprobante de pago - GIMM'

    mensaje = f"""
Hola {cobro.socio.nombres} {cobro.socio.apellidos}.

Gracias por su pago realizado en GIMM.

Adjuntamos su comprobante de pago en formato PDF.

Concepto: {cobro.concepto}
Valor: ${cobro.valor}
Fecha de cobro: {cobro.fecha_cobro.strftime('%d/%m/%Y')}

Gracias por utilizar GIMM.

Sistema de Gestión de Gimnasio
"""

    # ------------------------------------------------------
    # Crear correo
    # ------------------------------------------------------

    correo = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=None,
        to=[
            email_destino
        ]
    )

    # ------------------------------------------------------
    # Adjuntar PDF
    # ------------------------------------------------------

    correo.attach(
        f'comprobante_{cobro.id}.pdf',
        pdf,
        'application/pdf'
    )

    # ------------------------------------------------------
    # Enviar correo
    # ------------------------------------------------------

    correo.send(
        fail_silently=False
    )

    # ------------------------------------------------------
    # Mostrar comprobante nuevamente
    # ------------------------------------------------------

    return render(
        request,
        'accounts/cobros/comprobante.html',
        {
            'cobro': cobro,
            'email_enviado': email_destino
        }
    )
# ==========================================================
# INVENTARIO - LISTA DE TIPOS DE ARTÍCULO
# ==========================================================

@login_required
def lista_tipos_articulo(request):

    tipos = TipoArticulo.objects.all()

    return render(
        request,
        'accounts/inventario/tipos/lista.html',
        {
            'tipos': tipos
        }
    )


# ==========================================================
# INVENTARIO - NUEVO TIPO DE ARTÍCULO
# ==========================================================

@login_required
def nuevo_tipo_articulo(request):

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        TipoArticulo.objects.create(
            nombre=nombre,
            descripcion=descripcion
        )

        return redirect(
            'lista_tipos_articulo'
        )

    return render(
        request,
        'accounts/inventario/tipos/nuevo.html'
    )


# ==========================================================
# INVENTARIO - EDITAR TIPO DE ARTÍCULO
# ==========================================================

@login_required
def editar_tipo_articulo(request, id):

    tipo = get_object_or_404(
        TipoArticulo,
        id=id
    )

    if request.method == 'POST':

        tipo.nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        tipo.descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        tipo.save()

        return redirect(
            'lista_tipos_articulo'
        )

    return render(
        request,
        'accounts/inventario/tipos/editar.html',
        {
            'tipo': tipo
        }
    )


# ==========================================================
# INVENTARIO - CAMBIAR ESTADO DEL TIPO
# ==========================================================

@login_required
def cambiar_estado_tipo_articulo(request, id):

    tipo = get_object_or_404(
        TipoArticulo,
        id=id
    )

    if request.method == 'POST':

        tipo.activo = not tipo.activo

        tipo.save()

    return redirect(
        'lista_tipos_articulo'
    )
# ==========================================================
# CATEGORIAS DE ARTICULOS
# ==========================================================

@login_required
def lista_categorias_articulo(request):

    categorias = CategoriaArticulo.objects.select_related(
        'tipo'
    ).all()

    return render(
        request,
        'accounts/inventario/categorias/lista.html',
        {
            'categorias': categorias
        }
    )


@login_required
def nuevo_categoria_articulo(request):

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        tipo_id = request.POST.get(
            'tipo'
        )

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True
        )

        # Evitar categorías duplicadas
        if CategoriaArticulo.objects.filter(
            nombre__iexact=nombre,
            tipo=tipo
        ).exists():

            return render(
                request,
                'accounts/inventario/categorias/nuevo.html',
                {
                    'tipos': tipos,
                    'error': 'Ya existe una categoría con ese nombre para este tipo de artículo.'
                }
            )

        CategoriaArticulo.objects.create(
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion
        )

        return redirect(
            'lista_categorias_articulo'
        )

    return render(
        request,
        'accounts/inventario/categorias/nuevo.html',
        {
            'tipos': tipos
        }
    )


@login_required
def editar_categoria_articulo(request, id):

    categoria = get_object_or_404(
        CategoriaArticulo,
        id=id
    )

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    if request.method == 'POST':

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        tipo_id = request.POST.get(
            'tipo'
        )

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True
        )

        # Evitar duplicados
        if CategoriaArticulo.objects.filter(
            nombre__iexact=nombre,
            tipo=tipo
        ).exclude(
            id=categoria.id
        ).exists():

            return render(
                request,
                'accounts/inventario/categorias/editar.html',
                {
                    'categoria': categoria,
                    'tipos': tipos,
                    'error': 'Ya existe otra categoría con ese nombre para este tipo de artículo.'
                }
            )

        categoria.nombre = nombre
        categoria.tipo = tipo
        categoria.descripcion = descripcion

        categoria.save()

        return redirect(
            'lista_categorias_articulo'
        )

    return render(
        request,
        'accounts/inventario/categorias/editar.html',
        {
            'categoria': categoria,
            'tipos': tipos
        }
    )


@login_required
def cambiar_estado_categoria_articulo(request, id):

    categoria = get_object_or_404(
        CategoriaArticulo,
        id=id
    )

    if request.method == 'POST':

        categoria.activo = not categoria.activo

        categoria.save()

    return redirect(
        'lista_categorias_articulo'
    )
# ==========================================================
# PRODUCTOS
# ==========================================================

@login_required
def lista_productos(request):

    productos = Producto.objects.select_related(
        'tipo',
        'categoria'
    ).all()

    return render(
        request,
        'accounts/inventario/productos/lista.html',
        {
            'productos': productos
        }
    )


@login_required
def nuevo_producto(request):

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    categorias = CategoriaArticulo.objects.filter(
        activo=True
    ).select_related(
        'tipo'
    ).order_by('nombre')

    if request.method == 'POST':

        codigo = request.POST.get(
            'codigo',
            ''
        ).strip()

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        tipo_id = request.POST.get(
            'tipo'
        )

        categoria_id = request.POST.get(
            'categoria'
        )

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        proveedor = request.POST.get(
            'proveedor',
            ''
        ).strip()

        precio_compra = request.POST.get(
            'precio_compra',
            '0'
        )

        precio_venta = request.POST.get(
            'precio_venta',
            '0'
        )

        stock = request.POST.get(
            'stock',
            '0'
        )

        stock_minimo = request.POST.get(
            'stock_minimo',
            '0'
        )

        unidad_medida = request.POST.get(
            'unidad_medida',
            'UNIDAD'
        )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True
        )

        categoria = get_object_or_404(
            CategoriaArticulo,
            id=categoria_id,
            activo=True
        )

        # Verificar que la categoría pertenezca al tipo seleccionado
        if categoria.tipo_id != tipo.id:

            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                {
                    'tipos': tipos,
                    'categorias': categorias,
                    'unidades': Producto.UNIDADES_MEDIDA,
                    'error': 'La categoría seleccionada no pertenece al tipo de artículo seleccionado.'
                }
            )

        # Evitar códigos duplicados
        if Producto.objects.filter(
            codigo=codigo
        ).exists():

            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                {
                    'tipos': tipos,
                    'categorias': categorias,
                    'unidades': Producto.UNIDADES_MEDIDA,
                    'error': 'Ya existe un producto con ese código.'
                }
            )

        Producto.objects.create(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            categoria=categoria,
            descripcion=descripcion,
            proveedor=proveedor,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock=stock,
            stock_minimo=stock_minimo,
            unidad_medida=unidad_medida
        )

        return redirect(
            'lista_productos'
        )

    return render(
        request,
        'accounts/inventario/productos/nuevo.html',
        {
            'tipos': tipos,
            'categorias': categorias,
            'unidades': Producto.UNIDADES_MEDIDA
        }
    )


@login_required
def editar_producto(request, id):

    producto = get_object_or_404(
        Producto,
        id=id
    )

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    categorias = CategoriaArticulo.objects.filter(
        activo=True
    ).select_related(
        'tipo'
    ).order_by('nombre')

    if request.method == 'POST':

        codigo = request.POST.get(
            'codigo',
            ''
        ).strip()

        nombre = request.POST.get(
            'nombre',
            ''
        ).strip()

        tipo_id = request.POST.get(
            'tipo'
        )

        categoria_id = request.POST.get(
            'categoria'
        )

        descripcion = request.POST.get(
            'descripcion',
            ''
        ).strip()

        proveedor = request.POST.get(
            'proveedor',
            ''
        ).strip()

        precio_compra = request.POST.get(
            'precio_compra',
            '0'
        )

        precio_venta = request.POST.get(
            'precio_venta',
            '0'
        )

        stock = request.POST.get(
            'stock',
            '0'
        )

        stock_minimo = request.POST.get(
            'stock_minimo',
            '0'
        )

        unidad_medida = request.POST.get(
            'unidad_medida',
            'UNIDAD'
        )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True
        )

        categoria = get_object_or_404(
            CategoriaArticulo,
            id=categoria_id,
            activo=True
        )

        if categoria.tipo_id != tipo.id:

            return render(
                request,
                'accounts/inventario/productos/editar.html',
                {
                    'producto': producto,
                    'tipos': tipos,
                    'categorias': categorias,
                    'unidades': Producto.UNIDADES_MEDIDA,
                    'error': 'La categoría seleccionada no pertenece al tipo de artículo seleccionado.'
                }
            )

        if Producto.objects.filter(
            codigo=codigo
        ).exclude(
            id=producto.id
        ).exists():

            return render(
                request,
                'accounts/inventario/productos/editar.html',
                {
                    'producto': producto,
                    'tipos': tipos,
                    'categorias': categorias,
                    'unidades': Producto.UNIDADES_MEDIDA,
                    'error': 'Ya existe otro producto con ese código.'
                }
            )

        producto.codigo = codigo
        producto.nombre = nombre
        producto.tipo = tipo
        producto.categoria = categoria
        producto.descripcion = descripcion
        producto.proveedor = proveedor
        producto.precio_compra = precio_compra
        producto.precio_venta = precio_venta
        producto.stock = stock
        producto.stock_minimo = stock_minimo
        producto.unidad_medida = unidad_medida

        producto.save()

        return redirect(
            'lista_productos'
        )

    return render(
        request,
        'accounts/inventario/productos/editar.html',
        {
            'producto': producto,
            'tipos': tipos,
            'categorias': categorias,
            'unidades': Producto.UNIDADES_MEDIDA
        }
    )


@login_required
def cambiar_estado_producto(request, id):

    producto = get_object_or_404(
        Producto,
        id=id
    )

    if request.method == 'POST':

        producto.activo = not producto.activo

        producto.save()

    return redirect(
        'lista_productos'
    )
@login_required
def nuevo_producto(request):

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    categorias = CategoriaArticulo.objects.filter(
        activo=True
    ).select_related('tipo').order_by('nombre')

    if request.method == 'POST':

        codigo = request.POST.get('codigo', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        tipo_id = request.POST.get('tipo')
        categoria_id = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion', '').strip()
        proveedor = request.POST.get('proveedor', '').strip()
        precio_compra = request.POST.get('precio_compra') or 0
        precio_venta = request.POST.get('precio_venta') or 0
        stock = request.POST.get('stock') or 0
        stock_minimo = request.POST.get('stock_minimo') or 0
        unidad_medida = request.POST.get('unidad_medida')

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True
        )

        categoria = get_object_or_404(
            CategoriaArticulo,
            id=categoria_id,
            activo=True
        )

        Producto.objects.create(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            categoria=categoria,
            descripcion=descripcion,
            proveedor=proveedor,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock=stock,
            stock_minimo=stock_minimo,
            unidad_medida=unidad_medida,
        )

        return redirect('lista_productos')

    return render(
        request,
        'accounts/inventario/productos/nuevo.html',
        {
            'tipos': tipos,
            'categorias': categorias,
        }
    )
# region de Reportes: socios..
@login_required
def reporte_usuarios(request):
    usuarios = User.objects.select_related('profile').all().order_by('username')

    # Búsqueda por usuario, nombres, apellidos o correo
    buscar = request.GET.get('buscar', '').strip()

    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    # Filtro por rol
    rol = request.GET.get('rol', '').strip()

    if rol in ['ADMIN', 'RECEPTION', 'INSTRUCTOR']:
        usuarios = usuarios.filter(profile__role=rol)

    # Filtro por estado de la cuenta
    estado = request.GET.get('estado', '').strip()

    if estado == 'activo':
        usuarios = usuarios.filter(is_active=True, profile__active=True)
    elif estado == 'inactivo':
        usuarios = usuarios.filter(
            Q(is_active=False) | Q(profile__active=False)
        )

    # Resumen general de usuarios
    total_usuarios = User.objects.count()

    usuarios_activos = User.objects.filter(
        is_active=True,
        profile__active=True
    ).count()

    usuarios_inactivos = total_usuarios - usuarios_activos

    contexto = {
        'usuarios': usuarios,
        'buscar': buscar,
        'rol_seleccionado': rol,
        'estado_seleccionado': estado,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
    }

    return render(
        request,
        #'accounts/reportes/usuarios.html',
        'reportes/usuarios.html',
        contexto
    )