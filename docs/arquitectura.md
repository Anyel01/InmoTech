# Arquitectura

InmoTech es una aplicación Flask organizada en capas. Cada capa hace una sola cosa y solo le habla a la que tiene debajo.

![Arquitectura en capas](img/diagramas/arquitectura.svg)

## Por qué capas

La primera versión de cualquier proyecto suele mezclar todo en las rutas: validar el formulario, armar el SQL y devolver el HTML en la misma función. Funciona, pero cualquier cambio obliga a tocar todo. Separar en capas nos permite:

- **Cambiar la base de datos sin tocar las reglas.** De hecho lo hicimos: el proyecto corre en SQLite y en MySQL con el mismo código de negocio.
- **Encontrar rápido dónde está cada cosa.** Si falla una validación se busca en `services.py`; si falla una consulta, en `repositories.py`.
- **Probar cada capa por separado**, porque los servicios no dependen de Flask ni las rutas de SQL.

## Responsabilidad de cada archivo

| Archivo | Capa | Qué hace | Qué no debe hacer |
|---|---|---|---|
| `app/routes.py` | Presentación | Lee la petición, llama al servicio, devuelve plantilla o redirección, muestra mensajes | Validar reglas de negocio, escribir SQL |
| `app/services.py` | Negocio | Valida datos, aplica reglas (fecha futura, dueño del inmueble, transiciones de estado, formato y cantidad de fotos) y lanza `ValueError` o `PermissionError` | Escribir SQL |
| `app/repositories.py` | Datos | Contiene todo el SQL, una clase por entidad (`UsuarioRepository`, `InmuebleRepository`, `VisitaRepository`, `ImagenRepository`, `UbicacionCategoriaRepository`) | Tomar decisiones de negocio |
| `app/db.py` | Infraestructura | Abre la conexión, elige el motor, hace commit o rollback | Contener consultas de la aplicación |
| `app/auth.py` | Transversal | Guarda y lee la sesión, decoradores de rol, token CSRF | — |
| `app/admin/` | Las tres capas del panel de administración | Su propio `routes.py`, `services.py` y `repositories.py`, más el blueprint `/admin` | Mezclarse con el código de las pantallas públicas |
| `app/__init__.py` | Arranque | `create_app()`: configuración, filtros de plantilla (`cop`, `fecha`), iconos, páginas de error | — |
| `app/templates/` | Presentación | HTML con Jinja2; todas heredan de `base.html`. Los fragmentos que se repiten viven en parciales con guion bajo (`_tarjeta_inmueble.html`, `_galeria.html`) | Lógica de negocio |
| `app/static/js/` | Presentación | `main.js` (avisos, ciudades por departamento), `carrusel.js` (carrusel, vista ampliada, vista rápida) y `subida-fotos.js` (previsualización al publicar) | Reglas de negocio: todo se vuelve a validar en el servidor |

## Cómo viaja una petición

Ejemplo: un comprador pide una visita.

![Recorrido de una solicitud de visita](img/diagramas/flujo-solicitar-visita.svg)

1. El navegador envía el formulario por `POST`.
2. La ruta comprueba sesión, rol y token CSRF (`@role_required`, `validate_csrf`).
3. Llama a `VisitaService.solicitar_visita(...)`.
4. El servicio consulta el inmueble a través del repositorio y aplica las reglas: que exista, que esté disponible, que el comprador no sea el dueño y que la fecha sea futura.
5. Si todo está bien, el repositorio inserta la visita con estado `PENDIENTE` y hace commit.
6. La ruta redirige a `/mis-visitas` con un mensaje de éxito. Si una regla falló, el servicio lanzó `ValueError` y la ruta lo muestra como mensaje, sin haber tocado la base de datos.

## Rutas

