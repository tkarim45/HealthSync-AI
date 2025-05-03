import sqlite3
import logging
from config.settings import settings
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


def init_db():
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    """
    )
    # Add role column if it doesn't exist
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if "role" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    # Hospitals table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS hospitals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            created_at TEXT
        )
    """
    )
    # Hospital admins table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_admins (
            hospital_id TEXT,
            user_id TEXT,
            assigned_at TEXT,
            PRIMARY KEY (hospital_id, user_id),
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )
    # Departments table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id TEXT PRIMARY KEY,
            hospital_id TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
        )
    """
    )
    # Doctors table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            user_id TEXT NOT NULL,
            department_id TEXT NOT NULL,
            specialty TEXT NOT NULL,
            title TEXT NOT NULL,
            phone TEXT,
            bio TEXT,
            PRIMARY KEY (user_id, department_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
        )
    """
    )
    # Doctor availability table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS doctor_availability (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            day_of_week TEXT NOT NULL,  -- e.g., 'Monday', 'Tuesday'
            start_time TEXT NOT NULL,   -- e.g., '09:00'
            end_time TEXT NOT NULL,     -- e.g., '09:30'
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )
    # Appointments table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,      -- Patient
            doctor_id TEXT NOT NULL,    -- Doctor
            department_id TEXT NOT NULL,
            hospital_id TEXT NOT NULL,
            appointment_date TEXT NOT NULL,  -- e.g., '2025-04-25'
            start_time TEXT NOT NULL,   -- e.g., '09:00'
            end_time TEXT NOT NULL,     -- e.g., '09:30'
            status TEXT NOT NULL,       -- e.g., 'scheduled', 'completed', 'cancelled'
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            UNIQUE (doctor_id, appointment_date, start_time)
        )
    """
    )
    # Medical history table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS medical_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            conditions TEXT,
            allergies TEXT,
            notes TEXT,
            updated_at TEXT,
            updated_by TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
        )
    """
    )
    # General chat history table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS general_chat_history (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            query TEXT,
            response TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def insert_dummy_medical_history():
    conn = sqlite3.connect(settings.DB_PATH)
    c = conn.cursor()
    user_id = "0d3074c3-12e5-4517-b661-08c7e390296e"
    dummy_records = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "conditions": "Hypertension, Type 2 Diabetes",
            "allergies": "Penicillin, Peanuts",
            "notes": "Patient diagnosed with hypertension in 2020. Type 2 Diabetes managed with metformin.",
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": user_id,
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "conditions": "Asthma",
            "allergies": "Dust mites",
            "notes": "Asthma diagnosed in 2018. Uses albuterol inhaler as needed.",
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": user_id,
        },
    ]
    for record in dummy_records:
        c.execute(
            """
            INSERT OR REPLACE INTO medical_history (id, user_id, conditions, allergies, notes, updated_at, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["user_id"],
                record["conditions"],
                record["allergies"],
                record["notes"],
                record["updated_at"],
                record["updated_by"],
            ),
        )
    conn.commit()
    conn.close()
    logger.info(
        f"Inserted {len(dummy_records)} dummy medical history records for user {user_id}"
    )


def get_db_connection():
    """Create a new database connection."""
    return sqlite3.connect(settings.DB_PATH)


async def get_user(username: str):
    """Retrieve user by username."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, email, password, role, created_at FROM users WHERE username = ?",
        (username,),
    )
    user = c.fetchone()
    conn.close()
    if user:
        from models.schemas import UserInDB
        from datetime import datetime

        return UserInDB(
            id=user[0],
            username=user[1],
            email=user[2],
            hashed_password=user[3],
            role=user[4],
            created_at=datetime.fromisoformat(user[5]),
        )
    return None
