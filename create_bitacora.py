# create_bitacora.py
"""
Script para crear la tabla BitacoraAcceso
Ejecutar: python create_bitacora.py
"""
from config.db import execute_scalar, execute_non_query

def create_bitacora_table():
    try:
        # Verificar si existe la tabla
        check_table = execute_scalar("""
            SELECT COUNT(*) AS existe 
            FROM sysobjects 
            WHERE name='BitacoraAcceso' AND xtype='U'
        """)
        
        if not check_table or check_table.get('existe', 0) == 0:
            execute_non_query("""
                CREATE TABLE BitacoraAcceso (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    idUsuario INT NOT NULL,
                    dtmFechaAcceso DATETIME NOT NULL,
                    FOREIGN KEY (idUsuario) REFERENCES Usuario(id)
                )
            """)
            print("✅ Tabla BitacoraAcceso creada exitosamente")
        else:
            print("ℹ️  Tabla BitacoraAcceso ya existe")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    create_bitacora_table()