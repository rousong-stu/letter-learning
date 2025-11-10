import asyncio
import os
import shutil
from pathlib import Path

os.environ.setdefault("MEDIA_DIRECTORY", "test_uploads")

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app, get_settings
from app.core.database import get_db
from app.models import Base, Role, User, UserRole
from app.core.security import get_password_hash


TEST_DB_PATH = Path(__file__).parent / "test_app.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    engine = create_async_engine(TEST_DB_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(scope="session")
async def session_factory(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


async def _seed_data(session: AsyncSession):
    roles = [
        Role(slug="admin", name="管理员", description="平台超级管理员", is_system=1),
        Role(slug="teacher", name="教师", description="教师权限", is_system=1),
        Role(slug="student", name="学生", description="学生权限", is_system=1),
    ]
    session.add_all(roles)
    await session.flush()

    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        display_name="系统管理员",
        status=1,
    )
    session.add(admin_user)
    await session.flush()

    admin_role = next(role for role in roles if role.slug == "admin")
    session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
    await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def override_dependencies(session_factory):
    async def _get_db():
        async with session_factory() as session:
            yield session

    async with session_factory() as session:
        await _seed_data(session)

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    media_path = Path(get_settings().media_path)
    if media_path.exists():
        shutil.rmtree(media_path, ignore_errors=True)


@pytest.fixture
async def client(session_factory, override_dependencies):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
