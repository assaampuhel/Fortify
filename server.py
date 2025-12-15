from flask import Flask, request, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATABASE = "fortify.db"


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def init_db():
    """
    Creates database and table if not exists
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intrusion_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        event_timestamp TEXT,
        evidence_path TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

@app.route("/api/upload_evidence", methods=["POST"])
def upload_evidence():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files["image"]
    device_id = request.form.get("device_id")
    timestamp = request.form.get("timestamp")

    if not device_id or not timestamp:
        return jsonify({"error": "Missing data"}), 400

    filename = f"{device_id}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO intrusion_events 
        (device_id, event_timestamp, evidence_path, status)
        VALUES (?, ?, ?, ?)
    """, (device_id, timestamp, filepath, "PENDING"))

    conn.commit()
    conn.close()

    return jsonify({"message": "Upload successful"}), 200


@app.route("/api/status_check")
def status_check():
    return jsonify({"status": "Server running"}), 200


if __name__ == "__main__":
    print("[INFO] Starting Fortify Polaris Backend on port 5000...")
    app.run(debug=True)