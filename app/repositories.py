

from app.db import get_db_cursor

# Columnas que agregan la foto de portada (la de menor orden) y cuántas fotos
# tiene cada inmueble. Se concatenan a los SELECT de los listados.
COLUMNAS_FOTOS = """
                (SELECT im.ruta FROM `imagen_inmueble` im
                 WHERE im.id_inmueble = i.id_inmueble
                 ORDER BY im.orden ASC, im.id_imagen ASC LIMIT 1) AS portada,
                (SELECT COUNT(*) FROM `imagen_inmueble` im2
                 WHERE im2.id_inmueble = i.id_inmueble) AS total_imagenes
"""


class UsuarioRepository:


    @staticmethod
    def find_by_correo(correo):

        sql = """
            SELECT 
                u.id_usuario,
                u.nombre,
                u.apellido,
                u.correo,
                u.password_hash,
                u.telefono,
                u.id_rol,
                u.activo,
                r.nombre AS rol_nombre
            FROM `usuario` u
            INNER JOIN `rol` r ON u.id_rol = r.id_rol
            WHERE u.correo = %s
            LIMIT 1;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (correo.strip().lower(),))
            return cursor.fetchone()

    @staticmethod
    def find_by_id(id_usuario):
        """
        Busca un usuario por su ID primario.
        """
        sql = """
            SELECT 
                u.id_usuario,
                u.nombre,
                u.apellido,
                u.correo,
                u.telefono,
                u.id_rol,
                u.activo,
                r.nombre AS rol_nombre
            FROM `usuario` u
            INNER JOIN `rol` r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = %s
            LIMIT 1;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()

    @staticmethod
    def create_comprador(nombre, apellido, correo, password_hash, telefono):
        """
        Registra un nuevo usuario con rol estricto de COMPRADOR.
        """
        sql_insert = """
            INSERT INTO `usuario` (nombre, apellido, correo, password_hash, telefono, id_rol)
            VALUES (
                %s, 
                %s, 
                %s, 
                %s, 
                %s, 
                (SELECT id_rol FROM `rol` WHERE nombre = 'COMPRADOR' LIMIT 1)
            );
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql_insert, (
                nombre.strip(),
                apellido.strip(),
                correo.strip().lower(),
                password_hash,
                telefono.strip()
            ))
            return cursor.lastrowid
    
    @staticmethod
    def update_password(id_usuario, password_hash):
        sql = """
            UPDATE usuario
            SET password_hash = %s
            WHERE id_usuario = %s;
        """

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (password_hash, id_usuario))


    @staticmethod
    def find_id_by_correo(correo):
        sql = """
            SELECT id_usuario, correo
            FROM usuario
            WHERE correo = %s
            LIMIT 1;
        """

        with get_db_cursor() as cursor:
            cursor.execute(sql, (correo.strip().lower(),))
            return cursor.fetchone()


class InmuebleRepository:


    @staticmethod
    def find_all_disponibles(filtros=None):
        """
        Consulta inmuebles DISPONIBLES con filtros combinables en SQL.
        No carga datos en memoria para filtrar en Python.
        """
        filtros = filtros or {}
        sql = """
            SELECT 
                i.id_inmueble,
                i.titulo,
                i.descripcion,
                i.direccion,
                i.precio,
                i.area,
                i.habitaciones,
                i.banos,
                i.operacion,
                i.estado,
                c.id_categoria,
                c.nombre AS categoria,
                ci.id_ciudad,
                ci.nombre AS ciudad,
                d.id_departamento,
                d.nombre AS departamento,
                CONCAT(u.nombre, ' ', u.apellido) AS vendedor_nombre,
                u.telefono AS vendedor_telefono,
                """ + COLUMNAS_FOTOS + """
            FROM `inmueble` i
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            INNER JOIN `usuario` u ON i.id_vendedor = u.id_usuario
            WHERE i.estado = 'DISPONIBLE'
        """
        params = []

        if filtros.get('id_ciudad'):
            sql += " AND i.id_ciudad = %s"
            params.append(int(filtros['id_ciudad']))

        if filtros.get('id_categoria'):
            sql += " AND i.id_categoria = %s"
            params.append(int(filtros['id_categoria']))

        if filtros.get('operacion'):
            sql += " AND i.operacion = %s"
            params.append(filtros['operacion'])

        if filtros.get('precio_min'):
            sql += " AND i.precio >= %s"
            params.append(float(filtros['precio_min']))

        if filtros.get('precio_max'):
            sql += " AND i.precio <= %s"
            params.append(float(filtros['precio_max']))

        if filtros.get('habitaciones_min'):
            sql += " AND i.habitaciones >= %s"
            params.append(int(filtros['habitaciones_min']))

        sql += " ORDER BY i.id_inmueble DESC;"

        with get_db_cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()

    @staticmethod
    def find_destacados(limite=6):
        """
        Obtiene los inmuebles disponibles más recientes para la página de inicio.
        """
        sql = """
            SELECT 
                i.id_inmueble,
                i.titulo,
                i.descripcion,
                i.direccion,
                i.precio,
                i.area,
                i.habitaciones,
                i.banos,
                i.operacion,
                i.estado,
                c.nombre AS categoria,
                ci.nombre AS ciudad,
                d.nombre AS departamento,
                """ + COLUMNAS_FOTOS + """
            FROM `inmueble` i
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            WHERE i.estado = 'DISPONIBLE'
            ORDER BY i.id_inmueble DESC
            LIMIT %s;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (limite,))
            return cursor.fetchall()

    @staticmethod
    def find_by_id(id_inmueble):
        """
        Obtiene los detalles completos de un inmueble específico.
        """
        sql = """
            SELECT 
                i.id_inmueble,
                i.titulo,
                i.descripcion,
                i.direccion,
                i.precio,
                i.area,
                i.habitaciones,
                i.banos,
                i.operacion,
                i.estado,
                i.id_categoria,
                i.id_ciudad,
                i.id_vendedor,
                c.nombre AS categoria,
                ci.nombre AS ciudad,
                d.id_departamento,
                d.nombre AS departamento,
                CONCAT(u.nombre, ' ', u.apellido) AS vendedor_nombre,
                u.telefono AS vendedor_telefono,
                u.correo AS vendedor_correo
            FROM `inmueble` i
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            INNER JOIN `usuario` u ON i.id_vendedor = u.id_usuario
            WHERE i.id_inmueble = %s
            LIMIT 1;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_inmueble,))
            return cursor.fetchone()

    @staticmethod
    def find_by_vendedor(id_vendedor):
        """
        Obtiene todas las propiedades publicadas por un vendedor, junto con el total de visitas recibidas.
        """
        sql = """
            SELECT 
                i.id_inmueble,
                i.titulo,
                i.descripcion,
                i.direccion,
                i.precio,
                i.area,
                i.habitaciones,
                i.banos,
                i.operacion,
                i.estado,
                c.nombre AS categoria,
                ci.nombre AS ciudad,
                d.nombre AS departamento,
                COUNT(v.id_visita) AS total_visitas,
                """ + COLUMNAS_FOTOS + """
            FROM `inmueble` i
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            LEFT JOIN `visita` v ON i.id_inmueble = v.id_inmueble
            WHERE i.id_vendedor = %s
            GROUP BY 
                i.id_inmueble, i.titulo, i.descripcion, i.direccion, 
                i.precio, i.area, i.habitaciones, i.banos, i.operacion, 
                i.estado, c.nombre, ci.nombre, d.nombre
            ORDER BY i.id_inmueble DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_vendedor,))
            return cursor.fetchall()

    @staticmethod
    def create(datos):
        """
        Inserta un nuevo inmueble en la base de datos.
        """
        sql = """
            INSERT INTO `inmueble` (
                titulo, descripcion, direccion, precio, area,
                habitaciones, banos, operacion, estado,
                id_categoria, id_ciudad, id_vendedor
            ) VALUES (
                %(titulo)s, %(descripcion)s, %(direccion)s, %(precio)s, %(area)s,
                %(habitaciones)s, %(banos)s, %(operacion)s, %(estado)s,
                %(id_categoria)s, %(id_ciudad)s, %(id_vendedor)s
            );
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, datos)
            return cursor.lastrowid

    @staticmethod
    def update(id_inmueble, datos):
        """
        Actualiza los datos de un inmueble existente.
        """
        sql = """
            UPDATE `inmueble` SET
                titulo = %(titulo)s,
                descripcion = %(descripcion)s,
                direccion = %(direccion)s,
                precio = %(precio)s,
                area = %(area)s,
                habitaciones = %(habitaciones)s,
                banos = %(banos)s,
                operacion = %(operacion)s,
                id_categoria = %(id_categoria)s,
                id_ciudad = %(id_ciudad)s
            WHERE id_inmueble = %(id_inmueble)s;
        """
        datos_completos = {**datos, 'id_inmueble': id_inmueble}
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, datos_completos)
            return cursor.rowcount

    @staticmethod
    def update_estado(id_inmueble, nuevo_estado):
        """
        Modifica la disponibilidad de un inmueble (DISPONIBLE o NO_DISPONIBLE).
        """
        sql = "UPDATE `inmueble` SET estado = %s WHERE id_inmueble = %s;"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (nuevo_estado, id_inmueble))
            return cursor.rowcount


class VisitaRepository:
    """
    Repositorio para operaciones sobre la tabla `visita`.
    """

    @staticmethod
    def create(datos):
        """
        Inserta una nueva solicitud de visita con estado PENDIENTE.
        """
        sql = """
            INSERT INTO `visita` (fecha_visita, mensaje, estado, id_inmueble, id_comprador)
            VALUES (%(fecha_visita)s, %(mensaje)s, 'PENDIENTE', %(id_inmueble)s, %(id_comprador)s);
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, datos)
            return cursor.lastrowid

    @staticmethod
    def find_by_id(id_visita):
        """
        Busca una visita por su identificador primario.
        """
        sql = """
            SELECT 
                v.id_visita,
                v.fecha_visita,
                v.mensaje,
                v.estado,
                v.id_inmueble,
                v.id_comprador,
                i.titulo AS inmueble_titulo,
                i.id_vendedor
            FROM `visita` v
            INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
            WHERE v.id_visita = %s
            LIMIT 1;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_visita,))
            return cursor.fetchone()

    @staticmethod
    def find_by_comprador(id_comprador):
        """
        Obtiene las solicitudes de visita creadas por un comprador específico.
        """
        sql = """
            SELECT 
                v.id_visita,
                v.fecha_visita,
                v.mensaje,
                v.estado,
                i.id_inmueble,
                i.titulo AS inmueble_titulo,
                i.direccion AS inmueble_direccion,
                i.precio AS inmueble_precio,
                i.operacion AS inmueble_operacion,
                ci.nombre AS inmueble_ciudad,
                c.nombre AS inmueble_categoria,
                CONCAT(vend.nombre, ' ', vend.apellido) AS vendedor_nombre,
                vend.telefono AS vendedor_telefono,
                vend.correo AS vendedor_correo
            FROM `visita` v
            INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `usuario` vend ON i.id_vendedor = vend.id_usuario
            WHERE v.id_comprador = %s
            ORDER BY v.fecha_visita DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_comprador,))
            return cursor.fetchall()

    @staticmethod
    def find_by_vendedor(id_vendedor):
        """
        Obtiene las solicitudes de visitas realizadas a los inmuebles publicados por un vendedor.
        """
        sql = """
            SELECT 
                v.id_visita,
                v.fecha_visita,
                v.mensaje,
                v.estado,
                i.id_inmueble,
                i.titulo AS inmueble_titulo,
                i.direccion AS inmueble_direccion,
                i.precio AS inmueble_precio,
                i.operacion AS inmueble_operacion,
                ci.nombre AS inmueble_ciudad,
                CONCAT(comp.nombre, ' ', comp.apellido) AS comprador_nombre,
                comp.correo AS comprador_correo,
                comp.telefono AS comprador_telefono
            FROM `visita` v
            INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `usuario` comp ON v.id_comprador = comp.id_usuario
            WHERE i.id_vendedor = %s
            ORDER BY v.fecha_visita ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_vendedor,))
            return cursor.fetchall()

    @staticmethod
    def update_estado(id_visita, nuevo_estado):
        """
        Actualiza el estado de una visita (PENDIENTE, CONFIRMADA, CANCELADA, REALIZADA).
        """
        sql = "UPDATE `visita` SET estado = %s WHERE id_visita = %s;"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (nuevo_estado, id_visita))
            return cursor.rowcount


class UbicacionCategoriaRepository:
    """
    Repositorio para consultar departamentos, ciudades y categorías.
    """

    @staticmethod
    def get_departamentos():
        sql = "SELECT id_departamento, nombre FROM `departamento` ORDER BY nombre ASC;"
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def get_ciudades(id_departamento=None):
        if id_departamento:
            sql = "SELECT id_ciudad, nombre, id_departamento FROM `ciudad` WHERE id_departamento = %s ORDER BY nombre ASC;"
            params = (id_departamento,)
        else:
            sql = "SELECT id_ciudad, nombre, id_departamento FROM `ciudad` ORDER BY nombre ASC;"
            params = ()
        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    @staticmethod
    def get_categorias():
        sql = "SELECT id_categoria, nombre FROM `categoria` ORDER BY nombre ASC;"
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


class ImagenRepository:
    """
    Repositorio para las fotos de los inmuebles (tabla `imagen_inmueble`).
    """

    @staticmethod
    def find_by_inmueble(id_inmueble):
        sql = """
            SELECT id_imagen, ruta, descripcion, orden, id_inmueble
            FROM `imagen_inmueble`
            WHERE id_inmueble = %s
            ORDER BY orden ASC, id_imagen ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_inmueble,))
            return cursor.fetchall()

    @staticmethod
    def create_many(id_inmueble, fotos):
        """Guarda varias fotos en una sola transacción. fotos = [(ruta, descripcion, orden), ...]"""
        sql = """
            INSERT INTO `imagen_inmueble` (ruta, descripcion, orden, id_inmueble)
            VALUES (%s, %s, %s, %s);
        """
        with get_db_cursor(commit=True) as cursor:
            for ruta, descripcion, orden in fotos:
                cursor.execute(sql, (ruta, descripcion, orden, id_inmueble))

    @staticmethod
    def delete_many(id_inmueble, ids_imagenes):
        """Borra las fotos indicadas, solo si pertenecen a ese inmueble."""
        if not ids_imagenes:
            return 0
        marcas = ', '.join(['%s'] * len(ids_imagenes))
        sql = f"DELETE FROM `imagen_inmueble` WHERE id_inmueble = %s AND id_imagen IN ({marcas});"
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (id_inmueble, *ids_imagenes))
            return cursor.rowcount

    @staticmethod
    def reordenar(id_inmueble, ids_en_orden):
        """Numera las fotos 1, 2, 3... según la lista; la primera queda de portada."""
        sql = "UPDATE `imagen_inmueble` SET orden = %s WHERE id_imagen = %s AND id_inmueble = %s;"
        with get_db_cursor(commit=True) as cursor:
            for posicion, id_imagen in enumerate(ids_en_orden, start=1):
                cursor.execute(sql, (posicion, id_imagen, id_inmueble))

