from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import sqlite3
from dotenv import load_dotenv
from jose import jwt
from models.user import UserCreate, UserInDB, UserResponse, Token, LoginRequest
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel
import googlemaps
import requests

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DB_PATH = os.getenv("SQLITE_DB_PATH")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic model for chatbot request
class ChatbotRequest(BaseModel):
    query: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Hospital response model
class Hospital(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    doctorAvailability: bool


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


# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
            id=user[0],  # Explicitly map fields
            username=user[1],
            email=user[2],
            hashed_password=user[3],  # Use hashed_password for verification
            created_at=datetime.fromisoformat(user[4]),
        )
    return None


@app.post("/api/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    # print(f"Received signup request: {user.dict()}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username, email FROM users WHERE username = ? OR email = ?",
        (user.username, user.email),
    )
    if c.fetchone():
        conn.close()
        print(f"User {user.username} or email {user.email} already exists")
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
    # print(f"Signup successful for user: {user.username}, ID: {user_id}")
    return {
        "token": access_token,
        "user": UserResponse(id=user_id, username=user.username, email=user.email),
    }


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    # print(f"Received login request for username: {login_data.username}")
    user = await get_user(login_data.username)
    if not user or not pwd_context.verify(
        login_data.password, user.hashed_password
    ):  # Direct verification
        # print(f"Login failed for username: {login_data.username}")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # print(f"Login successful for user: {login_data.username}")
    return {
        "token": access_token,
        "user": UserResponse(id=user.id, username=user.username, email=user.email),
    }


# chatbot endpoint
@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    print(f"Received chatbot query: {request.query}")
    return {"response": "Hello, How are you doing? I hope you are doing good"}


@app.get("/api/emergency/hospitals", response_model=dict)
async def get_nearby_hospitals(
    lat: float, lng: float, current_user: str = Depends(get_current_user)
):
    try:
        # Overpass API query for hospitals within ~5km (0.045 degrees ~ 5km)
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
        for element in data["elements"][:15]:  # Limit to 5
            hospital = {
                "name": element["tags"].get("name", "Unnamed Hospital"),
                "address": element["tags"].get("addr:street", "Address not available"),
                "lat": element["lat"],
                "lng": element["lon"],
                "doctorAvailability": (
                    True if hash(element["tags"].get("name", "")) % 2 == 0 else False
                ),  # Mock
            }
            hospitals.append(hospital)

        return {"hospitals": hospitals}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Overpass API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
