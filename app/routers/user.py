from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.user import UserBase, UserInDB, UserLogIn
from app.models.user import User
from app.core.database import get_session
from app.core.security import get_current_user, get_passwords_hashed


router = APIRouter(tags=["users"])


@router.post("/signup", response_model=UserBase, status_code=status.HTTP_200_OK)
async def add_new_user(
            user:Annotated[UserLogIn, Body()], 
            session: Annotated[AsyncSession, Depends(get_session)]):
    
    hashed_password = get_passwords_hashed(user.password)
    new_user = User(user_name=user.user_name, user_password=hashed_password)
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        response_user = UserBase(user_name=new_user.user_name)
        return response_user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"an unexpected erro accured: {e}"
        )

@router.get("/users/me", response_model=UserBase, status_code=status.HTTP_200_OK)
async def get_users(user: Annotated[UserBase, Depends(get_current_user)]):
    return user


