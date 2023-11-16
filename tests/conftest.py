import asyncio
from typing import AsyncGenerator
from src.models.models import metadata
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.config import TEST_DB_USER as test_db_us, TEST_DB_PASSWORD as test_db_pass
from src.config import TEST_DB_HOST as test_db_host, TEST_DB_NAME as test_db_name, TEST_DB_PORT as test_db_port
from src.database import get_async_session
from src.main import app

# DATABASE
DATABASE_URL_TEST = f'postgresql+asyncpg://{test_db_us}:{test_db_pass}@{test_db_host}:{test_db_port}/{test_db_name}'

engine_test = create_async_engine(DATABASE_URL_TEST)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

