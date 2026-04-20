# test_db.py
from config.db import test_connection, execute_scalar, execute_query

# Probar conexión
print("🔌 Probando conexión...")
result = test_connection()
print(f"✅ Conexión exitosa: {result['success']}")
if result['success']:
    print(f"📦 Base de datos: {result['database']}")
    print(f"🖥️  Versión SQL Server: {result['version'][:100]}...")
else:
    print(f"❌ Error: {result.get('error', 'Unknown error')}")
    exit(1)

print("\n" + "="*50)

# Probar consulta simple
print("\n🔍 Probando execute_scalar (SELECT * FROM Usuario)...")
try:
    user = execute_scalar("SELECT TOP 1 * FROM Usuario")
    if user:
        print(f"✅ Usuario encontrado:")
        for key, value in user.items():
            print(f"   {key}: {value}")
    else:
        print("ℹ️  No hay usuarios en la tabla")
except Exception as e:
    print(f"❌ Error en execute_scalar: {e}")

print("\n" + "="*50)

# Probar consulta múltiple
print("\n🔍 Probando execute_query (SELECT TOP 3 * FROM Perfil)...")
try:
    perfiles = execute_query("SELECT TOP 3 * FROM Perfil")
    if perfiles:
        print(f"✅ {len(perfiles)} perfiles encontrados:")
        for i, perfil in enumerate(perfiles, 1):
            print(f"\n   Perfil #{i}:")
            for key, value in perfil.items():
                print(f"      {key}: {value}")
    else:
        print("ℹ️  No hay perfiles en la tabla")
except Exception as e:
    print(f"❌ Error en execute_query: {e}")

print("\n" + "="*50)
print("\n✅ ¡Todas las pruebas completadas!")