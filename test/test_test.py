import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_session

# -------------------------------
# Setup a temporary test database
# -------------------------------
DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # in-memory SQLite DB for testing
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Override the get_session dependency
async def override_get_session():
    async with AsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

# -------------------------------
# Setup the database before tests
# -------------------------------
@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# -------------------------------
# Test signup endpoint
# -------------------------------
def test_signup_user():
    response = client.post(
        "/signup",
        json={"user_name": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json() == {"user_name": "testuser"}

# -------------------------------
# Test get current user
# -------------------------------
def test_get_current_user():
    # First, signup
    client.post("/signup", json={"user_name": "meuser", "password": "password123"})

    # Get token using your auth/token endpoint (simulate OAuth2PasswordRequestForm)
    token_response = client.post(
        "/token",
        data={"username": "meuser", "password": "password123"}
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    # Use token to call /users/me
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["user_name"] == "meuser"