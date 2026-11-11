

from functools import wraps
import secrets
from flask import session, redirect, url_for, flash, request, abort


ROL_ADMINISTRADOR = 'ADMINISTRADOR'
ROL_VENDEDOR = 'VENDEDOR'
ROL_COMPRADOR = 'COMPRADOR'


def login_user(usuario_data):
    session.clear()
    session['user_id'] = usuario_data['id_usuario']
    session['nombre'] = usuario_data['nombre']
    session['apellido'] = usuario_data['apellido']
    session['correo'] = usuario_data['correo']
    session['id_rol'] = usuario_data['id_rol']
    session['rol_nombre'] = usuario_data['rol_nombre']
    session.permanent = True


def logout_user():

    session.clear()


def is_authenticated():

    return 'user_id' in session


def current_user():

    if not is_authenticated():
        return None
    return {
        'id_usuario': session.get('user_id'),
        'nombre': session.get('nombre'),
        'apellido': session.get('apellido'),
        'correo': session.get('correo'),
        'id_rol': session.get('id_rol'),
        'rol_nombre': session.get('rol_nombre')
    }


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('routes.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Debes iniciar sesión para acceder a esta función.', 'warning')
                return redirect(url_for('routes.login', next=request.path))
            
            user_role = session.get('rol_nombre')
            if user_role not in allowed_roles:
                flash('Acceso denegado: Tu perfil no cuenta con permisos para realizar esta acción.', 'danger')
                return redirect(url_for('routes.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_csrf_token():

    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf():

    token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
    session_token = session.get('_csrf_token')
    if not token or not session_token or not secrets.compare_digest(token, session_token):
        abort(400, description="Token CSRF inválido o expirado.")
