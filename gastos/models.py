from django.conf import settings
from django.db import models


class Gasto(models.Model):
    class Categoria(models.TextChoices):
        ALIMENTACION = "alimentacion", "Alimentación"
        TRANSPORTE = "transporte", "Transporte"
        HOGAR = "hogar", "Hogar"
        ENTRETENIMIENTO = "entretenimiento", "Entretenimiento"
        SALUD = "salud", "Salud"
        OTROS = "otros", "Otros"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gastos"
    )
    # Pesos colombianos enteros, sin centavos.
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    fecha = models.DateField()
    categoria = models.CharField(max_length=20, choices=Categoria, default=Categoria.OTROS)
    descripcion = models.CharField(max_length=200, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name="gasto_monto_positivo",
                violation_error_message="El monto debe ser mayor que cero.",
            ),
        ]

    def __str__(self):
        return f"{self.descripcion or self.get_categoria_display()} · ${self.monto}"


class Meta(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="metas"
    )
    nombre = models.CharField(max_length=100)
    # Pesos colombianos enteros, sin centavos.
    precio = models.DecimalField(max_digits=12, decimal_places=0)
    ahorrado = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    fecha_limite = models.DateField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha_limite", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gt=0),
                name="meta_precio_positivo",
                violation_error_message="El precio debe ser mayor que cero.",
            ),
            models.CheckConstraint(
                condition=models.Q(ahorrado__gte=0),
                name="meta_ahorrado_no_negativo",
                violation_error_message="Lo ahorrado no puede ser negativo.",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} · ${self.precio}"
