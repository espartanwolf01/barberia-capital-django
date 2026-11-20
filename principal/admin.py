from django.contrib import admin

from .models import Barbero, Cita, Perfil, Producto, Servicio


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "usuario", "telefono")
    search_fields = (
        "nombre_completo",
        "usuario__email",
        "telefono",
    )


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre",)


@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especialidad", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "especialidad")


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "servicio",
        "barbero",
        "fecha",
        "hora",
        "estado",
    )
    list_filter = ("estado", "barbero", "fecha")
    search_fields = (
        "cliente__email",
        "cliente__perfil__nombre_completo",
        "servicio__nombre",
    )
    list_select_related = ("cliente", "servicio", "barbero")
    readonly_fields = ("fecha_asignacion",)
    date_hierarchy = "fecha"


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "precio",
        "stock",
        "activo",
    )
    list_filter = ("categoria", "activo")
    search_fields = ("nombre", "descripcion")