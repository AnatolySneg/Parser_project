import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.models.models import metadata
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.config import TEST_DB_USER as test_db_us, TEST_DB_PASSWORD as test_db_pass
from src.config import TEST_DB_HOST as test_db_host, TEST_DB_NAME as test_db_name, TEST_DB_PORT as test_db_port
from src.database import get_async_session
from src.main import app

# DATABASE
DATABASE_URL_TEST = f'postgresql+asyncpg://{test_db_us}:{test_db_pass}@{test_db_host}:{test_db_port}/{test_db_name}'

engine_test = create_async_engine(DATABASE_URL_TEST)
async_session_maker = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


# @pytest.fixture(autouse=True, scope='session')
# async def prepare_database():
#     async with engine_test.begin() as conn:
#         await conn.run_sync(metadata.create_all)
#     yield
#     async with engine_test.begin() as conn:
#         await conn.run_sync(metadata.drop_all)


# SETUP
# @pytest.fixture(scope='session')
# async def event_loop(request):
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#

client = TestClient(app)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
