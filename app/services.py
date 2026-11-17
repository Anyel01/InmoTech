

import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories import (
    UsuarioRepository,
    InmuebleRepository,
    VisitaRepository,
    UbicacionCategoriaRepository
)

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app, url_for
from flask_mail import Message

class UsuarioService:


    EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    @classmethod
    def registrar_comprador(cls, nombre, apellido, correo, telefono, password, confirm_password):

        nombre = (nombre or '').strip()
        apellido = (apellido or '').strip()
        correo = (correo or '').strip().lower()
        telefono = (telefono or '').strip()
        password = password or ''
        confirm_password = confirm_password or ''

        if not nombre or not apellido or not correo or not telefono or not password:
            raise ValueError("Todos los campos del formulario son obligatorios.")

        if not re.match(cls.EMAIL_REGEX, correo):
            raise ValueError("El formato del correo electrónico no es válido.")

        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")

        if password != confirm_password:
            raise ValueError("Las contraseñas ingresadas no coinciden.")

        usuario_existente = UsuarioRepository.find_by_correo(correo)
        if usuario_existente:
            raise ValueError("Ya existe una cuenta registrada con este correo electrónico.")

        password_hash = generate_password_hash(password)

        nuevo_id = UsuarioRepository.create_comprador(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=password_hash,
            telefono=telefono
        )
        return nuevo_id

    @classmethod
    def autenticar(cls, correo, password):

        correo = (correo or '').strip().lower()
        password = password or ''

        if not correo or not password:
            raise ValueError("Debe ingresar correo electrónico y contraseña.")

        usuario = UsuarioRepository.find_by_correo(correo)
        if not usuario:
            raise ValueError("Credenciales inválidas. Verifique su correo y contraseña.")

        if not check_password_hash(usuario['password_hash'], password):
            raise ValueError("Credenciales inválidas. Verifique su correo y contraseña.")

        return usuario
    
    @classmethod
    def generar_token_recuperacion(cls, correo):

        correo = (correo or '').strip().lower()

        usuario = UsuarioRepository.find_id_by_correo(correo)

        if not usuario:
            return None

        serializer = URLSafeTimedSerializer(
            current_app.config['SECRET_KEY']
        )

        token = serializer.dumps(
            usuario['id_usuario'],
            salt='recuperacion-password'
        )

        enlace = url_for(
            'routes.restablecer_password',
            token=token,
            _external=True
        )

        mail = current_app.extensions['mail']

        mensaje = Message(
            subject='Recuperación de contraseña - InmoTech',
            recipients=[correo]
        )

        mensaje.body = f"""
    Hola,

    Hemos recibido una solicitud para restablecer tu contraseña.

    Ingresa al siguiente enlace:

    {enlace}

    Este enlace tiene una validez de 15 minutos.

    Si no solicitaste este cambio, ignora este correo.

    Equipo InmoTech.
    """

        mail.send(mensaje)

        return True


    @classmethod
    def restablecer_password(cls, token, nueva_password, confirmar_password):

        if not nueva_password or not confirmar_password:
            raise ValueError("Todos los campos son obligatorios.")

        if len(nueva_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")

        if nueva_password != confirmar_password:
            raise ValueError("Las contraseñas no coinciden.")

        serializer = URLSafeTimedSerializer(
            current_app.config['SECRET_KEY']
        )

        try:
            id_usuario = serializer.loads(
                token,
                salt='recuperacion-password',
                max_age=900
            )

        except SignatureExpired:
            raise ValueError("El enlace ha expirado. Solicita uno nuevo.")

        except BadSignature:
            raise ValueError("El enlace no es válido.")

        password_hash = generate_password_hash(nueva_password)

        UsuarioRepository.update_password(
            id_usuario,
            password_hash
        )


class InmuebleService:


    OPERACIONES_VALIDAS = {'VENTA', 'ARRIENDO'}
    ESTADOS_VALIDOS = {'DISPONIBLE', 'NO_DISPONIBLE'}

    @classmethod
    def obtener_catalogo(cls, filtros_raw):

        filtros = {}

        if filtros_raw.get('ciudad'):
            try:
                filtros['id_ciudad'] = int(filtros_raw['ciudad'])
            except ValueError:
                pass

        if filtros_raw.get('categoria'):
            try:
                filtros['id_categoria'] = int(filtros_raw['categoria'])
            except ValueError:
                pass

        operacion = filtros_raw.get('operacion')
        if operacion in cls.OPERACIONES_VALIDAS:
            filtros['operacion'] = operacion

        if filtros_raw.get('precio_min'):
            try:
                p_min = float(filtros_raw['precio_min'])
                if p_min >= 0:
                    filtros['precio_min'] = p_min
            except ValueError:
                pass

        if filtros_raw.get('precio_max'):
            try:
                p_max = float(filtros_raw['precio_max'])
                if p_max >= 0:
                    filtros['precio_max'] = p_max
            except ValueError:
                pass

        if filtros_raw.get('habitaciones_min'):
            try:
                hab = int(filtros_raw['habitaciones_min'])
                if hab >= 0:
                    filtros['habitaciones_min'] = hab
            except ValueError:
                pass

        return InmuebleRepository.find_all_disponibles(filtros)

    @classmethod
    def obtener_destacados(cls, limite=6):
        return InmuebleRepository.find_destacados(limite)

    @classmethod
    def obtener_detalle(cls, id_inmueble):
        inmueble = InmuebleRepository.find_by_id(id_inmueble)
        if not inmueble:
            raise ValueError("El inmueble solicitado no existe.")
        return inmueble

    @classmethod
    def listar_inmuebles_vendedor(cls, id_vendedor):
        return InmuebleRepository.find_by_vendedor(id_vendedor)

    @classmethod
    def validar_y_estructurar_datos(cls, form_data):

        titulo = (form_data.get('titulo') or '').strip()
        descripcion = (form_data.get('descripcion') or '').strip()
        direccion = (form_data.get('direccion') or '').strip()
        operacion = form_data.get('operacion')

        if not titulo or len(titulo) > 200:
            raise ValueError("El título es obligatorio y no puede exceder 200 caracteres.")

        if not descripcion:
            raise ValueError("La descripción es obligatoria.")

        if not direccion or len(direccion) > 200:
            raise ValueError("La dirección es obligatoria y no puede exceder 200 caracteres.")

        if operacion not in cls.OPERACIONES_VALIDAS:
            raise ValueError("La operación seleccionada no es válida (debe ser VENTA o ARRIENDO).")

        try:
            precio = float(form_data.get('precio', 0))
            if precio <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("El precio debe ser un número positivo mayor a cero.")

        try:
            area = float(form_data.get('area', 0))
            if area <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("El área debe ser un número positivo en metros cuadrados.")

        try:
            habitaciones = int(form_data.get('habitaciones', 0))
            if habitaciones < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("El número de habitaciones no puede ser negativo.")

        try:
            banos = int(form_data.get('banos', 0))
            if banos < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("El número de baños no puede ser negativo.")

        try:
            id_categoria = int(form_data.get('id_categoria'))
            id_ciudad = int(form_data.get('id_ciudad'))
        except (ValueError, TypeError):
            raise ValueError("Debe seleccionar una categoría y una ciudad válidas.")

        return {
            'titulo': titulo,
            'descripcion': descripcion,
            'direccion': direccion,
            'precio': precio,
            'area': area,
            'habitaciones': habitaciones,
            'banos': banos,
            'operacion': operacion,
            'id_categoria': id_categoria,
            'id_ciudad': id_ciudad
        }

    @classmethod
    def publicar_inmueble(cls, id_vendedor, form_data):
        datos = cls.validar_y_estructurar_datos(form_data)
        datos['id_vendedor'] = id_vendedor
        datos['estado'] = 'DISPONIBLE'
        return InmuebleRepository.create(datos)

    @classmethod
    def editar_inmueble(cls, id_inmueble, id_vendedor, form_data):
        inmueble = InmuebleRepository.find_by_id(id_inmueble)
        if not inmueble:
            raise ValueError("El inmueble a editar no existe.")

        if inmueble['id_vendedor'] != id_vendedor:
            raise PermissionError("No tienes permisos para modificar este inmueble.")

        datos = cls.validar_y_estructurar_datos(form_data)
        return InmuebleRepository.update(id_inmueble, datos)

    @classmethod
    def cambiar_disponibilidad(cls, id_inmueble, id_vendedor, nuevo_estado):
        if nuevo_estado not in cls.ESTADOS_VALIDOS:
            raise ValueError("Estado no válido.")

        inmueble = InmuebleRepository.find_by_id(id_inmueble)
        if not inmueble:
            raise ValueError("El inmueble no existe.")

        if inmueble['id_vendedor'] != id_vendedor:
            raise PermissionError("No tienes permisos para modificar la disponibilidad de este inmueble.")

        return InmuebleRepository.update_estado(id_inmueble, nuevo_estado)


class VisitaService:


    ESTADOS_VALIDOS = {'PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'REALIZADA'}

    @classmethod
    def solicitar_visita(cls, id_comprador, id_inmueble, fecha_visita_str, mensaje):
        inmueble = InmuebleRepository.find_by_id(id_inmueble)
        if not inmueble:
            raise ValueError("El inmueble solicitado no existe.")

        if inmueble['estado'] != 'DISPONIBLE':
            raise ValueError("No se pueden solicitar visitas para inmuebles no disponibles.")

        if inmueble['id_vendedor'] == id_comprador:
            raise ValueError("Un vendedor no puede solicitar visitas a sus propias publicaciones.")

        if not fecha_visita_str:
            raise ValueError("Debe especificar la fecha y hora deseada para la visita.")

        try:
            fecha_limpia = fecha_visita_str.replace('T', ' ')
            if len(fecha_limpia) == 16:
                fecha_limpia += ':00'
            fecha_dt = datetime.strptime(fecha_limpia, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("El formato de fecha y hora ingresado es incorrecto.")

        if fecha_dt <= datetime.now():
            raise ValueError("La fecha y hora de la visita debe ser futura.")

        datos = {
            'fecha_visita': fecha_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'mensaje': (mensaje or '').strip(),
            'id_inmueble': id_inmueble,
            'id_comprador': id_comprador
        }
        return VisitaRepository.create(datos)

    @classmethod
    def listar_visitas_comprador(cls, id_comprador):
        return VisitaRepository.find_by_comprador(id_comprador)

    @classmethod
    def cancelar_visita_comprador(cls, id_visita, id_comprador):
        visita = VisitaRepository.find_by_id(id_visita)
        if not visita:
            raise ValueError("La solicitud de visita no existe.")

        if visita['id_comprador'] != id_comprador:
            raise PermissionError("No tienes permiso para gestionar esta solicitud.")

        if visita['estado'] != 'PENDIENTE':
            raise ValueError(f"Solo se pueden cancelar visitas en estado PENDIENTE (estado actual: {visita['estado']}).")

        return VisitaRepository.update_estado(id_visita, 'CANCELADA')

    @classmethod
    def listar_visitas_vendedor(cls, id_vendedor):
        return VisitaRepository.find_by_vendedor(id_vendedor)

    @classmethod
    def actualizar_estado_visita_vendedor(cls, id_visita, id_vendedor, nuevo_estado):
        if nuevo_estado not in cls.ESTADOS_VALIDOS:
            raise ValueError("Estado de visita no válido.")

        visita = VisitaRepository.find_by_id(id_visita)
        if not visita:
            raise ValueError("La visita no existe.")

        if visita['id_vendedor'] != id_vendedor:
            raise PermissionError("No tienes permiso para gestionar las visitas de este inmueble.")

        # Validar transiciones de estado
        estado_actual = visita['estado']
        if estado_actual in ('CANCELADA', 'REALIZADA'):
            raise ValueError(f"No es posible modificar una visita que ya se encuentra {estado_actual}.")

        return VisitaRepository.update_estado(id_visita, nuevo_estado)