| Método | Ruta | Quién | Función |
|---|---|---|---|
| GET | `/` | Todos | Inicio con categorías y últimos inmuebles |
| GET | `/catalogo` | Todos | Catálogo con filtros por query string |
| GET | `/inmuebles/<id>` | Todos | Detalle de un inmueble |
| GET, POST | `/login` | Todos | Inicio de sesión |
| GET, POST | `/registro` | Todos | Registro de comprador |
| GET | `/logout` | Todos | Cierra la sesión |
| GET, POST | `/inmuebles/nuevo` | Vendedor | Publicar inmueble |
| GET, POST | `/inmuebles/<id>/editar` | Vendedor dueño | Editar inmueble |
| POST | `/inmuebles/<id>/cambiar-estado` | Vendedor dueño | Pausar o reactivar |
| GET | `/mis-inmuebles` | Vendedor | Sus publicaciones |
| GET, POST | `/inmuebles/<id>/solicitar-visita` | Comprador | Pedir una visita |
| GET | `/mis-visitas` | Comprador | Sus solicitudes |
| POST | `/mis-visitas/<id>/cancelar` | Comprador dueño | Cancelar una solicitud pendiente |
| GET | `/visitas-recibidas` | Vendedor | Visitas a sus inmuebles |
| POST | `/visitas-recibidas/<id>/cambiar-estado` | Vendedor dueño | Confirmar, rechazar o marcar realizada |
| GET | `/api/ciudades/<id_departamento>` | Todos | JSON con las ciudades de un departamento (lo usa el formulario de publicar) |
| GET | `/api/inmuebles/<id>` | Todos | JSON con los datos públicos de un inmueble y sus fotos (lo usa la vista rápida del catálogo) |

## Fotos de los inmuebles

Es la parte con más piezas, así que se resume aquí el recorrido completo.

**Al publicar o editar** (`POST /inmuebles/nuevo` y `/inmuebles/<id>/editar`, con `enctype="multipart/form-data"`):

1. La ruta pasa `request.files.getlist('fotos')` al servicio.
2. `ImagenService.preparar` revisa **todas** las fotos antes de guardar nada: extensión permitida, peso máximo (4 MB), formato real por los primeros bytes del archivo (JPG, PNG o WebP) y cantidad máxima (8 por inmueble). Si una falla, lanza `ValueError` y no se crea ni se modifica nada.
3. Se crea o actualiza el inmueble.
4. `ImagenService.guardar` escribe cada archivo en `app/static/uploads/inmuebles/` con un nombre aleatorio (nunca se usa el nombre que trae el usuario) y registra las rutas en una sola transacción.
5. Al editar también se aplican los cambios sobre las fotos actuales: las marcadas "Quitar" se borran (fila y archivo, solo si fue subido por un vendedor) y la elegida como portada pasa a `orden = 1`.

**Al mostrarlas:**

| Pantalla | Qué muestra | De dónde salen los datos |
|---|---|---|
| Inicio y catálogo | Portada y número de fotos en cada tarjeta | Subconsultas `portada` y `total_imagenes` en los listados |
| Inicio | Las tarjetas recientes en un carrusel horizontal con flechas | `carrusel.js`, `[data-tarjetas]` |
| Catálogo e inicio | Botón "Vista rápida": ventana con carrusel y datos del inmueble | `GET /api/inmuebles/<id>`; la respuesta se guarda en memoria para no repetir la consulta |
| Detalle | Carrusel con miniaturas y vista ampliada | `_galeria.html`, renderizado en el servidor |
| Mis inmuebles | Miniatura y número de fotos | Subconsultas de `find_by_vendedor` |
| Publicar y editar | Fotos nuevas con vista previa, y una tarjeta que muestra cómo quedará la publicación | `subida-fotos.js` |

El carrusel del detalle se dibuja en el servidor (funciona aunque falle el JavaScript) y el de la vista rápida se arma en el navegador con el mismo HTML. Si el inmueble no tiene fotos, el detalle muestra el icono de su categoría como antes.

## Panel de administración

Es un subsistema con las mismas tres capas, en su propio paquete para no mezclarlo con las pantallas públicas:

