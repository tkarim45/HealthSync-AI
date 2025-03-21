from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    created_at: Optional[datetime] = datetime.utcnow()


class UserInDB(BaseModel):
    id: str
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr


class Token(BaseModel):
    token: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str
