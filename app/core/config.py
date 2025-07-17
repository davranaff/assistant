import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "env" / ".env"


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432"

    # Telegram Bot
    telegram_bot_token: str = "bot_token"
    webhook_base_url: str = "localhost:8000"

    # OpenAI
    openai_api_key: str = "openai_api_key"

    # Together
    together_api_key: str = "together_api_key"

    # Publishers API Keys
    medium_api_key: Optional[str] = "medium_api_key"
    dev_to_api_key: Optional[str] = "dev_to_api_key"

    # Reddit API
    reddit_client_id: Optional[str] = "reddit_client_id"
    reddit_client_secret: Optional[str] = "reddit_client_secret"
    reddit_username: Optional[str] = "reddit_username"
    reddit_password: Optional[str] = "reddit_password"

    # FastAPI
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_name: str = "AutoPoster Bot"
    debug: bool = False

    class Config:
        env_file = ENV_PATH
        case_sensitive = False

settings = Settings()
