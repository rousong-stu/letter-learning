from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

async_engine = create_async_engine(settings.async_database_url, echo=settings.app_debug, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    """提供数据库会话给 FastAPI 依赖使用。"""
    async with AsyncSessionLocal() as session:
        yield session

