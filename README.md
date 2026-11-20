# InmoTech

Portal inmobiliario web para publicar, buscar y visitar inmuebles en Colombia. Hace parte del proyecto integrador y está construido con Python, Flask y SQL.

Un **vendedor** publica casas, apartamentos, lotes y locales; un **comprador** los busca con filtros y pide una visita; el vendedor confirma o rechaza esa visita. Todo el recorrido está cubierto: registro, inicio de sesión, catálogo, publicación, edición, agenda de visitas.

![Página de inicio](docs/img/capturas/01-inicio.png)

## Contenido

- [Qué hace](#qué-hace)
- [Tecnologías](#tecnologías)
- [Cómo ejecutarlo](#cómo-ejecutarlo)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Documentación](#documentación)
- [Pantallas](#pantallas)
- [Pendientes y mejoras](#pendientes-y-mejoras)

## Qué hace

| Rol | Puede |
|---|---|
| Visitante | Ver el inicio, explorar el catálogo con filtros, abrir el detalle de un inmueble, registrarse |
| Comprador | Todo lo anterior, pedir una visita a un inmueble disponible y cancelar sus solicitudes pendientes |
| Vendedor | Publicar inmuebles, editarlos, pausarlos o reactivarlos y gestionar las visitas que le llegan |
| Administrador | Entra al **panel de administración**: resumen con estadísticas, gestión de usuarios (crear, editar, bloquear, restablecer contraseña), de inmuebles, de visitas y de los catálogos, y exportación a CSV |

Cada inmueble tiene su galería de fotos con carrusel y vista ampliada, y el catálogo ofrece una vista rápida sin salir de la lista. Al publicar, el vendedor ve las fotos y la tarjeta tal como quedarán antes de guardar.

El catálogo se puede filtrar por ciudad, categoría, operación (venta o arriendo), rango de precio y mínimo de habitaciones. Los precios se muestran en pesos colombianos.

## Tecnologías

- **Python 3** y **Flask 3** (rutas, sesiones, plantillas Jinja2)
- **SQLite** como base de datos (un archivo, sin servidor). El mismo código también funciona con **MySQL** (`mysql-connector-python`)
- **Werkzeug** para el hash de contraseñas
- **python-dotenv** para la configuración
- HTML, CSS y JavaScript sin frameworks; iconos propios en SVG

## Cómo ejecutarlo

Requisitos: Python 3.10 o superior.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Después abre <http://127.0.0.1:5000>.

La primera vez que arranca, la aplicación crea el archivo `instance/inmotech.sqlite3` con las tablas y los datos de prueba. No hay que instalar ningún servidor de base de datos.

### Cuentas de prueba

La clave de todas es `123456`.

| Rol | Correo |
|---|---|
| Vendedor | carlos.vendedor@inmotech.com |
| Vendedor | maria.vendedora@inmotech.com |
| Comprador | juan.comprador@gmail.com |
| Comprador | laura.compradora@gmail.com |
| Administrador | admin@inmotech.com |

### Usar MySQL

1. Ejecuta en orden `database/01_estructura.sql` y `database/02_datos_iniciales.sql`.
2. En el `.env` cambia `DB_DRIVER=mysql` y completa `DB_HOST`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`.
3. Reinicia la aplicación.

El detalle está en [docs/base-de-datos.md](docs/base-de-datos.md).

## Estructura del proyecto

```
InmoTech/
├── run.py                    punto de entrada
├── requirements.txt
├── .env.example              plantilla de configuración
├── app/
│   ├── __init__.py           create_app(), filtros de plantilla, páginas de error
│   ├── routes.py             rutas HTTP públicas (controladores)
│   ├── services.py           reglas de negocio y validaciones
│   ├── repositories.py       todo el SQL de la aplicación
│   ├── db.py                 conexión y transacciones (SQLite / MySQL)
│   ├── auth.py               sesión, roles y protección CSRF
│   ├── admin/                panel de administración: routes, services y repositories propios
│   ├── templates/            base.html, las páginas, los parciales y admin/ (panel)
│   └── static/
│       ├── css/              styles.css, theme.css, icons.css, galeria.css, admin.css
│       ├── js/               main.js, carrusel.js, subida-fotos.js
│       ├── img/              favicon, iconos SVG e ilustraciones de los inmuebles de prueba
│       └── uploads/          fotos subidas por los vendedores (no se sube a git)
├── database/
│   ├── sqlite/               esquema y datos de la base SQLite (la que usa el proyecto)
│   ├── 01_estructura.sql     el mismo modelo para MySQL (opcional)
│   ├── 02_datos_iniciales.sql
│   └── 03_consultas.sql      consultas de referencia
├── tools/                    generador de las ilustraciones de ejemplo
├── docs/                     documentación y diagramas
└── instance/                 base SQLite local (no se sube a git)
```

![Arquitectura en capas](docs/img/diagramas/arquitectura.svg)
