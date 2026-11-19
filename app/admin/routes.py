"""
Rutas del panel de administración.

Seguridad en un solo lugar: antes de CUALQUIER ruta del blueprint se exige sesión
iniciada y rol ADMINISTRADOR, y en todo POST se valida el token CSRF. Así una
ruta nueva queda protegida sin tener que acordarse de decorarla.
"""

from datetime import date

from flask import (
    Response, flash, redirect, render_template, request, session, url_for
)

from app.admin import admin_bp
from app.admin.services import (
    CatalogoService, DashboardService, InmuebleAdminService, UsuarioAdminService,
    VisitaAdminService, ESTADOS_INMUEBLE, ESTADOS_VISITA, OPERACIONES
)
from app.auth import ROL_ADMINISTRADOR, is_authenticated, validate_csrf
from app.repositories import UbicacionCategoriaRepository


@admin_bp.before_request
def exigir_administrador():
    if not is_authenticated():
        flash('Debes iniciar sesión para entrar al panel de administración.', 'warning')
        return redirect(url_for('routes.login', next=request.path))
    if session.get('rol_nombre') != ROL_ADMINISTRADOR:
        flash('Esta sección es solo para administradores.', 'danger')
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        validate_csrf()


def _volver(por_defecto):
    """Regresa a la lista de donde se hizo la acción, con sus filtros y su página."""
    destino = request.form.get('volver', '')
    if destino.startswith('/admin') and not destino.startswith('//'):
        return redirect(destino)
    return redirect(por_defecto)


def _descargar_csv(contenido, nombre):
    return Response(
        contenido,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={nombre}-{date.today():%Y-%m-%d}.csv'}
    )


# ------------------------------------------------------------------------------
# Tablero
# ------------------------------------------------------------------------------
@admin_bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html', seccion='resumen', datos=DashboardService.obtener())


# ------------------------------------------------------------------------------
# Usuarios
# ------------------------------------------------------------------------------
@admin_bp.route('/usuarios')
def usuarios():
    filas, pagina, filtros = UsuarioAdminService.listar(request.args)
    return render_template(
        'admin/usuarios.html', seccion='usuarios', usuarios=filas, pagina=pagina, filtros=filtros,
        roles=UsuarioAdminService.roles()
    )


@admin_bp.route('/usuarios/exportar.csv')
def usuarios_exportar():
    return _descargar_csv(UsuarioAdminService.exportar(request.args), 'usuarios')


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
def usuario_nuevo():
    if request.method == 'POST':
        try:
            UsuarioAdminService.crear(request.form)
            flash('Usuario creado.', 'success')
            return redirect(url_for('admin.usuarios'))
        except ValueError as error:
            flash(str(error), 'danger')
    return render_template(
        'admin/usuario_form.html', seccion='usuarios', modo='crear',
        usuario=request.form.to_dict() if request.method == 'POST' else None,
        roles=UsuarioAdminService.roles()
    )


@admin_bp.route('/usuarios/<int:id_usuario>/editar', methods=['GET', 'POST'])
def usuario_editar(id_usuario):
    try:
        usuario = UsuarioAdminService.obtener(id_usuario)
    except ValueError as error:
        flash(str(error), 'danger')
        return redirect(url_for('admin.usuarios'))

    if request.method == 'POST':
        try:
            UsuarioAdminService.editar(id_usuario, request.form, session['user_id'])
            flash('Datos del usuario actualizados.', 'success')
            return redirect(url_for('admin.usuarios'))
        except ValueError as error:
            flash(str(error), 'danger')
            usuario = {**usuario, **request.form.to_dict(), 'rol_nombre': request.form.get('rol', usuario['rol_nombre'])}

    return render_template(
        'admin/usuario_form.html', seccion='usuarios', modo='editar', usuario=usuario,
        roles=UsuarioAdminService.roles()
    )


