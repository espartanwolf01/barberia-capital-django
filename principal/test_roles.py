from datetime import timedelta, time
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Barbero, Cita, Pedido, Perfil, Servicio

Usuario = get_user_model()
CLAVE = "EnsayoClaro#7q9X"


class RolesTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser("adminprueba", "adminprueba@example.com", CLAVE)
        self.cliente = Usuario.objects.create_user("cliente@example.com", "cliente@example.com", CLAVE)
        self.otro_cliente = Usuario.objects.create_user("otro@example.com", "otro@example.com", CLAVE)
        self.u1 = Usuario.objects.create_user("barbero1@example.com", "barbero1@example.com", CLAVE)
        self.u2 = Usuario.objects.create_user("barbero2@example.com", "barbero2@example.com", CLAVE)
        for usuario in [self.admin, self.cliente, self.otro_cliente, self.u1, self.u2]:
            Perfil.objects.create(usuario=usuario, nombre_completo=usuario.username, telefono="3001234567")
        self.b1 = Barbero.objects.create(nombre="Carlos Prueba", usuario=self.u1)
        self.b2 = Barbero.objects.create(nombre="Andrés Prueba", usuario=self.u2)
        self.servicio = Servicio.objects.create(nombre="Corte Prueba", categoria="cortes", precio="25000")
        fecha = timezone.localdate() + timedelta(days=2)
        self.c1 = Cita.objects.create(cliente=self.cliente, servicio=self.servicio, barbero=self.b1, fecha=fecha, hora=time(10))
        self.c2 = Cita.objects.create(cliente=self.otro_cliente, servicio=self.servicio, barbero=self.b2, fecha=fecha, hora=time(10))

    def test_login_redirige_cada_rol_y_acepta_usuario_admin(self):
        for usuario, destino in [(self.admin, "panel"), (self.cliente, "panel_cliente"), (self.u1, "panel_barbero")]:
            self.client.logout()
            respuesta = self.client.post(reverse("login"), {"dato": usuario.username, "password": CLAVE})
            self.assertRedirects(respuesta, reverse(destino))

    def test_cliente_y_barbero_no_entran_a_administracion(self):
        for usuario in [self.cliente, self.u1]:
            self.client.force_login(usuario)
            for ruta in ["panel", "gestionar_cuentas", "reportes", "exportar_reportes", "exportar_general", "admin:index"]:
                respuesta = self.client.get(reverse(ruta))
                self.assertEqual(respuesta.status_code, 302, ruta)
            self.client.logout()

    def test_agenda_solo_contiene_citas_propias(self):
        self.client.force_login(self.u1)
        respuesta = self.client.get(reverse("panel_barbero"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["agenda"].values_list("pk", flat=True)), [self.c1.pk])
        self.assertNotContains(respuesta, "Panel admin")

    def test_barbero_no_puede_modificar_cita_ajena(self):
        self.client.force_login(self.u1)
        respuesta = self.client.post(reverse("estado_barbero", args=[self.c2.pk]), {"estado": "cancelada"})
        self.assertEqual(respuesta.status_code, 404)
        self.c2.refresh_from_db()
        self.assertEqual(self.c2.estado, "pendiente")

    def test_barbero_actualiza_solo_pendientes_y_mediante_post(self):
        self.client.force_login(self.u1)
        url = reverse("estado_barbero", args=[self.c1.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url, {"estado": "atendida"})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.estado, "atendida")
        self.client.post(url, {"estado": "cancelada"})
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.estado, "atendida")

    def test_cliente_no_puede_usar_agenda_barbero(self):
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.get(reverse("panel_barbero")).status_code, 403)
        respuesta = self.client.post(reverse("estado_barbero", args=[self.c1.pk]), {"estado": "atendida"})
        self.assertEqual(respuesta.status_code, 403)

    def test_barbero_no_utiliza_acciones_de_admin(self):
        self.client.force_login(self.u1)
        respuesta = self.client.post(reverse("cambiar_estado_cita", args=[self.c2.pk]), {"estado": "atendida"})
        self.assertEqual(respuesta.status_code, 302)
        self.c2.refresh_from_db()
        self.assertEqual(self.c2.estado, "pendiente")

    def test_barbero_inactivo_no_entra_y_cuenta_desactivada_no_inicia(self):
        self.b1.activo = False
        self.b1.save(update_fields=["activo"])
        respuesta = self.client.post(reverse("login"), {"dato": self.u1.username, "password": CLAVE})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.client.force_login(self.u1)
        self.assertEqual(self.client.get(reverse("panel_barbero")).status_code, 403)
        self.client.logout()
        self.cliente.is_active = False
        self.cliente.save(update_fields=["is_active"])
        self.client.post(reverse("login"), {"dato": self.cliente.username, "password": CLAVE})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_cliente_no_muestra_datos_ajenos(self):
        Pedido.objects.create(cliente=self.otro_cliente, total="12345")
        self.client.force_login(self.cliente)
        respuesta = self.client.get(reverse("panel_cliente"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["citas_cliente"].values_list("pk", flat=True)), [self.c1.pk])
        self.assertEqual(len(respuesta.context["pedidos_cliente"]), 0)
        self.assertNotContains(respuesta, "Panel admin")

    def test_registro_publico_no_concede_privilegios(self):
        respuesta = self.client.post(reverse("registro"), {
            "nombre": "Nueva persona", "email": "nuevo@example.com", "telefono": "3001234567",
            "password": CLAVE, "rol": "administrador", "is_staff": "1", "is_superuser": "1",
        })
        usuario = Usuario.objects.get(username="nuevo@example.com")
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertFalse(Barbero.objects.filter(usuario=usuario).exists())
        self.assertRedirects(respuesta, reverse("panel_cliente"))

    def test_admin_crea_cuenta_barbero_y_perfil_correcto(self):
        nuevo = Barbero.objects.create(nombre="Juan sin cuenta")
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse("gestionar_cuentas"), {
            "nombre": "Juan sin cuenta", "email": "juan@example.com", "telefono": "3001234567",
            "rol": "barbero", "barbero": nuevo.pk, "password1": CLAVE, "password2": CLAVE,
        })
        self.assertRedirects(respuesta, reverse("gestionar_cuentas"))
        nuevo.refresh_from_db()
        self.assertEqual(nuevo.usuario.email, "juan@example.com")
        self.assertTrue(nuevo.usuario.check_password(CLAVE))
        self.assertFalse(nuevo.usuario.is_staff)
        self.assertEqual(nuevo.usuario.perfil.rol, "Barbero")

    def test_no_se_eleva_a_admin_un_staff_ordinario(self):
        usuario = Usuario.objects.create_user("staff", password=CLAVE, is_staff=True)
        self.client.force_login(usuario)
        self.client.post(reverse("gestionar_cuentas"), {
            "nombre": "Intento", "email": "intento@example.com", "rol": "administrador",
            "password1": CLAVE, "password2": CLAVE,
        })
        self.assertFalse(Usuario.objects.filter(email="intento@example.com").exists())
        respuesta = self.client.post(reverse("activar_cuenta", args=[self.admin.pk]))
        self.assertEqual(respuesta.status_code, 403)

    def test_perfil_cliente_no_puede_cambiar_su_rol(self):
        self.client.force_login(self.cliente)
        self.client.post(reverse("perfil"), {"nombre_completo": "Nombre editado", "telefono": "3007654321", "rol": "administrador", "is_staff": "1"})
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_staff)
        self.assertEqual(self.cliente.perfil.rol, "Cliente")

    def test_no_se_desactiva_la_propia_cuenta(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("activar_cuenta", args=[self.admin.pk]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_acciones_protegidas_por_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.u1)
        respuesta = cliente.post(reverse("estado_barbero", args=[self.c1.pk]), {"estado": "atendida"})
        self.assertEqual(respuesta.status_code, 403)

    @patch("principal.management.commands.preparar_accesos.getpass", return_value=CLAVE)
    def test_preparacion_repetible_no_resetea_claves(self, pedir_clave):
        nuevo = Barbero.objects.create(nombre="Barbero de presentación")
        call_command("preparar_accesos", verbosity=0)
        nuevo.refresh_from_db()
        pk = nuevo.usuario_id
        clave_guardada = nuevo.usuario.password
        total = Usuario.objects.count()
        call_command("preparar_accesos", verbosity=0)
        nuevo.refresh_from_db()
        self.assertEqual(nuevo.usuario_id, pk)
        self.assertEqual(nuevo.usuario.password, clave_guardada)
        self.assertEqual(Usuario.objects.count(), total)
