# Base de datos

Este documento explica cómo se diseñó la base de datos de InmoTech, cómo se implementó y cómo la usa la aplicación.

## Resumen

- **Base de datos:** SQLite. Es un solo archivo, `instance/inmotech.sqlite3`, que la aplicación crea sola la primera vez que arranca, con las tablas y los datos de ejemplo. No hay que instalar ni configurar ningún servidor.
- **8 tablas**, todas relacionadas por llaves foráneas.
- **Scripts:** el esquema y los datos de la base SQLite están en `database/sqlite/` (`01_estructura.sql` y `02_datos_iniciales.sql`). `database/03_consultas.sql` reúne las consultas principales para probarlas a mano.
- **MySQL (opcional):** `database/01_estructura.sql` y `02_datos_iniciales.sql` son el mismo modelo escrito para MySQL 8, por si el proyecto se lleva a un servidor. La aplicación funciona con cualquiera de los dos cambiando `DB_DRIVER` en el `.env` (ver [la sección 7](#7-sqlite-y-mysql-con-el-mismo-código)).

![Modelo entidad-relación](img/diagramas/modelo-er.svg)

## 1. Cómo se diseñó

### Paso 1: identificar las entidades

Se partió de lo que el portal necesita guardar:

| Necesidad | Entidad |
|---|---|
| Quién usa el portal (compradores, vendedores, administrador) | `usuario` y `rol` |
| Qué se publica | `inmueble` |
| De qué tipo es (casa, apartamento, lote, local) | `categoria` |
| Dónde queda | `ciudad` y `departamento` |
| Quién quiere conocerlo y cuándo | `visita` |
| Cómo se ve | `imagen_inmueble` |

### Paso 2: definir las relaciones

Todas son de uno a muchos:

| Relación | Se lee como |
|---|---|
| `rol` 1 — N `usuario` | un rol lo tienen muchos usuarios |
| `usuario` 1 — N `inmueble` | un vendedor publica muchos inmuebles |
| `categoria` 1 — N `inmueble` | una categoría agrupa muchos inmuebles |
| `ciudad` 1 — N `inmueble` | en una ciudad hay muchos inmuebles |
| `departamento` 1 — N `ciudad` | un departamento tiene muchas ciudades |
| `inmueble` 1 — N `visita` | un inmueble recibe muchas visitas |
| `usuario` 1 — N `visita` | un comprador solicita muchas visitas |
| `inmueble` 1 — N `imagen_inmueble` | un inmueble tiene varias fotos |

`usuario` participa dos veces: como **vendedor** de un inmueble (`inmueble.id_vendedor`) y como **comprador** de una visita (`visita.id_comprador`). No se crearon tablas separadas de vendedor y comprador porque comparten los mismos datos; lo que los distingue es el rol.

### Paso 3: normalizar

El modelo está en tercera forma normal. Las decisiones concretas:

- **Ciudad y departamento en tablas aparte.** El departamento depende de la ciudad, no del inmueble. Si se guardara el nombre de ambos dentro de `inmueble`, un cambio de nombre obligaría a actualizar muchas filas y habría errores de escritura ("Bogota", "Bogotá").
- **`visita` no guarda el vendedor.** Se obtiene pasando por `inmueble`. Guardarlo dos veces permitiría que una visita apunte a un vendedor distinto al dueño del inmueble.
- **Las fotos van en su propia tabla.** Un inmueble tiene entre 0 y 8 fotos; guardarlas como columnas (`foto1`, `foto2`...) limitaría la cantidad y dejaría columnas vacías. La base de datos guarda solo la **ruta** del archivo, no la imagen: los archivos viven en `app/static/` y la base los referencia.
- **`categoria` y `rol` son tablas, `operacion` y `estado` son `ENUM`.** Las categorías y los roles son catálogos que pueden crecer sin tocar el código. En cambio `VENTA/ARRIENDO`, `DISPONIBLE/NO_DISPONIBLE` y los estados de la visita son conjuntos cerrados que el código usa para tomar decisiones, así que se dejan fijos en la propia columna.

### Paso 4: tipos de dato y restricciones

| Decisión | Razón |
|---|---|
| `precio DECIMAL(14,2)` | El dinero no se guarda en `FLOAT`: tiene errores de redondeo. 14 dígitos alcanzan para precios de inmuebles en pesos colombianos |
| `area DECIMAL(8,2)` | Metros cuadrados con dos decimales, hasta lotes grandes |
| `CHECK (precio > 0)`, `CHECK (area > 0)`, `CHECK (habitaciones >= 0)`, `CHECK (banos >= 0)` | La base rechaza datos absurdos aunque la aplicación falle |
| `correo UNIQUE` | No pueden existir dos cuentas con el mismo correo |
| `password_hash VARCHAR(255)` | Se guarda el hash, nunca la contraseña. 255 caracteres alcanzan para el formato de Werkzeug |
| `fecha_visita DATETIME` | La visita tiene fecha y hora |
| `utf8mb4` | Tildes, eñes y cualquier carácter sin problemas |

## 2. Diccionario de datos

### `rol`

| Columna | Tipo | Notas |
|---|---|---|
| `id_rol` | INT, PK, autoincremental | |
| `nombre` | VARCHAR(50), único | ADMINISTRADOR, VENDEDOR, COMPRADOR |

### `usuario`

| Columna | Tipo | Notas |
|---|---|---|
| `id_usuario` | INT, PK, autoincremental | |
| `nombre` | VARCHAR(100) | |
| `apellido` | VARCHAR(100) | |
| `correo` | VARCHAR(150), único | Se guarda en minúsculas |
| `password_hash` | VARCHAR(255) | Hash de Werkzeug (PBKDF2 en los datos de prueba; los registros nuevos usan el método por defecto de la versión instalada) |
| `telefono` | VARCHAR(20) | Texto, porque puede llevar prefijos |
| `id_rol` | INT, FK a `rol` | |
| `activo` | TINYINT(1) en MySQL / INTEGER en SQLite | `1` = la cuenta puede iniciar sesión, `0` = bloqueada. Por defecto 1. Solo lo cambia un administrador (`CHECK (activo IN (0, 1))`) |

### `departamento`

| Columna | Tipo | Notas |
|---|---|---|
| `id_departamento` | INT, PK, autoincremental | |
| `nombre` | VARCHAR(100), único | |

### `ciudad`

| Columna | Tipo | Notas |
|---|---|---|
| `id_ciudad` | INT, PK, autoincremental | |
| `nombre` | VARCHAR(100) | |
| `id_departamento` | INT, FK a `departamento` | |

### `categoria`

| Columna | Tipo | Notas |
|---|---|---|
| `id_categoria` | INT, PK, autoincremental | |
| `nombre` | VARCHAR(50), único | Casa, Apartamento, Lote, Local |

### `inmueble`

| Columna | Tipo | Notas |
|---|---|---|
| `id_inmueble` | INT, PK, autoincremental | |
| `titulo` | VARCHAR(200) | |
| `descripcion` | TEXT | |
| `direccion` | VARCHAR(200) | |
| `precio` | DECIMAL(14,2) | Mayor que 0. En COP; si es arriendo, es el canon mensual |
| `area` | DECIMAL(8,2) | Mayor que 0, en m² |
| `habitaciones` | INT | 0 o más. Los lotes y locales usan 0 |
| `banos` | INT | 0 o más |
| `operacion` | ENUM('VENTA','ARRIENDO') | |
| `estado` | ENUM('DISPONIBLE','NO_DISPONIBLE') | Por defecto DISPONIBLE |
| `id_categoria` | INT, FK a `categoria` | |
| `id_ciudad` | INT, FK a `ciudad` | |
| `id_vendedor` | INT, FK a `usuario` | |

### `visita`

| Columna | Tipo | Notas |
|---|---|---|
| `id_visita` | INT, PK, autoincremental | |
| `fecha_visita` | DATETIME | Fecha y hora propuestas |
| `mensaje` | TEXT, opcional | Lo que el comprador quiere decirle al vendedor |
| `estado` | ENUM('PENDIENTE','CONFIRMADA','CANCELADA','REALIZADA') | Por defecto PENDIENTE |
| `id_inmueble` | INT, FK a `inmueble` | |
| `id_comprador` | INT, FK a `usuario` | |

### `imagen_inmueble`

| Columna | Tipo | Notas |
|---|---|---|
| `id_imagen` | INT, PK, autoincremental | |
| `ruta` | VARCHAR(255) | Relativa a `static/`, por ejemplo `img/inmuebles/inmueble-2-1-fachada.svg` (fotos de ejemplo) o `uploads/inmuebles/<código>.jpg` (subidas por vendedores) |
| `descripcion` | VARCHAR(200) | Texto alternativo de la foto, para lectores de pantalla. Si está vacío la página usa "Foto N de <título>" |
| `orden` | INT | 1 o más (`CHECK`). Define la secuencia del carrusel; la foto con `orden = 1` es la portada |
| `id_inmueble` | INT, FK a `inmueble` | `ON DELETE CASCADE` |

## 3. Integridad referencial

Todas las llaves foráneas se declararon con:

```sql
ON UPDATE CASCADE
ON DELETE RESTRICT
```

- `ON UPDATE CASCADE`: si cambia una llave primaria, el cambio se propaga.
- `ON DELETE RESTRICT`: no se puede borrar algo que otra tabla está usando. No se puede borrar un vendedor que tiene inmuebles, ni un inmueble que tiene visitas, ni una ciudad con inmuebles. Es una protección contra borrados que dejarían datos huérfanos. Por eso el portal **no borra** inmuebles: los pausa con `estado = 'NO_DISPONIBLE'`.

La única excepción es `imagen_inmueble.id_inmueble`, que usa `ON DELETE CASCADE`: una foto no tiene sentido sin su inmueble, así que si algún día se borra un inmueble sus fotos se borran con él. (Al quitar una foto desde la edición se borra la fila y, si fue subida por el vendedor, también el archivo.)

Hay una regla que la base de datos **no** puede expresar con llaves foráneas: que `inmueble.id_vendedor` sea un usuario con rol VENDEDOR y que `visita.id_comprador` sea un COMPRADOR. Eso lo garantiza la aplicación (`@role_required` en las rutas y las comprobaciones de `services.py`).

## 4. Índices

Además de las llaves primarias y de las columnas `UNIQUE` (que MySQL indexa solo), se crearon índices en las columnas por las que se filtra o se une:

| Índice | Para qué |
|---|---|
| `idx_usuario_rol` | Unir `usuario` con `rol` |
| `idx_ciudad_departamento` | Listar ciudades de un departamento (el formulario de publicar) |
| `idx_inmueble_estado` | El catálogo siempre filtra `estado = 'DISPONIBLE'` |
| `idx_inmueble_ciudad`, `idx_inmueble_categoria`, `idx_inmueble_operacion`, `idx_inmueble_precio` | Filtros del catálogo |
| `idx_inmueble_vendedor` | "Mis inmuebles" |
| `idx_visita_inmueble`, `idx_visita_comprador` | Visitas de un inmueble o de un comprador |
| `idx_visita_estado`, `idx_visita_fecha` | Filtrar y ordenar visitas |
| `idx_imagen_inmueble_orden` (`id_inmueble`, `orden`) | Traer las fotos de un inmueble ya ordenadas, y encontrar la portada |

## 5. Scripts y orden de ejecución

| Script | Contenido |
|---|---|
| `database/01_estructura.sql` | Crea la base `inmotech_db`, borra las tablas si existen y las vuelve a crear con llaves, restricciones e índices |
| `database/02_datos_iniciales.sql` | Roles, 6 departamentos, 12 ciudades, 4 categorías, 5 usuarios de prueba, 8 inmuebles, 4 visitas y 26 fotos de ejemplo |
| `database/03_consultas.sql` | Las consultas principales del sistema, para probarlas a mano: catálogo, catálogo con filtros, detalle, publicaciones de un vendedor, visitas de un comprador, visitas de un vendedor y estadísticas |

Los dos primeros existen en dos versiones: la de MySQL en `database/` y la de SQLite en `database/sqlite/` (la que usa la aplicación por defecto). Son el mismo modelo.

**No hay migraciones.** El esquema se aplica cuando se crea la base. Si más adelante cambia una tabla (como pasó al agregar `usuario.activo` o la tabla `imagen_inmueble`), se modifica la base existente una sola vez y se actualizan los scripts, para que una base nueva nazca igual. La alternativa, si no hay datos que conservar, es borrar `instance/inmotech.sqlite3`: la aplicación lo vuelve a crear con el esquema y los datos de ejemplo actuales.

### SQLite (la que usa el proyecto)

No hay nada que ejecutar. En el `.env`:

```
DB_DRIVER=sqlite
DB_SQLITE_PATH=instance/inmotech.sqlite3
```

Al abrir la primera conexión, `app/db.py` ejecuta `database/sqlite/01_estructura.sql` (todo es `CREATE ... IF NOT EXISTS`, así que se puede repetir sin riesgo) y, si la tabla `rol` está vacía, carga `database/sqlite/02_datos_iniciales.sql`.

### MySQL (opcional)

`01_estructura.sql` **borra** las tablas existentes: úsalo para empezar de cero, no sobre datos reales. Para montar la base en MySQL:

```bash
mysql -u root -p < database/01_estructura.sql
mysql -u root -p < database/02_datos_iniciales.sql
```

Y en el `.env`:

```
DB_DRIVER=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_clave
DB_NAME=inmotech_db
```

Las cifras del panel de administración salen de consultas parecidas a la sección 7 de `03_consultas.sql` (ver [la sección 6](#consultas-del-panel-de-administración)).

## 6. Cómo la usa la aplicación

### Una sola puerta: `get_db_cursor()`

Toda consulta pasa por el gestor de contexto de `app/db.py`:

```python
with get_db_cursor() as cursor:                    # lectura
    cursor.execute("SELECT ... WHERE id = %s", (id,))
    fila = cursor.fetchone()

with get_db_cursor(commit=True) as cursor:         # escritura
    cursor.execute("INSERT ...", datos)
```

Hace tres cosas por nosotros:

1. Abre la conexión con el motor indicado en `DB_DRIVER`.
2. Si pasó `commit=True` y no hubo errores, confirma la transacción.
3. Si hubo cualquier excepción, hace `rollback` y la vuelve a lanzar; y siempre cierra cursor y conexión.

Las lecturas devuelven **diccionarios** (`fila['titulo']`), que es lo que consumen las plantillas.

### El SQL vive solo en `repositories.py`

Cada entidad tiene su clase:

| Clase | Tabla(s) | Métodos principales |
|---|---|---|
| `UsuarioRepository` | `usuario`, `rol` | `find_by_correo`, `find_by_id`, `create_comprador` |
| `InmuebleRepository` | `inmueble` y sus relaciones | `find_all_disponibles`, `find_destacados`, `find_by_id`, `find_by_vendedor`, `create`, `update`, `update_estado` |
| `VisitaRepository` | `visita` | `create`, `find_by_id`, `find_by_comprador`, `find_by_vendedor`, `update_estado` |
| `ImagenRepository` | `imagen_inmueble` | `find_by_inmueble`, `create_many`, `delete_many`, `reordenar` |
| `UbicacionCategoriaRepository` | `departamento`, `ciudad`, `categoria` | `get_departamentos`, `get_ciudades`, `get_categorias` |

### Consultas parametrizadas

Los valores que vienen del usuario **nunca** se pegan dentro del texto SQL. Se pasan aparte, como parámetros, y el motor los trata como datos:

```python
sql = "SELECT ... FROM `usuario` u ... WHERE u.correo = %s LIMIT 1;"
cursor.execute(sql, (correo,))
```

Esto evita la inyección SQL. Si alguien escribe `' OR 1=1 --` como correo, la base de datos lo busca literalmente como un correo.

### Filtros dinámicos del catálogo

El catálogo combina hasta seis filtros opcionales. La consulta se construye agregando condiciones fijas según qué filtros llegaron; lo único que viene del usuario son los valores, que van como parámetros:

```python
sql = """SELECT ... WHERE i.estado = 'DISPONIBLE'"""
params = []

if filtros.get('id_ciudad'):
    sql += " AND i.id_ciudad = %s"
    params.append(int(filtros['id_ciudad']))

if filtros.get('precio_min'):
    sql += " AND i.precio >= %s"
    params.append(float(filtros['precio_min']))
# ... categoría, operación, precio máximo y habitaciones
```

Los valores además pasan antes por `InmuebleService.obtener_catalogo`, que los convierte a número y descarta los inválidos. El filtrado ocurre en la base de datos, no en Python, así que el catálogo escala aunque haya miles de inmuebles.

### Uniones (JOIN)

Casi todas las consultas de lectura unen varias tablas para entregar la fila lista para mostrar. Por ejemplo, el detalle de un inmueble une `inmueble` con `categoria`, `ciudad`, `departamento` y `usuario` (el vendedor):

```sql
FROM `inmueble` i
INNER JOIN `categoria` c     ON i.id_categoria = c.id_categoria
INNER JOIN `ciudad` ci       ON i.id_ciudad = ci.id_ciudad
INNER JOIN `departamento` d  ON ci.id_departamento = d.id_departamento
INNER JOIN `usuario` u       ON i.id_vendedor = u.id_usuario
```

"Mis inmuebles" usa además `LEFT JOIN` con `visita` y `COUNT(...)` con `GROUP BY`, para contar cuántas visitas tiene cada publicación, incluidas las que tienen cero.

### La foto de portada en los listados

El inicio, el catálogo y "Mis inmuebles" necesitan la portada y el número de fotos de cada inmueble. En vez de unir con `imagen_inmueble` (lo que repetiría filas) se usan dos subconsultas en el `SELECT`, definidas una sola vez en `COLUMNAS_FOTOS` de `repositories.py`:

```sql
(SELECT im.ruta FROM `imagen_inmueble` im
 WHERE im.id_inmueble = i.id_inmueble
 ORDER BY im.orden ASC, im.id_imagen ASC LIMIT 1) AS portada,
(SELECT COUNT(*) FROM `imagen_inmueble` im2
 WHERE im2.id_inmueble = i.id_inmueble) AS total_imagenes
```

El índice `(id_inmueble, orden)` hace que cada subconsulta sea una búsqueda directa.

### Escrituras

| Acción | Sentencia |
|---|---|
| Registrar comprador | `INSERT INTO usuario` con una subconsulta que busca el `id_rol` de `'COMPRADOR'`, para que el rol no dependa de un número escrito en el código |
| Publicar inmueble | `INSERT INTO inmueble` con parámetros con nombre (`%(titulo)s`) |
| Editar inmueble | `UPDATE inmueble SET ... WHERE id_inmueble = ...` |
| Pausar o reactivar | `UPDATE inmueble SET estado = ...` |
| Pedir una visita | `INSERT INTO visita` con estado `PENDIENTE` |
| Cambiar el estado de una visita | `UPDATE visita SET estado = ...` |
| Subir fotos | `INSERT INTO imagen_inmueble` de todas las fotos en una sola transacción (`create_many`): o se guardan todas o ninguna |
| Quitar fotos | `DELETE FROM imagen_inmueble WHERE id_inmueble = ... AND id_imagen IN (...)`; el filtro por inmueble impide borrar fotos de otro vendedor |
| Elegir la portada | `UPDATE imagen_inmueble SET orden = ...` renumerando 1, 2, 3... con la elegida primero (`reordenar`) |

Las reglas que deciden **si** se puede hacer una escritura (dueño, fecha futura, transición válida) están en `services.py`, antes de llegar al repositorio. La base de datos es la última barrera, con sus `CHECK`, `UNIQUE` y llaves foráneas.

### Consultas del panel de administración

El panel (`app/admin/repositories.py`) agrega cuatro tipos de consulta nuevos:

**Estadísticas del resumen.** Una sola conexión ejecuta una consulta por cifra, todas con `GROUP BY` y `COUNT`:

| Cifra | Idea de la consulta |
|---|---|
| Usuarios por rol | `rol LEFT JOIN usuario ... GROUP BY rol`: así un rol sin usuarios aparece con 0 |
| Inmuebles por estado y por operación | `GROUP BY estado` / `GROUP BY operacion` |
| Inmuebles disponibles por categoría, con precio promedio | `categoria LEFT JOIN inmueble ON ... AND estado = 'DISPONIBLE'` con `COUNT` y `AVG(precio)`; el `LEFT JOIN` conserva las categorías sin inmuebles |
| Ciudades con más inmuebles | `GROUP BY ciudad ORDER BY COUNT(*) DESC LIMIT 6` |
| Visitas por estado | `GROUP BY estado` |
| Inmuebles con más visitas | `inmueble JOIN visita GROUP BY inmueble ORDER BY COUNT(*) DESC LIMIT 5` |
| Inmuebles sin fotos | `WHERE NOT EXISTS (SELECT 1 FROM imagen_inmueble ...)` |
| Cuentas bloqueadas | `WHERE activo = 0` |

Los porcentajes y el ancho de las barras se calculan en el servicio, no en SQL ni en la plantilla.

**Listados con filtros y paginación.** Usuarios, inmuebles y visitas se arman igual que el catálogo (condiciones fijas, valores como parámetros) más dos piezas:

- *Búsqueda de texto*: `LOWER(columna) LIKE %s ESCAPE '!'`. El texto del usuario se pasa por `patron_like()`, que escapa `%`, `_` y `!` para que no actúen como comodines. Se usa `ESCAPE` explícito porque SQLite lo exige y MySQL lo acepta.
- *Paginación*: primero `SELECT COUNT(*)` con las mismas condiciones, luego la consulta con `LIMIT %s OFFSET %s`. El servicio corrige la página si se pide una fuera de rango.

**Exportaciones.** Reutilizan los mismos listados sin `LIMIT`, así que el CSV respeta los filtros que se están viendo.

**Catálogos (categorías, departamentos y ciudades).** Las tres tablas se administran con el mismo código en `CatalogoRepository`. Los nombres de tabla y de columna salen de un diccionario fijo del código —nunca de lo que escribe el usuario—, y todos los valores van como parámetros. Antes de borrar, el servicio cuenta si el elemento está en uso (`ON DELETE RESTRICT` lo impediría de todos modos, pero así el mensaje explica por qué).

**Reglas de borrado que se apoyan en la base:**

| Acción | Qué pasa |
|---|---|
| Eliminar un usuario | Solo si no tiene inmuebles ni visitas; si tiene, se ofrece bloquear su cuenta |
| Eliminar un inmueble | Solo si no tiene visitas; sus fotos se borran en cascada y los archivos subidos también |
| Eliminar categoría, departamento o ciudad | Solo si no están en uso |
| Siempre | Debe quedar al menos un administrador activo |

## 7. SQLite y MySQL con el mismo código

![Un mismo SQL para dos motores](img/diagramas/motores-bd.svg)

El proyecto trabaja con SQLite, pero el SQL de los repositorios está escrito con la sintaxis de MySQL (marcadores `%s`, `CONCAT`...) para que se pueda cambiar de motor sin reescribir nada. `app/db.py` hace de adaptador:

| MySQL | SQLite | Cómo se resuelve |
|---|---|---|
| `%s` | `?` | `SQLiteCursor.execute` reemplaza los placeholders |
| `%(nombre)s` | `:nombre` | Ídem |
| `CONCAT(a, ' ', b)` | no existe | Se registra una función `CONCAT` al abrir la conexión |
| `AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | Está en el esquema propio de SQLite |
| `ENUM(...)` | `TEXT` con `CHECK (col IN (...))` | Ídem |
| `DECIMAL` | `NUMERIC` | Ídem |
| Llaves foráneas siempre activas | Hay que activarlas | `PRAGMA foreign_keys = ON` en cada conexión |
| Resultados como diccionario | `sqlite3.Row` | Se convierte con `dict(fila)` |

El esquema de SQLite vive en `database/sqlite/`:

- `01_estructura.sql` usa `CREATE TABLE IF NOT EXISTS`, así que se puede ejecutar en cada arranque.
- `02_datos_iniciales.sql` solo se carga si la tabla `rol` está vacía, es decir, la primera vez. Incluye los usuarios, los inmuebles, las visitas y las 26 fotos de ejemplo.

La base queda en `instance/inmotech.sqlite3`. Si se borra ese archivo, la aplicación lo vuelve a crear con los datos de prueba. Está en el `.gitignore`.

Conviene recordar que los scripts de `database/sqlite/` y los de `database/` (MySQL) son dos copias del mismo modelo: si se cambia una tabla, hay que cambiarla en los dos lugares.

## 8. Datos de prueba

Los 5 usuarios (clave `123456`) cubren los tres roles; el administrador es `admin@inmotech.com` y entra directo al panel. Cada inmueble tiene entre 2 y 4 fotos de ejemplo (ilustraciones propias, ver [diseño](diseno.md)). Los 8 inmuebles están repartidos entre 7 ciudades y las 4 categorías, y uno está `NO_DISPONIBLE` para comprobar que no aparece en el catálogo. Las 4 visitas tienen un estado distinto (pendiente, confirmada, realizada y cancelada), de modo que todas las pantallas se pueden probar de inmediato.

## 9. Limitaciones conocidas

- Se abre una conexión nueva por cada operación. Es simple y suficiente para este tamaño; con más usuarios convendría un pool de conexiones.
- La visita no impide por sí misma que dos compradores pidan el mismo horario; el vendedor decide al confirmar.
- Los dos conjuntos de scripts (MySQL y SQLite) deben mantenerse en paralelo.
- No hay migraciones automáticas (ver la sección 5): un cambio de esquema se aplica a mano sobre la base existente.
- La paginación usa `OFFSET`, que se vuelve lenta con cientos de miles de filas; para el tamaño de este portal no es un problema.
- No se guarda cuándo se creó una cuenta, un inmueble o una visita. Los "últimos" del resumen se calculan por el número de identificador, y no hay historial de cambios (quién cambió qué).
- La base guarda rutas, no archivos. Si se copia la base a otro equipo hay que copiar también `app/static/uploads/`, que es donde quedan las fotos subidas (esa carpeta no se versiona en git).
