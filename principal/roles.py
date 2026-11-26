from .models import Barbero


def rol_usuario(usuario):
    if not usuario.is_authenticated:
        return "invitado"
    if usuario.is_staff:
        return "administrador"
    if Barbero.objects.filter(usuario_id=usuario.pk).exists():
        return "barbero"
    return "cliente"


def destino_usuario(usuario):
    return {
        "administrador": "panel",
        "barbero": "panel_barbero",
        "cliente": "panel_cliente",
    }.get(rol_usuario(usuario), "login")
