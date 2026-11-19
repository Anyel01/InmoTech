"""
SQL del panel de administración.

Igual que el resto de la aplicación: consultas parametrizadas y compatibles con
MySQL y SQLite. Los listados reciben los filtros ya validados por los servicios.
"""

from app.db import get_db_cursor
from app.repositories import COLUMNAS_FOTOS


def patron_like(texto):
    """Convierte lo que escribió el usuario en un patrón LIKE, sin que %, _ o ! actúen como comodines."""
    limpio = texto.lower().replace('!', '!!').replace('%', '!%').replace('_', '!_')
    return f'%{limpio}%'


def _paginar(sql, params, pagina, por_pagina):
    if por_pagina:
        sql += ' LIMIT %s OFFSET %s'
        params = params + [por_pagina, (pagina - 1) * por_pagina]
    return sql, params


# ------------------------------------------------------------------------------
# Estadísticas del tablero
# ------------------------------------------------------------------------------
class EstadisticasRepository:

    @staticmethod
    def resumen():
        """Todas las cifras del tablero en una sola conexión."""
        consultas = {
            'usuarios_por_rol': """
                SELECT r.nombre AS rol, COUNT(u.id_usuario) AS total
                FROM `rol` r
                LEFT JOIN `usuario` u ON u.id_rol = r.id_rol
                GROUP BY r.id_rol, r.nombre
                ORDER BY r.id_rol
            """,
            'inmuebles_por_estado': """
                SELECT estado, COUNT(*) AS total FROM `inmueble` GROUP BY estado
            """,
            'disponibles_por_operacion': """
                SELECT operacion, COUNT(*) AS total FROM `inmueble`
                WHERE estado = 'DISPONIBLE' GROUP BY operacion
            """,
            'disponibles_por_categoria': """
                SELECT c.nombre AS categoria,
                       COUNT(i.id_inmueble) AS total,
                       AVG(i.precio) AS precio_promedio
                FROM `categoria` c
                LEFT JOIN `inmueble` i
                       ON i.id_categoria = c.id_categoria AND i.estado = 'DISPONIBLE'
                GROUP BY c.id_categoria, c.nombre
                ORDER BY total DESC, c.nombre ASC
            """,
            'disponibles_por_ciudad': """
                SELECT ci.nombre AS ciudad, COUNT(i.id_inmueble) AS total
                FROM `inmueble` i
                INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
                WHERE i.estado = 'DISPONIBLE'
                GROUP BY ci.id_ciudad, ci.nombre
                ORDER BY total DESC, ci.nombre ASC
                LIMIT 6
            """,
            'visitas_por_estado': """
                SELECT estado, COUNT(*) AS total FROM `visita` GROUP BY estado
            """,
            'inmuebles_mas_visitados': """
                SELECT i.id_inmueble, i.titulo, ci.nombre AS ciudad,
                       COUNT(v.id_visita) AS total_visitas
                FROM `inmueble` i
                INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
                INNER JOIN `visita` v ON v.id_inmueble = i.id_inmueble
                GROUP BY i.id_inmueble, i.titulo, ci.nombre
                ORDER BY total_visitas DESC, i.id_inmueble ASC
                LIMIT 5
            """,
            'ultimas_visitas': """
                SELECT v.id_visita, v.fecha_visita, v.estado, i.titulo,
                       CONCAT(c.nombre, ' ', c.apellido) AS comprador
                FROM `visita` v
                INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
                INNER JOIN `usuario` c ON v.id_comprador = c.id_usuario
                ORDER BY v.id_visita DESC
                LIMIT 5
            """,
            'ultimos_usuarios': """
                SELECT u.id_usuario, u.nombre, u.apellido, u.correo, u.activo,
                       r.nombre AS rol_nombre
                FROM `usuario` u
                INNER JOIN `rol` r ON u.id_rol = r.id_rol
                ORDER BY u.id_usuario DESC
                LIMIT 5
            """,
        }
        unicas = {
            'usuarios_bloqueados': "SELECT COUNT(*) AS total FROM `usuario` WHERE activo = 0",
            'inmuebles_sin_fotos': """
                SELECT COUNT(*) AS total FROM `inmueble` i
                WHERE NOT EXISTS (
                    SELECT 1 FROM `imagen_inmueble` im WHERE im.id_inmueble = i.id_inmueble
                )
            """,
        }
        resultado = {}
        with get_db_cursor() as cursor:
            for nombre, sql in consultas.items():
                cursor.execute(sql)
                resultado[nombre] = cursor.fetchall()
            for nombre, sql in unicas.items():
                cursor.execute(sql)
                resultado[nombre] = cursor.fetchone()['total']
        return resultado


