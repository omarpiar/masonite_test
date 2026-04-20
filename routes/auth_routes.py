import os
import requests as http_requests
from flask import Blueprint, render_template, request, redirect, make_response, g
from config.db import execute_scalar
from middleware.auth import sign_token, require_auth, load_permissions
from services.dashboard_data import get_dashboard_payload, registrar_acceso

auth_bp = Blueprint('auth', __name__)

RECAPTCHA_SECRET = os.getenv('RECAPTCHA_SECRET', '6LebTlYsAAAAAD0Q3XM3e6ah7CctvUEK4OEclWDR')
RECAPTCHA_SITE = os.getenv('RECAPTCHA_SITE', '6LebTlYsAAAAADnLSamRI9p-VJYYovtlyxHeRD-8')


@auth_bp.route('/')
def login_page():
    error = request.args.get('error', '')
    return render_template('login.html', error=error, site_key=RECAPTCHA_SITE)


@auth_bp.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario', '')
    password = request.form.get('password', '')
    captcha = request.form.get('g-recaptcha-response', '')

    if not captcha:
        return redirect('/?error=Verifica el reCAPTCHA')

    try:
        captcha_resp = http_requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            params={'secret': RECAPTCHA_SECRET, 'response': captcha},
            timeout=5
        )
        if not captcha_resp.json().get('success'):
            return redirect('/?error=Captcha inválido')
    except Exception:
        return redirect('/?error=Error al verificar captcha')

    try:
        user = execute_scalar("""
            SELECT TOP 1
                u.id AS idUsuario,
                u.strNombreUsuario,
                u.strPwd,
                u.idPerfil,
                u.idEstadoUsuario,
                u.strCorreo,
                p.bitAdministrador,
                eu.strNombreEstado
            FROM Usuario u
            INNER JOIN Perfil p ON p.id = u.idPerfil
            INNER JOIN EstadoUsuario eu ON eu.id = u.idEstadoUsuario
            WHERE u.strNombreUsuario = %s OR u.strCorreo = %s
        """, (usuario, usuario))

        if not user:
            return redirect('/?error=Usuario o contraseña incorrectos')
        if user['strPwd'] != password:
            return redirect('/?error=Usuario o contraseña incorrectos')
        if user['idEstadoUsuario'] != 1:
            return redirect('/?error=El usuario no existe o está inactivo')

        # Registrar acceso en bitácora
        registrar_acceso(user['idUsuario'])
        
        token = sign_token(user)
        resp = make_response(redirect('/dashboard'))
        resp.set_cookie('token', token, httponly=True, samesite='Lax')
        return resp

    except Exception as e:
        print(f"Error en login: {e}")
        return redirect('/?error=Error interno al iniciar sesión')


@auth_bp.route('/dashboard')
@require_auth
@load_permissions
def dashboard():
    payload = get_dashboard_payload(g.user, g.permissions)
    return render_template('dashboard.html', **payload, initial_module=None)


@auth_bp.route('/api/dashboard/stats')
@require_auth
def api_dashboard_stats():
    """Endpoint para actualizar estadísticas vía AJAX"""
    from services.dashboard_data import get_dashboard_stats_api
    from flask import jsonify
    return jsonify(get_dashboard_stats_api())


@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('token')
    return resp