@admin_bp.route('/usuarios/<int:id_usuario>/estado', methods=['POST'])
def usuario_estado(id_usuario):
    activar = request.form.get('activo') == '1'
    try:
        usuario = UsuarioAdminService.cambiar_estado(id_usuario, activar, session['user_id'])
        accion = 'reactivada' if activar else 'bloqueada'
        flash(f"La cuenta de {usuario['nombre']} {usuario['apellido']} fue {accion}.", 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return _volver(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:id_usuario>/password', methods=['POST'])
def usuario_password(id_usuario):
    try:
        usuario = UsuarioAdminService.restablecer_password(
            id_usuario, request.form.get('password'), request.form.get('confirm_password'))
        flash(f"Nueva contraseña guardada para {usuario['nombre']} {usuario['apellido']}.", 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return redirect(url_for('admin.usuario_editar', id_usuario=id_usuario))


@admin_bp.route('/usuarios/<int:id_usuario>/eliminar', methods=['POST'])
def usuario_eliminar(id_usuario):
    try:
        usuario = UsuarioAdminService.eliminar(id_usuario, session['user_id'])
        flash(f"Se eliminó la cuenta de {usuario['nombre']} {usuario['apellido']}.", 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return _volver(url_for('admin.usuarios'))


# ------------------------------------------------------------------------------
# Inmuebles
# ------------------------------------------------------------------------------
@admin_bp.route('/inmuebles')
def inmuebles():
    filas, pagina, filtros = InmuebleAdminService.listar(request.args)
    return render_template(
        'admin/inmuebles.html', seccion='inmuebles', inmuebles=filas, pagina=pagina, filtros=filtros,
        opciones=InmuebleAdminService.opciones_filtro(), estados=ESTADOS_INMUEBLE, operaciones=OPERACIONES
    )


@admin_bp.route('/inmuebles/exportar.csv')
def inmuebles_exportar():
    return _descargar_csv(InmuebleAdminService.exportar(request.args), 'inmuebles')


@admin_bp.route('/inmuebles/<int:id_inmueble>/editar', methods=['GET', 'POST'])
def inmueble_editar(id_inmueble):
    try:
        inmueble = InmuebleAdminService.obtener(id_inmueble)
    except ValueError as error:
        flash(str(error), 'danger')
        return redirect(url_for('admin.inmuebles'))

    if request.method == 'POST':
        try:
            InmuebleAdminService.editar(
                id_inmueble, request.form, request.files.getlist('fotos'),
                request.form.getlist('quitar_fotos'), request.form.get('portada'))
            flash('Inmueble actualizado.', 'success')
            return redirect(url_for('admin.inmuebles'))
        except (ValueError, PermissionError) as error:
            flash(str(error), 'danger')

    return render_template(
        'property_form.html', seccion='inmuebles', modo='editar', inmueble=inmueble,
        imagenes=InmuebleAdminService.obtener_imagenes(id_inmueble),
        departamentos=UbicacionCategoriaRepository.get_departamentos(),
        ciudades=UbicacionCategoriaRepository.get_ciudades(),
        categorias=UbicacionCategoriaRepository.get_categorias(),
        accion_url=url_for('admin.inmueble_editar', id_inmueble=id_inmueble),
        volver_url=url_for('admin.inmuebles'), volver_texto='Volver a Inmuebles',
        titulo_admin=f"Editar inmueble de {inmueble['vendedor_nombre']}"
    )


@admin_bp.route('/inmuebles/<int:id_inmueble>/estado', methods=['POST'])
def inmueble_estado(id_inmueble):
    nuevo = request.form.get('estado')
    try:
        inmueble = InmuebleAdminService.cambiar_estado(id_inmueble, nuevo)
        accion = 'se publicó de nuevo' if nuevo == 'DISPONIBLE' else 'se pausó'
        flash(f"«{inmueble['titulo']}» {accion}.", 'success')
    except (ValueError, PermissionError) as error:
        flash(str(error), 'danger')
    return _volver(url_for('admin.inmuebles'))


@admin_bp.route('/inmuebles/<int:id_inmueble>/eliminar', methods=['POST'])
def inmueble_eliminar(id_inmueble):
    try:
        inmueble = InmuebleAdminService.eliminar(id_inmueble)
        flash(f"Se eliminó «{inmueble['titulo']}».", 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return _volver(url_for('admin.inmuebles'))


# ------------------------------------------------------------------------------
# Visitas
# ------------------------------------------------------------------------------
@admin_bp.route('/visitas')
def visitas():
    filas, pagina, filtros = VisitaAdminService.listar(request.args)
    return render_template(
        'admin/visitas.html', seccion='visitas', visitas=filas, pagina=pagina, filtros=filtros,
        estados=ESTADOS_VISITA
    )


@admin_bp.route('/visitas/exportar.csv')
def visitas_exportar():
    return _descargar_csv(VisitaAdminService.exportar(request.args), 'visitas')


@admin_bp.route('/visitas/<int:id_visita>/estado', methods=['POST'])
def visita_estado(id_visita):
    nuevo = request.form.get('estado')
    try:
        VisitaAdminService.cambiar_estado(id_visita, nuevo)
        flash(f'La visita pasó a {nuevo.lower()}.', 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return _volver(url_for('admin.visitas'))


# ------------------------------------------------------------------------------
# Catálogos
# ------------------------------------------------------------------------------
@admin_bp.route('/catalogos')
def catalogos():
    return render_template('admin/catalogos.html', seccion='catalogos', **CatalogoService.obtener_todo())


@admin_bp.route('/catalogos/<entidad>/nuevo', methods=['POST'])
def catalogo_crear(entidad):
    try:
        nombre = CatalogoService.crear(entidad, request.form)
        flash(f'Se agregó «{nombre}».', 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return redirect(url_for('admin.catalogos', _anchor=entidad))


@admin_bp.route('/catalogos/<entidad>/<int:id_>/editar', methods=['POST'])
def catalogo_editar(entidad, id_):
    try:
        nombre = CatalogoService.renombrar(entidad, id_, request.form)
        flash(f'Se guardó «{nombre}».', 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return redirect(url_for('admin.catalogos', _anchor=entidad))


@admin_bp.route('/catalogos/<entidad>/<int:id_>/eliminar', methods=['POST'])
def catalogo_eliminar(entidad, id_):
    try:
        CatalogoService.eliminar(entidad, id_)
        flash('Elemento eliminado.', 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return redirect(url_for('admin.catalogos', _anchor=entidad))
