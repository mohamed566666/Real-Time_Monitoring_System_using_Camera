import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.infrastructure.db.base import Base
import app.infrastructure.db.models
from app.core.config import settings
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_database():
    """Create all database tables"""
    logger.info(f"🚀 Creating database tables for {settings.APP_NAME}")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    try:
        async with engine.begin() as conn:
            logger.info("📝 Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        raise
    finally:
        await engine.dispose()


async def drop_database():
    logger.warning("⚠️  DROPPING ENTIRE SCHEMA!")
    confirm = input("Type 'drop schema' to confirm: ")

    if confirm.lower() == "drop schema":
        engine = create_async_engine(settings.DATABASE_URL, echo=True)

        try:
            async with engine.begin() as conn:
                from sqlalchemy import text

                await conn.execute(text("DROP SCHEMA public CASCADE"))
                await conn.execute(text("CREATE SCHEMA public"))

            logger.info("✅ Schema dropped & recreated successfully!")

        finally:
            await engine.dispose()
    else:
        logger.info("❌ Cancelled")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        asyncio.run(drop_database())
    else:
        asyncio.run(create_database())
