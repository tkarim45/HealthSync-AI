from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import logging
from models.schemas import UserCreate, Token, LoginRequest, UserResponse
from utils.db import get_user, get_db_connection
from config.settings import settings
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Retrieve the current user from a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
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


@router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    """Register a new user."""
    logger.info(f"Attempting signup for username: {user.username}")
    conn = get_db_connection()
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
    role = "user"  # Restrict to 'user' role
    c.execute(
        "INSERT INTO users (id, username, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, user.username, user.email, hashed_password, role, created_at),
    )
    conn.commit()
    conn.close()

    access_token = create_access_token(
        data={"sub": user_id, "role": role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"User signed up: {user.username}")
    return {
        "token": access_token,
        "user": UserResponse(
            id=user_id, username=user.username, email=user.email, role=role
        ),
    }


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    conn = get_db_connection()
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
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
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
