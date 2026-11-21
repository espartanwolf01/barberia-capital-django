import os
import unicodedata
from pathlib import Path

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "barberia_capital.settings",
)

import django

django.setup()

from django.conf import settings
from django.core.files import File
from principal.models import Producto


CARPETA = (
    Path(settings.BASE_DIR)
    / "principal"
    / "static"
    / "principal"
    / "img"
    / "productos"
)

# Palabras para identificar cada producto y su fotografía.
PRODUCTOS = [
    ("Wahl Magic Clip", ("wahl", "magic")),
    ("Oster Fast Feed", ("oster", "fast")),
    ("Pomada Layrite Natural", ("layrite",)),
    ("Aceite para barba", ("aceite", "barba")),
    ("Navaja Dovo Solingen", ("dovo",)),
    ("Peines de carbono", ("peine", "carbon")),
]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )
    return texto.casefold()


def coincide(texto, palabras):
    texto = normalizar(texto)
    return all(palabra in texto for palabra in palabras)


def ejecutar():
    if not CARPETA.is_dir():
        print(f"No existe la carpeta:\n{CARPETA}")
        return

    archivos = [
        archivo
        for archivo in CARPETA.iterdir()
        if archivo.is_file()
        and archivo.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".webp", ".avif"
        }
    ]

    productos_bd = list(Producto.objects.all())
    pendientes = []
    errores = []

    # Comprueba las seis coincidencias antes de guardar.
    for etiqueta, palabras in PRODUCTOS:
        productos = [
            producto
            for producto in productos_bd
            if coincide(producto.nombre, palabras)
        ]

        fotos = [
            archivo
            for archivo in archivos
            if coincide(archivo.name, palabras)
        ]

        if len(productos) != 1:
            errores.append(
                f"{etiqueta}: encontré {len(productos)} productos; "
                "debe existir exactamente uno."
            )

        if len(fotos) != 1:
            errores.append(
                f"{etiqueta}: encontré {len(fotos)} fotos; "
                "debe existir exactamente una."
            )

        if len(productos) == 1 and len(fotos) == 1:
            pendientes.append((productos[0], fotos[0]))

    if errores:
        print("\nNo se modificó ningún producto.\n")
        for error in errores:
            print(f"- {error}")
        return

    # Comprueba que Pillow pueda leer todas las imágenes.
    from PIL import Image

    for producto, foto in pendientes:
        try:
            with Image.open(foto) as imagen:
                imagen.verify()
        except Exception as error:
            print(f"No se puede leer {foto.name}: {error}")
            print("No se modificó ningún producto.")
            return

    for producto, foto in pendientes:
        # Evita crear otra copia si ya tiene la misma imagen.
        if producto.imagen:
            almacenamiento = producto.imagen.storage

            if almacenamiento.exists(producto.imagen.name):
                with almacenamiento.open(
                    producto.imagen.name, "rb"
                ) as actual:
                    if actual.read() == foto.read_bytes():
                        print(f"Ya estaba lista: {producto.nombre}")
                        continue

        # ImageField guarda la copia en media/productos/.
        with foto.open("rb") as archivo:
            producto.imagen.save(
                f"producto-{producto.pk}{foto.suffix.lower()}",
                File(archivo),
                save=False,
            )

        producto.save(update_fields=["imagen"])
        print(f"Foto asignada: {producto.nombre}")

    print("\n¡Listo! Actualiza la tienda con Ctrl + F5.")


if __name__ == "__main__":
    ejecutar()