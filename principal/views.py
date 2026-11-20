from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from .forms import CitaForm, EditarPerfilForm, RegistroForm
from .models import Barbero, Cita, Perfil, Producto, Servicio
Usuario = get_user_model()


def inicio(request):
    return render(request, "principal/inicio.html")


def servicios(request):
    return render(request, "principal/servicios.html")


def contacto(request):
    return render(request, "principal/contacto.html")


def registro(request):
    formulario = RegistroForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and formulario.is_valid():
        datos = formulario.cleaned_data

        try:
            with transaction.atomic():
                usuario = Usuario.objects.create_user(
                    username=datos["email"],
                    email=datos["email"],
                    password=datos["password"],
                )

                Perfil.objects.create(
                    usuario=usuario,
                    nombre_completo=datos["nombre"],
                    telefono=datos["telefono"],
                )

        except IntegrityError:
            formulario.add_error(
                None,
                "No se pudo crear la cuenta. "
                "Comprueba si el correo ya existe.",
            )
        else:
            login(request, usuario)
            return redirect("inicio")

    return render(
        request,
        "principal/registro.html",
        {"formulario": formulario},
    )


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    error = None

    if request.method == "POST":
        correo = request.POST.get("dato", "").strip().lower()
        password = request.POST.get("password", "")

        usuario = authenticate(
            request,
            username=correo,
            password=password,
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")

        error = "Correo o contraseña incorrectos, o cuenta inactiva."

    return render(
        request,
        "principal/login.html",
        {"error": error},
    )


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect("inicio")


@login_required(login_url="login")
def perfil(request):
    datos_perfil = Perfil.objects.filter(
        usuario=request.user
    ).first()

    if datos_perfil is None:
        datos_perfil = Perfil(usuario=request.user)

    formulario = EditarPerfilForm(
        request.POST if request.method == "POST" else None,
        instance=datos_perfil,
    )

    if request.method == "POST" and formulario.is_valid():
        formulario.save()

        messages.success(
            request,
            "Tus datos se actualizaron correctamente.",
        )

        return redirect("perfil")

    return render(
        request,
        "principal/perfil.html",
        {
            "datos_perfil": datos_perfil,
            "formulario": formulario,
        },
    )


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def citas(request):
    formulario = CitaForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and formulario.is_valid():
        try:
            with transaction.atomic():
                nueva_cita = formulario.save(commit=False)
                nueva_cita.cliente = request.user
                nueva_cita.estado = Cita.Estado.PENDIENTE
                nueva_cita.save()

        except IntegrityError:
            formulario.add_error(
                None,
                "No se pudo reservar ese turno. "
                "Puede que otro cliente lo haya reservado. "
                "Elige otro horario e inténtalo nuevamente.",
            )
        else:
            messages.success(
                request,
                "¡Tu cita se reservó correctamente!",
            )

            return redirect("citas")

    mis_citas = Cita.objects.filter(
        cliente=request.user
    ).select_related(
        "servicio",
        "barbero",
    )

    datos_perfil = Perfil.objects.filter(
        usuario=request.user
    ).first()

    return render(
        request,
        "principal/citas.html",
        {
            "formulario": formulario,
            "mis_citas": mis_citas,
            "datos_perfil": datos_perfil,
        },
    )


@login_required(login_url="login")
@require_POST
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(
        Cita,
        pk=cita_id,
        cliente=request.user,
    )

    actualizadas = Cita.objects.filter(
        pk=cita.pk,
        cliente=request.user,
        estado=Cita.Estado.PENDIENTE,
    ).update(
        estado=Cita.Estado.CANCELADA,
    )

    if actualizadas:
        messages.success(
            request,
            "Tu cita fue cancelada. El turno quedó disponible.",
        )
    else:
        messages.error(
            request,
            "Solo puedes cancelar citas pendientes.",
        )

    return redirect("citas")


@login_required(login_url="login")
@require_POST
def reprogramar_cita(request, cita_id):
    cita = get_object_or_404(
        Cita,
        pk=cita_id,
        cliente=request.user,
    )

    if cita.estado != Cita.Estado.PENDIENTE:
        messages.error(
            request,
            "Solo puedes reprogramar citas pendientes.",
        )

        return redirect("citas")

    datos = {
        "servicio": request.POST.get(
            "servicio",
            cita.servicio_id,
        ),
        "barbero": cita.barbero_id,
        "fecha": request.POST.get("fecha", ""),
        "hora": request.POST.get("hora", ""),
        "notas": request.POST.get("notas", cita.notas),
    }

    formulario = CitaForm(datos, instance=cita)

    if not formulario.is_valid():
        for errores in formulario.errors.values():
            for error in errores:
                messages.error(request, error)

        return redirect("citas")

    try:
        with transaction.atomic():
            actualizadas = Cita.objects.filter(
                pk=cita.pk,
                cliente=request.user,
                estado=Cita.Estado.PENDIENTE,
            ).update(
                servicio=formulario.cleaned_data["servicio"],
                fecha=formulario.cleaned_data["fecha"],
                hora=formulario.cleaned_data["hora"],
                notas=formulario.cleaned_data["notas"],
            )

    except IntegrityError:
        messages.error(
            request,
            "Ese turno ya está ocupado. Elige otro horario.",
        )
    else:
        if actualizadas:
            messages.success(
                request,
                "El servicio y horario de tu cita se actualizaron.",
            )
        else:
            messages.error(
                request,
                "La cita ya no está pendiente y no se puede modificar.",
            )

    return redirect("citas")


@staff_member_required(login_url="admin:login")
@require_GET
def panel(request):
    resumen_usuarios = Usuario.objects.aggregate(
        total=Count("pk"),
        activos=Count(
            "pk",
            filter=Q(is_active=True),
        ),
    )

    resumen_citas = Cita.objects.aggregate(
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

    todas_las_citas = Cita.objects.select_related(
        "cliente",
        "cliente__perfil",
        "servicio",
        "barbero",
    )

    usuarios = Usuario.objects.select_related(
        "perfil"
    ).order_by("-date_joined")

    return render(
        request,
        "principal/panel.html",
        {
            "total_usuarios": resumen_usuarios["total"],
            "usuarios_activos": resumen_usuarios["activos"],
            "citas_pendientes": resumen_citas["pendientes"],
            "citas_atendidas": resumen_citas["atendidas"],
            "citas_canceladas": resumen_citas["canceladas"],
            "total_servicios": Servicio.objects.count(),
            "total_barberos": Barbero.objects.count(),
            "citas": todas_las_citas,
            "usuarios": usuarios,
        },
    )


@staff_member_required(login_url="admin:login")
@require_POST
def cambiar_estado_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    nuevo_estado = request.POST.get("estado", "")

    estados_permitidos = [
        Cita.Estado.ATENDIDA,
        Cita.Estado.CANCELADA,
    ]

    if nuevo_estado not in estados_permitidos:
        messages.error(
            request,
            "Selecciona un estado válido.",
        )

        return redirect("panel")

    actualizadas = Cita.objects.filter(
        pk=cita.pk,
        estado=Cita.Estado.PENDIENTE,
    ).update(
        estado=nuevo_estado,
    )

    if actualizadas:
        etiqueta = Cita.Estado(nuevo_estado).label

        messages.success(
            request,
            f"La cita #{cita.pk} se marcó como {etiqueta.lower()}.",
        )
    else:
        messages.error(
            request,
            "La cita ya no está pendiente. Recarga el panel.",
        )

    return redirect("panel")

@require_GET
def tienda(request):
    productos = Producto.objects.filter(activo=True)

    return render(
        request,
        "principal/tienda.html",
        {"productos": productos},
    )