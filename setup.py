"""
Ejecutar UNA sola vez para instalar dependencias y Playwright.
    python setup.py
"""
import subprocess
import sys
import shutil
from pathlib import Path

def run(cmd):
    print(f"$ {cmd}")
    subprocess.check_call(cmd, shell=True)

def main():
    print("=== Flyer GEN — Setup ===\n")

    # 1. Instalar dependencias Python
    run(f"{sys.executable} -m pip install -r requirements.txt")

    # 2. Instalar browser de Playwright
    run(f"{sys.executable} -m playwright install chromium")

    # 3. Crear .env si no existe
    env_file = Path(".env")
    if not env_file.exists():
        shutil.copy(".env.example", ".env")
        print("\n⚠️  Creé el archivo .env — abrilo y pegá tu ANTHROPIC_API_KEY.")
    else:
        print("\n✅ .env ya existe.")

    # 4. Recordatorio de fotos
    print("\n📸 Copiá las fotos del complejo en:  assets/photos/")
    print("   Formatos soportados: .jpg  .jpeg  .png  .webp")
    print("   (Si no hay fotos, el fondo será negro puro — igual funciona)\n")

    # 5. Recordatorio de número de WhatsApp
    print("📱 Editá config.py y reemplazá WHATSAPP con el número real.")
    print("\n✅ Setup completo. Para generar el flyer de hoy:")
    print("   python main.py          # real")
    print("   python main.py --mock   # prueba sin conectarse al sitio\n")

if __name__ == '__main__':
    main()
