from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/autopost_db"

    # Telegram Bot
    telegram_bot_token: str = ""
    webhook_base_url: str = "https://your-domain.com"

    # OpenAI
    openai_api_key: str = ""

    # Publishers API Keys
    medium_api_key: Optional[str] = None
    dev_to_api_key: Optional[str] = None

    # Reddit API
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None

    # FastAPI
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_name: str = "AutoPoster Bot"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
