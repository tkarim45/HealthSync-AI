import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_PATH = os.getenv(
        "DB_PATH",
        "/Users/taimourabdulkarim/Documents/Personal Github Repositories/HealthSync-AI/backend/healthsync.db",
    )
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    PUBLIC_API_URL = os.getenv(
        "PUBLIC_API_URL", "https://6af3-34-169-149-75.ngrok-free.app/generate"
    )
    ALLOWED_ORIGINS = ["http://localhost:3000"]
    GOOGLE_API_KEY = os.getenv(
        "GOOGLE_API_KEY", "AIzaSyAbF61cmhhOth0uo0esgsrY5edTGykCdAw"
    )
    PINECONE_API_KEY = os.getenv(
        "PINECONE_API_KEY",
        "pcsk_76DBPG_F4EW97MoRMhn7EPWmiwjzyAv2L1camQd7katdQcniJikBHLgcXMcQB5HKNLSFTp",
    )
    # Email settings
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = os.getenv("SMTP_PORT", 587)


settings = Settings()
