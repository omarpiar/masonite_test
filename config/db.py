# config/db.py
import os
import pyodbc
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'server': os.getenv('DB_SERVER', 'db47937.public.databaseasp.net'),
    'user': os.getenv('DB_USER', 'db47937'),
    'password': os.getenv('DB_PASSWORD', '5t#LE-8c+xD3'),
    'database': os.getenv('DB_NAME', 'db47937'),
    'port': int(os.getenv('DB_PORT', 1433)),
}


def get_connection():
    """
    Returns a new pyodbc connection.
    Compatible con SQL Server en Render y entornos locales.
    """
    # Construir connection string para pyodbc
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']},{DB_CONFIG['port']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']};"
        f"CHARSET=UTF-8;"
        f"TrustServerCertificate=yes;"  # Necesario para conexiones cloud
        f"Encrypt=yes;"
    )
    
    return pyodbc.connect(connection_string)


def rows_to_dicts(cursor, rows):
    """
    Convierte las filas de pyodbc a una lista de diccionarios.
    Equivalente al as_dict=True de pymssql.
    """
    if not rows:
        return []
    
    # Obtener nombres de columnas
    columns = [column[0] for column in cursor.description]
    
    # Convertir cada fila a diccionario
    result = []
    for row in rows:
        result.append(dict(zip(columns, row)))
    
    return result


def row_to_dict(cursor, row):
    """
    Convierte una fila de pyodbc a diccionario.
    Equivalente al fetchone con as_dict=True de pymssql.
    """
    if not row:
        return None
    
    # Obtener nombres de columnas
    columns = [column[0] for column in cursor.description]
    
    # Convertir fila a diccionario
    return dict(zip(columns, row))


@contextmanager
def db_cursor():
    """
    Context manager que mantiene la misma interfaz que tu código original.
    Retorna (conn, cursor) y maneja commit/rollback automáticamente.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(sql, params=None):
    """
    Execute a SELECT and return list of dicts.
    Mantiene exactamente la misma firma que tu código original.
    """
    with db_cursor() as (conn, cursor):
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        rows = cursor.fetchall()
        return rows_to_dicts(cursor, rows)


def execute_scalar(sql, params=None):
    """
    Execute a SELECT and return first row as dict.
    Mantiene exactamente la misma firma que tu código original.
    """
    with db_cursor() as (conn, cursor):
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        row = cursor.fetchone()
        return row_to_dict(cursor, row)


def execute_non_query(sql, params=None):
    """
    Execute INSERT/UPDATE/DELETE.
    Mantiene exactamente la misma firma que tu código original.
    """
    with db_cursor() as (conn, cursor):
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        return cursor.rowcount


# ✅ Función adicional útil para mantener compatibilidad
def test_connection():
    """
    Prueba la conexión a la base de datos.
    Útil para debugging en Render.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION as version, DB_NAME() as database_name")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'success': True,
                'version': row[0],
                'database': row[1]
            }
        return {
            'success': True,
            'version': 'Unknown',
            'database': 'Unknown'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }