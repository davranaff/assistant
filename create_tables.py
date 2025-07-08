#!/usr/bin/env python3
"""
Script for creating database tables
"""
import asyncio
import logging
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import engine
from app.infrastructure.database.models import PostEntity, PublicationEntity


async def create_tables():
    """Create all database tables"""
    logging.info("Creating database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logging.info("Database tables created successfully!")
    logging.info("Tables: posts, publications")


async def drop_tables():
    """Drop all database tables"""
    logging.info("Dropping database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logging.info("Database tables dropped successfully!")


async def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        await drop_tables()
    else:
        await create_tables()


if __name__ == "__main__":
    asyncio.run(main()) 