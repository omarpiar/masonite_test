import os
import re
from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from config.db import execute_query, execute_scalar, execute_non_query, db_cursor
from middleware.auth import require_auth, load_permissions, require_module_access

crud_bp = Blueprint('crud', __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'users')
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}


def bool_body(v):
    return v in (True, 'true', 1, '1', 'on')


def only_digits(v):
    return re.sub(r'\D', '', str(v or ''))


def is_valid_phone(v):
    return bool(re.match(r'^\d{10}$', only_digits(v)))


def save_upload(file):
    if not file or file.content_type not in ALLOWED_TYPES:
        return None
    import time, random
    ext = os.path.splitext(file.filename or '')[1].lower() or '.png'
    filename = f"{int(time.time()*1000)}-{random.randint(0,999999999)}{ext}"
    file.save(os.path.join(UPLOAD_DIR, filename))
    return f'/uploads/users/{filename}'


# ── Apply auth to all CRUD routes ────────────────────────────────────────────
@crud_bp.before_request
def before_crud():
    # Auth is checked per route via decorators; here we do nothing
    pass


# ── Catalogues ────────────────────────────────────────────────────────────────
@crud_bp.route('/api/catalogos/base')
@require_auth
@load_permissions
def catalogos_base():
    try:
        perfiles = execute_query('SELECT id, strNombrePerfil FROM Perfil ORDER BY strNombrePerfil')
        estados = execute_query('SELECT id, strNombreEstado FROM EstadoUsuario ORDER BY id')
        modulos = execute_query('SELECT id, strNombreModulo FROM Modulo ORDER BY id')
        menus = execute_query('SELECT id, strNombreMenu FROM Menu ORDER BY intOrdenMenu, id')
        return jsonify({'ok': True, 'perfiles': perfiles, 'estados': estados, 'modulos': modulos, 'menus': menus})
    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@crud_bp.route('/api/static/<module_key>')
@require_auth
@load_permissions
def static_perms(module_key):
    perm = g.permissions.get(module_key)
    if not perm or not perm.get('any'):
        return jsonify({'ok': False, 'message': 'No tienes permiso'}), 403
    return jsonify({'ok': True, 'actions': perm})


