"""Small production-oriented starter API for JKCORP inquiries.

Run locally from the repository root:
  pip install -r backend/requirements.txt
  flask --app backend.app run --debug

GitHub Pages cannot execute this Python service; deploy it separately.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = os.getenv("DATABASE_PATH", str(BASE_DIR / "jkcorp.sqlite3"))
app = Flask(__name__)
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5500").split(",") if origin.strip()]
CORS(app, origins=allowed_origins)


def connection():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def initialise_database():
    with connection() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )"""
        )
        db.commit()


initialise_database()


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "jkcorp-api"})


@app.post("/api/inquiries")
def create_inquiry():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    service = str(payload.get("service", "")).strip()
    message = str(payload.get("message", "")).strip()

    if not name or not phone or not service:
        return jsonify({"ok": False, "error": "name, phone and service are required"}), 400
    if len(name) > 120 or len(phone) > 30 or len(service) > 120 or len(message) > 2000:
        return jsonify({"ok": False, "error": "one or more fields are too long"}), 400

    created_at = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        cursor = db.execute(
            "INSERT INTO inquiries (name, phone, service, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, service, message, created_at),
        )
        db.commit()
        inquiry_id = cursor.lastrowid

    return jsonify({"ok": True, "id": inquiry_id}), 201


@app.get("/api/inquiries")
def list_inquiries():
    # Protect this endpoint with real admin authentication before deployment.
    with connection() as db:
        rows = db.execute(
            "SELECT id, name, phone, service, message, created_at FROM inquiries ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify({"ok": True, "inquiries": [dict(row) for row in rows]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")))
