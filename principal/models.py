from django.conf import settings
from django.db import models


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_completo


class Servicio(models.Model):
    class Categoria(models.TextChoices):
        CORTES = "cortes", "Cortes"
        BARBA = "barba", "Barba"
        COLOR = "color", "Coloración"

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=10,
        choices=Categoria.choices,
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["categoria", "nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name="servicio_precio_no_negativo",
            ),
        ]

    def __str__(self):
        return self.nombre


class Barbero(models.Model):
    nombre = models.CharField(max_length=150)
    especialidad = models.CharField(
        max_length=150,
        blank=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ATENDIDA = "atendida", "Atendida"
        CANCELADA = "cancelada", "Cancelada"

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="citas",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="citas",
    )
    barbero = models.ForeignKey(
        Barbero,
        on_delete=models.PROTECT,
        related_name="citas",
    )
    fecha = models.DateField()
    hora = models.TimeField()
    notas = models.TextField(
        blank=True,
        max_length=1000,
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-hora"]
        constraints = [
            models.UniqueConstraint(
                fields=["barbero", "fecha", "hora"],
                condition=models.Q(
                    estado__in=["pendiente", "atendida"],
                ),
                name="cita_turno_ocupado_unico",
            ),
        ]

    def __str__(self):
        return (
            f"{self.cliente} - {self.servicio} "
            f"- {self.fecha} {self.hora}"
        )


class Producto(models.Model):
    class Categoria(models.TextChoices):
        MAQUINAS = "maquinas", "Máquinas"
        PRODUCTOS = "productos", "Productos"
        ACCESORIOS = "accesorios", "Accesorios"

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(max_length=2000)
    categoria = models.CharField(
        max_length=15,
        choices=Categoria.choices,
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["categoria", "nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name="producto_precio_no_negativo",
            ),
        ]

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    class Estado(models.TextChoices):
        REGISTRADO = "registrado", "Registrado"

    clave_confirmacion = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.REGISTRADO,
    )

    class Meta:
        ordering = ["-fecha", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="pedido_total_no_negativo",
            ),
        ]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    nombre_producto = models.CharField(max_length=150)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad__gt=0),
                name="detalle_cantidad_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(precio_unitario__gte=0),
                name="detalle_precio_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="detalle_subtotal_no_negativo",
            ),
            models.UniqueConstraint(
                fields=["pedido", "producto"],
                name="detalle_producto_unico_por_pedido",
            ),
        ]

    def __str__(self):
        return (
            f"{self.nombre_producto} x{self.cantidad} "
            f"- Pedido #{self.pedido_id}"
        )