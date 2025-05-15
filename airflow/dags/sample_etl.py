from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import logging
import psycopg2

# Configure logging
logger = logging.getLogger(__name__)


# Extraction function: Simulate extracting doctor data from a source (e.g., API, file, or another DB)
def extract_data(**context):
    # For demonstration, we'll just log and push a static list of doctors
    doctors = [
        {"id": 1, "name": "Dr. Smith", "role": "doctor"},
        {"id": 2, "name": "Dr. Jones", "role": "doctor"},
        {"id": 3, "name": "Dr. Lee", "role": "doctor"},
    ]
    logger.info(f"Extracted {len(doctors)} doctors.")
    context["ti"].xcom_push(key="doctors", value=doctors)


# Transformation function: Simulate transforming the extracted data
def transform_data(**context):
    doctors = context["ti"].xcom_pull(key="doctors", task_ids="extract_data")
    # Example transformation: filter only doctors with 'doctor' role (all in this case)
    transformed = [doc for doc in doctors if doc["role"] == "doctor"]
    logger.info(f"Transformed data: {transformed}")
    context["ti"].xcom_push(key="transformed_doctors", value=transformed)


# Data quality check: Ensure the table has at least one row for today
def data_quality_check(**context):
    import os
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # Use Airflow connection env vars
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "healthsync"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute("SELECT COUNT(*) as cnt FROM etl_stats WHERE run_date = CURRENT_DATE;")
    result = c.fetchone()
    logger.info(f"Rows for today: {result['cnt']}")
    if result["cnt"] < 1:
        raise ValueError("Data quality check failed: No rows for today in etl_stats.")
    conn.close()


