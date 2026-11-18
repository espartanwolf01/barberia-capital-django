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
]