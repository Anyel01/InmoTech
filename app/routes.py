

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from app.auth import (
    login_user, logout_user, is_authenticated,
    current_user, role_required,
    generate_csrf_token, validate_csrf,
    ROL_VENDEDOR, ROL_COMPRADOR
)
from app.services import UsuarioService, InmuebleService, VisitaService
from app.repositories import UbicacionCategoriaRepository

routes_bp = Blueprint('routes', __name__)


@routes_bp.context_processor
def inject_global_template_data():
    return {
        'current_user': current_user(),
        'is_authenticated': is_authenticated(),
        'csrf_token': generate_csrf_token(),
        'ROL_VENDEDOR': ROL_VENDEDOR,
        'ROL_COMPRADOR': ROL_COMPRADOR
    }


# Inicio
@routes_bp.route('/')
def index():
    destacados = InmuebleService.obtener_destacados(limite=6)
    categorias = UbicacionCategoriaRepository.get_categorias()
    ciudades = UbicacionCategoriaRepository.get_ciudades()
    return render_template(
        'index.html',
        destacados=destacados,
        categorias=categorias,
        ciudades=ciudades
    )


# Catálogo y Búsqueda con Filtros
@routes_bp.route('/catalogo')
def catalog():
    filtros = request.args.to_dict()
    inmuebles = InmuebleService.obtener_catalogo(filtros)
    ciudades = UbicacionCategoriaRepository.get_ciudades()
    categorias = UbicacionCategoriaRepository.get_categorias()
    return render_template(
        'catalog.html',
        inmuebles=inmuebles,
        ciudades=ciudades,
        categorias=categorias,
        filtros=filtros
    )


@routes_bp.route('/inmuebles/<int:id_inmueble>')
def property_detail(id_inmueble):
    try:
        inmueble = InmuebleService.obtener_detalle(id_inmueble)
        return render_template('property_detail.html', inmueble=inmueble)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('routes.catalog'))


@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if is_authenticated():
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        validate_csrf()
        correo = request.form.get('correo')
        password = request.form.get('password')
        next_url = request.args.get('next')

        try:
            usuario = UsuarioService.autenticar(correo, password)
            login_user(usuario)
            flash(f"¡Bienvenido de nuevo, {usuario['nombre']}!", 'success')

            # Redirección inteligente según el rol si no hay next específico
            # Solo rutas internas: "//otro-sitio.com" también empieza por "/"
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)

            if usuario['rol_nombre'] == ROL_VENDEDOR:
                return redirect(url_for('routes.seller_properties'))
            elif usuario['rol_nombre'] == ROL_COMPRADOR:
                return redirect(url_for('routes.catalog'))
            return redirect(url_for('routes.index'))

        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('login.html')


@routes_bp.route('/registro', methods=['GET', 'POST'])
def register():
    if is_authenticated():
        return redirect(url_for('routes.index'))

    form_data = {}
    if request.method == 'POST':
        validate_csrf()
        form_data = request.form.to_dict()

        try:
            UsuarioService.registrar_comprador(
                nombre=request.form.get('nombre'),
                apellido=request.form.get('apellido'),
                correo=request.form.get('correo'),
                telefono=request.form.get('telefono'),
                password=request.form.get('password'),
                confirm_password=request.form.get('confirm_password')
            )
            flash("¡Registro exitoso! Tu cuenta de comprador ha sido creada. Ya puedes iniciar sesión.", 'success')
            return redirect(url_for('routes.login'))

        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('register.html', form_data=form_data)


@routes_bp.route('/logout')
def logout():
    logout_user()
    flash("Has cerrado sesión exitosamente.", 'info')
    return redirect(url_for('routes.index'))


@routes_bp.route('/inmuebles/nuevo', methods=['GET', 'POST'])
@role_required(ROL_VENDEDOR)
def create_property():
    if request.method == 'POST':
        validate_csrf()
        id_vendedor = session['user_id']
        try:
            InmuebleService.publicar_inmueble(id_vendedor, request.form)
            flash("Inmueble publicado con éxito.", 'success')
            return redirect(url_for('routes.seller_properties'))
        except (ValueError, PermissionError) as e:
            flash(str(e), 'danger')

    departamentos = UbicacionCategoriaRepository.get_departamentos()
    ciudades = UbicacionCategoriaRepository.get_ciudades()
    categorias = UbicacionCategoriaRepository.get_categorias()
    return render_template(
        'property_form.html',
        modo='crear',
        inmueble=request.form.to_dict() if request.method == 'POST' else None,
        departamentos=departamentos,
        ciudades=ciudades,
        categorias=categorias
    )


