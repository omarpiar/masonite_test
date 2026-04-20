# services/dashboard_data.py
from config.db import execute_query, execute_scalar, execute_non_query
from datetime import datetime


def get_dashboard_payload(user_jwt, permissions):
    """
    Obtiene el payload completo para el dashboard de Masonite
    """
    # Obtener menús y módulos
    rows = execute_query("""
        SELECT
            mn.id AS idMenu,
            mn.strNombreMenu,
            mn.intOrdenMenu,
            m.id AS idModulo,
            m.strNombreModulo,
            m.strClaveModulo,
            m.strRuta,
            ISNULL(pp.bitAgregar, 0) AS bitAgregar,
            ISNULL(pp.bitEditar, 0) AS bitEditar,
            ISNULL(pp.bitConsulta, 0) AS bitConsulta,
            ISNULL(pp.bitEliminar, 0) AS bitEliminar,
            ISNULL(pp.bitDetalle, 0) AS bitDetalle
        FROM Menu mn
        INNER JOIN MenuModulo mm ON mm.idMenu = mn.id
        INNER JOIN Modulo m ON m.id = mm.idModulo
        LEFT JOIN PermisosPerfil pp
            ON pp.idModulo = m.id AND pp.idPerfil = %s
        ORDER BY mn.intOrdenMenu, m.id
    """, (user_jwt['idPerfil'],))

    menu_map = {}
    for row in rows:
        allowed = bool(row['bitAgregar'] or row['bitEditar'] or row['bitConsulta'] or row['bitEliminar'] or row['bitDetalle'])
        mid = row['idMenu']
        if mid not in menu_map:
            menu_map[mid] = {'id': mid, 'nombre': row['strNombreMenu'], 'modulos': []}
        if allowed:
            menu_map[mid]['modulos'].append({
                'id': row['idModulo'],
                'nombre': row['strNombreModulo'],
                'clave': row['strClaveModulo'],
                'ruta': row['strRuta']
            })

    visible_menus = [m for m in menu_map.values() if m['modulos']]

    # Obtener información del usuario
    user_row = execute_scalar("""
        SELECT 
            u.id, 
            u.strNombreUsuario, 
            u.strCorreo, 
            u.strNumeroCelular, 
            u.strImagen, 
            p.strNombrePerfil,
            p.bitAdministrador
        FROM Usuario u
        INNER JOIN Perfil p ON p.id = u.idPerfil
        WHERE u.id = %s
    """, (user_jwt['idUsuario'],))

    # Obtener estadísticas del dashboard
    dashboard_stats = get_dashboard_statistics(user_jwt['idUsuario'])
    
    return {
        'user': user_row,
        'menus': visible_menus,
        'permissions': permissions,
        'dashboard_stats': dashboard_stats
    }


