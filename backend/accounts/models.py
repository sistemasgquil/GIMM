from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):

    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('RECEPTION', 'Recepción'),
        ('INSTRUCTOR', 'Instructor'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='RECEPTION'
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Socio(models.Model):

    nombres = models.CharField(
        max_length=100
    )

    apellidos = models.CharField(
        max_length=100
    )

    cedula = models.CharField(
        max_length=10,
        unique=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    fecha_registro = models.DateField(
        auto_now_add=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Cobro(models.Model):

    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA', 'Tarjeta'),
        ('OTRO', 'Otro'),
    ]

    ESTADOS = [
        ('PAGADO', 'Pagado'),
        ('PENDIENTE', 'Pendiente'),
        ('ANULADO', 'Anulado'),
    ]

    socio = models.ForeignKey(
        Socio,
        on_delete=models.PROTECT,
        related_name='cobros'
    )

    concepto = models.CharField(
        max_length=200
    )

    fecha_cobro = models.DateField(
        auto_now_add=True
    )

    fecha_vencimiento = models.DateField(
        null=True,
        blank=True
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='EFECTIVO'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PAGADO'
    )

    observacion = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.socio} - ${self.valor}"

        

class TipoArticulo(models.Model):

        nombre = models.CharField(
        max_length=100,
        unique=True
    )

        descripcion = models.TextField(
            blank=True
        )

        activo = models.BooleanField(
            default=True
        )

        def __str__(self):
            return self.nombre


class CategoriaArticulo(models.Model):

    nombre = models.CharField(
        max_length=100
    )

    tipo = models.ForeignKey(
        TipoArticulo,
        on_delete=models.PROTECT,
        related_name='categorias'
    )

    descripcion = models.TextField(
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = ('nombre', 'tipo')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.tipo.nombre} - {self.nombre}"

class Producto(models.Model):

    UNIDADES_MEDIDA = [
        ('UNIDAD', 'Unidad'),
        ('CAJA', 'Caja'),
        ('PAQUETE', 'Paquete'),
        ('PAR', 'Par'),
        ('DOCENA', 'Docena'),
        ('KILOGRAMO', 'Kilogramo'),
        ('GRAMO', 'Gramo'),
        ('LITRO', 'Litro'),
        ('MILILITRO', 'Mililitro'),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    nombre = models.CharField(
        max_length=150
    )

    tipo = models.ForeignKey(
        TipoArticulo,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    categoria = models.ForeignKey(
        CategoriaArticulo,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    descripcion = models.TextField(
        blank=True
    )

    proveedor = models.CharField(
        max_length=150,
        blank=True
    )

    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='UNIDAD'
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MovimientoInventario(models.Model):

    TIPOS_MOVIMIENTO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )

    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPOS_MOVIMIENTO
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    motivo = models.CharField(
        max_length=200
    )

    observacion = models.TextField(
        blank=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimientos_inventario'
    )

    def __str__(self):
        return (
            f"{self.producto.nombre} - "
            f"{self.tipo_movimiento} - "
            f"{self.cantidad}"
        )