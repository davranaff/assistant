import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432")

    # Telegram Bot
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "7888828778:AAEH35_WGl3GLWjVZReNcECY_y-OyVW6e-w")
    webhook_base_url: str = os.getenv("WEBHOOK_BASE_URL", "https://34d7464538fe.ngrok-free.app")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "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")

    # Together
    together_api_key: str = os.getenv("TOGETHER_API_KEY", "tgp_v1_Kre7Ol-Pm2Rz8mKaw_h8HUfXQi4Xko6JaMPypzPgank")

    # Publishers API Keys
    medium_api_key: Optional[str] = os.getenv("MEDIUM_API_KEY", None)
    dev_to_api_key: Optional[str] = os.getenv("DEV_TO_API_KEY", None)

    # Reddit API
    reddit_client_id: Optional[str] = os.getenv("REDDIT_CLIENT_ID", None)
    reddit_client_secret: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET", None)
    reddit_username: Optional[str] = os.getenv("REDDIT_USERNAME", None)
    reddit_password: Optional[str] = os.getenv("REDDIT_PASSWORD", None)

    # FastAPI
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    app_name: str = os.getenv("APP_NAME", "AutoPoster Bot")
    debug: bool = os.getenv("DEBUG", False)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
