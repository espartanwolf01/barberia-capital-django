from django.urls import path

from . import carrito, reportes, views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("servicios", views.servicios, name="servicios"),
    path("contacto", views.contacto, name="contacto"),
    path("registro", views.registro, name="registro"),
    path("login", views.iniciar_sesion, name="login"),
    path("logout", views.cerrar_sesion, name="logout"),
    path("perfil", views.perfil, name="perfil"),
    path("tienda", views.tienda, name="tienda"),
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
    path(
        "panel/productos/<int:producto_id>/reponer",
        views.reponer_stock,
        name="reponer_stock",
    ),

    path("carrito", carrito.ver_carrito, name="carrito"),
    path(
        "carrito/<int:producto_id>/agregar",
        carrito.agregar_carrito,
        name="agregar_carrito",
    ),
    path(
        "carrito/<int:producto_id>/actualizar",
        carrito.actualizar_carrito,
        name="actualizar_carrito",
    ),
    path(
        "carrito/<int:producto_id>/eliminar",
        carrito.eliminar_carrito,
        name="eliminar_carrito",
    ),
    path(
        "carrito/finalizar",
        carrito.finalizar_pedido,
        name="finalizar_pedido",
    ),
    path(
        "pedidos/<int:pedido_id>/confirmacion",
        carrito.compra_exitosa,
        name="compra_exitosa",
    ),

    path(
        "reportes",
        reportes.ver_reportes,
        name="reportes",
    ),
    path(
        "reportes/exportar",
        reportes.exportar_reportes,
        name="exportar_reportes",
    ),
    path(
        "reportes/general",
        reportes.exportar_general,
        name="exportar_general",
    ),
]

from . import roles_views

urlpatterns += [
    path("mi-acceso", roles_views.mi_acceso, name="mi_acceso"),
    path("mi-cuenta", roles_views.panel_cliente, name="panel_cliente"),
    path("barbero", roles_views.panel_barbero, name="panel_barbero"),
    path("barbero/citas/<int:cita_id>/estado", roles_views.estado_barbero, name="estado_barbero"),
    path("panel/cuentas", roles_views.gestionar_cuentas, name="gestionar_cuentas"),
    path("panel/cuentas/<int:usuario_id>/estado", roles_views.activar_cuenta, name="activar_cuenta"),
]