with DAG(
    dag_id="sample_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": True,
        "email": ["taimourabdulkarim20@gmail.com"],
    },
    doc_md="""
    ### Sample ETL DAG
    This DAG demonstrates a robust ETL pipeline with data extraction, transformation, loading, data quality checks, and notifications.
    """,
) as dag:
    extract = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        provide_context=True,
    )

    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS etl_stats (
                id SERIAL PRIMARY KEY,
                run_date DATE UNIQUE,
                doctor_count INT
            );
        """,
    )

    load = PostgresOperator(
        task_id="load_data",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO etl_stats (run_date, doctor_count)
            SELECT CURRENT_DATE, COUNT(*) FROM users WHERE role = 'doctor'
            ON CONFLICT (run_date) DO UPDATE
            SET doctor_count = EXCLUDED.doctor_count;
        """,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command='docker exec -i $(docker ps -qf "ancestor=ghcr.io/dbt-labs/dbt-postgres:1.7.4") dbt run --project-dir /usr/app --profiles-dir /usr/app',
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command='docker exec -i $(docker ps -qf "ancestor=ghcr.io/dbt-labs/dbt-postgres:1.7.4") dbt test --project-dir /usr/app',
    )

    quality = PythonOperator(
        task_id="data_quality_check",
        python_callable=data_quality_check,
        provide_context=True,
    )

    notify = EmailOperator(
        task_id="notify",
        to="taimourabdulkarim20@gmail.com",
        subject="ETL DAG Finished",
        html_content="The ETL DAG has completed.",
        trigger_rule="all_done",
    )

    # Additional aggregation and analytics tasks for visualization

    # Create user stats table
    create_user_stats_table = PostgresOperator(
        task_id="create_user_stats_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS user_stats (
                stat_date DATE PRIMARY KEY,
                total_users INT,
                new_users INT
            );
        """,
    )

    # Aggregate and insert user stats
    aggregate_user_stats = PostgresOperator(
        task_id="aggregate_user_stats",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO user_stats (stat_date, total_users, new_users)
            SELECT
                CURRENT_DATE,
                COUNT(*),
                COUNT(*) FILTER (WHERE created_at::date = CURRENT_DATE)
            FROM users
            ON CONFLICT (stat_date) DO UPDATE
            SET
                total_users = EXCLUDED.total_users,
                new_users = EXCLUDED.new_users;
        """,
    )

    # Create doctor specialty counts table
    create_doctor_specialty_table = PostgresOperator(
        task_id="create_doctor_specialty_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS doctor_specialty_counts (
                stat_date DATE,
                specialty TEXT,
                doctor_count INT,
                PRIMARY KEY (stat_date, specialty)
            );
        """,
    )

    # Aggregate and insert doctor specialty counts
    aggregate_doctor_specialty = PostgresOperator(
        task_id="aggregate_doctor_specialty",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO doctor_specialty_counts (stat_date, specialty, doctor_count)
            SELECT
                CURRENT_DATE,
                specialty,
                COUNT(*)
            FROM doctors
            GROUP BY specialty
            ON CONFLICT (stat_date, specialty) DO UPDATE
            SET doctor_count = EXCLUDED.doctor_count;
        """,
    )

    # Create appointment stats table
    create_appointment_stats_table = PostgresOperator(
        task_id="create_appointment_stats_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS appointment_stats (
                stat_date DATE PRIMARY KEY,
                total_appointments INT,
                avg_appointments_per_doctor FLOAT
            );
        """,
    )

    # Aggregate and insert appointment stats
    aggregate_appointment_stats = PostgresOperator(
        task_id="aggregate_appointment_stats",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO appointment_stats (stat_date, total_appointments, avg_appointments_per_doctor)
            SELECT
                CURRENT_DATE,
                COUNT(*),
                COUNT(*)::float / NULLIF((SELECT COUNT(*) FROM users WHERE role = 'doctor'), 0)
            FROM appointments
            WHERE appointment_date::date = CURRENT_DATE
            ON CONFLICT (stat_date) DO UPDATE
            SET
                total_appointments = EXCLUDED.total_appointments,
                avg_appointments_per_doctor = EXCLUDED.avg_appointments_per_doctor;
        """,
    )

    # Create weekly signups table
    create_weekly_signups_table = PostgresOperator(
        task_id="create_weekly_signups_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS weekly_signups (
                week_start DATE PRIMARY KEY,
                user_signups INT
            );
        """,
    )

    # Aggregate and insert weekly signups
    aggregate_weekly_signups = PostgresOperator(
        task_id="aggregate_weekly_signups",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO weekly_signups (week_start, user_signups)
            SELECT
                date_trunc('week', CURRENT_DATE)::date AS week_start,
                COUNT(*)
            FROM users
            WHERE created_at >= date_trunc('week', CURRENT_DATE)
            AND created_at < date_trunc('week', CURRENT_DATE) + INTERVAL '7 days'
            ON CONFLICT (week_start) DO UPDATE
            SET user_signups = EXCLUDED.user_signups;
        """,
    )

    # Create hospital stats table
    create_hospital_stats_table = PostgresOperator(
        task_id="create_hospital_stats_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS hospital_stats (
                stat_date DATE PRIMARY KEY,
                total_hospitals INT,
                total_departments INT
            );
        """,
    )

    # Aggregate and insert hospital stats
    aggregate_hospital_stats = PostgresOperator(
        task_id="aggregate_hospital_stats",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO hospital_stats (stat_date, total_hospitals, total_departments)
            SELECT
                CURRENT_DATE,
                (SELECT COUNT(*) FROM hospitals),
                (SELECT COUNT(*) FROM departments)
            ON CONFLICT (stat_date) DO UPDATE
            SET
                total_hospitals = EXCLUDED.total_hospitals,
                total_departments = EXCLUDED.total_departments;
        """,
    )

    # Create department doctor counts table
    create_department_doctor_counts_table = PostgresOperator(
        task_id="create_department_doctor_counts_table",
        postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS department_doctor_counts (
                stat_date DATE,
                department_id UUID,
                doctor_count INT,
                PRIMARY KEY (stat_date, department_id)
            );
        """,
    )

    # Aggregate and insert department doctor counts
    aggregate_department_doctor_counts = PostgresOperator(
        task_id="aggregate_department_doctor_counts",
        postgres_conn_id="postgres_default",
        sql="""
            INSERT INTO department_doctor_counts (stat_date, department_id, doctor_count)
            SELECT
                CURRENT_DATE,
                department_id,
                COUNT(*)
            FROM doctors
            GROUP BY department_id
            ON CONFLICT (stat_date, department_id) DO UPDATE
            SET doctor_count = EXCLUDED.doctor_count;
        """,
    )

    # DAG dependencies
    (
        extract
        >> transform
        >> create_table
        >> load
        >> create_user_stats_table
        >> aggregate_user_stats
        >> create_doctor_specialty_table
        >> aggregate_doctor_specialty
        >> create_appointment_stats_table
        >> aggregate_appointment_stats
        >> create_weekly_signups_table
        >> aggregate_weekly_signups
        >> create_hospital_stats_table
        >> aggregate_hospital_stats
        >> create_department_doctor_counts_table
        >> aggregate_department_doctor_counts
        >> dbt_run
        >> dbt_test
        >> quality
        >> notify
    )
