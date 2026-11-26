import os
import sqlite3
import unicodedata
from datetime import datetime
from decimal import Decimal
from pathlib import Path

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "barberia_capital.settings",
)

import django

django.setup()

from django.conf import settings
from django.db import transaction
from principal.models import Barbero, Servicio


# Datos del SQL, sin repetir los servicios duplicados.
SERVICIOS = [
    ("Corte clásico", "cortes", "25000.00"),
    ("Corte + barba", "barba", "40000.00"),
    ("Fade", "cortes", "30000.00"),
    ("Afeitado clásico", "barba", "20000.00"),
    ("Diseño de barba", "barba", "18000.00"),
    ("Corte fade bajo", "cortes", "30000.00"),
    ("Corte fade alto", "cortes", "30000.00"),
    ("Corte texturizado", "cortes", "28000.00"),
    ("Corte infantil", "cortes", "20000.00"),
    ("Corte + peinado", "cortes", "35000.00"),
    ("Perfilado de barba", "barba", "18000.00"),
    ("Afeitado completo", "barba", "20000.00"),
    ("Barba + toalla caliente", "barba", "25000.00"),
    ("Tinte completo", "color", "60000.00"),
    ("Mechas", "color", "70000.00"),
    ("Decoloración", "color", "80000.00"),
    ("Balayage", "color", "90000.00"),
    ("Matiz / tónico", "color", "45000.00"),
]

BARBEROS = [
    ("Carlos Rodríguez", "Fade y cortes clásicos"),
    ("Andrés Martínez", "Barba y afeitado"),
    ("Juan Pérez", "Cortes modernos"),
]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        letra
        for letra in texto
        if not unicodedata.combining(letra)
    )
    return " ".join(texto.casefold().split())


def crear_respaldo():
    configuracion = settings.DATABASES["default"]

    if configuracion["ENGINE"] != "django.db.backends.sqlite3":
        raise ValueError(
            "Este script está preparado para tu base SQLite actual."
        )

    origen = Path(configuracion["NAME"])

    if not origen.is_file():
        raise FileNotFoundError(
            f"No encuentro la base de datos: {origen}"
        )

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    carpeta = (
        Path(settings.BASE_DIR).parent
        / f"BarberiaCapital_respaldo_catalogo_{fecha}"
    )
    carpeta.mkdir(parents=True)

    destino = carpeta / "db.sqlite3"

    # Respalda también los datos confirmados si SQLite usa WAL.
    with sqlite3.connect(str(origen)) as conexion:
        with sqlite3.connect(str(destino)) as copia:
            conexion.backup(copia)

    print(f"Respaldo creado: {destino}\n")


def ejecutar():
    crear_respaldo()
    resultados = []

    with transaction.atomic():
        servicios_existentes = {
            normalizar(nombre)
            for nombre in Servicio.objects.values_list(
                "nombre", flat=True
            )
        }

        barberos_existentes = {
            normalizar(nombre)
            for nombre in Barbero.objects.values_list(
                "nombre", flat=True
            )
        }

        for nombre, categoria, precio in SERVICIOS:
            clave = normalizar(nombre)

            if clave in servicios_existentes:
                resultados.append(
                    f"Servicio conservado: {nombre}"
                )
                continue

            Servicio.objects.create(
                nombre=nombre,
                categoria=categoria,
                precio=Decimal(precio),
                activo=True,
            )
            servicios_existentes.add(clave)
            resultados.append(f"Servicio agregado: {nombre}")

        for nombre, especialidad in BARBEROS:
            clave = normalizar(nombre)

            if clave in barberos_existentes:
                resultados.append(
                    f"Barbero conservado: {nombre}"
                )
                continue

            Barbero.objects.create(
                nombre=nombre,
                especialidad=especialidad,
                activo=True,
            )
            barberos_existentes.add(clave)
            resultados.append(f"Barbero agregado: {nombre}")

    for resultado in resultados:
        print(resultado)

    print("\nCatálogo importado.")
    print(f"Servicios totales: {Servicio.objects.count()}")
    print(f"Barberos totales: {Barbero.objects.count()}")
    print("Actualiza Citas y Reportes con Ctrl + F5.")


if __name__ == "__main__":
    ejecutar()