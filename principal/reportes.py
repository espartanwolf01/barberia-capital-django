from datetime import datetime
from io import BytesIO

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .models import (
    Barbero,
    Cita,
    DetallePedido,
    Pedido,
    Producto,
    Servicio,
)

Usuario = get_user_model()


class FiltrosReporteForm(forms.Form):
    desde = forms.DateField(
        label="Desde",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date"},
        ),
    )

    hasta = forms.DateField(
        label="Hasta",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date"},
        ),
    )

    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=[
            ("", "Todos los estados"),
            *Cita.Estado.choices,
        ],
    )

    barbero = forms.ModelChoiceField(
        label="Barbero",
        required=False,
        queryset=Barbero.objects.all(),
        empty_label="Todos los barberos",
    )

    servicio = forms.ModelChoiceField(
        label="Servicio",
        required=False,
        queryset=Servicio.objects.all(),
        empty_label="Todos los servicios",
    )

    def clean(self):
        datos = super().clean()

        desde = datos.get("desde")
        hasta = datos.get("hasta")

        if desde and hasta and desde > hasta:
            raise forms.ValidationError(
                "La fecha Desde no puede ser posterior a Hasta."
            )

        return datos


def nombre_usuario(usuario):
    perfil = getattr(usuario, "perfil", None)

    if perfil and perfil.nombre_completo:
        return perfil.nombre_completo

    return usuario.get_username()


def consultar_citas(parametros):
    formulario = FiltrosReporteForm(parametros)

    citas = Cita.objects.select_related(
        "cliente",
        "cliente__perfil",
        "servicio",
        "barbero",
    ).order_by("-fecha", "-hora", "-pk")

    if not formulario.is_valid():
        return formulario, citas.none()

    filtros = formulario.cleaned_data

    if filtros["desde"]:
        citas = citas.filter(fecha__gte=filtros["desde"])

    if filtros["hasta"]:
        citas = citas.filter(fecha__lte=filtros["hasta"])

    if filtros["estado"]:
        citas = citas.filter(estado=filtros["estado"])

    if filtros["barbero"]:
        citas = citas.filter(barbero=filtros["barbero"])

    if filtros["servicio"]:
        citas = citas.filter(servicio=filtros["servicio"])

    return formulario, citas


def filas_citas(citas):
    for cita in citas.iterator(chunk_size=500):
        yield [
            cita.pk,
            nombre_usuario(cita.cliente),
            cita.servicio.nombre,
            cita.barbero.nombre,
            cita.fecha,
            cita.hora,
            cita.get_estado_display(),
            cita.notas or "",
        ]


def agregar_hoja(libro, nombre, encabezados, filas):
    hoja = libro.create_sheet(title=nombre)
    hoja.append(encabezados)

    for fila in filas:
        valores = []

        for valor in fila:
            if isinstance(valor, datetime) and timezone.is_aware(valor):
                valor = timezone.localtime(valor).replace(tzinfo=None)

            valores.append(valor)

        hoja.append(valores)

        for celda in hoja[hoja.max_row]:
            if isinstance(celda.value, str):
                # Impide interpretar nombres o notas como fórmulas.
                celda.data_type = "s"

            celda.alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )

    for celda in hoja[1]:
        celda.font = Font(bold=True, color="0E0C0A")
        celda.fill = PatternFill(
            fill_type="solid",
            fgColor="C9A84C",
        )

    for indice, encabezado in enumerate(encabezados, start=1):
        columna = get_column_letter(indice)
        hoja.column_dimensions[columna].width = (
            45 if encabezado in ("Notas", "Descripción") else 24
        )

    hoja.row_dimensions[1].height = 28
    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions

    return hoja


