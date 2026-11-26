import re
import shutil
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent

INICIO = (
    BASE / "principal" / "templates"
    / "principal" / "inicio.html"
)

CSS = (
    BASE / "principal" / "static"
    / "principal" / "css" / "fondo_animado.css"
)

INCLUSION = (
    BASE / "principal" / "templates"
    / "principal" / "includes" / "fondo_animado.html"
)


ESTILOS = """
body {
    isolation: isolate;
}

.capital-fondo {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
    user-select: none;
    background: #0E0C0A;
}

.capital-fondo-plano {
    position: absolute;
    top: 50%;
    left: 50%;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    width: 220vmax;
    height: 220vmax;
    transform: translate(-50%, -50%) rotate(-28deg);
}

.capital-fondo-fila {
    display: flex;
    flex-shrink: 0;
    width: 100%;
    overflow: hidden;
}

.capital-fondo-pista {
    display: flex;
    width: max-content;
    animation: capital-deslizar 100s linear infinite;
    will-change: transform;
}

.capital-fondo-fila:nth-child(even) .capital-fondo-pista {
    animation-direction: reverse;
    animation-duration: 120s;
}

.capital-fondo-grupo {
    display: flex;
    align-items: center;
    justify-content: space-around;
    flex-shrink: 0;
    gap: 70px;
    min-width: 220vmax;
    padding-right: 70px;
}

.capital-fondo-frase {
    display: inline-flex;
    align-items: center;
    gap: 18px;
    flex-shrink: 0;
    white-space: nowrap;
    color: rgba(201, 168, 76, .11);
    font-family: 'Montserrat', sans-serif;
    font-size: clamp(24px, 2.8vw, 44px);
    font-weight: 700;
    line-height: 1.4;
    letter-spacing: 5px;
}

.capital-fondo-emoji {
    opacity: .18;
    font-size: 1.15em;
    letter-spacing: 0;
}

.capital-fondo::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
        ellipse at center,
        rgba(14, 12, 10, .15),
        rgba(14, 12, 10, .6)
    );
}

@keyframes capital-deslizar {
    from {
        transform: translateX(0);
    }
    to {
        transform: translateX(-50%);
    }
}

/* El título conserva contraste sobre las letras del fondo. */
.hero h1,
.hero-sub,
.hero-eyebrow {
    text-shadow: 0 2px 18px rgba(0, 0, 0, .85);
}

@media (max-width: 650px) {
    .capital-fondo-frase {
        font-size: 25px;
        letter-spacing: 3px;
    }

    .capital-fondo-grupo {
        gap: 45px;
        padding-right: 45px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .capital-fondo-pista {
        animation: none;
        will-change: auto;
    }
}
"""


def construir_fondo():
    frase = """
        <span class="capital-fondo-frase">
            <span class="capital-fondo-emoji">💈</span>
            BARBERÍA CAPITAL
        </span>
    """

    grupo = (
        '<div class="capital-fondo-grupo">'
        + frase * 6
        + "</div>"
    )

    fila = (
        '<div class="capital-fondo-fila">'
        '<div class="capital-fondo-pista">'
        + grupo * 2
        + "</div></div>"
    )

    return (
        '<div class="capital-fondo" aria-hidden="true">'
        '<div class="capital-fondo-plano">'
        + fila * 18
        + "</div></div>"
    )


def ejecutar():
    if not INICIO.is_file():
        raise FileNotFoundError(
            "No encuentro inicio.html. "
            "Guarda el script junto a manage.py."
        )

    contenido = INICIO.read_text(encoding="utf-8-sig")

    if "{% load static %}" not in contenido:
        contenido = "{% load static %}\n" + contenido

    if "principal/css/fondo_animado.css" not in contenido:
        cierre = re.search(r"</head\s*>", contenido, re.I)

        if cierre is None:
            raise ValueError(
                "No encuentro </head>. No se cambió ningún archivo."
            )

        enlace = """
<link rel="stylesheet"
      href="{% static 'principal/css/fondo_animado.css' %}?v=1">
"""

        contenido = (
            contenido[:cierre.start()]
            + enlace
            + contenido[cierre.start():]
        )

    incluir = (
        "{% include 'principal/includes/fondo_animado.html' %}"
    )

    if incluir not in contenido:
        apertura = re.search(r"<body\b[^>]*>", contenido, re.I)

        if apertura is None:
            raise ValueError(
                "No encuentro <body>. No se cambió ningún archivo."
            )

        contenido = (
            contenido[:apertura.end()]
            + "\n"
            + incluir
            + "\n"
            + contenido[apertura.end():]
        )

    cambios = {
        INICIO: contenido,
        CSS: ESTILOS.strip() + "\n",
        INCLUSION: construir_fondo() + "\n",
    }

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    respaldo = (
        BASE.parent
        / f"{BASE.name}_respaldo_fondo_{fecha}"
    )

    for ruta in cambios:
        if ruta.exists():
            copia = respaldo / ruta.relative_to(BASE)
            copia.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ruta, copia)

    for ruta, texto in cambios.items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        print(f"Actualizado: {ruta.relative_to(BASE)}")

    print(f"\nRespaldo: {respaldo}")
    print("Fondo listo. Actualiza el inicio con Ctrl + F5.")


if __name__ == "__main__":
    try:
        ejecutar()
    except (OSError, ValueError) as error:
        print(f"No se pudo completar: {error}")