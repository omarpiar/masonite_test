# config/db.py
import os
import pymssql
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
    """Returns a new pymssql connection."""
    try:
        conn = pymssql.connect(
            server=DB_CONFIG['server'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            as_dict=True,
            charset='UTF-8',
            timeout=30,
            login_timeout=30
        )
        print("✅ Conexión a SQL Server exitosa con pymssql")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a SQL Server: {e}")
        raise


@contextmanager
def db_cursor():
    """Context manager that yields a (conn, cursor) tuple and commits/rolls back."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield conn, cursor
        conn.commit()
    except Exception as e:
        print(f"❌ Error en transacción: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(sql, params=None):
    """Execute a SELECT and return list of dicts."""
    with db_cursor() as (conn, cursor):
        cursor.execute(sql, params or ())
        return cursor.fetchall()


def execute_scalar(sql, params=None):
    """Execute a SELECT and return first row."""
    with db_cursor() as (conn, cursor):
        cursor.execute(sql, params or ())
        return cursor.fetchone()


def execute_non_query(sql, params=None):
    """Execute INSERT/UPDATE/DELETE."""
    with db_cursor() as (conn, cursor):
        cursor.execute(sql, params or ())
        return cursor.rowcount


def test_connection():
    """Prueba la conexión a la base de datos."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION as version, DB_NAME() as database_name")
        result = cursor.fetchone()
        conn.close()
        return {
            'success': True,
            'version': result['version'] if result else 'Unknown',
            'database': result['database'] if result else 'Unknown'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }