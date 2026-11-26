from datetime import datetime
from pathlib import Path
import shutil


BASE = Path(__file__).resolve().parent
INICIO = (
    BASE / "principal" / "templates"
    / "principal" / "inicio.html"
)

CAMBIOS = {
    "Carlos Mendoza": "Carlos Rodríguez",
    "Andrés Rivera": "Andrés Martínez",
    "Santiago Torres": "Juan Pérez",
    "Director &amp; Barbero Senior": "Barbero · Cortes clásicos y fade",
    "Director & Barbero Senior": "Barbero · Cortes clásicos y fade",
    "Barbero &amp; Especialista en Color": "Barbero · Barba y afeitado",
    "Barbero & Especialista en Color": "Barbero · Barba y afeitado",
    "Barbero &amp; Especialista en Barba": "Barbero · Cortes modernos",
    "Barbero & Especialista en Barba": "Barbero · Cortes modernos",
}


def ejecutar():
    original = INICIO.read_text(encoding="utf-8-sig")
    nuevo = original

    for anterior, actualizado in CAMBIOS.items():
        nuevo = nuevo.replace(anterior, actualizado)

    # Actualiza las descripciones de las especialidades.
    import re

    biografias = [
        (
            r"Experto en técnicas de coloración y\s*"
            r"degradados\. Amante del detalle y la\s*"
            r"precisión en cada trabajo\.",
            "Especialista en barba y afeitado. "
            "Cuida cada detalle para conseguir un acabado "
            "limpio y definido.",
        ),
        (
            r"Maestro del afeitado clásico con navaja\s*"
            r"y el arte del perfilado\. Cada barba,\s*"
            r"una obra de arte\.",
            "Especialista en cortes modernos. "
            "Textura, estilo y atención al detalle "
            "para renovar tu imagen.",
        ),
    ]

    for patron, texto in biografias:
        nuevo = re.sub(patron, lambda coincidencia: texto, nuevo)

    if nuevo == original:
        print("No encontré cambios pendientes en el inicio.")
        return

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    respaldo = (
        BASE.parent
        / f"{BASE.name}_respaldo_equipo_{fecha}"
        / "inicio.html"
    )

    respaldo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(INICIO, respaldo)

    INICIO.write_text(nuevo, encoding="utf-8")

    print("Nombres y especialidades actualizados.")
    print("Las fotos se conservaron.")
    print(f"Respaldo: {respaldo}")
    print("Actualiza el inicio con Ctrl + F5.")


if __name__ == "__main__":
    try:
        ejecutar()
    except OSError as error:
        print(f"No se pudo completar: {error}")