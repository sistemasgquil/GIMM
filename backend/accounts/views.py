from decimal import Decimal, InvalidOperation
import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
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


logger = logging.getLogger(__name__)


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        usuario = authenticate(
            request,
            username=username,
            password=password,
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('lista_socios')

        return render(
            request,
            'accounts/login.html',
            {'error': 'Usuario o contraseña incorrectos'},
        )

    return render(request, 'accounts/login.html')


# ==========================================================
# LOGOUT
# ==========================================================

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('lista_socios')


# ==========================================================
# SOCIOS
# ==========================================================

@login_required
def lista_socios(request):
    buscar = request.GET.get('buscar', '').strip()

    socios = Socio.objects.all()

    if buscar:
        socios = socios.filter(
            Q(nombres__icontains=buscar)
            | Q(apellidos__icontains=buscar)
            | Q(cedula__icontains=buscar)
        )

    socios = socios.order_by('apellidos', 'nombres')

    return render(
        request,
        'accounts/socios/lista.html',
        {
            'socios': socios,
            'buscar': buscar,
        },
    )


@login_required
def nuevo_socio(request):
    if request.method == 'POST':
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula = request.POST.get('cedula', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        fecha_nacimiento = request.POST.get(
            'fecha_nacimiento', ''
        ).strip()

        if not nombres or not apellidos or not cedula:
            messages.error(
                request,
                'Nombres, apellidos y cédula son obligatorios.',
            )
            return render(
                request,
                'accounts/socios/nuevo.html',
            )

        if Socio.objects.filter(cedula=cedula).exists():
            messages.error(
                request,
                'Ya existe un socio registrado con esa cédula.',
            )
            return render(
                request,
                'accounts/socios/nuevo.html',
            )

        socio = Socio(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            telefono=telefono,
            email=email,
            fecha_nacimiento=fecha_nacimiento or None,
        )
        socio.save()

        messages.success(request, 'Socio registrado correctamente.')
        return redirect('lista_socios')

    return render(request, 'accounts/socios/nuevo.html')


@login_required
def editar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)

    if request.method == 'POST':
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        cedula = request.POST.get('cedula', '').strip()

        if not nombres or not apellidos or not cedula:
            messages.error(
                request,
                'Nombres, apellidos y cédula son obligatorios.',
            )
            return render(
                request,
                'accounts/socios/editar.html',
                {'socio': socio},
            )

        if Socio.objects.filter(
            cedula=cedula
        ).exclude(id=socio.id).exists():
            messages.error(
                request,
                'Otro socio ya tiene registrada esa cédula.',
            )
            return render(
                request,
                'accounts/socios/editar.html',
                {'socio': socio},
            )

        socio.nombres = nombres
        socio.apellidos = apellidos
        socio.cedula = cedula
        socio.telefono = request.POST.get('telefono', '').strip()
        socio.email = request.POST.get('email', '').strip()

        fecha_nacimiento = request.POST.get(
            'fecha_nacimiento', ''
        ).strip()

        socio.fecha_nacimiento = fecha_nacimiento or None
        socio.save()

        messages.success(request, 'Socio actualizado correctamente.')
        return redirect('lista_socios')

    return render(
        request,
        'accounts/socios/editar.html',
        {'socio': socio},
    )


@login_required
def cambiar_estado_socio(request, id):
    socio = get_object_or_404(Socio, id=id)

    if request.method == 'POST':
        socio.activo = not socio.activo
        socio.save(update_fields=['activo'])

        messages.success(
            request,
            'Estado del socio actualizado correctamente.',
        )

    return redirect('lista_socios')


# ==========================================================
# COBROS
# ==========================================================

@login_required
def lista_cobros(request):
    cobros = Cobro.objects.select_related(
        'socio'
    ).order_by('-fecha_cobro')

    return render(
        request,
        'accounts/cobros/lista.html',
        {'cobros': cobros},
    )


@login_required
def nuevo_cobro(request):
    socios = Socio.objects.filter(
        activo=True
    ).order_by('apellidos', 'nombres')

    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        concepto = request.POST.get('concepto', '').strip()
        fecha_vencimiento = request.POST.get('fecha_vencimiento') or None
        valor_texto = request.POST.get('valor', '').strip()
        metodo_pago = request.POST.get('metodo_pago', '').strip()
        estado = request.POST.get('estado', '').strip()
        observacion = request.POST.get('observacion', '').strip()

        try:
            valor = Decimal(valor_texto)

            if (
                not valor.is_finite()
                or valor <= 0
                or valor.as_tuple().exponent < -2
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            messages.error(
                request,
                'Ingresa un valor de cobro válido.',
            )
            return render(
                request,
                'accounts/cobros/nuevo.html',
                {'socios': socios},
            )

        socio = get_object_or_404(
            Socio,
            id=socio_id,
            activo=True,
        )

        if not concepto:
            messages.error(request, 'El concepto es obligatorio.')
            return render(
                request,
                'accounts/cobros/nuevo.html',
                {'socios': socios},
            )

        try:
            Cobro.objects.create(
                socio=socio,
                concepto=concepto,
                fecha_vencimiento=fecha_vencimiento,
                valor=valor,
                metodo_pago=metodo_pago,
                estado=estado,
                observacion=observacion,
            )
        except Exception:
            logger.exception('Error al registrar el cobro.')
            messages.error(
                request,
                'No se pudo registrar el cobro. Verifica los datos.',
            )
            return render(
                request,
                'accounts/cobros/nuevo.html',
                {'socios': socios},
            )

        messages.success(request, 'Cobro registrado correctamente.')
        return redirect('lista_cobros')

    return render(
        request,
        'accounts/cobros/nuevo.html',
        {'socios': socios},
    )


@login_required
def comprobante_cobro(request, id):
    cobro = get_object_or_404(
        Cobro.objects.select_related('socio'),
        id=id,
    )

    return render(
        request,
        'accounts/cobros/comprobante.html',
        {'cobro': cobro},
    )


@login_required
def pdf_cobro(request, id):
    cobro = get_object_or_404(
        Cobro.objects.select_related('socio'),
        id=id,
    )

    html_string = render(
        request,
        'accounts/cobros/comprobante.html',
        {'cobro': cobro},
    ).content.decode('utf-8')

    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/'),
    ).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="comprobante_{cobro.id}.pdf"'
    )

    return response