# ------------------------------------------------------------------------------
# Usuarios
# ------------------------------------------------------------------------------
class AdminUsuarioRepository:

    COLUMNAS = """
        u.id_usuario, u.nombre, u.apellido, u.correo, u.telefono, u.activo,
        u.id_rol, r.nombre AS rol_nombre,
        (SELECT COUNT(*) FROM `inmueble` i WHERE i.id_vendedor = u.id_usuario) AS total_inmuebles,
        (SELECT COUNT(*) FROM `visita` v WHERE v.id_comprador = u.id_usuario) AS total_visitas
    """

    @staticmethod
    def _condiciones(filtros):
        donde, params = ['1 = 1'], []
        if filtros.get('q'):
            patron = patron_like(filtros['q'])
            donde.append("""(LOWER(u.nombre) LIKE %s ESCAPE '!' OR LOWER(u.apellido) LIKE %s ESCAPE '!'
                             OR LOWER(u.correo) LIKE %s ESCAPE '!'
                             OR LOWER(CONCAT(u.nombre, ' ', u.apellido)) LIKE %s ESCAPE '!')""")
            params += [patron] * 4
        if filtros.get('rol'):
            donde.append('r.nombre = %s')
            params.append(filtros['rol'])
        if filtros.get('estado') == 'activos':
            donde.append('u.activo = 1')
        elif filtros.get('estado') == 'bloqueados':
            donde.append('u.activo = 0')
        return ' AND '.join(donde), params

    @classmethod
    def listar(cls, filtros, pagina=1, por_pagina=None):
        donde, params = cls._condiciones(filtros)
        base = f"FROM `usuario` u INNER JOIN `rol` r ON u.id_rol = r.id_rol WHERE {donde}"
        sql, params_pagina = _paginar(
            f"SELECT {cls.COLUMNAS} {base} ORDER BY u.id_usuario ASC", list(params), pagina, por_pagina)
        with get_db_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) AS total {base}", tuple(params))
            total = cursor.fetchone()['total']
            cursor.execute(sql, tuple(params_pagina))
            return cursor.fetchall(), total

    @classmethod
    def find_by_id(cls, id_usuario):
        sql = f"""
            SELECT {cls.COLUMNAS}
            FROM `usuario` u INNER JOIN `rol` r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = %s LIMIT 1
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()

    @staticmethod
    def correo_en_uso(correo, excepto_id=None):
        sql = "SELECT id_usuario FROM `usuario` WHERE correo = %s"
        params = [correo]
        if excepto_id:
            sql += " AND id_usuario <> %s"
            params.append(excepto_id)
        with get_db_cursor() as cursor:
            cursor.execute(sql + " LIMIT 1", tuple(params))
            return cursor.fetchone() is not None

    @staticmethod
    def create(nombre, apellido, correo, telefono, password_hash, rol):
        sql = """
            INSERT INTO `usuario` (nombre, apellido, correo, password_hash, telefono, id_rol)
            VALUES (%s, %s, %s, %s, %s, (SELECT id_rol FROM `rol` WHERE nombre = %s LIMIT 1))
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (nombre, apellido, correo, password_hash, telefono, rol))
            return cursor.lastrowid

    @staticmethod
    def update(id_usuario, nombre, apellido, correo, telefono, rol):
        sql = """
            UPDATE `usuario` SET nombre = %s, apellido = %s, correo = %s, telefono = %s,
                   id_rol = (SELECT id_rol FROM `rol` WHERE nombre = %s LIMIT 1)
            WHERE id_usuario = %s
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (nombre, apellido, correo, telefono, rol, id_usuario))
            return cursor.rowcount

    @staticmethod
    def set_activo(id_usuario, activo):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE `usuario` SET activo = %s WHERE id_usuario = %s",
                           (1 if activo else 0, id_usuario))
            return cursor.rowcount

    @staticmethod
    def set_password(id_usuario, password_hash):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE `usuario` SET password_hash = %s WHERE id_usuario = %s",
                           (password_hash, id_usuario))

    @staticmethod
    def delete(id_usuario):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM `usuario` WHERE id_usuario = %s", (id_usuario,))
            return cursor.rowcount

    @staticmethod
    def contar_administradores_activos(excepto_id=None):
        sql = """
            SELECT COUNT(*) AS total FROM `usuario` u
            INNER JOIN `rol` r ON u.id_rol = r.id_rol
            WHERE r.nombre = 'ADMINISTRADOR' AND u.activo = 1
        """
        params = []
        if excepto_id:
            sql += " AND u.id_usuario <> %s"
            params.append(excepto_id)
        with get_db_cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchone()['total']

    @staticmethod
    def listar_roles():
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id_rol, nombre FROM `rol` ORDER BY id_rol")
            return cursor.fetchall()


# ------------------------------------------------------------------------------
# Inmuebles
# ------------------------------------------------------------------------------
class AdminInmuebleRepository:

    @staticmethod
    def _condiciones(filtros):
        donde, params = ['1 = 1'], []
        if filtros.get('q'):
            patron = patron_like(filtros['q'])
            donde.append("""(LOWER(i.titulo) LIKE %s ESCAPE '!' OR LOWER(i.direccion) LIKE %s ESCAPE '!'
                             OR LOWER(CONCAT(u.nombre, ' ', u.apellido)) LIKE %s ESCAPE '!')""")
            params += [patron] * 3
        if filtros.get('estado'):
            donde.append('i.estado = %s')
            params.append(filtros['estado'])
        if filtros.get('operacion'):
            donde.append('i.operacion = %s')
            params.append(filtros['operacion'])
        if filtros.get('id_categoria'):
            donde.append('i.id_categoria = %s')
            params.append(filtros['id_categoria'])
        if filtros.get('id_ciudad'):
            donde.append('i.id_ciudad = %s')
            params.append(filtros['id_ciudad'])
        if filtros.get('id_vendedor'):
            donde.append('i.id_vendedor = %s')
            params.append(filtros['id_vendedor'])
        return ' AND '.join(donde), params

    @classmethod
    def listar(cls, filtros, pagina=1, por_pagina=None):
        donde, params = cls._condiciones(filtros)
        base = f"""
            FROM `inmueble` i
            INNER JOIN `categoria` c ON i.id_categoria = c.id_categoria
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            INNER JOIN `usuario` u ON i.id_vendedor = u.id_usuario
            WHERE {donde}
        """
        columnas = f"""
            i.id_inmueble, i.titulo, i.direccion, i.precio, i.area, i.habitaciones, i.banos,
            i.operacion, i.estado, i.id_vendedor,
            c.nombre AS categoria, ci.nombre AS ciudad, d.nombre AS departamento,
            CONCAT(u.nombre, ' ', u.apellido) AS vendedor_nombre, u.correo AS vendedor_correo,
            (SELECT COUNT(*) FROM `visita` v WHERE v.id_inmueble = i.id_inmueble) AS total_visitas,
            {COLUMNAS_FOTOS}
        """
        sql, params_pagina = _paginar(
            f"SELECT {columnas} {base} ORDER BY i.id_inmueble DESC", list(params), pagina, por_pagina)
        with get_db_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) AS total {base}", tuple(params))
            total = cursor.fetchone()['total']
            cursor.execute(sql, tuple(params_pagina))
            return cursor.fetchall(), total

    @staticmethod
    def contar_visitas(id_inmueble):
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM `visita` WHERE id_inmueble = %s", (id_inmueble,))
            return cursor.fetchone()['total']

    @staticmethod
    def delete(id_inmueble):
        """Borra el inmueble; sus fotos (imagen_inmueble) se borran en cascada."""
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM `inmueble` WHERE id_inmueble = %s", (id_inmueble,))
            return cursor.rowcount

    @staticmethod
    def listar_vendedores():
        sql = """
            SELECT u.id_usuario, CONCAT(u.nombre, ' ', u.apellido) AS nombre
            FROM `usuario` u INNER JOIN `rol` r ON u.id_rol = r.id_rol
            WHERE r.nombre = 'VENDEDOR' ORDER BY u.nombre, u.apellido
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