| Archivo | Qué hace |
|---|---|
| `app/admin/__init__.py` | Crea el blueprint `admin` con el prefijo `/admin` |
| `app/admin/routes.py` | Las rutas. Un único `before_request` exige sesión y rol ADMINISTRADOR y valida el CSRF en todo `POST`, así una ruta nueva queda protegida sin decorarla |
| `app/admin/services.py` | Reglas: validación de usuarios, protecciones (no bloquearse, no dejar el sistema sin administradores, no borrar lo que tiene historial), paginación, exportación a CSV y cálculo de las cifras del resumen |
| `app/admin/repositories.py` | Todo el SQL del panel: estadísticas, listados con filtros y paginación, y el CRUD de usuarios y catálogos |
| `app/templates/admin/` | Menú lateral común (`_layout.html`), piezas repetidas (`_macros.html`) y una plantilla por pantalla |

| Ruta | Función |
|---|---|
| `GET /admin/` | Resumen con estadísticas |
| `GET /admin/usuarios` · `/nuevo` · `/<id>/editar` | Listado con filtros, alta y edición |
| `POST /admin/usuarios/<id>/estado` · `/password` · `/eliminar` | Bloquear o reactivar, restablecer contraseña, eliminar |
| `GET /admin/inmuebles` · `/<id>/editar` | Listado de todos los inmuebles y edición (reutiliza el formulario del vendedor, con fotos) |
| `POST /admin/inmuebles/<id>/estado` · `/eliminar` | Pausar o publicar, eliminar |
| `GET /admin/visitas` · `POST /admin/visitas/<id>/estado` | Listado y cambio de estado |
| `GET /admin/catalogos` · `POST /admin/catalogos/<entidad>/nuevo` · `/<id>/editar` · `/<id>/eliminar` | Categorías, departamentos y ciudades |
| `GET /admin/usuarios/exportar.csv` · `inmuebles/exportar.csv` · `visitas/exportar.csv` | Exportaciones que respetan los filtros activos |

**Actuar en nombre del dueño.** El administrador no tiene una ruta aparte para editar o pausar un inmueble: el servicio busca al vendedor dueño y llama al mismo `InmuebleService` que usa el vendedor, así las reglas y las fotos funcionan igual.

**La sesión siempre al día.** `auth.sincronizar_sesion` corre antes de cada petición y compara la sesión con la base de datos. Si el administrador bloquea una cuenta, esa persona queda fuera en su siguiente clic; si le cambia el rol, la sesión abierta lo refleja sin volver a iniciar sesión. Cuesta una lectura por petición, que en SQLite es despreciable.

**Después de iniciar sesión**, el administrador va directo a `/admin/`, y la barra superior le muestra el enlace al panel.

## Decisiones de diseño

**Repositorios con métodos estáticos.** Cada consulta es un método con nombre propio (`find_by_vendedor`, `update_estado`). Las rutas y servicios nunca arman SQL.

**Errores como excepciones.** Los servicios lanzan `ValueError` cuando el dato es inválido y `PermissionError` cuando el usuario no es el dueño. La ruta los atrapa y los convierte en un `flash`. Así una regla vive en un solo lugar.

**Nombres.** El dominio (tablas, columnas, servicios) está en español porque es el lenguaje del negocio; las URLs también. Las funciones de las rutas llevan nombres técnicos cortos (`catalog`, `request_visit`) para usarlas con `url_for`.

**Iconos.** Cada icono es un archivo SVG en `static/img/icons/`. La función `ico('nombre')` (registrada en `create_app`) pinta un `<span>` que usa ese archivo como máscara, así el icono toma el color del texto que lo rodea. `ico_categoria()` elige el icono según el tipo de inmueble.

**Estilos.** `styles.css` es la base y `theme.css` la sobrescribe con la identidad visual actual; `icons.css` solo define los iconos.

## Cómo agregar una funcionalidad

Por ejemplo, "marcar un inmueble como favorito":

1. **Base de datos**: tabla `favorito` en `database/01_estructura.sql` y su equivalente en `database/sqlite/01_estructura.sql`.
2. **Repositorio**: `FavoritoRepository` con `create`, `delete` y `find_by_usuario`.
3. **Servicio**: `FavoritoService` con las reglas (no duplicar, el inmueble debe existir).
4. **Ruta**: una ruta protegida con `@role_required('COMPRADOR')` que llame al servicio y valide el CSRF si es `POST`.
5. **Plantilla**: el botón en `property_detail.html` y la lista en una página nueva.
6. Documentar el cambio en `docs/base-de-datos.md`.