@login_required
def enviar_email_cobro(request, id):
    if request.method != 'POST':
        return redirect('comprobante_cobro', id=id)

    cobro = get_object_or_404(
        Cobro.objects.select_related('socio'),
        id=id,
    )

    email_destino = (cobro.socio.email or '').strip()

    if not email_destino:
        messages.error(
            request,
            'El socio no tiene un correo electrónico registrado.',
        )
        return redirect('comprobante_cobro', id=id)

    html_string = render(
        request,
        'accounts/cobros/comprobante.html',
        {'cobro': cobro},
    ).content.decode('utf-8')

    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/'),
    ).write_pdf()

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

    correo = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=None,
        to=[email_destino],
    )

    correo.attach(
        f'comprobante_{cobro.id}.pdf',
        pdf,
        'application/pdf',
    )

    try:
        correo.send(fail_silently=False)
    except Exception:
        logger.exception('Error al enviar el comprobante por correo.')
        messages.error(
            request,
            'No se pudo enviar el correo. Verifica la configuración SMTP.',
        )
        return redirect('comprobante_cobro', id=id)

    messages.success(
        request,
        f'Comprobante enviado a {email_destino}.',
    )

    return redirect('comprobante_cobro', id=id)


# ==========================================================
# INVENTARIO - TIPOS DE ARTÍCULO
# ==========================================================

@login_required
def lista_tipos_articulo(request):
    tipos = TipoArticulo.objects.all().order_by('nombre')

    return render(
        request,
        'accounts/inventario/tipos/lista.html',
        {'tipos': tipos},
    )


@login_required
def nuevo_tipo_articulo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(
                request,
                'accounts/inventario/tipos/nuevo.html',
            )

        TipoArticulo.objects.create(
            nombre=nombre,
            descripcion=descripcion,
        )

        messages.success(
            request,
            'Tipo de artículo registrado correctamente.',
        )
        return redirect('lista_tipos_articulo')

    return render(
        request,
        'accounts/inventario/tipos/nuevo.html',
    )


