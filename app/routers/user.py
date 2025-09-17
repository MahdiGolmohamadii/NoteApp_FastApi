from fastapi import APIRouter, Depends, Body
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


from ..models.user import User
from ..schemas.user import UserBase, UserInDB
from ..core.database import get_session
from ..core import security

router = APIRouter(tags=["users"])


@router.post("/signup", response_model=UserBase)
async def add_new_user(user:Annotated[UserInDB, Body()], session: Annotated[AsyncSession, Depends(get_session)]):
    hashed_password = security.get_passwords_hashed(user.password)
    new_user = User(user_name=user.user_name, user_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    response_user = UserBase(user_name=new_user.user_name)
    return response_user

@router.get("/users", response_model=UserBase)
async def get_users(user: Annotated[UserBase, Depends(security.get_current_user)]):
    return user



