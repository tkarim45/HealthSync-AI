import os
import json
import logging
import re
import base64
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import sqlite3
from dotenv import load_dotenv
from jose import jwt
from jose.exceptions import JWTError
from models.user import (
    UserCreate,
    UserInDB,
    UserResponse,
    Token,
    LoginRequest,
    HospitalCreate,
    HospitalResponse,
    HospitalAdminAssign,
)
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import Optional, List
import requests
from utils.parser import (
    parse_blood_report,
    structure_report,
    get_chat_history,
    store_chat_history,
    analyze_acne_image,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
DB_PATH = "/Users/taimourabdulkarim/Documents/Personal Github Repositories/HealthSync-AI/backend/healthsync.db"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
PUBLIC_API_URL = "https://1e13-35-233-239-24.ngrok-free.app/generate"

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic models
class ChatbotRequest(BaseModel):
    query: str


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            appointment_date TEXT NOT NULL,  -- e.g., '2025-04-25'
            start_time TEXT NOT NULL,   -- e.g., '09:00'
            end_time TEXT NOT NULL,     -- e.g., '09:30'
            status TEXT NOT NULL,       -- e.g., 'scheduled', 'completed', 'cancelled'
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
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
    conn.commit()
    conn.close()


# Call init_db at startup
init_db()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.info(f"Authenticated user: {user_id}, role: {role}")
        return {"user_id": user_id, "role": role}
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail=f"Requires {role} role")
        return current_user

    return role_checker


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, username, email, password, role, created_at FROM users WHERE username = ?",
        (username,),
    )
    user = c.fetchone()
    conn.close()
    if user:
        return UserInDB(
            id=user[0],
            username=user[1],
            email=user[2],
            hashed_password=user[3],
            role=user[4],
            created_at=datetime.fromisoformat(user[5]),
        )
    return None


