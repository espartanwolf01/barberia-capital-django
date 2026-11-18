from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import EditarPerfilForm, RegistroForm
from .models import Perfil

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
                "No se pudo crear la cuenta. Comprueba si el correo ya existe.",
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
        messages.success(request, "Tus datos se actualizaron correctamente.")
        return redirect("perfil")

    return render(
        request,
        "principal/perfil.html",
        {
            "datos_perfil": datos_perfil,
            "formulario": formulario,
        },
    )