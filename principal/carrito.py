import secrets
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import DetallePedido, Pedido, Producto


class PedidoNoDisponible(Exception):
    pass


def obtener_carrito(request):
    carrito = request.session.get("carrito", {})

    if not isinstance(carrito, dict):
        return {}

    limpio = {}

    for identificador, cantidad in carrito.items():
        identificador = str(identificador)

        if (
            identificador.isascii()
            and identificador.isdigit()
            and len(identificador) <= 18
            and type(cantidad) is int
            and 1 <= cantidad <= 9999
        ):
            limpio[str(int(identificador))] = cantidad

    return limpio


def guardar_carrito(request, carrito):
    anterior = request.session.get("carrito", {})

    if anterior != carrito:
        request.session["carrito_token"] = secrets.token_hex(32)

    request.session["carrito"] = carrito


def leer_cantidad(request):
    valor = request.POST.get("cantidad", "").strip()

    if not valor.isascii() or not valor.isdigit():
        return None

    if len(valor) > 4:
        return None

    cantidad = int(valor)

    if not 1 <= cantidad <= 9999:
        return None

    return cantidad


@login_required(login_url="login")
@require_GET
def ver_carrito(request):
    carrito = obtener_carrito(request)

    productos = Producto.objects.filter(
        pk__in=[int(clave) for clave in carrito],
    ).in_bulk()

    items = []
    total = Decimal("0.00")
    cantidad_total = 0
    hay_problemas = False
    hay_eliminados = False

    for identificador, cantidad in list(carrito.items()):
        producto = productos.get(int(identificador))

        if producto is None:
            del carrito[identificador]
            hay_eliminados = True
            continue

        subtotal = producto.precio * cantidad

        disponible = (
            producto.activo
            and cantidad <= producto.stock
        )

        if not disponible:
            hay_problemas = True

        items.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
                "disponible": disponible,
            }
        )

        total += subtotal
        cantidad_total += cantidad

    guardar_carrito(request, carrito)

    token = request.session.get("carrito_token")

    if not token:
        token = secrets.token_hex(32)
        request.session["carrito_token"] = token

    if hay_eliminados:
        messages.warning(
            request,
            "Se retiraron productos que ya no existen.",
        )

    return render(
        request,
        "principal/carrito.html",
        {
            "items": items,
            "total": total,
            "cantidad_carrito": cantidad_total,
            "hay_problemas": hay_problemas,
            "carrito_token": token,
        },
    )


@login_required(login_url="login")
@require_POST
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(
        Producto,
        pk=producto_id,
        activo=True,
    )

    cantidad = leer_cantidad(request)

    if cantidad is None:
        messages.error(request, "Escribe una cantidad válida.")
        return redirect("tienda")

    carrito = obtener_carrito(request)
    identificador = str(producto.pk)
    nueva_cantidad = carrito.get(identificador, 0) + cantidad

    if nueva_cantidad > producto.stock:
        messages.error(
            request,
            "No hay suficientes unidades disponibles. "
            "Revisa también las que ya tienes en el carrito.",
        )
        return redirect("tienda")

    if nueva_cantidad > 9999:
        messages.error(
            request,
            "El máximo por producto es de 9999 unidades.",
        )
        return redirect("tienda")

    carrito[identificador] = nueva_cantidad
    guardar_carrito(request, carrito)

    messages.success(
        request,
        f"Agregaste {producto.nombre} al carrito.",
    )

    return redirect("carrito")


@login_required(login_url="login")
@require_POST
def actualizar_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    identificador = str(producto_id)

    if identificador not in carrito:
        messages.error(
            request,
            "Ese producto no está en tu carrito.",
        )
        return redirect("carrito")

    producto = get_object_or_404(
        Producto,
        pk=producto_id,
        activo=True,
    )

    cantidad = leer_cantidad(request)

    if cantidad is None:
        messages.error(request, "Escribe una cantidad válida.")
        return redirect("carrito")

    if cantidad > producto.stock:
        messages.error(
            request,
            f"Solo quedan {producto.stock} unidades disponibles.",
        )
        return redirect("carrito")

    carrito[identificador] = cantidad
    guardar_carrito(request, carrito)

    messages.success(request, "Cantidad actualizada.")

    return redirect("carrito")