@routes_bp.route('/inmuebles/<int:id_inmueble>/editar', methods=['GET', 'POST'])
@role_required(ROL_VENDEDOR)
def edit_property(id_inmueble):
    id_vendedor = session['user_id']
    try:
        inmueble_actual = InmuebleService.obtener_detalle(id_inmueble)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('routes.seller_properties'))

    if inmueble_actual['id_vendedor'] != id_vendedor:
        flash("No tienes permisos para modificar este inmueble.", 'danger')
        return redirect(url_for('routes.seller_properties'))

    if request.method == 'POST':
        validate_csrf()
        try:
            InmuebleService.editar_inmueble(id_inmueble, id_vendedor, request.form)
            flash("Inmueble actualizado exitosamente.", 'success')
            return redirect(url_for('routes.seller_properties'))
        except (ValueError, PermissionError) as e:
            flash(str(e), 'danger')

    departamentos = UbicacionCategoriaRepository.get_departamentos()
    ciudades = UbicacionCategoriaRepository.get_ciudades()
    categorias = UbicacionCategoriaRepository.get_categorias()
    return render_template(
        'property_form.html',
        modo='editar',
        inmueble=inmueble_actual,
        departamentos=departamentos,
        ciudades=ciudades,
        categorias=categorias
    )


@routes_bp.route('/inmuebles/<int:id_inmueble>/cambiar-estado', methods=['POST'])
@role_required(ROL_VENDEDOR)
def toggle_property_status(id_inmueble):
    validate_csrf()
    id_vendedor = session['user_id']
    nuevo_estado = request.form.get('estado')
    try:
        InmuebleService.cambiar_disponibilidad(id_inmueble, id_vendedor, nuevo_estado)
        flash(f"El estado del inmueble ha sido actualizado a {nuevo_estado}.", 'success')
    except (ValueError, PermissionError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('routes.seller_properties'))


@routes_bp.route('/mis-inmuebles')
@role_required(ROL_VENDEDOR)
def seller_properties():
    id_vendedor = session['user_id']
    inmuebles = InmuebleService.listar_inmuebles_vendedor(id_vendedor)
    return render_template('seller_properties.html', inmuebles=inmuebles)


# Solicitud de Visita (Solo COMPRADOR)
@routes_bp.route('/inmuebles/<int:id_inmueble>/solicitar-visita', methods=['GET', 'POST'])
@role_required(ROL_COMPRADOR)
def request_visit(id_inmueble):
    try:
        inmueble = InmuebleService.obtener_detalle(id_inmueble)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('routes.catalog'))

    if inmueble['estado'] != 'DISPONIBLE':
        flash("Este inmueble ya no se encuentra disponible para agendar visitas.", 'warning')
        return redirect(url_for('routes.property_detail', id_inmueble=id_inmueble))

    if request.method == 'POST':
        validate_csrf()
        id_comprador = session['user_id']
        fecha_visita = request.form.get('fecha_visita')
        mensaje = request.form.get('mensaje')

        try:
            VisitaService.solicitar_visita(id_comprador, id_inmueble, fecha_visita, mensaje)
            flash("¡Solicitud de visita enviada con éxito! El vendedor revisará tu propuesta.", 'success')
            return redirect(url_for('routes.my_visits'))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('visit_form.html', inmueble=inmueble)


@routes_bp.route('/mis-visitas')
@role_required(ROL_COMPRADOR)
def my_visits():
    id_comprador = session['user_id']
    visitas = VisitaService.listar_visitas_comprador(id_comprador)
    return render_template('my_visits.html', visitas=visitas)


@routes_bp.route('/mis-visitas/<int:id_visita>/cancelar', methods=['POST'])
@role_required(ROL_COMPRADOR)
def cancel_visit(id_visita):
    validate_csrf()
    id_comprador = session['user_id']
    try:
        VisitaService.cancelar_visita_comprador(id_visita, id_comprador)
        flash("La solicitud de visita ha sido cancelada correctamente.", 'info')
    except (ValueError, PermissionError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('routes.my_visits'))


@routes_bp.route('/visitas-recibidas')
@role_required(ROL_VENDEDOR)
def seller_visits():
    id_vendedor = session['user_id']
    visitas = VisitaService.listar_visitas_vendedor(id_vendedor)
    return render_template('seller_visits.html', visitas=visitas)


@routes_bp.route('/visitas-recibidas/<int:id_visita>/cambiar-estado', methods=['POST'])
@role_required(ROL_VENDEDOR)
def update_visit_status(id_visita):
    validate_csrf()
    id_vendedor = session['user_id']
    nuevo_estado = request.form.get('estado')
    try:
        VisitaService.actualizar_estado_visita_vendedor(id_visita, id_vendedor, nuevo_estado)
        flash(f"La visita ha sido actualizada al estado: {nuevo_estado}.", 'success')
    except (ValueError, PermissionError) as e:
        flash(str(e), 'danger')
    return redirect(url_for('routes.seller_visits'))


@routes_bp.route('/api/ciudades/<int:id_departamento>')
def get_ciudades_by_departamento(id_departamento):
    ciudades = UbicacionCategoriaRepository.get_ciudades(id_departamento=id_departamento)
    return jsonify(ciudades)
