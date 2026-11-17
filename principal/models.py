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