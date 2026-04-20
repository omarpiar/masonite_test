"""
seed.py — Poblar la base de datos con datos iniciales
=====================================================
Ejecutar UNA sola vez para crear:
  - EstadoUsuario (Activo / Inactivo)
  - Perfiles (Administrador, Operador)
  - Menús y Módulos del sistema
  - MenuModulo (relaciones)
  - Usuario admin con todos los permisos
  - Usuario operador con permisos limitados
  - PermisosPerfil para ambos perfiles

Uso:
    python seed.py

    # Para forzar recreación aunque ya existan datos:
    python seed.py --force
"""

import sys
import pymssql

DB = {
    'server':   'db47937.public.databaseasp.net',
    'user':     'db47937',
    'password': '5t#LE-8c+xD3',
    'database': 'db47937',
    'port':     1433,
}

FORCE = '--force' in sys.argv


def connect():
    return pymssql.connect(
        server=DB['server'], user=DB['user'], password=DB['password'],
        database=DB['database'], port=DB['port'], as_dict=True, charset='UTF-8'
    )


def run(cursor, sql, params=None):
    cursor.execute(sql, params or ())


def ok(msg):  print(f"  ✅  {msg}")
def skip(msg): print(f"  ⏭️   {msg} (ya existe, usa --force para reescribir)")
def info(msg): print(f"  ℹ️   {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PARA CREAR TABLAS SI NO EXISTEN
# ─────────────────────────────────────────────────────────────────────────────

def crear_tablas_si_no_existen(cur):
    """Crea las tablas necesarias si no existen"""
    print("\n📌 Verificando/Creando tablas...")
    
    tablas = {
        'EstadoUsuario': """
            CREATE TABLE EstadoUsuario (
                id INT PRIMARY KEY IDENTITY(1,1),
                strNombreEstado VARCHAR(50) NOT NULL
            )
        """,
        'Perfil': """
            CREATE TABLE Perfil (
                id INT PRIMARY KEY IDENTITY(1,1),
                strNombrePerfil VARCHAR(100) NOT NULL,
                bitAdministrador BIT NOT NULL
            )
        """,
        'Menu': """
            CREATE TABLE Menu (
                id INT PRIMARY KEY IDENTITY(1,1),
                strNombreMenu VARCHAR(100) NOT NULL,
                intOrdenMenu INT NOT NULL
            )
        """,
        'Modulo': """
            CREATE TABLE Modulo (
                id INT PRIMARY KEY IDENTITY(1,1),
                strNombreModulo VARCHAR(100) NOT NULL,
                strClaveModulo VARCHAR(50) NOT NULL,
                strRuta VARCHAR(255) NOT NULL
            )
        """,
        'MenuModulo': """
            CREATE TABLE MenuModulo (
                id INT PRIMARY KEY IDENTITY(1,1),
                idMenu INT NOT NULL,
                idModulo INT NOT NULL,
                FOREIGN KEY (idMenu) REFERENCES Menu(id),
                FOREIGN KEY (idModulo) REFERENCES Modulo(id)
            )
        """,
        'Usuario': """
            CREATE TABLE Usuario (
                id INT PRIMARY KEY IDENTITY(1,1),
                strNombreUsuario VARCHAR(100) NOT NULL,
                idPerfil INT NOT NULL,
                strPwd VARCHAR(255) NOT NULL,
                idEstadoUsuario INT NOT NULL,
                strCorreo VARCHAR(255),
                strNumeroCelular VARCHAR(20),
                strImagen VARCHAR(255),
                FOREIGN KEY (idPerfil) REFERENCES Perfil(id),
                FOREIGN KEY (idEstadoUsuario) REFERENCES EstadoUsuario(id)
            )
        """,
        'PermisosPerfil': """
            CREATE TABLE PermisosPerfil (
                id INT PRIMARY KEY IDENTITY(1,1),
                idModulo INT NOT NULL,
                idPerfil INT NOT NULL,
                bitAgregar BIT NOT NULL,
                bitEditar BIT NOT NULL,
                bitConsulta BIT NOT NULL,
                bitEliminar BIT NOT NULL,
                bitDetalle BIT NOT NULL,
                FOREIGN KEY (idModulo) REFERENCES Modulo(id),
                FOREIGN KEY (idPerfil) REFERENCES Perfil(id)
            )
        """
    }
    
    for nombre_tabla, sql_creacion in tablas.items():
        try:
            # Verificar si la tabla existe en SQL Server
            cur.execute(f"""
                SELECT COUNT(*) as existe 
                FROM sysobjects 
                WHERE name='{nombre_tabla}' AND xtype='U'
            """)
            if cur.fetchone()['existe'] == 0:
                cur.execute(sql_creacion)
                print(f"  ✅ Tabla {nombre_tabla} creada")
            else:
                print(f"  ⏭️  Tabla {nombre_tabla} ya existe")
        except Exception as e:
            print(f"  ❌ Error creando tabla {nombre_tabla}: {e}")
            raise


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE SEED (POBLADO DE DATOS)
# ─────────────────────────────────────────────────────────────────────────────

def seed_estados(cur):
    print("\n📌 EstadoUsuario")
    cur.execute("SELECT COUNT(*) AS c FROM EstadoUsuario")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("EstadoUsuario")
    if FORCE:
        cur.execute("DELETE FROM EstadoUsuario")
    cur.execute("INSERT INTO EstadoUsuario (strNombreEstado) VALUES ('Activo')")
    cur.execute("INSERT INTO EstadoUsuario (strNombreEstado) VALUES ('Inactivo')")
    ok("Activo, Inactivo insertados")


def seed_perfiles(cur):
    print("\n📌 Perfil")
    cur.execute("SELECT COUNT(*) AS c FROM Perfil")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("Perfil")
    if FORCE:
        cur.execute("DELETE FROM Perfil")
    cur.execute("INSERT INTO Perfil (strNombrePerfil, bitAdministrador) VALUES ('Administrador', 1)")
    cur.execute("INSERT INTO Perfil (strNombrePerfil, bitAdministrador) VALUES ('Operador', 0)")
    ok("Administrador, Operador insertados")


def seed_menus(cur):
    print("\n📌 Menu")
    cur.execute("SELECT COUNT(*) AS c FROM Menu")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("Menu")
    if FORCE:
        cur.execute("DELETE FROM MenuModulo")
        cur.execute("DELETE FROM Menu")
    for nombre, orden in [('Seguridad', 1), ('Principal 1', 2), ('Principal 2', 3)]:
        cur.execute("INSERT INTO Menu (strNombreMenu, intOrdenMenu) VALUES (%s, %d)", (nombre, orden))
    ok("Seguridad, Principal 1, Principal 2 insertados")


def seed_modulos(cur):
    print("\n📌 Modulo")
    cur.execute("SELECT COUNT(*) AS c FROM Modulo")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("Modulo")
    if FORCE:
        cur.execute("DELETE FROM MenuModulo")
        cur.execute("DELETE FROM PermisosPerfil")
        cur.execute("DELETE FROM Modulo")
    modulos = [
        ('Perfil',         'perfil',         '/seguridad/perfil'),
        ('Módulo',         'modulo',         '/seguridad/modulo'),
        ('Permisos Perfil','permisos_perfil','/seguridad/permisos-perfil'),
        ('Usuario',        'usuario',        '/seguridad/usuario'),
        ('Principal 1.1',  'principal_1_1',  '/principal-1-1'),
        ('Principal 1.2',  'principal_1_2',  '/principal-1-2'),
        ('Principal 2.1',  'principal_2_1',  '/principal-2-1'),
        ('Principal 2.2',  'principal_2_2',  '/principal-2-2'),
    ]
    for nombre, clave, ruta in modulos:
        cur.execute(
            "INSERT INTO Modulo (strNombreModulo, strClaveModulo, strRuta) VALUES (%s, %s, %s)",
            (nombre, clave, ruta)
        )
    ok(f"{len(modulos)} módulos insertados")


def seed_menu_modulo(cur):
    print("\n📌 MenuModulo")
    cur.execute("SELECT COUNT(*) AS c FROM MenuModulo")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("MenuModulo")
    if FORCE:
        cur.execute("DELETE FROM MenuModulo")

    # Obtenemos IDs reales
    cur.execute("SELECT id, strNombreMenu FROM Menu ORDER BY intOrdenMenu")
    menus = {r['strNombreMenu']: r['id'] for r in cur.fetchall()}

    cur.execute("SELECT id, strClaveModulo FROM Modulo ORDER BY id")
    mods = {r['strClaveModulo']: r['id'] for r in cur.fetchall()}

    relaciones = [
        ('Seguridad',   ['perfil','modulo','permisos_perfil','usuario']),
        ('Principal 1', ['principal_1_1','principal_1_2']),
        ('Principal 2', ['principal_2_1','principal_2_2']),
    ]

    total = 0
    for menu_nombre, claves in relaciones:
        mid = menus.get(menu_nombre)
        if not mid:
            info(f"Menú '{menu_nombre}' no encontrado, omitido")
            continue
        for clave in claves:
            mod_id = mods.get(clave)
            if not mod_id:
                info(f"Módulo '{clave}' no encontrado, omitido")
                continue
            cur.execute(
                "INSERT INTO MenuModulo (idMenu, idModulo) VALUES (%d, %d)",
                (mid, mod_id)
            )
            total += 1
    ok(f"{total} relaciones MenuModulo insertadas")


def seed_usuarios(cur):
    print("\n📌 Usuario")
    cur.execute("SELECT COUNT(*) AS c FROM Usuario")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("Usuario")
    if FORCE:
        cur.execute("DELETE FROM Usuario")

    # IDs reales
    cur.execute("SELECT TOP 1 id FROM Perfil WHERE bitAdministrador = 1")
    r = cur.fetchone()
    id_admin = r['id'] if r else 1

    cur.execute("SELECT TOP 1 id FROM Perfil WHERE bitAdministrador = 0")
    r = cur.fetchone()
    id_operador = r['id'] if r else 2

    cur.execute("SELECT TOP 1 id FROM EstadoUsuario WHERE strNombreEstado = 'Activo'")
    r = cur.fetchone()
    id_activo = r['id'] if r else 1

    usuarios = [
        # (usuario, idPerfil, pwd, idEstado, correo, celular)
        ('admin',    id_admin,    'Admin123',  id_activo, 'admin@empresa.com',    '5511111111'),
        ('operador', id_operador, 'Oper456',   id_activo, 'operador@empresa.com', '5522222222'),
    ]
    for u, ip, pwd, ie, correo, cel in usuarios:
        cur.execute(
            "INSERT INTO Usuario (strNombreUsuario, idPerfil, strPwd, idEstadoUsuario, strCorreo, strNumeroCelular, strImagen) "
            "VALUES (%s, %d, %s, %d, %s, %s, NULL)",
            (u, ip, pwd, ie, correo, cel)
        )
    ok(f"{len(usuarios)} usuarios creados")
    info("Usuario: admin     / Contraseña: Admin123")
    info("Usuario: operador  / Contraseña: Oper456")


def seed_permisos(cur):
    print("\n📌 PermisosPerfil")
    cur.execute("SELECT COUNT(*) AS c FROM PermisosPerfil")
    if cur.fetchone()['c'] > 0 and not FORCE:
        return skip("PermisosPerfil")
    if FORCE:
        cur.execute("DELETE FROM PermisosPerfil")

    cur.execute("SELECT id FROM Modulo ORDER BY id")
    modulos = [r['id'] for r in cur.fetchall()]

    cur.execute("SELECT TOP 1 id FROM Perfil WHERE bitAdministrador = 1")
    r = cur.fetchone()
    id_admin = r['id'] if r else 1

    cur.execute("SELECT TOP 1 id FROM Perfil WHERE bitAdministrador = 0")
    r = cur.fetchone()
    id_operador = r['id'] if r else 2

    cur.execute("SELECT id, strClaveModulo FROM Modulo")
    mod_map = {r['strClaveModulo']: r['id'] for r in cur.fetchall()}

    # Administrador — acceso total a todo
    for mid in modulos:
        cur.execute(
            "INSERT INTO PermisosPerfil (idModulo, idPerfil, bitAgregar, bitEditar, bitConsulta, bitEliminar, bitDetalle) "
            "VALUES (%d, %d, 1, 1, 1, 1, 1)",
            (mid, id_admin)
        )
    ok(f"Administrador: permisos totales en {len(modulos)} módulos")

    # Operador — solo consulta y detalle en algunos módulos
    permisos_operador = {
        'perfil':         (0, 0, 1, 0, 1),
        'usuario':        (0, 0, 1, 0, 1),
        'principal_1_1':  (0, 0, 1, 0, 0),
        'principal_2_1':  (0, 0, 1, 0, 0),
    }
    total_op = 0
    for clave, (agr, edi, con, eli, det) in permisos_operador.items():
        mid = mod_map.get(clave)
        if not mid:
            continue
        cur.execute(
            "INSERT INTO PermisosPerfil (idModulo, idPerfil, bitAgregar, bitEditar, bitConsulta, bitEliminar, bitDetalle) "
            "VALUES (%d, %d, %d, %d, %d, %d, %d)",
            (mid, id_operador, agr, edi, con, eli, det)
        )
        total_op += 1
    ok(f"Operador: permisos limitados en {total_op} módulos")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  🌱  SEED — CorpSystem Base de Datos")
    if FORCE:
        print("  ⚠️   Modo FORCE activado — se borrarán datos existentes")
    print("=" * 55)

    try:
        conn = connect()
        print(f"\n✅ Conectado a {DB['server']} / {DB['database']}\n")
    except Exception as e:
        print(f"\n❌ No se pudo conectar: {e}")
        sys.exit(1)

    cur = conn.cursor()

    try:
        # PRIMERO: Crear las tablas si no existen
        crear_tablas_si_no_existen(cur)
        conn.commit()
        
        # SEGUNDO: Poblar los datos
        seed_estados(cur)
        seed_perfiles(cur)
        seed_menus(cur)
        seed_modulos(cur)
        seed_menu_modulo(cur)
        seed_usuarios(cur)
        seed_permisos(cur)
        
        conn.commit()
        
        print("\n" + "=" * 55)
        print("  🎉  Seed completado exitosamente")
        print("=" * 55)
        print("\n  Credenciales de acceso:")
        print("  ┌─────────────┬──────────────┬───────────────────┐")
        print("  │ Usuario     │ Contraseña   │ Perfil            │")
        print("  ├─────────────┼──────────────┼───────────────────┤")
        print("  │ admin       │ Admin123     │ Administrador     │")
        print("  │ operador    │ Oper456      │ Operador          │")
        print("  └─────────────┴──────────────┴───────────────────┘\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()