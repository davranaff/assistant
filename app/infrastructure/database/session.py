"""
Database session configuration
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import sessionmaker
import asyncio

from core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

base_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create async session factory
AsyncSessionLocal = async_scoped_session(base_session_factory, scopefunc=asyncio.current_task)

async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
