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
| Rol del registro | El registro siempre asigna COMPRADOR; el formulario no puede pedir otro rol | `UsuarioRepository.create_comprador` |

## Qué cambiar antes de publicar el sitio

- **`SECRET_KEY`**: definir una clave larga y propia en el `.env`. Si falta, la aplicación usa una clave de desarrollo que está escrita en el código.
- **`FLASK_DEBUG=0`**: el modo debug muestra errores detallados y no debe usarse en producción.
- **Servidor de producción**: `python run.py` usa el servidor de desarrollo de Flask. En producción corresponde un servidor WSGI (por ejemplo gunicorn o waitress) detrás de HTTPS.
- **Cookie segura**: con HTTPS, activar `SESSION_COOKIE_SECURE = True`.
- **Cuentas de prueba**: borrar los usuarios de `02_datos_iniciales.sql`, todos comparten la clave `123456`.
- **`.env`**: no se sube al repositorio (está en `.gitignore`); solo se versiona `.env.example`.
