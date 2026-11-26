from getpass import getpass
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from principal.models import Barbero, Perfil

Usuario = get_user_model()


class Command(BaseCommand):
    help = "Prepara cuentas de presentación para administrador, cliente y cada barbero; conserva las contraseñas existentes."

    def handle(self, *args, **options):
        if not Barbero.objects.filter(activo=True).exists():
            raise CommandError("Primero carga los barberos con cargar_catalogo.py o desde el administrador.")
        administrador = Usuario.objects.filter(is_staff=True, is_superuser=True, is_active=True).order_by("pk").first()
        especificaciones = []
        if administrador is None:
            especificaciones.append(("admin@capital.local", "Administrador Capital", "administrador", None))
        especificaciones.append(("cliente@capital.local", "Cliente de presentación", "cliente", None))
        for barbero in Barbero.objects.filter(activo=True).select_related("usuario"):
            if barbero.usuario_id:
                if barbero.usuario.is_staff or barbero.usuario.is_superuser:
                    raise CommandError(f"{barbero.nombre}: la cuenta vinculada es administrativa. Revisa la ficha del barbero.")
                continue
            especificaciones.append((f"barbero{barbero.pk}@capital.local", barbero.nombre, "barbero", barbero))

        pendientes = []
        for correo, nombre, rol, barbero in especificaciones:
            existente = Usuario.objects.filter(username__iexact=correo).first()
            if existente:
                if rol == "cliente" and not existente.is_staff and not existente.is_superuser and not Barbero.objects.filter(usuario=existente).exists():
                    continue
                raise CommandError(f"{correo} ya existe con otra configuración. No se cambió su contraseña ni su rol.")
            if Usuario.objects.filter(email__iexact=correo).exists():
                raise CommandError(f"Ya existe otra cuenta con el correo {correo}. Revisa Gestión de cuentas.")
            pendientes.append((correo, nombre, rol, barbero))

        clave = None
        if pendientes:
            self.stdout.write("Elige la contraseña para las cuentas NUEVAS de presentación. No se mostrará ni se guardará en archivos.")
            while True:
                clave = getpass("Contraseña para las cuentas nuevas: ")
                repetida = getpass("Repite la contraseña: ")
                if clave != repetida:
                    self.stdout.write("No coinciden. Inténtalo otra vez.")
                    continue
                try:
                    validate_password(clave)
                except ValidationError as errores:
                    self.stdout.write(" ".join(errores.messages))
                    continue
                break

        with transaction.atomic():
            for correo, nombre, rol, barbero in pendientes:
                usuario = Usuario.objects.create_user(
                    username=correo, email=correo, password=clave,
                    first_name=nombre, is_staff=rol == "administrador",
                    is_superuser=rol == "administrador",
                )
                Perfil.objects.create(usuario=usuario, nombre_completo=nombre, telefono="")
                if barbero:
                    if Barbero.objects.filter(pk=barbero.pk, usuario__isnull=True).update(usuario=usuario) != 1:
                        raise CommandError("La vinculación cambió. No se guardaron las nuevas cuentas.")
                elif rol == "administrador":
                    administrador = usuario

        self.stdout.write(self.style.SUCCESS("Accesos guardados. Las contraseñas de cuentas existentes se conservaron."))
        if administrador:
            self.stdout.write(f"ADMINISTRADOR: {administrador.get_username()} (usa su contraseña actual si ya existía)")
        cliente = Usuario.objects.filter(username__iexact="cliente@capital.local").first()
        if cliente:
            self.stdout.write(f"CLIENTE: {cliente.get_username()}")
        for barbero in Barbero.objects.filter(activo=True).select_related("usuario"):
            if barbero.usuario_id:
                estado = "activo" if barbero.usuario.is_active else "inactivo"
                self.stdout.write(f"BARBERO {barbero.nombre}: {barbero.usuario.get_username()} ({estado})")
