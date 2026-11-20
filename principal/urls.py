from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("servicios", views.servicios, name="servicios"),
    path("contacto", views.contacto, name="contacto"),
    path("registro", views.registro, name="registro"),
    path("login", views.iniciar_sesion, name="login"),
    path("logout", views.cerrar_sesion, name="logout"),
    path("perfil", views.perfil, name="perfil"),
    path("citas", views.citas, name="citas"),
    path(
        "citas/<int:cita_id>/cancelar",
        views.cancelar_cita,
        name="cancelar_cita",
    ),
    path(
        "citas/<int:cita_id>/reprogramar",
        views.reprogramar_cita,
        name="reprogramar_cita",
    ),
    path("panel", views.panel, name="panel"),
    path(
        "panel/citas/<int:cita_id>/estado",
        views.cambiar_estado_cita,
        name="cambiar_estado_cita",
    ),
]