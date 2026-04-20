from flask import Blueprint, render_template, g
from middleware.auth import require_auth, load_permissions, require_module_access
from services.dashboard_data import get_dashboard_payload

seguridad_bp = Blueprint('seguridad', __name__)


def render_seguridad_view(view_name, initial_module):
    payload = get_dashboard_payload(g.user, g.permissions)
    return render_template('dashboard.html', **payload, initial_module=initial_module)


@seguridad_bp.route('/seguridad/perfil')
@require_auth
@load_permissions
@require_module_access('perfil', 'consulta')
def perfil():
    return render_seguridad_view('perfil', {
        'menuName': 'Seguridad', 'moduleKey': 'perfil', 'moduleName': 'Perfil'
    })


@seguridad_bp.route('/seguridad/modulo')
@require_auth
@load_permissions
@require_module_access('modulo', 'consulta')
def modulo():
    return render_seguridad_view('modulo', {
        'menuName': 'Seguridad', 'moduleKey': 'modulo', 'moduleName': 'Módulo'
    })


@seguridad_bp.route('/seguridad/permisos-perfil')
@require_auth
@load_permissions
@require_module_access('permisos_perfil', 'consulta')
def permisos_perfil():
    return render_seguridad_view('permisos-perfil', {
        'menuName': 'Seguridad', 'moduleKey': 'permisos_perfil', 'moduleName': 'Permisos Perfil'
    })


@seguridad_bp.route('/seguridad/usuario')
@require_auth
@load_permissions
@require_module_access('usuario', 'consulta')
def usuario():
    return render_seguridad_view('usuario', {
        'menuName': 'Seguridad', 'moduleKey': 'usuario', 'moduleName': 'Usuario'
    })
