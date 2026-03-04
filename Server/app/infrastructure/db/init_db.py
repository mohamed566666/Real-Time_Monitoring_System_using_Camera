import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.infrastructure.db.base import Base
import app.infrastructure.db.models
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    logger.info("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