@login_required
def editar_tipo_articulo(request, id):
    tipo = get_object_or_404(TipoArticulo, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(
                request,
                'accounts/inventario/tipos/editar.html',
                {'tipo': tipo},
            )

        tipo.nombre = nombre
        tipo.descripcion = descripcion
        tipo.save()

        messages.success(
            request,
            'Tipo de artículo actualizado correctamente.',
        )
        return redirect('lista_tipos_articulo')

    return render(
        request,
        'accounts/inventario/tipos/editar.html',
        {'tipo': tipo},
    )


@login_required
def cambiar_estado_tipo_articulo(request, id):
    tipo = get_object_or_404(TipoArticulo, id=id)

    if request.method == 'POST':
        tipo.activo = not tipo.activo
        tipo.save(update_fields=['activo'])

        messages.success(
            request,
            'Estado del tipo de artículo actualizado.',
        )

    return redirect('lista_tipos_articulo')


# ==========================================================
# INVENTARIO - CATEGORÍAS
# ==========================================================

@login_required
def lista_categorias_articulo(request):
    categorias = CategoriaArticulo.objects.select_related(
        'tipo'
    ).order_by('tipo__nombre', 'nombre')

    return render(
        request,
        'accounts/inventario/categorias/lista.html',
        {'categorias': categorias},
    )


@login_required
def nuevo_categoria_articulo(request):
    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        tipo_id = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion', '').strip()

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(
                request,
                'accounts/inventario/categorias/nuevo.html',
                {'tipos': tipos},
            )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True,
        )

        if CategoriaArticulo.objects.filter(
            nombre__iexact=nombre,
            tipo=tipo,
        ).exists():
            return render(
                request,
                'accounts/inventario/categorias/nuevo.html',
                {
                    'tipos': tipos,
                    'error': (
                        'Ya existe una categoría con ese nombre '
                        'para este tipo de artículo.'
                    ),
                },
            )

        CategoriaArticulo.objects.create(
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion,
        )

        messages.success(
            request,
            'Categoría registrada correctamente.',
        )
        return redirect('lista_categorias_articulo')

    return render(
        request,
        'accounts/inventario/categorias/nuevo.html',
        {'tipos': tipos},
    )


@login_required
def editar_categoria_articulo(request, id):
    categoria = get_object_or_404(CategoriaArticulo, id=id)

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        tipo_id = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion', '').strip()

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return render(
                request,
                'accounts/inventario/categorias/editar.html',
                {
                    'categoria': categoria,
                    'tipos': tipos,
                },
            )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True,
        )

        if CategoriaArticulo.objects.filter(
            nombre__iexact=nombre,
            tipo=tipo,
        ).exclude(id=categoria.id).exists():
            return render(
                request,
                'accounts/inventario/categorias/editar.html',
                {
                    'categoria': categoria,
                    'tipos': tipos,
                    'error': (
                        'Ya existe otra categoría con ese nombre '
                        'para este tipo de artículo.'
                    ),
                },
            )

        categoria.nombre = nombre
        categoria.tipo = tipo
        categoria.descripcion = descripcion
        categoria.save()

        messages.success(
            request,
            'Categoría actualizada correctamente.',
        )
        return redirect('lista_categorias_articulo')

    return render(
        request,
        'accounts/inventario/categorias/editar.html',
        {
            'categoria': categoria,
            'tipos': tipos,
        },
    )


@login_required
def cambiar_estado_categoria_articulo(request, id):
    categoria = get_object_or_404(CategoriaArticulo, id=id)

    if request.method == 'POST':
        categoria.activo = not categoria.activo
        categoria.save(update_fields=['activo'])

        messages.success(
            request,
            'Estado de la categoría actualizado.',
        )

    return redirect('lista_categorias_articulo')


# ==========================================================
# INVENTARIO - PRODUCTOS
# ==========================================================

@login_required
def lista_productos(request):
    productos = Producto.objects.select_related(
        'tipo',
        'categoria',
    ).order_by('nombre')

    buscar = request.GET.get('buscar', '').strip()

    if buscar:
        productos = productos.filter(
            Q(codigo__icontains=buscar)
            | Q(nombre__icontains=buscar)
            | Q(categoria__nombre__icontains=buscar)
        )

    return render(
        request,
        'accounts/inventario/productos/lista.html',
        {
            'productos': productos,
            'buscar': buscar,
        },
    )


