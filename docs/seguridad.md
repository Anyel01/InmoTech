# Seguridad

Qué medidas tiene la aplicación y dónde está cada una.

| Riesgo | Medida | Dónde |
|---|---|---|
| Contraseñas expuestas | Se guarda solo el hash (`generate_password_hash`) y se compara con `check_password_hash` | `services.py`, `UsuarioService` |
| Inyección SQL | Todas las consultas son parametrizadas; los valores nunca se concatenan al texto SQL | `repositories.py` |
| CSRF (formularios enviados desde otro sitio) | Token aleatorio en la sesión, incluido como campo oculto y validado en cada `POST` con comparación de tiempo constante | `auth.py`: `generate_csrf_token`, `validate_csrf` |
| Acceso a pantallas de otro rol | Decorador `@role_required(...)` | `auth.py`, usado en `routes.py` |
| Modificar datos ajenos | Los servicios verifican que el inmueble o la visita pertenezcan al usuario de la sesión | `services.py` |
| Robo de la cookie de sesión por JavaScript | `SESSION_COOKIE_HTTPONLY = True` | `__init__.py` |
| Envío de la cookie desde otros sitios | `SESSION_COOKIE_SAMESITE = 'Lax'` | `__init__.py` |
| Fijación de sesión | `session.clear()` antes de guardar al usuario al iniciar sesión | `auth.py`: `login_user` |
| XSS | Jinja2 escapa automáticamente todo lo que se imprime en las plantillas | Plantillas |
| Redirección abierta en el login | El parámetro `next` solo se acepta si es una ruta interna (empieza por `/` y no por `//`) | `routes.py`: `login` |
| Saber si un correo existe | El login responde con el mismo mensaje si falla el correo o la clave | `services.py`: `autenticar` |
| Entrar al panel sin ser administrador | Un único `before_request` en el blueprint `/admin` exige sesión y rol ADMINISTRADOR en todas sus rutas, existentes y futuras | `app/admin/routes.py` |
| CSRF en las acciones del panel | El mismo `before_request` valida el token en todo `POST` | `app/admin/routes.py` |
| Cuenta bloqueada con la sesión abierta | Antes de cada petición se compara la sesión con la base de datos; si la cuenta está bloqueada o ya no existe, se cierra la sesión | `auth.py`: `sincronizar_sesion` |
| Rol cambiado con la sesión abierta | La misma comprobación actualiza el rol de la sesión, así un vendedor degradado pierde el acceso de inmediato | `auth.py`: `sincronizar_sesion` |
| Un administrador se deja fuera, o deja el sistema sin administradores | No puede bloquearse, cambiarse el rol ni eliminarse; y nunca se puede quitar, bloquear o eliminar al último administrador activo | `app/admin/services.py`: `UsuarioAdminService` |
| Borrar datos con historial | Un usuario con inmuebles o visitas y un inmueble con visitas no se pueden eliminar; se ofrece bloquear o pausar | `app/admin/services.py` |
| Inyección de fórmulas en los CSV | Los textos que empiezan por `=`, `+`, `-` o `@` se exportan con una comilla delante para que Excel no los ejecute | `app/admin/services.py`: `_celda_csv` |
| Redirección abierta tras una acción | El campo `volver` solo se acepta si empieza por `/admin` y no por `//` | `app/admin/routes.py`: `_volver` |
| Búsquedas con comodines | El texto buscado se escapa para que `%` y `_` se traten como caracteres normales | `app/admin/repositories.py`: `patron_like` |
| Rol del registro | El registro siempre asigna COMPRADOR; el formulario no puede pedir otro rol | `UsuarioRepository.create_comprador` |
| Archivos disfrazados al subir fotos | Se acepta solo JPG, PNG y WebP; además de la extensión se comprueban los primeros bytes del archivo, así que un texto renombrado a `.png` se rechaza | `services.py`: `ImagenService` |
| Scripts dentro de una "imagen" | No se aceptan SVG de usuarios (pueden llevar JavaScript). Las ilustraciones SVG del sitio las puso el equipo, no se suben | `ImagenService.EXTENSIONES` |
| Nombres de archivo peligrosos | El archivo se guarda con un nombre aleatorio; el nombre original nunca se usa como ruta en disco | `ImagenService.guardar` |
| Archivos enormes | 4 MB por foto, 8 fotos por inmueble y 36 MB por petición (`MAX_CONTENT_LENGTH`); si se pasa, se responde 413 con un mensaje | `ImagenService`, `__init__.py` |
| Borrar fotos de otro vendedor | La consulta de borrado filtra por inmueble y el servicio verifica el dueño antes de tocar nada | `ImagenRepository.delete_many`, `editar_inmueble` |
| Borrar archivos que no son fotos | Solo se borran archivos dentro de `static/uploads/inmuebles/`; las fotos de ejemplo no se tocan | `ImagenService._borrar_archivo` |
| El navegador adivina el tipo de un archivo | Cabecera `X-Content-Type-Options: nosniff` en todas las respuestas | `__init__.py` |

## Qué cambiar antes de publicar el sitio

- **`SECRET_KEY`**: definir una clave larga y propia en el `.env`. Si falta, la aplicación usa una clave de desarrollo que está escrita en el código.
- **`FLASK_DEBUG=0`**: el modo debug muestra errores detallados y no debe usarse en producción.
- **Servidor de producción**: `python run.py` usa el servidor de desarrollo de Flask. En producción corresponde un servidor WSGI (por ejemplo gunicorn o waitress) detrás de HTTPS.
- **Cookie segura**: con HTTPS, activar `SESSION_COOKIE_SECURE = True`.
- **Cuentas de prueba**: borrar los usuarios de `02_datos_iniciales.sql`, todos comparten la clave `123456`.
- **`.env`**: no se sube al repositorio (está en `.gitignore`); solo se versiona `.env.example`.

## Mejoras pendientes

- Reprocesar las fotos subidas (redimensionar y quitar metadatos como la ubicación GPS de la cámara). Hoy se guardan tal cual llegan.
- Límite de intentos fallidos de inicio de sesión.
