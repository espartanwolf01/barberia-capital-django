import re
import shutil
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent
PANEL = (
    BASE
    / "principal"
    / "templates"
    / "principal"
    / "panel.html"
)


ENCABEZADO = """
<header class="panel-cabecera">
    <div class="panel-marca">
        <a href="{% url 'inicio' %}" class="panel-logo">
            💈 Peluquería Capital
        </a>
        <p class="panel-etiqueta">Panel administrativo</p>
    </div>

    <nav class="panel-enlaces" aria-label="Herramientas administrativas">
        <a href="{% url 'reportes' %}" class="panel-boton">
            Reportes
        </a>
        <a href="{% url 'admin:index' %}" class="panel-boton">
            Gestión de datos
        </a>
        <a href="{% url 'inicio' %}" class="panel-boton">
            Ver sitio ↗
        </a>
    </nav>

    <div class="panel-cuenta">
        <a href="{% url 'perfil' %}"
           class="panel-boton panel-perfil"
           aria-label="Ir a mi perfil">
            <span class="panel-avatar" aria-hidden="true">
                {{ user.get_username|first|upper }}
            </span>
            <span class="panel-identidad">
                <span class="panel-nombre">
                    {{ user.perfil.nombre_completo|default:user.get_username }}
                </span>
                <span class="panel-perfil-texto">Mi perfil →</span>
            </span>
        </a>

        <form action="{% url 'logout' %}" method="post">
            {% csrf_token %}
            <button type="submit" class="panel-boton">
                Cerrar sesión
            </button>
        </form>
    </div>
</header>
"""


ESTILOS = """
<style id="panel-cabecera-estilos">
    .panel-cabecera,
    .panel-cabecera * {
        box-sizing: border-box;
    }

    header.panel-cabecera {
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: 28px;
        width: 100%;
        height: auto;
        margin: 0;
        padding: 22px 4%;
        background: #0E0C0A;
        border-bottom: 1px solid rgba(201, 168, 76, .25);
        color: #EDE8DF;
        font-family: 'Montserrat', sans-serif;
        line-height: 1.4;
    }

    .panel-cabecera .panel-logo {
        display: inline-block;
        color: #E4C97E;
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        line-height: 1.2;
        text-decoration: none;
    }

    .panel-cabecera .panel-etiqueta {
        margin: 7px 0 0;
        color: #ADA193;
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .panel-cabecera .panel-enlaces {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        width: auto;
        margin: 0;
        padding: 0;
    }

    .panel-cabecera .panel-cuenta {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: 12px;
        min-width: 0;
    }

    .panel-cabecera .panel-cuenta form {
        display: flex;
        margin: 0;
        padding: 0;
    }

    .panel-cabecera .panel-boton {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 11px;
        min-height: 46px;
        margin: 0;
        padding: 11px 15px;
        border: 1px solid rgba(201, 168, 76, .4);
        border-radius: 5px;
        background: transparent;
        color: #E4C97E;
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 500;
        line-height: 1.4;
        letter-spacing: .5px;
        text-decoration: none;
        white-space: nowrap;
        cursor: pointer;
        transition: background .2s, border-color .2s;
    }

    .panel-cabecera .panel-boton:hover {
        border-color: #C9A84C;
        background: rgba(201, 168, 76, .1);
    }

    .panel-cabecera .panel-perfil {
        justify-content: flex-start;
        padding: 9px 14px;
    }

    .panel-cabecera .panel-avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #C9A84C;
        color: #0E0C0A;
        font-size: 13px;
        font-weight: 700;
    }

    .panel-cabecera .panel-identidad {
        display: grid;
        gap: 3px;
        min-width: 0;
        text-align: left;
    }

    .panel-cabecera .panel-nombre {
        display: block;
        max-width: 210px;
        overflow: hidden;
        color: #EDE8DF;
        font-size: 12px;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .panel-cabecera .panel-perfil-texto {
        color: #C9A84C;
        font-size: 10px;
    }

    .panel-cabecera a:focus-visible,
    .panel-cabecera button:focus-visible {
        outline: 2px solid #E4C97E;
        outline-offset: 4px;
    }

    @media (max-width: 1350px) {
        header.panel-cabecera {
            grid-template-columns: 1fr auto;
            gap: 20px;
        }

        .panel-cabecera .panel-enlaces {
            grid-column: 1 / -1;
            grid-row: 2;
            justify-content: flex-start;
            padding-top: 18px;
            border-top: 1px solid rgba(201, 168, 76, .15);
        }
    }

    @media (max-width: 700px) {
        header.panel-cabecera {
            grid-template-columns: 1fr;
            padding: 22px 5%;
        }

        .panel-cabecera .panel-cuenta {
            justify-content: flex-start;
        }

        .panel-cabecera .panel-enlaces {
            grid-column: 1;
            grid-row: auto;
            justify-content: flex-start;
        }

        .panel-cabecera .panel-logo {
            font-size: 22px;
        }

        .panel-cabecera .panel-nombre {
            max-width: 170px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .panel-cabecera .panel-boton {
            transition: none;
        }
    }
</style>
"""


def ejecutar():
    if not PANEL.is_file():
        raise FileNotFoundError(
            "No encuentro principal/templates/principal/panel.html. "
            "Guarda el script junto a manage.py."
        )

    contenido = PANEL.read_text(encoding="utf-8-sig")

    cabeceras = list(
        re.finditer(
            r"<header\b[^>]*>.*?</header\s*>",
            contenido,
            flags=re.I | re.S,
        )
    )

    if len(cabeceras) != 1:
        raise ValueError(
            "No pude identificar un único encabezado. "
            "No se modificó el archivo."
        )

    cabecera = cabeceras[0]

    nuevo = (
        contenido[:cabecera.start()]
        + ENCABEZADO.strip()
        + contenido[cabecera.end():]
    )

    # Permite ejecutar el script otra vez sin duplicar los estilos.
    nuevo = re.sub(
        r'<style id="panel-cabecera-estilos">.*?</style>',
        "",
        nuevo,
        flags=re.S,
    )

    cierre = re.search(r"</head\s*>", nuevo, flags=re.I)

    if cierre is None:
        raise ValueError(
            "No encuentro </head>. No se modificó el archivo."
        )

    nuevo = (
        nuevo[:cierre.start()]
        + ESTILOS
        + "\n"
        + nuevo[cierre.start():]
    )

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    respaldo = (
        BASE.parent
        / f"{BASE.name}_respaldo_panel_{fecha}"
        / "panel.html"
    )

    respaldo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PANEL, respaldo)

    PANEL.write_text(nuevo, encoding="utf-8")

    print("Panel actualizado.")
    print("Tu nombre ahora lleva a Mi perfil.")
    print(f"Respaldo: {respaldo}")
    print("Actualiza el navegador con Ctrl + F5.")


if __name__ == "__main__":
    try:
        ejecutar()
    except (OSError, ValueError) as error:
        print(f"No se pudo completar: {error}")