@login_required
def nuevo_producto(request):
    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    categorias = CategoriaArticulo.objects.filter(
        activo=True
    ).select_related('tipo').order_by('nombre')

    contexto = {
        'tipos': tipos,
        'categorias': categorias,
        'unidades': Producto.UNIDADES_MEDIDA,
    }

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        tipo_id = request.POST.get('tipo')
        categoria_id = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion', '').strip()
        proveedor = request.POST.get('proveedor', '').strip()
        unidad_medida = request.POST.get('unidad_medida', '').strip()

        try:
            precio_compra = Decimal(
                request.POST.get('precio_compra', '0') or '0'
            )
            precio_venta = Decimal(
                request.POST.get('precio_venta', '0') or '0'
            )
            stock = Decimal(request.POST.get('stock', '0') or '0')
            stock_minimo = Decimal(
                request.POST.get('stock_minimo', '0') or '0'
            )

            valores = [
                precio_compra,
                precio_venta,
                stock,
                stock_minimo,
            ]

            if any(
                not valor.is_finite() or valor < 0
                for valor in valores
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            contexto['error'] = (
                'Los precios y las cantidades deben ser números '
                'válidos y no negativos.'
            )
            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                contexto,
            )

        if not codigo or not nombre or not tipo_id or not categoria_id:
            contexto['error'] = (
                'Completa el código, nombre, tipo y categoría.'
            )
            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                contexto,
            )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True,
        )

        categoria = get_object_or_404(
            CategoriaArticulo,
            id=categoria_id,
            activo=True,
        )

        if categoria.tipo_id != tipo.id:
            contexto['error'] = (
                'La categoría seleccionada no pertenece '
                'al tipo de artículo seleccionado.'
            )
            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                contexto,
            )

        if Producto.objects.filter(codigo=codigo).exists():
            contexto['error'] = 'Ya existe un producto con ese código.'
            return render(
                request,
                'accounts/inventario/productos/nuevo.html',
                contexto,
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

        messages.success(request, 'Producto registrado correctamente.')
        return redirect('lista_productos')

    return render(
        request,
        'accounts/inventario/productos/nuevo.html',
        contexto,
    )


@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    tipos = TipoArticulo.objects.filter(
        activo=True
    ).order_by('nombre')

    categorias = CategoriaArticulo.objects.filter(
        activo=True
    ).select_related('tipo').order_by('nombre')

    contexto = {
        'producto': producto,
        'tipos': tipos,
        'categorias': categorias,
        'unidades': Producto.UNIDADES_MEDIDA,
    }

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        tipo_id = request.POST.get('tipo')
        categoria_id = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion', '').strip()
        proveedor = request.POST.get('proveedor', '').strip()
        unidad_medida = request.POST.get('unidad_medida', '').strip()

        try:
            precio_compra = Decimal(
                request.POST.get('precio_compra', '0') or '0'
            )
            precio_venta = Decimal(
                request.POST.get('precio_venta', '0') or '0'
            )
            stock = Decimal(request.POST.get('stock', '0') or '0')
            stock_minimo = Decimal(
                request.POST.get('stock_minimo', '0') or '0'
            )

            valores = [
                precio_compra,
                precio_venta,
                stock,
                stock_minimo,
            ]

            if any(
                not valor.is_finite() or valor < 0
                for valor in valores
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            contexto['error'] = (
                'Los precios y las cantidades deben ser números '
                'válidos y no negativos.'
            )
            return render(
                request,
                'accounts/inventario/productos/editar.html',
                contexto,
            )

        if not codigo or not nombre or not tipo_id or not categoria_id:
            contexto['error'] = (
                'Completa el código, nombre, tipo y categoría.'
            )
            return render(
                request,
                'accounts/inventario/productos/editar.html',
                contexto,
            )

        tipo = get_object_or_404(
            TipoArticulo,
            id=tipo_id,
            activo=True,
        )

        categoria = get_object_or_404(
            CategoriaArticulo,
            id=categoria_id,
            activo=True,
        )

        if categoria.tipo_id != tipo.id:
            contexto['error'] = (
                'La categoría seleccionada no pertenece '
                'al tipo de artículo seleccionado.'
            )
            return render(
                request,
                'accounts/inventario/productos/editar.html',
                contexto,
            )

        if Producto.objects.filter(
            codigo=codigo
        ).exclude(id=producto.id).exists():
            contexto['error'] = (
                'Ya existe otro producto con ese código.'
            )
            return render(
                request,
                'accounts/inventario/productos/editar.html',
                contexto,
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

        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('lista_productos')

    return render(
        request,
        'accounts/inventario/productos/editar.html',
        contexto,
    )


@login_required
def cambiar_estado_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.activo = not producto.activo
        producto.save(update_fields=['activo'])

        messages.success(
            request,
            'Estado del producto actualizado.',
        )

    return redirect('lista_productos')


# ==========================================================
# INVENTARIO - MOVIMIENTOS
# ==========================================================

@login_required
def lista_movimientos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto', '').strip()
        tipo_movimiento = request.POST.get(
            'tipo_movimiento', ''
        ).strip().upper()
        cantidad_texto = request.POST.get('cantidad', '').strip()
        motivo = request.POST.get('motivo', '').strip()
        observacion = request.POST.get('observacion', '').strip()

        if not all([
            producto_id,
            tipo_movimiento,
            cantidad_texto,
            motivo,
        ]):
            messages.error(
                request,
                'Completa todos los campos obligatorios.',
            )
            return redirect('lista_movimientos')

        try:
            producto_id = int(producto_id)

            if producto_id <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                'El producto seleccionado no es válido.',
            )
            return redirect('lista_movimientos')

        try:
            cantidad = Decimal(cantidad_texto)

            if (
                not cantidad.is_finite()
                or cantidad <= 0
                or cantidad.as_tuple().exponent < -2
                or cantidad.adjusted() > 7
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            messages.error(
                request,
                'Ingresa una cantidad válida con un máximo de dos decimales.',
            )
            return redirect('lista_movimientos')

        tipos_validos = {'ENTRADA', 'SALIDA', 'AJUSTE'}

        if tipo_movimiento not in tipos_validos:
            messages.error(
                request,
                'Selecciona un tipo de movimiento válido.',
            )
            return redirect('lista_movimientos')

        try:
            with transaction.atomic():
                producto = Producto.objects.select_for_update().get(
                    pk=producto_id,
                    activo=True,
                )

                stock_anterior = Decimal(str(producto.stock))

                if tipo_movimiento == 'ENTRADA':
                    stock_nuevo = stock_anterior + cantidad

                elif tipo_movimiento == 'SALIDA':
                    if cantidad > stock_anterior:
                        messages.error(
                            request,
                            (
                                f'Stock insuficiente para {producto.nombre}. '
                                f'Stock disponible: {stock_anterior}.'
                            ),
                        )
                        return redirect('lista_movimientos')

                    stock_nuevo = stock_anterior - cantidad

                else:
                    # En AJUSTE, la cantidad representa el stock final.
                    stock_nuevo = cantidad

                producto.stock = stock_nuevo
                producto.save(update_fields=['stock'])

                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo_movimiento=tipo_movimiento,
                    cantidad=cantidad,
                    motivo=motivo,
                    observacion=observacion,
                    usuario=request.user,
                )

            messages.success(
                request,
                (
                    'Movimiento registrado correctamente. '
                    f'Stock anterior: {stock_anterior}. '
                    f'Stock actual: {stock_nuevo}.'
                ),
            )

        except Producto.DoesNotExist:
            messages.error(
                request,
                'El producto no existe o está inactivo.',
            )

        except Exception:
            logger.exception(
                'Error al registrar un movimiento de inventario.'
            )
            messages.error(
                request,
                'No se pudo registrar el movimiento. '
                'Revisa el error en la terminal.',
            )

        return redirect('lista_movimientos')

    movimientos = MovimientoInventario.objects.select_related(
        'producto',
        'usuario',
    ).order_by('-fecha', '-id')

    productos = Producto.objects.filter(
        activo=True
    ).order_by('nombre')

    contexto = {
        'movimientos': movimientos,
        'productos': productos,
        'total_movimientos': movimientos.count(),
        'total_entradas': movimientos.filter(
            tipo_movimiento='ENTRADA'
        ).count(),
        'total_salidas': movimientos.filter(
            tipo_movimiento='SALIDA'
        ).count(),
        'total_ajustes': movimientos.filter(
            tipo_movimiento='AJUSTE'
        ).count(),
    }

    return render(
        request,
        'accounts/inventario/movimientos/lista.html',
        contexto,
    )


# ==========================================================
# REPORTES - USUARIOS
# ==========================================================

@login_required
def reporte_usuarios(request):
    usuarios = User.objects.select_related(
        'profile'
    ).all().order_by('username')

    buscar = request.GET.get('buscar', '').strip()

    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    rol = request.GET.get('rol', '').strip()

    if rol in ['ADMIN', 'RECEPTION', 'INSTRUCTOR']:
        usuarios = usuarios.filter(profile__role=rol)

    estado = request.GET.get('estado', '').strip()

    if estado == 'activo':
        usuarios = usuarios.filter(
            is_active=True,
            profile__active=True,
        )

    elif estado == 'inactivo':
        usuarios = usuarios.filter(
            Q(is_active=False) | Q(profile__active=False)
        )

    total_usuarios = User.objects.count()

    usuarios_activos = User.objects.filter(
        is_active=True,
        profile__active=True,
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
        'reportes/usuarios.html',
        contexto,
    )