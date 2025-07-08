"""
Main API v1 router
"""
from fastapi import APIRouter

from app.api.v1.telegram import router as telegram_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(telegram_router, prefix="/telegram", tags=["telegram"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "api_version": "v1"
    }
