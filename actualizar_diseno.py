import re
import shutil
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "principal" / "templates" / "principal"
CSS = BASE / "principal" / "static" / "principal" / "css"


ENCABEZADO = """
{% with pagina=request.resolver_match.url_name %}
<header class="capital-header">
    <a class="capital-logo" href="{% url 'inicio' %}">
        <span aria-hidden="true">💈</span>
        Peluquería Capital
    </a>

    <nav class="capital-nav" aria-label="Navegación principal">
        <a href="{% url 'inicio' %}"
           {% if pagina == 'inicio' %}aria-current="page"{% endif %}>
            Inicio
        </a>
        <a href="{% url 'servicios' %}"
           {% if pagina == 'servicios' %}aria-current="page"{% endif %}>
            Servicios
        </a>
        <a href="{% url 'citas' %}"
           {% if pagina == 'citas' %}aria-current="page"{% endif %}>
            Citas
        </a>
        <a href="{% url 'tienda' %}"
           {% if pagina == 'tienda' %}aria-current="page"{% endif %}>
            Tienda
        </a>
        <a href="{% url 'contacto' %}"
           {% if pagina == 'contacto' %}aria-current="page"{% endif %}>
            Contacto
        </a>
    </nav>

    <div class="capital-cuenta">
        {% if user.is_authenticated %}
            {% if user.is_staff %}
                <a class="capital-btn" href="{% url 'panel' %}">
                    Panel admin
                </a>
            {% endif %}

            <a class="capital-btn capital-perfil"
               href="{% url 'perfil' %}"
               aria-label="Mi perfil">
                <span class="capital-avatar" aria-hidden="true">
                    {{ user.get_username|first|upper }}
                </span>
                <span class="capital-nombre">
                    {{ user.perfil.nombre_completo|default:user.get_username }}
                </span>
            </a>

            <form action="{% url 'logout' %}" method="post">
                {% csrf_token %}
                <button class="capital-btn" type="submit">
                    Cerrar sesión
                </button>
            </form>
        {% else %}
            <a class="capital-btn" href="{% url 'login' %}">
                Iniciar sesión
            </a>
            <a class="capital-btn" href="{% url 'registro' %}">
                Crear cuenta
            </a>
        {% endif %}
    </div>
</header>
{% endwith %}
"""


ESTILOS_MENU = """
.capital-header,
.capital-header * {
    box-sizing: border-box;
}

.capital-header {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 22px;
    width: 100%;
    height: auto;
    min-height: 86px;
    margin: 0;
    padding: 20px 4%;
    background: rgba(14, 12, 10, .97);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(201, 168, 76, .23);
    color: #EDE8DF;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.4;
    text-align: left;
}

.capital-header .capital-logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    margin: 0;
    padding: 0;
    color: #C9A84C;
    font-family: 'Playfair Display', serif;
    font-size: 23px;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: 0;
    text-decoration: none;
    text-transform: none;
}

.capital-header .capital-nav {
    position: static;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: nowrap;
    gap: 26px;
    width: auto;
    margin: 0;
    padding: 6px 0;
    background: transparent;
    border: 0;
}

.capital-header .capital-nav a {
    position: relative;
    display: inline-block;
    flex-shrink: 0;
    margin: 0;
    padding: 5px 0;
    color: #ADA193;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.4;
    letter-spacing: 1.4px;
    text-decoration: none;
    text-transform: uppercase;
    white-space: nowrap;
    transition: color .2s;
}

.capital-header .capital-nav a::after {
    content: '';
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 1px;
    background: #C9A84C;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform .2s;
}

.capital-header .capital-nav a:hover,
.capital-header .capital-nav a[aria-current="page"] {
    color: #E4C97E;
}

.capital-header .capital-nav a:hover::after,
.capital-header .capital-nav a[aria-current="page"]::after {
    transform: scaleX(1);
}

.capital-header .capital-cuenta {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 10px;
    margin: 0;
    padding: 0;
}

.capital-header .capital-cuenta form {
    display: flex;
    margin: 0;
    padding: 0;
}

.capital-header .capital-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    min-height: 40px;
    margin: 0;
    padding: 9px 14px;
    border: 1px solid rgba(201, 168, 76, .45);
    border-radius: 0;
    background: transparent;
    color: #E4C97E;
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    font-weight: 500;
    line-height: 1.4;
    letter-spacing: 1px;
    text-decoration: none;
    text-transform: uppercase;
    white-space: nowrap;
    cursor: pointer;
    transition: background .2s, border-color .2s;
}

.capital-header .capital-btn:hover {
    background: rgba(201, 168, 76, .12);
    border-color: #C9A84C;
}

.capital-header .capital-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #C9A84C;
    color: #0E0C0A;
    font-size: 11px;
    font-weight: 700;
}

.capital-header .capital-nombre {
    display: block;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.capital-header a:focus-visible,
.capital-header button:focus-visible {
    outline: 2px solid #E4C97E;
    outline-offset: 4px;
}

@media (max-width: 1250px) {
    .capital-header .capital-nav {
        order: 3;
        justify-content: flex-start;
        width: 100%;
        overflow-x: auto;
    }
}

@media (max-width: 650px) {
    .capital-header {
        gap: 16px;
        padding: 17px 20px;
    }

    .capital-header .capital-logo {
        font-size: 21px;
    }

    .capital-header .capital-cuenta {
        justify-content: flex-start;
    }

    .capital-header .capital-nav {
        gap: 24px;
        padding-bottom: 8px;
    }

    .capital-header .capital-btn {
        padding: 9px 11px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .capital-header *,
    .capital-header *::after {
        transition: none;
    }
}
"""


