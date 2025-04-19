import os
import json
import logging
import base64
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import sqlite3
from dotenv import load_dotenv
from jose import jwt
from jose.exceptions import JWTError
from models.user import UserCreate, UserInDB, UserResponse, Token, LoginRequest
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import requests
from utils.parser import (
    parse_blood_report,
    structure_report,
    interpret_report,
    answer_followup_query,
    get_chat_history,
    analyze_acne_image,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
DB_PATH = os.getenv("SQLITE_DB_PATH", "users.db")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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


class ChatbotRequest(BaseModel):
    query: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Hospital(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    doctorAvailability: bool


class MedicalQueryRequest(BaseModel):
    query: str


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.info(f"Authenticated user: {user_id}")
        return user_id
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


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
        "SELECT id, username, email, password, created_at FROM users WHERE username = ?",
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
            created_at=datetime.fromisoformat(user[4]),
        )
    return None


@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserCreate):
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
    c.execute(
        "INSERT INTO users (id, username, email, password, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, user.username, user.email, hashed_password, created_at),
    )
    conn.commit()
    conn.close()
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User signed up: {user.username}")
    return {
        "token": access_token,
        "user": UserResponse(id=user_id, username=user.username, email=user.email),
    }


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = await get_user(login_data.username)
    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        logger.error(f"Login failed for username: {login_data.username}")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User logged in: {user.username}")
    return {
        "token": access_token,
        "user": UserResponse(id=user.id, username=user.username, email=user.email),
    }


@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    logger.info(f"Chatbot query: {request.query}")
    return {"response": "Hello, How are you doing? I hope you are doing good"}


@app.get("/api/emergency/hospitals", response_model=dict)
async def get_nearby_hospitals(
    lat: float, lng: float, current_user: str = Depends(get_current_user)
):
    try:
        logger.info(
            f"Fetching hospitals for lat: {lat}, lng: {lng}, user: {current_user}"
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
async def debug_version(current_user: str = Depends(get_current_user)):
    logger.info(f"Debug version requested by user: {current_user}")
    return {"version": "3e7f9a2b-5c6a-4d8b-b9e3-1c4e0f2d7a9c", "file": "main.py"}


@app.post("/api/medical-query")
async def medical_query(
    query: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
    request: Request = None,
):
    """Process blood report and/or answer follow-up query using stored report."""
    form_data = await request.form()
    logger.info(
        f"Received medical query for user: {current_user}, raw_query: {query!r}, file: {file.filename if file else None}, form_data: {dict(form_data)}"
    )

    json_output = None
    response = None

    if file:
        # Case 1: File uploaded (with or without query)
        file_path = f"uploads/{current_user}_{file.filename}"
        logger.info(f"Saving file: {file_path}")
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        report_text = await parse_blood_report(file_path)
        json_output, _ = await structure_report(report_text)
        os.remove(file_path)
        logger.info(f"File processed and deleted: {file_path}")

        # Use provided query or default to "Explain my blood test results"
        effective_query = query.strip() if query else "Explain my blood test results"
        logger.info(f"Effective query for file upload: {effective_query}")
        response, _ = await interpret_report(json_output, effective_query, current_user)
    else:
        # Case 2: No file, must have a query
        if query is None or query.strip() == "":
            logger.error("No query provided for follow-up question")
            raise HTTPException(
                status_code=400,
                detail="A non-empty query is required when no file is uploaded.",
            )

        # Retrieve stored report
        history = get_chat_history(current_user)
        if history and any(h["report_json"] for h in history):
            logger.info(f"Retrieving stored report for user: {current_user}")
            json_output = json.loads(history[-1]["report_json"])
        else:
            logger.error("No report uploaded for user")
            raise HTTPException(
                status_code=400,
                detail="No report uploaded. Please upload a blood report first.",
            )

        # Process follow-up query with stored report
        effective_query = query.strip()
        logger.info(f"Effective query for follow-up: {effective_query}")
        response, _ = await answer_followup_query(
            json_output, effective_query, current_user
        )

    logger.info("Query processed successfully")
    return {"structured_report": json_output, "response": response}


@app.post("/api/acne-analysis")
async def acne_analysis(
    image: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Analyze an acne-related image and provide insights."""
    try:
        logger.info(
            f"Received acne image for user: {current_user}, file: {image.filename}"
        )

        # Validate file type
        if image.content_type not in ["image/jpeg", "image/png"]:
            logger.error(f"Invalid file type: {image.content_type}")
            raise HTTPException(
                status_code=400, detail="Only JPEG or PNG images are supported."
            )

        # Read and encode image to base64
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_url = f"data:{image.content_type};base64,{base64_image}"

        # Analyze image using Groq
        response = await analyze_acne_image(image_url, current_user)
        logger.info("Acne image analysis completed successfully")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing acne image: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing acne image: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