@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    logger.info(
        f"Attempting signup for username: {user.username}, email: {user.email}, role: {user.role}"
    )
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username, email FROM users WHERE username = ? OR email = ?",
        (user.username, user.email),
    )
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_password = pwd_context.hash(user.password)
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    # Restrict signup to 'user' role; other roles set manually via DB
    role = "user"
    logger.info(f"Assigning role: {role} to user: {user.username}")
    c.execute(
        "INSERT INTO users (id, username, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, user.username, user.email, hashed_password, role, created_at),
    )
    conn.commit()
    conn.close()
    access_token = create_access_token(
        data={"sub": user_id, "role": role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User signed up: {user.username}, role: {role}")
    return {
        "token": access_token,
        "user": UserResponse(
            id=user_id, username=user.username, email=user.email, role=role
        ),
    }


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    user = await get_user(login_data.username)
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not pwd_context.verify(login_data.password, user.hashed_password):
        conn.close()
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User logged in: {user.username}, role: {user.role}")
    response = {
        "token": access_token,
        "user": UserResponse(
            id=user.id, username=user.username, email=user.email, role=user.role
        ),
    }
    conn.close()
    logger.debug(f"Login response: {response}")
    return response


class HospitalAdminCreate(BaseModel):
    hospital_id: str
    username: str


@app.post("/api/hospitals", response_model=HospitalResponse)
async def create_hospital(
    hospital: HospitalCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hospital_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO hospitals (id, name, address, lat, lng) VALUES (?, ?, ?, ?, ?)",
        (hospital_id, hospital.name, hospital.address, hospital.lat, hospital.lng),
    )
    conn.commit()
    conn.close()
    logger.info(f"Hospital created: {hospital.name}")
    return HospitalResponse(
        id=hospital_id,
        name=hospital.name,
        address=hospital.address,
        lat=hospital.lat,
        lng=hospital.lng,
    )


@app.post("/api/hospital-admins", response_model=dict)
async def assign_hospital_admin(
    admin_data: HospitalAdminCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if any admins exist
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = c.fetchone()[0]
    if admin_count == 0:
        conn.close()
        raise HTTPException(
            status_code=400, detail="No admins exist. Create an admin first."
        )

    # Verify hospital exists
    c.execute("SELECT id FROM hospitals WHERE id = ?", (admin_data.hospital_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Hospital not found")

    # Verify user exists and has admin role
    c.execute("SELECT id, role FROM users WHERE username = ?", (admin_data.username,))
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    user_id, user_role = user
    if user_role != "admin":
        conn.close()
        raise HTTPException(status_code=400, detail="User must have admin role")

    # Assign user as hospital admin
    c.execute(
        "INSERT INTO hospital_admins (hospital_id, user_id) VALUES (?, ?)",
        (admin_data.hospital_id, user_id),
    )

    conn.commit()
    conn.close()

    logger.info(
        f"Assigned user {admin_data.username} as admin to hospital {admin_data.hospital_id}"
    )
    return {
        "message": f"User {admin_data.username} assigned as admin to hospital {admin_data.hospital_id}"
    }


@app.get("/api/admins", response_model=List[UserResponse])
async def get_admins(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, role FROM users WHERE role = 'admin'")
    admins = [
        UserResponse(id=row[0], username=row[1], email=row[2], role=row[3])
        for row in c.fetchall()
    ]
    conn.close()

    logger.info("Fetched list of admins")
    return admins


@app.get("/api/hospitals", response_model=list[HospitalResponse])
async def list_hospitals(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, address, lat, lng FROM hospitals")
    hospitals = [
        HospitalResponse(id=row[0], name=row[1], address=row[2], lat=row[3], lng=row[4])
        for row in c.fetchall()
    ]
    conn.close()
    logger.info(
        f"Hospitals listed for user: {current_user['user_id']}, role: {current_user['role']}"
    )
    return hospitals


@app.put("/api/hospitals/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: str,
    hospital: HospitalCreate,
    current_user: dict = Depends(require_role("super_admin")),
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM hospitals WHERE id = ?", (hospital_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Hospital not found")
    try:
        c.execute(
            "UPDATE hospitals SET name = ?, address = ?, lat = ?, lng = ? WHERE id = ?",
            (hospital.name, hospital.address, hospital.lat, hospital.lng, hospital_id),
        )
        conn.commit()
        logger.info(
            f"Hospital updated: {hospital_id} by super_admin: {current_user['user_id']}"
        )
        return HospitalResponse(
            id=hospital_id,
            name=hospital.name,
            address=hospital.address,
            lat=hospital.lat,
            lng=hospital.lng,
        )
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Hospital name already exists")
    finally:
        conn.close()


@app.delete("/api/hospitals/{hospital_id}")
async def delete_hospital(
    hospital_id: str, current_user: dict = Depends(require_role("super_admin"))
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM hospitals WHERE id = ?", (hospital_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Hospital not found")
    c.execute("DELETE FROM hospitals WHERE id = ?", (hospital_id,))
    conn.commit()
    conn.close()
    logger.info(
        f"Hospital deleted: {hospital_id} by super_admin: {current_user['user_id']}"
    )
    return {"detail": "Hospital deleted"}


@app.post("/api/hospitals/{hospital_id}/assign-admin")
async def assign_hospital_admin(
    hospital_id: str,
    assignment: HospitalAdminAssign,
    current_user: dict = Depends(require_role("super_admin")),
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Verify hospital exists
    c.execute("SELECT id FROM hospitals WHERE id = ?", (hospital_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Hospital not found")
    # Verify user exists and is an admin
    c.execute("SELECT id, role FROM users WHERE id = ?", (assignment.user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if user[1] != "admin":
        conn.close()
        raise HTTPException(status_code=400, detail="User must be an admin")
    # Assign admin to hospital
    assigned_at = datetime.utcnow().isoformat()
    try:
        c.execute(
            "INSERT INTO hospital_admins (hospital_id, user_id, assigned_at) VALUES (?, ?, ?)",
            (hospital_id, assignment.user_id, assigned_at),
        )
        conn.commit()
        logger.info(
            f"Admin {assignment.user_id} assigned to hospital {hospital_id} by super_admin: {current_user['user_id']}"
        )
        return {"detail": "Admin assigned to hospital"}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400, detail="Admin already assigned to this hospital"
        )
    finally:
        conn.close()


@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    logger.info(f"Chatbot query: {request.query}")
    return {"response": "Hello, How are you doing? I hope you are doing good"}


@app.get("/api/emergency/hospitals", response_model=dict)
async def get_nearby_hospitals(
    lat: float, lng: float, current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(
            f"Fetching hospitals for lat: {lat}, lng: {lng}, user: {current_user['user_id']}"
        )
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node["amenity"="hospital"](around:10000,{lat},{lng});
        out body;
        """
        response = requests.post(overpass_url, data=query)
        response.raise_for_status()
        data = response.json()
        hospitals = []
        for element in data["elements"][:15]:
            hospital = {
                "name": element["tags"].get("name", "Unnamed Hospital"),
                "address": element["tags"].get("addr:street", "Address not available"),
                "lat": element["lat"],
                "lng": element["lon"],
                "doctorAvailability": (
                    True if hash(element["tags"].get("name", "")) % 2 == 0 else False
                ),
            }
            hospitals.append(hospital)
        logger.info(f"Found {len(hospitals)} hospitals")
        return {"hospitals": hospitals}
    except requests.RequestException as e:
        logger.error(f"Overpass API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Overpass API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_nearby_hospitals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/api/debug/version")
async def debug_version(current_user: dict = Depends(get_current_user)):
    """Return the version of the running main.py to verify correct code."""
    logger.info(f"Debug version requested by user: {current_user['user_id']}")
    return {"version": "7a8c3e9d-2b1f-4e7c-9f2a-5c3d8e6f9012", "file": "main.py"}


@app.post("/api/medical-query")
async def medical_query(
    query: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    request: Request = None,
):
    """Process blood report and/or answer query using public API."""
    try:
        form_data = await request.form()
        logger.info(
            f"Received medical query for user: {current_user['user_id']}, raw_query: {query!r}, file: {file.filename if file else None}, form_data: {dict(form_data)}"
        )

        json_output = None
        response = None

        if file:
            file_path = f"uploads/{current_user['user_id']}_{file.filename}"
            logger.info(f"Saving file: {file_path}")
            os.makedirs("uploads", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            report_text = await parse_blood_report(file_path)
            json_output, _ = await structure_report(report_text)
            os.remove(file_path)
            logger.info(f"File processed and deleted: {file_path}")

            effective_query = (
                query.strip() if query else "Explain my blood test results"
            )
            logger.info(f"Effective query for file upload: {effective_query}")
        else:
            if query is None or query.strip() == "":
                logger.error("No query provided for follow-up question")
                raise HTTPException(
                    status_code=400,
                    detail="A non-empty query is required when no file is uploaded.",
                )

            history = get_chat_history(current_user["user_id"])
            if history and any(h["report_json"] for h in history):
                logger.info(
                    f"Retrieving stored report for user: {current_user['user_id']}"
                )
                json_output = json.loads(history[-1]["report_json"])
            else:
                logger.info("No stored report, proceeding with query only")
                json_output = None

            effective_query = query.strip()
            logger.info(f"Effective query for follow-up: {effective_query}")

        prompt = f"""
You are a friendly medical AI assistant who explains blood test results and answers medical questions in simple, kind words for non-experts. Follow these guidelines:
1. Keep answers 100-150 words, clear, and focused.
2. Use analogies (e.g., “Red blood cells are like trucks carrying oxygen”) and avoid jargon.
3. Suggest 1-2 next steps (e.g., “Talk to your doctor about iron supplements”).
4. Highlight urgency (e.g., “If you feel dizzy, go now”).
5. Note this is not a diagnosis and recommend consulting a doctor.
6. Output only the answer text, without labels like "assistant:" or code blocks.

Current Query: {effective_query}
"""
        if json_output:
            patient_age = json_output.get("patient_info", {}).get("age", "Unknown")
            patient_gender = json_output.get("patient_info", {}).get(
                "gender", "Unknown"
            )
            prompt += f"""
Patient Age: {patient_age}
Patient Gender: {patient_gender}
Blood Test Results (JSON):
{json.dumps(json_output, indent=2)}
"""
        else:
            prompt += "\nNo blood test results available."

        logger.info(f"Sending prompt to public API: {prompt[:100]}...")
        api_response = requests.post(
            PUBLIC_API_URL, json={"prompt": prompt, "max_new_tokens": 300}
        )
        api_response.raise_for_status()
        response_data = api_response.json()

        if "error" in response_data:
            logger.error(f"Public API error: {response_data['error']}")
            raise HTTPException(
                status_code=500, detail=f"Public API error: {response_data['error']}"
            )

        raw_response = response_data.get("generated_text")
        if not raw_response:
            logger.error("No generated_text in public API response")
            raise HTTPException(
                status_code=500, detail="No generated_text in public API response"
            )

        cleaned_response = raw_response.strip()
        cleaned_response = re.sub(
            r"^(assistant:|[\[\{]?(ANSWER|RESPONSE)[\]\}]?:?\s*)",
            "",
            cleaned_response,
            flags=re.IGNORECASE,
        )
        cleaned_response = re.sub(
            r"```(?:json)?\s*(.*?)\s*```", r"\1", cleaned_response, flags=re.DOTALL
        )
        cleaned_response = re.sub(r"\s*(</s>|[EOT]|\[.*?\])$", "", cleaned_response)
        if not cleaned_response.strip():
            logger.error("Cleaned response is empty")
            raise HTTPException(status_code=500, detail="Cleaned response is empty")

        response = cleaned_response.strip()
        logger.info(f"Parsed public API response: {response[:100]}...")

        store_chat_history(
            user_id=current_user["user_id"],
            query=effective_query,
            report_json=json.dumps(json_output) if json_output else "",
            response=response,
        )

        logger.info("Query processed successfully")
        return {"structured_report": json_output, "response": response}
    except requests.RequestException as e:
        logger.error(f"Public API request failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Public API request failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/acne-analysis")
async def acne_analysis(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        logger.info(
            f"Received acne image for user: {current_user['user_id']}, file: {image.filename}"
        )
        if image.content_type not in ["image/jpeg", "image/png"]:
            logger.error(f"Invalid file type: {image.content_type}")
            raise HTTPException(
                status_code=400, detail="Only JPEG or PNG images are supported."
            )
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_url = f"data:{image.content_type};base64,{base64_image}"
        response = await analyze_acne_image(image_url, current_user["user_id"])
        logger.info("Acne image analysis completed successfully")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing acne image: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing acne image: {str(e)}"
        )


##########################################################################################
##########################################################################################
############################ Admin  ###################################
##########################################################################################
##########################################################################################
##########################################################################################


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: str
    hospital_id: str
    name: str
    hospital_name: Optional[str]


class DoctorCreate(BaseModel):
    department_id: str
    username: str
    specialty: str
    title: str
    phone: Optional[str] = None
    bio: Optional[str] = None


class DoctorResponse(BaseModel):
    user_id: str
    username: str
    email: str
    department_id: str
    department_name: str
    specialty: str
    title: str
    phone: Optional[str]
    bio: Optional[str]


class AvailabilityCreate(BaseModel):
    user_id: str
    day_of_week: str
    start_time: str
    end_time: str


class AvailabilityResponse(BaseModel):
    id: str
    user_id: str
    day_of_week: str
    start_time: str
    end_time: str


class AppointmentCreate(BaseModel):
    doctor_id: str
    department_id: str
    hospital_id: str
    appointment_date: str
    start_time: str
    end_time: str


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    doctor_id: str
    doctor_username: str
    department_id: str
    department_name: str
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    created_at: str
    hospital_id: Optional[str] = None


class DoctorCreate(BaseModel):
    department_id: str
    username: str
    email: str
    password: str
    specialty: str
    title: str
    phone: Optional[str] = None
    bio: Optional[str] = None


class MedicalHistoryResponse(BaseModel):
    id: str
    user_id: str
    conditions: Optional[str]
    allergies: Optional[str]
    notes: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]


@app.get("/api/admin/hospital", response_model=HospitalResponse)
async def get_admin_hospital(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    logger.info(f"Current user: {current_user}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT h.id, h.name, h.address, h.lat, h.lng FROM hospitals h JOIN hospital_admins ha ON h.id = ha.hospital_id WHERE ha.user_id = ?",
        (current_user["user_id"],),
    )
    hospital = c.fetchone()
    conn.close()

    if not hospital:
        raise HTTPException(status_code=404, detail="No hospital assigned")

    return HospitalResponse(
        id=hospital[0],
        name=hospital[1],
        address=hospital[2],
        lat=hospital[3],
        lng=hospital[4],
    )


@app.post("/api/departments", response_model=DepartmentResponse)
async def create_department(
    department: DepartmentCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT hospital_id FROM hospital_admins WHERE user_id = ?",
        (current_user["user_id"],),
    )
    hospital_id = c.fetchone()
    if not hospital_id:
        conn.close()
        raise HTTPException(status_code=404, detail="No hospital assigned")
    hospital_id = hospital_id[0]

    department_id = str(uuid.uuid4())
    c.execute(
        "INSERT INTO departments (id, hospital_id, name) VALUES (?, ?, ?)",
        (department_id, hospital_id, department.name),
    )

    conn.commit()
    conn.close()

    logger.info(f"Department created: {department.name} in hospital {hospital_id}")
    return DepartmentResponse(
        id=department_id, hospital_id=hospital_id, name=department.name
    )


@app.post("/api/doctors", response_model=dict)
async def assign_doctor(
    doctor: DoctorCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    logger.info(
        f"Assigning doctor: username={doctor.username}, department_id={doctor.department_id}, email={doctor.email}"
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get admin's hospital
    c.execute(
        "SELECT hospital_id FROM hospital_admins WHERE user_id = ?",
        (current_user["user_id"],),
    )
    hospital_id = c.fetchone()
    if not hospital_id:
        conn.close()
        logger.error("No hospital assigned to admin")
        raise HTTPException(status_code=404, detail="No hospital assigned")
    hospital_id = hospital_id[0]
    logger.info(f"Admin hospital_id: {hospital_id}")

    # Verify department belongs to admin's hospital
    c.execute(
        "SELECT id FROM departments WHERE id = ? AND hospital_id = ?",
        (doctor.department_id, hospital_id),
    )
    department = c.fetchone()
    if not department:
        conn.close()
        logger.error(
            f"Department not found: id={doctor.department_id}, hospital_id={hospital_id}"
        )
        raise HTTPException(
            status_code=404, detail="Department not found or not in your hospital"
        )

    # Check if user exists
    c.execute("SELECT id, role FROM users WHERE username = ?", (doctor.username,))
    user = c.fetchone()
    if user:
        user_id, user_role = user
        logger.info(f"Found existing user: id={user_id}, role={user_role}")
        if user_role != "doctor":
            c.execute("UPDATE users SET role = 'doctor' WHERE id = ?", (user_id,))
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = pwd_context.hash(doctor.password)
        created_at = datetime.utcnow().isoformat()
        try:
            c.execute(
                """
                INSERT INTO users (id, username, email, password, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    doctor.username,
                    doctor.email,
                    hashed_password,
                    "doctor",
                    created_at,
                ),
            )
            logger.info(f"Created new user: id={user_id}, username={doctor.username}")
        except sqlite3.IntegrityError as e:
            conn.close()
            logger.error(f"User creation failed: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Username or email already exists"
            )

    # Check if doctor is already assigned to this department
    c.execute(
        "SELECT user_id FROM doctors WHERE user_id = ? AND department_id = ?",
        (user_id, doctor.department_id),
    )
    if c.fetchone():
        conn.close()
        logger.error(
            f"Doctor already assigned: user_id={user_id}, department_id={doctor.department_id}"
        )
        raise HTTPException(
            status_code=400, detail="Doctor already assigned to this department"
        )

    # Assign doctor to department
    c.execute(
        """
        INSERT INTO doctors (user_id, department_id, specialty, title, phone, bio)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            doctor.department_id,
            doctor.specialty,
            doctor.title,
            doctor.phone,
            doctor.bio,
        ),
    )

    # Initialize availability (Mon–Sat, 9 AM–6 PM, 30-min slots)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    slots = [
        ("09:00", "09:30"),
        ("09:30", "10:00"),
        ("10:00", "10:30"),
        ("10:30", "11:00"),
        ("11:00", "11:30"),
        ("11:30", "12:00"),
        ("12:00", "12:30"),
        ("12:30", "13:00"),
        ("13:00", "13:30"),
        ("13:30", "14:00"),
        ("14:00", "14:30"),
        ("14:30", "15:00"),
        ("15:00", "15:30"),
        ("15:30", "16:00"),
        ("16:00", "16:30"),
        ("16:30", "17:00"),
        ("17:00", "17:30"),
        ("17:30", "18:00"),
    ]
    for day in days:
        for start, end in slots:
            availability_id = str(uuid.uuid4())
            c.execute(
                """
                INSERT INTO doctor_availability (id, user_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (availability_id, user_id, day, start, end),
            )

    conn.commit()
    conn.close()

    logger.info(
        f"Assigned doctor {doctor.username} to department {doctor.department_id}"
    )
    return {"message": f"Doctor {doctor.username} assigned to department"}


@app.get("/api/departments", response_model=List[DepartmentResponse])
async def get_departments(
    hospital_id: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = """
        SELECT d.id, d.hospital_id, d.name, h.name
        FROM departments d
        JOIN hospitals h ON d.hospital_id = h.id
    """
    params = []
    if hospital_id:
        query += " WHERE d.hospital_id = ?"
        params.append(hospital_id)
    c.execute(query, params)
    departments = [
        DepartmentResponse(
            id=row[0], hospital_id=row[1], name=row[2], hospital_name=row[3]
        )
        for row in c.fetchall()
    ]
    conn.close()
    logger.info(
        f"Fetched departments for user {current_user['user_id']}, hospital_id: {hospital_id}"
    )
    return departments


# Updated endpoint: GET /api/doctors
@app.get("/api/doctors", response_model=List[DoctorResponse])
async def get_doctors(
    department_id: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = """
        SELECT doc.user_id, u.username, u.email, doc.department_id, d.name,
               doc.specialty, doc.title, doc.phone, doc.bio
        FROM doctors doc
        JOIN users u ON doc.user_id = u.id
        JOIN departments d ON doc.department_id = d.id
    """
    params = []
    if department_id:
        query += " WHERE doc.department_id = ?"
        params.append(department_id)
    c.execute(query, params)
    doctors = [
        DoctorResponse(
            user_id=row[0],
            username=row[1],
            email=row[2],
            department_id=row[3],
            department_name=row[4],
            specialty=row[5],
            title=row[6],
            phone=row[7],
            bio=row[8],
        )
        for row in c.fetchall()
    ]
    conn.close()
    logger.info(
        f"Fetched doctors for user {current_user['user_id']}, department_id: {department_id}"
    )
    return doctors


@app.get(
    "/api/doctors/{doctor_id}/availability", response_model=List[AvailabilityResponse]
)
async def get_doctor_availability(
    doctor_id: str, current_user: dict = Depends(get_current_user)
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, user_id, day_of_week, start_time, end_time
        FROM doctor_availability
        WHERE user_id = ?
        """,
        (doctor_id,),
    )
    availability = [
        AvailabilityResponse(
            id=row[0],
            user_id=row[1],
            day_of_week=row[2],
            start_time=row[3],
            end_time=row[4],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched availability for doctor {doctor_id}")
    return availability


@app.post("/api/appointments", response_model=AppointmentResponse)
async def book_appointment(
    appointment: AppointmentCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verify doctor exists and get username
    c.execute(
        """
        SELECT u.id, u.username
        FROM users u
        WHERE u.id = ? AND u.role = 'doctor'
        """,
        (appointment.doctor_id,),
    )
    doctor = c.fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor_id, doctor_username = doctor

    # Verify department exists and get name
    c.execute(
        """
        SELECT d.id, d.name
        FROM departments d
        WHERE d.id = ?
        """,
        (appointment.department_id,),
    )
    department = c.fetchone()
    if not department:
        conn.close()
        raise HTTPException(status_code=404, detail="Department not found")
    department_id, department_name = department

    # Verify hospital exists
    c.execute("SELECT id FROM hospitals WHERE id = ?", (appointment.hospital_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Hospital not found")

    # Verify slot is available
    c.execute(
        """
        SELECT id FROM doctor_availability
        WHERE user_id = ? AND day_of_week = ? AND start_time = ? AND end_time = ?
        """,
        (
            appointment.doctor_id,
            datetime.strptime(appointment.appointment_date, "%Y-%m-%d").strftime("%A"),
            appointment.start_time,
            appointment.end_time,
        ),
    )
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Slot not available")

    # Check if slot is already booked
    c.execute(
        """
        SELECT id FROM appointments
        WHERE doctor_id = ? AND appointment_date = ? AND start_time = ? AND status != 'cancelled'
        """,
        (appointment.doctor_id, appointment.appointment_date, appointment.start_time),
    )
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Slot already booked")

    # Fetch patient's username
    c.execute(
        "SELECT username FROM users WHERE id = ?",
        (current_user["user_id"],),
    )
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    patient_username = user[0]

    # Insert appointment
    appointment_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    c.execute(
        """
        INSERT INTO appointments (
            id, user_id, doctor_id, department_id, hospital_id, appointment_date, 
            start_time, end_time, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            appointment_id,
            current_user["user_id"],
            appointment.doctor_id,
            appointment.department_id,
            appointment.hospital_id,
            appointment.appointment_date,
            appointment.start_time,
            appointment.end_time,
            "scheduled",
            created_at,
        ),
    )

    conn.commit()
    conn.close()

    logger.info(
        f"Booked appointment for user {current_user['user_id']} with doctor {appointment.doctor_id}"
    )
    return AppointmentResponse(
        id=appointment_id,
        user_id=current_user["user_id"],
        username=patient_username,  # Use fetched username
        email=None,  # Still not needed by frontend
        doctor_id=appointment.doctor_id,
        doctor_username=doctor_username,
        department_id=appointment.department_id,
        department_name=department_name,
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        status="scheduled",
        created_at=created_at,
        hospital_id=appointment.hospital_id,
    )


class TimeSlotResponse(BaseModel):
    start_time: str
    end_time: str


@app.get("/api/doctor/{doctor_id}/slots", response_model=List[TimeSlotResponse])
async def get_doctor_slots(
    doctor_id: str, date: str, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["user", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        # Validate date format
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = appointment_date.strftime("%A")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Verify doctor exists
    c.execute(
        "SELECT id FROM users WHERE id = ? AND role = 'doctor'",
        (doctor_id,),
    )
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Get available slots for the doctor on the given day
    c.execute(
        """
        SELECT da.start_time, da.end_time
        FROM doctor_availability da
        WHERE da.user_id = ? AND da.day_of_week = ?
        AND NOT EXISTS (
            SELECT 1 FROM appointments a
            WHERE a.doctor_id = da.user_id
            AND a.appointment_date = ?
            AND a.start_time = da.start_time
            AND a.status != 'cancelled'
        )
        ORDER BY da.start_time
        """,
        (doctor_id, day_of_week, date),
    )
    slots = [
        TimeSlotResponse(start_time=row[0], end_time=row[1]) for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched available slots for doctor {doctor_id} on {date}")
    return slots


@app.get("/api/appointments", response_model=List[AppointmentResponse])
async def get_appointments(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if current_user["role"] == "admin":
        c.execute(
            """
            SELECT a.id, a.user_id, a.doctor_id, a.department_id, a.appointment_date, a.start_time, a.end_time, a.status, a.created_at
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.user_id
            JOIN departments dept ON d.department_id = dept.id
            JOIN hospital_admins ha ON dept.hospital_id = ha.hospital_id
            WHERE ha.user_id = ?
            """,
            (current_user["user_id"],),
        )
    else:
        c.execute(
            """
            SELECT id, user_id, doctor_id, department_id, appointment_date, start_time, end_time, status, created_at
            FROM appointments
            WHERE user_id = ?
            """,
            (current_user["user_id"],),
        )
    appointments = [
        AppointmentResponse(
            id=row[0],
            user_id=row[1],
            doctor_id=row[2],
            department_id=row[3],
            appointment_date=row[4],
            start_time=row[5],
            end_time=row[6],
            status=row[7],
            created_at=row[8],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched appointments for user {current_user['user_id']}")
    return appointments


##########################################################################################
##########################################################################################
############################ Doctor  ###################################
##########################################################################################
##########################################################################################
##########################################################################################


# New endpoints
@app.get("/api/doctor/department", response_model=DepartmentResponse)
async def get_doctor_department(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT d.id, d.hospital_id, d.name, h.name
        FROM departments d
        JOIN doctors doc ON d.id = doc.department_id
        JOIN hospitals h ON d.hospital_id = h.id
        WHERE doc.user_id = ?
        """,
        (current_user["user_id"],),
    )
    department = c.fetchone()
    conn.close()

    if not department:
        raise HTTPException(status_code=404, detail="No department assigned")

    logger.info(f"Fetched department for doctor {current_user['user_id']}")
    return DepartmentResponse(
        id=department[0],
        hospital_id=department[1],
        name=department[2],
        hospital_name=department[3],
    )


@app.get("/api/doctor/appointments/today", response_model=List[AppointmentResponse])
async def get_todays_appointments(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")

    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT a.id, a.user_id, u.username, u.email, a.doctor_id, du.username, a.department_id,
               d.name, a.appointment_date, a.start_time, a.end_time, a.status, a.created_at,
               a.hospital_id
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN users du ON a.doctor_id = du.id
        JOIN departments d ON a.department_id = d.id
        WHERE a.doctor_id = ? AND a.appointment_date = ? AND a.status != 'cancelled'
        ORDER BY a.start_time
        """,
        (current_user["user_id"], today),
    )
    appointments = [
        AppointmentResponse(
            id=row[0],
            user_id=row[1],
            username=row[2],
            email=row[3],
            doctor_id=row[4],
            doctor_username=row[5],
            department_id=row[6],
            department_name=row[7],
            appointment_date=row[8],
            start_time=row[9],
            end_time=row[10],
            status=row[11],
            created_at=row[12],
            hospital_id=row[13],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched today's appointments for doctor {current_user['user_id']}")
    return appointments


@app.get("/api/doctor/appointments/week", response_model=List[AppointmentResponse])
async def get_weekly_appointments(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Calculate the start (Monday) and end (Sunday) of the current week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    start_date = start_of_week.isoformat()
    end_date = end_of_week.isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT a.id, a.user_id, u.username, u.email, a.doctor_id, du.username, a.department_id,
               d.name, a.appointment_date, a.start_time, a.end_time, a.status, a.created_at,
               a.hospital_id
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN users du ON a.doctor_id = du.id
        JOIN departments d ON a.department_id = d.id
        WHERE a.doctor_id = ? 
        AND a.appointment_date BETWEEN ? AND ? 
        AND a.status != 'cancelled'
        ORDER BY a.appointment_date, a.start_time
        """,
        (current_user["user_id"], start_date, end_date),
    )
    appointments = [
        AppointmentResponse(
            id=row[0],
            user_id=row[1],
            username=row[2],
            email=row[3],
            doctor_id=row[4],
            doctor_username=row[5],
            department_id=row[6],
            department_name=row[7],
            appointment_date=row[8],
            start_time=row[9],
            end_time=row[10],
            status=row[11],
            created_at=row[12],
            hospital_id=row[13],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(
        f"Fetched weekly appointments for doctor {current_user['user_id']} from {start_date} to {end_date}"
    )
    return appointments


@app.get(
    "/api/doctor/patient/{user_id}/history", response_model=List[MedicalHistoryResponse]
)
async def get_patient_medical_history(
    user_id: str, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify doctor has an appointment with this patient
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT id FROM appointments
        WHERE doctor_id = ? AND user_id = ? AND status != 'cancelled'
        """,
        (current_user["user_id"], user_id),
    )
    if not c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=403, detail="No active appointments with this patient"
        )

    c.execute(
        """
        SELECT id, user_id, conditions, allergies, notes, updated_at, updated_by
        FROM medical_history
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    history = [
        MedicalHistoryResponse(
            id=row[0],
            user_id=row[1],
            conditions=row[2],
            allergies=row[3],
            notes=row[4],
            updated_at=row[5],
            updated_by=row[6],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(
        f"Fetched medical history for patient {user_id} by doctor {current_user['user_id']}"
    )
    return history


##########################################################################################
##########################################################################################
############################ Super Admin  ###################################
##########################################################################################
##########################################################################################
##########################################################################################


# Models (only new/updated models shown)
class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    hospital_name: Optional[str]


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    username: str
    doctor_id: str
    doctor_username: str
    department_id: str
    department_name: str
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    created_at: str


# Updated endpoint: GET /api/admins
@app.get("/api/admins", response_model=List[AdminResponse])
async def get_admins(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT u.id, u.username, u.email, u.role, h.name
        FROM users u
        LEFT JOIN hospital_admins ha ON u.id = ha.user_id
        LEFT JOIN hospitals h ON ha.hospital_id = h.id
        WHERE u.role = 'admin'
        """
    )
    admins = [
        AdminResponse(
            id=row[0], username=row[1], email=row[2], role=row[3], hospital_name=row[4]
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched admins for superadmin {current_user['user_id']}")
    return admins


# New endpoint: GET /api/appointments
@app.get("/api/appointments", response_model=List[AppointmentResponse])
async def get_all_appointments(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT a.id, a.user_id, u.username, a.doctor_id, du.username, a.department_id,
               d.name, a.appointment_date, a.start_time, a.end_time, a.status, a.created_at
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN users du ON a.doctor_id = du.id
        JOIN departments d ON a.department_id = d.id
        WHERE a.status != 'cancelled'
        ORDER BY a.appointment_date, a.start_time
        """
    )
    appointments = [
        AppointmentResponse(
            id=row[0],
            user_id=row[1],
            username=row[2],
            doctor_id=row[3],
            doctor_username=row[4],
            department_id=row[5],
            department_name=row[6],
            appointment_date=row[7],
            start_time=row[8],
            end_time=row[9],
            status=row[10],
            created_at=row[11],
        )
        for row in c.fetchall()
    ]
    conn.close()

    logger.info(f"Fetched all appointments for superadmin {current_user['user_id']}")
    return appointments


class AdminCreate(BaseModel):
    username: str
    email: str
    password: str
    hospital_id: Optional[str]


@app.post("/api/admins")
async def create_admin(
    admin: AdminCreate, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if username or email already exists
    c.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (admin.username, admin.email),
    )
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Validate hospital_id if provided
    if admin.hospital_id:
        c.execute("SELECT id FROM hospitals WHERE id = ?", (admin.hospital_id,))
        if not c.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid hospital ID")

    # Generate user ID and hash password
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(admin.password)
    created_at = datetime.utcnow().isoformat()

    # Insert user
    try:
        c.execute(
            """
            INSERT INTO users (id, username, email, password, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                admin.username,
                admin.email,
                hashed_password,
                "admin",
                created_at,
            ),
        )

        # Assign to hospital if hospital_id is provided
        if admin.hospital_id:
            assigned_at = datetime.utcnow().isoformat()
            c.execute(
                """
                INSERT INTO hospital_admins (hospital_id, user_id, assigned_at)
                VALUES (?, ?, ?)
                """,
                (admin.hospital_id, user_id, assigned_at),
            )

        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

    logger.info(
        f"Created admin user {user_id} by super_admin {current_user['user_id']}"
    )
    return {"message": "Admin created successfully"}


from datetime import date, timedelta


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
