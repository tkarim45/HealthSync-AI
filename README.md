# HealthSync-AI

**HealthSync-AI** is a modern, production-grade health data platform that orchestrates ETL pipelines, analytics, and rich dashboards for healthcare operations. It leverages Airflow, dbt, PostgreSQL, FastAPI, and a React frontend to provide a robust, extensible, and analytics-ready environment for hospitals, doctors, and patients.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Directory Structure](#directory-structure)
- [Setup & Installation](#setup--installation)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Airflow & ETL](#airflow--etl)
  - [dbt Analytics](#dbt-analytics)
- [Data Model](#data-model)
- [API Endpoints](#api-endpoints)
- [Dummy Data Population](#dummy-data-population)
- [Dashboards & Analytics](#dashboards--analytics)
- [Development & Contribution](#development--contribution)
- [License](#license)

---

## Project Overview

HealthSync-AI is designed to streamline healthcare data management, analytics, and operational workflows. It supports:

- Automated ETL pipelines for user, doctor, appointment, and hospital data.
- Analytics-ready tables for dashboards (user stats, doctor specialties, appointments, etc.).
- A secure, role-based backend API for hospital admins, doctors, and patients.
- A modern React frontend for booking, management, and analytics.
- Integration with dbt for advanced data modeling and transformation.
- Extensible support for AI-powered features (e.g., medical report analysis, chatbot).

---

## Architecture

```
[React Frontend] <---> [FastAPI Backend] <---> [PostgreSQL DB]
                                   ^
                                   |
                        [Airflow ETL & dbt]
                                   |
                             [Analytics Tables]
                                   |
                              [Grafana, etc.]
```

- **Airflow** orchestrates ETL and analytics table population.
- **dbt** manages data transformations and analytics models.
- **FastAPI** exposes REST APIs for all user roles.
- **React** provides a modern, role-based UI.
- **PostgreSQL** is the central data warehouse.
- **Grafana** is used for dashboards.

---

## Features

- **ETL Pipelines:** Automated extraction, transformation, and loading of healthcare data.
- **Analytics Tables:** User stats, doctor specialty counts, appointment stats, hospital/department metrics, and more.
- **Role-Based Access:** Super Admin, Admin, Doctor, and Patient flows.
- **Appointment Booking:** Real-time doctor availability, booking, and notifications.
- **Medical AI:** Blood report parsing, chatbot, and disease detection (AI/ML ready).
- **Idempotent Dummy Data:** Robust script for generating realistic, non-duplicated demo data.
- **dbt Analytics:** Modular, testable SQL models for advanced reporting.
- **Extensible:** Easily add new analytics, AI features, or integrations.
- **Grafana:** Used for dashboards.

---

## Tech Stack

- **Backend:** FastAPI, Python, psycopg2, Pydantic, Passlib
- **Frontend:** React, Tailwind CSS
- **Database:** PostgreSQL
- **ETL Orchestration:** Apache Airflow
- **Analytics/Modeling:** dbt
- **AI/ML:** LangChain, Llama, Pinecone, Groq (for advanced features)
- **Containerization:** Docker, Docker Compose

---

## Directory Structure

```
HealthSync-AI/
│
├── airflow/                # Airflow DAGs and logs
│   └── dags/
│       └── sample_etl.py   # Main ETL and analytics DAG
│
├── backend/                # FastAPI backend
│   ├── main.py             # Main API application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile
│   ├── models/             # Pydantic schemas
│   ├── routes/             # API route modules
│   ├── utils/              # Utility scripts (db, email, AI, dummy data, etc.)
│   ├── config/             # Settings and environment
│   ├── data/               # Sample data (blood reports, skin detection)
│   ├── notebooks/          # Jupyter notebooks for exploration
│   └── uploads/            # Uploaded files
│
├── dbt/                    # dbt analytics project
│   ├── healthsync_dbt/
│   │   ├── models/
│   │   │   └── doctor_appointments.sql
│   │   └── profiles.yml
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Main UI pages (Admin, Doctor, Booking, etc.)
│   │   ├── components/     # Reusable UI components
│   │   └── utils/          # Frontend utilities
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
└── README.md               # Project documentation
```

---

## Setup & Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set up environment variables in config/settings.py or .env
# (DB credentials, API keys, etc.)
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
# Visit http://localhost:3000
```

#### Docker both backend and frontend

```bash
docker compose up --build
```

### 3. Airflow & ETL

- Airflow is configured in `airflow/dags/sample_etl.py`.
- Use Docker Compose or your Airflow deployment to run the DAG.
- The DAG will create and populate analytics tables, run dbt, and send notifications.

```bash
# Visit http://localhost:8080
```

### 4. dbt Analytics

- Configure your `profiles.yml` for database connection.

---

## Data Model

- **users:** All users (super_admin, admin, doctor, patient)
- **hospitals, departments:** Hospital and department structure
- **doctors:** Doctor profiles and assignments
- **appointments:** Appointment bookings
- **doctor_availability:** Doctor time slots
- **hospital_admins:** Admin-hospital assignments
- **analytics tables:** (created by ETL/dbt)
  - `etl_stats`, `user_stats`, `doctor_specialty_counts`, `appointment_stats`, `weekly_signups`, `hospital_stats`, `department_doctor_counts`, etc.

---

## API Endpoints

The backend exposes a rich set of REST APIs. Key endpoints include:

- **Auth:** `/api/auth/login`, `/api/auth/signup`
- **Hospitals/Admins:** `/api/hospitals`, `/api/admins`, `/api/hospitals/{id}/assign-admin`
- **Departments/Doctors:** `/api/departments`, `/api/doctors`
- **Appointments:** `/api/appointments`, `/api/doctor/appointments/today|week|upcoming`
- **Medical AI:** `/api/medical-query`, `/api/acne-analysis`, `/chatbot`
- **Analytics:** (via ETL/dbt tables)
- **See `backend/main.py` and `routes/` for full details.**

---

## Dummy Data Population

- The backend runs `utils/populate_dummy_data.py` on startup.
- This script:
  - Populates hospitals, departments, admins, doctors, and availability.
  - Ensures idempotency and uniqueness (no duplicates on rerun).
  - Generates a `dummy_passwords.txt` file for demo logins.
- You can run it manually:
  ```bash
  python backend/utils/populate_dummy_data.py
  ```

---

## Dashboards & Analytics

- **Analytics tables** are created and populated by Airflow and dbt.
- **Grafana** or other BI tools can be connected to the analytics tables for dashboards.
- Example dbt model: `doctor_appointments.sql` (counts appointments per doctor).
- Extend with new dbt models for custom analytics.

---

## Development & Contribution

- Fork and clone the repo.
- Use feature branches and submit PRs.
- Follow PEP8 and best practices for Python, React, and SQL.
- Add tests and update documentation for new features.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Apache Airflow](https://airflow.apache.org/)
- [dbt](https://www.getdbt.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [LangChain, Llama, Pinecone, Groq] for AI/ML features

---

**For questions or support, open an issue or contact the maintainer.**
