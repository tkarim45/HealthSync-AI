from fastapi import APIRouter, HTTPException
import sqlite3
import jwt
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

SECRET_KEY = "your-secret-key"  # Replace with a secure key
ALGORITHM = "HS256"


class User(BaseModel):
    id: int
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """
    )
    c.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("testuser", "testpass"),
    )
    conn.commit()
    conn.close()


init_db()


@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password = ?",
        (user.username, user.password),
    )
    db_user = c.fetchone()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {"id": db_user[0], "username": db_user[1]}, SECRET_KEY, algorithm=ALGORITHM
    )
    return {"token": token, "user": {"id": db_user[0], "username": db_user[1]}}
