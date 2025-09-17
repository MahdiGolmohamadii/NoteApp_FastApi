from fastapi import APIRouter, Body, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from models.user import User
from schemas.user import UserBase
from core.database import get_session
from core import security

router = APIRouter(tags=["users"])


@router.post("/signup")
async def add_new_user(user: str, password: str, session: Annotated[AsyncSession, Depends(get_session)]):
    hashed_password = security.get_passwords_hashed(password)
    new_user = User(user_name=user, user_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.get("/users", response_model=UserBase)
async def get_users(user: Annotated[UserBase, Depends(security.get_current_user)]):
    return user



