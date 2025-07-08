from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.bootstrap import bootstrap_application
from app.api.v1.api import api_router
from app.api.v1.telegram import cleanup_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    bootstrap_application()
    
    yield
    
    # Shutdown
    await cleanup_bot()


app = FastAPI(
    title=settings.app_name,
    description="AutoPoster Bot - AI-powered content generation and multi-platform publishing",
    version="2.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "message": "AutoPoster Bot API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "Clean Architecture with DDD",
        "features": [
            "AI Content Generation",
            "Multi-platform Publishing",
            "Telegram Bot Interface",
            "Webhook Support"
        ]
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "telegram_webhook": "enabled",
        "api_version": "v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )