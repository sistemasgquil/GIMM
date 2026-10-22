from django.db import models
from django.contrib.auth.models import User


class Socio(models.Model):

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