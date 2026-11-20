import os
from decimal import Decimal

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "barberia_capital.settings",
)
django.setup()

from django.db import transaction
from principal.models import Producto


PRODUCTOS = [
    {
        "nombre": "Wahl Magic Clip",
        "descripcion": "Máquina profesional para cortes de cabello.",
        "precio": Decimal("320000.00"),
        "stock": 5,
        "categoria": "maquinas",
    },
    {
        "nombre": "Oster Fast Feed",
        "descripcion": "Máquina profesional de corte ajustable.",
        "precio": Decimal("280000.00"),
        "stock": 5,
        "categoria": "maquinas",
    },
    {
        "nombre": "Pomada Layrite Natural",
        "descripcion": "Pomada para peinado de acabado natural.",
        "precio": Decimal("65000.00"),
        "stock": 10,
        "categoria": "productos",
    },
    {
        "nombre": "Aceite para barba 30ml",
        "descripcion": "Aceite para cuidado y mantenimiento de la barba.",
        "precio": Decimal("38000.00"),
        "stock": 10,
        "categoria": "productos",
    },
    {
        "nombre": "Navaja Dovo Solingen",
        "descripcion": "Navaja profesional para barbería.",
        "precio": Decimal("180000.00"),
        "stock": 5,
        "categoria": "accesorios",
    },
    {
        "nombre": "Peine barbero carbono x5",
        "descripcion": "Set de peines profesionales de carbono.",
        "precio": Decimal("35000.00"),
        "stock": 10,
        "categoria": "accesorios",
    },
]


def cargar_productos():
    creados = 0
    existentes = 0

    with transaction.atomic():
        for datos in PRODUCTOS:
            valores = datos.copy()
            nombre = valores.pop("nombre")
            valores["activo"] = True

            producto, creado = Producto.objects.get_or_create(
                nombre=nombre,
                defaults=valores,
            )

            if creado:
                creados += 1
                print(f"Creado: {producto.nombre}")
            else:
                existentes += 1
                print(f"Ya existe: {producto.nombre}")

    print()
    print(f"Productos creados: {creados}")
    print(f"Productos que ya existían: {existentes}")


if __name__ == "__main__":
    cargar_productos()