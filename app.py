"""
Flyer GEN — Web App
Correr: python app.py
Abrir:  http://localhost:5000
"""

import os
import io
import base64
from datetime import date, timedelta

from flask import Flask, render_template, jsonify, send_file, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from scraper   import get_available_slots
from generator import generate_flyer

app = Flask(__name__)

DAYS_ES   = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
MONTHS_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _next_7_days():
    today = date.today()
    days = []
    for i in range(7):
        d = today + timedelta(days=i)
        days.append({
            'offset': i,
            'label':  DAYS_ES[d.weekday()],
            'date':   f"{d.day} {MONTHS_ES[d.month - 1]}",
            'iso':    d.isoformat(),
        })
    return days


@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)


@app.route('/')
def index():
    return render_template('index.html', days=_next_7_days())


@app.route('/generate/<iso_date>')
def generate(iso_date):
    try:
        target = date.fromisoformat(iso_date)
    except ValueError:
        return jsonify({'error': 'Fecha inválida'}), 400

    try:
        slots = get_available_slots(target_date=target)
    except Exception as e:
        return jsonify({'error': f'Error scrapeando: {e}'}), 500

    if not slots:
        return jsonify({'error': 'No hay turnos disponibles ese día'}), 404

    try:
        path = generate_flyer(slots, target_date=target)
    except Exception as e:
        return jsonify({'error': f'Error generando flyer: {e}'}), 500

    with open(path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()

    return jsonify({
        'image': img_b64,
        'filename': path.name,
        'slots': len(slots),
    })


@app.route('/file/<filename>')
def serve_file(filename):
    from pathlib import Path
    output_dir = Path('output')
    filepath = output_dir / filename
    if not filepath.exists():
        return "Archivo no encontrado", 404
    return send_file(
        filepath,
        mimetype='image/png',
        as_attachment=True,
        download_name=filename,
    )


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
