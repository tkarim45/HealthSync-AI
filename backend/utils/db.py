import psycopg2
import logging
from config.settings import settings
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


def init_db():
    conn = psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    conn.set_session(autocommit=True)
    c = conn.cursor()

    # Users table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP
        )
        """
    )

    # Check if role column exists and add if not
    c.execute(
        """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'role'
        """
    )
    if not c.fetchone():
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

    # Hospitals table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS hospitals (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            lat DOUBLE PRECISION NOT NULL,
            lng DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP
        )
        """
    )

    # Hospital admins table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_admins (
            hospital_id UUID,
            user_id UUID,
            assigned_at TIMESTAMP,
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
            id UUID PRIMARY KEY,
            hospital_id UUID NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
        )
        """
    )

    # Doctors table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            user_id UUID NOT NULL,
            department_id UUID NOT NULL,
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
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    # Appointments table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            doctor_id UUID NOT NULL,
            department_id UUID NOT NULL,
            hospital_id UUID NOT NULL,
            appointment_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, appointment_date, start_time)
        )
        """
    )

    # Medical history table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS medical_history (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            conditions TEXT,
            allergies TEXT,
            notes TEXT,
            updated_at TIMESTAMP,
            updated_by UUID,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
        )
        """
    )

    # General chat history table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS general_chat_history (
            id UUID PRIMARY KEY,
            user_id UUID,
            query TEXT,
            response TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.close()
    logger.info("Database initialized successfully")


def insert_dummy_medical_history():
    conn = psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
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
            INSERT INTO medical_history (id, user_id, conditions, allergies, notes, updated_at, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
            SET user_id = EXCLUDED.user_id,
                conditions = EXCLUDED.conditions,
                allergies = EXCLUDED.allergies,
                notes = EXCLUDED.notes,
                updated_at = EXCLUDED.updated_at,
                updated_by = EXCLUDED.updated_by
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
    return psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )


async def get_user(username: str):
    """Retrieve user by username."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT id, username, email, password, role, created_at 
        FROM users 
        WHERE username = %s
        """,
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
            created_at=user[5],  # Already a timestamp
        )
    return None
