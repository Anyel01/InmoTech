

import os
from datetime import datetime
from flask import Flask, render_template
from markupsafe import Markup


def format_cop(valor):

    if valor is None:
        return "$ 0 COP"
    try:
        val_float = float(valor)
        # Formateo con separador de miles por punto
        formateado = f"{val_float:,.0f}".replace(',', '.')
        return f"$ {formateado} COP"
    except (ValueError, TypeError):
        return f"$ {valor} COP"


def format_date(valor):
 
    if not valor:
        return ""
    if isinstance(valor, str):
        try:
            limpia = valor.replace('T', ' ')
            if len(limpia) == 16:
                limpia += ':00'
            dt = datetime.strptime(limpia, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return valor
    elif isinstance(valor, datetime):
        dt = valor
    else:
        return str(valor)

    hora_12 = dt.strftime('%I:%M %p')
    return f"{dt.day:02d}/{dt.month:02d}/{dt.year} {hora_12}"


ICONO_CATEGORIA = {
    'Casa': 'casa',
    'Apartamento': 'apartamento',
    'Lote': 'lote',
    'Local': 'local',
}


def ico(nombre):
    return Markup(f'<span class="ico ico-{nombre}" aria-hidden="true"></span>')


def ico_categoria(categoria):
    return ico(ICONO_CATEGORIA.get(categoria, 'ubicacion'))


def create_app():

    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # Configuración de seguridad
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'inmotech_clave_secreta_por_defecto_desarrollo_2026'
    )
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Registro de filtros personalizados en Jinja2
    app.jinja_env.filters['cop'] = format_cop
    app.jinja_env.filters['fecha'] = format_date
    app.jinja_env.globals['ico'] = ico
    app.jinja_env.globals['ico_categoria'] = ico_categoria

    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return render_template('base.html', error_status=404, error_msg="La página solicitada no fue encontrada."), 404

    @app.errorhandler(403)
    def acceso_prohibido(e):
        return render_template('base.html', error_status=403, error_msg="No tienes autorización para acceder a este recurso."), 403

    @app.errorhandler(500)
    def error_interno(e):
        return render_template('base.html', error_status=500, error_msg="Ocurrió un error interno en el servidor. Intente más tarde."), 500

    return app
