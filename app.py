import os
import random
import sqlite3
from datetime import date
from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "aceest_fitness.db")

app = Flask(__name__)

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": [
		"Push/Pull/Legs",
		"Upper/Lower Split",
		"Full Body Strength"
		],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_status TEXT DEFAULT 'Active',
            membership_end TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
    """)

    cur.execute(
        "INSERT OR IGNORE INTO users "
	"(username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin", "Admin"),
    )

    conn.commit()
    conn.close()


def row_to_dict(row):
    return dict(row) if row else None


@app.get("/")
def index():
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "status": "running",
        "service": "Flask API",
    })


@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except sqlite3.Error as exc:
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    conn = get_db()
    row = conn.execute(
        "SELECT username, role FROM users WHERE username=? AND password=?",
        (username, password),
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "username": row["username"],
        "role": row["role"],
    }), 200


@app.get("/clients")
def get_clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200


@app.post("/clients")
def add_client():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()

    if not name:
        return jsonify({"error": "name is required"}), 400

    try:
        conn = get_db()
        cur = conn.execute("""
            INSERT INTO clients
            (name, age, height, weight, program, calories, target_weight,
             target_adherence, membership_status, membership_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            data.get("age"),
            data.get("height"),
            data.get("weight"),
            data.get("program"),
            data.get("calories"),
            data.get("target_weight"),
            data.get("target_adherence"),
            data.get("membership_status", "Active"),
            data.get("membership_end"),
        ))
        conn.commit()
        row = conn.execute(
            "SELECT * FROM clients WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        conn.close()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return jsonify({"error": "Client name already exists"}), 409


@app.get("/clients/<int:client_id>")
def get_client(client_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM clients WHERE id=?", (client_id,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(dict(row)), 200


@app.post("/clients/<int:client_id>/program")
def generate_program(client_id):
    data = request.get_json(silent=True) or {}
    requested_type = data.get("program_type")

    if requested_type and requested_type not in PROGRAM_TEMPLATES:
        return jsonify({
            "error": "Invalid program_type",
            "allowed": list(PROGRAM_TEMPLATES),
        }), 400

    program_type = requested_type or random.choice(list(PROGRAM_TEMPLATES))
    program_detail = random.choice(PROGRAM_TEMPLATES[program_type])

    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id=?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    conn.execute(
        "UPDATE clients SET program=? WHERE id=?",
        (program_detail, client_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "client": client["name"],
        "program_type": program_type,
        "program": program_detail,
    }), 200


@app.get("/clients/<int:client_id>/membership")
def check_membership(client_id):
    conn = get_db()
    row = conn.execute("""
        SELECT name, membership_status, membership_end
        FROM clients WHERE id=?
    """, (client_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Client not found"}), 404

    return jsonify({
        "client": row["name"],
        "membership_status": row["membership_status"],
        "membership_end": row["membership_end"],
    }), 200


@app.post("/clients/<int:client_id>/workouts")
def add_workout(client_id):
    data = request.get_json(silent=True) or {}
    workout_date = data.get("date", date.today().isoformat())
    workout_type = str(data.get("workout_type", "")).strip()
    duration = data.get("duration_min")

    if not workout_type or duration is None:
        return jsonify({
            "error": "workout_type and duration_min are required"
        }), 400

    try:
        duration = int(duration)
    except (TypeError, ValueError):
        return jsonify({"error": "duration_min must be an integer"}), 400

    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id=?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    cur = conn.execute("""
        INSERT INTO workouts
        (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        client["name"],
        workout_date,
        workout_type,
        duration,
        data.get("notes"),
    ))
    conn.commit()
    row = conn.execute(
        "SELECT * FROM workouts WHERE id=?", (cur.lastrowid,)
    ).fetchone()
    conn.close()

    return jsonify(dict(row)), 201


@app.get("/clients/<int:client_id>/workouts")
def get_workouts(client_id):
    conn = get_db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id=?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    rows = conn.execute("""
        SELECT * FROM workouts
        WHERE client_name=?
        ORDER BY date DESC
    """, (client["name"],)).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows]), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