def respuesta_excel(libro, nombre):
    archivo = BytesIO()
    libro.save(archivo)
    libro.close()

    respuesta = HttpResponse(
        archivo.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    respuesta["Content-Disposition"] = (
        f'attachment; filename="{nombre}"'
    )
    respuesta["Cache-Control"] = "no-store"

    return respuesta


@staff_member_required(login_url="admin:login")
@require_GET
def ver_reportes(request):
    formulario, citas = consultar_citas(request.GET)

    resumen_citas = citas.aggregate(
        cantidad=Count("pk"),
        pendientes=Count(
            "pk",
            filter=Q(estado=Cita.Estado.PENDIENTE),
        ),
        atendidas=Count(
            "pk",
            filter=Q(estado=Cita.Estado.ATENDIDA),
        ),
        canceladas=Count(
            "pk",
            filter=Q(estado=Cita.Estado.CANCELADA),
        ),
    )

    resumen_usuarios = Usuario.objects.aggregate(
        cantidad=Count("pk"),
        activos=Count(
            "pk",
            filter=Q(is_active=True),
        ),
    )

    resumen_productos = Producto.objects.aggregate(
        cantidad=Count("pk"),
        agotados=Count(
            "pk",
            filter=Q(activo=True, stock=0),
        ),
        stock_bajo=Count(
            "pk",
            filter=Q(
                activo=True,
                stock__gt=0,
                stock__lte=3,
            ),
        ),
    )

    respuesta = render(
        request,
        "principal/reportes.html",
        {
            "formulario": formulario,
            "citas": citas,
            "resumen_citas": resumen_citas,
            "resumen_usuarios": resumen_usuarios,
            "resumen_productos": resumen_productos,
            "filtros_query": request.GET.urlencode(),
            "generado": timezone.now(),
        },
    )

    respuesta["Cache-Control"] = "no-store"

    return respuesta


@staff_member_required(login_url="admin:login")
@require_GET
def exportar_reportes(request):
    formulario, citas = consultar_citas(request.GET)

    if not formulario.is_valid():
        return HttpResponse(
            "Los filtros no son válidos. "
            "Vuelve a Reportes y corrígelos.",
            status=400,
            content_type="text/plain; charset=utf-8",
        )

    libro = Workbook()
    libro.remove(libro.active)

    agregar_hoja(
        libro,
        "Citas",
        [
            "ID",
            "Cliente",
            "Servicio",
            "Barbero",
            "Fecha",
            "Hora",
            "Estado",
            "Notas",
        ],
        filas_citas(citas),
    )

    return respuesta_excel(libro, "reporte_citas.xlsx")


@staff_member_required(login_url="admin:login")
@require_GET
def exportar_general(request):
    libro = Workbook()
    libro.remove(libro.active)

    citas = Cita.objects.select_related(
        "cliente",
        "cliente__perfil",
        "servicio",
        "barbero",
    ).order_by("-fecha", "-hora", "-pk")

    agregar_hoja(
        libro,
        "Citas",
        [
            "ID",
            "Cliente",
            "Servicio",
            "Barbero",
            "Fecha",
            "Hora",
            "Estado",
            "Notas",
        ],
        filas_citas(citas),
    )

    pedidos = Pedido.objects.select_related(
        "cliente",
        "cliente__perfil",
    ).order_by("-fecha", "-pk")

    agregar_hoja(
        libro,
        "Pedidos",
        [
            "ID",
            "Cliente",
            "Fecha",
            "Total registrado",
            "Estado",
        ],
        (
            [
                pedido.pk,
                nombre_usuario(pedido.cliente),
                pedido.fecha,
                pedido.total,
                pedido.get_estado_display(),
            ]
            for pedido in pedidos.iterator(chunk_size=500)
        ),
    )

    detalles = DetallePedido.objects.order_by("pedido_id", "pk")

    agregar_hoja(
        libro,
        "Detalles de pedidos",
        [
            "Pedido ID",
            "Producto ID",
            "Nombre al comprar",
            "Cantidad",
            "Precio unitario",
            "Subtotal",
        ],
        (
            [
                detalle.pedido_id,
                detalle.producto_id,
                detalle.nombre_producto,
                detalle.cantidad,
                detalle.precio_unitario,
                detalle.subtotal,
            ]
            for detalle in detalles.iterator(chunk_size=500)
        ),
    )

    productos = Producto.objects.order_by("pk")

    agregar_hoja(
        libro,
        "Productos",
        [
            "ID",
            "Nombre",
            "Categoría",
            "Descripción",
            "Precio actual",
            "Stock actual",
            "Activo",
        ],
        (
            [
                producto.pk,
                producto.nombre,
                producto.get_categoria_display(),
                producto.descripcion,
                producto.precio,
                producto.stock,
                "Sí" if producto.activo else "No",
            ]
            for producto in productos.iterator(chunk_size=500)
        ),
    )

    usuarios = Usuario.objects.select_related(
        "perfil"
    ).order_by("pk")

    agregar_hoja(
        libro,
        "Usuarios",
        [
            "ID",
            "Nombre",
            "Correo",
            "Teléfono",
            "Activo",
            "Acceso administrativo",
            "Fecha de registro",
        ],
        (
            [
                usuario.pk,
                nombre_usuario(usuario),
                usuario.email,
                getattr(
                    getattr(usuario, "perfil", None),
                    "telefono",
                    "",
                ),
                "Sí" if usuario.is_active else "No",
                "Sí" if usuario.is_staff else "No",
                usuario.date_joined,
            ]
            for usuario in usuarios.iterator(chunk_size=500)
        ),
    )

    return respuesta_excel(libro, "reporte_general.xlsx")