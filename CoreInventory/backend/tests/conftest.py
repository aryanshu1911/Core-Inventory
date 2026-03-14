import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base


# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_db():
    async with TestingSessionLocal() as session:
        async with session.begin():
            yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def manager_token(client):
    """Register and log in an inventory_manager; return the bearer token."""
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Test Manager",
        "email": "manager@ci.test",
        "password": "SecurePass123!",
        "role": "inventory_manager",
    })
    if reg.status_code not in (200, 201, 400):  # 400 = already exists
        pytest.fail(f"Register failed: {reg.text}")
    login = await client.post("/api/v1/auth/login", json={
        "email": "manager@ci.test",
        "password": "SecurePass123!",
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


@pytest_asyncio.fixture
async def staff_token(client):
    """Register and log in a warehouse_staff; return the bearer token."""
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Test Staff",
        "email": "staff@ci.test",
        "password": "SecurePass123!",
        "role": "warehouse_staff",
    })
    if reg.status_code not in (200, 201, 400):
        pytest.fail(f"Register failed: {reg.text}")
    login = await client.post("/api/v1/auth/login", json={
        "email": "staff@ci.test",
        "password": "SecurePass123!",
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}
