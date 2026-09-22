import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_PATH = os.getenv('DATABASE_PATH', str(Path(__file__).with_name('jkcorp.sqlite3')))
origins = [x.strip() for x in os.getenv('CORS_ORIGINS', 'http://localhost:5500').split(',') if x.strip()]
CORS(app, origins=origins)


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialise():
    with db() as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, phone TEXT NOT NULL, service TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL)''')
        connection.commit()


initialise()


@app.get('/api/health')
def health():
    return jsonify({'ok': True, 'service': 'jkcorp-api'})


@app.post('/api/inquiries')
def create_inquiry():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get('name', '')).strip()
    phone = str(payload.get('phone', '')).strip()
    service = str(payload.get('service', '')).strip()
    message = str(payload.get('message', '')).strip()
    if not name or not phone or not service:
        return jsonify({'ok': False, 'error': 'name, phone and service are required'}), 400
    if len(name) > 120 or len(phone) > 30 or len(service) > 120 or len(message) > 2000:
        return jsonify({'ok': False, 'error': 'input too long'}), 400
    with db() as connection:
        cursor = connection.execute(
            'INSERT INTO inquiries (name, phone, service, message, created_at) VALUES (?, ?, ?, ?, ?)',
            (name, phone, service, message, datetime.now(timezone.utc).isoformat()))
        connection.commit()
    return jsonify({'ok': True, 'id': cursor.lastrowid}), 201


@app.get('/api/inquiries')
def list_inquiries():
    expected = os.getenv('ADMIN_TOKEN', '')
    supplied = request.headers.get('X-Admin-Token', '')
    if not expected or not secrets.compare_digest(supplied, expected):
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    with db() as connection:
        rows = connection.execute('SELECT id, name, phone, service, message, created_at FROM inquiries ORDER BY id DESC LIMIT 100').fetchall()
    return jsonify({'ok': True, 'inquiries': [dict(row) for row in rows]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