CONTACTO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contacto | Peluquería Capital</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            color-scheme: dark;
            --gold: #C9A84C;
            --light: #E4C97E;
            --text: #EDE8DF;
            --muted: #ADA193;
            --border: rgba(201, 168, 76, .22);
        }

        body {
            min-height: 100vh;
            background: #0E0C0A;
            color: var(--text);
            font-family: 'Montserrat', sans-serif;
        }

        .contacto {
            max-width: 1240px;
            margin: auto;
            padding: 76px 28px 85px;
        }

        .contacto a {
            text-decoration: none;
        }

        .contacto .eyebrow {
            color: var(--gold);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        .contacto .intro {
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            align-items: center;
            gap: 65px;
            margin-bottom: 50px;
        }

        .contacto h1 {
            max-width: 680px;
            margin: 18px 0 22px;
            font-family: 'Playfair Display', serif;
            font-size: clamp(44px, 5.5vw, 74px);
            font-weight: 700;
            line-height: 1.08;
        }

        .contacto h1 em {
            color: var(--gold);
        }

        .contacto .intro-texto {
            max-width: 520px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.9;
        }

        .contacto .destacado {
            position: relative;
            overflow: hidden;
            padding: 36px;
            border: 1px solid var(--border);
            background:
                radial-gradient(
                    circle at top right,
                    rgba(201, 168, 76, .12),
                    transparent 65%
                ),
                #181410;
        }

        .contacto .destacado::before {
            content: '✂';
            position: absolute;
            top: 7px;
            right: 20px;
            color: rgba(201, 168, 76, .1);
            font-size: 110px;
            pointer-events: none;
        }

        .contacto .destacado h2 {
            position: relative;
            margin: 18px 0 14px;
            font-family: 'Playfair Display', serif;
            font-size: 29px;
        }

        .contacto .destacado p:not(.eyebrow) {
            position: relative;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.9;
        }

        .contacto .boton {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            min-height: 46px;
            margin-top: 23px;
            padding: 14px 20px;
            border: 1px solid var(--gold);
            background: var(--gold);
            color: #0E0C0A;
            font-family: inherit;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.5;
            cursor: pointer;
            transition: background .2s, transform .2s;
        }

        .contacto .boton:hover {
            background: var(--light);
            transform: translateY(-2px);
        }

        .contacto .tarjetas {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-bottom: 65px;
        }

        .contacto .tarjeta {
            min-width: 0;
            padding: 28px;
            border: 1px solid var(--border);
            background: #181410;
        }

        .contacto .icono {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 43px;
            height: 43px;
            margin-bottom: 22px;
            border: 1px solid var(--border);
            color: var(--gold);
            font-size: 20px;
        }

        .contacto .tarjeta h2 {
            margin-bottom: 12px;
            color: var(--text);
            font-family: 'Playfair Display', serif;
            font-size: 23px;
        }

        .contacto .tarjeta p {
            margin-bottom: 18px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
        }

        .contacto .enlace {
            color: var(--light);
            font-size: 13px;
            font-weight: 500;
            line-height: 1.7;
        }

        .contacto .enlace:hover {
            text-decoration: underline;
            text-underline-offset: 5px;
        }

        .contacto .inferior {
            display: grid;
            grid-template-columns: 1.15fr 1fr;
            gap: 55px;
            align-items: start;
        }

        .contacto .mensaje {
            padding: 34px;
            border: 1px solid var(--border);
            background: #181410;
        }

        .contacto .titulo {
            margin: 14px 0;
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            line-height: 1.2;
        }

        .contacto .ayuda {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.8;
        }

        .contacto .campo {
            display: grid;
            gap: 10px;
            margin-top: 23px;
        }

        .contacto label {
            color: var(--light);
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .contacto input,
        .contacto select,
        .contacto textarea {
            width: 100%;
            min-width: 0;
            padding: 14px;
            border: 1px solid var(--border);
            border-radius: 0;
            background: #0E0C0A;
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
        }

        .contacto textarea {
            min-height: 125px;
            resize: vertical;
        }

        .contacto input::placeholder,
        .contacto textarea::placeholder {
            color: #ADA193;
        }

        .contacto .mensaje .boton {
            width: 100%;
        }

        .contacto .nota {
            margin-top: 14px;
            color: var(--muted);
            font-size: 11px;
            line-height: 1.8;
        }

        .contacto .preguntas {
            padding-top: 12px;
        }

        .contacto details {
            border-bottom: 1px solid var(--border);
        }

        .contacto summary {
            padding: 22px 0;
            color: var(--text);
            font-size: 14px;
            font-weight: 500;
            line-height: 1.6;
            cursor: pointer;
        }

        .contacto details p {
            padding: 0 0 22px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.9;
        }

        .contacto .recordatorio {
            margin-top: 28px;
            padding-left: 18px;
            border-left: 2px solid var(--gold);
            color: var(--muted);
            font-size: 13px;
            line-height: 1.9;
        }

        .contacto-footer {
            padding: 30px 20px;
            border-top: 1px solid var(--border);
            color: var(--muted);
            text-align: center;
            font-size: 11px;
            line-height: 1.9;
            letter-spacing: 1px;
        }

        .contacto-footer strong {
            color: var(--gold);
        }

        .contacto :focus-visible {
            outline: 2px solid var(--light);
            outline-offset: 4px;
        }

        @media (max-width: 850px) {
            .contacto .intro,
            .contacto .inferior {
                grid-template-columns: 1fr;
                gap: 30px;
            }

            .contacto .tarjetas {
                grid-template-columns: 1fr;
                margin-bottom: 40px;
            }

            .contacto .tarjeta {
                padding: 25px;
            }
        }

        @media (max-width: 500px) {
            .contacto {
                padding: 45px 20px 55px;
            }

            .contacto .destacado,
            .contacto .mensaje {
                padding: 26px 22px;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .contacto .boton {
                transition: none;
            }
        }
    </style>
</head>

<body>
<header></header>

<main class="contacto">

    <section class="intro" aria-labelledby="contacto-titulo">
        <div>
            <p class="eyebrow">Contacto · Bogotá</p>

            <h1 id="contacto-titulo">
                Tu próximo estilo<br>
                empieza con un <em>hola.</em>
            </h1>

            <p class="intro-texto">
                ¿Un nuevo corte, una consulta o ayuda con tu reserva?
                Hablemos. En Peluquería Capital te ayudamos a
                encontrar lo que buscas.
            </p>
        </div>

        <aside class="destacado">
            <p class="eyebrow">Tu espacio, tu estilo</p>
            <h2>Hazle espacio a un buen corte.</h2>
            <p>
                Elige tu servicio, tu barbero y el horario
                que mejor se adapte a ti.
            </p>
            <a class="boton" href="{% url 'citas' %}">
                Reservar mi cita →
            </a>
        </aside>
    </section>

    <section class="tarjetas" aria-label="Canales de contacto">

        <article class="tarjeta">
            <span class="icono" aria-hidden="true">↗</span>
            <h2>Escríbenos</h2>
            <p>
                Consulta por servicios, productos o detalles
                de tu próxima visita.
            </p>
            <a class="enlace"
               href="https://wa.me/573246083901?text=Hola%2C%20quiero%20informaci%C3%B3n%20sobre%20Peluquer%C3%ADa%20Capital.">
                Abrir WhatsApp →
            </a>
        </article>

        <article class="tarjeta">
            <span class="icono" aria-hidden="true">☎</span>
            <h2>Hablemos</h2>
            <p>
                ¿Prefieres una llamada? Comunícate con nosotros
                para resolver tus dudas.
            </p>
            <a class="enlace" href="tel:+573246083901">
                +57 324 608 3901
            </a>
        </article>

        <article class="tarjeta">
            <span class="icono" aria-hidden="true">⌖</span>
            <h2>Nos vemos en Bogotá</h2>
            <p>
                Escríbenos para confirmar la dirección y
                las indicaciones antes de visitarnos.
            </p>
            <a class="enlace"
               href="https://wa.me/573246083901?text=Hola%2C%20%C2%BFme%20comparten%20la%20direcci%C3%B3n%20de%20la%20barber%C3%ADa%20y%20c%C3%B3mo%20llegar%3F">
                Consultar ubicación →
            </a>
        </article>

    </section>

    <section class="inferior">

        <div class="mensaje">
            <p class="eyebrow">Cuéntanos qué necesitas</p>
            <h2 class="titulo">Te leemos por WhatsApp.</h2>
            <p class="ayuda">
                Prepara tu consulta aquí y envíala directamente
                desde tu WhatsApp.
            </p>

            <form id="contacto-form"
                  action="https://wa.me/573246083901"
                  method="get">

                <div class="campo">
                    <label for="contacto-nombre">
                        Tu nombre · opcional
                    </label>
                    <input id="contacto-nombre"
                           type="text"
                           autocomplete="name"
                           maxlength="150"
                           placeholder="¿Cómo te llamas?">
                </div>

                <div class="campo">
                    <label for="contacto-asunto">
                        ¿De qué hablamos?
                    </label>
                    <select id="contacto-asunto">
                        <option>Consulta general</option>
                        <option>Servicios y precios</option>
                        <option>Ayuda con mi cita</option>
                        <option>Productos de la tienda</option>
                    </select>
                </div>

                <div class="campo">
                    <label for="contacto-mensaje">Tu mensaje</label>
                    <textarea id="contacto-mensaje"
                              name="text"
                              maxlength="1500"
                              placeholder="Cuéntanos en qué podemos ayudarte…"
                              required></textarea>
                </div>

                <button type="submit" class="boton">
                    Continuar en WhatsApp ↗
                </button>

                <p class="nota">
                    WhatsApp se abrirá con tu mensaje preparado.
                    Allí podrás revisarlo y enviarlo.
                </p>
            </form>
        </div>

        <div class="preguntas">
            <p class="eyebrow">Antes de tu visita</p>
            <h2 class="titulo">Dudas rápidas.</h2>

            <details>
                <summary>¿Cómo puedo reservar una cita?</summary>
                <p>
                    Inicia sesión y entra en
                    <a class="enlace" href="{% url 'citas' %}">Citas</a>.
                    Selecciona servicio, barbero, fecha y hora.
                    Tu reserva aparecerá en tu historial.
                </p>
            </details>

            <details>
                <summary>¿Puedo cambiar o cancelar mi reserva?</summary>
                <p>
                    Sí. Desde Mis citas puedes reprogramar,
                    cambiar el servicio o cancelar una cita
                    que todavía esté pendiente.
                </p>
            </details>

            <details>
                <summary>¿Dónde consulto los servicios y precios?</summary>
                <p>
                    Visita
                    <a class="enlace" href="{% url 'servicios' %}">
                        Servicios
                    </a>.
                    Si necesitas orientación sobre un corte o
                    tratamiento, escríbenos por WhatsApp.
                </p>
            </details>

            <details>
                <summary>¿También tienen productos de barbería?</summary>
                <p>
                    Sí. En la
                    <a class="enlace" href="{% url 'tienda' %}">Tienda</a>
                    puedes consultar productos, herramientas
                    y sus existencias disponibles.
                </p>
            </details>

            <p class="recordatorio">
                Para confirmar una reserva, consulta siempre
                el estado de la cita dentro de tu cuenta.
            </p>
        </div>

    </section>
</main>

<footer class="contacto-footer">
    <strong>PELUQUERÍA CAPITAL</strong>
    · BOGOTÁ, COLOMBIA · © {% now "Y" %}
</footer>

<script>
    document.getElementById("contacto-form").addEventListener(
        "submit",
        function (evento) {
            evento.preventDefault();

            const nombre = document.getElementById(
                "contacto-nombre"
            ).value.trim();

            const asunto = document.getElementById(
                "contacto-asunto"
            ).value;

            const campo = document.getElementById(
                "contacto-mensaje"
            );

            const mensaje = campo.value.trim();

            if (!mensaje) {
                campo.setCustomValidity("Escribe tu consulta.");
                campo.reportValidity();
                return;
            }

            campo.setCustomValidity("");

            const saludo = nombre
                ? "Hola, soy " + nombre + "."
                : "Hola, Peluquería Capital.";

            const texto =
                saludo + "\\n\\n" +
                "Asunto: " + asunto + "\\n\\n" +
                mensaje;

            window.location.assign(
                "https://wa.me/573246083901?text=" +
                encodeURIComponent(texto)
            );
        }
    );

    document.getElementById("contacto-mensaje").addEventListener(
        "input",
        function () {
            this.setCustomValidity("");
        }
    );
</script>

</body>
</html>
"""


RECURSOS = """
<!-- CAPITAL: RECURSOS COMPARTIDOS -->
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap">
<link rel="stylesheet"
      href="{% static 'principal/css/navegacion.css' %}?v=1">
"""


def preparar_html(contenido, nombre):
    inclusion = "{% include 'principal/includes/encabezado.html' %}"

    if inclusion not in contenido:
        patron = r"<header\\b[^>]*>.*?</header\\s*>"
        # Una sola cabecera por página.
        patron = patron.replace("\\\\", "\\")

        cabeceras = list(
            re.finditer(patron, contenido, flags=re.I | re.S)
        )

        if len(cabeceras) != 1:
            raise ValueError(
                f"{nombre}: esperaba un encabezado y encontré "
                f"{len(cabeceras)}. No se cambió ningún archivo."
            )

        cabecera = cabeceras[0]
        contenido = (
            contenido[:cabecera.start()]
            + inclusion
            + contenido[cabecera.end():]
        )

    if "{% load static %}" not in contenido:
        contenido = "{% load static %}\n" + contenido

    if "<!-- CAPITAL: RECURSOS COMPARTIDOS -->" not in contenido:
        cierre = re.search(r"</head\s*>", contenido, flags=re.I)

        if cierre is None:
            raise ValueError(f"{nombre}: falta </head>.")

        contenido = (
            contenido[:cierre.start()]
            + RECURSOS
            + "\n"
            + contenido[cierre.start():]
        )

    return contenido


def ejecutar():
    if not (BASE / "manage.py").is_file():
        raise ValueError(
            "Guarda este script junto a manage.py."
        )

    archivos = [
        "inicio.html",
        "servicios.html",
        "citas.html",
        "tienda.html",
        "contacto.html",
        "perfil.html",
    ]

    cambios = {}

    # Primero revisa y prepara todos los HTML.
    for nombre in archivos:
        ruta = TEMPLATES / nombre

        if not ruta.is_file():
            raise FileNotFoundError(
                f"No encuentro {ruta}. No se cambió ningún archivo."
            )

        contenido = (
            CONTACTO
            if nombre == "contacto.html"
            else ruta.read_text(encoding="utf-8-sig")
        )

        cambios[ruta] = preparar_html(contenido, nombre)

    cambios[TEMPLATES / "includes" / "encabezado.html"] = (
        ENCABEZADO.strip() + "\n"
    )
    cambios[CSS / "navegacion.css"] = (
        ESTILOS_MENU.strip() + "\n"
    )

    # Respaldo al lado de la carpeta del proyecto.
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    respaldo = BASE.parent / f"{BASE.name}_respaldo_{fecha}"

    for ruta in cambios:
        if ruta.exists():
            copia = respaldo / ruta.relative_to(BASE)
            copia.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ruta, copia)

    for ruta, contenido in cambios.items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")
        print(f"Actualizado: {ruta.relative_to(BASE)}")

    print(f"\nRespaldo guardado en:\n{respaldo}")
    print("\nListo. Actualiza el navegador con Ctrl + F5.")


if __name__ == "__main__":
    try:
        ejecutar()
    except (OSError, ValueError) as error:
        print(f"\nNo se pudo completar: {error}")