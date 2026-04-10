import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=_env_int("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 15)
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=_env_int("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)
    )

    DEBUG = _env_bool("FLASK_DEBUG", True)
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = _env_int("FLASK_PORT", 5000)
