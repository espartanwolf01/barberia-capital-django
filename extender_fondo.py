import re
import shutil
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "principal" / "templates" / "principal"

CSS = (
    BASE / "principal" / "static"
    / "principal" / "css" / "fondo_animado.css"
)

FONDO = TEMPLATES / "includes" / "fondo_animado.html"

INCLUSION = (
    "{% include 'principal/includes/fondo_animado.html' %}"
)

ENLACE = """
<link rel="stylesheet"
      href="{% static 'principal/css/fondo_animado.css' %}?v=3">
"""


def preparar(ruta):
    original = ruta.read_text(encoding="utf-8-sig")
    contenido = original

    # Solo modifica páginas completas, no fragmentos.
    if not re.search(r"<head\b", contenido, re.I):
        return None

    if not re.search(r"<body\b", contenido, re.I):
        return None

    if "{% load static %}" not in contenido:
        contenido = "{% load static %}\n" + contenido

    if "principal/css/fondo_animado.css" not in contenido:
        cierre = re.search(r"</head\s*>", contenido, re.I)

        if cierre is None:
            raise ValueError(
                f"{ruta.name}: no encuentro </head>."
            )

        contenido = (
            contenido[:cierre.start()]
            + ENLACE
            + contenido[cierre.start():]
        )

    if INCLUSION not in contenido:
        apertura = re.search(r"<body\b[^>]*>", contenido, re.I)

        contenido = (
            contenido[:apertura.end()]
            + "\n"
            + INCLUSION
            + "\n"
            + contenido[apertura.end():]
        )

    if contenido == original:
        return None

    return contenido


def ejecutar():
    if not (BASE / "manage.py").is_file():
        raise ValueError(
            "Guarda extender_fondo.py junto a manage.py."
        )

    if not CSS.is_file() or not FONDO.is_file():
        raise FileNotFoundError(
            "Faltan los archivos del fondo del inicio."
        )

    cambios = {}

    # Revisa las páginas de principal.
    # La carpeta includes queda fuera.
    for ruta in sorted(TEMPLATES.glob("*.html")):
        contenido = preparar(ruta)

        if contenido is not None:
            cambios[ruta] = contenido

    if not cambios:
        print("Todas las páginas ya tienen el fondo.")
        return

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    respaldo = (
        BASE.parent
        / f"{BASE.name}_respaldo_fondos_{fecha}"
    )

    # Respalda todas las páginas antes de modificarlas.
    for ruta in cambios:
        copia = respaldo / ruta.relative_to(BASE)
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ruta, copia)

    for ruta, contenido in cambios.items():
        ruta.write_text(contenido, encoding="utf-8")
        print(f"Fondo agregado: {ruta.name}")

    print(f"\nRespaldo: {respaldo}")
    print("\nListo. Actualiza las páginas con Ctrl + F5.")


if __name__ == "__main__":
    try:
        ejecutar()
    except (OSError, ValueError) as error:
        print(f"No se pudo completar: {error}")