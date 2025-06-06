import os
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
Base = declarative_base()

ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.exception("Database session failed")
        raise

@asynccontextmanager
async def lifespan(app):
    try:
        logger.info("Starting up DB connection...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        logger.info("Shutting down DB connection...")
        await engine.dispose()
