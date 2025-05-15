import psycopg2
import uuid
from datetime import datetime, timedelta
import random
import logging
from faker import Faker
from config.settings import settings  # Adjust import based on your project structure

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Faker for realistic data
fake = Faker()


# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )


# Helper function to generate random time slots
def generate_time_slot():
    hours = random.randint(9, 17)  # 9 AM to 5 PM
    minutes = random.choice([0, 30])
    start_time = f"{hours:02d}:{minutes:02d}"
    end_hour = hours + (1 if minutes == 30 else 0)
    end_minutes = (minutes + 30) % 60
    end_time = f"{end_hour:02d}:{end_minutes:02d}"
    return start_time, end_time


# Create aggregated tables (matching etl_pipeline.py)
def create_aggregated_tables(conn):
    c = conn.cursor()
    # User stats table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_stats (
            stat_date DATE PRIMARY KEY,
            total_users INT,
            new_users INT
        );
        """
    )
    # Doctor specialty counts table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS doctor_specialty_counts (
            stat_date DATE,
            specialty TEXT,
            doctor_count INT,
            PRIMARY KEY (stat_date, specialty)
        );
        """
    )
    # Appointment stats table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS appointment_stats (
            stat_date DATE PRIMARY KEY,
            total_appointments INT,
            avg_appointments_per_doctor FLOAT
        );
        """
    )
    # Weekly signups table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS weekly_signups (
            week_start DATE PRIMARY KEY,
            user_signups INT
        );
        """
    )
    # Hospital stats table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS hospital_stats (
            stat_date DATE PRIMARY KEY,
            total_hospitals INT,
            total_departments INT
        );
        """
    )
    # Department doctor counts table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS department_doctor_counts (
            stat_date DATE,
            department_id UUID,
            doctor_count INT,
            PRIMARY KEY (stat_date, department_id)
        );
        """
    )
    conn.commit()
    logger.info("Aggregated tables created or verified")


