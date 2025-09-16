from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from typing import Annotated
from itertools import count
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from models.user import User
from core.database import get_session

from core import security

router = APIRouter(tags=["users"])


# session = get_session()
# last_user_id = session.execute(select(User)).scalar_one_or_none()
# id_counter = count(start=len(last_user_id))

# # FOR TEST MUST BE CHANGED
# class User(BaseModel):
#     user_name: str
#     password: str

@router.post("/signup")
async def add_new_user(user: str, password: str, session: Annotated[AsyncSession, Depends(get_session)]):
    hashed_password = security.get_passwords_hashed(password)
    new_user = User(user_name=user, user_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.get("/users")
async def get_users():
    return {"message": "we ar live in users"}

