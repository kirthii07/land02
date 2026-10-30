import sqlite3
from datetime import datetime
from pathlib import Path

from config import DATABASE_PATH


def get_connection():
    """Create and return a SQLite database connection."""
    global DATABASE_PATH
    try:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )
    except OSError:
        DATABASE_PATH = Path("/tmp") / "landslide.db"
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Sensor readings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT DEFAULT 'Unknown',

            rainfall REAL DEFAULT 0,
            soil_moisture REAL DEFAULT 0,
            tilt REAL DEFAULT 0,
            temperature REAL DEFAULT 0,
            humidity REAL DEFAULT 0,

            risk_level TEXT DEFAULT 'UNKNOWN',
            shi REAL DEFAULT 0
        )
    """)

    # Alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT DEFAULT 'Unknown',
            risk_level TEXT NOT NULL,
            message TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def insert_sensor_data(
    rainfall,
    soil_moisture,
    tilt,
    temperature,
    humidity,
    location="Unknown",
    risk_level="UNKNOWN",
    shi=0,
    timestamp=None
):
    """Insert a sensor reading into the database."""

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO sensor_data (
            timestamp,
            location,
            rainfall,
            soil_moisture,
            tilt,
            temperature,
            humidity,
            risk_level,
            shi
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        location,
        rainfall,
        soil_moisture,
        tilt,
        temperature,
        humidity,
        risk_level,
        shi
    ))

    connection.commit()
    inserted_id = cursor.lastrowid

    connection.close()

    return inserted_id


def get_recent_data(limit=50):
    """Return latest sensor readings."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM sensor_data
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_latest_data():
    """Return the latest sensor reading."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    return dict(row) if row else None


def insert_alert(
    location,
    risk_level,
    message,
    timestamp=None,
    acknowledged=0
):
    """Insert a risk alert."""

    connection = get_connection()
    cursor = connection.cursor()

    if not timestamp:
        timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO alerts (
            timestamp,
            location,
            risk_level,
            message,
            acknowledged
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        timestamp,
        location,
        risk_level,
        message,
        acknowledged
    ))

    connection.commit()
    alert_id = cursor.lastrowid

    connection.close()

    return alert_id


def get_recent_alerts(limit=20):
    """Return latest alerts."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")
    print(f"📁 Database: {DATABASE_PATH}")