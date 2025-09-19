import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient



from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_session, Base
from app.schemas.user import UserBase



DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

AsyncTestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session_test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncTestSessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def clean_Db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

app.dependency_overrides[get_session] = get_session_test

client = TestClient(app=app)

def test_get_root():
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert reponse.json() == {"message": "we are live!"}

@pytest.mark.asyncio
async def test_add_new_user():
    payload = {"user_name": "testuser", "password": "testuser"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/signup",json=payload)
    assert response.status_code == 200
    assert response.json() == {"user_name": "testuser"}


@pytest.mark.asyncio
async def test_get_user_me():
    payload = {"user_name": "testuser2", "password": "testuser2"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/signup",json=payload)
        assert response.status_code == 200
        assert response.json() == {"user_name": "testuser2"}


        data = {"username": "testuser2", "password": "testuser2"}
   
        response = await ac.post("/token", data=data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        header = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/users/me", headers=header)
        assert response.status_code == 200
        assert response.json() == {"user_name": "testuser2"}



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("validuser", "validpass", 200),
        ("validuser", "wrongpass", 401),
        ("ghost", "whatever", 401),
    ],
)
async def test_multiple_get_user_me(username, password, expected_status):

    await clean_Db()
    
    payload = {"user_name": "validuser", "password": "validpass"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/signup",json=payload)
        assert response.status_code == 200
        assert response.json() == {"user_name": "validuser"}

        resp = await ac.post("/token", data={"username": username, "password": password})
        assert resp.status_code == expected_status

    
