import os
import jwt
from functools import wraps
from flask import request, redirect, jsonify, g
from config.db import execute_query

JWT_SECRET = os.getenv('JWT_SECRET', 'mi_servidor_jwt_secret_2026')


def sign_token(user):
    import time
    payload = {
        'idUsuario': user['idUsuario'],
        'idPerfil': user['idPerfil'],
        'nombre': user['strNombreUsuario'],
        'administrador': bool(user.get('bitAdministrador')),
        'exp': int(time.time()) + 8 * 3600
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def get_token_from_request():
    cookie = request.cookies.get('token')
    if cookie:
        return cookie
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return redirect('/')
        try:
            g.user = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return redirect('/')
        except jwt.InvalidTokenError:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated


def load_permissions(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            rows = execute_query("""
                SELECT
                    m.id,
                    m.strNombreModulo,
                    m.strClaveModulo,
                    m.strRuta,
                    ISNULL(pp.bitAgregar, 0) AS bitAgregar,
                    ISNULL(pp.bitEditar, 0) AS bitEditar,
                    ISNULL(pp.bitConsulta, 0) AS bitConsulta,
                    ISNULL(pp.bitEliminar, 0) AS bitEliminar,
                    ISNULL(pp.bitDetalle, 0) AS bitDetalle
                FROM Modulo m
                LEFT JOIN PermisosPerfil pp
                    ON pp.idModulo = m.id
                   AND pp.idPerfil = %s
            """, (g.user['idPerfil'],))

            permissions = {}
            for row in rows:
                key = row['strClaveModulo']
                permissions[key] = {
                    'idModulo': row['id'],
                    'nombre': row['strNombreModulo'],
                    'ruta': row['strRuta'],
                    'agregar': bool(row['bitAgregar']),
                    'editar': bool(row['bitEditar']),
                    'consulta': bool(row['bitConsulta']),
                    'eliminar': bool(row['bitEliminar']),
                    'detalle': bool(row['bitDetalle']),
                    'any': bool(row['bitAgregar'] or row['bitEditar'] or row['bitConsulta'] or row['bitEliminar'] or row['bitDetalle'])
                }
            g.permissions = permissions
        except Exception as e:
            g.permissions = {}
        return f(*args, **kwargs)
    return decorated


def require_module_access(module_key, action=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            perm = g.permissions.get(module_key)
            if not perm or not perm.get('any'):
                if request.path.startswith('/api/'):
                    return jsonify({'ok': False, 'message': 'No tienes permiso'}), 403
                return redirect('/')
            if action and not perm.get(action):
                return jsonify({'ok': False, 'message': 'No tienes permiso para esta acción'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
