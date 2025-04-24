from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"  # Default to regular user


class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    role: str
    created_at: datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str


class Token(BaseModel):
    token: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class HospitalCreate(BaseModel):
    name: str
    address: str
    lat: float
    lng: float


class HospitalResponse(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float


class HospitalAdminAssign(BaseModel):
    user_id: str