# ------------------------------------------------------------------------------
# Visitas
# ------------------------------------------------------------------------------
class AdminVisitaRepository:

    @staticmethod
    def _condiciones(filtros):
        donde, params = ['1 = 1'], []
        if filtros.get('q'):
            patron = patron_like(filtros['q'])
            donde.append("""(LOWER(i.titulo) LIKE %s ESCAPE '!'
                             OR LOWER(CONCAT(comp.nombre, ' ', comp.apellido)) LIKE %s ESCAPE '!'
                             OR LOWER(CONCAT(vend.nombre, ' ', vend.apellido)) LIKE %s ESCAPE '!')""")
            params += [patron] * 3
        if filtros.get('estado'):
            donde.append('v.estado = %s')
            params.append(filtros['estado'])
        if filtros.get('desde'):
            donde.append('DATE(v.fecha_visita) >= %s')
            params.append(filtros['desde'])
        if filtros.get('hasta'):
            donde.append('DATE(v.fecha_visita) <= %s')
            params.append(filtros['hasta'])
        return ' AND '.join(donde), params

    @classmethod
    def listar(cls, filtros, pagina=1, por_pagina=None):
        donde, params = cls._condiciones(filtros)
        base = f"""
            FROM `visita` v
            INNER JOIN `inmueble` i ON v.id_inmueble = i.id_inmueble
            INNER JOIN `ciudad` ci ON i.id_ciudad = ci.id_ciudad
            INNER JOIN `usuario` comp ON v.id_comprador = comp.id_usuario
            INNER JOIN `usuario` vend ON i.id_vendedor = vend.id_usuario
            WHERE {donde}
        """
        columnas = """
            v.id_visita, v.fecha_visita, v.mensaje, v.estado,
            i.id_inmueble, i.titulo AS inmueble_titulo, ci.nombre AS inmueble_ciudad,
            CONCAT(comp.nombre, ' ', comp.apellido) AS comprador_nombre,
            comp.correo AS comprador_correo, comp.telefono AS comprador_telefono,
            CONCAT(vend.nombre, ' ', vend.apellido) AS vendedor_nombre
        """
        sql, params_pagina = _paginar(
            f"SELECT {columnas} {base} ORDER BY v.fecha_visita DESC, v.id_visita DESC",
            list(params), pagina, por_pagina)
        with get_db_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) AS total {base}", tuple(params))
            total = cursor.fetchone()['total']
            cursor.execute(sql, tuple(params_pagina))
            return cursor.fetchall(), total

    @staticmethod
    def find_by_id(id_visita):
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id_visita, estado FROM `visita` WHERE id_visita = %s LIMIT 1", (id_visita,))
            return cursor.fetchone()

    @staticmethod
    def update_estado(id_visita, estado):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE `visita` SET estado = %s WHERE id_visita = %s", (estado, id_visita))
            return cursor.rowcount


