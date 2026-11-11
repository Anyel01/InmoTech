

import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_SQL_SQLITE = RAIZ_PROYECTO / 'database' / 'sqlite'

_sqlite_listo = False
_sqlite_lock = threading.Lock()


class SQLiteCursor:

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=()):
        # MySQL usa %s y %(nombre)s; SQLite usa ? y :nombre
        sql = re.sub(r"%\((\w+)\)s", r":\1", sql)
        sql = sql.replace("%s", "?")
        self._cursor.execute(sql, params)
        return self

    def fetchone(self):
        fila = self._cursor.fetchone()
        return dict(fila) if fila is not None else None

    def fetchall(self):
        return [dict(fila) for fila in self._cursor.fetchall()]

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()


class SQLiteConnection:
    """Conexión de SQLite con la misma interfaz que mysql.connector."""

    def __init__(self, conexion):
        self._conexion = conexion

    def cursor(self, dictionary=False):
        return SQLiteCursor(self._conexion.cursor())

    def commit(self):
        self._conexion.commit()

    def rollback(self):
        self._conexion.rollback()

    def close(self):
        self._conexion.close()


# ------------------------------------------------------------------------------
# SQLite
# ------------------------------------------------------------------------------
def _inicializar_sqlite(conexion):
    """
    Crea las tablas (si no existen) y carga los datos de prueba la primera vez.
    Los scripts viven en database/sqlite/ para no tener SQL pegado en el código.
    """
    global _sqlite_listo

    with _sqlite_lock:
        if _sqlite_listo:
            return

        esquema = (CARPETA_SQL_SQLITE / '01_estructura.sql').read_text(encoding='utf-8')
        conexion.executescript(esquema)

        hay_datos = conexion.execute("SELECT COUNT(*) FROM rol").fetchone()[0] > 0
        if not hay_datos:
            semilla = (CARPETA_SQL_SQLITE / '02_datos_iniciales.sql').read_text(encoding='utf-8')
            conexion.executescript(semilla)

        conexion.commit()
        _sqlite_listo = True


def _conectar_sqlite():
    ruta = Path(os.environ.get('DB_SQLITE_PATH', 'instance/inmotech.sqlite3'))
    if not ruta.is_absolute():
        ruta = RAIZ_PROYECTO / ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute('PRAGMA foreign_keys = ON')  # SQLite no valida FK si no se activa
    # MySQL trae CONCAT() y SQLite no; la registramos para reutilizar las mismas consultas
    conexion.create_function(
        'CONCAT', -1,
        lambda *valores: ''.join('' if v is None else str(v) for v in valores)
    )
    _inicializar_sqlite(conexion)
    return SQLiteConnection(conexion)


# ------------------------------------------------------------------------------
# MySQL
# ------------------------------------------------------------------------------
def get_db_config():
    """Parámetros de conexión a MySQL, leídos de las variables de entorno."""
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'inmotech_db'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False,
    }


def _conectar_mysql():
    # Import diferido: quien trabaja con SQLite no necesita el conector instalado
    import mysql.connector
    try:
        return mysql.connector.connect(**get_db_config())
    except mysql.connector.Error as error:
        print(f"[ERROR DB] No se pudo conectar con MySQL: {error}")
        raise


# ------------------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------------------
def get_raw_connection():
    """Abre una conexión nueva con el motor indicado en DB_DRIVER."""
    driver = os.environ.get('DB_DRIVER', 'sqlite').strip().lower()
    if driver == 'sqlite':
        return _conectar_sqlite()
    return _conectar_mysql()


@contextmanager
def get_db_cursor(commit=False):
    """
    Entrega un cursor y se encarga de cerrar todo al terminar.

    - commit=True: confirma los cambios si el bloque termina bien.
    - Si ocurre cualquier excepción hace rollback y la vuelve a lanzar.

        with get_db_cursor() as cursor:                  # lectura
            cursor.execute("SELECT ...", params)
            filas = cursor.fetchall()

        with get_db_cursor(commit=True) as cursor:       # escritura
            cursor.execute("INSERT ...", params)
    """
    conexion = None
    cursor = None
    try:
        conexion = get_raw_connection()
        cursor = conexion.cursor(dictionary=True)
        yield cursor
        if commit:
            conexion.commit()
    except Exception as error:
        if conexion:
            conexion.rollback()
        print(f"[ERROR DB] Falló la consulta o la transacción: {error}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
