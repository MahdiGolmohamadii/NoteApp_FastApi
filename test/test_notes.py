import pytest
import pytest_asyncio

import json

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.security import get_session
from app.core.database import Base


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

AsyncTestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_test_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncTestSessionLocal()
    try:
        yield db
    finally:
        await db.close()

@pytest_asyncio.fixture
async def clean_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture
async def async_client(clean_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def add_user(async_client):
    payload = {"user_name": "testuser", "password": "testuser"}

    response = await async_client.post("/signup",json=payload)
    # assert response.status_code == 200
    # assert response.json() == {"user_name": "testuser"}



@pytest_asyncio.fixture
async def user_token(async_client, add_user):
    data = {"username": "testuser", "password": "testuser"}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]


app.dependency_overrides[get_session] = get_test_session


@pytest.mark.asyncio
async def test_add_new_note (async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post("/notes", json={"title": "Note", "description": "Hello"}, headers=headers)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_all_notes(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    note1 = {"title": "this is title 1", "description": "this is description1"}
    note2 = {"title": "this is title 2", "description": "this is description2"}
    response = await async_client.post("/notes", json=note1, headers=headers)
    assert response.status_code == 201
    note_id1 = response.json()

    response = await async_client.post("/notes", json=note2, headers=headers)
    assert response.status_code == 201
    note_id2 = response.json()

    response = await async_client.get("/notes", headers=headers)
    assert response.status_code == 200
    
    notes = response.json()
    assert isinstance(notes, list)
    assert len(notes) == 3

    titles = [n["title"] for n in notes]
    assert note1["title"] in titles
    assert note2["title"] in titles

@pytest.mark.asyncio
async def test_patch_note(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    repsonse = await async_client.patch("/notes/1", headers=headers, json={"title": "ops"})
    assert repsonse.status_code == 202
    assert repsonse.json()["title"] == "ops"

    repsonse = await async_client.patch("/notes/1", headers=headers, json={"description": "ops1"})
    assert repsonse.status_code == 202
    assert repsonse.json()["description"] == "ops1"

    repsonse = await async_client.patch("/notes/1", headers=headers, json={"title": "string", "description": "string"})
    assert repsonse.status_code == 202
    assert repsonse.json()["title"] == "string"
    assert repsonse.json()["description"] == "string"


@pytest.mark.asyncio
async def test_delete_note(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    response = await async_client.delete("/notes/1", headers=headers)
    assert response.status_code == 200

    response = await async_client.get("/notes/1", headers=headers)
    assert response.status_code == 404