# ------------------------------------------------------------------------------
# Catálogos: categorías, departamentos y ciudades
# ------------------------------------------------------------------------------
class CatalogoRepository:
    """
    Las tres tablas se manejan igual. Los nombres de tabla y de columna salen de
    este diccionario (nunca del usuario), por eso es seguro armarlos en el SQL.
    """

    TABLAS = {
        'categoria': {'tabla': 'categoria', 'id': 'id_categoria'},
        'departamento': {'tabla': 'departamento', 'id': 'id_departamento'},
        'ciudad': {'tabla': 'ciudad', 'id': 'id_ciudad'},
    }

    @classmethod
    def _t(cls, entidad):
        return cls.TABLAS[entidad]

    @staticmethod
    def listar_categorias():
        sql = """
            SELECT c.id_categoria AS id, c.nombre,
                   (SELECT COUNT(*) FROM `inmueble` i WHERE i.id_categoria = c.id_categoria) AS en_uso
            FROM `categoria` c ORDER BY c.nombre
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def listar_departamentos():
        sql = """
            SELECT d.id_departamento AS id, d.nombre,
                   (SELECT COUNT(*) FROM `ciudad` ci WHERE ci.id_departamento = d.id_departamento) AS en_uso
            FROM `departamento` d ORDER BY d.nombre
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def listar_ciudades():
        sql = """
            SELECT ci.id_ciudad AS id, ci.nombre, ci.id_departamento, d.nombre AS departamento,
                   (SELECT COUNT(*) FROM `inmueble` i WHERE i.id_ciudad = ci.id_ciudad) AS en_uso
            FROM `ciudad` ci INNER JOIN `departamento` d ON ci.id_departamento = d.id_departamento
            ORDER BY d.nombre, ci.nombre
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    @classmethod
    def nombre_en_uso(cls, entidad, nombre, id_departamento=None, excepto_id=None):
        t = cls._t(entidad)
        sql = f"SELECT {t['id']} AS id FROM `{t['tabla']}` WHERE LOWER(nombre) = %s"
        params = [nombre.lower()]
        if entidad == 'ciudad':
            sql += " AND id_departamento = %s"
            params.append(id_departamento)
        if excepto_id:
            sql += f" AND {t['id']} <> %s"
            params.append(excepto_id)
        with get_db_cursor() as cursor:
            cursor.execute(sql + " LIMIT 1", tuple(params))
            return cursor.fetchone() is not None

    @classmethod
    def existe(cls, entidad, id_):
        t = cls._t(entidad)
        with get_db_cursor() as cursor:
            cursor.execute(f"SELECT {t['id']} AS id FROM `{t['tabla']}` WHERE {t['id']} = %s LIMIT 1", (id_,))
            return cursor.fetchone() is not None

    @classmethod
    def crear(cls, entidad, nombre, id_departamento=None):
        t = cls._t(entidad)
        with get_db_cursor(commit=True) as cursor:
            if entidad == 'ciudad':
                cursor.execute("INSERT INTO `ciudad` (nombre, id_departamento) VALUES (%s, %s)", (nombre, id_departamento))
            else:
                cursor.execute(f"INSERT INTO `{t['tabla']}` (nombre) VALUES (%s)", (nombre,))
            return cursor.lastrowid

    @classmethod
    def renombrar(cls, entidad, id_, nombre, id_departamento=None):
        t = cls._t(entidad)
        with get_db_cursor(commit=True) as cursor:
            if entidad == 'ciudad':
                cursor.execute("UPDATE `ciudad` SET nombre = %s, id_departamento = %s WHERE id_ciudad = %s",
                               (nombre, id_departamento, id_))
            else:
                cursor.execute(f"UPDATE `{t['tabla']}` SET nombre = %s WHERE {t['id']} = %s", (nombre, id_))
            return cursor.rowcount

    @classmethod
    def eliminar(cls, entidad, id_):
        t = cls._t(entidad)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(f"DELETE FROM `{t['tabla']}` WHERE {t['id']} = %s", (id_,))
            return cursor.rowcount

    @classmethod
    def contar_uso(cls, entidad, id_):
        consultas = {
            'categoria': "SELECT COUNT(*) AS total FROM `inmueble` WHERE id_categoria = %s",
            'departamento': "SELECT COUNT(*) AS total FROM `ciudad` WHERE id_departamento = %s",
            'ciudad': "SELECT COUNT(*) AS total FROM `inmueble` WHERE id_ciudad = %s",
        }
        with get_db_cursor() as cursor:
            cursor.execute(consultas[entidad], (id_,))
            return cursor.fetchone()['total']
