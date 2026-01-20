# build_render.py
import sys
import subprocess
import os

def run_command(cmd):
    """Ejecuta un comando y maneja errores."""
    print(f"🚀 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    print(f"✅ Completado: {cmd}")
    return result.stdout

def main():
    print("🔧 Iniciando build para Render...")
    
    # 1. Actualizar pip y herramientas
    run_command("python -m pip install --upgrade pip setuptools wheel")
    
    # 2. Verificar versión Python
    run_command("python --version")
    
    # 3. Instalar dependencias del sistema (si es posible)
    try:
        run_command("apt-get update && apt-get install -y python3-dev libmysqlclient-dev")
    except:
        print("⚠️  No se pudieron instalar dependencias del sistema")
    
    # 4. Instalar dependencias de Python
    print("📦 Instalando dependencias de Python...")
    
    # Primero instalar setuptools y wheel
    run_command("pip install setuptools==70.0.0 wheel==0.43.0")
    
    # Instalar pendulum primero con flags específicos
    run_command("pip install pendulum==2.1.2 --no-build-isolation")
    
    # Instalar el resto
    run_command("pip install -r requirements.txt")
    
    # 5. Verificar instalación
    run_command("pip list")
    
    print("🎉 Build completado exitosamente!")

if __name__ == "__main__":
    main()