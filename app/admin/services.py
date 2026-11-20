

import csv
import io
import re
from datetime import datetime

from werkzeug.security import generate_password_hash

from app.admin.repositories import (
    AdminInmuebleRepository,
    AdminUsuarioRepository,
    AdminVisitaRepository,
    CatalogoRepository,
    EstadisticasRepository,
)
from app.auth import ROL_ADMINISTRADOR, ROL_COMPRADOR, ROL_VENDEDOR
from app.repositories import ImagenRepository, InmuebleRepository, UbicacionCategoriaRepository
from app.services import ImagenService, InmuebleService

ROLES = (ROL_ADMINISTRADOR, ROL_VENDEDOR, ROL_COMPRADOR)
ESTADOS_VISITA = ('PENDIENTE', 'CONFIRMADA', 'REALIZADA', 'CANCELADA')
ESTADOS_INMUEBLE = ('DISPONIBLE', 'NO_DISPONIBLE')
OPERACIONES = ('VENTA', 'ARRIENDO')
POR_PAGINA = 15
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


def numero_o_none(valor):
    try:
        numero = int(valor)
        return numero if numero > 0 else None
    except (TypeError, ValueError):
        return None


def fecha_o_none(valor):
    try:
        return datetime.strptime(valor, '%Y-%m-%d').strftime('%Y-%m-%d')
    except (TypeError, ValueError):
        return None


