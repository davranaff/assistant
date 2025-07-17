import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432")

    # Telegram Bot
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "bot_token")
    webhook_base_url: str = os.getenv("WEBHOOK_BASE_URL", "localhost:8000")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "openai_api_key")

    # Together
    together_api_key: str = os.getenv("TOGETHER_API_KEY", "together_api_key")

    # Publishers API Keys
    medium_api_key: Optional[str] = os.getenv("MEDIUM_API_KEY", "medium_api_key")
    dev_to_api_key: Optional[str] = os.getenv("DEV_TO_API_KEY", "dev_to_api_key")

    # Reddit API
    reddit_client_id: Optional[str] = os.getenv("REDDIT_CLIENT_ID", "reddit_client_id")
    reddit_client_secret: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET", "reddit_client_secret")
    reddit_username: Optional[str] = os.getenv("REDDIT_USERNAME", "reddit_username")
    reddit_password: Optional[str] = os.getenv("REDDIT_PASSWORD", "reddit_password")

    # FastAPI
    secret_key: str = os.getenv("SECRET_KEY", "secret_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_name: str = os.getenv("APP_NAME", "AutoPoster Bot")
    debug: bool = os.getenv("DEBUG", False)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