# Populate foundational tables
def populate_foundational_data():
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Populate users (patients, doctors, admins)
    users = []
    user_roles = [("patient", 50), ("doctor", 20), ("admin", 5)]
    for role, count in user_roles:
        for _ in range(count):
            user_id = str(uuid.uuid4())
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            created_at = fake.date_time_between(start_date="-90d", end_date="now")
            users.append((user_id, username, email, password, role, created_at))
    c.executemany(
        """
        INSERT INTO users (id, username, email, password, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        users,
    )
    logger.info(f"Inserted {len(users)} users")

    # 2. Populate hospitals
    hospitals = []
    for _ in range(5):
        hospital_id = str(uuid.uuid4())
        name = fake.company() + " Hospital"
        address = fake.address()
        lat = fake.latitude()
        lng = fake.longitude()
        created_at = fake.date_time_between(start_date="-90d", end_date="now")
        hospitals.append((hospital_id, name, address, lat, lng, created_at))
    c.executemany(
        """
        INSERT INTO hospitals (id, name, address, lat, lng, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        hospitals,
    )
    logger.info(f"Inserted {len(hospitals)} hospitals")

    # 3. Populate hospital_admins
    c.execute("SELECT id FROM users WHERE role = 'admin'")
    admin_ids = [row[0] for row in c.fetchall()]
    c.execute("SELECT id FROM hospitals")
    hospital_ids = [row[0] for row in c.fetchall()]
    hospital_admins = []
    for admin_id in admin_ids:
        hospital_id = random.choice(hospital_ids)
        assigned_at = datetime.utcnow()
        hospital_admins.append((hospital_id, admin_id, assigned_at))
    c.executemany(
        """
        INSERT INTO hospital_admins (hospital_id, user_id, assigned_at)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        hospital_admins,
    )
    logger.info(f"Inserted {len(hospital_admins)} hospital_admins")

    # 4. Populate departments
    departments = []
    department_names = [
        "Cardiology",
        "Neurology",
        "Pediatrics",
        "Orthopedics",
        "Oncology",
    ]
    for hospital_id in hospital_ids:
        for name in department_names:
            department_id = str(uuid.uuid4())
            departments.append((department_id, hospital_id, name))
    c.executemany(
        """
        INSERT INTO departments (id, hospital_id, name)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        departments,
    )
    logger.info(f"Inserted {len(departments)} departments")

    # 5. Populate doctors
    c.execute("SELECT id FROM users WHERE role = 'doctor'")
    doctor_ids = [row[0] for row in c.fetchall()]
    c.execute("SELECT id FROM departments")
    department_ids = [row[0] for row in c.fetchall()]
    specialties = [
        "Cardiologist",
        "Neurologist",
        "Pediatrician",
        "Orthopedist",
        "Oncologist",
    ]
    doctors = []
    for doctor_id in doctor_ids:
        department_id = random.choice(department_ids)
        specialty = random.choice(specialties)
        title = f"Dr. {fake.last_name()}"
        phone = fake.phone_number()
        bio = fake.text(max_nb_chars=200)
        doctors.append((doctor_id, department_id, specialty, title, phone, bio))
    c.executemany(
        """
        INSERT INTO doctors (user_id, department_id, specialty, title, phone, bio)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        doctors,
    )
    logger.info(f"Inserted {len(doctors)} doctors")

    # 6. Populate appointments
    c.execute("SELECT id FROM users WHERE role = 'patient'")
    patient_ids = [row[0] for row in c.fetchall()]
    c.execute("SELECT user_id, department_id FROM doctors")
    doctor_depts = c.fetchall()
    c.execute("SELECT id FROM hospitals")
    hospital_ids = [row[0] for row in c.fetchall()]
    appointments = []
    statuses = ["scheduled", "completed", "cancelled"]
    start_date = datetime.now() - timedelta(days=90)
    for _ in range(200):
        appointment_id = str(uuid.uuid4())
        user_id = random.choice(patient_ids)
        doctor_id, department_id = random.choice(doctor_depts)
        hospital_id = random.choice(hospital_ids)
        appt_date = fake.date_between(start_date=start_date, end_date="now")
        start_time, end_time = generate_time_slot()
        status = random.choices(statuses, weights=[70, 20, 10], k=1)[0]
        created_at = fake.date_time_between(start_date=start_date, end_date="now")
        appointments.append(
            (
                appointment_id,
                user_id,
                doctor_id,
                department_id,
                hospital_id,
                appt_date.strftime("%Y-%m-%d"),
                start_time,
                end_time,
                status,
                created_at,
            )
        )
    c.executemany(
        """
        INSERT INTO appointments (id, user_id, doctor_id, department_id, hospital_id, appointment_date, start_time, end_time, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        appointments,
    )
    logger.info(f"Inserted {len(appointments)} appointments")

    conn.commit()
    conn.close()


# Populate aggregated tables
def populate_aggregated_data():
    conn = get_db_connection()
    # Create aggregated tables
    create_aggregated_tables(conn)
    c = conn.cursor()

    # Generate data for the past 90 days
    start_date = datetime.now().date() - timedelta(days=90)
    end_date = datetime.now().date()
    current_date = start_date

    while current_date <= end_date:
        try:
            # 1. user_stats
            c.execute(
                """
                SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE created_at::date = %s) AS new
                FROM users
                WHERE created_at::date <= %s
                """,
                (current_date, current_date),
            )
            total_users, new_users = c.fetchone()
            c.execute(
                """
                INSERT INTO user_stats (stat_date, total_users, new_users)
                VALUES (%s, %s, %s)
                ON CONFLICT (stat_date) DO UPDATE
                SET total_users = EXCLUDED.total_users, new_users = EXCLUDED.new_users
                """,
                (current_date, total_users, new_users),
            )

            # 2. doctor_specialty_counts
            c.execute("SELECT specialty, COUNT(*) FROM doctors GROUP BY specialty")
            specialty_counts = c.fetchall()
            for specialty, count in specialty_counts:
                c.execute(
                    """
                    INSERT INTO doctor_specialty_counts (stat_date, specialty, doctor_count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (stat_date, specialty) DO UPDATE
                    SET doctor_count = EXCLUDED.doctor_count
                    """,
                    (current_date, specialty, count),
                )

            # 3. appointment_stats
            c.execute(
                """
                SELECT COUNT(*) AS total,
                       COUNT(*)::float / NULLIF((SELECT COUNT(*) FROM users WHERE role = 'doctor'), 0) AS avg
                FROM appointments
                WHERE appointment_date::date = %s
                """,
                (current_date,),
            )
            total_appts, avg_appts = c.fetchone()
            c.execute(
                """
                INSERT INTO appointment_stats (stat_date, total_appointments, avg_appointments_per_doctor)
                VALUES (%s, %s, %s)
                ON CONFLICT (stat_date) DO UPDATE
                SET total_appointments = EXCLUDED.total_appointments,
                    avg_appointments_per_doctor = EXCLUDED.avg_appointments_per_doctor
                """,
                (current_date, total_appts, avg_appts),
            )

            # 4. weekly_signups
            week_start = current_date - timedelta(days=current_date.weekday())
            c.execute(
                """
                SELECT COUNT(*) 
                FROM users 
                WHERE created_at::date >= %s AND created_at::date < %s + INTERVAL '7 days'
                """,
                (week_start, week_start),
            )
            user_signups = c.fetchone()[0]
            c.execute(
                """
                INSERT INTO weekly_signups (week_start, user_signups)
                VALUES (%s, %s)
                ON CONFLICT (week_start) DO UPDATE
                SET user_signups = EXCLUDED.user_signups
                """,
                (week_start, user_signups),
            )

            # 5. hospital_stats
            c.execute("SELECT COUNT(*) FROM hospitals")
            total_hospitals = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM departments")
            total_departments = c.fetchone()[0]
            c.execute(
                """
                INSERT INTO hospital_stats (stat_date, total_hospitals, total_departments)
                VALUES (%s, %s, %s)
                ON CONFLICT (stat_date) DO UPDATE
                SET total_hospitals = EXCLUDED.total_hospitals,
                    total_departments = EXCLUDED.total_departments
                """,
                (current_date, total_hospitals, total_departments),
            )

            # 6. department_doctor_counts
            c.execute(
                "SELECT department_id, COUNT(*) FROM doctors GROUP BY department_id"
            )
            dept_counts = c.fetchall()
            for dept_id, count in dept_counts:
                c.execute(
                    """
                    INSERT INTO department_doctor_counts (stat_date, department_id, doctor_count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (stat_date, department_id) DO UPDATE
                    SET doctor_count = EXCLUDED.doctor_count
                    """,
                    (current_date, dept_id, count),
                )

            conn.commit()
        except psycopg2.Error as e:
            logger.error(f"Error on {current_date}: {str(e)}")
            conn.rollback()
            raise
        current_date += timedelta(days=1)

    conn.close()
    logger.info("Inserted aggregated data for all tables")


def populate_dummy_data():
    logger.info("Starting dummy data population")
    populate_foundational_data()
    populate_aggregated_data()
    logger.info("Dummy data population completed")


if __name__ == "__main__":
    populate_dummy_data()
