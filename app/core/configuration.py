import os

APP_TITLE = os.getenv("APP_TITLE", "MY NEW API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_MONGO_URL = os.getenv("APP_MONGO_URL", "mongodb://user:password@localhost/db")
APP_MONGO_DB = os.getenv("APP_MONGO_DB", "db")
APP_SECRET_KEY = os.getenv(
    "APP_SECRET_KEY",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
)
APP_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("APP_ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
)
APP_USERS_API_URL = os.getenv("APP_USERS_API_URL", "http://localhost:8000")
APP_USERS_API_TOKEN = os.getenv("APP_USERS_API_TOKEN", "token")
APP_SMTP_HOST = os.getenv("APP_SMTP_HOST", "")
APP_SMTP_PORT = int(os.getenv("APP_SMTP_PORT", "587"))
APP_SMTP_USER = os.getenv("APP_SMTP_USER", "")
APP_SMTP_PASSWORD = os.getenv("APP_SMTP_PASSWORD", "")
APP_SMTP_FROM = os.getenv("APP_SMTP_FROM", "")
APP_SMTP_STARTTLS = os.getenv("APP_SMTP_STARTTLS", "true").lower() == "true"
ALGORITHM = "HS256"
