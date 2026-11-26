from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .cuentas_forms import AgendaFiltroForm, CuentaForm
from .models import Barbero, Cita, Pedido, Perfil
from .roles import destino_usuario, rol_usuario

Usuario = get_user_model()


def barbero_autorizado(request):
    barbero = Barbero.objects.filter(usuario=request.user, activo=True).first()
    if barbero is None or request.user.is_staff:
        raise PermissionDenied("Esta agenda pertenece a una cuenta de barbero activa.")
    return barbero


@login_required(login_url="login")
@require_GET
def mi_acceso(request):
    return redirect(destino_usuario(request.user))


@login_required(login_url="login")
@require_GET
def panel_cliente(request):
    if rol_usuario(request.user) != "cliente":
        return redirect(destino_usuario(request.user))
    citas = Cita.objects.filter(cliente=request.user).select_related("servicio", "barbero")
    pedidos = Pedido.objects.filter(cliente=request.user).prefetch_related("detalles")
    return render(request, "principal/panel_cliente.html", {
        "citas_cliente": citas[:8], "pedidos_cliente": pedidos[:8],
        "pendientes": citas.filter(estado=Cita.Estado.PENDIENTE).count(),
        "total_pedidos_cliente": pedidos.count(),
    })


@login_required(login_url="login")
@require_GET
def panel_barbero(request):
    barbero = barbero_autorizado(request)
    citas = Cita.objects.filter(barbero=barbero).select_related("cliente", "cliente__perfil", "servicio")
    resumen = citas.aggregate(
        pendientes=Count("pk", filter=Q(estado=Cita.Estado.PENDIENTE)),
        atendidas=Count("pk", filter=Q(estado=Cita.Estado.ATENDIDA)),
        canceladas=Count("pk", filter=Q(estado=Cita.Estado.CANCELADA)),
    )
    filtro = AgendaFiltroForm(request.GET or None)
    if filtro.is_bound:
        if filtro.is_valid():
            if filtro.cleaned_data["fecha"]:
                citas = citas.filter(fecha=filtro.cleaned_data["fecha"])
            if filtro.cleaned_data["estado"]:
                citas = citas.filter(estado=filtro.cleaned_data["estado"])
        else:
            citas = citas.none()
    return render(request, "principal/panel_barbero.html", {
        "barbero_actual": barbero, "agenda": citas.order_by("fecha", "hora", "pk"),
        "resumen": resumen, "filtro": filtro,
    })


@login_required(login_url="login")
@require_POST
def estado_barbero(request, cita_id):
    barbero = barbero_autorizado(request)
    cita = get_object_or_404(Cita, pk=cita_id, barbero=barbero)
    estado = request.POST.get("estado", "")
    if estado not in [Cita.Estado.ATENDIDA, Cita.Estado.CANCELADA]:
        messages.error(request, "Selecciona un estado válido.")
    else:
        actualizadas = Cita.objects.filter(
            pk=cita.pk, barbero=barbero, estado=Cita.Estado.PENDIENTE,
            barbero__activo=True, barbero__usuario=request.user,
        ).update(estado=estado)
        if actualizadas:
            messages.success(request, f"Cita #{cita.pk}: {Cita.Estado(estado).label}.")
        else:
            messages.error(request, "La cita ya cambió de estado. Recarga la agenda.")
    return redirect("panel_barbero")


@staff_member_required(login_url="admin:login")
@require_http_methods(["GET", "POST"])
def gestionar_cuentas(request):
    formulario = CuentaForm(request.POST if request.method == "POST" else None, administrador=request.user)
    if request.method == "POST" and formulario.is_valid():
        datos = formulario.cleaned_data
        try:
            with transaction.atomic():
                usuario = Usuario.objects.create_user(
                    username=datos["email"], email=datos["email"],
                    password=datos["password1"], first_name=datos["nombre"],
                    is_staff=datos["rol"] == "administrador", is_superuser=False,
                )
                Perfil.objects.create(usuario=usuario, nombre_completo=datos["nombre"], telefono=datos["telefono"])
                if datos["rol"] == "barbero":
                    vinculados = Barbero.objects.filter(pk=datos["barbero"].pk, usuario__isnull=True, activo=True).update(usuario=usuario)
                    if vinculados != 1:
                        raise IntegrityError("El barbero ya tiene cuenta.")
                elif datos["rol"] == "administrador":
                    usuario.user_permissions.set(Permission.objects.filter(content_type__app_label="principal"))
        except IntegrityError:
            formulario.add_error(None, "El correo o el barbero ya se utilizaron. Comprueba los datos.")
        else:
            messages.success(request, "Cuenta creada. Ya puede iniciar sesión con su correo.")
            return redirect("gestionar_cuentas")
    usuarios = Usuario.objects.select_related("perfil", "barbero").order_by("username")
    cuentas = [{"usuario": usuario, "rol": rol_usuario(usuario)} for usuario in usuarios]
    return render(request, "principal/gestionar_cuentas.html", {"formulario": formulario, "cuentas": cuentas})


@staff_member_required(login_url="admin:login")
@require_POST
def activar_cuenta(request, usuario_id):
    with transaction.atomic():
        usuario = get_object_or_404(Usuario.objects.select_for_update(), pk=usuario_id)
        if usuario.pk == request.user.pk:
            messages.error(request, "No puedes desactivar tu propia cuenta.")
            return redirect("gestionar_cuentas")
        if usuario.is_staff or usuario.is_superuser:
            if not request.user.is_superuser:
                raise PermissionDenied("Solo el superadministrador administra otras cuentas administrativas.")
        if usuario.is_superuser and usuario.is_active and Usuario.objects.filter(is_superuser=True, is_active=True).count() <= 1:
            messages.error(request, "Debe quedar un superadministrador activo.")
            return redirect("gestionar_cuentas")
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])
    messages.success(request, "Estado de la cuenta actualizado.")
    return redirect("gestionar_cuentas")