def paginar(total, pagina, por_pagina=POR_PAGINA):
    """Datos para dibujar el paginador. Corrige páginas fuera de rango."""
    paginas = max(1, -(-total // por_pagina))
    pagina = min(max(numero_o_none(pagina) or 1, 1), paginas)
    return {
        'pagina': pagina,
        'paginas': paginas,
        'total': total,
        'por_pagina': por_pagina,
        'desde': 0 if total == 0 else (pagina - 1) * por_pagina + 1,
        'hasta': min(pagina * por_pagina, total),
    }


def _celda_csv(valor):
    """
    Excel interpreta como fórmula un texto que empiece por = + - @ (inyección de
    fórmulas, p. ej. un nombre de usuario "=HYPERLINK(...)"). Se le antepone una
    comilla para que se lea como texto.
    """
    if valor is None:
        return ''
    if isinstance(valor, str) and valor[:1] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + valor
    return valor


def a_csv(columnas, filas):
    """
    Genera un CSV listo para abrir en Excel: separador ";" y BOM UTF-8 para que
    se vean bien las tildes. `columnas` = [(encabezado, clave), ...]
    """
    salida = io.StringIO()
    escritor = csv.writer(salida, delimiter=';')
    escritor.writerow([encabezado for encabezado, _ in columnas])
    for fila in filas:
        escritor.writerow([_celda_csv(fila.get(clave)) for _, clave in columnas])
    return '﻿' + salida.getvalue()



class DashboardService:

    @staticmethod
    def _contar(filas, clave, valor):
        return next((f['total'] for f in filas if f[clave] == valor), 0)

    @classmethod
    def obtener(cls):
        datos = EstadisticasRepository.resumen()

        por_rol = {f['rol']: f['total'] for f in datos['usuarios_por_rol']}
        total_usuarios = sum(por_rol.values())
        estados = datos['inmuebles_por_estado']
        disponibles = cls._contar(estados, 'estado', 'DISPONIBLE')
        pausados = cls._contar(estados, 'estado', 'NO_DISPONIBLE')

        visitas = {estado: cls._contar(datos['visitas_por_estado'], 'estado', estado) for estado in ESTADOS_VISITA}
        total_visitas = sum(visitas.values())

        return {
            'usuarios': {
                'total': total_usuarios,
                'por_rol': por_rol,
                'bloqueados': datos['usuarios_bloqueados'],
            },
            'inmuebles': {
                'total': disponibles + pausados,
                'disponibles': disponibles,
                'pausados': pausados,
                'sin_fotos': datos['inmuebles_sin_fotos'],
                'venta': cls._contar(datos['disponibles_por_operacion'], 'operacion', 'VENTA'),
                'arriendo': cls._contar(datos['disponibles_por_operacion'], 'operacion', 'ARRIENDO'),
            },
            'visitas': {
                'total': total_visitas,
                'por_estado': [
                    {
                        'estado': estado,
                        'total': visitas[estado],
                        'porcentaje': round(visitas[estado] * 100 / total_visitas) if total_visitas else 0,
                    }
                    for estado in ESTADOS_VISITA
                ],
            },
            'categorias': cls._con_porcentaje(datos['disponibles_por_categoria']),
            'ciudades': cls._con_porcentaje(datos['disponibles_por_ciudad']),
            'mas_visitados': datos['inmuebles_mas_visitados'],
            'ultimas_visitas': datos['ultimas_visitas'],
            'ultimos_usuarios': datos['ultimos_usuarios'],
        }

    @staticmethod
    def _con_porcentaje(filas):
        """Agrega 'ancho' (0-100) a cada fila, relativo a la mayor, para dibujar las barras."""
        mayor = max((f['total'] for f in filas), default=0)
        return [{**f, 'ancho': round(f['total'] * 100 / mayor) if mayor else 0} for f in filas]



class UsuarioAdminService:

    @staticmethod
    def filtros(args):
        rol = args.get('rol')
        estado = args.get('estado')
        return {
            'q': (args.get('q') or '').strip()[:80],
            'rol': rol if rol in ROLES else '',
            'estado': estado if estado in ('activos', 'bloqueados') else '',
        }

    @classmethod
    def listar(cls, args):
        filtros = cls.filtros(args)
        _, total = AdminUsuarioRepository.listar(filtros, 1, 1)
        pagina = paginar(total, args.get('pagina'))
        filas, _ = AdminUsuarioRepository.listar(filtros, pagina['pagina'], POR_PAGINA)
        return filas, pagina, filtros

    @classmethod
    def exportar(cls, args):
        filas, _ = AdminUsuarioRepository.listar(cls.filtros(args))
        for fila in filas:
            fila['estado_cuenta'] = 'Activa' if fila['activo'] else 'Bloqueada'
        return a_csv([
            ('ID', 'id_usuario'), ('Nombre', 'nombre'), ('Apellido', 'apellido'), ('Correo', 'correo'),
            ('Teléfono', 'telefono'), ('Rol', 'rol_nombre'), ('Cuenta', 'estado_cuenta'),
            ('Inmuebles publicados', 'total_inmuebles'), ('Visitas solicitadas', 'total_visitas'),
        ], filas)

    @staticmethod
    def obtener(id_usuario):
        usuario = AdminUsuarioRepository.find_by_id(id_usuario)
        if not usuario:
            raise ValueError("El usuario no existe.")
        return usuario

    @staticmethod
    def roles():
        return [r['nombre'] for r in AdminUsuarioRepository.listar_roles()]

    @classmethod
    def _validar_datos(cls, form, excepto_id=None):
        nombre = (form.get('nombre') or '').strip()
        apellido = (form.get('apellido') or '').strip()
        correo = (form.get('correo') or '').strip().lower()
        telefono = (form.get('telefono') or '').strip()
        rol = form.get('rol')

        if not nombre or not apellido or not telefono:
            raise ValueError("Nombre, apellido y teléfono son obligatorios.")
        if len(nombre) > 100 or len(apellido) > 100:
            raise ValueError("El nombre y el apellido no pueden superar 100 caracteres.")
        if len(telefono) > 20:
            raise ValueError("El teléfono no puede superar 20 caracteres.")
        if not re.match(EMAIL_REGEX, correo) or len(correo) > 150:
            raise ValueError("El formato del correo electrónico no es válido.")
        if rol not in ROLES:
            raise ValueError("Elige un rol válido.")
        if AdminUsuarioRepository.correo_en_uso(correo, excepto_id):
            raise ValueError("Ya existe una cuenta con ese correo electrónico.")
        return nombre, apellido, correo, telefono, rol

    @staticmethod
    def _validar_password(password, confirmar):
        if len(password or '') < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if password != confirmar:
            raise ValueError("Las contraseñas no coinciden.")

    @classmethod
    def crear(cls, form):
        nombre, apellido, correo, telefono, rol = cls._validar_datos(form)
        cls._validar_password(form.get('password'), form.get('confirm_password'))
        return AdminUsuarioRepository.create(
            nombre, apellido, correo, telefono, generate_password_hash(form['password']), rol)

    @classmethod
    def _proteger_ultimo_admin(cls, usuario, accion):
        """No se puede dejar el sistema sin ningún administrador activo."""
        if usuario['rol_nombre'] == ROL_ADMINISTRADOR and usuario['activo']:
            if AdminUsuarioRepository.contar_administradores_activos(excepto_id=usuario['id_usuario']) == 0:
                raise ValueError(f"No puedes {accion} al único administrador activo.")

    @classmethod
    def editar(cls, id_usuario, form, id_admin_actual):
        usuario = cls.obtener(id_usuario)
        nombre, apellido, correo, telefono, rol = cls._validar_datos(form, excepto_id=id_usuario)

        if rol != usuario['rol_nombre']:
            if id_usuario == id_admin_actual:
                raise ValueError("No puedes cambiar tu propio rol. Pídeselo a otro administrador.")
            cls._proteger_ultimo_admin(usuario, "quitarle el rol de administrador")

        AdminUsuarioRepository.update(id_usuario, nombre, apellido, correo, telefono, rol)

    @classmethod
    def cambiar_estado(cls, id_usuario, activo, id_admin_actual):
        usuario = cls.obtener(id_usuario)
        if not activo:
            if id_usuario == id_admin_actual:
                raise ValueError("No puedes bloquear tu propia cuenta.")
            cls._proteger_ultimo_admin(usuario, "bloquear")
        AdminUsuarioRepository.set_activo(id_usuario, activo)
        return usuario

    @classmethod
    def restablecer_password(cls, id_usuario, password, confirmar):
        usuario = cls.obtener(id_usuario)
        cls._validar_password(password, confirmar)
        AdminUsuarioRepository.set_password(id_usuario, generate_password_hash(password))
        return usuario

    @classmethod
    def eliminar(cls, id_usuario, id_admin_actual):
        usuario = cls.obtener(id_usuario)
        if id_usuario == id_admin_actual:
            raise ValueError("No puedes eliminar tu propia cuenta.")
        cls._proteger_ultimo_admin(usuario, "eliminar")
        if usuario['total_inmuebles'] or usuario['total_visitas']:
            raise ValueError(
                "Este usuario tiene inmuebles o visitas registradas y no se puede eliminar. "
                "Puedes bloquear su cuenta para que no vuelva a iniciar sesión.")
        AdminUsuarioRepository.delete(id_usuario)
        return usuario



class InmuebleAdminService:

    @staticmethod
    def filtros(args):
        estado = args.get('estado')
        operacion = args.get('operacion')
        return {
            'q': (args.get('q') or '').strip()[:80],
            'estado': estado if estado in ESTADOS_INMUEBLE else '',
            'operacion': operacion if operacion in OPERACIONES else '',
            'id_categoria': numero_o_none(args.get('id_categoria')),
            'id_ciudad': numero_o_none(args.get('id_ciudad')),
            'id_vendedor': numero_o_none(args.get('id_vendedor')),
        }

    @classmethod
    def listar(cls, args):
        filtros = cls.filtros(args)
        _, total = AdminInmuebleRepository.listar(filtros, 1, 1)
        pagina = paginar(total, args.get('pagina'))
        filas, _ = AdminInmuebleRepository.listar(filtros, pagina['pagina'], POR_PAGINA)
        return filas, pagina, filtros

    @classmethod
    def opciones_filtro(cls):
        return {
            'categorias': UbicacionCategoriaRepository.get_categorias(),
            'ciudades': UbicacionCategoriaRepository.get_ciudades(),
            'vendedores': AdminInmuebleRepository.listar_vendedores(),
        }

    @classmethod
    def exportar(cls, args):
        filas, _ = AdminInmuebleRepository.listar(cls.filtros(args))
        return a_csv([
            ('ID', 'id_inmueble'), ('Título', 'titulo'), ('Categoría', 'categoria'), ('Operación', 'operacion'),
            ('Estado', 'estado'), ('Precio (COP)', 'precio'), ('Área (m²)', 'area'),
            ('Habitaciones', 'habitaciones'), ('Baños', 'banos'), ('Ciudad', 'ciudad'),
            ('Departamento', 'departamento'), ('Dirección', 'direccion'), ('Vendedor', 'vendedor_nombre'),
            ('Correo del vendedor', 'vendedor_correo'), ('Visitas', 'total_visitas'), ('Fotos', 'total_imagenes'),
        ], filas)

    @staticmethod
    def obtener(id_inmueble):
        return InmuebleService.obtener_detalle(id_inmueble)

    @staticmethod
    def obtener_imagenes(id_inmueble):
        return InmuebleService.obtener_imagenes(id_inmueble)

    @classmethod
    def cambiar_estado(cls, id_inmueble, nuevo_estado):
        """El administrador actúa en nombre del dueño: se usa el mismo servicio que el vendedor."""
        inmueble = cls.obtener(id_inmueble)
        InmuebleService.cambiar_disponibilidad(id_inmueble, inmueble['id_vendedor'], nuevo_estado)
        return inmueble

    @classmethod
    def editar(cls, id_inmueble, form, archivos, quitar, portada):
        inmueble = cls.obtener(id_inmueble)
        return InmuebleService.editar_inmueble(
            id_inmueble, inmueble['id_vendedor'], form, archivos=archivos, quitar=quitar, portada=portada)

    @classmethod
    def eliminar(cls, id_inmueble):
        inmueble = cls.obtener(id_inmueble)
        if AdminInmuebleRepository.contar_visitas(id_inmueble):
            raise ValueError(
                "Este inmueble tiene visitas registradas y no se puede eliminar. "
                "Puedes pausarlo para que deje de aparecer en el catálogo.")
        rutas = [f['ruta'] for f in ImagenRepository.find_by_inmueble(id_inmueble)]
        AdminInmuebleRepository.delete(id_inmueble)
        for ruta in rutas:
            ImagenService._borrar_archivo(ruta)
        return inmueble


class VisitaAdminService:

    @staticmethod
    def filtros(args):
        estado = args.get('estado')
        return {
            'q': (args.get('q') or '').strip()[:80],
            'estado': estado if estado in ESTADOS_VISITA else '',
            'desde': fecha_o_none(args.get('desde')) or '',
            'hasta': fecha_o_none(args.get('hasta')) or '',
        }

    @classmethod
    def listar(cls, args):
        filtros = cls.filtros(args)
        _, total = AdminVisitaRepository.listar(filtros, 1, 1)
        pagina = paginar(total, args.get('pagina'))
        filas, _ = AdminVisitaRepository.listar(filtros, pagina['pagina'], POR_PAGINA)
        return filas, pagina, filtros

    @classmethod
    def exportar(cls, args):
        filas, _ = AdminVisitaRepository.listar(cls.filtros(args))
        return a_csv([
            ('ID', 'id_visita'), ('Fecha y hora', 'fecha_visita'), ('Estado', 'estado'),
            ('Inmueble', 'inmueble_titulo'), ('Ciudad', 'inmueble_ciudad'), ('Comprador', 'comprador_nombre'),
            ('Correo del comprador', 'comprador_correo'), ('Teléfono del comprador', 'comprador_telefono'),
            ('Vendedor', 'vendedor_nombre'), ('Mensaje', 'mensaje'),
        ], filas)

    @staticmethod
    def cambiar_estado(id_visita, nuevo_estado):
        if nuevo_estado not in ESTADOS_VISITA:
            raise ValueError("Estado de visita no válido.")
        visita = AdminVisitaRepository.find_by_id(id_visita)
        if not visita:
            raise ValueError("La visita no existe.")
        if visita['estado'] == nuevo_estado:
            raise ValueError(f"La visita ya está {nuevo_estado.lower()}.")
        AdminVisitaRepository.update_estado(id_visita, nuevo_estado)
        return visita



class CatalogoService:

    ETIQUETAS = {'categoria': 'categoría', 'departamento': 'departamento', 'ciudad': 'ciudad'}

    @staticmethod
    def obtener_todo():
        return {
            'categorias': CatalogoRepository.listar_categorias(),
            'departamentos': CatalogoRepository.listar_departamentos(),
            'ciudades': CatalogoRepository.listar_ciudades(),
        }

    @classmethod
    def _validar(cls, entidad, form, excepto_id=None):
        if entidad not in cls.ETIQUETAS:
            raise ValueError("Catálogo no válido.")
        etiqueta = cls.ETIQUETAS[entidad]
        nombre = ' '.join((form.get('nombre') or '').split())
        if not nombre:
            raise ValueError(f"Escribe el nombre de la {etiqueta}." if entidad != 'departamento'
                             else "Escribe el nombre del departamento.")
        if len(nombre) > (50 if entidad == 'categoria' else 100):
            raise ValueError("El nombre es demasiado largo.")

        id_departamento = None
        if entidad == 'ciudad':
            id_departamento = numero_o_none(form.get('id_departamento'))
            if not id_departamento or not CatalogoRepository.existe('departamento', id_departamento):
                raise ValueError("Elige el departamento de la ciudad.")

        if CatalogoRepository.nombre_en_uso(entidad, nombre, id_departamento, excepto_id):
            raise ValueError(f"Ya existe una {etiqueta} con ese nombre." if entidad != 'departamento'
                             else "Ya existe un departamento con ese nombre.")
        return nombre, id_departamento

    @classmethod
    def crear(cls, entidad, form):
        nombre, id_departamento = cls._validar(entidad, form)
        CatalogoRepository.crear(entidad, nombre, id_departamento)
        return nombre

    @classmethod
    def renombrar(cls, entidad, id_, form):
        if entidad not in cls.ETIQUETAS or not CatalogoRepository.existe(entidad, id_):
            raise ValueError("El elemento que intentas editar no existe.")
        nombre, id_departamento = cls._validar(entidad, form, excepto_id=id_)
        CatalogoRepository.renombrar(entidad, id_, nombre, id_departamento)
        return nombre

    @classmethod
    def eliminar(cls, entidad, id_):
        if entidad not in cls.ETIQUETAS or not CatalogoRepository.existe(entidad, id_):
            raise ValueError("El elemento que intentas eliminar no existe.")
        if CatalogoRepository.contar_uso(entidad, id_):
            motivo = {
                'categoria': "hay inmuebles con esta categoría",
                'departamento': "tiene ciudades registradas",
                'ciudad': "hay inmuebles en esta ciudad",
            }[entidad]
            raise ValueError(f"No se puede eliminar porque {motivo}.")
        CatalogoRepository.eliminar(entidad, id_)
