from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Ensure .env is loaded into the process environment before Settings is evaluated
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


class Settings(BaseSettings):
    """
    Central application settings loaded from environment or .env file.
    """

    database_url: str = Field(
        default="sqlite:///./sql_app.db",
        env="DATABASE_URL",
        description="SQLAlchemy database URL",
    )
    # Default to the secret you provided; still overridable via JWT_SECRET in .env
    jwt_secret: str = Field(
        default="4fYhT2kP9Qx8mZ7j1pLf3vS0wR6aB8cD",
        env="JWT_SECRET",
        description="Secret key for signing JWT tokens",
    )
    google_api_key: Optional[str] = Field(
        default=None,
        env="GOOGLE_API_KEY",
        description="Google Gemini API key",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader so values are read once per process.
    """
    return Settings()