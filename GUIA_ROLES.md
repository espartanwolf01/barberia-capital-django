# Accesos de Barbería Capital

## Instalación en el proyecto existente

1. Detén el servidor con Ctrl + C.
2. Coloca `instalar_roles_capital.py` junto a `manage.py`.
3. Ejecuta `.\entorno\Scripts\python.exe instalar_roles_capital.py`.
4. El instalador respalda los archivos y SQLite, aplica la migración y ejecuta las pruebas.
5. Cuando pida contraseña, escribe una para las cuentas nuevas de presentación y repítela. No aparece al escribir. Las cuentas existentes conservan su contraseña.
6. Arranca `.\entorno\Scripts\python.exe manage.py runserver`.

## Roles y rutas

| Rol | Pantalla al iniciar sesión | Funciones |
| --- | --- | --- |
| Cliente | `/mi-cuenta` | Sus citas, sus pedidos, perfil, tienda y carrito. |
| Barbero | `/barbero` | Solo sus citas asignadas; filtrar y marcar pendientes como atendidas o canceladas. |
| Administrador | `/panel` | Gestión general, inventario, reportes y usuarios/accesos. |

El acceso es común: `/login`. Acepta correo o nombre de usuario.
El rol no se selecciona en la pantalla de acceso ni en el registro público.

## Cuentas para la presentación

- Administrador: conserva tu superusuario actual. Si no existe ninguno activo, crea `admin@capital.local`.
- Cliente: crea `cliente@capital.local` si todavía no existe.
- Cada barbero activo sin cuenta recibe `barbero<ID>@capital.local`. El comando imprime las cuentas exactas.
- Una ficha Barbero solo puede tener una cuenta vinculada y cada cuenta solo una ficha.
- El registro público siempre crea clientes. Solo un superadministrador puede crear nuevos administradores desde Usuarios y accesos.

Las cuentas y claves se guardan en SQLite. Las contraseñas se almacenan mediante el hash de Django.
`preparar_accesos` puede ejecutarse nuevamente: conserva cuentas vinculadas y contraseñas existentes.

## Gestionar cuentas

Desde el panel abre **Usuarios y accesos** (`/panel/cuentas`).
Puedes crear clientes y vincular cuentas de barberos. Para un barbero nuevo, crea antes su ficha con **Gestionar barberos**.
Los administradores pueden activar o desactivar las cuentas permitidas; no se puede desactivar la propia cuenta desde esta pantalla.
Un barbero con ficha inactiva no puede iniciar sesión ni usar su agenda. Una cuenta desactivada tampoco puede entrar.

## Prueba rápida de sustentación

1. Entra con un cliente y reserva con un barbero.
2. En otra ventana de incógnito entra con la cuenta de ese barbero: la reserva debe aparecer en su agenda.
3. Entra con otro barbero: no debe mostrar la reserva anterior.
4. Marca la cita como atendida desde el barbero asignado y comprueba el estado con el cliente y el administrador.
5. Comprueba que cliente y barbero no entran en `/panel`, `/panel/cuentas`, `/reportes` ni `/admin/`.
6. Cierra sesión e inicia con cada rol: debe abrir su pantalla correspondiente.

Pruebas automáticas: `.\entorno\Scripts\python.exe manage.py test principal.test_roles`.

## Guardar en GitHub

Revisa `git status`, después agrega `principal`, `instalar_roles_capital.py` y `GUIA_ROLES.md` al commit.
No agregues `db.sqlite3`, las carpetas de respaldo ni archivos con contraseñas.

## Otro PC

Después de `git pull`, instala requirements y ejecuta las migraciones.
Carga el catálogo y los productos si esa BD está vacía, asigna las imágenes y ejecuta:

`.\entorno\Scripts\python.exe manage.py preparar_accesos`

Los archivos del código viajan por Git; las cuentas y citas de una BD local no se sincronizan entre PCs. Para conservar exactamente las cuentas y el historial, transfiere un respaldo de SQLite con el servidor detenido y también `media/` por un medio privado. Conserva la copia anterior del otro PC antes de reemplazarla. No subas ese respaldo a GitHub.