def get_dashboard_statistics(user_id=None):
    """
    Obtiene estadísticas para el dashboard de Masonite
    
    Args:
        user_id (int, optional): ID del usuario actual para estadísticas personalizadas
    """
    stats = {}
    
    try:
        # Total de usuarios
        result = execute_scalar("SELECT COUNT(*) AS total FROM Usuario")
        stats['totalUsuarios'] = result['total'] if result and 'total' in result else 0
        
        # Total de perfiles
        result = execute_scalar("SELECT COUNT(*) AS total FROM Perfil")
        stats['totalPerfiles'] = result['total'] if result and 'total' in result else 0
        
        # Usuarios activos (con estado activo - idEstadoUsuario = 1)
        result = execute_scalar("SELECT COUNT(*) AS total FROM Usuario WHERE idEstadoUsuario = 1")
        stats['usuariosActivos'] = result['total'] if result and 'total' in result else 0
        
        # Módulos activos (todos los módulos del sistema)
        result = execute_scalar("SELECT COUNT(*) AS total FROM Modulo")
        stats['modulosActivos'] = result['total'] if result and 'total' in result else 0
        
        # Total de permisos asignados
        result = execute_scalar("""
            SELECT COUNT(*) AS total FROM PermisosPerfil
            WHERE bitAgregar = 1 
               OR bitEditar = 1 
               OR bitConsulta = 1 
               OR bitEliminar = 1 
               OR bitDetalle = 1
        """)
        stats['permisosAsignados'] = result['total'] if result and 'total' in result else 0
        
        # Usuarios administradores (con perfil administrador)
        result = execute_scalar("""
            SELECT COUNT(*) AS total FROM Usuario u
            INNER JOIN Perfil p ON p.id = u.idPerfil
            WHERE p.bitAdministrador = 1
        """)
        stats['usuariosAdmin'] = result['total'] if result and 'total' in result else 0
        
        # Perfiles activos (que tienen al menos un usuario asignado)
        result = execute_scalar("""
            SELECT COUNT(DISTINCT p.id) AS total
            FROM Perfil p
            INNER JOIN Usuario u ON u.idPerfil = p.id
        """)
        stats['perfilesActivos'] = result['total'] if result and 'total' in result else 0
        
        # Módulos con permisos asignados
        result = execute_scalar("""
            SELECT COUNT(DISTINCT idModulo) AS total
            FROM PermisosPerfil
            WHERE bitAgregar = 1 
               OR bitEditar = 1 
               OR bitConsulta = 1 
               OR bitEliminar = 1 
               OR bitDetalle = 1
        """)
        stats['modulosConPermisos'] = result['total'] if result and 'total' in result else 0
        
        # Último acceso
        stats['ultimoAcceso'] = "Hoy"
        if user_id:
            # Verificar si existe la tabla BitacoraAcceso
            try:
                ultimo_usuario = execute_scalar("""
                    SELECT TOP 1 dtmFechaAcceso
                    FROM BitacoraAcceso 
                    WHERE idUsuario = %s
                    ORDER BY dtmFechaAcceso DESC
                """, (user_id,))
                
                if ultimo_usuario and 'dtmFechaAcceso' in ultimo_usuario:
                    fecha = ultimo_usuario['dtmFechaAcceso']
                    if hasattr(fecha, 'strftime'):
                        stats['ultimoAcceso'] = fecha.strftime("%d/%m/%Y %H:%M")
                    else:
                        stats['ultimoAcceso'] = str(fecha)[:16]
            except Exception as e:
                print(f"Tabla BitacoraAcceso no existe o error: {e}")
                stats['ultimoAcceso'] = "Primer acceso"
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        import traceback
        traceback.print_exc()
        # Valores por defecto en caso de error
        stats = {
            'totalUsuarios': 0,
            'totalPerfiles': 0,
            'usuariosActivos': 0,
            'modulosActivos': 0,
            'permisosAsignados': 0,
            'usuariosAdmin': 0,
            'perfilesActivos': 0,
            'modulosConPermisos': 0,
            'ultimoAcceso': 'N/A'
        }
    
    return stats


def registrar_acceso(usuario_id):
    """
    Registra el acceso del usuario en la bitácora
    """
    try:
        # Verificar si existe la tabla BitacoraAcceso
        check_table = execute_scalar("""
            SELECT COUNT(*) AS existe 
            FROM sysobjects 
            WHERE name='BitacoraAcceso' AND xtype='U'
        """)
        
        if not check_table or check_table.get('existe', 0) == 0:
            # Crear la tabla
            execute_non_query("""
                CREATE TABLE BitacoraAcceso (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    idUsuario INT NOT NULL,
                    dtmFechaAcceso DATETIME NOT NULL,
                    FOREIGN KEY (idUsuario) REFERENCES Usuario(id)
                )
            """)
            print("✅ Tabla BitacoraAcceso creada")
        
        # Insertar registro de acceso
        execute_non_query("""
            INSERT INTO BitacoraAcceso (idUsuario, dtmFechaAcceso)
            VALUES (%s, GETDATE())
        """, (usuario_id,))
        
        print(f"✅ Acceso registrado para usuario ID: {usuario_id}")
        return True
        
    except Exception as e:
        print(f"Error registrando acceso: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_dashboard_stats_api():
    """
    Endpoint para obtener solo las estadísticas (útil para actualizaciones AJAX)
    """
    return get_dashboard_statistics()