@login_required(login_url="login")
@require_POST
def eliminar_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    identificador = str(producto_id)

    if identificador in carrito:
        del carrito[identificador]
        guardar_carrito(request, carrito)
        messages.success(request, "Producto eliminado del carrito.")
    else:
        messages.error(
            request,
            "Ese producto no está en tu carrito.",
        )

    return redirect("carrito")


@login_required(login_url="login")
@require_POST
def finalizar_pedido(request):
    token = request.POST.get("carrito_token", "")

    if (
        len(token) != 64
        or any(
            caracter not in "0123456789abcdef"
            for caracter in token
        )
    ):
        messages.error(
            request,
            "Recarga el carrito antes de confirmar.",
        )
        return redirect("carrito")

    existente = Pedido.objects.filter(
        clave_confirmacion=token,
        cliente=request.user,
    ).first()

    if existente:
        return redirect(
            "compra_exitosa",
            pedido_id=existente.pk,
        )

    token_sesion = request.session.get("carrito_token", "")

    if not secrets.compare_digest(token, token_sesion):
        messages.error(
            request,
            "El carrito cambió. Revísalo antes de confirmar.",
        )
        return redirect("carrito")

    carrito = obtener_carrito(request)

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito")

    try:
        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=request.user,
                clave_confirmacion=token,
                total=Decimal("0.00"),
            )

            productos = {
                producto.pk: producto
                for producto in (
                    Producto.objects.select_for_update()
                    .filter(
                        pk__in=[
                            int(clave)
                            for clave in carrito
                        ]
                    )
                    .order_by("pk")
                )
            }

            total = Decimal("0.00")

            for identificador, cantidad in sorted(carrito.items()):
                producto = productos.get(int(identificador))

                if producto is None or not producto.activo:
                    raise PedidoNoDisponible(
                        "Un producto ya no está disponible. "
                        "Revisa tu carrito."
                    )

                actualizados = Producto.objects.filter(
                    pk=producto.pk,
                    activo=True,
                    stock__gte=cantidad,
                    precio=producto.precio,
                ).update(
                    stock=F("stock") - cantidad,
                )

                if actualizados != 1:
                    raise PedidoNoDisponible(
                        f"No se pudo reservar {producto.nombre}. "
                        "Su stock o precio cambió. Revisa el carrito."
                    )

                subtotal = producto.precio * cantidad
                total += subtotal

                if total > Decimal("999999999999.99"):
                    raise PedidoNoDisponible(
                        "El total supera el máximo permitido. "
                        "Reduce las cantidades."
                    )

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    nombre_producto=producto.nombre,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                )

            pedido.total = total
            pedido.save(update_fields=["total"])

    except PedidoNoDisponible as error:
        messages.error(request, str(error))
        return redirect("carrito")

    except IntegrityError:
        existente = Pedido.objects.filter(
            clave_confirmacion=token,
            cliente=request.user,
        ).first()

        if existente:
            return redirect(
                "compra_exitosa",
                pedido_id=existente.pk,
            )

        messages.error(
            request,
            "No se pudo registrar el pedido. "
            "Revisa el carrito e inténtalo nuevamente.",
        )
        return redirect("carrito")

    guardar_carrito(request, {})

    messages.success(
        request,
        f"Tu pedido #{pedido.pk} fue registrado.",
    )

    return redirect(
        "compra_exitosa",
        pedido_id=pedido.pk,
    )


@login_required(login_url="login")
@require_GET
def compra_exitosa(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("detalles"),
        pk=pedido_id,
        cliente=request.user,
    )

    return render(
        request,
        "principal/compra_exito.html",
        {"pedido": pedido},
    )