# ── Perfiles ──────────────────────────────────────────────────────────────────
@crud_bp.route('/api/perfiles')
@require_auth
@load_permissions
@require_module_access('perfil', 'consulta')
def get_perfiles():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit
    search = f"%{request.args.get('search', '').strip()}%"
    total = execute_scalar('SELECT COUNT(*) AS total FROM Perfil WHERE strNombrePerfil LIKE %s', (search,))['total']
    data = execute_query(
        f'SELECT id, strNombrePerfil, bitAdministrador FROM Perfil WHERE strNombrePerfil LIKE %s ORDER BY id DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY',
        (search,))
    return jsonify({'ok': True, 'data': data, 'page': page, 'totalPages': max(1, -(-total // limit))})


@crud_bp.route('/api/perfiles/<int:pid>')
@require_auth
@load_permissions
@require_module_access('perfil', 'detalle')
def get_perfil(pid):
    row = execute_scalar('SELECT id, strNombrePerfil, bitAdministrador FROM Perfil WHERE id = %s', (pid,))
    return jsonify({'ok': True, 'data': row})


@crud_bp.route('/api/perfiles', methods=['POST'])
@require_auth
@load_permissions
@require_module_access('perfil', 'agregar')
def create_perfil():
    d = request.get_json() or request.form
    execute_non_query('INSERT INTO Perfil (strNombrePerfil, bitAdministrador) VALUES (%s, %s)',
                      (d.get('strNombrePerfil'), int(bool_body(d.get('bitAdministrador')))))
    return jsonify({'ok': True})


@crud_bp.route('/api/perfiles/<int:pid>', methods=['PUT'])
@require_auth
@load_permissions
@require_module_access('perfil', 'editar')
def update_perfil(pid):
    d = request.get_json() or request.form
    execute_non_query('UPDATE Perfil SET strNombrePerfil = %s, bitAdministrador = %s WHERE id = %s',
                      (d.get('strNombrePerfil'), int(bool_body(d.get('bitAdministrador'))), pid))
    return jsonify({'ok': True})


@crud_bp.route('/api/perfiles/<int:pid>', methods=['DELETE'])
@require_auth
@load_permissions
@require_module_access('perfil', 'eliminar')
def delete_perfil(pid):
    execute_non_query('DELETE FROM Perfil WHERE id = %s', (pid,))
    return jsonify({'ok': True})


# ── Módulos ───────────────────────────────────────────────────────────────────
@crud_bp.route('/api/modulos')
@require_auth
@load_permissions
@require_module_access('modulo', 'consulta')
def get_modulos():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit
    search = f"%{request.args.get('search', '').strip()}%"
    total = execute_scalar('SELECT COUNT(*) AS total FROM Modulo WHERE strNombreModulo LIKE %s', (search,))['total']
    data = execute_query(
        f'SELECT id, strNombreModulo, strClaveModulo, strRuta FROM Modulo WHERE strNombreModulo LIKE %s ORDER BY id DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY',
        (search,))
    return jsonify({'ok': True, 'data': data, 'page': page, 'totalPages': max(1, -(-total // limit))})


@crud_bp.route('/api/modulos/<int:mid>')
@require_auth
@load_permissions
@require_module_access('modulo', 'detalle')
def get_modulo(mid):
    row = execute_scalar('SELECT id, strNombreModulo, strClaveModulo, strRuta FROM Modulo WHERE id = %s', (mid,))
    return jsonify({'ok': True, 'data': row})


@crud_bp.route('/api/modulos', methods=['POST'])
@require_auth
@load_permissions
@require_module_access('modulo', 'agregar')
def create_modulo():
    d = request.get_json() or request.form
    execute_non_query('INSERT INTO Modulo (strNombreModulo, strClaveModulo, strRuta) VALUES (%s, %s, %s)',
                      (d.get('strNombreModulo'), d.get('strClaveModulo'), d.get('strRuta')))
    return jsonify({'ok': True})


@crud_bp.route('/api/modulos/<int:mid>', methods=['PUT'])
@require_auth
@load_permissions
@require_module_access('modulo', 'editar')
def update_modulo(mid):
    d = request.get_json() or request.form
    execute_non_query('UPDATE Modulo SET strNombreModulo=%s, strClaveModulo=%s, strRuta=%s WHERE id=%s',
                      (d.get('strNombreModulo'), d.get('strClaveModulo'), d.get('strRuta'), mid))
    return jsonify({'ok': True})


@crud_bp.route('/api/modulos/<int:mid>', methods=['DELETE'])
@require_auth
@load_permissions
@require_module_access('modulo', 'eliminar')
def delete_modulo(mid):
    execute_non_query('DELETE FROM Modulo WHERE id = %s', (mid,))
    return jsonify({'ok': True})


# ── Permisos Perfil ───────────────────────────────────────────────────────────
@crud_bp.route('/api/permisos-perfil')
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'consulta')
def get_permisos_perfil():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit
    id_perfil = int(request.args.get('idPerfil', 0))

    if id_perfil > 0:
        total = execute_scalar('SELECT COUNT(*) AS total FROM Modulo')['total']
        data = execute_query(f"""
            SELECT
                ISNULL(pp.id, 0) AS id,
                m.id AS idModulo,
                %s AS idPerfil,
                ISNULL(pp.bitAgregar, 0) AS bitAgregar,
                ISNULL(pp.bitEditar, 0) AS bitEditar,
                ISNULL(pp.bitConsulta, 0) AS bitConsulta,
                ISNULL(pp.bitEliminar, 0) AS bitEliminar,
                ISNULL(pp.bitDetalle, 0) AS bitDetalle,
                p.strNombrePerfil,
                m.strNombreModulo
            FROM Modulo m
            CROSS JOIN Perfil p
            LEFT JOIN PermisosPerfil pp ON pp.idModulo = m.id AND pp.idPerfil = p.id
            WHERE p.id = %s
            ORDER BY m.id
            OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
        """, (id_perfil, id_perfil))
        return jsonify({'ok': True, 'data': data, 'page': page, 'totalPages': max(1, -(-total // limit))})

    total = execute_scalar('SELECT COUNT(*) AS total FROM PermisosPerfil')['total']
    data = execute_query(
        f'SELECT pp.id, pp.idModulo, pp.idPerfil, pp.bitAgregar, pp.bitEditar, pp.bitConsulta, pp.bitEliminar, pp.bitDetalle, p.strNombrePerfil, m.strNombreModulo FROM PermisosPerfil pp INNER JOIN Perfil p ON p.id = pp.idPerfil INNER JOIN Modulo m ON m.id = pp.idModulo ORDER BY pp.id DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY')
    return jsonify({'ok': True, 'data': data, 'page': page, 'totalPages': max(1, -(-total // limit))})


@crud_bp.route('/api/permisos-perfil/<int:pid>')
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'detalle')
def get_permiso_perfil(pid):
    row = execute_scalar('SELECT id, idModulo, idPerfil, bitAgregar, bitEditar, bitConsulta, bitEliminar, bitDetalle FROM PermisosPerfil WHERE id = %s', (pid,))
    return jsonify({'ok': True, 'data': row})


@crud_bp.route('/api/permisos-perfil', methods=['POST'])
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'agregar')
def create_permiso_perfil():
    d = request.get_json() or request.form
    execute_non_query(
        'INSERT INTO PermisosPerfil (idModulo, idPerfil, bitAgregar, bitEditar, bitConsulta, bitEliminar, bitDetalle) VALUES (%s,%s,%s,%s,%s,%s,%s)',
        (d.get('idModulo'), d.get('idPerfil'), int(bool_body(d.get('bitAgregar'))),
         int(bool_body(d.get('bitEditar'))), int(bool_body(d.get('bitConsulta'))),
         int(bool_body(d.get('bitEliminar'))), int(bool_body(d.get('bitDetalle')))))
    return jsonify({'ok': True})


@crud_bp.route('/api/permisos-perfil/<int:pid>', methods=['PUT'])
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'editar')
def update_permiso_perfil(pid):
    d = request.get_json() or request.form
    id_perfil = int(d.get('idPerfil', 0))
    id_modulo = int(d.get('idModulo', 0))

    if pid > 0:
        execute_non_query(
            'UPDATE PermisosPerfil SET idModulo=%s,idPerfil=%s,bitAgregar=%s,bitEditar=%s,bitConsulta=%s,bitEliminar=%s,bitDetalle=%s WHERE id=%s',
            (id_modulo, id_perfil, int(bool_body(d.get('bitAgregar'))), int(bool_body(d.get('bitEditar'))),
             int(bool_body(d.get('bitConsulta'))), int(bool_body(d.get('bitEliminar'))),
             int(bool_body(d.get('bitDetalle'))), pid))
    else:
        existing = execute_scalar('SELECT TOP 1 id FROM PermisosPerfil WHERE idPerfil=%s AND idModulo=%s', (id_perfil, id_modulo))
        if existing:
            execute_non_query(
                'UPDATE PermisosPerfil SET idModulo=%s,idPerfil=%s,bitAgregar=%s,bitEditar=%s,bitConsulta=%s,bitEliminar=%s,bitDetalle=%s WHERE id=%s',
                (id_modulo, id_perfil, int(bool_body(d.get('bitAgregar'))), int(bool_body(d.get('bitEditar'))),
                 int(bool_body(d.get('bitConsulta'))), int(bool_body(d.get('bitEliminar'))),
                 int(bool_body(d.get('bitDetalle'))), existing['id']))
        else:
            execute_non_query(
                'INSERT INTO PermisosPerfil (idModulo, idPerfil, bitAgregar, bitEditar, bitConsulta, bitEliminar, bitDetalle) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                (id_modulo, id_perfil, int(bool_body(d.get('bitAgregar'))), int(bool_body(d.get('bitEditar'))),
                 int(bool_body(d.get('bitConsulta'))), int(bool_body(d.get('bitEliminar'))),
                 int(bool_body(d.get('bitDetalle')))))
    return jsonify({'ok': True})


@crud_bp.route('/api/permisos-perfil/<int:pid>', methods=['DELETE'])
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'eliminar')
def delete_permiso_perfil(pid):
    execute_non_query('DELETE FROM PermisosPerfil WHERE id = %s', (pid,))
    return jsonify({'ok': True})


# ── Usuarios ──────────────────────────────────────────────────────────────────
@crud_bp.route('/api/usuarios')
@require_auth
@load_permissions
@require_module_access('usuario', 'consulta')
def get_usuarios():
    page = int(request.args.get('page', 1))
    limit = 5
    offset = (page - 1) * limit
    search = f"%{request.args.get('search', '').strip()}%"
    total = execute_scalar('SELECT COUNT(*) AS total FROM Usuario WHERE strNombreUsuario LIKE %s OR strCorreo LIKE %s', (search, search))['total']
    data = execute_query(
        f'SELECT u.id, u.strNombreUsuario, u.idPerfil, u.strPwd, u.idEstadoUsuario, u.strCorreo, u.strNumeroCelular, u.strImagen, p.strNombrePerfil, eu.strNombreEstado FROM Usuario u INNER JOIN Perfil p ON p.id = u.idPerfil INNER JOIN EstadoUsuario eu ON eu.id = u.idEstadoUsuario WHERE u.strNombreUsuario LIKE %s OR u.strCorreo LIKE %s ORDER BY u.id DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY',
        (search, search))
    return jsonify({'ok': True, 'data': data, 'page': page, 'totalPages': max(1, -(-total // limit))})


@crud_bp.route('/api/usuarios/<int:uid>')
@require_auth
@load_permissions
@require_module_access('usuario', 'detalle')
def get_usuario(uid):
    row = execute_scalar('SELECT id, strNombreUsuario, idPerfil, strPwd, idEstadoUsuario, strCorreo, strNumeroCelular, strImagen FROM Usuario WHERE id = %s', (uid,))
    return jsonify({'ok': True, 'data': row})


@crud_bp.route('/api/usuarios', methods=['POST'])
@require_auth
@load_permissions
@require_module_access('usuario', 'agregar')
def create_usuario():
    telefono = only_digits(request.form.get('strNumeroCelular', ''))
    if not is_valid_phone(telefono):
        return jsonify({'ok': False, 'message': 'El número de teléfono debe tener exactamente 10 dígitos.'}), 400
    imagen = save_upload(request.files.get('strImagen'))
    execute_non_query(
        'INSERT INTO Usuario (strNombreUsuario, idPerfil, strPwd, idEstadoUsuario, strCorreo, strNumeroCelular, strImagen) VALUES (%s,%s,%s,%s,%s,%s,%s)',
        (request.form.get('strNombreUsuario'), request.form.get('idPerfil'),
         request.form.get('strPwd'), request.form.get('idEstadoUsuario'),
         request.form.get('strCorreo'), telefono, imagen))
    return jsonify({'ok': True})


@crud_bp.route('/api/usuarios/<int:uid>', methods=['PUT'])
@require_auth
@load_permissions
@require_module_access('usuario', 'editar')
def update_usuario(uid):
    telefono = only_digits(request.form.get('strNumeroCelular', ''))
    if not is_valid_phone(telefono):
        return jsonify({'ok': False, 'message': 'El número de teléfono debe tener exactamente 10 dígitos.'}), 400
    if request.files.get('strImagen'):
        imagen = save_upload(request.files.get('strImagen'))
    else:
        old = execute_scalar('SELECT strImagen FROM Usuario WHERE id = %s', (uid,))
        imagen = old['strImagen'] if old else None
    execute_non_query(
        'UPDATE Usuario SET strNombreUsuario=%s, idPerfil=%s, strPwd=%s, idEstadoUsuario=%s, strCorreo=%s, strNumeroCelular=%s, strImagen=%s WHERE id=%s',
        (request.form.get('strNombreUsuario'), request.form.get('idPerfil'),
         request.form.get('strPwd'), request.form.get('idEstadoUsuario'),
         request.form.get('strCorreo'), telefono, imagen, uid))
    return jsonify({'ok': True})


@crud_bp.route('/api/usuarios/<int:uid>', methods=['DELETE'])
@require_auth
@load_permissions
@require_module_access('usuario', 'eliminar')
def delete_usuario(uid):
    execute_non_query('DELETE FROM Usuario WHERE id = %s', (uid,))
    return jsonify({'ok': True})
