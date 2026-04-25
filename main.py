"""
Flyer GEN — entry point
Usage:
    python main.py              # genera flyer con turnos de HOY
    python main.py --manana     # genera flyer con turnos de MAÑANA
    python main.py --mock       # usa turnos de prueba (sin conectarse al sitio)
    python main.py --debug      # muestra HTML scrapeado
"""

import os
import sys
import subprocess
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()  # carga ANTHROPIC_API_KEY si existe en .env

from scraper   import get_available_slots
from generator import generate_flyer

MOCK_SLOTS = [
    {'time': '09:30', 'price': '$20.000', 'status': 'DISPONIBLE'},
    {'time': '11:00', 'price': '$20.000', 'status': 'DISPONIBLE'},
    {'time': '14:30', 'price': '$24.000', 'status': 'DISPONIBLE'},
    {'time': '17:30', 'price': '$24.000', 'status': 'DISPONIBLE'},
]


def main():
    debug  = '--debug'  in sys.argv
    mock   = '--mock'   in sys.argv
    manana = '--manana' in sys.argv

    target = date.today() + timedelta(days=1) if manana else date.today()
    print(f"\nFlyer GEN -- Negro Padel")
    print(f"Fecha: {target.strftime('%d/%m/%Y')}\n")

    # ── 1. Obtener turnos ──
    if mock:
        print("Modo mock -- usando turnos de prueba")
        slots = MOCK_SLOTS
    else:
        print("Scrapeando negropadel.com...")
        try:
            slots = get_available_slots(target_date=target, debug=debug)
        except Exception as e:
            print(f"Error en el scraper: {e}")
            sys.exit(1)

    if not slots:
        print("No hay turnos disponibles. No se genera flyer.")
        sys.exit(0)

    print(f"{len(slots)} turno(s) disponible(s):")
    for s in slots:
        print(f"  {s['time']}  {s.get('price', '')}")

    # ── 2. Generar flyer ──
    print("\nGenerando flyer...")
    output_path = generate_flyer(slots, target_date=target)

    print(f"\nFlyer guardado en: {output_path}")

    # Abrir imagen automáticamente en Windows
    try:
        os.startfile(str(output_path))
    except Exception:
        subprocess.Popen(['explorer', str(output_path)])


if __name__ == '__main__':
    main()
