from flask import Blueprint, render_template, g
from middleware.auth import require_auth, load_permissions, require_module_access
from services.dashboard_data import get_dashboard_payload

static_bp = Blueprint('static_routes', __name__)

STATIC_MODULES = [
    {'path': '/principal-1-1', 'menuName': 'Principal 1', 'moduleKey': 'principal_1_1', 'moduleName': 'Principal 1.1'},
    {'path': '/principal-1-2', 'menuName': 'Principal 1', 'moduleKey': 'principal_1_2', 'moduleName': 'Principal 1.2'},
    {'path': '/principal-2-1', 'menuName': 'Principal 2', 'moduleKey': 'principal_2_1', 'moduleName': 'Principal 2.1'},
    {'path': '/principal-2-2', 'menuName': 'Principal 2', 'moduleKey': 'principal_2_2', 'moduleName': 'Principal 2.2'},
]


def make_static_view(module_info):
    @require_auth
    @load_permissions
    @require_module_access(module_info['moduleKey'], 'consulta')
    def view():
        payload = get_dashboard_payload(g.user, g.permissions)
        return render_template('dashboard.html', **payload, initial_module=module_info)
    view.__name__ = f"static_{module_info['moduleKey']}"
    return view


for mod in STATIC_MODULES:
    static_bp.add_url_rule(mod['path'], endpoint=f"static_{mod['moduleKey']}", view_func=make_static_view(mod))
